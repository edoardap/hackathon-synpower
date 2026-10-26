---
name: observability-coverage
description: 'Política única de "onde o sinal de observabilidade pertence", em dois modos sobre o mesmo repositório Python/FastAPI/Dagster com OpenTelemetry. MODO AUTOR, durante a implementação: instrumenta o código no padrão canônico — chama o setup_opentelemetry, cria span manual na fronteira de negócio e carimba o trace_id no log. Use ao "instrumentar", "adicionar tracing/métrica/log", "dar observabilidade a essa rota/asset/consumo de fila/chamada externa". MODO REVISOR, no code review: audita diff, branch ou repo contra a política e devolve relatório com arquivo:linha, gravidade, escopo e veredito, sem escrever instrumentação. Use ao "revisar se o logging/telemetria está coberto", "falta log/observabilidade nesse PR?", "auditoria de observabilidade", e quando despachada numa revisão de PR.'
---

# Observability Coverage

Uma política só, dois modos. A política responde **onde um sinal de observabilidade pertence**: na fronteira de confiança,
no I/O externo, no ramo de `except`, no retry, na transição de estado ou de transação. O **modo autor** emite o sinal ali
enquanto implementa; o **modo revisor** cobra o sinal ali enquanto revisa. É a mesma lista nos dois lados, e esta skill é
a dona dela.

Por que isso importa: a stack de destino (LGTM+Alloy — Grafana, Loki, Tempo, Prometheus) só **mostra** o que o código
**emite**. Sem emissão, os painéis ficam vazios e, pior, o código vira uma caixa-preta em produção: quando uma requisição
falha às 3h, não há span que diga onde parou nem log com `trace_id` que ligue a linha de log ao trace. Observabilidade não
é decoração: é a única forma de saber o que o sistema fez com um pedido real depois que ele saiu da sua máquina.

A **estrutura** (subir Alloy, apontar OTLP para 4317/4318, rotear traces→Tempo, métricas→Prometheus, logs→Loki) é da skill
irmã `observability-structure`. Esta skill assume a estrutura pronta e trata do **conteúdo**: preenche a estrutura com
sinal (autor) e depois audita se o sinal está onde deveria (revisor).

Nos caminhos abaixo, `${CLAUDE_SKILL_DIR}` é a pasta desta skill (`.claude/skills/observability-coverage/`).
Repositórios alvo em `/home/fafnir/Projects/Synpower/`: `ai-agents`, `data-pipeline-orchestrator`, `extrator-ai-gov`
(Python/uv, FastAPI + Dagster, layout `src/shared/...`, OpenTelemetry).

## A política: onde o sinal pertence

Cada ponto abaixo é uma fronteira onde o sistema cruza de um mundo para outro — e é exatamente nessas fronteiras que
produção falha sem deixar rastro. O autor emite; o revisor cobra. O "porquê" é o que separa cobrir de encher de ruído.

### Lacunas (sinal faltando — o sistema fica cego)

- **`except` que engole o erro.** Um `except` que faz `pass`, só retorna `None` ou devolve um fallback sem registrar nada
  apaga a falha. Em produção o sintoma aparece longe da causa e não há como voltar. O ramo de erro é o lugar mais caro
  para não ter sinal: registre o erro (`logger.exception` ou `span.record_exception` + `set_status(ERROR)`).
- **Chamada a serviço externo sem span.** HTTP, banco, fila, LLM — toda ida à rede pode ficar lenta, falhar ou dar
  *timeout*, e é onde mais tempo se perde. Sem span, o trace não mostra a latência nem o erro dessa dependência. Em
  `httpx` e `sqlalchemy` a instrumentação automática já cria o span (ver modo autor); fila, LLM e cliente de terceiros
  sem instrumentador precisam de span manual.
- **Retry silencioso.** Um laço que tenta de novo sem registrar a tentativa esconde instabilidade: o sistema "funciona"
  depois de três falhas e ninguém vê que a dependência está degradada. Cada tentativa que falhou é um sinal (log em
  `WARNING` ou evento no span com o número da tentativa).
- **Transição de estado ou transação sem rastro.** Pedido que vira "pago", documento que vira "processado", `commit`/
  `rollback` — são os fatos de negócio que alguém vai querer auditar ou reconstruir. Sem log ou atributo de span com o
  identificador e o estado novo, a linha do tempo do negócio some.
- **Rota ou endpoint sem métrica.** Sem contagem e latência por rota, não dá para saber se um endpoint está sendo usado,
  se quebrou ou se ficou lento. A instrumentação de servidor cobre o caso comum; endpoint crítico de negócio pode pedir
  métrica própria.
- **Log sem `trace_id`.** Um log solto não liga à requisição que o gerou. Com `trace_id` no registro, o Loki e o Tempo se
  cruzam: do log você pula pro trace e vice-versa. Sem ele, cada log é uma ilha. (Ver a regra do `trace_id` no modo autor
  — o padrão canônico resolve isso globalmente via `LoggingInstrumentor`.)

### Ruído (sinal demais — o sinal útil se perde e a conta sobe)

