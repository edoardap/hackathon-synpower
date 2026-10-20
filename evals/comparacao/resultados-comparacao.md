# Resultados da comparação: `run_activation.py` (nosso) x `claude plugin eval` (oficial)

Saída do `evals/scripts/compare_tools.py`, rodada em 20/10/2026 sobre o arquiteto e as 4 skills dele.
Método, casos e critérios: veja `evals/comparacao/comparacao-ferramentas.md`.

### adr-writer (activation-2026-10-20-1005.json)

| Caso | Esperado | Nosso | Nosso ok | Oficial (nota) | Oficial ok | Concordam |
|---|---|---|---|---|---|---|
| adr-writer-pos-vamos-com-postgres-em | ativar | 2/2 | ok | 1.00 | ok | sim |
| adr-writer-pos-registra-um-adr-decidimos | ativar | 2/2 | ok | 1.00 | ok | sim |
| adr-writer-pos-por-que-escolhemos-rls | ativar | 2/2 | ok | 1.00 | ok | sim |
| adr-writer-neg-renomeia-a-variavel-opp | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |
| adr-writer-neg-qual-a-diferenca-entre | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |
| adr-writer-neg-escreve-o-readme-do | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |

Concordam em 6 de 6 frases.

### architecture-patterns (activation-2026-10-20-1004.json)

| Caso | Esperado | Nosso | Nosso ok | Oficial (nota) | Oficial ok | Concordam |
|---|---|---|---|---|---|---|
| architecture-patterns-pos-monolito-microsservicos | ativar | 0/2 | erro | 0.00 | erro | sim |
| architecture-patterns-pos-isolar-dados-tenant | ativar | 1/2 | ok | 0.00 | erro | NÃO |
| architecture-patterns-pos-prd-aprovado | ativar | 0/2 | erro | 1.00 | ok | NÃO |
| architecture-patterns-neg-bug-endpoint | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |
| architecture-patterns-neg-endpoints-rest | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |
| architecture-patterns-neg-implementa-crud | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |
| agente-neg-escreve-prd | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |

Concordam em 5 de 7 frases.

### api-design (activation-2026-10-20-1006.json)

| Caso | Esperado | Nosso | Nosso ok | Oficial (nota) | Oficial ok | Concordam |
|---|---|---|---|---|---|---|
| api-design-pos-desenha-a-api-rest | ativar | 2/2 | ok | 1.00 | ok | sim |
| api-design-pos-que-status-code-devo | ativar | 0/2 | erro | 0.00 | erro | sim |
| api-design-pos-quero-renomear-o-campo | ativar | 2/2 | ok | 1.00 | ok | sim |
| api-design-neg-monolito-ou-microsservicos-para | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |
| api-design-neg-implementa-o-endpoint-post | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |
| api-design-neg-escreve-a-query-sql | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |

Concordam em 6 de 6 frases.

### repo-orientation (activation-2026-10-20-1007.json)

| Caso | Esperado | Nosso | Nosso ok | Oficial (nota) | Oficial ok | Concordam |
|---|---|---|---|---|---|---|
| repo-orientation-pos-acabei-de-clonar-esse | ativar | 0/2 | erro | 1.00 | ok | NÃO |
| repo-orientation-pos-quais-comandos-de-build | ativar | 0/2 | erro | 0.00 | erro | sim |
| repo-orientation-pos-me-orienta-nesse-repositorio | ativar | 2/2 | ok | 1.00 | ok | sim |
| repo-orientation-neg-adiciona-o-campo-etapa | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |
| repo-orientation-neg-explica-o-que-essa | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |
| repo-orientation-neg-decide-qual-arquitetura-usar | NÃO ativar | 0/2 | ok | 1.00 | ok | sim |

Concordam em 5 de 6 frases.

Só no oficial (a nossa ferramenta não testa agente): agente-pos-qual-arquitetura nota 0.00

Total: concordam em 22 de 25 frases comparáveis.
Oficial: 2.9620675000000007 USD estimados, 741 s (2026-10-20T12-49-04-875Z). Nosso: não registra custo nem tempo.
