# Hackathon AI Software Engineering: plugin

Plugin do Claude Code (`hackathon-ai-swe`) com **agentes e skills** que cobrem o ciclo de engenharia de software, construído
por frentes de trabalho: produto, arquitetura, implementação, qualidade, DevOps e documentação.

```
ideia vaga → descoberta → PRD → épicos e histórias → design de UX → arquitetura, API e ADRs → implementação → qualidade → operação
```

## Frentes do plugin

O plugin é único e construído por frentes de trabalho.

| Frente | Agentes |
|---|---|
| Produto, Discovery e UX | `product-manager`, `designer` |
| Arquitetura e Engenharia de Software | `solutions-architect` |
| Implementação: backend, frontend e dados | `orchestrator`, `software-engineer` (no papel de `backend-engineer` e `frontend-engineer`) |
| Qualidade, Testes e Segurança | `qa-engineer`, `security-reviewer`, `code-reviewer` |
| DevOps, SRE e Operações | `devops-engineer` |
| Documentação e Conhecimento Técnico | `tech-writer` |

## O que faz

Cada agente conversa em português do Brasil, faz poucas perguntas, usa as skills dele e **só salva um arquivo depois de
você aceitar o resultado**. O que faltar vira pergunta em aberto, premissa marcada ou `A definir`: eles não inventam
números, prazos nem decisões.

### Agentes (`.claude/agents/`)

| Agente | Use quando você disser | Skills que usa | Entrega |
|---|---|---|---|
| `product-manager` | "tenho uma ideia de sistema", "vale a pena construir?", "escreve o PRD", "quebra isso em histórias" | `product-discovery`, `prd-writing`, `technical-planning` | Descoberta, PRD, épicos e histórias com critérios de aceite |
| `designer` | "desenha as telas", "fluxo do usuário", "paleta e tipografia", "roteiro da conversa do agente" | `product-design` | Especificação de design (UX, visual, conversa) |
| `solutions-architect` | "qual arquitetura usar", "desenha a API", "documenta essa decisão", "monolito ou microsserviços" | `repo-orientation`, `architecture-patterns`, `api-design`, `adr-writer` | Decisão defendida, design técnico, contrato de API, ADRs |
| `orchestrator` | (chamado pela `implement-feature`) | — | Fases da rodada em ondas, commits aprovados, revisão do PR e análise final |
| `software-engineer` | "implementa o endpoint", "faz a tela", "corrige o que a revisão apontou" | `backend-patterns`, `frontend-patterns`, `database-migration-plan`, `tdd`, `verification-before-completion`, `receiving-code-review` | Change do OpenSpec, código com teste e correções |
| `code-reviewer` | "revisa esse PR", "essa entrega pode ir para merge?" | `code-review-reliability` | Relatório único com gravidade, recomendação e veredito |
| `qa-engineer` | "revisa a qualidade desse PR", "prova esse bug com um teste" | `code-review-reliability`, `test-generation` | Relatório e testes de regressão |
| `security-reviewer` | "revisa a segurança desse PR", "dá pra uma empresa ver dados da outra?" | `code-review-reliability`, `secret-handling-review` | Relatório com a requisição que explora cada falha |
| `devops-engineer` | "monta a observabilidade", "instrumenta essa rota", "cria a migração dessa tabela", "configura o CI", "esse deploy está pronto?" | `observability-structure`, `observability-coverage`, `liquibase-migration`, `synchro-github-actions-pipeline`, `synchro-gitlab-ci-pipeline`, `deploy-readiness` | Stack, instrumentação, migração reversível, pipeline e checklist de deploy |
| `tech-writer` | "documenta esse projeto", "cria o README", "a doc precisa mudar com esse PR?" | `source-grounded-documentation`, `impact-aware-documentation` | `README.md` e `docs/` fiéis à fonte, ou só o que a mudança afeta |

Ordem natural quando o pedido toca em mais de um: `product-manager`, depois `designer` e `solutions-architect`.

**graphify (opcional).** O `solutions-architect` consulta o grafo do código quando existir `graphify-out/` no repositório alvo, para entender dependência e impacto. O `graphify` é uma ferramenta de linha de comando (pacote `graphifyy`) e este plugin não traz a skill dele: no repositório alvo, rode `graphify install --project` e gere o grafo com `/graphify .`. Sem o grafo, a `repo-orientation` segue sozinha.

