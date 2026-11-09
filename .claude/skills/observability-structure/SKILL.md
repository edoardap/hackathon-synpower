---
name: observability-structure
description: 'Monta e padroniza a ESTRUTURA de observabilidade de um repositório Python/uv da Synpower: a stack LGTM+Alloy do Docker Compose, os arquivos de resources/observability/, os alvos de Makefile e as variáveis de ambiente, tudo a partir de templates embutidos parametrizados pelo nome do serviço. Use ao "montar a observabilidade", "montar a stack de telemetria", quando "esse serviço novo precisa de Grafana/Prometheus/Loki/Tempo", "padronizar a observabilidade desse repo", ou quando "falta a stack de observabilidade aqui". Prepara o terreno; não instrumenta o código (isso é da observability-coverage) nem configura dashboards.'
---

# Observability Structure

Prepara o terreno de observabilidade de um serviço: a stack de coleta e visualização (Grafana, Prometheus,
Loki, Tempo e Alloy) e os arquivos de configuração, alvos de Makefile e variáveis de ambiente que a sustentam.
A stack só **recebe e mostra** sinal; quem **emite** (trace, métrica, log) é o código do serviço, e instrumentar
é papel da skill irmã `observability-coverage`. Esta skill não decide onde ficam os sinais nem monta dashboard.

Existe porque hoje só o `ai-agents` tem essa estrutura. O `data-pipeline-orchestrator` e o `extrator-ai-gov`
não têm o compose nem o `resources/observability/`, e qualquer serviço novo nasce sem eles. Esta skill é a fonte
única do padrão: aplicada em qualquer repo, deixa a estrutura idêntica à de referência, trocando só o nome do serviço.

Nos caminhos abaixo, `${CLAUDE_SKILL_DIR}` é a pasta desta skill (`.claude/skills/observability-structure/`).

## Os templates (fonte da estrutura)

Esta skill é **autossuficiente**: os arquivos de referência já vêm embutidos em `${CLAUDE_SKILL_DIR}/assets/`, com o
nome do serviço substituído pelo marcador `__SERVICE__`. Você não depende de nenhum repositório estar presente na
máquina — copie o template, troque `__SERVICE__` pelo nome do serviço alvo e pronto.

- `${CLAUDE_SKILL_DIR}/assets/docker-compose.observability.yml`
- `${CLAUDE_SKILL_DIR}/assets/resources/observability/config.alloy`
- `${CLAUDE_SKILL_DIR}/assets/resources/observability/grafana.yml`
- `${CLAUDE_SKILL_DIR}/assets/resources/observability/prometheus.yml`
- `${CLAUDE_SKILL_DIR}/assets/resources/observability/loki.yml`
- `${CLAUDE_SKILL_DIR}/assets/resources/observability/tempo.yaml`

O `ai-agents` é a **implementação viva** desse mesmo padrão (`docker-compose.observability.yml`,
`resources/observability/`, alvos `*-observability` no `Makefile`, bloco OTEL/GRAFANA no `.env.example`). Consulte-o
apenas se precisar conferir uma versão de imagem ou um campo que tenha evoluído desde que os templates foram
embutidos; na dúvida, os templates de `assets/` são a fonte desta skill.

## Princípios

- **Parametrize pelo nome do serviço, nunca copie `synchro-agents` cru.** No `ai-agents` o nome do serviço é
  `synchro-agents` e ele aparece em tudo: nome dos containers (`synchro-agents-grafana`), da rede externa
  (`synchro-agents-prod-network`), dos volumes nomeados (`synchro-agents-grafana-data`), do host no
  `OTEL_ENDPOINT` (`synchro-agents-alloy`), das URLs internas entre serviços dentro do `config.alloy` e do
  `grafana.yml` (`synchro-agents-prometheus`, `synchro-agents-loki`, `synchro-agents-tempo`) e do `external_labels.project`.
  Ao aplicar noutro repo, troque **todas** essas ocorrências pelo nome daquele serviço. Container e volume órfãos
  com o nome errado é o erro mais comum e silencioso.
- **A referência manda.** Não invente versão de imagem, porta nem campo de config. Leia o arquivo correspondente
  no `ai-agents` e espelhe.
- **A stack recebe, o código emite.** Monte os receptores e os bancos de sinal; não escreva instrumentação aqui.
  Deixe o `OTEL_ENDPOINT` apontando para o Alloy do serviço, para a `observability-coverage` ligar o emissor depois.
