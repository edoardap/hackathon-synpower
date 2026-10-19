---
name: architecture-patterns
description: Ajuda a tomar decisões de arquitetura de software: escolher entre padrões e estilos (monolito, monolito modular, microsserviços, camadas, hexagonal, event-driven, filas, CQRS, multi-tenant, plugins/adapters), separar responsabilidades, definir limites entre módulos e avaliar trade-offs contra requisitos e restrições reais. Use sempre que o usuário perguntar "qual arquitetura usar", "como estruturar esse sistema", "monolito ou microsserviços", "como organizar os módulos", "como deixar extensível", pedir desenho técnico a partir de um PRD, comparar abordagens de design, ou pedir diagramas de arquitetura (C4, Mermaid, contexto, containers), mesmo que não diga a palavra "arquitetura".
---

# Architecture Patterns

Conduz uma decisão de arquitetura do requisito até uma recomendação defendida. O objetivo é escolher o padrão mais simples que atende aos requisitos, e não o mais sofisticado. Padrão sem requisito que o justifique é custo sem retorno.

## Princípios

- **Requisito primeiro, padrão depois.** Comece pelo que força a decisão (prazo, tamanho do time, carga, extensibilidade, compliance) e só então escolha. Se esses dados não existirem, pergunte ou registre como premissa. Não invente números.
- **Comece simples.** Prefira o monolito modular a microsserviços até existir um motivo concreto (escala independente, times independentes, isolamento de falha). Uma extensibilidade exigida pode ser atendida com uma fronteira bem desenhada (interface/adapter), sem serviços separados.
- **Toda escolha tem custo.** Para cada opção, diga o que se ganha e o que se paga (complexidade operacional, consistência, curva de aprendizado, risco de prazo).
- **Decisões difíceis de reverter merecem mais análise.** Dados, contratos públicos e fronteiras entre módulos custam caro para mudar. Detalhes internos não.
- **Respeite o que já existe.** Em repositório existente, entenda a estrutura e as convenções antes de propor (use a skill `repo-orientation` se ainda não foi feita).

## Passos

1. **Contexto.** Resuma o problema em 2 ou 3 linhas e liste os requisitos que mais pesam, separando os confirmados dos presumidos. Se houver PRD ou docs do projeto, leia-os e cite a origem.
2. **Forças e restrições.** Liste o que limita a decisão: prazo, time, stack já fixada, orçamento, regulação (ex.: LGPD), integrações externas. Passe pelas dimensões de `references/design-doc.md` (falha parcial, idempotência, auth, concorrência, ciclo de vida dos dados, observabilidade) para não deixar pontos cegos.
3. **Opções.** Em decisão grande ou difícil de reverter, apresente de 2 a 4 alternativas reais, incluindo a mais simples. Em decisão pequena, recomende direto e cite a alternativa descartada em uma linha. Consulte `references/padroes.md` para o catálogo de padrões e quando cada um se aplica.
4. **Trade-offs.** Compare as opções contra as forças do passo 2, em uma tabela curta. Marque riscos e o que é reversível.
5. **Recomendação.** Escolha uma opção, justifique ligando aos requisitos e diga em que condição você mudaria de ideia (o "gatilho de revisão").
6. **Perguntas em aberto.** Liste o que falta para confirmar a decisão e quem deveria responder.
7. **Diagrama (opcional).** Se a decisão definir a estrutura do sistema, ofereça os diagramas de Contexto e de Container da opção escolhida, em C4 com Mermaid. Siga `references/c4-mermaid.md`. Só desenhe o que já foi decidido e marque o resto como `a validar`.
8. **Design técnico.** Se a decisão pedir componentes novos, ofereça detalhar com o modelo de `references/design-doc.md` e salve em `docs/architecture/<nome>/design.md`.
9. **Registro.** Se a decisão for relevante, ofereça documentá-la com a skill `adr-writer`.

## Formato da resposta

```
## Decisão: <tema>

### Contexto
...

### Forças e restrições
- ...

### Opções
| Opção | Ganha | Paga | Reversível? |
|---|---|---|---|

### Recomendação
<opção> porque <requisitos>. Revisar se <gatilho>.

### Perguntas em aberto
- ...

### Diagrama (se aceito)
<Contexto e Container em Mermaid C4>
```

Mantenha curto. Não desenhe a arquitetura inteira se a pergunta é sobre uma decisão específica, e não proponha tecnologia nem número (latência, custo, volume) que o usuário não informou.
