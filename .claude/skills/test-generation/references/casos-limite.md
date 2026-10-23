# Catálogo de Casos Limite

Casos que costumam revelar defeito. Para cada comportamento da lista, percorra as famílias que se aplicam e acrescente
os casos que fazem sentido para a regra.

## Entrada

| Família                            | Casos                                                                                |
| ---------------------------------- | ------------------------------------------------------------------------------------ |
| Número                             | `0`, `-1`, o mínimo, o máximo, o máximo + 1, decimal onde se espera inteiro          |
| Texto                              | vazio, só espaços, no tamanho máximo, uma letra acima do máximo, acentos e emoji     |
| Lista de valores (estágio, status) | cada valor válido, um valor fora da lista, maiúscula e minúscula                     |
| Data                               | passado, futuro, fim do mês, fuso horário diferente                                  |
| Campo opcional                     | ausente, `null`, vazio                                                               |
| Campo de controle                  | `organization_id`, dono ou papel enviados no corpo: devem ser ignorados ou recusados |

## Identificador

| Caso                                      | Resultado esperado comum    |
| ----------------------------------------- | --------------------------- |
| Id existente da própria organização       | `200` com o dado            |
| Id inexistente                            | `404`                       |
| Id de outra organização                   | `404`, igual ao inexistente |
| Id malformado (`abc` onde se espera UUID) | `422`                       |

## Autenticação

| Caso                                 | Resultado esperado comum               |
| ------------------------------------ | -------------------------------------- |
| Sem token                            | `401` ou `403`, como as rotas vizinhas |
| Token inválido ou expirado           | `401` ou `403`                         |
| Usuário inativo                      | `400` ou `403`, como as rotas vizinhas |
| Usuário comum em rota administrativa | `403`                                  |

## Isolamento entre Organizações

Crie o recurso na organização A e chame com o usuário da organização B:

| Operação                             | Resultado esperado                                   |
| ------------------------------------ | ---------------------------------------------------- |
| Listagem                             | O recurso de A não aparece e a contagem não o inclui |
| Leitura por id                       | `404`                                                |
| Atualização                          | `404`, e o recurso de A continua igual               |
| Exclusão                             | `404`, e o recurso de A continua existindo           |
| Criação apontando para entidade de A | `404` ou `422`, e nada é gravado                     |

## Listagem

| Caso        | O que conferir                                                                           |
| ----------- | ---------------------------------------------------------------------------------------- |
| Lista vazia | `data` vazio e `count` igual a `0`                                                       |
| Paginação   | `skip` além do total devolve lista vazia; `limit` respeitado                             |
| Ordem       | A ordem documentada (ex.: mais recente primeiro) com dois registros criados em sequência |