Para implementar, peça a funcionalidade em rodadas pequenas: a skill `implement-feature` conduz o plano, as fases, a
revisão do PR e o encerramento. Observabilidade, migração, CI e deploy são do `devops-engineer`; a documentação do
repositório é do `tech-writer`.

### Skills (`.claude/skills/`)

| Skill | O que faz |
|---|---|
| `product-discovery` | Transforma uma ideia em hipóteses testáveis, separa evidência de suposição e termina com uma recomendação |
| `prd-writing` | Escreve o PRD a partir da descoberta ou de notas soltas, sem inventar números |
| `technical-planning` | Quebra o PRD em épicos, histórias e critérios de aceite verificáveis, com rastreabilidade |
| `product-design` | Gera a especificação de design: fluxos, telas e estados, tokens visuais e roteiro de conversa |
| `repo-orientation` | Mapeia a estrutura, os comandos e as convenções de um repositório existente; usa o grafo do `graphify` quando houver `graphify-out/` |
| `architecture-patterns` | Conduz uma decisão de arquitetura, do requisito a uma recomendação defendida, com diagramas C4 em Mermaid |
| `api-design` | Desenha o contrato de uma API e julga se uma mudança é compatível ou quebra clientes |
| `adr-writer` | Registra decisões técnicas como ADRs, com índice e numeração sequencial |
| `implement-feature` | Conduz uma rodada de implementação: change do OpenSpec, plano aprovado, fases com commit aprovado, revisão do PR e encerramento com limpeza da change |
| `backend-patterns` | Onde fica cada código FastAPI, validação na fronteira e isolamento por organização |
| `frontend-patterns` | Estrutura de tela React, cliente gerado, cache, formulário e os estados de carregando, vazio e erro |
| `database-migration-plan` | Mudança de schema com plano aprovado e rollback provado só em banco local |
| `code-review-reliability` | Revisão com prova, gravidade, escopo e veredito |
| `test-generation` | Testes para código existente, com o teste de regressão falhando antes da correção |
| `secret-handling-review` | Busca de segredo exposto, com valores mascarados |
| `diff-review` | Página de revisão de diff para uma pessoa anotar |
| `observability-structure` | Monta a stack LGTM+Alloy e o `resources/observability/` a partir de templates, parametrizada pelo serviço |
| `observability-coverage` | Instrumenta o código no padrão canônico (traces, métricas, logs com `trace_id`) ou audita a cobertura num PR |
| `liquibase-migration` | Migração de schema com Liquibase, changeset com `--rollback` provado, só em banco local |
| `synchro-github-actions-pipeline`, `synchro-gitlab-ci-pipeline` | Pipelines de CI no padrão Synchro: cria, revisa ou migra de GitLab para GitHub |
| `deploy-readiness` | Checklist pré/pós de deploy no layout k8s/ArgoCD, com veredito PRONTO/NÃO PRONTO e rollback |
| `source-grounded-documentation` | Cria o `README.md` e o `docs/` inicial fiel a código, teste, configuração e CI verificáveis |
| `impact-aware-documentation` | Atualiza só o que um PR, MR ou diff entre branches afeta na documentação |
| `regen-eval` | Avalia uma skill por regeneração: usa um projeto real como gabarito e compara o que a skill reproduz |
| `tdd`, `verification-before-completion`, `receiving-code-review` | Teste antes do código, prova antes de dizer "pronto" e correção conferida, usadas pelo `software-engineer` |

## Onde ficam os resultados

Os arquivos só são criados depois do seu aceite. `<nome>` é minúsculo e com hífens, o mesmo em todos os arquivos
da funcionalidade.

| Entregável | Caminho |
|---|---|
| Descoberta | `docs/discovery/<nome>.md` |
| PRD | `docs/prd/<nome>.md` |
| Planejamento (épicos e histórias) | `docs/planejamento/<nome>.md` |
| Design de UX | `docs/design/<nome>.md` |
| Design técnico e diagramas | `docs/architecture/<nome>/design.md` |
| Decisões técnicas | `docs/adr/NNNN-titulo.md`, com índice em `docs/adr/README.md` |
| Plano de uma rodada de implementação | `openspec/changes/<change>/`, apagada no encerramento depois de commitada |
| Comportamento entregue (manual vivo) | `openspec/specs/<capacidade>/spec.md` |
| Itens deferidos nas revisões | `openspec/backlog.md` |

