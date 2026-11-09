# Juízes de Revisão de Código

Este arquivo traz seis juízes que avaliam um relatório de revisão de código, qualquer que seja o revisor (um agente, uma
skill, um modelo ou uma pessoa). O dataset guarda um diff com defeitos conhecidos, e cada variante de revisão devolve o
seu relatório sobre o mesmo diff. Cada juiz mede um critério, com resultado Pass ou Fail.

## Variáveis

| Variável              | Conteúdo                                                                                 |
| --------------------- | ---------------------------------------------------------------------------------------- |
| `diff`                | código revisado                                                                          |
| `defeitos_conhecidos` | defeitos reais do diff, um por linha, com arquivo, linha e causa; vêm do item do dataset |
| `revisao`             | relatório que a variante de revisão devolveu                                             |

No dataset, `diff` e `defeitos_conhecidos` são fixos por item; `revisao` vem de cada variante. Para medir falso alarme,
inclua diffs sem defeito algum e deixe `defeitos_conhecidos` vazio.

Valores concretos para este repositório, com os comandos para obtê-los: [Configuração](./configuracao.md).

## `acha_os_defeitos_conhecidos`

```text
Você avalia se um relatório de revisão encontrou os defeitos reais de um código.
Defeitos conhecidos: {{defeitos_conhecidos}}
Relatório: {{revisao}}
PASS: cada defeito conhecido aparece no relatório como um achado com a mesma causa e o mesmo trecho.
FAIL: ao menos um defeito conhecido não aparece. Liste os ausentes.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `sem_falso_alarme`

```text
Você avalia se todo achado de um relatório de revisão descreve um problema real do código.
Código: {{diff}}
Defeitos conhecidos: {{defeitos_conhecidos}}
Relatório: {{revisao}}
PASS: cada achado aponta um problema que existe no código ou está nos defeitos conhecidos.
FAIL: algum achado descreve linha, comportamento ou erro que o código não tem. Cite o achado e o que o código mostra.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `evidencia_verificavel`

```text
Você avalia se os achados de um relatório de revisão trazem evidência que se pode conferir.
Relatório: {{revisao}}
PASS: cada achado cita arquivo e linha e mostra o valor ou o resultado de comando que demonstra o problema.
FAIL: algum achado não cita o local, ou afirma o problema sem demonstrá-lo. Cite o achado.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `severidade_coerente`

```text
Você avalia se a severidade dos achados de um relatório de revisão corresponde ao impacto.
Código: {{diff}}
Relatório: {{revisao}}
PASS: o que quebra comportamento, perde dado ou abre falha de segurança está marcado como bloqueante, e o que é estilo
  ou preferência não está.
FAIL: algum achado tem severidade desproporcional ao impacto. Cite o achado e o impacto real.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `correcao_acionavel`

```text
Você avalia se os achados de um relatório de revisão trazem uma correção que alguém sem contexto consegue aplicar.
Relatório: {{revisao}}
PASS: cada achado traz a mudança concreta (diff ou edição exata) e como verificá-la.
FAIL: algum achado traz só conselho genérico, como "melhore" ou "refatore". Cite o achado.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `veredito_coerente`

```text
Você avalia se o veredito de um relatório de revisão é coerente com os achados dele.
Relatório: {{revisao}}
PASS: o relatório reprova se e somente se tem ao menos um achado bloqueante.
FAIL: o relatório aprova com achado bloqueante ou reprova sem nenhum. Cite o veredito e o achado.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```
