# Evals das skills

Os testes usam só o `claude plugin eval` do Claude Code. Os casos ficam em `plugin-eval/`, no formato que a ferramenta exige,
e ela grava os resultados em `plugin-eval/results/`.

Os casos cobrem a **ativação**: o Claude escolhe a skill ou o agente quando deveria e não escolhe quando não deveria
(casos `pos` e `neg`). O `.claude-plugin/plugin.json` aponta para eles em `experimental.evals`.

Para rodar, na raiz do repo:

```bash
claude plugin eval
```
