# Padrão em Camadas

Mapa para repositórios FastAPI que já separam rota, serviço e repositório. É uma versão reduzida da *Layered Capability
Architecture* (LCA): cada camada importa apenas as camadas abaixo dela.

```text
Entrada (app.py) → Rota (routers/) → Serviço (services/) → Repositório (repository/) → Plataforma (config, conexões) → Contratos (schemas/, models/, exceptions/)
```

## Onde Fica Cada Código

Percorra de cima para baixo e pare no primeiro sim.

| #   | O código…                                                          | Vai para                             |
| --- | ------------------------------------------------------------------ | ------------------------------------ |
| 1   | Reage a um estímulo externo (requisição HTTP, comando, evento)     | `routers/`                           |
| 2   | Monta consulta ou usa a sessão do banco para ler e gravar          | `repository/<entidade>.py`           |
| 3   | Tem regra de negócio ou orquestra várias operações                 | `services/<entidade>.py`             |
| 4   | Faz I/O ou guarda estado técnico (cliente HTTP, configuração, log) | `core/` ou `connectors/`             |
| 5   | É um tipo: entrada, saída, tabela, exceção                         | `schemas/`, `models/`, `exceptions/` |
| 6   | É função pura sem I/O                                              | `utils/<assunto>.py`                 |

## Regras

- **Dependência para baixo.** Um módulo nunca importa de uma camada acima dele. A rota chama o serviço; o serviço chama
  o repositório.
- **Repositório simples.** O repositório devolve a entidade, `None` ou lista vazia. Quem decide que `None` vira `404` é
  o serviço ou a rota.
- **O serviço faz o *commit*.** O repositório faz `add` e `flush`; o serviço confirma a transação quando a operação
  inteira está consistente. Assim uma operação de vários passos é desfeita como unidade.
- **Modelo para no serviço.** A rota devolve schema público, e o schema nunca importa o modelo de tabela.
- **Dependências pelo construtor.** O serviço recebe o repositório pronto, montado em `dependencies/`. Para usar outra
  entidade, injete o repositório dela, e não o serviço dela.
- **Mesmo nome em toda camada.** `opportunity.py` em `routers/`, `services/`, `repository/`, `schemas/` e `models/`.
  Arquivo ausente é informação: sem `models/opportunity.py`, a entidade não é persistida.
- **Estrutura do tamanho do problema.** Pasta vazia "para depois" e interface com uma única implementação são custo sem
  benefício.

## Anti-padrões

| Anti-padrão                  | Sintoma                                                      | Correção                                                           |
| ---------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------ |
| Regra de negócio na rota     | `if opportunity.stage == "won": raise ...` dentro do handler | O serviço levanta exceção de domínio; a rota só a converte em HTTP |
| Repositório com regra        | `get_or_raise()`, código HTTP dentro do repositório          | Devolver `None` e decidir no serviço                               |
| Consulta fora do repositório | `select(...)` em serviço ou rota                             | Mover para `repository/`                                           |
| Configuração espalhada       | `os.getenv()` no meio do código                              | Campo em `Settings`, lido na inicialização                         |
| Abstração prematura          | `base/` e `registry.py` para uma implementação               | Módulo simples até existir a segunda implementação                 |
