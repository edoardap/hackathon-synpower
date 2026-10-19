---
name: product-design
description: Transforma requisitos, histórias e critérios de aceite em uma especificação de design em Markdown, cobrindo três frentes - UI/UX (fluxos, telas, estados, usabilidade), design visual (princípios visuais, tokens, componentes) e design de conversa (roteiro de conversas guiadas, tom e comportamento de agentes de IA). Use sempre que o usuário pedir "desenha as telas", "fluxo de usuário", "wireframe", "design system", "identidade visual", "paleta e tipografia", "roteiro da conversa", "como o agente deve falar", "experiência do usuário leigo", ou quiser transformar o PRD em design, mesmo que não diga a palavra "design".
---

# Product Design

Produz uma especificação de design que outro agente ou pessoa consegue implementar sem adivinhar. A saída é um documento Markdown em português, e não um protótipo. O design serve aos requisitos e ao usuário, então cada tela, componente e fala do agente aponta para uma história ou necessidade que a justifica.

## Princípios

- **Parta de quem usa.** Identifique o usuário e o contexto dele nos docs do projeto (PRD, brainstorm). Para usuários leigos, o design reduz decisões, usa a linguagem dele e explica passos técnicos em vez de escondê-los.
- **Rastreie cada decisão.** Cada tela, componente ou fala cita a origem (RF-xx, HU-xx). Sem origem, é especulação e deve ser questionada.
- **Não invente.** Marca, cores da empresa, métricas de usabilidade e textos finais que o usuário não definiu ficam como proposta marcada `a validar`. Dados de pesquisa com usuários não existem até alguém coletar.
- **Cubra todos os estados.** Toda tela tem estado vazio, carregando, sucesso e erro. Os erros dizem o que aconteceu e o que fazer.
- **Acessibilidade desde o início.** Contraste legível, navegação por teclado, rótulos claros e não depender só de cor.
- **Simples primeiro.** Entregue o mínimo que cobre o escopo confirmado (MVP). Itens Desejáveis ficam em seção separada.

## Passos

1. **Contexto.** Leia os docs do projeto (`docs/prd/`, `docs/planejamento/`, `docs/brainstorm/`). Resuma o usuário, o objetivo e as restrições em poucas linhas, separando o confirmado do presumido.
2. **Escolha as frentes.** Veja o que o pedido exige e leia só as referências necessárias:
   - Fluxos, telas e estados: `references/ux.md`
   - Cores, tipografia, tokens e componentes: `references/visual.md`
   - Roteiro de conversa e comportamento de agentes de IA: `references/conversa.md`
3. **Desenhe.** Siga o roteiro da referência de cada frente. Comece pelo fluxo ponta a ponta e depois detalhe.
4. **Verifique a cobertura.** Toda história do MVP aparece em pelo menos uma tela ou fluxo, e cada tela cita sua história.
5. **Registre as pendências** e o que precisa de validação com o usuário.

## Formato da saída

```
# Design: <nome do produto ou funcionalidade>

## Contexto
<usuário, objetivo, restrições; origem dos dados>

## UX
### Fluxo principal
<passos numerados, com a história de origem>
### Telas
#### <Tela> (origem: HU-xx)
- Objetivo, conteúdo, ações, estados (vazio, carregando, sucesso, erro)

## Visual
<princípios, tokens, componentes; itens a validar>

## Conversa
<camadas, roteiro, tom, casos limite>

## Cobertura
| História | Tela / fluxo | Status |

## Pendências
- <o que depende do usuário, e por quê>
```

Inclua só as frentes que o pedido cobre e omita as outras. Salve em `docs/design/<nome>.md` (nome em minúsculas e com hífens) apenas quando o usuário aceitar, e não sobrescreva um arquivo existente sem avisar. Não escreva código nem gere protótipo, a menos que o usuário peça.
