"""O turno como árvore de spans e a conversão em spans OTel."""

from dataclasses import dataclass, field

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import Status, StatusCode, set_span_in_context


@dataclass
class Span:
    """Um nó do turno, em ns; `entrada`, `saida` e `codigo` são o conteúdo, redigido e omitido em `metadata`."""

    nome: str
    inicio: int
    fim: int
    atributos: dict = field(default_factory=dict)
    entrada: str | None = None
    saida: str | None = None
    codigo: str | None = None
    erro: bool = False
    filhos: list["Span"] = field(default_factory=list)

    @classmethod
    def de_dict(cls, d):
        return cls(**{**d, "filhos": [cls.de_dict(f) for f in d["filhos"]]})


def _atributos(span, raiz):
    a = dict(span.atributos)
    for texto, chaves in ((span.entrada, ("input.value", "gen_ai.prompt")), (span.saida, ("output.value", "gen_ai.completion"))):
        if texto is not None:
            # Q5: atributo de entrada/saída da raiz no Opik; 8.3 confirma
            a.update({k: texto for k in chaves if raiz or k.endswith(".value")})
    if span.codigo is not None:
        a["opik.metadata.artifact.code"] = span.codigo
    return {k: v for k, v in a.items() if v is not None}


def _emitir(tracer, span, pai=None):
    s = tracer.start_span(
        span.nome,
        context=set_span_in_context(pai) if pai else None,
        start_time=span.inicio,
        attributes=_atributos(span, pai is None),
    )
    for filho in span.filhos:
        _emitir(tracer, filho, s)
    if span.erro:
        s.set_status(Status(StatusCode.ERROR))
    s.end(end_time=span.fim)


def para_otel(raiz):
    """Spans OTel terminados, prontos para o encoder OTLP."""
    memoria = InMemorySpanExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": "ras-harness"}))
    provider.add_span_processor(SimpleSpanProcessor(memoria))
    _emitir(provider.get_tracer("ras.observability"), raiz)
    return memoria.get_finished_spans()
