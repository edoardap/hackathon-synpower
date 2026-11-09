"""Leitor do transcript do Claude Code: cada turno vira uma árvore de spans (D1, D2)."""

import json
import re
from pathlib import Path

from observability.adapters.comum import ler_linhas, ler_turnos as _ler_turnos, ns, provedor, raiz
from observability.tracing.turno import Span

CODIGO = {
    "Write": lambda i: i.get("content"),
    "Edit": lambda i: i.get("new_string"),
    "MultiEdit": lambda i: "\n".join(e.get("new_string", "") for e in i.get("edits") or []),
}
# Campos do despacho do ciclo (SKILL.md, Despacho). Os atributos não passam pela redação: só entra o que casa o padrão.
DESPACHO = {
    "Fase": ("fase", r"(PROPOSE|APPLY|plano|fase|final|detalhamento|correção|ARCHIVE)\b"),
    "Change": ("change", r"([\w.-]+)"),
    "Grupo de tarefas": ("grupo", r"(\d+(?:\.\d+)*)"),
    "Foco": ("foco", r"(qa|seguranca|arquitetura)\b"),
}


def _texto(conteudo):
    if isinstance(conteudo, str):
        return conteudo
    return "\n".join(b.get("text", "") for b in conteudo or [] if isinstance(b, dict) and b.get("type") == "text")


def _abre_turno(r):
    """Prompt do usuário. O resultado de ferramenta e o `isMeta` (skill, aviso) também chegam como `user`."""
    return (
        r.get("type") == "user" and "timestamp" in r and not r.get("isSidechain") and not r.get("isMeta")
        and bool(_texto((r.get("message") or {}).get("content")).strip())
    )


def _anexar(atual, texto):
    return f"{atual}\n{texto}" if atual else texto


def _uso(msg):
    """O total de entrada inclui o cache; as duas partes dele seguem à parte para o custo descontá-las."""
    u = msg.get("usage") or {}
    lido, criado = u.get("cache_read_input_tokens", 0), u.get("cache_creation_input_tokens", 0)
    atributos = {"gen_ai.usage.input_tokens": u.get("input_tokens", 0) + lido + criado,
                 "gen_ai.usage.cache_read.input_tokens": lido, "gen_ai.usage.cache_creation.input_tokens": criado,
                 "gen_ai.usage.output_tokens": u.get("output_tokens", 0), **provedor("anthropic")}
    if msg.get("model"):
        atributos["gen_ai.request.model"] = msg["model"]
    return atributos


def _agente(nome, entrada):
    """Nome e atributos do span de uma chamada: o `Agent` leva o tipo do subagente e os campos do despacho."""
    tipo = entrada.get("subagent_type")
    if nome != "Agent" or not isinstance(tipo, str) or not re.fullmatch(r"[\w.:-]{1,60}", tipo):
        return nome, {}
    prompt = entrada.get("prompt") if isinstance(entrada.get("prompt"), str) else ""
    atributos = {"opik.metadata.agent_type": tipo}
    for campo, (chave, valor) in DESPACHO.items():
        if achado := re.search(rf"^{campo}:[ \t]*{valor}", prompt, re.M):
            atributos[f"opik.metadata.{chave}"] = achado.group(1)
    return f"agent:{tipo}", atributos


def _marcar(spans, tipo):
    """O tipo do agente que fez cada chamada, para o Opik somar custo e filtrar regra por agente."""
    for s in spans:
        s.atributos.setdefault("opik.metadata.agent_type", tipo)  # o agente aninhado já veio com o dele
        _marcar(s.filhos, tipo)


def _subagente(ferramenta, agente_id, pasta, codigos):
    arquivo = pasta / f"agent-{agente_id}.jsonl"
    registros = ler_linhas(arquivo) if arquivo.is_file() else []
    if registros and "timestamp" in registros[0]:
        ferramenta.filhos = _spans(registros, pasta, codigos, ns(registros[0]["timestamp"]))
        if tipo := ferramenta.atributos.get("opik.metadata.agent_type"):
            _marcar(ferramenta.filhos, tipo)
        # ponytail: subagente assíncrono depois do export não é lido
        ferramenta.fim = max([ferramenta.fim, *(f.fim for f in ferramenta.filhos)])


