---
name: database-migration-plan
description: 'Planeja e escreve mudanças de schema de banco relacional com migração reversível: classifica o risco de cada operação, separa em expandir e contrair quando a mudança quebra o código em produção, escreve o up e o down e prova o rollback com o ciclo up, down, up. Use ao criar ou alterar tabela, coluna, tipo, índice, constraint ou chave estrangeira, ao renomear ou remover campo, ao migrar dados existentes (backfill) e ao revisar uma migração. Cobre Alembic e golang-migrate.'
---

# Database Migration Plan

Guia para mudar o schema sem perder dado e sem derrubar a aplicação que já está rodando. Toda migração tem um caminho de
volta escrito e testado, e a mudança que quebra o código antigo é dividida em passos que convivem com ele.

Nos caminhos abaixo, `${CLAUDE_SKILL_DIR}` é a pasta desta skill (`.claude/skills/database-migration-plan/`).

## Princípios

- **Reversível.** Toda migração tem `up` e `down`. O `down` desfaz exatamente o `up` e é provado pelo ciclo up, down, up
  no banco local. "Restaurar o backup" não conta como rollback.
- **Expandir e contrair.** Mudança que quebra o código em produção (renomear, remover, mudar tipo, tornar obrigatório)
  vira passos separados: expandir o schema, migrar os dados, trocar o código e só depois contrair. Cada passo é uma
  migração e um *deploy*. O mapa de cada operação está em `${CLAUDE_SKILL_DIR}/references/operacoes.md`.
- **Schema e dado separados.** Mudança de estrutura e cópia de dados existentes ficam em migrações diferentes. Assim uma
  falha na cópia não deixa a estrutura pela metade.
- **Histórico imutável.** Migração já aplicada em algum ambiente compartilhado nunca é editada: a correção é uma
  migração nova.
- **Rascunho gerado é lido.** O que a ferramenta gera sozinha (Alembic `--autogenerate`) é ponto de partida. Leia cada
  operação antes de aplicar.

## Passos

Progresso:

- [ ] 1. **Ferramenta e convenção.** Descubra a ferramenta, o diretório, o padrão de nome e os comandos olhando as
  migrações existentes e o `Makefile` ou o README. Leia a referência da ferramenta:
  `${CLAUDE_SKILL_DIR}/references/alembic.md` ou `${CLAUDE_SKILL_DIR}/references/golang-migrate.md`.
- [ ] 2. **Classifique.** Para cada mudança, ache a linha em `${CLAUDE_SKILL_DIR}/references/operacoes.md` e anote se
  ela é compatível ou se quebra o código atual.
- [ ] 3. **Planeje e espere a aprovação.** Toda mudança ganha um plano no modelo de
  `${CLAUDE_SKILL_DIR}/assets/plano-migracao.md`. Mudança só compatível (tabela nova, coluna opcional nova) usa só as
  seções Classificação e Passos. Mostre o plano ao usuário e pare: o passo 4 começa depois que ele aprovar. Ajuste
  pedido volta a este passo, com o plano novo mostrado de novo. Pedido de revisão termina aqui, com o relatório e sem
  arquivo criado.
- [ ] 4. **Escreva.** Uma migração por passo do plano aprovado, com `up` e `down`, no padrão de nome do repositório.
- [ ] 5. **Prove o rollback.** Rode `${CLAUDE_SKILL_DIR}/scripts/verificar-rollback.sh --url <url do banco local>`. O
  script recusa qualquer host fora de `localhost`, `127.0.0.1`, `::1`, `db` e `postgres`; recusado, peça ao usuário a
  URL do banco local. Se o ciclo falhar, corrija a migração e rode de novo. Avance só com o ciclo passando.
- [ ] 6. **Teste a aplicação.** Rode os testes do repositório com o banco na versão nova.

A tarefa termina quando o usuário aprovou o plano, o ciclo up, down, up passa, os testes passam e a entrega traz o plano
e as saídas.

## Armadilhas

- **Renomear vira apagar.** O `--autogenerate` do Alembic não reconhece renomeação de coluna ou tabela: ele gera
  `drop_column` e `add_column`, e o dado da coluna se perde. Troque por `op.alter_column(..., new_column_name=...)` ou
  siga o caminho de expandir e contrair.
- **Coluna obrigatória em tabela com dados.** `NOT NULL` sem valor padrão falha quando a tabela já tem linhas. Adicione
  como opcional, preencha e só então torne obrigatória.
- **Tipo `ENUM` do PostgreSQL.** O `down` precisa apagar o tipo (`DROP TYPE`) depois da coluna. Sem isso, o próximo `up`
  falha com o tipo já existente.
- **Índice concorrente.** `CREATE INDEX CONCURRENTLY` não roda dentro de transação. Coloque-o numa migração própria,
  fora do bloco transacional da ferramenta.
- **Arquivo de rollback ausente.** No golang-migrate, um `NNNNNN_nome.up.sql` sem o `.down.sql` correspondente torna a
  versão irreversível. Confira os pares antes de entregar.
- **Banco sujo.** Migração que falha no meio deixa o golang-migrate em estado `dirty`. Corrija o SQL, desfaça à mão o
  que foi aplicado e use `migrate force <versão>` só depois.

## Formato da Entrega

```text
Classificação:
<operação> — compatível | quebra, uma por linha

Plano:
<caminho do plano> — aprovado pelo usuário em <frase da aprovação>

Migrações:
<caminho do arquivo>, uma por linha

Rollback:
<saída do scripts/verificar-rollback.sh>

Testes:
<comando e últimas linhas da saída>
```
