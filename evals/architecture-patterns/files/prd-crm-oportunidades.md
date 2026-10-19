# PRD: CRM de oportunidades

## Requisitos funcionais
| ID | Requisito | Prioridade | Critério de aceite | Origem |
| -- | -- | -- | -- | -- |
| RF-01 | Cadastrar oportunidade (nome, valor, etapa) | Essencial | Oportunidade criada aparece na lista da organização | Vendedor precisa registrar negócios |
| RF-02 | Mudar a etapa de uma oportunidade | Essencial | A nova etapa é salva e o histórico registra quem mudou | Vendedor acompanha o funil |
| RF-03 | Listar apenas oportunidades da própria organização | Essencial | Usuário da org A nunca vê dados da org B | Isolamento entre clientes |

## Requisitos não funcionais
| ID | Requisito | Origem |
| -- | -- | -- |
| RNF-01 | Isolamento de dados entre organizações | Contrato com clientes |
