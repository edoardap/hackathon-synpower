#!/usr/bin/env python3
"""Compara, frase a frase, o nosso run_activation.py com o `claude plugin eval` (piloto em evals/plugin-eval).

Lê o aggregate-result.json mais recente do piloto e o activation-*.json mais recente de cada skill do arquiteto.
Só lê JSON: não roda nada nem chama o claude.

  evals/scripts/compare_tools.py                          # as 4 skills do arquiteto
  evals/scripts/compare_tools.py adr-writer               # uma skill
"""
import argparse, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PILOTO = REPO / "evals" / "plugin-eval"


def ultimo(pasta, padrao):
    achados = sorted(pasta.glob(padrao))
    return achados[-1] if achados else None


def frase(caso):
    """Corpo do prompt.md do caso, depois do frontmatter."""
    txt = (PILOTO / caso / "prompt.md").read_text()
    return re.split(r"^---\s*$", txt, flags=re.M)[2].strip()


SKILLS = ["adr-writer", "architecture-patterns", "api-design", "repo-orientation"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skills", nargs="*", default=SKILLS)
    a = ap.parse_args()

    of = ultimo(PILOTO / "results", "*/aggregate-result.json")
    if not of:
        sys.exit("Faltam resultados do oficial em evals/plugin-eval/results/.")
    res = json.loads(of.read_text())
    if res.get("partial"):
        print(f"ATENÇÃO: o resultado oficial é parcial ({res.get('partialReason')}); não use para concluir.\n")
    casos = {frase(c["name"]): c for c in res["cases"]}

    usados, total_ok, total = set(), 0, 0
    for skill in a.skills:
        nf = ultimo(REPO / "evals" / "manual" / skill / "results", "activation-*.json")
        if not nf:
            print(f"### {skill}: sem resultado do nosso (rode evals/scripts/run_activation.py {skill})\n")
            continue
        print(f"### {skill} ({nf.name})\n\n| Caso | Esperado | Nosso | Nosso ok | Oficial (nota) | Oficial ok | Concordam |\n|---|---|---|---|---|---|---|")
        ok_s = n_s = 0
        for r in json.loads(nf.read_text())["results"]:
            c = casos.get(r["query"])
            if not c:
                continue
            usados.add(r["query"])
            score = c["aggregates"]["score"]
            if r.get("invalido"):
                print(f"| {c['name']} | - | INVÁLIDO | - | {score:.2f} | - | - |")
                continue
            ok_n, ok_o = bool(r["pass"]), score >= 0.5
            n_s += 1
            ok_s += ok_n == ok_o
            print(f"| {c['name']} | {'ativar' if r['should_trigger'] else 'NÃO ativar'} | {r['triggers']}/{r['runs']} | "
                  f"{'ok' if ok_n else 'erro'} | {score:.2f} | {'ok' if ok_o else 'erro'} | {'sim' if ok_n == ok_o else 'NÃO'} |")
        print(f"\nConcordam em {ok_s} de {n_s} frases.\n")
        total_ok += ok_s
        total += n_s

    for q, c in casos.items():
        if q not in usados and c["name"].startswith("agente-"):
            print(f"Só no oficial (a nossa ferramenta não testa agente): {c['name']} nota {c['aggregates']['score']:.2f}")
    if total:
        print(f"\nTotal: concordam em {total_ok} de {total} frases comparáveis.")
    print(f"Oficial: {res.get('costUsd', '—')} USD estimados, {res.get('durationSeconds', '—')} s ({of.parent.name}). "
          f"Nosso: não registra custo nem tempo.")


if __name__ == "__main__":
    main()