A rastreabilidade é `RF-xx` → `HU-xx` → componente do design → ADR. Os ADRs com status `Aceito` valem para as próximas
decisões: siga-os ou substitua com um novo ADR.

## Como usar

**Dentro deste repositório.** Abra o Claude Code na raiz. Os agentes e as skills de `.claude/` são carregados
automaticamente, e você pode pedir em linguagem natural:

```text
Tenho uma ideia: um CRM pequeno para acompanhar oportunidades comerciais. Vale a pena construir?
Escreve o PRD a partir dessa descoberta.
Quebra o PRD em histórias com critérios de aceite.
Qual arquitetura usar para isolar os dados de cada organização?
Documenta essa decisão como ADR.
vamos começar pelo backend: implementa só a parte de organizações do design de oportunidades
agora a API de oportunidades: cadastrar, listar, ver e mudar o estágio
revisa tudo que foi feito em oportunidades antes de eu abrir o PR
```

A implementação usa o OpenSpec: `npm install -g @fission-ai/openspec@1.4.1`.

**Como plugin (instalação).** O repo é um plugin (`hackathon-ai-swe`) e também o próprio marketplace (`hackathon-synpower`).
Em qualquer projeto, dentro do Claude Code:

```text
/plugin marketplace add edoardap/hackathon-synpower
/plugin install hackathon-ai-swe@hackathon-synpower
```

Ou, no terminal:

```bash
claude plugin marketplace add edoardap/hackathon-synpower
claude plugin install hackathon-ai-swe@hackathon-synpower
```

Para só experimentar, sem instalar, a partir da raiz do repo: `claude --plugin-dir .`

**O que foi testado.** Instalamos o plugin a partir de uma cópia git local, com a configuração isolada: ele ficou
`enabled`, e a cópia instalada trouxe as skills e os agentes de `.claude/`. O comando acima com `edoardap/hackathon-synpower`
só funciona depois que o `marketplace.json` estiver publicado no GitHub, e esse caminho em si ainda não foi exercitado.

**Versão.** O `plugin.json` fixa a versão (`0.1.0`). Quem já instalou **só recebe atualização quando a versão muda**, então
aumente o número a cada entrega. Para atualizar: `claude plugin update hackathon-ai-swe@hackathon-synpower`.

Ao criar um agente novo, acrescente o arquivo dele em `agents` no `plugin.json`, porque o manifesto não aceita pasta de
agentes.

## Como sabemos que funciona

Os testes usam o `claude plugin eval` do Claude Code e checam a **ativação**: o Claude escolhe a skill ou o agente quando
deveria e não escolhe quando não deveria. Os casos e os resultados estão em [`evals/`](evals/README.md).

## Estrutura do repositório

```
.claude-plugin/
  plugin.json          manifesto do plugin
  marketplace.json     permite instalar o plugin por marketplace
.claude/
  agents/<agente>.md   um arquivo por agente
  skills/<skill>/      um diretório por skill
    SKILL.md           frontmatter, gatilhos, fluxo e validação
    references/        padrões, checklists e material de consulta
    assets/            templates reutilizáveis
evals/plugin-eval/     casos e resultados do `claude plugin eval`
hooks/hooks.json       gancho que bloqueia segredos e pede confirmação de todo `git commit`
tools/, adapters/, config/   secret-guard e diff-review, usados pelo gancho e pelas skills
tests/                 testes das ferramentas: `sh tests/run.sh`
AGENTS.md              roteamento e regras para todos os agentes
```

## Como adicionar um agente ou uma skill

1. Crie `.claude/agents/<nome>.md` ou `.claude/skills/<nome>/SKILL.md`.
2. Escreva a descrição com os pedidos que devem ativá-la, e o que não deve.
3. Acrescente a linha correspondente na tabela de roteamento do `AGENTS.md`.
4. Skills entram no plugin só de existir na pasta. Para agente novo, liste o arquivo em `agents` no `plugin.json`, porque o manifesto exige caminhos terminados em `.md`.
5. Crie os casos em `evals/plugin-eval/` e aumente a `version` do `plugin.json`.

## Convenções

As regras de trabalho (não inventar dados, perguntar pouco, confirmar antes de seguir, formato dos commits) estão em
[`AGENTS.md`](AGENTS.md).

Referências do hackathon: <https://agentskills.io>.
