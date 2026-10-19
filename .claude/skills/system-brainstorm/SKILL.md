---
name: system-brainstorm
description: Recebe uma ideia bruta de sistema, app, plataforma, integração ou produto e conduz um brainstorm guiado com o usuário, fazendo poucas perguntas focadas por rodada até a ideia ficar clara o bastante para ser especificada. Termina com um resumo estruturado (problema, usuários, escopo, requisitos, riscos, perguntas em aberto). Use sempre que o usuário compartilhar uma ideia de sistema que quer construir, disser coisas como "tenho uma ideia de sistema", "quero criar um app/plataforma/sistema para...", "vamos fazer um brainstorm", "me ajuda a pensar nessa ideia", ou descrever um produto de forma vaga sem ter definido o escopo, mesmo que nunca diga a palavra "brainstorm".
---

# Brainstorm de Sistema

Transforme uma ideia vaga de sistema em um entendimento claro e compartilhado, por meio de conversa. O usuário costuma
chegar com uma frase ou um parágrafo. O seu valor está nas perguntas que ele ainda não se fez. Boas perguntas agora
evitam retrabalho depois, então pergunte antes de propor soluções.

## Idioma

Converse e escreva o resumo final em português do Brasil. Mantenha termos técnicos e identificadores no original.
Para suportar outro idioma no futuro, altere esta seção, o corpo do arquivo e os títulos do modelo de resumo.

## Fluxo

1. **Reformule a ideia.** Em uma ou duas frases, diga o que você entendeu e liste as premissas que está assumindo. Isso
   permite ao usuário corrigir um mal-entendido antes que ele influencie todo o resto.
2. **Pergunte em rodadas de 2 a 4 perguntas.** Várias perguntas de uma vez mantêm a conversa andando, mas mais de quatro
   sobrecarregam. Use a ferramenta AskUserQuestion quando ela estiver disponível, oferecendo de 2 a 4 opções concretas
   por pergunta (o usuário sempre pode digitar a própria resposta). Caso contrário, use uma lista numerada curta com
   sugestões de resposta.
3. **Adapte-se a cada rodada.** Pule os temas que o usuário já respondeu. Aprofunde respostas vagas ("rápido", "muitos
   usuários", "seguro") pedindo um número ou um exemplo. Aponte contradições e trade-offs que você perceber, e dê uma
   recomendação quando o usuário estiver indeciso, em vez de só listar opções.
4. **Pare quando for o bastante.** Em geral, de 3 a 5 rodadas. Quando as perguntas restantes não mudarem o escopo, diga
   isso e ofereça encerrar. Não interrogue por completude: o que ficar sem resposta vai para "Perguntas em aberto".
5. **Entregue o resumo** usando o modelo abaixo e pergunte se falta algo ou se algo está errado. Se o usuário quiser um PRD, a skill `prd-writing` usa esse resumo como entrada.

## Temas a cobrir

Escolha o que importa para esta ideia. É um cardápio, não uma lista de verificação.

- **Problema e valor:** quem sofre hoje, como lida com isso agora, por que vale a pena construir.
- **Usuários:** quem são, quantos, quão técnicos, o que cada um precisa realizar.
- **Escopo:** o fluxo principal de ponta a ponta, o que a primeira versão precisa fazer, o que está fora.
- **Requisitos funcionais:** o que o sistema precisa fazer, com prioridade (essencial, importante, desejável) e como
  saber que cada item está pronto.
- **Dados e integrações:** que dados entram e saem, sistemas existentes a conectar, quem é o dono deles.
- **Requisitos não funcionais:** carga esperada, latência, disponibilidade, segurança, privacidade e conformidade (por
  exemplo, LGPD).
- **Restrições:** tamanho do time, prazo, orçamento, stack ou infraestrutura obrigatória.
- **Sucesso:** como o usuário saberá que funcionou: uma métrica com valor atual e meta, ou um resultado observável.
- **Pessoas e prazos:** quem decide, quem é afetado, marcos esperados e dependências de outras equipes.
- **Riscos e incógnitas:** o que pode fazer o projeto falhar, o que depende de terceiros.

## O que não fazer

- Não desenhe a arquitetura, não escolha tecnologias e não escreva código, a menos que o usuário peça. O objetivo aqui é
  o "o quê e por quê". O "como" vem depois, e misturar os dois cedo demais trava escolhas antes de o problema ser
  entendido.
- Não invente respostas. Se o usuário não souber, registre como pergunta em aberto ou como premissa identificada.

## Modelo de resumo

Use estes títulos. Mantenha cada seção curta e concreta, e omita uma seção só se ela realmente não se aplicar.

```markdown
# [Nome do sistema]

## Resumo
Uma ou duas frases sobre o que é e para quem.

## Problema e valor
## Usuários e necessidades
## Escopo do MVP
- Dentro:
- Fora:
## Fluxo principal
## Requisitos funcionais
- [Essencial | Importante | Desejável] requisito, e como saber que está pronto
## Dados e integrações
## Requisitos não funcionais
## Restrições
## Critérios de sucesso
Métrica, valor atual e meta.
## Riscos
## Partes interessadas
## Marcos e dependências
## Premissas
## Perguntas em aberto
```