- **Não sobrescreva arquivo existente sem avisar** (regra do `AGENTS.md`). Se o repo já tem `docker-compose.observability.yml`
  ou um `resources/observability/` parcial, detecte o que existe, mostre a diferença para o padrão e só então alinhe.
- **Pontual, uma vez por serviço.** Isto roda quando o serviço nasce ou quando um repo que divergiu precisa convergir.
  Repo já alinhado não precisa desta skill.
- **Comente o mínimo.** Os templates já vêm enxutos; mantenha assim. Reduza os comentários ao estritamente necessário —
  só o *porquê* de um valor não óbvio (uma porta, uma retenção, um `insecure`). Não anote o que a chave do YAML já diz.

## Procedimento

1. **Descubra o nome do serviço e detecte o que já existe.** Pegue o nome do repo alvo (ex.: `data-pipeline-orchestrator`,
   `extrator-ai-gov`). Liste `docker-compose.observability.yml`, `resources/observability/`, os alvos `*-observability`
   do `Makefile` e o bloco OTEL/GRAFANA do `.env.example`. Classifique cada peça como ausente, parcial ou alinhada.
   Mostre o diagnóstico ao usuário antes de escrever.

2. **Crie ou alinhe o `docker-compose.observability.yml`.** Copie `${CLAUDE_SKILL_DIR}/assets/docker-compose.observability.yml`
   e troque **todo** `__SERVICE__` pelo nome do serviço alvo (um `sed 's/__SERVICE__/<serviço>/g'` resolve). Cinco
   serviços, uma rede externa, um volume nomeado por serviço com estado:

   | Serviço      | Imagem (confira na referência) | Porta/expose | Pontos que não podem faltar |
   |--------------|--------------------------------|--------------|-----------------------------|
   | `grafana`    | `grafana/grafana`              | `${GRAFANA_PORT}:3000` | monta `grafana.yml` como datasource; `GF_SECURITY_ADMIN_*`; healthcheck em `/api/health` |
   | `prometheus` | `prom/prometheus`              | expõe `9090` | `--storage.tsdb.retention.time=15d` e `--web.enable-remote-write-receiver`; healthcheck em `/-/healthy` |
   | `loki`       | `grafana/loki`                 | expõe `3100` | `user: root`; healthcheck em `/ready` |
   | `alloy`      | `grafana/alloy`                | `4317` e `4318` | monta `config.alloy` e o `docker.sock` (ro) para ler logs dos containers; `depends_on` loki saudável |
   | `tempo`      | `grafana/tempo`                | expõe `3200` e `4317` | recebe OTLP do Alloy |

   A rede é `external: true` com `name: <serviço>-prod-network`. Ela precisa existir antes de subir a stack
   (`docker network create <serviço>-prod-network`, ou é criada pelo compose principal do serviço) — confira na etapa 7.

3. **Crie os 5 arquivos de `resources/observability/`.** Copie-os de `${CLAUDE_SKILL_DIR}/assets/resources/observability/`
   com a mesma substituição de `__SERVICE__`. O que cada um faz:

   - **`config.alloy`** — o coração. Pipeline OTel: `otelcol.receiver.otlp` (grpc `0.0.0.0:4317`, http `0.0.0.0:4318`)
     → `otelcol.processor.batch` → três exporters: `otelcol.exporter.prometheus` encaminhando para
     `prometheus.remote_write` (`http://<serviço>-prometheus:9090/api/v1/write`), `otelcol.exporter.loki`, e
     `otelcol.exporter.otlp` para `<serviço>-tempo:4317` com `tls.insecure = true`. Além do OTLP, coleta os logs dos
     containers via `discovery.docker` + `discovery.relabel` + `loki.source.docker`, empurrando para `loki.write` em
     `http://<serviço>-loki:3100/loki/api/v1/push`. O `external_labels` leva `environment` e `project` (o `project` é
     o nome do serviço). Todos os hosts internos usam os nomes de container prefixados — reparametrize.
   - **`grafana.yml`** — provisionamento de datasources (`apiVersion: 1`): Prometheus (`http://<serviço>-prometheus:9090`),
     Loki (`http://<serviço>-loki:3100`) e Tempo (`http://<serviço>-tempo:3200`), todos `access: proxy`, `editable: false`.
   - **`prometheus.yml`** — `global.scrape_interval: 15s` e um scrape do próprio Prometheus. O trabalho pesado de
     ingestão vem do remote-write do Alloy, então este arquivo é enxuto.
   - **`loki.yml`** — Loki single-binary: `auth_enabled: false`, listen `3100`, storage em filesystem sob `/loki`,
     `replication_factor: 1`, `schema v13` com `tsdb`, `allow_structured_metadata: true`.
   - **`tempo.yaml`** — listen `3200`, `distributor.receivers.otlp.protocols.grpc` em `0.0.0.0:4317`, storage local
     em `/tmp/tempo/traces`.

   Nenhum desses arquivos precisa de segredo. O que varia entre repos é só o nome do serviço nos hosts e no `project`.

