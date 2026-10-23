---
name: backend-patterns
description: 'Padrões para escrever e alterar backend Python com FastAPI: onde fica cada código (rota, modelo, schema, CRUD, serviço), validação na fronteira, formato de erro, configuração e isolamento por organização (multi-tenant). Use ao implementar endpoint, rota, modelo, CRUD ou regra de negócio num backend FastAPI, ao decidir "onde esse código vai", e ao tocar qualquer dado que pertence a uma organização ou tenant. O desenho do contrato da API é da api-design; a mudança de schema do banco é da database-migration-plan.'
---

# Backend Patterns

Guia de implementação para backend FastAPI. O código novo segue o padrão que o repositório já usa, e duas regras valem
em qualquer repositório: a entrada é validada na fronteira e todo dado de uma organização só é lido ou alterado por quem
pertence a ela.

Nos caminhos abaixo, `${CLAUDE_SKILL_DIR}` é a pasta desta skill (`.claude/skills/backend-patterns/`).

## Princípios

- **O vizinho manda.** Antes de criar um arquivo, abra dois arquivos do mesmo tipo (duas rotas, dois modelos) e copie a
  estrutura, os nomes e a forma de teste deles. Uma camada que o repositório não tem só entra quando o usuário pedir.
- **Fronteira validada.** Todo dado que chega de fora (corpo, parâmetro de caminho, *query string*, cabeçalho) passa por
  um schema com tipo e limite: `min_length`, `max_length`, `ge`, `le`, `EmailStr`, `Literal`. A resposta sai por um
  schema público (`response_model`), que lista só os campos que o cliente pode ver.
- **Organização vem do usuário.** O `organization_id` sai do usuário autenticado, nunca do corpo, do caminho ou da
  *query string*. Toda consulta a tabela de organização filtra por ele. As regras completas e o teste obrigatório estão
  em `${CLAUDE_SKILL_DIR}/references/multi-tenant.md`.
- **Erro curto e previsível.** Use o mesmo mecanismo de erro das rotas vizinhas (`HTTPException` com `status_code` e um
  `detail` curto). O cliente recebe o status e a frase; o *stack trace* e a mensagem da exceção interna ficam no log.
- **Configuração centralizada.** Segredo, URL e limite vêm da classe de configuração do projeto (`settings`). O código
  de negócio lê `settings`, e não `os.getenv`.
- **Construa de baixo para cima.** Schema e modelo, migração, acesso ao banco, regra de negócio, rota, registro no
  roteador e testes, nessa ordem. Assim cada camada já encontra pronta a camada de que depende.

## Passos

1. **Leia as regras.** Abra o `AGENTS.md` do repositório e, se existirem, o `CLAUDE.md` e o guia de contribuição. Anote
   os comandos de teste e de lint.
2. **Leia os vizinhos.** Identifique o padrão de organização do backend com a tabela
   [Onde Fica Cada Código](#onde-fica-cada-c%C3%B3digo) e abra dois arquivos de cada tipo que você vai criar.
3. **Decida o lugar de cada peça.** Use a tabela do padrão que o repositório segue. Se o repositório separa serviço e
   repositório, siga `${CLAUDE_SKILL_DIR}/references/camadas.md`.
4. **Mude o banco, se precisar.** Tabela nova, coluna nova ou mudança de tipo seguem a skill `database-migration-plan`.
5. **Implemente com teste.** Escreva o teste da rota antes do código, como manda a `tdd`. Toda rota que toca dado de
   organização ganha o teste de isolamento de `${CLAUDE_SKILL_DIR}/references/multi-tenant.md`.
6. **Verifique.** Rode os testes e o lint do repositório. A tarefa termina quando os dois passam e cada rota nova tem
   teste de sucesso, de entrada inválida, de recurso inexistente e de isolamento.

## Onde Fica Cada Código

Os repositórios FastAPI costumam seguir um destes dois padrões. Descubra qual pelos diretórios existentes.

**Padrão plano** (o do `full-stack-fastapi-template`): poucos arquivos, rota acessa o banco direto.

| Peça                          | Lugar                                        | Observação                                                                    |
| ----------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------- |
| Tabela e schemas da entidade  | `app/models.py`                              | Família `XBase`, `XCreate`, `XUpdate`, `X(table=True)`, `XPublic`, `XsPublic` |
| Função de banco reaproveitada | `app/crud.py`                                | Usada por mais de uma rota ou pelos testes                                    |
| Rota                          | `app/api/routes/<entidade_plural>.py`        | `APIRouter(prefix=..., tags=[...])`, registrada em `app/api/main.py`          |
| Dependência injetável         | `app/api/deps.py`                            | `SessionDep`, `CurrentUser` e afins, como `Annotated[..., Depends(...)]`      |
| Configuração                  | `app/core/config.py`                         | Campo novo em `Settings`                                                      |
| Teste de rota                 | `tests/api/routes/test_<entidade_plural>.py` | Usa `client` e os *headers* de token do `conftest.py`                         |
| Fábrica de dado de teste      | `tests/utils/<entidade>.py`                  | `create_random_<entidade>(db)`                                                |

**Padrão em camadas**: diretórios `routers/`, `services/`, `repository/`, `schemas/` e `models/` separados. A rota só
traduz HTTP, o serviço tem a regra de negócio e o repositório tem as consultas. O mapa completo e os anti-padrões estão
em `${CLAUDE_SKILL_DIR}/references/camadas.md`.

Exemplos reais do padrão plano, com arquivo e linha, estão em `${CLAUDE_SKILL_DIR}/references/exemplo-crm.md`.

## Armadilhas

- **Leitura por id que vaza.** `session.get(X, id)` seguido de comparação do dono devolve o registro de outra
  organização quando a comparação é esquecida, e a resposta `403` confirma que o id existe. Filtre na consulta e
  responda `404`.
- **Schema de entrada com campo de controle.** `organization_id`, `owner_id` ou `is_superuser` em `XCreate` ou `XUpdate`
  deixa o cliente escolher o próprio dono ou privilégio. Esses campos são preenchidos pela rota.
- **Limpeza dos testes.** No template, a fixture `db` do `tests/conftest.py` apaga as tabelas ao fim da sessão de
  testes. Tabela nova com chave estrangeira entra nessa limpeza antes da tabela referenciada, ou a exclusão falha.
- **Script de teste quebrado.** No template, `scripts/test.sh` falha porque a imagem do backend não copia `tests/`. Use
  o caminho do CI em `${CLAUDE_SKILL_DIR}/references/exemplo-crm.md`, seção Verificação.
- **Skills das bibliotecas.** O template traz as skills `fastapi` e `sqlmodel`, mantidas pelos autores das bibliotecas.
  Para a forma idiomática da biblioteca, siga-as; para onde o código fica e para o isolamento por organização, siga
  esta.

## Formato da Entrega

Devolva ao fim da tarefa:

```text
Arquivos alterados:
<caminho a partir da raiz do repositório>, um por linha

Testes novos:
<arquivo>::<nome do teste> — <o que prova>, um por linha

Verificação:
<comando>
<últimas linhas da saída, com o total de testes e o resultado do lint>

Pendências:
<o que ficou de fora e por quê, ou "nenhuma">
```
