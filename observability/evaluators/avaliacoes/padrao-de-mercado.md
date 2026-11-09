# Como o Mercado Mede Implementação de Código por Agente

Este documento registra como benchmarks e produtos nomeiam e coletam as métricas de implementação de código por agentes,
e o conjunto mínimo que sai disso para este repositório. As fontes são páginas públicas consultadas em 2026-10-23; o que
veio só de resumo de terceiros está marcado.

## O Que o Mercado Faz

| Prática                 | Nome e forma de medir                                                                                                                                                                          | Fonte                                                                                                                                                   |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Testes como oráculo     | "resolved": o patch aplica e passam todos os testes FAIL_TO_PASS (corrigem) e PASS_TO_PASS (não regridem); sem crédito parcial                                                                 | [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/)                                                                          |
| Três tipos de avaliador | *code-based* (testes, análise estática, checagem de chamadas), *model-based* (rubrica, asserções em linguagem natural) e humano; "determinístico onde der, LLM onde for preciso"               | [Anthropic](https://anthropic.com/engineering/demystifying-evals-for-ai-agents)                                                                         |
| Agente de código        | testes unitários para a corretude e rubrica de LLM para a qualidade; o exemplo usa ruff, mypy e bandit                                                                                         | Anthropic                                                                                                                                               |
| Como escrever o juiz    | uma dimensão por juiz, saída "Unknown" quando falta informação, calibração com especialistas humanos                                                                                           | Anthropic                                                                                                                                               |
| Confiabilidade          | `pass@k` (ao menos um acerto em k tentativas) e `pass^k` (todos os k acertam); capacidade começa baixa, regressão fica perto de 100%                                                           | Anthropic                                                                                                                                               |
| Juízes prontos          | Opik: Agent Task Completion Judge, Agent Tool Correctness Judge, G-Eval, Hallucination, Usefulness. Langfuse: correctness, helpfulness, relevance, conciseness, hallucination, toxicity        | [Opik](https://www.comet.com/docs/opik/evaluation/metrics/overview), [Langfuse](https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge) |
| Portão de código novo   | Sonar: sem issues novos, *hotspots* revistos, cobertura do código novo de 80% ou mais, duplicação de 3% ou menos                                                                               | [Sonar](https://docs.sonarsource.com/sonarqube-server/10.8/instance-administration/analysis-functions/quality-gates/)                                   |
| Segurança               | analisadores com CWE (Semgrep, CodeQL, Bandit), em contagem, taxa por amostra e densidade por linha; num estudo só 65% das saídas do Semgrep e 61% das do CodeQL conferiam com o rótulo humano | estudos no arXiv, via resumo                                                                                                                            |
| Qualidade dos testes    | "falha antes, passa depois" e *mutation score* (mutantes mortos sobre mutantes cobertos); a relação com falha real é contestada                                                                | artigos, via resumo                                                                                                                                     |
| LLM como juiz de código | critérios em funcionalidade e qualidade; juízes erram a corretude com frequência, então a execução serve de verdade de referência                                                              | [arXiv 2503.02246](https://arxiv.org/abs/2503.02246)                                                                                                    |

## As Seis Regras no Vocabulário do Mercado

| Regra           | Nome no mercado                                                  | Nome do score      | Avaliador que o mercado prefere            |
| --------------- | ---------------------------------------------------------------- | ------------------ | ------------------------------------------ |
| Cumpre o pedido | *task completion*, *correctness*, *resolved*                     | `task_completion`  | testes; juiz como complemento              |
| Fica no escopo  | sem nome padrão achado; PASS_TO_PASS cobre regressão, não escopo | `scope_adherence`  | juiz                                       |
| Segue as regras | *instruction following*, aderência a política                    | `rules_adherence`  | juiz; lint para o que for mecânico         |
| Solução mínima  | *maintainability*, *conciseness*; sem nome padrão para "mínima"  | `minimal_solution` | juiz e Sonar                               |
| Segurança       | *security*, *vulnerabilities*, CWE                               | `security`         | analisador estático; juiz como complemento |
| Testes provam   | FAIL_TO_PASS, cobertura de código novo, *mutation score*         | `test_adequacy`    | execução dos testes; juiz como aproximação |

## O Mínimo Para Começar

- **Seis juízes no Opik:** um critério por juiz, escopo trace, filtro pela tag `code_written`. Três leem o trace inteiro
  (`{{trace}}`) e três leem campos. Os prompts estão em `observability/evaluators/<nome>.md`, e o passo a passo, em
  `observability/evaluators/configurar_regras_no_opik.md`.
- **O que o mercado faz e ainda não fazemos:** testes e análise estática como nota por código, sem LLM. O hook já vê os
  spans de `Bash`, então `tests_passed` e `lint_issues` são o próximo passo, fora destas seis.
- **Calibração:** leia à mão 20 traces com a nota do juiz e conte os acertos antes de decidir algo pela nota.

## Limites da Pesquisa

- Não achei nome padrão para escopo (*scope creep*) nem para "solução mínima"; os nomes `scope_adherence` e
  `minimal_solution` são escolha nossa.
- A segurança e a qualidade dos testes vieram de resumos de estudos; leia os artigos antes de citar números.
- A página do Opik não lista os modelos que aceitam as ferramentas do modo *Agent as a Judge*; teste com o modelo
  escolhido.
