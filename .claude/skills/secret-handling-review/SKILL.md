---
name: secret-handling-review
description: 'Revisa um repositório, um diff ou um PR procurando segredo exposto (senha, token, chave de API, chave privada, URL de banco com senha) em código, configuração, teste, log, Dockerfile, CI e histórico do Git, e confere se os segredos vêm de variável de ambiente e se o .env está fora do versionamento. Use ao perguntar "tem senha no código?", ao revisar segurança de um PR, antes de tornar um repositório público e ao encontrar uma credencial. Bloquear a leitura do .env pelo agente é papel do hook, e não desta skill.'
---

# Secret Handling Review

Guia para achar segredo exposto e dizer o que fazer com cada um. O script faz a varredura mecânica; o agente classifica
cada achado, confere o que a varredura por padrão não cobre e escreve o relatório. Nenhum valor de segredo aparece
inteiro na saída.

Nos caminhos abaixo, `${CLAUDE_SKILL_DIR}` é a pasta desta skill (`.claude/skills/secret-handling-review/`).

## Princípios

- **Valor sempre mascarado.** Relatório, comentário e mensagem mostram só o começo do valor e o tamanho
  (`Kq7v…(12 caracteres)`). Copiar o segredo para o relatório espalha o vazamento.
- **Versionado é comprometido.** Segredo real que entrou num commit já foi exposto a quem tem acesso ao repositório,
  mesmo que um commit seguinte o apague. A correção é rotacionar o segredo, e não só remover a linha.
- **Real, de exemplo ou de teste.** Valor de documentação (`changethis`, `EXAMPLE`, `xxxx`) e valor falso de teste não
  são vazamento. Valor de exemplo usado como padrão em configuração de produção é.
- **O `.env` não é lido.** A revisão confere se o `.env` está no `.gitignore` e fora do versionamento, sem abrir o
  conteúdo dele. O script segue a mesma regra.

## Passos

1. **Varra.** Rode o script na raiz do repositório ou na pasta da mudança:

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/procurar_segredos.py" <caminho> [--historico]
   ```

   Ele lê os arquivos rastreados e os novos ainda não commitados, ignora o que o `.gitignore` exclui e devolve JSON com
   `achados`, `configuracao` e, com `--historico`, as linhas adicionadas nos commits. Use `--historico` antes de tornar
   o repositório público ou quando um achado sugerir que o segredo já esteve em outro lugar.

2. **Classifique cada achado.** Abra a linha e decida pela tabela:

   | Situação                                                                           | Classe       | Gravidade                                       |
   | ---------------------------------------------------------------------------------- | ------------ | ----------------------------------------------- |
   | Segredo real em código, configuração ou CI versionados                             | real         | `CRITICAL`                                      |
   | Segredo real só no histórico                                                       | real         | `CRITICAL`, com rotação                         |
   | `.env` versionado ou fora do `.gitignore`                                          | configuração | `WARNING`; `CRITICAL` se os valores forem reais |
   | Padrão inseguro em configuração de produção (`SECRET_KEY` com padrão `changethis`) | configuração | `WARNING`                                       |
   | Valor fixo em teste, sem uso fora do teste                                         | teste        | `SUGGESTION`: trocar por valor gerado           |
   | Valor de documentação ou marcador                                                  | exemplo      | fora do relatório                               |

3. **Confira o que o script não vê.** Leia os pontos de `${CLAUDE_SKILL_DIR}/references/onde-procurar.md`: log que grava
   token ou cabeçalho, segredo em mensagem de erro, padrão inseguro lido por `getenv`, `Dockerfile` e CI.

4. **Relate.** Escreva o relatório no formato da `code-review-reliability`. Cada finding traz o arquivo, a linha, o
   valor mascarado e a correção de `${CLAUDE_SKILL_DIR}/references/correcao.md`.

A revisão termina quando cada achado do JSON foi classificado, os pontos de `onde-procurar.md` foram conferidos e o
relatório não contém nenhum valor inteiro.

## Armadilhas

- **Remover não basta.** O commit que apaga a senha deixa a senha no histórico. Sem rotação, o finding continua
  `CRITICAL`.
- **Padrão de `getenv`.** `os.getenv("SECRET_KEY", "changethis")` passa pela varredura, porque o valor é um marcador. Em
  produção sem a variável, o sistema roda com a chave pública da documentação.
- **Segredo em log.** `logger.info("token %s", token)` não tem segredo no código, mas grava o segredo em cada execução.
- **Teste que vira credencial.** Senha fixa de teste reaproveitada no ambiente de homologação deixa de ser valor de
  teste.
- **Leitura do `.env`.** Ler, imprimir ou procurar dentro do `.env` para confirmar um valor expõe o segredo na conversa.
  Pergunte ao usuário se o valor é real.
