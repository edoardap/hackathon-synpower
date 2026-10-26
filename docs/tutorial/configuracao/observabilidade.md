# Observabilidade com Opik

O hook `observability/adapters/hook.sh` exporta cada turno do Claude Code e do Codex como trace OTLP/HTTP e calcula
heurísticas sobre ele. Esta página ativa o export no **Opik Cloud** e cadastra a regra de avaliação `code_quality`. As
variáveis estão em [Variáveis de Ambiente](./variaveis-de-ambiente.md#observabilidade).

## Ativar o Export

O hook roda no Python do `.venv` (3.11 ou superior, Linux ou macOS) e, sem ele, sai sem fazer nada. Rode `make init`: ele
executa `uv sync` e copia o `.env.example` para `.env` quando o arquivo não existe, e o modelo já traz as variáveis
`OBS_*` e `OPIK_*`.

1. Preencha no `.env`:

   ```text
   OBS_OTLP_ENDPOINT=https://www.comet.com/opik/api/v1/private/otel
   OPIK_API_KEY=<chave criada no Opik>
   OPIK_WORKSPACE=<nome do workspace no Opik>
   ```

   O hook acrescenta `/v1/traces` ao endpoint. Sem `OBS_OTLP_ENDPOINT`, e com `OBS_SPIKE` em `0`, ele sai sem fazer nada
   e sem criar arquivo.

   Opcionais: `OBS_PROJECT` (projeto do Opik, padrão `hackathon-synpower`), `OBS_DISABLED=1` (desliga o hook),
   `OBS_CONTENT=metadata` (ver adiante) e `OBS_ARTIFACT_MAX` (limite em bytes do código e do texto de cada chamada, padrão
   `20000`). O resumo de todas está em [Variáveis de Ambiente](./variaveis-de-ambiente.md#observabilidade).

2. Abra uma sessão e termine um turno. O hook roda em `Stop` e em `SessionEnd`, registrado em `.claude/settings.json` e
   em `.codex/hooks.json`. Cada turno chega ao Opik quando termina; um turno longo só aparece no fim. No Codex, marque o
   workspace como `trusted` e aprove os hooks em `/hooks`; cada mudança em `.codex/hooks.json` pede nova aprovação.

3. Procure o trace no projeto `hackathon-synpower` do Opik (`OBS_PROJECT`; o hook só envia o projeto e o workspace com `OPIK_API_KEY`).
   Se o destino recusar o envio, o trace fica em `.cache/observability/spool/` e segue no próximo `Stop` ou
   `SessionEnd`; erros do hook vão para `.cache/observability/erros.log`. O Opik recusa de vez o trace com mais de 24 h
   (`HTTP 400`, `too_old`): ele sai do spool e fica só no log. Por isso o primeiro disparo sobre uma sessão antiga não
   envia os turnos de mais de um dia.

Para que o conteúdo dos turnos não saia da máquina, use `OBS_CONTENT=metadata`. O que a redação cobre está em
[Segredos](../referencia/segredos.md#reda%C3%A7%C3%A3o-na-observabilidade). Nesse modo o trace mantém a tag
`code_written` sem o código, e as sete regras julgariam uma entrada vazia e cobrariam a chave do provedor:
desative as sete.

## Cadastrar a Regra `code_quality`

A regra online avalia com o Haiku 5.5 os traces com a tag `code_written`, que o hook acrescenta aos turnos que usam
`Write`, `Edit`, `MultiEdit` ou `apply_patch`. A nota de 0 a 1 chega ao trace depois do turno e não interrompe a sessão.
No Claude Code, a escrita em arquivo `.md` não conta: o juiz pontua código, não prosa. No Codex, o `apply_patch` ainda
leva o patch inteiro, `.md` incluído.

1. Em *AI Providers*, na configuração do workspace do Opik, cadastre a chave de um provedor com acesso ao Haiku 5.5. A
   chamada do juiz é cobrada nessa chave: uma por trace com código.

2. Crie uma regra de avaliação online do tipo *LLM-as-judge* no projeto `hackathon-synpower`. Os valores vêm de
   `observability/evaluators/code_quality_rule.json`, que segue o corpo de
   `POST /api/v1/private/automations/evaluators`:

   | Campo      | Valor                                                         |
   | ---------- | ------------------------------------------------------------- |
   | Prompt     | Texto de `observability/evaluators/code_quality.md`           |
   | Variáveis  | `pedido` = `input.value`; `codigo` = `metadata.artifact.code` |
   | Filtro     | `tags` contém `code_written`                                  |
   | Amostragem | `1` (todos os traces filtrados)                               |
   | Modelo     | `claude-haiku-5-5`, temperatura `0`                           |
   | Saída      | `code_quality`, tipo `DOUBLE`                                 |

3. Termine um turno que escreva um arquivo e confira a nota `code_quality` no trace.

As seis regras PASS ou FAIL (`task_completion`, `scope_adherence`, `test_adequacy`, `rules_adherence`,
`minimal_solution` e `security`) se criam pelo guia `observability/evaluators/configurar_regras_no_opik.md`.

Conferido num trace real: a tag `code_written`, `input.value` e `metadata.artifact.code` existem, e o menu *AI
Providers* aceitou o provedor da Anthropic. Ainda não foi conferido se a regra aceita o filtro `tags`, o mapeamento
`input.value` e o nome do modelo. Se recusar algum, ajuste o campo na própria regra e atualize o JSON.

O agente opera o Opik só pelo MCP hospedado (`https://www.comet.com/opik/api/v1/mcp`, com OAuth), sem ler o `.env`. O
servidor está registrado em `.mcp.json` e em `.codex/config.toml`; o Claude Code autentica em `/mcp` e o Codex, com
`codex mcp login opik`. Em todo `list`, `read` e `write`, o agente passa `project_name` = `hackathon-synpower`, e só
cria outro projeto, mesmo de teste, quando o usuário pedir.

## Marcação dos Subagentes

No Claude Code, o hook nomeia cada chamada de subagente `agent:<tipo>`, como `agent:code-reviewer`, e grava
`agent_type` nos metadados de todos os spans dele. O span `agent:<tipo>` leva também `fase`, `change`, `grupo` e `foco`,
lidos das linhas `Fase:`, `Change:`, `Grupo de tarefas:` e `Foco:` do despacho do ciclo `implement-feature` (o despacho
daqui não traz `Foco:`); só entra o valor que casa o padrão do campo. O Codex ainda
não marca os subagentes.

Conferido no Opik: o filtro `metadata.agent_type = "<tipo>"` devolve o span do agente e os spans dele, com o custo de
cada `chat`. O gráfico `span_cost` não aceita agrupamento, então o custo por agente sai da soma dos spans filtrados.

O subagente roda em segundo plano, então o span `agent:<tipo>` guarda só o aviso de início. O relatório que o agente
devolve é o `input.value.message` do span `SubagentHandback`, filho dele; num agente em primeiro plano, é o
`output.value` do próprio `agent:<tipo>`.

## Preços dos Modelos

`observability/config/pricing.toml` guarda o preço em USD por milhão de tokens e alimenta `score.cost_usd`. Os modelos
Sonnet 5.5, Opus 5.5, Haiku 5.5 e Fable 5.1 já constam, conferidos na [página de preços da Anthropic](https://platform.claude.com/docs/en/about-claude/pricing). O Haiku 5.5 só tem a faixa de prompts até 100 mil tokens. Os do Codex e qualquer outro modelo ausente ficam sem preço, e o trace deles sai sem
`score.cost_usd`, até você acrescentar:

```toml
[modelos."<id do modelo>"]
input = <USD por 1 milhão de tokens de entrada>
output = <USD por 1 milhão de tokens de saída>
```
