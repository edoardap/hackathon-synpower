# Hackathon AI Software Engineering: plugin de agentes e skills

Este repositório é um plugin com agentes e skills que cobrem o ciclo de engenharia de software.
Os agentes ficam em `.claude/agents/` e as skills em `.claude/skills/`. Converse em português do Brasil.

## Qual agente usar

| Pedido do usuário | Agente | Entrada | Saída |
|---|---|---|---|
| Ideia vaga, "vale a pena construir?", PRD, histórias, critérios de aceite | `product-manager` | Ideia, notas ou PRD | Descoberta, PRD, planejamento |
| Telas, fluxos, wireframe, design visual, roteiro de conversa | `designer` | PRD e histórias | Especificação de design |
| Arquitetura, API, design técnico, ADR, "como estruturar" | `solutions-architect` | PRD e histórias, repositório | Decisão, design técnico, ADR |

Se o pedido tocar em mais de um, siga a ordem: `product-manager`, depois `designer` e `solutions-architect`.
Se o usuário pedir para escrever código, testar ou fazer deploy, diga que isso é de outro agente (grupos 2 e 3).

## Onde salvar (cada arquivo só depois de o usuário aceitar)

| Entregável | Caminho |
|---|---|
| Descoberta | `docs/discovery/<nome>.md` |
| PRD | `docs/prd/<nome>.md` |
| Planejamento (épicos e histórias) | `docs/planejamento/<nome>.md` |
| Design de UX | `docs/design/<nome>.md` |
| Design técnico e diagramas | `docs/architecture/<nome>/design.md` |
| Decisões técnicas | `docs/adr/NNNN-titulo.md`, com índice em `docs/adr/README.md` |

`<nome>` em minúsculas e com hífens, o mesmo em todos os arquivos da feature. Nunca sobrescreva um arquivo existente sem avisar.

## Regras para todos os agentes

- Não invente número, prazo, usuário nem decisão. O que faltar vira pergunta em aberto, premissa marcada ou `A definir`.
- Pergunte pouco e só o que muda o escopo. Mostre o resultado de cada etapa e espere a confirmação antes de seguir.
- Mantenha a rastreabilidade: `RF-xx` → `HU-xx` → componente do design → ADR.
- Antes de decidir, leia os ADRs com status `Aceito`; siga-os ou substitua com um novo ADR.
- O arquiteto só lê o código: não roda build nem testes e não altera código sem o usuário pedir.
- Commits: mensagem curta no imperativo, com prefixo (`feat:`, `fix:`, `docs:`, `refactor:`). Não faça push sem o usuário pedir.

## Evals

Os evals usam só o `claude plugin eval`. Os casos ficam em `evals/plugin-eval/` (o formato é dele, não o nosso) e os resultados em `evals/plugin-eval/results/`.
Não altere a skill durante um eval, só teste e reporte.
