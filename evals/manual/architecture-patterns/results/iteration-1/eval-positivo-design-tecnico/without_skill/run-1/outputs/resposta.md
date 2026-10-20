Escrevi o design técnico em `outputs/design.md`, sem criar nada em `docs/` e sem usar skills.

Resumo:
- **Estado do repo:** o mini-crm só tem `Opportunity` (sem etapa) e um `GET /opportunities` que devolve `[]`. Não há banco configurado, autenticação nem histórico.
- **Arquitetura:** monolito FastAPI em camadas (router, serviço, modelo), com multi-tenancy por coluna `org_id` em banco compartilhado. O `org_id` vem sempre do usuário autenticado e todo acesso passa por um serviço que filtra por ele (RNF-01, RF-03). Outra organização recebe 404, não 403.
- **Dados:** novo campo `stage` em `opportunities` e tabela `opportunity_stage_history` (de, para, quem, quando). A mudança de etapa e o histórico são gravados na mesma transação (RF-02).
- **API:** `POST /opportunities`, `GET /opportunities`, `PATCH /opportunities/{id}/stage`, `GET /opportunities/{id}/history`.
- **Rastreabilidade e testes:** tabela RF/RNF para componente e teste de aceite, com foco em isolamento entre organizações.
- **Em aberto (não inventei):** forma de autenticação, lista de etapas do funil, SGBD, obrigatoriedade e moeda do valor, volume e permissões por papel. Premissas marcadas no documento.
- **ADRs sugeridos:** multi-tenancy por `org_id` e histórico em tabela própria. Não os escrevi.

Arquivo: /home/eduarda/ideia/synpower/HACKATHON/evals/architecture-patterns/results/iteration-1/eval-positivo-design-tecnico/without_skill/run-1/outputs/design.md
