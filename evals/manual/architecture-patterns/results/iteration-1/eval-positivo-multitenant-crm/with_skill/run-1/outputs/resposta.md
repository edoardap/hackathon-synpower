## Decisão: estrutura do backend e isolamento entre organizações (CRM multi-tenant)

### Contexto
Pequeno CRM multi-tenant para cadastro e acompanhamento de oportunidades comerciais, com regras de acesso por organização. Stack: FastAPI, React, PostgreSQL. Time de 3 devs, 5 dias. Não há PRD nem ADRs em `docs/adr/` (a pasta não existe), então nenhuma decisão aceita restringe esta escolha.

Requisitos que mais pesam:
- **Confirmados:** isolamento entre organizações; prazo de 5 dias; 3 devs; stack fixada (Python/FastAPI, PostgreSQL).
- **Presumidos (confirmar):** todas as organizações cabem no mesmo produto e na mesma versão; não há exigência contratual ou regulatória de banco dedicado por cliente; um usuário pertence a uma organização; não há integrações externas nem carga que exija escala independente.

### Forças e restrições
- Prazo curto e time pequeno: cada peça operacional extra (serviço, banco, pipeline de migração por tenant) consome dias que não existem.
- O vazamento entre organizações é o risco de maior impacto (e dá problema de LGPD se houver dados pessoais de contatos). Ele precisa ser difícil de causar por descuido, não só "lembrado" em cada query.
- Dados e fronteira de tenant são caros de mudar depois: a coluna de tenant e o modelo de identidade têm de estar certos desde o dia 1.
- Dimensões a cobrir (design-doc): auth (quem é o usuário e de qual organização, vindo do token e nunca do corpo da requisição); concorrência (duas pessoas editando a mesma oportunidade); ciclo de vida (exclusão e retenção de dados por organização, LGPD); observabilidade (log com `org_id`); integridade de transição de estado (etapas do funil). Falha parcial e idempotência pesam pouco: não há integração externa nem fila.

### Opções
**Estilo de implantação**
| Opção | Ganha | Paga | Reversível? |
|---|---|---|---|
| Monolito modular (um deployable FastAPI) | Entrega em 5 dias, uma transação, um deploy, debug simples | Exige disciplina nas fronteiras entre módulos | Sim: módulo bem delimitado pode virar serviço depois |
| Microsserviços | Escala e deploy independentes | Rede, consistência eventual, observabilidade, operação; inviável em 5 dias com 3 devs | Difícil |

**Isolamento de tenant**
| Opção | Ganha | Paga | Reversível? |
|---|---|---|---|
| A. Banco por organização | Isolamento máximo; exclusão e backup por cliente triviais | Provisionamento, migrações em N bancos, pool de conexões, custo operacional | Difícil |
| B. Esquema por organização | Isolamento forte, sem tantas instâncias | Migrações em N esquemas, `search_path` por requisição, complexidade com pool | Difícil |
| C. Linha com `org_id` + filtro obrigatório na aplicação | Mais simples, uma migração, rápido | Um esquecimento de filtro vaza dados; proteção depende só de disciplina | Média (migrar depois para B/A é trabalhoso) |
| D. Linha com `org_id` + Row-Level Security (RLS) do PostgreSQL, além do filtro na aplicação | Mesma simplicidade de C, mas o banco recusa linha de outra organização mesmo se a query esquecer o filtro | Pequena complexidade: definir a variável de sessão por transação, usuário de banco sem `BYPASSRLS`, testes específicos | Boa: continua sendo "por linha" e permite evoluir |

### Recomendação
**Monolito modular + isolamento por linha com `org_id` reforçado por RLS no PostgreSQL (opção D).** Justificativa ligada aos requisitos:

- **Prazo e time:** monolito modular com um banco e um conjunto de migrações cabe em 5 dias; A e B e microsserviços não cabem sem sacrificar a funcionalidade.
- **Risco de vazamento:** C sozinho deixa o isolamento depender de 3 devs lembrando o filtro em toda query, sob pressa. RLS transforma o esquecimento em resultado vazio em vez de vazamento: é a defesa em profundidade mais barata disponível.
- **Reversibilidade:** a coluna `org_id` em toda tabela de negócio serve a D, a B e a A (migração para esquema ou banco dedicado depois, se um cliente exigir).

Estrutura do backend (camadas simples dentro de módulos, sem hexagonal, CQRS nem fila, porque nenhum requisito pede):
- Módulos: `identidade` (usuários, organizações, papéis), `oportunidades` (cadastro, etapas, histórico) e `compartilhado` (sessão de banco, dependências de auth). Cada módulo com `router`, `service` e `repository`; um módulo não importa o repositório de outro, só o serviço.
- **Contexto de tenant:** uma dependência do FastAPI lê o token, obtém `org_id` e papel do usuário **do token/banco, nunca do corpo ou da URL**, e abre a sessão de banco já com o tenant definido (ex.: `SET LOCAL app.org_id = ...` dentro da transação). Todo repositório recebe essa sessão; nenhum endpoint recebe `org_id` do cliente.
- **Banco:** `org_id NOT NULL` com FK em toda tabela de negócio; índices começando por `org_id`; política RLS por tabela comparando `org_id` com a variável de sessão; a aplicação conecta com um papel sem `BYPASSRLS` e sem ser dono das tabelas (o dono roda as migrações). Chaves estrangeiras compostas (`org_id`, `id`) onde uma oportunidade referencia contato ou usuário, para impedir referência cruzada entre organizações.
- **Regras de acesso dentro da organização:** papéis simples (a definir com o produto) checados no `service`, separados do isolamento entre organizações, que é responsabilidade do banco e do contexto.
- **Concorrência:** controle otimista (coluna de versão ou `updated_at`) na edição de oportunidades. **Observabilidade:** `org_id` em todo log. **Etapas do funil:** lista fixa validada no serviço, transições inválidas rejeitadas.
- **Testes obrigatórios (os que mais valem nos 5 dias):** para cada endpoint, usuário da organização A não lê, altera nem apaga recurso da B (espera 404); uma query sem filtro de aplicação, sob RLS, devolve só linhas da própria organização.

**Gatilho de revisão:** migrar para esquema ou banco por organização se aparecer cliente com exigência contratual ou regulatória de isolamento físico, necessidade de exclusão e backup por cliente, ou organização com volume que degrade as demais. Extrair serviço só se uma parte exigir escala ou time independente. Se RLS se mostrar inviável com o pool de conexões escolhido, a fallback é C com filtro centralizado no repositório base e testes de isolamento, aceitando o risco explicitamente.

### Perguntas em aberto
- Há exigência contratual, regulatória ou de cliente (LGPD, setor regulado) de isolamento físico por organização? (produto/jurídico)
- Um usuário pode pertencer a mais de uma organização? Isso muda o token e o contexto de tenant. (produto)
- Quais papéis e permissões existem dentro da organização? (produto)
- Quem faz a autenticação (login próprio ou provedor externo)? (time)
- Como o pool de conexões e o ambiente de hospedagem tratam variável de sessão por transação (por exemplo, pgbouncer em modo transação exige `SET LOCAL`)? (time/infra)
- Retenção e exclusão de dados de uma organização encerrada. (produto)

### Diagrama
Posso desenhar os diagramas de Contexto e Container (C4 em Mermaid) desta opção, e detalhar em `docs/architecture/<nome>/design.md`. Esta decisão é difícil de reverter e vale registrar com a skill `adr-writer` (ADR: "Isolamento multi-tenant por linha com RLS"). Quer que eu faça isso?
