---
name: adr-writer
description: Escreve ADRs (Architecture Decision Records, registros de decisão técnica) no formato MADR enxuto, salvando em docs/adr/ com numeração sequencial. Use sempre que o usuário pedir para "documentar uma decisão", "registrar essa decisão técnica", "escrever um ADR", "por que escolhemos X", ou quando uma decisão de arquitetura, stack, integração ou padrão acabou de ser tomada (por exemplo ao fim de uma análise da skill architecture-patterns, ou numa frase como "vamos com X em vez de Y") e merece ficar registrada, mesmo que o usuário não diga "ADR".
---

# ADR Writer

Registra uma decisão técnica para que quem chegar depois entenda o que foi decidido e por quê. O valor do ADR está no contexto e nas alternativas descartadas, e não só na decisão: sem isso, ninguém sabe se ela ainda vale.

## Princípios

- **Um ADR, uma decisão.** Se aparecerem duas, escreva dois.
- **Só o que foi dito ou decidido.** Não invente motivos, números nem alternativas que ninguém considerou. O que faltar vai como `A definir` ou em "Questões em aberto".
- **Imutável depois de aceito.** Para mudar uma decisão, crie um novo ADR que substitui o anterior e atualize só o campo de status do antigo.
- **Curto.** Uma página basta. Escreva em português, com os termos técnicos em sua forma original.

## Quando oferecer um ADR sem ser pedido

Quando o usuário fechar uma decisão técnica na conversa ("vamos com X em vez de Y", "ficou decidido que..."), ofereça registrar em uma linha e espere a resposta. Não crie o arquivo sem a confirmação dele. Ofereça só para decisões que custam caro para reverter ou que alguém vai questionar depois (stack, arquitetura, integrações, dados, segurança), e não para detalhes menores.

## Passos

1. **Colete o que existe.** Use a conversa, o PRD e os docs do projeto. Identifique: a decisão, o problema que ela resolve, as alternativas consideradas e as consequências. Se faltar algo essencial (a decisão em si, ou por que foi tomada), pergunte antes de escrever.
2. **Escolha o número e o nome.** Liste `docs/adr/`. Use o próximo número sequencial com 4 dígitos e um título em kebab-case: `docs/adr/0003-usar-fila-para-mensagens.md`. Se a pasta não existir, crie-a e comece em `0001`. Nunca sobrescreva um ADR existente.
3. **Preencha o modelo** abaixo.
4. **Status.** Use `Proposto` se ainda precisa de aprovação, `Aceito` se o usuário confirmou, e `Substituído por ADR-NNNN` ou `Rejeitado` quando for o caso. Em dúvida, use `Proposto`.
5. **Atualize o índice.** Mantenha `docs/adr/README.md` com uma tabela `| ADR | Título | Status | Data |`, uma linha por ADR, ligada ao arquivo. Se o índice não existir, crie-o. Quando um ADR substituir outro, atualize o status dos dois no índice e o campo de status do antigo.
6. **Confirme com o usuário** o que foi salvo e liste as lacunas.

## Modelo

```markdown
# ADR-NNNN: <título da decisão, no imperativo ou como afirmação>

- **Status:** Proposto | Aceito | Rejeitado | Substituído por ADR-NNNN
- **Data:** AAAA-MM-DD
- **Decisores:** <nomes ou papéis; "A definir" se não souber>

## Contexto
<Problema e forças em jogo: requisitos, restrições, o que motivou a decisão. Cite a origem (PRD, conversa).>

## Decisão
<O que foi decidido, em uma ou duas frases diretas.>

## Alternativas consideradas
- **<Alternativa A>:** <prós e contras, e por que foi descartada>
- **<Alternativa B>:** ...

## Consequências
- **Positivas:** ...
- **Negativas / custos:** ...
- **Riscos e gatilho de revisão:** <em que condição reabrir a decisão>

## Questões em aberto
- <o que ainda precisa ser confirmado, ou "Nenhuma">

## Relacionados
- <ADR anterior que este substitui ou complementa, diagrama em docs/architecture/, requisito (RF-xx) ou história (HU-xx) de origem; ou "Nenhum">
```

Se a decisão veio de uma análise com a skill `architecture-patterns`, reaproveite as forças, as opções e o gatilho de revisão em vez de reescrever.
