---
name: liquibase-migration
description: 'Planeja e escreve mudanças de schema com Liquibase de forma reversível nos repos Synpower que usam Liquibase (ai-agents, data-pipeline-orchestrator, extrator-ai-gov): classifica o risco da operação, separa em expandir e contrair quando a mudança quebra o código em produção, escreve o changeset em Liquibase formatted SQL com o --rollback e prova o rollback. Use ao "criar a migração dessa tabela", "alterar o schema", "adicionar/remover coluna", "esse DROP COLUMN é seguro?", "como faço o rollback dessa mudança", "migrar dado existente/backfill" ou "revisar um changeset Liquibase". É a skill de Liquibase; para Alembic ou golang-migrate use a database-migration-plan.'
---

# Liquibase Migration

Guia para mudar o schema com Liquibase sem perder dado e sem derrubar a aplicação que já está no ar. Toda migração tem um
caminho de volta escrito e provado, e a mudança que quebra o código antigo é dividida em passos que convivem com ele.

Nos caminhos abaixo, `${CLAUDE_SKILL_DIR}` é a pasta desta skill (`.claude/skills/liquibase-migration/`).

## Relação com a database-migration-plan

Esta skill **herda a teoria** da `database-migration-plan` (classificação de risco, expandir e contrair, ciclo up → down
→ up) e só troca a ferramenta. A `database-migration-plan` cobre Alembic e golang-migrate; **esta cobre Liquibase**. A
tabela de risco de cada operação é a mesma, em
`.claude/skills/database-migration-plan/references/operacoes.md` — leia-a e aplique aqui. O que muda é a mecânica: onde
o arquivo fica, o formato do changeset, como se escreve o rollback e como se prova.

## Princípios

- **Reversível, com `--rollback` explícito.** Em Liquibase formatted SQL o caminho de volta não é inferido: cada
  changeset declara o SQL de volta num comentário `--rollback`. **Sem `--rollback`, o `rollbackCount` falha.** Um
  changeset sem rollback não está pronto. "Restaurar o backup" não conta.
- **Expandir e contrair.** Mudança que quebra o código em produção (renomear, remover, mudar tipo, tornar obrigatório)
  vira changesets separados em deploys separados: expandir o schema, migrar o dado, trocar o código e só depois contrair.
  No Liquibase isso importa ainda mais por causa do PreSync (veja abaixo).
- **Schema e dado separados.** Mudança de estrutura e backfill de dado existente ficam em changesets diferentes. Assim
  uma falha no backfill não deixa a estrutura pela metade, e cada um tem seu próprio rollback.
- **Histórico imutável.** Changeset já aplicado em qualquer ambiente compartilhado nunca é editado — o Liquibase guarda
  o checksum em `databasechangelog` e recusa um changeset alterado. A correção é um changeset novo.
- **Um changeset por arquivo, numerado.** Cada arquivo novo é o próximo `NNNN` e é incluído na ordem do nome.
- **Comente o mínimo.** Reduza os comentários ao estritamente necessário: o SQL e o nome do arquivo já dizem o quê. Só
  comente o *porquê* de algo não óbvio (uma ordem de operações sutil, uma armadilha). Atenção: `--liquibase formatted sql`,
  `--changeset` e `--rollback` **não são comentários** — são diretivas obrigatórias; nunca os remova em nome de "menos
  comentário".

## Convenção real do Liquibase nos repos

Confirmado no `ai-agents` (vale igual em `data-pipeline-orchestrator` e `extrator-ai-gov`):

- **Changelog mestre:** `resources/liquibase/db.changelog-master.yaml` é só
  `databaseChangeLog: [{ includeAll: { path: ./tables/ } }]`. Ele inclui **todos** os arquivos de
  `resources/liquibase/tables/` **em ordem de nome**. Você quase nunca edita o mestre; só adiciona arquivo em `tables/`.
- **Ordem pelo prefixo `NNNN`:** `tables/` tem SQL numerado — `0001_create_agents_table.sql`,
  `0002_create_users_table.sql`, ... O arquivo novo é o **próximo número** livre. O nome descreve a mudança em
  minúsculas com `_`.
- **Formato Liquibase formatted SQL** (veja a seção de como escrever).
- **Execução** via `docker-compose.liquibase.yml` (imagem do registry interno, JDBC Postgres,
  `working_dir /liquibase/changelog`, volume `./resources/liquibase`). Os alvos do Makefile:
  - `make liquibase-update` — aplica os changesets pendentes em ordem.
  - `make liquibase-rollback` — roda `rollbackCount 1` (desfaz o último changeset).
  - `make liquibase-status` — lista o que está pendente em relação ao banco.
  - `make liquibase-validate` — valida os changelogs (sintaxe, ids duplicados, checksums).
- **No deploy k8s** o Liquibase roda como Job ArgoCD `PreSync` com `sync-wave: "1"`
  (`infra/<ambiente>/liquibase.yaml`), **antes** do Deployment da app (`sync-wave: "2"`).

## Por que o PreSync força expandir e contrair

O Job de migração roda **antes** do novo código subir. No momento do PreSync, quem ainda está no ar é o **código
antigo**. Logo todo changeset precisa ser compatível com **dois** códigos ao mesmo tempo:

