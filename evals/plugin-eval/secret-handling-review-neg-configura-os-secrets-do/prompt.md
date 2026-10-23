---
description: Ativação (não deve acionar secret-handling-review). Mesma frase do trigger_evals.json do Grupo 2.
tags: [ativacao, negativo, skill]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

configura os secrets do github actions pra passar a DATABASE_URL pro job de testes
