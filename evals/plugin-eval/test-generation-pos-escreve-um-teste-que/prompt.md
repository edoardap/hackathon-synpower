---
description: Ativação (deve acionar test-generation). Mesma frase do trigger_evals.json do Grupo 2.
tags: [ativacao, positivo, skill]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

escreve um teste que prova que o GET /tickets/{id} devolve ticket de outra empresa; não corrige o código
