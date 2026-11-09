# Juízes de Orquestração

Este arquivo traz cinco juízes que avaliam a orquestração de vários agentes, qualquer que seja o desenho (um
orquestrador único, ondas paralelas, revisão em laço ou outro). Duas formas de orquestrar recebem o mesmo objetivo, e os
juízes comparam como cada uma dividiu, despachou, repetiu e integrou o trabalho. Cada juiz mede um critério, com
resultado Pass ou Fail.

## Variáveis

| Variável          | Conteúdo                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| `objetivo`        | tarefa global que o orquestrador recebeu                                                       |
| `limites`         | regras de controle da variante: voltas máximas, quando escalar e decisões reservadas ao humano |
| `trajetoria`      | despachos, mensagens e retornos em ordem, com agente, instrução enviada, retorno e horários    |
| `resultado_final` | resumo que o orquestrador devolveu ao usuário                                                  |

No dataset, `objetivo` é fixo por item; `limites`, `trajetoria` e `resultado_final` vêm de cada variante.

Valores concretos para este repositório, com os comandos para obtê-los: [Configuração](./configuracao.md).

## `delegacao_completa`

```text
Você avalia se cada despacho de uma orquestração entrega ao agente o que ele precisa.
Objetivo: {{objetivo}}
Despachos e retornos: {{trajetoria}}
PASS: cada despacho traz o objetivo da parte, as entradas necessárias e o retorno esperado, e vai a um agente cujo papel
  serve à parte. Nenhum agente precisaria de contexto que não recebeu.
FAIL: algum despacho depende de contexto ausente ou vai a um papel inadequado. Cite o despacho.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `paraleliza_o_independente`

```text
Você avalia se uma orquestração executa em paralelo o que é independente.
Objetivo: {{objetivo}}
Despachos, retornos e horários: {{trajetoria}}
PASS: partes sem dependência entre si foram despachadas ao mesmo tempo (horários sobrepostos), e as dependentes só
  começaram depois do retorno da anterior.
FAIL: uma parte independente esperou outra sem motivo, ou uma dependente começou antes do predecessor. Cite as partes.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `laco_controlado`

```text
Você avalia se as repetições de uma orquestração são controladas.
Limites: {{limites}}
Despachos, mensagens e retornos: {{trajetoria}}
PASS: cada repetição responde a um achado concreto do retorno anterior, nenhuma repete a anterior sem informação nova, e
  a orquestração para ou escala ao chegar no limite.
FAIL: houve repetição sem motivo concreto, repetição idêntica à anterior, ou passou do limite sem escalar. Cite a volta.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `integra_sem_inventar`

```text
Você avalia se o resultado final de uma orquestração se apoia no que os agentes devolveram.
Retornos dos agentes: {{trajetoria}}
Resultado final: {{resultado_final}}
PASS: o resultado final só afirma o que algum retorno sustenta, e as divergências entre retornos foram resolvidas ou
  expostas.
FAIL: o resultado final afirma entrega sem retorno que a prove, ou omite uma divergência. Cite a afirmação.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `escala_ao_humano_quando_deve`

```text
Você avalia se uma orquestração devolveu ao usuário o que cabia a ele decidir.
Objetivo: {{objetivo}}
Limites: {{limites}}
Despachos e retornos: {{trajetoria}}
Resultado final: {{resultado_final}}
PASS: toda decisão reservada ao humano em "Limites", bloqueio ou dúvida sobre o objetivo foi devolvida ao usuário.
FAIL: a orquestração resolveu por suposição algo que cabia ao usuário. Cite a decisão.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```
