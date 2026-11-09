# Configurar as Seis Regras de Implementação no Opik

Cada regra tem um arquivo com o texto do prompt em `observability/evaluators/`, no mesmo lugar do `code_quality.md`.
Este guia diz, para cada uma, o que colar, quais variáveis aparecem no prompt, qual campo do Opik cada variável recebe e
o que a nota significa.

## Como a Variável Funciona

Numa regra online, o `{{...}}` do prompt é trocado, a cada trace avaliado, pelo valor de um campo dele. O caminho começa
em `input`, `output` ou `metadata`. A variável `{{trace}}` entrega o trace inteiro ao juiz, no modo *Agent as a Judge*,
e ele lê os spans com ferramentas.

Na tela de criação, digite `{{` no prompt para abrir a lista de campos de traces recentes e escolha o campo. O Opik
guarda o par variável e campo: a `code_quality` ficou com `trace`, `var_1` = `input.value` e `var_2` =
`metadata.artifact.code`. Se a sua tela mostrar o nome da variável e o campo em colunas separadas, use o campo da tabela
abaixo.

## Criar Cada Regra

1. No projeto `hackathon-synpower`, abra *Online evaluation*, clique em *Evaluator* e escolha *LLM-as-a-Judge*.
2. Dê à regra o nome do arquivo (sem `.md`) e cole o conteúdo do arquivo no editor de prompt.
3. Confira cada `{{...}}` do prompt contra a tabela da próxima seção.
4. Escolha o modelo no cabeçalho do prompt. Para as regras com `{{trace}}`, use um modelo com chamada de ferramenta; sem
   ela, o juiz lê só uma versão truncada do trace.
5. À direita: *Scope* = Traces; filtro com a tag `code_written`; *Sampling rate* `1` na primeira semana; *Cost limit* da
   tabela.
6. Em *Score configuration*, nomeie o score principal com o nome da regra, escolha *Boolean* e escreva a instrução:
   "true se o resultado for PASS; false se for FAIL".
7. Clique em *Create evaluator*, termine um turno que escreva código e confira a nota no trace.

A `code_quality` atual está sem filtro e com limite de US$ 10. As seis novas levam o filtro `code_written`, para não
gastar juiz em turno sem código, e um limite menor.

## Mapa Por Regra

| Arquivo               | Variáveis no prompt                              | Campo do Opik                            | Modelo             | Cost limit |
| --------------------- | ------------------------------------------------ | ---------------------------------------- | ------------------ | ---------- |
| `task_completion.md`  | `{{trace}}`                                      | o trace inteiro, sem campo               | com ferramenta     | US$ 0,20   |
| `scope_adherence.md`  | `{{trace}}`                                      | o trace inteiro, sem campo               | com ferramenta     | US$ 0,20   |
| `test_adequacy.md`    | `{{trace}}`                                      | o trace inteiro, sem campo               | com ferramenta     | US$ 0,20   |
| `rules_adherence.md`  | `{{metadata.artifact.code}}`                     | `metadata.artifact.code`                 | `claude-haiku-5-5` | US$ 0,05   |
| `minimal_solution.md` | `{{input.value}}` e `{{metadata.artifact.code}}` | `input.value` e `metadata.artifact.code` | `claude-haiku-5-5` | US$ 0,05   |
| `security.md`         | `{{metadata.artifact.code}}`                     | `metadata.artifact.code`                 | `claude-haiku-5-5` | US$ 0,05   |

Os limites são ponto de partida. O modelo com ferramenta pode ser o Sonnet 5.5, se o seu provedor o listar; o Haiku 5.5
é o que a `code_quality` já usa.

## O Que Cada Campo Traz

- **`{{input.value}}`:** o pedido do turno. Num turno aberto por notificação do hook, vem a notificação com a sua
  mensagem dentro.
- **`{{metadata.artifact.code}}`:** o código escrito no turno, com o caminho de cada arquivo, até 20 KB e sem arquivos
  `.md`.
- **`{{trace}}`:** o pedido, os spans de ferramenta com entrada e saída e o código escrito.

## Colar as Regras do Repositório

O `rules_adherence.md` tem o marcador `[COLE AQUI ...]`. A regra online só lê campos do trace, então o texto das regras
vai literal no prompt. Imprima as seções "Regras para todos os agentes" e "Implementação e qualidade" do `AGENTS.md` (18 linhas, cerca de
1,3 KB) e cole no lugar do marcador:

```bash
awk '/^## /{p=/^## (Regras para todos os agentes|Implementação e qualidade)$/} p' AGENTS.md
```

O `AGENTS.md` daqui traz regras de processo, sem estilo de código. Para medir estilo, acrescente o texto das skills
`backend-patterns` e `frontend-patterns`. Para outro repositório, duplique a regra e cole as regras dele.

## O Que Cada Nota Significa

| Score              | `true` quando                               | A média mostra                                            | Cuidado                                                        |
| ------------------ | ------------------------------------------- | --------------------------------------------------------- | -------------------------------------------------------------- |
| `task_completion`  | tudo que o pedido exige foi feito           | fração dos turnos com código em que o pedido foi cumprido | FAIL por "faltou evidência" é trace sem prova                  |
| `scope_adherence`  | toda alteração serve ao pedido              | fração dos turnos sem mudança fora do pedido              | o relatório cita o arquivo                                     |
| `test_adequacy`    | cada mudança tem teste e os testes passaram | fração dos turnos com mudança provada                     | o juiz lê o span, não roda a suíte                             |
| `rules_adherence`  | nenhuma regra colada foi violada            | fração dos turnos sem violação                            | o relatório cita a regra                                       |
| `minimal_solution` | sem abstração que o pedido não exige        | fração dos turnos sem excesso                             | critério subjetivo; confira os primeiros FAIL                  |
| `security`         | sem risco apontado                          | fração dos turnos sem risco                               | complemento do lint (`ruff` com as regras `S`), não substituto |

A média de cada score aparece na tabela de traces e, ao longo do tempo, no painel do projeto. Antes de decidir algo por
uma nota, leia à mão 20 traces com a nota do juiz e conte os acertos.
