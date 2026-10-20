# Comparação: `run_activation.py` (nosso) x `claude plugin eval` (oficial)

Objetivo: decidir se o teste de ativação oficial substitui o nosso, comparando as duas ferramentas nas mesmas frases.
Status: **montado, ainda não rodado.** Nenhum resultado aqui foi medido.

## O que foi montado

- O repo virou plugin: `.claude-plugin/plugin.json` e os links `skills -> .claude/skills` e `agents -> .claude/agents`.
  `claude plugin validate .` passa, com aviso de que o validador não segue os links (o carregamento segue).
- 26 casos em `evals/plugin-eval/` (`--eval-dir evals/plugin-eval`, porque `evals/` já tem o nosso formato):
  - 24 de skill, 6 para cada skill do arquiteto (`adr-writer`, `architecture-patterns`, `api-design`, `repo-orientation`),
    com as mesmas frases dos `triggers.json` (3 positivas e 3 negativas por skill);
  - 2 de agente: "qual arquitetura devo usar" deve chamar o `solutions-architect`; "escreve o PRD" não deve.
- Cada caso tem 2 execuções, como o nosso `--runs 2`, e libera as mesmas ferramentas (`Skill` e `Agent`), para os dois verem a mesma ambiguidade entre chamar a skill direto ou delegar ao agente.

## Como rodar (no seu terminal, onde `claude -p "oi"` funciona)

Dentro da sessão de quem montou, o `claude -p` não estava autenticado ("Not logged in"), então nada foi rodado.

```bash
# 1. Oficial: 26 casos x 2 execuções = 52 execuções, sem baseline (mais barato)
claude plugin eval . --runs 2 --ablation none --trust-plugin --no-publish

# 2. Nosso: as 12 frases de cada skill (as 6 do piloto estão entre elas). Uma skill por vez, até 24 chamadas cada
evals/scripts/run_activation.py architecture-patterns
evals/scripts/run_activation.py adr-writer
evals/scripts/run_activation.py api-design
evals/scripts/run_activation.py repo-orientation

# 3. Comparar frase a frase
evals/scripts/compare_tools.py
```

Rode um de cada vez e espere o reset se bater o limite de uso. O oficial marca a execução como falha (nota 0) quando
o limite estoura, e o nosso marca `INVÁLIDO`. Se o resultado oficial vier `partial`, o `compare_tools.py` avisa.

## Critérios da comparação

| Critério | Nosso | Oficial | Resultado |
|---|---|---|---|
| Concordância por frase (24 de skill) | | | a preencher |
| Quando conta como ativação | `Skill:` entre as 3 primeiras ferramentas | em qualquer ponto da execução | a explicar as divergências |
| Cobre agente | não | sim (`tool: Agent`) | a conferir se funciona |
| Custo e tempo | não registra | `costUsd` e `durationSeconds` | a preencher |
| Erro de limite de uso | `INVÁLIDO`, não conta | nota 0, comando sai com erro | a conferir |
| Esforço de configuração | pronto | manifesto, links, casos | feito, falta ver se o link simbólico carrega |
| Saída | `activation-*.json` | `aggregate-result.json` e `report.html` | |

## Perguntas que a comparação precisa responder

1. As duas dão o mesmo veredito nas 6 frases? Onde divergem, é por causa do critério (3 primeiras x qualquer momento)?
2. O link simbólico `skills -> .claude/skills` realmente carrega as skills e os agentes na execução oficial?
3. Quando o Claude delega ao `solutions-architect`, o grader do oficial enxerga a skill chamada dentro do subagente?
4. O caso de agente funciona sem baseline (`--ablation none`)? Com baseline, o agente não existe e dá erro esperado.
5. O custo do oficial compensa o que ele cobre a mais?

Decisão: a preencher depois dos resultados.
