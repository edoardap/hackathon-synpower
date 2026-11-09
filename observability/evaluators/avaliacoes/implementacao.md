# Juízes de Implementação

Este arquivo traz seis juízes que avaliam um diff produzido por uma variante (uma skill, um prompt, um modelo ou um
fluxo) contra a tarefa que ela recebeu. Cada juiz mede um critério, com resultado Pass ou Fail. Os critérios não citam
skills nem agentes: o que muda de uma variante para outra entra pelas variáveis.

## Variáveis

| Variável    | Conteúdo                                                                       |
| ----------- | ------------------------------------------------------------------------------ |
| `tarefa`    | issue, critérios de aceite e restrições entregues à variante                   |
| `regras`    | o que a variante devia seguir: `AGENTS.md`, skills e convenções do repositório |
| `diff`      | alteração que a variante produziu                                              |
| `evidencia` | saída dos testes e do lint rodados sobre o diff                                |

No dataset, `tarefa` e `regras` são fixos por item; `diff` e `evidencia` vêm de cada variante.

Valores concretos para este repositório, com os comandos para obtê-los: [Configuração](./configuracao.md).

## `atende_a_tarefa`

```text
Você avalia se uma alteração de código atende à tarefa pedida.
Tarefa: {{tarefa}}
Alteração (diff): {{diff}}
PASS: cada critério de aceite da tarefa tem uma mudança no diff que o implementa, e você aponta arquivo e linha.
FAIL: algum critério de aceite não tem mudança correspondente, ou a mudança o contradiz.
Escreva a justificativa citando o trecho que sustenta a decisão e, depois, o resultado: Pass ou Fail.
```

## `escopo_fiel`

```text
Você avalia se uma alteração de código se limita ao que a tarefa pede.
Tarefa: {{tarefa}}
Alteração (diff): {{diff}}
PASS: todo arquivo e todo trecho alterado serve a um item da tarefa.
FAIL: o diff inclui refatoração, arquivo, funcionalidade ou formatação que nenhum item da tarefa exige. Cite o trecho.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `segue_as_regras`

```text
Você avalia se uma alteração de código respeita as regras que a variante devia seguir.
Regras: {{regras}}
Alteração (diff): {{diff}}
PASS: nenhuma regra de "Regras" é violada pelo diff. Regra que não se aplica ao diff não conta.
FAIL: o diff viola ao menos uma regra. Cite a regra e o trecho do diff que a viola.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `solucao_minima`

```text
Você avalia se uma alteração de código é a menor que resolve a tarefa.
Tarefa: {{tarefa}}
Alteração (diff): {{diff}}
PASS: o diff não acrescenta abstração, camada, opção de configuração, dependência ou generalização que a tarefa não
  exige, e não reescreve algo que o próprio diff mostra já existir.
FAIL: o diff acrescenta algo dessa lista sem a tarefa exigir. Cite o trecho.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `seguranca`

```text
Você avalia se uma alteração de código introduz risco de segurança.
Alteração (diff): {{diff}}
PASS: o diff não contém segredo nem credencial, valida na fronteira a entrada que vem de fora, não monta comando,
  consulta ou caminho com dado não validado e não reduz uma checagem de autorização existente.
FAIL: o diff tem ao menos um desses riscos. Cite o trecho e o risco.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```

## `testes_provam_o_comportamento`

```text
Você avalia se os testes provam o comportamento que a alteração muda.
Tarefa: {{tarefa}}
Alteração (diff): {{diff}}
Saída dos testes e do lint: {{evidencia}}
PASS: para cada comportamento novo ou corrigido, o diff inclui um teste que falharia sem a mudança, e a saída mostra os
  testes passando.
FAIL: algum comportamento mudado não tem teste, o teste só executa o código sem verificar o resultado, ou a saída mostra
  falha ou não mostra execução.
Escreva a justificativa e, depois, o resultado: Pass ou Fail.
```
