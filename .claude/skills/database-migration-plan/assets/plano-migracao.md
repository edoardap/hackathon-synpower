# Plano de Migração: [nome da mudança]

Plano que o agente mostra ao usuário antes de escrever a migração. Substitua cada texto entre colchetes e apague as
linhas de exemplo.

- **Repositório:** [caminho]
- **Ferramenta:** Alembic | golang-migrate | [outra]
- **Motivo:** [requisito, história ou design que pede a mudança]
- **Tabelas tocadas:** [tabela] ([número aproximado de linhas]), uma por item
- **Ambiente com dados reais:** sim | não (demo ou protótipo)

## Classificação

| Operação                                                  | Risco  | Caminho                           |
| --------------------------------------------------------- | ------ | --------------------------------- |
| \<ex.: adicionar `organization_id` obrigatório em `user`> | Quebra | Opcional → preencher → `NOT NULL` |

## Passos

| #   | Migração    | O que faz                                           | Código implantado junto | Rollback                                  |
| --- | ----------- | --------------------------------------------------- | ----------------------- | ----------------------------------------- |
| 1   | `[arquivo]` | [ex.: cria a coluna opcional e a chave estrangeira] | nenhum                  | `downgrade` remove índice, chave e coluna |

## Conferências Antes de Aplicar

| Consulta                                                            | Resultado esperado | Resultado   |
| ------------------------------------------------------------------- | ------------------ | ----------- |
| \<ex.: `SELECT count(*) FROM "user" WHERE organization_id IS NULL`> | 0 antes do passo 3 | [preencher] |

## Prova do Rollback

```text
[saída do scripts/verificar-rollback.sh]
```

## Pendências

- [decisão que depende do usuário, ou "nenhuma"]
