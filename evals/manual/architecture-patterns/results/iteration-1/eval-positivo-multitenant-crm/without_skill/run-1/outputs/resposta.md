# Recomendação: backend e isolamento multi-tenant do CRM

## Recomendação

**Monólito modular em FastAPI, um único PostgreSQL, esquema compartilhado com coluna `org_id` em toda tabela de negócio, e Row-Level Security (RLS) do Postgres como segunda trava.** O app filtra por organização e o banco impede o vazamento mesmo se o app esquecer.

## Estrutura do backend

Um deploy só, pastas por módulo, camadas simples dentro de cada um:

```
app/
  core/        # config, db (sessão), auth, dependência de tenant
  orgs/        # organizações, usuários, papéis
  opportunities/  # router.py, service.py, repo.py, schemas.py, models.py
  main.py
```

- `router` só valida e delega; `service` tem as regras (etapas do funil, permissões); `repo` fala com o banco (SQLAlchemy 2 + Alembic).
- Módulos conversam por funções do `service`, nunca importando `models` de outro módulo. Isso deixa extrair um serviço depois, sem pagar o custo agora.
- Sem filas, sem CQRS, sem hexagonal completo. Com 3 devs e 5 dias não há requisito que os peça.

## Isolamento entre organizações (três camadas)

1. **Identidade.** O JWT leva `user_id` e `org_id`. Uma dependência do FastAPI (`get_tenant_session`) lê o `org_id` do token (nunca do corpo ou da URL) e abre a sessão.
2. **Banco (a trava real).** Na abertura da transação: `SET LOCAL app.org_id = '<uuid>'` (use `set_config('app.org_id', :id, true)`, parametrizado). Em cada tabela de negócio:
   ```sql
   ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;
   ALTER TABLE opportunities FORCE ROW LEVEL SECURITY;
   CREATE POLICY tenant_isolation ON opportunities
     USING (org_id = current_setting('app.org_id')::uuid)
     WITH CHECK (org_id = current_setting('app.org_id')::uuid);
   ```
   Pontos que não podem falhar:
   - A aplicação conecta com um papel que **não é dono das tabelas e não tem BYPASSRLS**. As migrations rodam com outro papel.
   - Sem `app.org_id` definido, `current_setting` sem o segundo argumento dá erro: falha fechada (nenhuma linha vaza).
   - `SET LOCAL` vale só na transação, então é seguro com pool de conexões (não use `SET` de sessão).
3. **Integridade.** `org_id NOT NULL` em tudo; FKs compostas (`(org_id, cliente_id)` referenciando `(org_id, id)`) impedem uma oportunidade da org A apontar para um cliente da org B.

Regras de acesso dentro da organização (ex.: vendedor vê só as suas, gestor vê todas) ficam no `service`, com papel no token. RLS cuida da fronteira entre orgs; papéis cuidam do que vem depois. Misturar os dois nas policies complica sem ganho aqui.

## Por que não as alternativas

| Opção | Por que não agora |
|---|---|
| Só filtro `WHERE org_id` no código | Um esquecimento em uma query vaza dados. Aceitável apenas com a trava de RLS por baixo. |
| Schema por tenant | Migrations rodam N vezes, pool e ferramentas ficam mais complicados. Vale com poucos tenants grandes e exigência contratual, o que não consta. |
| Banco por tenant | Custo e operação altos para um CRM pequeno. |
| Microsserviços | 3 devs, 5 dias: o custo de rede, deploy e consistência consome o prazo sem benefício. |

## Riscos e como tratar

- **Esquecer RLS numa tabela nova.** Teste automático que lista tabelas com `org_id` e falha se alguma não tiver RLS habilitado e forçado.
- **Desempenho.** Índice começando por `org_id` em toda tabela (`(org_id, status)`, `(org_id, criado_em)`).
- **Jobs/scripts fora de requisição.** Devem definir `app.org_id` explicitamente; nunca usar o papel de migração.
- **Teste de isolamento obrigatório:** criar duas orgs, e checar que A não lê, edita nem apaga dados de B, inclusive por ID direto (deve dar 404) e por tentativa de `INSERT` com `org_id` alheio (deve falhar pelo `WITH CHECK`).

## Plano para 5 dias (3 devs)

- Dia 1: esqueleto, auth/JWT, `orgs`, migrations, papel do banco, RLS e o teste de isolamento (um dev; os outros começam frontend).
- Dias 2-3: CRUD de oportunidades, etapas do funil, histórico de acompanhamento.
- Dia 4: regras de acesso por papel, filtros e listagem paginada.
- Dia 5: testes de ponta a ponta, ajustes, deploy.

## Premissas e pontos em aberto

- Um usuário pertence a uma única organização (se puder pertencer a várias, o token precisa de seleção de org ativa).
- Papéis assumidos: admin, gestor, vendedor. A definir com o negócio.
- Volume pequeno, sem exigência de isolamento físico por contrato. Se aparecer, migrar o tenant para schema ou banco dedicado é possível, pois o código já isola por `org_id`.
- Recomenda-se registrar a decisão em um ADR.
