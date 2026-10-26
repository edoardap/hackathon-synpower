# Eval do Grupo 1 com DeepEval

Cobre produto, discovery, UX e arquitetura: skills `product-discovery`, `prd-writing`, `technical-planning`, `product-design`,
`architecture-patterns`, `api-design`, `adr-writer`, `repo-orientation` e os agentes `product-manager`, `designer` e `solutions-architect`.
Cada skill tem 3 casos (positivo, negativo e limite), em `cases_grupo1.py`.

Para cada caso, o `claude -p` roda com o plugin (`--plugin-dir`) num diretório vazio e sem escrita. O DeepEval aplica duas métricas:
**Ativação** (determinística: a skill/agente esperado foi acionado, ou os proibidos não foram) e **Qualidade** (GEval com os critérios do caso,
julgado pelo próprio `claude -p`, sem API key).

```bash
pip install -r evals/deepeval/requirements.txt
python evals/deepeval/run_eval.py              # tudo
python evals/deepeval/run_eval.py -k prd       # só casos cujo id contém "prd"
python evals/deepeval/run_eval.py --reuse      # reaproveita as respostas e só julga
```

Resultados em `results/grupo1.json` (métricas e motivos) e `results/outputs.json` (respostas e skills acionadas).
