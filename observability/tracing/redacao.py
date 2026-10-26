"""Redação de segredos antes do export (D5)."""

import json
import re
from dataclasses import replace

MARCADOR = "[REDIGIDO]"
MARCA_TRUNCADO = "\n[TRUNCADO]"
LIMITE_ARTEFATO = 20_000  # bytes, OBS_ARTIFACT_MAX
SUFIXOS = ("TOKEN", "KEY", "SECRET", "PASSWORD")
PADROES = re.compile(
    r"sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,}|glpat-[A-Za-z0-9_-]{20,}"
    r"|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|eyJ[\w-]{10,}\.[\w-]{10,}\.[\w-]{10,}"
    r"|Bearer [A-Za-z0-9._~+/=-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?(?:-----END [A-Z ]*PRIVATE KEY-----|$)"
)


def valores_secretos(env):
    """Valores de 8 ou mais caracteres cuja chave termina em TOKEN, KEY, SECRET ou PASSWORD."""
    return {v for k, v in env.items() if k.upper().endswith(SUFIXOS) and len(v) >= 8}


def redigir(texto, valores):
    formas = {f for v in valores for f in (v, json.dumps(v)[1:-1])}  # json.dumps escapa aspas e barra
    for v in sorted(formas, key=len, reverse=True):  # o mais longo primeiro
        texto = texto.replace(v, MARCADOR)
    return PADROES.sub(MARCADOR, texto)


def truncar(texto, limite):
    dados = texto.encode(errors="replace")
    return texto if len(dados) <= limite else dados[:limite].decode(errors="ignore") + MARCA_TRUNCADO


def sanear(span, valores, metadado, limite=LIMITE_ARTEFATO):
    """Cópia redigida da árvore, com código e texto do chat truncados depois; `nome` e `atributos` ficam intactos."""
    campos = {c: None if metadado or getattr(span, c) is None else redigir(getattr(span, c), valores)
              for c in ("entrada", "saida", "codigo")}
    # o que o chat recebeu já consta inteiro na raiz ou no span da ferramenta
    for c in ("codigo", *(("entrada", "saida") if span.nome == "chat" else ())):
        if campos[c] is not None:
            campos[c] = truncar(campos[c], limite)
    return replace(span, **campos, filhos=[sanear(f, valores, metadado, limite) for f in span.filhos])
