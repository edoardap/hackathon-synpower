# Checklist de Segurança

Foco do `security-reviewer`: ninguém lê, altera ou executa o que não deveria. Aplique cada item e registre no relatório
os que falharam. Para cada finding, mostre a requisição que explora a falha e a resposta que sai.

1. **Isolamento por organização.** Toda consulta a dado de organização filtra pela organização do usuário autenticado,
   inclusive listagem, contagem, atualização e exclusão. Recurso de outra organização responde como inexistente (`404`).
   A organização nunca vem do corpo, do caminho ou da *query string*. Vazamento é `CRITICAL`.
2. **Autorização por rota.** Rota nova exige autenticação do mesmo jeito que as vizinhas. Rota administrativa exige o
   papel certo. Rota sem checagem é `CRITICAL`.
3. **Campos de controle.** Schema de entrada não aceita `organization_id`, dono, papel ou `is_superuser`. Aceitar é
   `CRITICAL` (escalada de privilégio).
4. **Entrada validada.** Corpo, parâmetro, cabeçalho e arquivo passam por schema com tipo e limite antes de chegar à
   regra de negócio.
5. **Injeção.** Consulta SQL usa parâmetro do ORM ou *bind*, nunca texto concatenado com entrada. Comando de sistema não
   recebe entrada do usuário. HTML não renderiza entrada sem escape (`dangerouslySetInnerHTML`). Injeção é `CRITICAL`.
6. **Erro sem detalhe interno.** A resposta de erro não traz *stack trace*, SQL, caminho de arquivo nem mensagem de
   exceção interna.
7. **Segredo.** Nenhuma senha, token ou chave em código, teste, *fixture*, log ou configuração versionada. Rode a skill
   `secret-handling-review` sobre o diff.
8. **Dado pessoal em log.** Log não grava senha, token, documento ou corpo inteiro de requisição com dado pessoal.
9. **Dependência nova.** Pacote novo tem motivo na tarefa, versão fixada no arquivo de *lock* e origem conhecida.
