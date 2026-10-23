---
description: Ativação (deve acionar code-review-reliability). Mesma frase do trigger_evals.json do Grupo 2.
tags: [ativacao, positivo, skill]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

o executor terminou a fase 2, revisa os arquivos que ele mexeu: app/api/routes/products.py e app/models.py
