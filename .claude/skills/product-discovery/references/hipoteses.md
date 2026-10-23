# Hipóteses e critérios

Material de consulta para escrever hipóteses testáveis e definir de antemão o que as confirma ou refuta. O formato da tabela está em `assets/relatorio-descoberta.md`.

## As quatro frentes

| Frente | Pergunta | Exemplo de hipótese |
|---|---|---|
| Problema | A dor existe e é frequente? | Acreditamos que [usuário] perde tempo com [tarefa]. Saberemos que é verdade se [sinal] |
| Usuário | Estamos falando com a pessoa certa? | Acreditamos que quem decide é [papel]. Saberemos que é verdade se [sinal] |
| Solução | A abordagem resolve? | Acreditamos que [solução] reduz [dor]. Saberemos que é verdade se [sinal] |
| Valor | Vale esforço, dinheiro ou mudança de hábito? | Acreditamos que [usuário] adotaria no lugar de [alternativa]. Saberemos que é verdade se [sinal] |

Comece pelas de problema e usuário. Hipótese de solução antes de confirmar o problema costuma desperdiçar teste.

## Formato

> Acreditamos que **[usuário]** tem **[problema]**. Saberemos que é verdade se **[sinal observável]**.

## Critérios de confirmação e de refutação

Defina os dois **antes** de testar. O limite vem do usuário. Se ele não souber, ofereça uma sugestão marcada como tal ("sugestão, ajuste se tiver outro critério") e não a trate como fato.

| Hipótese | Confirma se | Refuta se | Fica inconclusivo se |
|---|---|---|---|
| H-01 | [sinal + limite] | [sinal + limite] | Entre os dois, ou amostra pequena demais |

Um resultado inconclusivo é legítimo e leva a "Testar mais".

## Priorizar por risco

Para cada hipótese, pergunte:

1. **Se estiver errada, o produto cai?** (impacto)
2. **Temos alguma evidência?** (incerteza)

| Impacto | Evidência | Prioridade |
|---|---|---|
| Alto | Nenhuma | **Testar primeiro** |
| Alto | Fraca (só relato) | Testar logo |
| Baixo | Qualquer | Deixar para depois ou aceitar o risco |
| Alto | Forte | Manter como premissa confirmada |

## Evidência, relato e suposição

| Tipo | Definição | Exemplo |
|---|---|---|
| Evidência | Observado ou medido | Dado de uso, observação do fluxo, pedido real |
| Relato | Alguém contou | "O cliente disse que..." |
| Suposição | Ninguém verificou | "Todo mundo prefere pelo celular" |

Perguntas úteis para classificar uma afirmação: "Você viu isso acontecer?", "Quem te contou?", "Tem algum número ou registro?".

## Hipóteses mal escritas

| Problema | Exemplo | Como arrumar |
|---|---|---|
| Sem sinal | "Os usuários vão gostar" | Dizer o que seria observado se gostassem |
| Sem limite | "Muita gente tem esse problema" | Definir "muita" com o usuário, ou `A definir` |
| Mistura várias | "Gestores têm o problema X e pagariam por Y" | Separar em duas |
| Embute a solução | "Precisamos de um app" | Voltar para a dor |
| Impossível de refutar | "Em algum momento alguém vai usar" | Pôr prazo e quantidade |

## Da hipótese para o método

Escolha o método mais barato que responda à hipótese. A tabela de métodos está no `SKILL.md`. Registre no "Plano de validação" quem, quantos e em que prazo. Esses valores vêm do usuário, e o que faltar fica `A definir`.

## Recomendação

| Resultado | Recomendação |
|---|---|
| Problema e valor confirmados, riscos altos cobertos | **Seguir** |
| Problema confirmado, solução ou escopo precisa mudar | **Ajustar** |
| Evidência fraca ou conflitante | **Testar mais**, dizendo o que testar |
| Problema não confirmado ou sem valor | **Parar** (resultado válido) |

Sempre diga o que mudaria a recomendação.
