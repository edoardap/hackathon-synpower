Li o SKILL.md, as referências (`design-doc.md`, `c4-mermaid.md`, `padroes.md`), o PRD e o mini-crm. Escrevi o design técnico em `outputs/design.md`. O destino pretendido é `docs/architecture/crm-oportunidades/design.md`, mas não criei nada em `docs/`. Status: Rascunho, aguardando sua confirmação.

**Resumo da decisão**
- O design fica dentro do monolito FastAPI existente, com camadas simples (router, serviço, modelo) e sem serviço novo.
- O isolamento entre organizações (RNF-01, RF-03) usa a coluna `org_id` por linha, que já existe em `Opportunity`. O filtro fica só no serviço, o `org_id` vem de uma dependência de contexto (nunca do corpo da requisição), e item de outra org responde 404.
- RF-01 e RF-02 usam `Opportunity.stage` e uma tabela append-only `OpportunityStageHistory`. A mudança de etapa grava os dois na mesma transação.
- O plano tem 4 passos em ordem: contexto do chamador, sessão e modelos, serviço, endpoints. Cada passo traz critérios binários de pronto.

**Achados no repositório**
- Não há autenticação, sessão de banco, migrações, schemas nem logging.
- `GET /opportunities` retorna `[]` fixo.
- Só existe o teste de `/health`.
- `docs/adr/` não existe, então não há ADR `Aceito` a seguir ou substituir. Recomendei um ADR para o isolamento por `org_id`, a ser escrito com a skill `adr-writer`.

**Perguntas em aberto**
1. Como o usuário se autentica e de onde vem a org? Isso bloqueia o passo 1.
2. Quais são as etapas do funil e há restrição de transição?
3. Há requisito de retenção do histórico ou de LGPD?
4. Qual banco e qual ferramenta de migração? Não verificado no repositório.
5. Qual o volume esperado por organização? Sem número, a listagem fica sem paginação.

As premissas (etapas, `amount` obrigatório, moeda única, POST pode duplicar) estão marcadas como não confirmadas no design. O PRD não tem histórias (HU-xx), então a rastreabilidade vai até o RF.

Arquivos:
- /home/eduarda/ideia/synpower/HACKATHON/evals/architecture-patterns/results/iteration-1/eval-positivo-design-tecnico/with_skill/run-1/outputs/design.md
- /home/eduarda/ideia/synpower/HACKATHON/evals/architecture-patterns/results/iteration-1/eval-positivo-design-tecnico/with_skill/run-1/outputs/resposta.md
