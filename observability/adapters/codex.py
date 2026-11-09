"""Leitor do rollout do Codex: cada turno vira uma árvore de spans (D1, D2)."""

import json
import re
from pathlib import Path

from observability.adapters.comum import ler_linhas, ler_turnos as _ler_turnos, ns, provedor, raiz
from observability.tracing.turno import Span

CHAMADAS = ("custom_tool_call", "function_call")
SAIDAS = ("custom_tool_call_output", "function_call_output")
PATCH = re.compile(r"\*\*\* (Add|Update|Delete) File:")


def _p(r):
    return r.get("payload") or {}


def _texto(blocos):
    if isinstance(blocos, str):
        return blocos
    return "\n".join(b.get("text", "") for b in blocos or [] if isinstance(b, dict))


def _abre_turno(r):
    return r.get("type") == "event_msg" and _p(r).get("type") == "task_started" and "timestamp" in r


def _subagente(ferramenta, saida, agentes, pasta, codigos):
    """Liga o `spawn_agent` ao rollout do subagente, achado ao lado do pai pelo id da thread."""
    try:
        thread = agentes.get(json.loads(saida).get("task_name"))
    except (ValueError, TypeError, AttributeError):
        return
    arquivo = next(pasta.glob(f"rollout-*-{thread}.jsonl"), None) if thread else None
    if arquivo is None:
        return
    registros = ler_linhas(arquivo)
    # ponytail: só o último turno do subagente; vários turnos (send_input) pedem um span por turno.
    inicios = [i for i, r in enumerate(registros) if _abre_turno(r)]
    if inicios:
        registros = registros[inicios[-1]:]
        ferramenta.filhos = _spans(registros, pasta, codigos, ns(registros[0]["timestamp"]))
        ferramenta.fim = max([ferramenta.fim, *(f.fim for f in ferramenta.filhos)])


def _spans(registros, pasta, codigos, inicio):
    """Spans de modelo (um por `token_usage_record`) e de ferramenta, na ordem do rollout."""
    agentes = {
        i["agent_path"]: i["agent_thread_id"]
        for r in registros
        if (i := _p(r).get("item")) and i.get("type") == "SubAgentActivity" and i.get("agent_thread_id")
    }
    filhos, ferramentas, modelo, saiu, anterior = [], {}, None, None, inicio
    for r in registros:
        p, ts = _p(r), ns(r["timestamp"]) if "timestamp" in r else anterior
        if r.get("type") == "turn_context":
            modelo = p.get("model") or modelo
        elif r.get("type") == "token_usage_record":
            uso = p.get("usage") or {}
            atributos = {"gen_ai.usage.input_tokens": uso.get("input_tokens", 0),
                         "gen_ai.usage.output_tokens": uso.get("output_tokens", 0), **provedor("openai")}
            if modelo:
                atributos["gen_ai.request.model"] = modelo
            filhos.append(Span("chat", anterior, ts, atributos))
        elif p.get("type") in CHAMADAS:
            entrada = p.get("input") if p["type"] == "custom_tool_call" else p.get("arguments")
            ferramentas[p.get("call_id")] = Span(p.get("name", ""), ts, ts, entrada=entrada)
            filhos.append(ferramentas[p.get("call_id")])
            if p.get("name") == "exec" and PATCH.search(entrada or ""):
                codigos.append(entrada)
        elif p.get("type") == "item_completed" and (p.get("item") or {}).get("type") == "CommandExecution":
            saiu = p["item"].get("exit_code")  # chega antes da saída do `exec`, sem o call_id
        elif p.get("type") in SAIDAS and (s := ferramentas.get(p.get("call_id"))):
            s.fim, s.saida, s.erro, saiu = ts, _texto(p.get("output")), bool(saiu), None
            if s.nome == "spawn_agent":
                _subagente(s, s.saida, agentes, pasta, codigos)
        anterior = ts
    return filhos


def _prompt(registros):
    """A última mensagem `user` antes da primeira saída do modelo; as anteriores são contexto injetado."""
    prompt = None
    for r in registros:
        p = _p(r)
        if r.get("type") == "token_usage_record" or p.get("type") in CHAMADAS or p.get("role") == "assistant":
            break
        if p.get("type") == "message" and p.get("role") == "user":
            prompt = _texto(p.get("content"))
    return prompt


def _final(registros):
    for r in reversed(registros):
        p = _p(r)
        if p.get("type") == "task_complete" and p.get("last_agent_message"):
            return p["last_agent_message"]
        if p.get("type") == "message" and p.get("role") == "assistant":
            return _texto(p.get("content"))
    return None


def _turno(registros, pasta):
    codigos, inicio = [], ns(registros[0]["timestamp"])
    filhos = _spans(registros, pasta, codigos, inicio)
    fim = ns(next(r["timestamp"] for r in reversed(registros) if "timestamp" in r))
    return raiz(inicio, fim, _prompt(registros), _final(registros), filhos, codigos)


def ler_turnos(transcript, offset=0):
    """Turnos que começam a partir da linha `offset` do rollout e o offset seguinte (linhas já lidas)."""
    pasta = Path(transcript).parent
    return _ler_turnos(transcript, offset, _abre_turno, lambda registros: _turno(registros, pasta))
