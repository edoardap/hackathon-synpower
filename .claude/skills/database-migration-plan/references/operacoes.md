# Operações de Schema

Mapa de risco de cada operação de schema. **Compatível** quer dizer que o código já em produção continua funcionando
logo depois da migração. **Quebra** quer dizer que o código antigo falha, por isso a operação segue o caminho seguro em
vários *deploys*.

## Mapa

| Operação                                                | Risco                              | Caminho seguro                                                           |
| ------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------ |
| Criar tabela                                            | Compatível                         | Uma migração                                                             |
| Adicionar coluna opcional (`NULL`)                      | Compatível                         | Uma migração                                                             |
| Adicionar coluna obrigatória com valor padrão constante | Compatível                         | Uma migração com `server_default`                                        |
| Adicionar coluna obrigatória sem valor padrão           | Quebra                             | Opcional → preencher → `NOT NULL`                                        |
| Criar índice                                            | Compatível                         | Migração própria; `CONCURRENTLY` em tabela grande                        |
| Adicionar chave estrangeira                             | Compatível se os dados já obedecem | Conferir órfãos antes; em tabela grande, `NOT VALID` e depois `VALIDATE` |
| Adicionar `UNIQUE` ou `CHECK`                           | Quebra se houver dado que viola    | Consultar violações antes; corrigir dados; criar a restrição             |
| Renomear coluna ou tabela                               | Quebra                             | Expandir e contrair                                                      |
| Mudar tipo de coluna                                    | Quebra                             | Expandir e contrair                                                      |
| Remover coluna ou tabela                                | Quebra                             | Remover o uso no código, *deploy*, depois remover do schema              |
| Tornar coluna obrigatória                               | Quebra se houver `NULL`            | Preencher os `NULL` → `NOT NULL`                                         |

## Expandir e Contrair

Sequência para renomear, mudar tipo ou dividir uma coluna. Cada passo é uma migração e um *deploy* separados, e o passo
de contrair espera a janela de rollback do passo anterior passar.

1. **Expandir.** Migração cria a coluna nova, opcional. O código antigo ignora a coluna.
2. **Escrever nas duas.** *Deploy* do código que grava na coluna antiga e na nova, e continua lendo da antiga.
3. **Migrar os dados.** Migração de dados copia os valores antigos para a coluna nova, em lotes com *commit* por lote em
   tabela grande.
4. **Ler da nova.** *Deploy* do código que lê da coluna nova. A antiga ainda recebe escrita, para o rollback deste passo
   continuar possível.
5. **Contrair.** Migração remove a coluna antiga, com o código já sem nenhuma referência a ela.

Em projeto sem produção, como uma demo ou um protótipo, os passos 2 a 4 podem cair num *deploy* só. Diga isso no plano.

## Coluna Obrigatória em Tabela com Dados

Três migrações. Exemplo em Alembic para a coluna `organization_id` em `user`:

```python
# 1. Expandir: coluna opcional com chave estrangeira
def upgrade():
    op.add_column("user", sa.Column("organization_id", sa.Uuid(), nullable=True))
    op.create_foreign_key("fk_user_organization", "user", "organization", ["organization_id"], ["id"])
    op.create_index("ix_user_organization_id", "user", ["organization_id"])

def downgrade():
    op.drop_index("ix_user_organization_id", table_name="user")
    op.drop_constraint("fk_user_organization", "user", type_="foreignkey")
    op.drop_column("user", "organization_id")
```

```python
# 2. Preencher: dado existente recebe um valor
def upgrade():
    op.execute(
        "UPDATE \"user\" SET organization_id = (SELECT id FROM organization WHERE name = 'Default') "
        "WHERE organization_id IS NULL"
    )

def downgrade():
    pass  # o passo 1 já desfaz a coluna inteira
```

```python
# 3. Restringir: a coluna vira obrigatória
def upgrade():
    op.alter_column("user", "organization_id", nullable=False)

def downgrade():
    op.alter_column("user", "organization_id", nullable=True)
```

O `downgrade` vazio do passo 2 é aceitável porque o dado preenchido some junto com a coluna no `downgrade` do passo 1.
Registre esse motivo no próprio arquivo.

## Consultas de Conferência

Rode antes da migração que cria a restrição e anote o resultado no plano.

```sql
-- Valores nulos que impedem NOT NULL
SELECT count(*) FROM "user" WHERE organization_id IS NULL;

-- Duplicatas que impedem UNIQUE
SELECT email, count(*) FROM "user" GROUP BY email HAVING count(*) > 1;

-- Órfãos que impedem a chave estrangeira
SELECT count(*) FROM opportunity o LEFT JOIN organization g ON g.id = o.organization_id WHERE g.id IS NULL;
```