4. **Adicione os alvos de Makefile.** Defina a variável e os quatro alvos, iguais aos da referência:

   ```make
   OBSERVABILITY_COMPOSE = docker compose -f docker-compose.observability.yml --env-file .env.prod

   up-observability:            $(OBSERVABILITY_COMPOSE) up -d
   down-observability:          $(OBSERVABILITY_COMPOSE) down
   down-volumes-observability:  $(OBSERVABILITY_COMPOSE) down --volumes
   logs-observability:          $(OBSERVABILITY_COMPOSE) logs -f
   ```

   Declare-os no `.PHONY` e mantenha os comentários `##` de ajuda que o repo usar. Confira qual `--env-file` o repo
   adota (a referência usa `.env.prod`); siga o do repo alvo.

5. **Adicione as variáveis ao `.env.example`.** O bloco mínimo, com o host do Alloy parametrizado:

   ```dotenv
   OTEL_ENDPOINT="http://<serviço>-alloy:4317"
   OTEL_EXPORT_TRACES=true
   OTEL_EXPORT_METRICS=true
   GRAFANA_ADMIN_USER="admin"
   GRAFANA_ADMIN_PASSWORD="admin"
   GRAFANA_PORT=9090
   ```

   São exemplos, não segredos — valor real vai no `.env` fora do versionamento. Replique o mesmo bloco no `.env.prod`
   de exemplo, se o repo tiver um.

6. **Aponte o lugar canônico do setup de OTel (sem instrumentar).** No `ai-agents` o consumo dessas variáveis mora em
   `src/shared/config/observability.py` (um `ObservabilityConfig` de pydantic-settings com `SERVICE_NAME`,
   `OTEL_ENDPOINT`, `OTEL_EXPORT_TRACES`, `OTEL_EXPORT_METRICS`) e o provider em `src/shared/logging/opentelemetry_setup.py`.
   Garanta que o repo alvo tenha esse lugar reservado em `src/shared/...`; preenchê-lo (TracerProvider, MeterProvider,
   instrumentação) é da `observability-coverage`. Aqui só se confirma que o endereço existe e que o `.env` alimenta ele.

7. **Confira a rede externa.** A stack não sobe se `<serviço>-prod-network` não existir. Verifique
   (`docker network ls | grep <serviço>-prod-network`); se faltar, crie ou documente que o compose principal do serviço
   a provê.

## Como verificar que funcionou

1. `make up-observability` sobe os cinco containers sem erro.
2. Os healthchecks ficam `healthy`: Grafana em `/api/health`, Prometheus em `/-/healthy`, Loki em `/ready`
   (`docker compose -f docker-compose.observability.yml ps`).
3. Grafana responde na porta `${GRAFANA_PORT}` e lista os três datasources (Prometheus, Loki, Tempo) provisionados.
4. O Alloy está escutando OTLP: as portas `4317` e `4318` do container estão publicadas e os logs do Alloy
   (`make logs-observability`) não mostram erro de conexão com Loki, Tempo ou Prometheus.
5. `docker volume ls` mostra os quatro volumes nomeados com o prefixo do serviço, e nenhum container/volume com o
   nome `synchro-agents` sobrou de um copia-e-cola.
6. `make down-observability` para tudo preservando os volumes; `down-volumes-observability` limpa o estado.

Um sinal de ponta a ponta (trace do serviço chegando no Tempo) só aparece depois que a `observability-coverage`
instrumentar o código — não é escopo desta verificação.

## Quando NÃO usar

- **Repo já alinhado ao padrão.** Se o compose, os 5 arquivos, os alvos e as vars já batem com a referência, não há
  estrutura a montar: vá para a `observability-coverage` (instrumentar o código) ou para a verificação acima.
- **Instrumentar o código** (criar spans, métricas, logs estruturados, ligar o OTel no FastAPI/Dagster) é da
  `observability-coverage`, não desta skill.
- **Criar ou editar dashboards e alertas no Grafana** é de outra skill; aqui só se provisiona os datasources.
- **Um repo que não é um serviço Python/uv da Synpower** foge do padrão de referência; trate caso a caso.