- **Log dentro de loop quente.** Um `logger.info` por item num laço de milhares vira megabytes no Loki e esconde o que
  importa. Logue o resumo (quantos, quanto tempo), não cada volta.
- **`debug` no caminho de produção.** Log em nível `debug` no fluxo normal ou polui ou é descartado pelo nível de
  produção — nos dois casos não serve. Deixe `info` para o marco e `debug` só para diagnóstico local.
- **Log redundante.** Logar "vou chamar X", "chamei X", "X voltou" em volta de uma chamada que já tem span triplica o
  volume e não diz nada que o span não diga. Deixe o span contar a chamada; logue só o que o span não captura.
- **Log vazando PII ou segredo (o mais grave).** Despejar o corpo inteiro da requisição, um token, uma senha, um CPF ou
  um e-mail no log manda dado sensível pro Loki, onde fica retido e visível a quem tem acesso aos painéis. Isto é um
  achado de segurança, não só de ruído: logue identificadores, não conteúdo sensível. A caça a segredo em geral é da skill
  `secret-handling-review` — mas **apontar um log que vaza segredo ou PII é válido e esperado aqui**.

## Modo autor

Durante a implementação, ao escrever rota FastAPI, asset Dagster, consumo de fila ou chamada externa, instrumente no padrão
canônico do projeto. A instrumentação automática já cobre o caso comum; você só adiciona span manual nas fronteiras de
**negócio** que o automático não vê.

**Comente o mínimo.** A instrumentação deve documentar a si mesma: o nome do span e os atributos dizem o que está
acontecendo. Reduza os comentários ao estritamente necessário — só o *porquê* de algo não óbvio (uma fronteira sutil, uma
decisão de não instrumentar). Um comentário que repete o que o span ou a linha já diz é ruído; prefira um nome de span
claro a um comentário.

### O `setup_opentelemetry` canônico

A versão canônica já vem embutida nesta skill: **`${CLAUDE_SKILL_DIR}/assets/opentelemetry_setup.py`**. Copie-a para o
`src/shared/logging/opentelemetry_setup.py` do repo alvo (ou alinhe o que já existe a ela). Ela é autossuficiente — você
não depende de nenhum outro repositório estar presente.

Esse template é a versão completa que hoje vive no `data-pipeline-orchestrator`; ela reúne tudo o que importa:

- **Métricas** — `MeterProvider` com `PeriodicExportingMetricReader` (intervalo de 15s).
- **Atributo de recurso `deployment.environment`** — separa `local`/`dev`/`prod` nos painéis.
- **Hook que renomeia o span do `httpx`** para `"{método} {host}"` (sem ele, todo span HTTP sai com o mesmo nome e o Tempo
  não distingue as chamadas).
- **Instrumentadores automáticos** — `LoggingInstrumentor(set_logging_format=True)`, `HTTPXClientInstrumentor` (com o hook
  acima) e `SQLAlchemyInstrumentor`.
- **Helpers** `get_current_trace_id()` / `get_current_span_id()` (formatam em hex).

Cuidado com a versão **desatualizada** que ainda está no `extrator-ai-gov`, no arquivo
`src/shared/logging/opentelemtry_setup.py` (**repare no typo do nome — "opentelemtry"**): ela é um subconjunto antigo —
não tem métricas, nem `deployment.environment`, nem o hook do `httpx`. Ao tocar aquele repo, substitua-a pelo template de
`assets/` e corrija o nome do arquivo. Assinatura canônica:

```python
def setup_opentelemetry(
    service_name: str,
    endpoint: str | None,
    *,
    environment: str = "local",
    export_traces: bool = False,
    export_metrics: bool = False,
) -> TracerProvider: ...
```

Exporters são OTLP gRPC com `insecure=True`, apontando para o Alloy. As variáveis de ambiente do padrão são `OTEL_ENDPOINT`,
`OTEL_EXPORT_TRACES` e `OTEL_EXPORT_METRICS` — leia-as na configuração, não espalhe `os.getenv` pelo código de negócio.

### Onde chamar

Chame `setup_opentelemetry` **uma vez, no arranque do processo**, antes de servir qualquer pedido:

- FastAPI: no startup da app (no `lifespan` ou antes de criar o `app`), passando o `service_name` do serviço.
- CLI / script: no `main`, antes da primeira chamada de negócio.
- Dagster: na inicialização do processo que roda os assets.

O que a instrumentação automática já cobre, você **não** reinstrumenta à mão: `httpx` (toda chamada HTTP de saída),
`sqlalchemy` (toda query) e o `logging` (formato e contexto). Span manual é só para a fronteira de negócio que essas libs
não enxergam.

### Span manual na fronteira de negócio

Asset Dagster, lógica de domínio, consumo de fila, chamada a um cliente de LLM sem instrumentador — ali o automático não
cria span. Crie um com atributos padronizados (identificadores, não conteúdo sensível) e marque o erro no `except`:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def processar_documento(documento_id: str, organization_id: str) -> None:
    with tracer.start_as_current_span("processar_documento") as span:
        span.set_attribute("documento.id", documento_id)
        span.set_attribute("organization.id", organization_id)
        try:
            # ... trabalho de negócio ...
            span.set_attribute("documento.status", "processado")  # transição de estado
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            logger.exception("falha ao processar documento", extra={"documento_id": documento_id})
            raise
