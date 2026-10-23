# Alembic

Referência para projetos que migram o banco com Alembic, como o CRM de referência (`full-stack-fastapi-template`). Os
comandos rodam de `backend/`, com o banco de pé.

## Comandos

| Ação                                     | Comando                                                   |
| ---------------------------------------- | --------------------------------------------------------- |
| Gerar rascunho a partir dos modelos      | `uv run alembic revision --autogenerate -m "<descrição>"` |
| Criar migração vazia (dados, SQL manual) | `uv run alembic revision -m "<descrição>"`                |
| Aplicar até a última                     | `uv run alembic upgrade head`                             |
| Desfazer a última                        | `uv run alembic downgrade -1`                             |
| Versão atual do banco                    | `uv run alembic current`                                  |
| Histórico                                | `uv run alembic history`                                  |

No template, `docker compose up -d --wait db` sobe o PostgreSQL e o `scripts/prestart.sh` aplica `alembic upgrade head`
antes dos testes. O Alembic lê os modelos de `app/models.py` (configurado em `app/alembic/env.py`).

## Revisão do Rascunho Gerado

Depois do `--autogenerate`, abra o arquivo novo em `app/alembic/versions/` e confira:

1. **Renomeação.** Um `drop_column` e um `add_column` na mesma tabela costumam ser uma renomeação. Troque por
   `op.alter_column(..., new_column_name=...)`.
2. **Tipos do SQLModel.** Campos `str` viram `sqlmodel.sql.sqltypes.AutoString()`, e o arquivo precisa de
   `import sqlmodel.sql.sqltypes`, como as migrações vizinhas.
3. **Nomes de restrição.** Chave estrangeira e índice gerados com nome `None` dificultam o `downgrade`. Dê nome
   explícito (`fk_<tabela>_<referência>`, `ix_<tabela>_<coluna>`).
4. **`downgrade` completo.** Cada operação do `upgrade` tem o inverso no `downgrade`, em ordem inversa: o índice sai
   antes da coluna, a coluna antes da tabela, o tipo `ENUM` por último.
5. **`NOT NULL` sem padrão.** Coluna obrigatória em tabela que já tem linhas segue o caminho de três migrações de
   [operacoes.md](operacoes.md).
6. **Escopo.** O rascunho traz só a mudança pedida. Diferença inesperada entre modelo e banco vira pergunta ao usuário,
   e não uma linha a mais na migração.

## Migração de Dados

Use `op.execute` com SQL explícito, sem importar os modelos da aplicação: o modelo muda com o tempo e a migração antiga
precisa continuar rodando como foi escrita.

```python
def upgrade():
    op.execute("UPDATE opportunity SET stage = 'prospecting' WHERE stage IS NULL")
```

Em tabela grande, atualize em lotes por chave primária e faça *commit* por lote, fora de uma transação única.

## Índice Concorrente

```python
def upgrade():
    with op.get_context().autocommit_block():
        op.create_index("ix_opportunity_stage", "opportunity", ["stage"], postgresql_concurrently=True)

def downgrade():
    with op.get_context().autocommit_block():
        op.drop_index("ix_opportunity_stage", table_name="opportunity", postgresql_concurrently=True)
```
