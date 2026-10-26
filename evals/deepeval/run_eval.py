"""Roda o eval do Grupo 1 com o DeepEval.

Uso (na raiz do repo):
    python evals/deepeval/run_eval.py                 # tudo
    python evals/deepeval/run_eval.py -k prd-writing  # só casos cujo id contém o texto
    python evals/deepeval/run_eval.py --reuse         # reaproveita as respostas já geradas e só julga
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from deepeval import evaluate
from deepeval.evaluate.configs import AsyncConfig, DisplayConfig, ErrorConfig
from deepeval.metrics import BaseMetric, GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from cases_grupo1 import CASES
from claude_cli import ClaudeJudge, run_plugin

RESULTS = Path(__file__).parent / "results"


class ActivationMetric(BaseMetric):
    """Determinístico: a skill/agente esperado foi acionado (positivo/limite) ou os proibidos não foram (negativo)."""

    def __init__(self, expect, forbid):
        self.expect, self.forbid = expect, forbid
        self.threshold = 1.0
        self.async_mode = False
        self.evaluation_model = "deterministico"
        self.strict_mode = False
        self.include_reason = True
        self.verbose_mode = False

    @property
    def __name__(self):
        return "Ativação"

    def measure(self, test_case, *args, **kwargs):
        got = set(json.loads(test_case.additional_metadata["activated"]))
        if self.forbid:
            hit = got & set(self.forbid)
            self.score = 0.0 if hit else 1.0
            self.reason = f"acionou proibidos: {sorted(hit)}" if hit else f"nenhum proibido acionado (acionados: {sorted(got)})"
        else:
            hit = got & set(self.expect)
            self.score = 1.0 if hit else 0.0
            self.reason = f"acionou {sorted(hit)}" if hit else f"esperava um de {self.expect}, acionou {sorted(got)}"
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case, *args, **kwargs):
        return self.measure(test_case)

    def is_successful(self):
        return self.success


def generate(cases, reuse):
    cache = RESULTS / "outputs.json"
    stored = json.loads(cache.read_text()) if cache.exists() else {}
    todo = [c for c in cases if not (reuse and c.id in stored)]
    print(f"Gerando {len(todo)} respostas com o plugin (as demais vêm do cache)...")
    with ThreadPoolExecutor(max_workers=4) as pool:
        for case, res in zip(todo, pool.map(lambda c: run_plugin(c.prompt), todo)):
            stored[case.id] = res
            print(f"  {case.id}: acionou {res['activated']}")
    RESULTS.mkdir(exist_ok=True)
    cache.write_text(json.dumps(stored, ensure_ascii=False, indent=2))
    return stored


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", default="")
    ap.add_argument("--reuse", action="store_true")
    ap.add_argument("--judge-model", default="sonnet")
    args = ap.parse_args()

    cases = [c for c in CASES if args.k in c.id]
    outputs = generate(cases, args.reuse)
    judge = ClaudeJudge(args.judge_model)

    test_cases, metrics_by_case = [], []
    for c in cases:
        res = outputs[c.id]
        tc = LLMTestCase(
            name=c.id, input=c.prompt, actual_output=res["output"] or "(sem resposta)",
            additional_metadata={"activated": json.dumps(res["activated"]), "kind": c.kind, "capability": c.capability},
        )
        quality = GEval(name="Qualidade", evaluation_steps=c.criteria, model=judge, threshold=0.7,
                        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT], async_mode=False)
        test_cases.append(tc)
        metrics_by_case.append([ActivationMetric(c.expect, c.forbid), quality])

    # DeepEval aplica a mesma lista de métricas a todos os casos; rodamos um caso por vez para usar a de cada um.
    summary = []
    for c, tc, metrics in zip(cases, test_cases, metrics_by_case):
        r = evaluate([tc], metrics, async_config=AsyncConfig(run_async=False),
                     display_config=DisplayConfig(show_indicator=False, print_results=False),
                     error_config=ErrorConfig(ignore_errors=True))
        tr = r.test_results[0]
        summary.append({
            "id": c.id, "capability": c.capability, "kind": c.kind, "success": tr.success,
            "metrics": [{"name": m.name, "score": m.score, "success": m.success, "reason": m.reason}
                        for m in (tr.metrics_data or [])],
        })
        print(f"{'PASS' if tr.success else 'FAIL'}  {c.id}")

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "grupo1.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    passed = sum(s["success"] for s in summary)
    print(f"\n{passed}/{len(summary)} casos passaram. Detalhes em {RESULTS / 'grupo1.json'}")


if __name__ == "__main__":
    main()
