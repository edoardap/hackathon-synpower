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
| Implementação: backend, frontend e dados | `backend-engineer`, `frontend-engineer` |
| Qualidade, Testes e Segurança | `qa-engineer`, `security-reviewer`, `code-reviewer` |
| DevOps, SRE e Operações | `devops-engineer`, `sre-engineer` |
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

Ordem natural quando o pedido toca em mais de um: `product-manager`, depois `designer` e `solutions-architect`.

**graphify (opcional).** O `solutions-architect` consulta o grafo do código quando existir `graphify-out/` no repositório alvo, para entender dependência e impacto. O `graphify` é uma ferramenta de linha de comando (pacote `graphifyy`) e este plugin não traz a skill dele: no repositório alvo, rode `graphify install --project` e gere o grafo com `/graphify .`. Sem o grafo, a `repo-orientation` segue sozinha.

Quem pedir para escrever código, testar ou fazer deploy deve ser direcionado aos agentes de implementação, qualidade e DevOps.

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
```

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
`enabled`, e a cópia instalada trouxe as 8 skills e os 3 agentes de `.claude/`. O comando acima com `edoardap/hackathon-synpower`
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
