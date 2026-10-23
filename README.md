# Hackathon AI Software Engineering: Grupo 1 (Produto e Arquitetura)

Plugin do Claude Code (`hackathon-ai-swe`) com **agentes e skills** que cobrem o ciclo de engenharia de software, construído
por frentes de trabalho. Este repositório traz a frente de **Produto e Arquitetura** (Grupo 1): leva uma ideia de sistema
até um design técnico pronto para ser implementado. Os Grupos 2 (implementação, qualidade e segurança) e 3 (DevOps, SRE e
documentação) completam o plugin.

```
ideia vaga → descoberta → PRD → épicos e histórias → design de UX → arquitetura, API e ADRs → (Grupo 2)
```

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
Quem pedir para escrever código, testar ou fazer deploy deve ser direcionado aos Grupos 2 e 3.

### Skills (`.claude/skills/`)

| Skill | O que faz |
|---|---|
| `product-discovery` | Transforma uma ideia em hipóteses testáveis, separa evidência de suposição e termina com uma recomendação |
| `prd-writing` | Escreve o PRD a partir da descoberta ou de notas soltas, sem inventar números |
| `technical-planning` | Quebra o PRD em épicos, histórias e critérios de aceite verificáveis, com rastreabilidade |
| `product-design` | Gera a especificação de design: fluxos, telas e estados, tokens visuais e roteiro de conversa |
| `repo-orientation` | Mapeia a estrutura, os comandos e as convenções de um repositório existente |
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
.claude/agents/       agentes (product-manager, designer, solutions-architect)
.claude/skills/       skills, cada uma com SKILL.md e, quando preciso, assets/ ou references/
.claude-plugin/       plugin.json (o plugin) e marketplace.json (como instalar)
evals/                casos e resultados do `claude plugin eval`
AGENTS.md             regras para todos os agentes e convenções do repositório
```

## Convenções

As regras de trabalho (não inventar dados, perguntar pouco, confirmar antes de seguir, formato dos commits) estão em
[`AGENTS.md`](AGENTS.md).

## Equipe

Grupo 1: Isaac, Maria Eduarda e Andreza.

Referências do hackathon: <https://agentskills.io>.
