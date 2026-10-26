# Configuração das Avaliações

Este documento diz, para cada variável dos juízes, qual texto passar neste repositório e de onde tirá-lo. Termina com a montagem do evaluator.

## Termos

- **Variante:** uma maneira de fazer o trabalho que você quer comparar, como o revisor com outro modelo ou com outro
  conjunto de skills.
- **Item:** uma tarefa do dataset, como uma issue ou um diff para revisar. Todas as variantes recebem os mesmos itens.
- **Variável:** o `{{nome}}` do prompt do juiz. O Opik troca o nome pelo texto do campo que você mapear a ele.

## O Que Muda em Cada Variante

Uma variante muda o arquivo de definição do agente: `model`, `effort`, `tools`, `skills` ou o texto do corpo, como em
`.claude/agents/code-reviewer.md`. Para criar a variante B, copie o arquivo, altere só o que quer testar e rode os
mesmos itens. O `papel` do juiz recebe o texto do arquivo de cada variante. Todo o resto fica igual entre elas.

## Regras e Limites: o Padrão Que o Juiz Usa

`regras` e `limites` não configuram o agente. São o padrão contra o qual o juiz mede. Passe o mesmo texto a todas as
variantes, para a comparação ser justa: o que diferencia as variantes é como cada uma tenta cumprir esse padrão.

| Variável           | Texto a passar                                                                                                                                                     | Onde está                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| `regras`           | seções "Regras para todos os agentes" e "Implementação e qualidade" do `AGENTS.md` do repositório alvo               | `AGENTS.md`                                                                                       |
| `regras`, opcional | o texto de uma skill, quando você quer medir a aderência a ela                                                                                                     | `.claude/skills/tdd/SKILL.md`; a `ponytail` vem de plugin, então copie o texto da skill instalada |
| `limites`          | três voltas por fase; na terceira, `BLOQUEADO`; nenhum commit sem o usuário aprovar o diff; achado `OUT_OF_SCOPE` vai para `reviews/deferidos.md` | `.claude/agents/orchestrator.md`, seções 2 e "Commit com Aprovação Humana"                                                   |

## Entradas de Cada Domínio

| Domínio       | Variável              | De onde vem                                   | Como obter                                                                                                                     |
| ------------- | --------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Implementação | `tarefa`              | história com os critérios de aceite           | `docs/planejamento/<nome>.md` (história `HU-xx`); sem planejamento, o pedido literal                                                                              |
| Implementação | `diff`                | alteração da variante                         | `git -C <repo> diff <commit base>..<commit da variante>`                                                                       |
| Implementação | `evidencia`           | testes e lint do repositório alvo             | comandos de teste do `design.md` ou do `tasks.md` da change; neste repositório, `sh tests/run.sh`                                              |
| Revisão       | `diff`                | código com o defeito                          | `git show <sha> -- <arquivo>`                                                                                                  |
| Revisão       | `defeitos_conhecidos` | uma linha por defeito, `arquivo:linha: causa` | relatório antigo em `openspec/changes/<change>/reviews/`, ou defeito que você planta                                                                        |
| Revisão       | `revisao`             | relatório que a variante devolve              | texto do retorno do revisor                                                                                                    |
| Agente        | `papel`               | definição do agente da variante               | conteúdo de `.claude/agents/<nome>.md`                                                                                         |
| Agente        | `pedido`              | despacho recebido                             | `input.value` do span `agent:<tipo>`, nos campos de `implement-feature/SKILL.md`, seção Despacho                               |
| Agente        | `resposta`            | retorno final                                 | `input.value.message` do span `SubagentHandback` dentro do `agent:<tipo>`; em primeiro plano, `output.value` dele              |
| Agente        | `trajetoria`          | chamadas em ordem                             | spans filhos do `agent:<tipo>`: nome, `input.value` e `output.value`, resumidos                                                |
| Orquestração  | `objetivo`            | tarefa global                                 | a tarefa, como em `tarefa`                                                                                                      |
| Orquestração  | `trajetoria`          | despachos, mensagens, retornos e horários     | spans filhos do `agent:orchestrator`, com `start_time` e `end_time`                                                      |
| Orquestração  | `resultado_final`     | resumo ao usuário                             | bloco `Retorno` (Status, Ponto, Commits, Verificação, Pendências), `input.value.message` do `SubagentHandback` do orquestrador |

Conferido no Opik: o filtro `metadata.agent_type` acha o span do agente e os filhos dele. O relatório do agente em
segundo plano está no span `SubagentHandback`, e não no último `chat`.

## Montar o Evaluator

1. Crie o dataset com os campos fixos do item: `tarefa`, `regras`, `diff` da revisão, `defeitos_conhecidos`, `objetivo`,
   `limites` e `pedido`.
2. O que cada variante produz entra na avaliação dela, e não no item: `diff` e `evidencia` da implementação, `revisao`,
   `resposta`, `trajetoria` e `resultado_final`.
3. No evaluator de cada critério, mapeie cada `{{variável}}` do prompt ao campo de mesmo nome.
