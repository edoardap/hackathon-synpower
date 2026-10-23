---
name: test-generation
description: 'Escreve testes para código que já existe: teste de regressão que reproduz um defeito (falha antes da correção e passa depois), casos limite, isolamento entre organizações e cobertura de critérios de aceite, pela interface pública (rota HTTP, tela). Use ao pedir "escreve teste para", "cobre esse bug com teste", "prova que esse defeito existe", "aumenta a cobertura", ao transformar um finding de revisão em teste, e quando for despachado como qa-engineer. Para código novo escrito junto com o teste, use a tdd.'
---

# Test Generation

Guia para escrever testes que provam comportamento de código existente. O teste de regressão é o caso central: ele falha
no código com o defeito, e essa falha é registrada antes de qualquer correção.

Nos caminhos abaixo, `${CLAUDE_SKILL_DIR}` é a pasta desta skill (`.claude/skills/test-generation/`).

## Princípios

- **Vermelho registrado.** Teste de regressão roda contra o código atual e falha pelo motivo do defeito. A saída da
  falha vai para a entrega. Teste que passa no código com defeito não reproduz o defeito e é refeito.
- **Pela interface pública.** O teste chama a rota HTTP, a função pública ou a tela, como o usuário ou o cliente
  chamaria. Conferir pelo banco ou por método interno deixa o teste preso à implementação.
- **Valor esperado independente.** O esperado é um literal ou vem do requisito, e não é recalculado do jeito que o
  código calcula.
- **Um comportamento por teste**, com nome que o descreve: `test_read_opportunity_other_organization_returns_404`, e não
  `test_opportunity_2`.
- **Dados próprios.** Cada teste cria o que usa com as fábricas do repositório e não depende da ordem de execução.
- ***Mock* só na fronteira.** Serviço externo, relógio e aleatoriedade podem ser simulados; o próprio código e o banco
  de teste, não. As regras estão em `${CLAUDE_SKILL_DIR}/references/exemplos.md`, seção Mock.

## Passos

1. **Padrão de teste.** Ache o diretório, o arquivo de *fixtures* (`conftest.py`), as fábricas e o comando de teste do
   repositório. Abra dois testes vizinhos e copie a forma.
2. **Liste os comportamentos.** A partir do defeito, do finding ou dos critérios de aceite, escreva a lista de casos:
   entrada, ação e resultado esperado. Complete com o catálogo de `${CLAUDE_SKILL_DIR}/references/casos-limite.md` que
   se aplica.
3. **Escreva um teste por vez.** Escreva, rode e confira o resultado:
   - regressão: falha pelo motivo do defeito (a mensagem da falha mostra o valor errado);
   - comportamento correto já existente: passa;
   - falha por outro motivo (erro de *fixture*, *import*): o teste está errado, corrija o teste.
4. **Sem permissão para corrigir.** Quando quem escreve o teste não corrige o código (o `qa-engineer`), o teste de
   regressão entra marcado como falha esperada estrita, para a suíte seguir verde e o teste avisar quando o defeito for
   corrigido. A forma por ferramenta está em `${CLAUDE_SKILL_DIR}/references/exemplos.md`, seção Falha Esperada.
5. **Rode a suíte inteira.** Os testes novos não quebram os existentes.

A tarefa termina quando cada comportamento da lista tem um teste, cada regressão tem a falha registrada e a suíte
inteira roda.

## Armadilhas

- **Asserção só no status.** `assert response.status_code == 200` passa mesmo quando o corpo traz o dado de outra
  organização. Confira o corpo e o efeito.
- **Superusuário nos testes.** O *fixture* de token de superusuário enxerga tudo e esconde vazamento entre organizações.
  Teste de isolamento usa usuário comum de duas organizações.
- **Dado compartilhado.** Teste que depende de registro criado por outro passa sozinho e falha em outra ordem, ou o
  contrário.
- **Falha esperada frouxa.** `xfail` sem `strict=True` continua verde quando o defeito é corrigido, e o teste deixa de
  avisar.
- **Teste de tela por texto.** Teste Playwright que encontra elemento pelo texto quebra quando o texto muda. Prefira o
  nome acessível (`getByRole`, `getByLabel`), como os vizinhos.

## Formato da Entrega

```text
Comportamentos cobertos:
<caso> — <arquivo>::<teste>, um por linha

Regressões (vermelho registrado):
<arquivo>::<teste>
<trecho da saída da falha no código atual>

Suíte:
<comando e últimas linhas da saída>

Não coberto:
<caso e motivo, ou "nenhum">
```
