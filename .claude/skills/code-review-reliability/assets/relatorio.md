# Revisão: [PR, branch ou tarefa]

Relatório no formato da `code-review-reliability`. Substitua cada texto entre colchetes. Sem findings, a seção Findings
traz a linha `Nenhum.`

- **Veredito:** APROVADO | REPROVADO
- **Revisor:** [agente e foco: qa-engineer (qualidade), security-reviewer (segurança), code-reviewer (todos)]
- **Alcance:** [o que foi revisado, ex.: git diff main...feature/oportunidades, 14 arquivos]

## Comandos

| Comando                                                             | Resultado        |
| ------------------------------------------------------------------- | ---------------- |
| [comando de teste ou lint, ex.: uv run bash scripts/tests-start.sh] | [ex.: 61 passed] |

## Findings

### F1. [título curto]

- **Gravidade:** CRITICAL | WARNING | SUGGESTION
- **Escopo:** IN_SCOPE | OUT_OF_SCOPE
- **Evidência:** `[caminho/arquivo.py:42]`
- **Trecho atual:**

```python
[5 a 15 linhas em torno da evidência]
```

- **Execução:** [entrada concreta] → [o que a linha faz com ela] → [valor ou erro que sai]
- **Reprodução:** `[comando que falha hoje e passa depois da correção]`
- **Correção proposta:**

```diff
[diff da mudança]
```

## Fora de Escopo

- [finding OUT_OF_SCOPE, uma linha cada, para virar tarefa]
