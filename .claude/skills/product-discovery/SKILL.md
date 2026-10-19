---
name: product-discovery
description: Conduz a descoberta de produto para validar se um problema vale a pena ser resolvido antes de especificar a solução. Transforma uma ideia ou um problema em hipóteses testáveis (problema, usuário, solução, valor), mapeia as evidências que existem e as que faltam, propõe experimentos e entrevistas baratas e termina com uma recomendação (seguir, ajustar, testar mais ou parar). Use sempre que o usuário falar em "descoberta de produto", "product discovery", "validar a ideia", "vale a pena construir isso?", "hipóteses", "pesquisa com usuários", "roteiro de entrevista", "MVP de teste", "como saber se alguém quer isso", ou quiser validar uma ideia antes de escrever o PRD, mesmo que não diga "discovery".
---

# Descoberta de Produto

Ajude o usuário a descobrir se o problema é real, se importa para as pessoas certas e se a solução imaginada tem chance
de funcionar, antes de gastar tempo especificando e construindo. O risco mais caro de um produto é construir bem algo que
ninguém precisa. Aqui você separa o que o usuário **sabe** do que ele **acha**, e transforma o que ele acha em algo que
dá para testar.

## Idioma

Converse e escreva o relatório final em português do Brasil. Mantenha termos técnicos e identificadores no original.

## Entrada

Aceite uma ideia solta, um problema percebido, notas de conversas com clientes, dados existentes ou um resumo. 
Procure na conversa o que já foi dito; se o usuário indicar um arquivo, leia-o. Não peça de novo o que ele já
informou.

## Fluxo

1. **Reformule o problema, não a solução.** Em uma ou duas frases, diga qual dor você entendeu, de quem, e liste as
   premissas que está assumindo. Se o usuário chegou com uma solução ("um app que..."), recue para o problema que ela
   resolve.
2. **Separe fatos de suposições.** Pergunte de onde vem cada afirmação importante: ele viu isso acontecer, ouviu de
   alguém, tem um dado, ou é intuição? Classifique cada uma como **Evidência** (observada ou medida), **Relato** (alguém
   contou) ou **Suposição** (ninguém verificou). Use rodadas de 2 a 4 perguntas, com AskUserQuestion quando disponível.
3. **Escreva as hipóteses.** Converta as suposições mais arriscadas em hipóteses testáveis, no formato "Acreditamos que
   [usuário] tem [problema]. Saberemos que é verdade se [sinal observável]". Priorize por risco: o que, se estiver
   errado, derruba o produto, e o que ainda não tem nenhuma evidência.
4. **Proponha a forma mais barata de testar.** Para cada hipótese prioritária, sugira um método proporcional ao risco
   (veja a tabela) e defina de antemão o resultado que confirma e o que refuta. Combinar o critério antes evita
   interpretar qualquer resultado como sucesso.
5. **Prepare o que o usuário vai levar a campo,** se ele pedir: roteiro de entrevista, perguntas de um formulário ou o
   desenho do teste.
6. **Entregue o relatório** com o modelo abaixo, incluindo uma recomendação clara e o que mudaria essa recomendação.
   Pergunte se falta algo e ofereça o próximo passo (`system-brainstorm` ou `prd-writing`, se for seguir).

## Métodos de teste

Escolha o mais simples que responda à pergunta.

| Pergunta de risco | Método | Custo |
| -- | -- | -- |
| O problema existe e dói? | Entrevistas sobre o passado, observação do fluxo atual | Baixo |
| Quantas pessoas têm esse problema? | Formulário curto, dados já existentes, busca por sinais de demanda | Baixo |
| Já tentam resolver de outro jeito? | Mapa de alternativas (planilha, concorrente, "não fazer nada") | Baixo |
| A solução faz sentido para o usuário? | Protótipo de papel ou tela, teste de conceito | Médio |
| Pagariam ou mudariam de hábito? | Página de interesse, lista de espera, piloto manual ("concierge") | Médio |
| Funciona na prática? | Piloto com poucos usuários, versão mínima | Alto |

## Regras de qualidade

- **Comportamento vale mais que opinião.** "Eu usaria" não é evidência. Perguntas sobre o que a pessoa fez da última vez
  que teve o problema, o que tentou e quanto custou revelam mais do que perguntas sobre o futuro.
- **Pergunte sobre o passado, não sobre a ideia.** Em roteiros de entrevista, evite perguntas que apresentam a solução ou
  induzem à resposta ("você não acha que seria útil...?").
- **Hipótese sem critério não é hipótese.** Toda hipótese leva um sinal observável e um limite que a confirma ou refuta.
  Não invente o limite: se o usuário não souber, proponha uma sugestão marcada como tal.
- **Não invente evidência.** Números, citações de usuários e tamanhos de mercado vêm do usuário ou de fontes que ele
  indicar. O que não existe vira suposição declarada.
- **Honestidade na recomendação.** Se as evidências são fracas, diga que ainda não dá para decidir, em vez de forçar um
  "vá em frente". Parar também é um resultado válido da descoberta.
- **Sem solução técnica.** Não escolha tecnologia nem desenhe arquitetura. O foco é problema, usuário e valor.

## Modelo do relatório

Mantenha cada seção curta e concreta. Omita uma seção só se ela realmente não se aplicar.

```markdown
# Descoberta: [Nome da ideia ou do problema]

## Resumo
Uma ou duas frases: o problema, para quem, e a recomendação.

## Problema
Qual é a dor, de quem, em que situação e com que frequência.

## Usuários e contexto
Quem são, como lidam com o problema hoje e que alternativas usam (inclusive "não fazer nada").

## O que já sabemos
| Afirmação | Tipo (Evidência / Relato / Suposição) | Fonte |
| -- | -- | -- |

## Hipóteses
| ID | Hipótese | Risco | Sinal que confirma | Sinal que refuta |
| -- | -- | -- | -- | -- |
| H-01 | Acreditamos que... | Alto | | |

## Plano de validação
| Hipótese | Método | Quem/quantos | Prazo | Resultado esperado |
| -- | -- | -- | -- | -- |

## Roteiro de entrevista (opcional)
Perguntas sobre comportamento passado, em ordem.

## Recomendação
Seguir, Ajustar, Testar mais ou Parar, com o motivo e o que mudaria a decisão.

## Perguntas em aberto
```
