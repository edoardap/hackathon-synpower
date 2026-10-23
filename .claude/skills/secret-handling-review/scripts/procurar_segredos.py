#!/usr/bin/env python3
"""Procura segredos em arquivos versionados e, opcionalmente, no histórico do Git.

Uso:
    procurar_segredos.py [CAMINHO] [--historico] [--max-commits N]

Em repositório Git, lê só os arquivos rastreados (git ls-files); fora dele, percorre a pasta. Arquivos .env* nunca
têm o conteúdo lido: um .env rastreado vira achado de configuração. Todo valor sai mascarado.

Saída: JSON em stdout. Código de saída 1 quando há achado real CRITICAL ou WARNING; 0 caso contrário.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PADROES = [
    ("chave_privada", "CRITICAL", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"), None),
    ("aws_access_key", "CRITICAL", re.compile(r"\b((?:AKIA|ASIA)[0-9A-Z]{16})\b"), 1),
    ("github_token", "CRITICAL", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})\b"), 1),
    ("gitlab_token", "CRITICAL", re.compile(r"\b(glpat-[A-Za-z0-9_-]{20,})"), 1),
    ("slack_token", "CRITICAL", re.compile(r"\b(xox[baprs]-[A-Za-z0-9-]{10,})"), 1),
    ("google_api_key", "CRITICAL", re.compile(r"\b(AIza[0-9A-Za-z_-]{35})\b"), 1),
    ("stripe_key", "CRITICAL", re.compile(r"\b((?:sk|rk)_live_[0-9A-Za-z]{20,})\b"), 1),
    ("chave_api_llm", "CRITICAL", re.compile(r"\b(sk-(?:ant-|proj-)?[A-Za-z0-9_-]{32,})\b"), 1),
    ("jwt", "WARNING", re.compile(r"\b(eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})\b"), 1),
    ("url_com_senha", "CRITICAL", re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s:/@'\"]+:([^\s@'\"/]+)@"), 1),
    (
        "atribuicao_de_segredo",
        "CRITICAL",
        re.compile(
            r"(?i)\b[a-z0-9_]*(?:password|passwd|senha|secret|token|api_?key|access_?key|private_?key)[a-z0-9_]*"
            r"\s*[:=]\s*['\"]([^'\"\s]{6,})['\"]"
        ),
        1,
    ),
]

MARCAS_DE_EXEMPLO = (
    "changethis", "changeme", "change_me", "example", "exemplo", "placeholder", "your_", "your-", "seu_", "sua_",
    "xxxx", "****", "dummy", "fake", "redacted", "<", "${", "{{", "%(", "aqui",
)

PASTAS_IGNORADAS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next", "coverage"}
ARQUIVOS_IGNORADOS = {"package-lock.json", "bun.lock", "bun.lockb", "uv.lock", "yarn.lock", "poetry.lock", "pnpm-lock.yaml"}
ENV_DE_EXEMPLO = {".env.example", ".env.sample", ".env.template", ".env.dist"}
TAMANHO_MAXIMO = 1_000_000


def eh_env(caminho: str) -> bool:
    nome = os.path.basename(caminho)
    return (nome == ".env" or nome.startswith(".env.")) and nome not in ENV_DE_EXEMPLO


def mascarar(valor: str) -> str:
    return f"{valor[:4]}…({len(valor)} caracteres)"


def classificar(valor: str) -> str:
    baixo = valor.lower()
    return "exemplo" if any(marca in baixo for marca in MARCAS_DE_EXEMPLO) else "real"


def procurar_na_linha(linha: str) -> list[dict]:
    achados, vistos = [], set()
    for tipo, gravidade, padrao, grupo in PADROES:
        for m in padrao.finditer(linha):
            valor = m.group(grupo) if grupo else m.group(0)
            # Os padrões específicos vêm antes do genérico; o mesmo valor não sai duas vezes.
            if any(valor in visto or visto in valor for visto in vistos):
                continue
            vistos.add(valor)
            classe = classificar(valor) if grupo else "real"
            achados.append(
                {
                    "tipo": tipo,
                    "classe": classe,
                    "gravidade": gravidade if classe == "real" else "SUGGESTION",
                    "valor": mascarar(valor),
                }
            )
    return achados


def git(raiz: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True)


def listar_arquivos(raiz: Path, alvo: Path, em_git: bool) -> list[str]:
    if em_git:
        # Rastreados e novos ainda não commitados; o que o .gitignore exclui (como o .env local) fica de fora.
        saida = git(raiz, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", str(alvo)).stdout
        return sorted({linha for linha in saida.split("\0") if linha})
    arquivos = []
    for pasta, subpastas, nomes in os.walk(alvo):
        subpastas[:] = [s for s in subpastas if s not in PASTAS_IGNORADAS]
        for nome in nomes:
            arquivos.append(os.path.relpath(os.path.join(pasta, nome), raiz))
    return arquivos


def ler_texto(caminho: Path) -> str | None:
    try:
        if caminho.stat().st_size > TAMANHO_MAXIMO:
            return None
        dados = caminho.read_bytes()
    except OSError:
        return None
    if b"\0" in dados[:8192]:
        return None
    return dados.decode("utf-8", errors="replace")


def varrer_arquivos(raiz: Path, arquivos: list[str]) -> tuple[list[dict], list[dict], int]:
    achados, configuracao, verificados = [], [], 0
    for relativo in arquivos:
        if eh_env(relativo):
            configuracao.append(
                {
                    "tipo": "env_versionado",
                    "arquivo": relativo,
                    "gravidade": "WARNING",
                    "nota": "conteúdo não lido; se os valores forem reais, a gravidade é CRITICAL e eles devem ser rotacionados",
                }
            )
            continue
        partes = Path(relativo).parts
        if any(p in PASTAS_IGNORADAS for p in partes) or os.path.basename(relativo) in ARQUIVOS_IGNORADOS:
            continue
        texto = ler_texto(raiz / relativo)
        if texto is None:
            continue
        verificados += 1
        for numero, linha in enumerate(texto.splitlines(), start=1):
            for achado in procurar_na_linha(linha):
                achados.append({"arquivo": relativo, "linha": numero, **achado})
    return achados, configuracao, verificados


def varrer_historico(raiz: Path, alvo: Path, max_commits: int) -> list[dict]:
    saida = git(
        raiz, "log", "-p", "--no-color", f"--max-count={max_commits}", "--format=commit %H", "--", str(alvo)
    ).stdout
    achados, commit, arquivo = [], "", ""
    for linha in saida.splitlines():
        if linha.startswith("commit "):
            commit = linha.split()[1][:12]
        elif linha.startswith("+++ "):
            arquivo = linha[6:] if linha.startswith("+++ b/") else ""
        elif linha.startswith("+") and arquivo and not eh_env(arquivo):
            for achado in procurar_na_linha(linha[1:]):
                achados.append({"commit": commit, "arquivo": arquivo, **achado})
    return achados


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("caminho", nargs="?", default=".")
    parser.add_argument("--historico", action="store_true", help="varre também as linhas adicionadas nos commits")
    parser.add_argument("--max-commits", type=int, default=500)
    args = parser.parse_args()

    alvo = Path(args.caminho).resolve()
    if not alvo.is_dir():
        print(f"pasta não encontrada: {alvo}", file=sys.stderr)
        return 2
    em_git = git(alvo, "rev-parse", "--is-inside-work-tree").stdout.strip() == "true"
    raiz = Path(git(alvo, "rev-parse", "--show-toplevel").stdout.strip()) if em_git else alvo

    achados, configuracao, verificados = varrer_arquivos(raiz, listar_arquivos(raiz, alvo, em_git))
    if em_git and git(raiz, "check-ignore", "-q", str(alvo / ".env")).returncode != 0:
        configuracao.append(
            {"tipo": "env_fora_do_gitignore", "arquivo": ".gitignore", "gravidade": "WARNING", "nota": ".env não é ignorado"}
        )
    historico = varrer_historico(raiz, alvo, args.max_commits) if em_git and args.historico else []

    resultado = {
        "raiz": str(raiz),
        "alvo": str(alvo),
        "git": em_git,
        "arquivos_verificados": verificados,
        "achados": achados,
        "configuracao": configuracao,
        "historico": historico,
    }
    print(json.dumps(resultado, ensure_ascii=False, indent=2))

    graves = [a for a in achados + historico if a["classe"] == "real" and a["gravidade"] in ("CRITICAL", "WARNING")]
    graves += [c for c in configuracao if c["gravidade"] in ("CRITICAL", "WARNING")]
    return 1 if graves else 0


if __name__ == "__main__":
    sys.exit(main())