1. o código antigo, que continua servindo requisições durante e logo após a migração;
2. o código novo, que sobe no sync-wave 2.

Uma mudança destrutiva num único changeset quebra o código antigo no instante do PreSync. Por isso ela vira **dois
deploys**:

- **Deploy 1 — expandir:** changeset que adiciona o novo (coluna nova nullable, nova tabela) sem tocar no que o código
  antigo usa. Backfill do dado num changeset separado. O código novo deste deploy passa a escrever nos dois lugares.
- **Deploy 2 — contrair:** só depois que nenhum código em produção usa mais o campo velho, um changeset remove/renomeia.

Renomear coluna = coluna nova + backfill + código escrevendo nas duas (deploy 1), depois dropar a antiga (deploy 2).
Nunca um `ALTER ... RENAME` solto.

## Classificação de risco

Ache a operação em `.claude/skills/database-migration-plan/references/operacoes.md` e anote se é compatível ou se quebra o
código atual. Em resumo:

**Compatíveis** (um changeset só, sem expandir e contrair):

- adicionar coluna **nullable** (ou com `DEFAULT`);
- adicionar tabela nova;
- adicionar índice com `CREATE INDEX CONCURRENTLY` (changeset próprio — veja Armadilhas).

**Quebram o código antigo** (expandir e contrair, dois deploys):

- remover (`DROP`) ou renomear coluna ou tabela;
- mudar o tipo de uma coluna;
- adicionar coluna `NOT NULL` sem `DEFAULT` numa tabela com linhas;
- adicionar `UNIQUE`/`FOREIGN KEY`/`CHECK` que o dado atual pode violar.

## Como escrever o changeset

1. Descubra o próximo `NNNN` livre em `resources/liquibase/tables/` e crie `NNNN_<descricao>.sql`.
2. Abra o arquivo com `--liquibase formatted sql`.
3. Declare `--changeset <autor>:<id>` (autor = seu usuário; id único e estável — por convенção o próprio `NNNN` mais a
   descrição, como `0021-add-status-to-agents`). O id entra na `databasechangelog`; **não mude depois de aplicado**.
4. Escreva o SQL do `up`.
5. Escreva o `--rollback <sql>` que desfaz exatamente o `up`.

Exemplo (adicionar coluna nullable — compatível):

```sql
--liquibase formatted sql

--changeset fulano.sobrenome:0021-add-status-to-agents
--comment: Adiciona o status do agente, opcional para não quebrar o código atual.
ALTER TABLE syn_ai_agents ADD COLUMN status TEXT;

--rollback ALTER TABLE syn_ai_agents DROP COLUMN status;
```

Backfill fica em **outro** changeset (outro arquivo `NNNN`), com seu próprio `--rollback` (quando houver volta possível;
se não houver, diga isso no `--comment` e no plano).

## Prove o rollback

Um changeset sem rollback provado **não está pronto**. Rode só no **banco local** (regra do `AGENTS.md`), com o ciclo
up → down → up:

1. `make liquibase-update` — aplica o changeset novo.
2. `make liquibase-status` — confere que não há pendência.
3. `make liquibase-rollback` — roda `rollbackCount 1` e desfaz o último changeset. **Se falhar aqui, falta `--rollback`
   ou ele está errado.**
4. `make liquibase-update` de novo — reaplica, provando que o par up/rollback fecha o ciclo.
5. `make liquibase-validate` — garante changelogs válidos (sem id duplicado nem checksum quebrado).

Se o ciclo falhar, corrija o changeset e repita. Avance só com o ciclo passando.

## Armadilhas

- **`--rollback` ausente.** O caso mais comum. Sem ele o `rollbackCount` para no changeset e a migração é irreversível.
  Todo arquivo novo precisa do seu `--rollback`.
- **Id ou checksum mudados depois de aplicado.** Editar um changeset já rodado muda o checksum e o Liquibase recusa
  (`validation failed`). Nunca edite um changeset aplicado em ambiente compartilhado — faça um novo.
- **`NOT NULL` em tabela com dados.** Falha quando já há linhas. Adicione nullable, faça o backfill, e só num deploy
  seguinte torne `NOT NULL` — como nos arquivos `add_and_backfill...` seguidos de `finalize...` do repo.
- **Índice concorrente dentro de transação.** `CREATE INDEX CONCURRENTLY` não roda em transação. Coloque-o num
  changeset próprio com `--changeset ... runInTransaction:false` e o rollback `DROP INDEX CONCURRENTLY`.
- **Destrutivo colado no deploy.** Um `DROP`/`RENAME` no mesmo deploy do código novo quebra o código antigo no PreSync.
  Separe em expandir e contrair.

## Quando NÃO usar

- Projeto que usa **Alembic ou golang-migrate** (não Liquibase) → `database-migration-plan`.
- **Aplicar a migração em produção** ou promover o deploy → `deploy-readiness`. Aqui a migração só roda no banco local.

## Formato da Entrega

```text
Classificação:
<operação> — compatível | quebra, uma por linha

Plano (se expandir e contrair):
expandir: <changesets/deploy 1> | contrair: <changesets/deploy 2>

Changesets:
resources/liquibase/tables/<NNNN_nome>.sql, um por linha

Rollback:
<saída do ciclo make liquibase-update → rollback → update → validate>
```