def _spans(registros, pasta, codigos, inicio):
    """Spans de modelo e de ferramenta, na ordem do transcript; `inicio` abre o primeiro span de modelo."""
    filhos, chats, ferramentas, anterior = [], {}, {}, inicio
    novas = []  # o que o modelo recebeu desde a chamada anterior: pedido e resultados de ferramenta
    for r in registros:
        ts = ns(r["timestamp"]) if "timestamp" in r else anterior
        msg = r.get("message") or {}
        conteudo = msg.get("content")
        if r.get("type") == "assistant":
            chat = chats.get(msg.get("id"))
            if chat is None:  # o transcript repete a mensagem (e o usage) a cada bloco de conteúdo
                chat = chats[msg.get("id")] = Span("chat", anterior, ts, _uso(msg), entrada="\n\n".join(novas) or None)
                novas.clear()
                filhos.append(chat)
            chat.fim = ts
            for b in conteudo or []:
                if b.get("type") == "text" and b.get("text"):
                    chat.saida = _anexar(chat.saida, b["text"])
                if b.get("type") != "tool_use":
                    continue
                chat.saida = _anexar(chat.saida, f"→ {b['name']}")
                entrada = b.get("input") or {}
                nome, atributos = _agente(b["name"], entrada)
                ferramentas[b["id"]] = Span(nome, ts, ts, atributos, entrada=json.dumps(entrada, ensure_ascii=False))
                filhos.append(ferramentas[b["id"]])
                trecho = CODIGO[b["name"]](entrada) if b["name"] in CODIGO else None
                if trecho is not None and not entrada.get("file_path", "").endswith(".md"):
                    codigos.append(f"# {entrada.get('file_path', '')}\n{trecho}")
        elif r.get("type") == "user":
            for b in [{"type": "text", "text": conteudo}] if isinstance(conteudo, str) else conteudo or []:
                texto = ""
                if b.get("type") == "tool_result":
                    texto = _texto(b.get("content"))
                    s = ferramentas.get(b.get("tool_use_id"))
                    if s is not None:
                        s.fim, s.saida, s.erro = ts, texto, bool(b.get("is_error"))
                        resultado = r.get("toolUseResult")
                        if isinstance(resultado, dict) and resultado.get("agentId"):
                            _subagente(s, resultado["agentId"], pasta, codigos)
                elif b.get("type") == "text" and not r.get("isMeta"):
                    texto = b.get("text", "")
                if texto.strip():
                    novas.append(texto)
        anterior = ts
    return filhos


def _final(registros):
    """O último texto do assistente no turno."""
    for r in reversed(registros):
        if r.get("type") == "assistant":
            for b in reversed((r.get("message") or {}).get("content") or []):
                if b.get("type") == "text" and b.get("text"):
                    return b["text"]
    return None


def _turno(registros, pasta):
    codigos, inicio = [], ns(registros[0]["timestamp"])
    filhos = _spans(registros, pasta, codigos, inicio)
    fim = ns(next(r["timestamp"] for r in reversed(registros) if "timestamp" in r))
    return raiz(inicio, fim, _texto(registros[0]["message"]["content"]), _final(registros), filhos, codigos)


def _continuacao(sobra):
    """O Stop do Discord prolonga o turno depois de o hook lê-lo: o que vem sem prompt abre um turno sintético."""
    primeiro = next((r for r in sobra if r.get("type") == "assistant" and "timestamp" in r), None)
    if primeiro:
        texto = "(continuação do turno anterior)"
        return {"type": "user", "timestamp": primeiro["timestamp"], "message": {"content": texto}}


def ler_turnos(transcript, offset=0):
    """Turnos que começam a partir da linha `offset` do transcript e o offset seguinte (linhas já lidas)."""
    pasta = Path(transcript).with_suffix("") / "subagents"
    return _ler_turnos(transcript, offset, _abre_turno, lambda registros: _turno(registros, pasta), _continuacao)
