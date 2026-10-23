---
description: Ativação (deve acionar backend-patterns). Mesma frase do trigger_evals.json do Grupo 2.
tags: [ativacao, positivo, skill]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

preciso de um endpoint POST /api/v1/products no nosso backend fastapi pra cadastrar produto com nome, preço e sku único; cada empresa tem o próprio catálogo
