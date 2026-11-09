"""Export OTLP/HTTP de uma tentativa só, spool em disco e reenvio (D6, D8, D17)."""

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans

from observability.tracing.redacao import LIMITE_ARTEFATO, redigir, sanear, valores_secretos
from observability.tracing.turno import Span, para_otel

# o exportador do SDK repete por ~3 s; o SessionEnd do Codex tem menos
TIMEOUT = 2
LIMITE_SPOOL = 200  # ponytail: descarta os mais antigos; sem política por idade nem tamanho
RECUSA_DO_CORPO = (400, 413, 422)  # 401, 403, 404, 408 e 429 passam quando a chave, o endpoint ou a hora mudam


@dataclass
class Config:
    url: str
    headers: dict
    valores: set
    metadado: bool
    spool: Path
    artefato_max: int = LIMITE_ARTEFATO


def _canal_seguro(url):
    """A chave só sai em https ou para a própria máquina."""
    partes = urlsplit(url)
    return partes.scheme == "https" or partes.hostname in ("127.0.0.1", "localhost")


def configuracao(env, cache):
    """None sem `OBS_OTLP_ENDPOINT`: nada é enviado nem gravado."""
    if not env.get("OBS_OTLP_ENDPOINT"):
        return None
    headers = {}
    if env.get("OPIK_API_KEY") and _canal_seguro(env["OBS_OTLP_ENDPOINT"]):
        headers = {
            "Authorization": env["OPIK_API_KEY"],
            "Comet-Workspace": env.get("OPIK_WORKSPACE", ""),
            "projectName": env.get("OBS_PROJECT", "hackathon-synpower"),
        }
    maximo = env.get("OBS_ARTIFACT_MAX", "")
    return Config(
        url=env["OBS_OTLP_ENDPOINT"].rstrip("/") + "/v1/traces",
        headers=headers,
        valores=valores_secretos(env),
        metadado=env.get("OBS_CONTENT") == "metadata",
        spool=Path(cache) / "spool",
        artefato_max=int(maximo) if maximo.isdigit() else LIMITE_ARTEFATO,
    )


def _registrar(config, turno, corpo, motivo):
    """Uma linha em erros.log ao lado do spool: o hook descarta a saída, e sem isto a recusa some."""
    config.spool.parent.mkdir(parents=True, exist_ok=True)
    linha = f"{time.strftime('%FT%T')} export {turno.atributos.get('thread_id')} {len(corpo)}B {motivo}"
    with (config.spool.parent / "erros.log").open("a") as f:
        f.write(redigir(linha, config.valores) + "\n")


def exportar(turno, config):
    """Um envio do turno, já redigido: True se 2xx, None se o destino recusa o corpo, False se vale repetir."""
    corpo = encode_spans(para_otel(turno)).SerializePartialToString()
    cabecalhos = {"Content-Type": "application/x-protobuf", **config.headers}
    try:
        with urlopen(Request(config.url, corpo, cabecalhos), timeout=TIMEOUT):
            return True
    except HTTPError as erro:
        try:
            detalhe = erro.read(200).decode("utf-8", "replace").replace("\n", " ")
        except (OSError, HTTPException):
            detalhe = ""
        erro.close()
        _registrar(config, turno, corpo, f"HTTP {erro.code} {erro.reason} {detalhe}".strip())
        return None if erro.code in RECUSA_DO_CORPO else False
    except (OSError, HTTPException) as erro:
        _registrar(config, turno, corpo, repr(erro))
        return False


def guardar(turno, config):
    config.spool.mkdir(parents=True, exist_ok=True)
    nome = f"{time.time_ns()}-{uuid.uuid4().hex[:6]}.json"
    tmp = config.spool / f".{nome}.tmp"
    try:
        tmp.write_text(json.dumps(asdict(turno)))
        os.replace(tmp, config.spool / nome)
    finally:
        tmp.unlink(missing_ok=True)
    for antigo in sorted(config.spool.glob("*.json"))[:-LIMITE_SPOOL]:
        antigo.unlink(missing_ok=True)


def reenviar(config):
    """Reenvia o spool em ordem e para no primeiro que vale tentar de novo. True quando o spool esvaziou."""
    for arquivo in sorted(config.spool.glob("*.json")):
        try:
            turno = Span.de_dict(json.loads(arquivo.read_text()))
        except (OSError, ValueError, TypeError, KeyError):  # ilegível: nunca será enviado
            arquivo.unlink(missing_ok=True)
            continue
        if exportar(turno, config) is False:
            return False
        arquivo.unlink(missing_ok=True)  # ponytail: o corpo recusado também sai, sem quarentena
    return True


def enfileirar(turno, config):
    """Redige o turno e o guarda no spool, sem rede."""
    guardar(sanear(turno, config.valores, config.metadado, config.artefato_max), config)
