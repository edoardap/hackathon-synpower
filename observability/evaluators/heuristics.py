"""Heurísticas locais do turno: falha de ferramenta, bloqueio do secret-guard, tokens e custo (D4, D9)."""

import tomllib
from functools import cache
from pathlib import Path

PRECOS = Path(__file__).parents[1] / "config" / "pricing.toml"
MARCA_GUARD = "politica de segredos"  # Q12: texto da negação do guard


@cache
def carregar_precos():
    with PRECOS.open("rb") as f:
        return tomllib.load(f)["modelos"]


def _descendentes(span):
    for filho in span.filhos:
        yield filho
        yield from _descendentes(filho)


def _bloqueio(span):
    # ponytail: um Read que cite a frase conta como bloqueio
    return MARCA_GUARD in (span.saida or "")


def _custo(chat, preco):
    """USD por milhão de tokens da chamada; o cache, dentro da entrada, tem preço próprio ou o de entrada."""
    a = chat.atributos
    lido = a.get("gen_ai.usage.cache_read.input_tokens", 0)
    criado = a.get("gen_ai.usage.cache_creation.input_tokens", 0)
    novos = a.get("gen_ai.usage.input_tokens", 0) - lido - criado
    entrada = novos * preco["input"] + lido * preco.get("cache_read", preco["input"])
    entrada += criado * preco.get("cache_write", preco["input"])
    return entrada + a.get("gen_ai.usage.output_tokens", 0) * preco["output"]


def calcular(turno, precos=None):
    """`(scores, tags)` do turno: `scores` vira `opik.metadata.score.<nome>` e `tags` entra em `opik.tags`."""
    precos = carregar_precos() if precos is None else precos
    spans = list(_descendentes(turno))
    chats = [s for s in spans if s.nome == "chat"]
    ferramentas = [s for s in spans if s.nome != "chat" and not s.filhos]  # subagente: só as folhas
    bloqueios = sum(map(_bloqueio, ferramentas))
    falhas = sum(s.erro or _bloqueio(s) for s in ferramentas)
    entrada = [s.atributos.get("gen_ai.usage.input_tokens", 0) for s in chats]
    saida = [s.atributos.get("gen_ai.usage.output_tokens", 0) for s in chats]
    scores = {
        "tool_failure_rate": falhas / len(ferramentas) if ferramentas else 0.0,
        "guard_blocks": bloqueios,
        "tokens_total": sum(entrada) + sum(saida),
    }
    modelos = [s.atributos.get("gen_ai.request.model") for s in chats]
    if modelos and all(m in precos for m in modelos):
        scores["cost_usd"] = round(sum(_custo(s, precos[m]) for s, m in zip(chats, modelos)) / 1e6, 6)
    return scores, [t for t, ativa in (("tool_failure", falhas), ("guard_block", bloqueios)) if ativa]
