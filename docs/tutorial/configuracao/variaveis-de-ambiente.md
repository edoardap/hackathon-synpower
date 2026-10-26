# Variáveis de Ambiente

Copie o `.env.example` para `.env` e preencha. O `.env` não vai para o Git, e o agente não o lê: só o hook de
observabilidade o carrega, no próprio processo.

## Observabilidade

O hook `observability/adapters/hook.sh` só exporta traces quando `OBS_OTLP_ENDPOINT` está preenchida. O passo a passo
está em [Observabilidade com Opik](./observabilidade.md).

| Variável            | Padrão               | Efeito                                                                                                                             |
| ------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `OBS_OTLP_ENDPOINT` | vazio                | Destino OTLP/HTTP; o hook acrescenta `/v1/traces`. No Opik Cloud: `https://www.comet.com/opik/api/v1/private/otel`                 |
| `OPIK_API_KEY`      | vazio                | Cabeçalho `Authorization`; sem ela, ou com `http://` fora de `127.0.0.1` e `localhost`, nenhum cabeçalho de autenticação é enviado |
| `OPIK_WORKSPACE`    | vazio                | Cabeçalho `Comet-Workspace`; só é enviado com `OPIK_API_KEY`                                                                       |
| `OBS_PROJECT`       | `hackathon-synpower` | Projeto do Opik que recebe os traces; só é enviado com `OPIK_API_KEY`                                                              |
| `OBS_DISABLED`      | `0`                  | Com `1`, o hook sai sem fazer nada                                                                                                 |
| `OBS_CONTENT`       | `full`               | `full` envia prompts e saídas; `metadata` envia só nomes, modelo, tokens, duração e status                                         |
| `OBS_ARTIFACT_MAX`  | `20000`              | Limite, em bytes, do código escrito no turno e do texto de cada chamada ao modelo; o excesso é cortado                             |
| `OBS_SPIKE`         | `0`                  | Com `1`, grava a estrutura dos transcripts, sem valores, em `.cache/observability/spike/`                                          |

O spool, os *offsets* de leitura e o `erros.log` ficam em `observability/` dentro de `.cache/` (ou de `RAS_CACHE_DIR`,
quando definida).
