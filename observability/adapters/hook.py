"""Hook de observabilidade: exporta um trace por turno novo da sessão."""

import fcntl
import hashlib
import json
import os
import re
import sys
import traceback
from contextlib import contextmanager
from pathlib import Path

from observability.adapters import claude_code, codex
from observability.evaluators.heuristics import MARCA_GUARD, calcular
from observability.tracing import envio

RAIZ = Path(__file__).resolve().parents[2]
CACHE = Path(os.environ.get("RAS_CACHE_DIR") or RAIZ / ".cache") / "observability"
# Valores de string que a estrutura do spike mantém: tags de formato, nunca conteúdo.
DISCRIMINADORES = {
    "type", "subtype", "role", "name", "model", "stop_reason", "status", "event", "kind", "phase",
    "source", "originator", "hook_event_name", "permission_mode", "agent_type", "effort",
}


def forma(valor, chave=""):
    """Chaves e tipos de um JSON; ids viram hash curto."""
    if isinstance(valor, dict):
        return {k: forma(v, k) for k, v in valor.items()}
    if isinstance(valor, list):
        return [forma(v, chave) for v in valor[:3]] + ([f"+{len(valor) - 3}"] if len(valor) > 3 else [])
    if isinstance(valor, str):
        if chave in DISCRIMINADORES:
            return valor[:60]
        if chave.lower().endswith("id"):
            return "#" + hashlib.sha1(valor.encode()).hexdigest()[:6]
        return f"<str {len(valor)}{' guard' if MARCA_GUARD in valor else ''}>"
    return valor


def gravar_estrutura(executor, sid, evento, payload, transcritos):
    """OBS_SPIKE=1: grava a forma do payload e dos transcritos em spike/ (D13)."""
    pasta = CACHE / "spike"
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / f"{executor}-{_seguro(sid)}-{evento}.payload.json").write_text(json.dumps(forma(payload), indent=1))
    for arquivo in transcritos:
        saida = pasta / f"{executor}-{_seguro(sid)}-{arquivo.stem}.shape.jsonl"
        with arquivo.open() as src, saida.open("w") as dst:
            for n, linha in enumerate(src, 1):
                try:
                    dst.write(json.dumps({"n": n, "forma": forma(json.loads(linha))}) + "\n")
                except ValueError:
                    dst.write(json.dumps({"n": n, "forma": "<linha invalida>"}) + "\n")


def transcritos_da_sessao(transcript):
    """O transcript e os de subagente, em <transcript sem extensão>/subagents/."""
    principal = Path(transcript)
    return [principal, *sorted((principal.with_suffix("") / "subagents").glob("*.jsonl"))]


LEITORES = {"claude-code": claude_code.ler_turnos, "codex": codex.ler_turnos}


def _seguro(sid):
    """O id da sessão como nome de arquivo."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", sid)


@contextmanager
def travada(sid):
    """Serializa os disparos da sessão (Stop e SessionEnd) na leitura, no envio, no spool e no offset (D17)."""
    pasta = CACHE / "locks"
    pasta.mkdir(parents=True, exist_ok=True)
    with (pasta / f"{_seguro(sid)}.lock").open("w") as trava:
        fcntl.flock(trava, fcntl.LOCK_EX)
        yield  # o flock cai quando o arquivo fecha, inclusive com o processo morto


def _arquivo_offset(sid):
    return CACHE / "offsets" / _seguro(sid)


def ler_offset(sid):
    try:
        return int(_arquivo_offset(sid).read_text())
    except (OSError, ValueError):
        return 0


def gravar_offset(sid, offset):
    arquivo = _arquivo_offset(sid)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    tmp = arquivo.with_suffix(".tmp")
    tmp.write_text(str(offset))
    os.replace(tmp, arquivo)


def anotar(turno):
    """Heurísticas e tags no span raiz; antes da redação, que no modo metadado corta a saída que o guard marca."""
    scores, tags = calcular(turno)
    turno.atributos.update({f"opik.metadata.score.{k}": v for k, v in scores.items()})
    if tags:
        turno.atributos["opik.tags"] = [*turno.atributos.get("opik.tags", []), *tags]


def main(executor):
    payload = json.load(sys.stdin)
    sid = payload.get("session_id") or ""
    transcript = payload.get("transcript_path") or ""
    evento = payload.get("hook_event_name") or "evento"
    if not sid or not Path(transcript).is_file():
        return
    if os.environ.get("OBS_SPIKE") == "1":
        gravar_estrutura(executor, sid, evento, payload, transcritos_da_sessao(transcript))
    config = envio.configuracao(os.environ, CACHE)
    if not config or evento not in ("Stop", "SessionEnd"):
        return
    # claude -p cancela o Stop: os dois eventos leem do offset (D1)
    with travada(sid):
        turnos, offset = LEITORES[executor](transcript, ler_offset(sid))
        for turno in turnos:
            turno.atributos.update({"ras.executor": executor, "thread_id": sid})
            anotar(turno)
            envio.enfileirar(turno, config)
        gravar_offset(sid, offset)  # antes da rede: o que já está no spool não se reenvia
        envio.reenviar(config)


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else "")
    except BaseException:
        CACHE.mkdir(parents=True, exist_ok=True)
        with (CACHE / "erros.log").open("a") as f:
            f.write(traceback.format_exc())
    sys.exit(0)
