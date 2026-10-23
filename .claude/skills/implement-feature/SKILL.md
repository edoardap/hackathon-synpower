---
name: implement-feature
description: Ciclo de implementação de uma funcionalidade num repositório alvo, a partir de um design técnico ou de uma tarefa, com uma change do OpenSpec por rodada, plano aprovado pelo usuário, commits só com aprovação humana, revisão de PR por qualidade e segurança e limpeza da change ao encerrar. Use quando o pedido for implementar um design, uma história ou uma tarefa já escrita ("implementa a funcionalidade de oportunidades", "agora a API de oportunidades", "pega essa tarefa", "/implement-feature"), ou retomar uma implementação em andamento. Escrever o design é do solutions-architect.
---

# Implement Feature

Você conduz a implementação de uma funcionalidade em **um** repositório alvo, uma rodada por vez. Você não escreve plano
nem código: prepara, despacha, conduz as aprovações humanas e encerra a rodada. Quem executa e quem revisa são os
agentes de `.claude/agents/`:

| Agente              | Papel                                                                                     | Quem despacha      | Pode editar                  |
| ------------------- | ----------------------------------------------------------------------------------------- | ------------------ | ---------------------------- |
| `software-engineer` | Escreve a change e implementa uma fase de backend, frontend ou banco; corrige os findings | você, orchestrator | sim                          |
| `orchestrator`      | Conduz as fases em ondas, a revisão do PR e a análise final                               | você               | `reviews/` e commit aprovado |
| `code-reviewer`     | Revisa o diff da rodada como um PR e junta os focos                                       | orchestrator       | não                          |
| `qa-engineer`       | Qualidade, com os testes de regressão de cada defeito                                     | code-reviewer      | só testes                    |
| `security-reviewer` | Segurança e segredos                                                                      | code-reviewer      | não                          |

O formato dos artefatos da change está em `${CLAUDE_SKILL_DIR}/references/plano.md`; o alcance e o formato da revisão,
em `${CLAUDE_SKILL_DIR}/references/revisao.md`. Você não precisa lê-los para conduzir o ciclo.

## Rodadas e Changes

