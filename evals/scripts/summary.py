#!/usr/bin/env python3
"""Resumo único dos evals do Grupo 1, lido de evals/*/results/.

Qualidade: o benchmark.json da última iteração de cada skill (gerado pelo aggregate_benchmark do skill-creator).
Ativação: o activation-*.json mais recente de cada skill.

  evals/scripts/summary.py            # imprime o resumo
  evals/scripts/summary.py --write    # troca o bloco entre os marcadores RESUMO no evals/README.md

Só lê JSON. Não roda eval nem chama o claude.
"""
import json, re, sys
from pathlib import Path

EVALS = Path(__file__).resolve().parent.parent
INI, FIM = "<!-- RESUMO:INICIO -->", "<!-- RESUMO:FIM -->"


def ultimo(skill_dir, padrao, chave):
    achados = sorted((skill_dir / "results").glob(padrao), key=chave)
    return achados[-1] if achados else None


def num_iteracao(p):
    return int(re.search(r"iteration-(\d+)", str(p)).group(1))


def qualidade(skill_dir):
    f = ultimo(skill_dir, "iteration-*/benchmark.json", num_iteracao)
    if not f:
        return None
    b = json.loads(f.read_text())
    rs = b["run_summary"]
    base = next((k for k in rs if k not in ("with_skill", "delta")), None)
    runs = b.get("runs", [])
    n = max([r.get("run_number", 1) for r in runs] or [1])

    def conta(cfg):
        rr = [r["result"] for r in runs if r["configuration"] == cfg]
        return sum(r["passed"] for r in rr), sum(r["total"] for r in rr)

    # asserção -> {config: [passou, total]}, só quando o benchmark traz as expectations por run
    por_asserc = {}
    for r in runs:
        for e in r.get("expectations", []):
            c = por_asserc.setdefault(e["text"], {}).setdefault(r["configuration"], [0, 0])
            c[0] += bool(e["passed"])
            c[1] += 1
    return {"it": num_iteracao(f), "n": n, "base": base, "com": conta("with_skill"),
            "sem": conta(base) if base else None, "delta": rs.get("delta", {}),
            "rs": rs, "asserc": por_asserc}


def ativacao(skill_dir):
    f = ultimo(skill_dir, "activation-*.json", lambda p: p.name)
    if not f:
        return None
    d = json.loads(f.read_text())
    valid = d.get("valid", sum(not r.get("invalido") for r in d["results"]))
    return {"arq": f.name, "passed": d["passed"], "valid": valid, "total": d["total"]}


def pct(a, b):
    return f"{a}/{b} ({round(100 * a / b)}%)" if b else "—"


def classifica(asserc, base):
    """Divide as asserções pelo que o 'Analisando padrões' da página manda olhar."""
    g = {"discrimina": [], "passa nos dois": [], "falha nos dois": []}
    for texto, c in asserc.items():
        com, sem = c.get("with_skill"), c.get(base)
        if not com or not sem:
            continue
        p_com, p_sem = com[0] / com[1] > 0.5, sem[0] / sem[1] > 0.5
        if p_com and not p_sem:
            g["discrimina"].append(texto)
        elif p_com and p_sem:
            g["passa nos dois"].append(texto)
        elif not p_com and not p_sem:
            g["falha nos dois"].append(texto)
    return g


def relatorio():
    skills = sorted(d for d in (EVALS / "manual").iterdir() if (d / "evals.json").exists())
    q = {s.name: qualidade(s) for s in skills}
    a = {s.name: ativacao(s) for s in skills}
    out = ["### Qualidade da saída (com a skill vs. sem a skill)", "",
           "| Skill | Iteração | Execuções por cenário | Com skill | Sem skill | Δ aprovação | Δ tempo (s) | Δ tokens |",
           "|---|---|---|---|---|---|---|---|"]
    for s, r in q.items():
        if not r:
            out.append(f"| `{s}` | — | — | sem iteração versionada | — | — | — | — |")
            continue
        d = r["delta"]
        out.append(f"| `{s}` | {r['it']} | {r['n']} | {pct(*r['com'])} | {pct(*r['sem']) if r['sem'] else '—'} "
                   f"| {d.get('pass_rate', '—')} | {d.get('time_seconds', '—')} | {d.get('tokens', '—')} |")
    com_desvio = [s for s, r in q.items() if r and r["n"] > 1]
    out += ["", "Com 1 execução por cenário o desvio padrão não significa nada, então só mostramos contagem e delta."]
    if com_desvio:
        out += ["Desvio padrão da taxa de aprovação (com skill): " + ", ".join(
            f"`{s}` ±{round(100 * q[s]['rs']['with_skill']['pass_rate']['stddev'])}%" for s in com_desvio) + "."]

    out += ["", "### Quais asserções discriminam", ""]
    algum = False
    for s, r in q.items():
        if not r or not r["asserc"]:
            continue
        algum = True
        g = classifica(r["asserc"], r["base"])
        out.append(f"- `{s}`: {len(g['discrimina'])} discriminam (passam com a skill e falham sem), "
                   f"{len(g['passa nos dois'])} passam nos dois (candidatas a sair), "
                   f"{len(g['falha nos dois'])} falham nos dois (asserção ou cenário quebrado)")
        for t in g["passa nos dois"] + g["falha nos dois"]:
            out.append(f"  - revisar: {t}")
    if not algum:
        out.append("Ainda sem dados: nenhuma iteração tem `benchmark.json` com as asserções por execução.")

    out += ["", "### Ativação (a skill é chamada quando deveria)", "",
            "| Skill | Acertos | Observação |", "|---|---|---|"]
    for s, r in a.items():
        if not r:
            out.append(f"| `{s}` | — | sem resultado |")
            continue
        obs = r["arq"] if r["valid"] == r["total"] else f"parcial: {r['valid']} de {r['total']} frases válidas ({r['arq']})"
        out.append(f"| `{s}` | {pct(r['passed'], r['valid'])} | {obs} |")
    return "\n".join(out)


if __name__ == "__main__":
    texto = relatorio()
    if "--write" not in sys.argv:
        print(texto)
        sys.exit()
    readme = EVALS / "README.md"
    conteudo = readme.read_text()
    if INI not in conteudo or FIM not in conteudo:
        sys.exit(f"Marcadores {INI} e {FIM} não encontrados em {readme}")
    antes, resto = conteudo.split(INI, 1)
    _, depois = resto.split(FIM, 1)
    readme.write_text(f"{antes}{INI}\n{texto}\n{FIM}{depois}")
    print(f"{readme} atualizado")
