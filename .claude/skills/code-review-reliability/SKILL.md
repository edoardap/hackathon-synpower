---
name: code-review-reliability
description: 'Método de revisão de código com prova: aplica o checklist de um foco (qualidade, segurança ou arquitetura), confirma cada problema com arquivo:linha e uma execução concreta, classifica gravidade e escopo e fecha com veredito APROVADO ou REPROVADO num relatório padrão. Use ao revisar um PR, um diff, uma branch ou uma entrega de outro agente, e quando for despachado como qa-engineer, security-reviewer ou code-reviewer.'
---

# Code Review Reliability

Método para revisar código de forma que quem lê o relatório possa agir sem refazer a revisão. Cada problema vem com a
linha, a entrada que o dispara e o resultado errado que sai. O revisor só lê e roda comandos: a correção é de quem
recebe o relatório.

Nos caminhos abaixo, `${CLAUDE_SKILL_DIR}` é a pasta desta skill (`.claude/skills/code-review-reliability/`).

## Princípios

- **Prova ou nada.** Todo finding tem `arquivo:linha`, o trecho atual e uma execução: a entrada concreta, o que a linha
  faz com ela e o valor ou erro que sai. O melhor é um comando que falha (um teste, um `curl`). Suspeita sem execução
  vai como pergunta, não como finding.
- **Regra antes de gosto.** Finding sustenta-se em um requisito, um critério de aceite, uma regra do `AGENTS.md` ou uma
  falha observável. Preferência de estilo sem regra escrita fica de fora.
- **Gravidade pelo efeito.** A tabela de [Gravidade](#gravidade) decide pelo dano possível, e não pelo tamanho da
  correção.
- **Escopo explícito.** `IN_SCOPE` é o que a mudança revisada introduz ou deveria resolver. `OUT_OF_SCOPE` é problema
  real que já existia ou que a mudança não pede: entra no relatório para virar tarefa, sem reprovar.
- **Só lê.** O revisor não edita arquivo. Comandos servem para ler (`git diff`, `git log`, `grep`) e para provar
  (testes, lint, uma requisição ao servidor local).

## Gravidade

| Gravidade    | Quando                                                      | Exemplos                                                                                                                                                      |
| ------------ | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CRITICAL`   | Dano a dado, segurança ou contrato, ou verificação quebrada | Dado de outra organização acessível; perda de dado numa migração; segredo real versionado; injeção; teste ou lint falhando; rota que quebra cliente existente |
| `WARNING`    | Comportamento errado em caso real, sem dano grave imediato  | Validação ausente que aceita valor inválido; erro devolvendo detalhe interno; critério de aceite sem teste; migração sem rollback                             |
| `SUGGESTION` | Melhoria que não muda comportamento observável              | Nome confuso; duplicação local; teste que poderia ser mais direto                                                                                             |

O veredito é `REPROVADO` quando sobra algum finding `IN_SCOPE` com gravidade `CRITICAL` ou `WARNING`. Caso contrário,
`APROVADO`.

## Passos

1. **Alcance.** Defina o que está em revisão: o diff (`git diff <base>...HEAD`), os arquivos ou o PR. Leia também quem
   chama e quem é chamado pelo código alterado, porque o defeito costuma aparecer na fronteira.
2. **Regras e requisito.** Leia o `AGENTS.md` do repositório e o que a mudança deveria fazer: a tarefa, o design, os
   critérios de aceite ou a descrição do PR.
3. **Verificação.** Rode os testes e o lint do repositório. Falha é finding `CRITICAL` com a saída como evidência.
4. **Checklist.** Aplique o checklist do seu foco, item por item:
   `${CLAUDE_SKILL_DIR}/references/checklist-qualidade.md`, `${CLAUDE_SKILL_DIR}/references/checklist-seguranca.md` ou
   `${CLAUDE_SKILL_DIR}/references/checklist-pr.md`. Sem foco definido, aplique os três.
5. **Confirme cada finding.** Monte a execução concreta e, sempre que possível, o comando que a reproduz. Finding que
   não se confirma sai do relatório.
6. **Relatório.** Preencha o modelo de `${CLAUDE_SKILL_DIR}/assets/relatorio.md`, com o veredito.

A revisão termina quando cada item do checklist foi aplicado e cada finding do relatório tem evidência e execução.

## Armadilhas

- **Teste verde que não testa.** Teste que passa com o código quebrado não prova nada. Desconfie de asserção que só
  confere status `200`, de valor esperado calculado como o código calcula e de *mock* do próprio módulo testado.
- **Só o diff.** Uma rota nova correta pode expor uma função antiga sem filtro de organização. Siga a chamada até o
  banco.
- **Intencional parecendo defeito.** Antes de apontar, procure no design, no ADR ou no comentário vizinho se o
  comportamento foi escolhido. Se foi, e você discorda, o finding é `SUGGESTION` citando a decisão.
- **Finding duplicado.** O mesmo defeito em cinco rotas é um finding com cinco evidências, e não cinco findings.
- **Gravidade inflada.** Nome ruim não é `WARNING`. Gravidade alta sem dano demonstrado faz o leitor desconfiar do resto
  do relatório.
