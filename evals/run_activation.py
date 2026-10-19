#!/usr/bin/env python3
"""Teste de ativação com a skill real: roda `claude -p <frase>` na raiz do repo e vê se
Skill:<skill> aparece entre as primeiras ferramentas que o Claude chama (--within, padrão 3).

Uso (no seu terminal, onde `claude -p "oi"` funciona):
  evals/run_activation.py                                  # as 4 skills do arquiteto, 2 repetições
  evals/run_activation.py api-design --runs 3 --within 1   # uma skill, critério estrito
  evals/run_activation.py --selftest                       # confere o detector, sem chamar o claude

Resultado: evals/<skill>/results/activation-<data-hora>.json (nunca sobrescreve).
Escrita e shell ficam bloqueados no claude -p; ele é morto assim que o critério é decidido.
Erros de execução (ex.: limite de uso) ficam como INVÁLIDO e não entram na nota; o teste para.
"""
import argparse, json, os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT = ["adr-writer", "architecture-patterns", "api-design", "repo-orientation"]


def decide(events, skill, within=1):
    """Lê eventos stream-json; devolve (acionou, ferramentas_vistas, terminou).
    Aciona se Skill:<skill> estiver entre as `within` primeiras ferramentas chamadas."""
    tools = []
    for e in events:
        if e.get("type") == "assistant":
            for c in e["message"].get("content", []):
                if c.get("type") == "tool_use":
                    name, inp = c["name"], c.get("input", {})
                    target = inp.get("skill") or inp.get("subagent_type") or ""
                    tools.append(f"{name}:{target}" if target else name)
                    if name == "Skill" and target.split(":")[-1] == skill:
                        return True, tools, True
                    if len(tools) >= within:
                        return False, tools, True
        elif e.get("type") == "result":
            return False, tools, True
    return False, tools, False


LIMITE = threading.Event()  # conta sem cota: para de gastar chamadas


def run_one(query, skill, timeout, within):
    """Devolve (acionou, ferramentas). acionou=None significa erro (resultado inválido)."""
    if LIMITE.is_set():
        return None, ["ERRO:abortado por limite de uso"]
    cmd = ["claude", "-p", query, "--output-format", "stream-json", "--verbose",
           "--disallowedTools", "Write,Edit,Bash,NotebookEdit"]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    p = subprocess.Popen(cmd, cwd=REPO, env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    events, start = [], time.time()
    try:
        for line in p.stdout:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            events.append(e)
            if e.get("type") == "result" and e.get("is_error"):
                msg = str(e.get("result"))
                if "limit" in msg.lower():
                    LIMITE.set()
                return None, ["ERRO:" + msg[:60]]
            hit, tools, done = decide(events, skill, within)
            if done or time.time() - start > timeout:
                return hit, tools
    finally:
        p.kill(); p.wait()
    return None, ["ERRO:sem resposta"]


def selftest():
    sk = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "adr-writer"}}]}}]
    ag = [{"type": "assistant", "message": {"content": [{"type": "text", "text": "oi"}]}},
          {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Agent", "input": {"subagent_type": "solutions-architect"}}]}}]
    late = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Glob", "input": {}}]}},
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "adr-writer"}}]}}]
    assert decide(sk, "adr-writer") == (True, ["Skill:adr-writer"], True)
    assert decide(sk, "api-design") == (False, ["Skill:adr-writer"], True)
    assert decide(ag, "adr-writer") == (False, ["Agent:solutions-architect"], True)
    assert decide([{"type": "result"}], "adr-writer") == (False, [], True)
    assert decide(late, "adr-writer", within=1) == (False, ["Glob"], True)   # exploração antes da skill
    assert decide(late, "adr-writer", within=3) == (True, ["Glob", "Skill:adr-writer"], True)
    assert decide([], "adr-writer") == (False, [], False)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skills", nargs="*")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("--within", type=int, default=3, help="aciona se Skill estiver entre as N primeiras ferramentas")
    ap.add_argument("--set", dest="set_")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    for s in a.skills or DEFAULT:
        items = json.loads(Path(a.set_ or REPO / "evals" / s / "triggers.json").read_text())
        with ThreadPoolExecutor(a.workers) as ex:
            futs = {(i, r): ex.submit(run_one, it["query"], s, a.timeout, a.within)
                    for i, it in enumerate(items) for r in range(a.runs)}
            res = {k: f.result() for k, f in futs.items()}
        out, ok, invalid = [], 0, 0
        for i, it in enumerate(items):
            runs = [res[(i, r)] for r in range(a.runs)]
            tools = [f for _, f in runs]
            if any(h is None for h, _ in runs):  # erro de execução: não conta como resultado
                invalid += 1
                out.append({**it, "invalido": True, "ferramentas": tools})
                print(f'  [INVÁLIDO] {it["query"][:70]}  {tools}')
                continue
            n = sum(h for h, _ in runs)
            passed = (n / a.runs >= 0.5) == it["should_trigger"]
            ok += passed
            out.append({**it, "triggers": n, "runs": a.runs, "pass": passed, "ferramentas": tools})
            print(f'  [{"PASS" if passed else "FAIL"}] {n}/{a.runs} esperado={it["should_trigger"]}: {it["query"][:70]}  {tools}')
        valid = len(items) - invalid
        if invalid:
            print(f"  ATENÇÃO: {invalid} frase(s) com erro de execução (ex.: limite de uso); não entram na nota. Não use este resultado como conclusivo.")
            if LIMITE.is_set():
                print("  Limite de uso atingido: parando. Tente de novo depois do reset.")
        d = REPO / "evals" / s / "results"; d.mkdir(parents=True, exist_ok=True)
        (d / f"activation-{stamp}.json").write_text(json.dumps({"skill": s, "passed": ok, "valid": valid, "total": len(items), "within": a.within, "results": out}, ensure_ascii=False, indent=2))
        print(f"{s}: {ok}/{valid} passed (válidas) de {len(items)}")
        if LIMITE.is_set():
            break


if __name__ == "__main__":
    main()
