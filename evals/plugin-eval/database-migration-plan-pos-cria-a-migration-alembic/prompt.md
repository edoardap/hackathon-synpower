---
description: Ativação (deve acionar database-migration-plan). Mesma frase do trigger_evals.json do Grupo 2.
tags: [ativacao, positivo, skill]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

cria a migration alembic da tabela product, com sku único por organização
