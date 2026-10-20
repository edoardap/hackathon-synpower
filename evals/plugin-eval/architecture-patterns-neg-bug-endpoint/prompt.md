---
description: Ativação (não deve acionar architecture-patterns). Mesma frase do triggers.json quando existir.
tags: [ativacao, negativo, skill]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

esse endpoint retorna 500 quando amount é null, corrige: def create(op): total = op.amount * op.quantity