```

Nomeie o span pela operação de negócio (`processar_documento`), não pela função genérica. Use atributos para o que você vai
querer filtrar no Tempo (id do recurso, organização, estado), nunca para o corpo inteiro nem para segredo.

### Regra do `trace_id` no log

Todo log precisa carregar o `trace_id` para cruzar com o trace no Tempo. O padrão canônico resolve isso de graça: o
`LoggingInstrumentor().instrument(set_logging_format=True)` injeta o contexto de trace no formato de log, então um
`logger.info(...)` dentro de um span já sai com o `trace_id`. Para incluir o id em um campo seu (um JSON estruturado, por
exemplo), use `get_current_trace_id()`. O que você garante como autor: **logar dentro do span** (fora dele não há
`trace_id` para carimbar) e não desligar o formato do instrumentador.

## Modo revisor

No code review, **audite** o código contra a política e devolva um relatório. Aqui você **não escreve instrumentação** —
só lê e aponta. É plugável no fluxo do `code-reviewer`. O formato é o mesmo da skill `code-review-reliability`: prova com
`arquivo:linha`, gravidade pelo efeito, escopo explícito, veredito.

### Como auditar

1. **Alcance.** Defina o que está em revisão: o diff (`git diff <base>...HEAD`), os arquivos, a branch ou o repo. Leia
   quem chama e quem é chamado pelo código alterado — a lacuna costuma estar na fronteira que o diff só encosta.
2. **Localize as fronteiras.** Passe a política ponto a ponto sobre o código: procure cada `except`, cada chamada a rede
   (HTTP, banco, fila, LLM), cada laço de retry, cada transição de estado/`commit`, cada rota, cada `logger.*`.
3. **Classifique cada ocorrência.** Para cada fronteira, decida: tem o sinal que a política pede? É lacuna (falta sinal)
   ou ruído (sinal demais, `debug` em produção, PII/segredo no log)?
4. **Prove.** Todo achado vem com `arquivo:linha`, o trecho atual, **por que** é lacuna ou ruído e **o efeito em
   produção** (que painel fica cego, que investigação trava, que dado vaza). Suspeita sem efeito concreto vira pergunta,
   não achado.
5. **Separe o escopo.** `IN_SCOPE` é fronteira que a mudança revisada introduz ou deveria cobrir. `OUT_OF_SCOPE` é lacuna
   que já existia e a mudança não toca: entra no relatório como tarefa, sem reprovar.
6. **Relatório e veredito.** Liste os achados por gravidade e feche com `APROVADO` ou `REPROVADO`.

### Gravidade (pelo efeito em produção)

| Gravidade    | Quando                                                            | Exemplos                                                                                                             |
| ------------ | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `CRITICAL`   | Dado sensível exposto, ou cegueira total num caminho de falha    | Log vazando PII, token ou segredo; `except` que engole erro num fluxo de negócio crítico sem nenhum rastro         |
| `WARNING`    | Investigação fica muito mais difícil, sem vazamento              | Chamada externa sem span; retry silencioso; transição de estado sem rastro; rota sem métrica; log sem `trace_id`    |
| `SUGGESTION` | Ruído ou polimento que não cega nem vaza                         | Log em loop quente; `debug` no caminho de produção; log redundante em volta de span                                |

O veredito é `REPROVADO` quando sobra algum achado `IN_SCOPE` com gravidade `CRITICAL` ou `WARNING`. Caso contrário,
`APROVADO`. O revisor só lê: comandos servem para localizar (`git diff`, `grep`) e para checar, nunca para corrigir —
instrumentar é do autor.

### Formato do relatório

```text
# Auditoria de observabilidade — <alcance>

## Achados

### [GRAVIDADE] <título curto> — IN_SCOPE | OUT_OF_SCOPE
- Local: <arquivo:linha>
- Trecho: <o código atual>
- Por quê: <lacuna ou ruído, e qual ponto da política>
- Efeito em produção: <que painel fica cego / que investigação trava / que dado vaza>

(repita por achado; o mesmo defeito em várias linhas é um achado com várias evidências)

## Veredito: APROVADO | REPROVADO
<uma linha justificando pelo pior achado IN_SCOPE>
```

## Quando NÃO usar

- **Montar a stack do zero** (subir Alloy, Tempo, Loki, Prometheus; rotear OTLP; configurar o `deployment.environment` no
  deploy) é da `observability-structure`. Esta skill assume a stack pronta.
- **Caçar segredo em geral** (histórico do Git, `.env`, Dockerfile, CI, chaves hardcoded) é da `secret-handling-review`.
  A exceção: um **log que vaza segredo ou PII** é achado desta skill — é uma falha de cobertura de telemetria, e você a
  aponta aqui.
- Bloquear a leitura do `.env` pelo agente é papel do hook do plugin, não desta skill.
