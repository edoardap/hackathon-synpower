"""Partes comuns dos leitores de transcript."""

import json
from datetime import datetime
from pathlib import Path

from observability.tracing.turno import Span


def ns(ts):
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return int(dt.timestamp()) * 10**9 + dt.microsecond * 1000


def ler_linhas(caminho):
    """Um registro por linha; a ilegível vira {} e o offset segue valendo."""
    linhas = Path(caminho).read_text(encoding="utf-8").split("\n")  # splitlines quebra em U+2028
    registros = []
    for linha in linhas[:-1]:  # a última é vazia ou ainda está sendo escrita
        try:
            r = json.loads(linha)
        except ValueError:
            r = None
        registros.append(r if isinstance(r, dict) else {})
    return registros


def ler_turnos(transcript, offset, abre_turno, montar, continuacao=None):
    """Turnos a partir da linha `offset` e o offset seguinte (linhas já lidas); o turno que não monta é pulado.

    `continuacao(sobra)` devolve o registro que abre o turno do que vem antes do primeiro prompt, ou None."""
    linhas = ler_linhas(transcript)
    novas = linhas[offset:]
    inicios = [i for i, r in enumerate(novas) if abre_turno(r)]
    if continuacao and (abertura := continuacao(novas[: inicios[0] if inicios else len(novas)])):
        novas, inicios = [abertura, *novas], [0, *(i + 1 for i in inicios)]
    turnos = []
    for a, b in zip(inicios, [*inicios[1:], len(novas)]):
        try:
            turnos.append(montar(novas[a:b]))
        except (KeyError, ValueError, TypeError, AttributeError):
            continue
    return turnos, len(linhas)


def provedor(nome):
    """O Opik só estima custo com provedor, modelo e uso; o nome do atributo muda entre versões da convenção OTel."""
    return {"gen_ai.system": nome, "gen_ai.provider.name": nome}


def ultimo_modelo(filhos):
    return next((f.atributos.get("gen_ai.request.model") for f in reversed(filhos) if f.nome == "chat"), None)


def raiz(inicio, fim, entrada, saida, filhos, codigos):
    """Span do turno. `thread_id` e o executor entram no hook, que conhece a sessão."""
    atributos = {"gen_ai.request.model": ultimo_modelo(filhos)}
    if codigos:
        atributos["opik.tags"] = ["code_written"]
    return Span("turno", inicio, fim, atributos, entrada, saida, "\n\n".join(codigos) or None, filhos=filhos)