Cada rodada é uma **change do OpenSpec** (`openspec/changes/<change>/` no repositório alvo), chamada
`<funcionalidade>-r<n>-<recorte>` (`oportunidades-r1-organizacoes`). Pedido que cita só parte da entrada ("só o
backend", "a tela", algumas histórias) define o **recorte** da rodada; pedido sem recorte é uma rodada com a entrada
inteira. A change guarda o plano (`proposal.md`, `specs/`, `design.md`, `tasks.md`), as decisões do usuário
(`decisoes.md`) e os relatórios (`reviews/`). Ao encerrar, a spec da rodada entra no manual vivo (`openspec/specs/`), e
a pasta da change é commitada e depois apagada.

## Regras do Ciclo

- **Um repositório alvo.** Código e change mudam só nele. Outro repositório é leitura, com o `AGENTS.md` dele lido
  antes.
- **`AGENTS.md` primeiro.** Você e cada agente leem o `AGENTS.md` do repositório alvo, e o `CLAUDE.md` e o guia de
  contribuição se existirem, antes de agir.
- **Commit com aprovação humana.** Nenhum commit acontece sem o usuário ver o diff e aprovar. O orchestrator para antes
  de cada commit com `AGUARDANDO_COMMIT`, e você conduz a aprovação. O gancho do plugin pede confirmação de todo
  `git commit` como segunda trava.
- **Git.** Siga o fluxo de git do repositório alvo. Os commits levam só o *header*. *Push*, *tag* e PR só quando o
  usuário pedir.
- **Banco local.** Migração e testes rodam só no banco local; o `verificar-rollback.sh` da `database-migration-plan`
  recusa outro host.
- **Espera.** Agente rodando é espera: sem novo despacho e sem troca de modelo.
- **Evidência.** Relatório de agente é alegação. Antes de avançar, confira com `git -C <repo> status --short`, com o
  diff e com a saída dos comandos, como manda `verification-before-completion`.
- **Retomada.** Change aberta em `openspec/changes/` com caixas sem marcar no `tasks.md`: a rodada não terminou. O ponto
  atual sai das caixas e de `reviews/`, e o contexto das aprovações sai de `decisoes.md`; despache o orchestrator de
  novo, e ele pula as fases feitas.
- **Decisões.** Depois de cada aprovação e com as `Descobertas` do orchestrator, anote em `decisoes.md` a decisão do
  usuário e o porquê, a rejeição, a armadilha achada ou o desvio do plano.
- **Fontes do projeto.** Decisão que contraria um ADR aceito (`docs/adr/`), o design ou o manual vivo
  (`openspec/specs/`) passa pelo usuário antes de avançar, e a resposta entra em `decisoes.md`.

## Fases

Cada fase termina no critério em negrito. Não avance sem ele.

### 1. Início

1. Defina o repositório alvo: o diretório atual ou o projeto que o pedido nomeia ("o CRM"). Leia o `AGENTS.md` dele e o
   guia de contribuição, se existir.
2. Localize a entrada. Pedido com caminho ou texto de tarefa: use-o. Pedido só com o nome da funcionalidade: procure no
   repositório alvo o design técnico em `docs/architecture/<nome>/design.md`, o PRD em `docs/prd/<nome>.md` e as
   histórias em `docs/planejamento/<nome>.md`, onde o Grupo 1 os salva; em projeto com a organização antiga, o
   `design.md` em `docs/issues/*/arquitetura/<nome>/` e, ao lado ou na pasta do domínio, o `prd-<nome>.md` e o
   `planejamento-<nome>.md`. Mais de um candidato, ou nenhum: mostre o que achou e pergunte ao
   usuário.
3. Rode `git -C <repo> status --short`. Repositório sujo: pare e pergunte ao usuário.
4. Sem a pasta `openspec/` no repositório alvo, rode `openspec init --tools none` e copie
   `${CLAUDE_SKILL_DIR}/assets/openspec-config.yaml` para `openspec/config.yaml`.
5. Prepare a *branch*: sem fluxo documentado, `feat/<funcionalidade>` a partir da *branch* padrão atualizada; na rodada
   seguinte, volte para a mesma *branch*. Anote o commit base da rodada (`git -C <repo> rev-parse HEAD`).
6. Defina o recorte e o número da rodada, crie a change com `openspec new change <change>` e crie nela o `decisoes.md`
   com a entrada, o recorte e o commit base.

**Entrada lida, repositório e *branch* prontos, change criada com `decisoes.md`.**

### 2. Plano

Despache `software-engineer` com a fase `PLANO`, a entrada, o recorte, o repositório alvo e a change.

**`openspec validate <change> --strict` passa, e a change tem `proposal.md`, `specs/`, `design.md` e `tasks.md` no
formato de `references/plano.md`.**

### 3. Aprovação do Plano

Mostre ao usuário o resumo da change: escopo, cenários das specs, pontos de teste, plano de migração (quando houver) e
as fases com o `Depende de` de cada uma. Pergunte com `AskUserQuestion` se aprova.

Cada ajuste pedido passa pelo **eco**:

1. Grave a frase do usuário, literal, em `decisoes.md`.
2. Despache `software-engineer` com a frase no campo `Ajuste:`.
3. Mostre a frase e, logo abaixo, o `diff` da change, junto do cenário que o ajuste toca. Pergunte com `AskUserQuestion`
   se o diff diz o que foi pedido.
4. Diff que não diz o pedido volta ao passo 2, com a correção do usuário.

**O usuário aprovou o plano e confirmou o eco de cada ajuste.** A aprovação vale também para o plano de migração que a
`database-migration-plan` exige e para os pontos de teste da `tdd`.

### 4. Implementação e Revisão

1. Despache `orchestrator` com a fase `APPLY` e o commit base. Ele roda as fases em ondas, chama o `code-reviewer` no
   fim e faz a análise final.
2. `AGUARDANDO_COMMIT`: para cada commit pendente, mostre `git -C <repo> diff --stat -- <arquivos>` e o diff dos
   arquivos (`git -C <repo> diff -- <arquivos>`), junto do *header* proposto e do aceite da fase. Pergunte com
   `AskUserQuestion` se pode commitar, uma pergunta por commit pendente, com as opções "commitar" e "pedir ajuste".
   Ajuste pedido: grave a frase literal em `decisoes.md`. Retome o orchestrator pelo `SendMessage` com
   `Commit: aprovado` ou `Ajuste: <frase>` para cada entrada.
3. `BLOQUEADO`: pergunte ao usuário com `AskUserQuestion` a decisão que ele devolveu, grave a resposta em `decisoes.md`
   e retome o orchestrator pelo `SendMessage` com ela.
4. `CONCLUÍDO`: confira `git -C <repo> log <commit base>..HEAD --oneline`, `git -C <repo> status --short` e os
   relatórios em `reviews/`, e grave as `Descobertas` em `decisoes.md`.

**O orchestrator devolveu `CONCLUÍDO`, todas as caixas do `tasks.md` estão marcadas, o último `reviews/revisao-*.md` diz
`APROVADO` e `reviews/analise-final.md` existe.**

### 5. Revisão Humana

1. **HTML.** Gere o diff da rodada pela skill `diff-review`:
   `${CLAUDE_PLUGIN_ROOT}/tools/diff-review <repo> <commit base> --open`. O comando sobrescreve o HTML da volta
   anterior, e as notas antigas continuam no navegador.
2. **Entrega.** Mostre o caminho do HTML, os commits, as pendências da análise final, as `SUGGESTION` e os deferidos.
   Pergunte com `AskUserQuestion` quais `SUGGESTION` entram (`multiSelect`); as recusadas vão para
   `reviews/deferidos.md`. Encerre o turno esperando o Markdown das notas ou a aprovação.
3. **Correção.** Grave o Markdown das notas em `reviews/notas-<volta>.md` e despache `software-engineer` com ele no
   campo `Relatório:`, junto das `SUGGESTION` escolhidas. Mostre uma linha por observação, pelo número, com o que foi
   feito ou por que não foi, e o `diff` da correção, e pergunte com `AskUserQuestion` se pode commitar. Com a aprovação,
   commite só com o *header*; com ajuste, devolva a frase ao `software-engineer`. Volte ao passo 1.

**O usuário aprovou a revisão.**

### 6. Encerramento

1. Rode de novo os testes e o lint do repositório alvo e `openspec validate <change> --strict`.
2. Leve cada item de `reviews/deferidos.md` para `openspec/backlog.md`, uma linha por item com a change de origem.
3. Rode `openspec archive <change> --yes`: a spec da rodada entra em `openspec/specs/`, e a change vai para
   `openspec/changes/archive/<data>-<change>/`.
4. Rode `${CLAUDE_SKILL_DIR}/scripts/encerrar-change.sh <repo> <change>`, que lista o que será apagado sem apagar nada.
5. Mostre ao usuário a saída dos testes, o `git -C <repo> status --short` do arquivamento e a lista do script, e
   pergunte com `AskUserQuestion` se pode encerrar. Com a aprovação:
   1. Commite o arquivamento (`docs: archive <change>`), para a change ficar no histórico do Git.
   2. Rode o script de novo com `--apagar` e commite a remoção (`chore: remove archived <change>`).

**A spec da rodada está em `openspec/specs/`, os deferidos em `openspec/backlog.md`, a pasta da change não existe mais
no disco e os dois commits estão no histórico.** Feche com uma linha sobre o que foi entregue e os deferidos que já
podem virar a próxima rodada.

## Despacho

Todo despacho leva estes campos, e nada da conversa além deles. O agente não tem o seu contexto. O orchestrator e o
code-reviewer usam os mesmos campos nos despachos deles.

```text
Fase: <PLANO | APPLY | correção>
Change: <change> (<repo>/openspec/changes/<change>/)
Repositório alvo: <repo>/
Entrada: <caminho do design.md, do PRD e das histórias, ou o texto da tarefa>
Recorte: <histórias ou camada da rodada, ou "entrada inteira">
Commit base: <sha>                      (APPLY, revisão)
Grupo de tarefas: <número e título>     (APPLY de uma fase)
Sonar: <caminho do relatório>           (revisão)
Relatório: <caminho em reviews/>        (correção)
Ajuste: <frase literal do usuário>      (eco da aprovação)
```
