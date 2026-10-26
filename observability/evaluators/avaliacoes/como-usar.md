# Avaliações no Opik: Como Usar

Esta página explica como usar os juízes de `implementacao.md`, `revisao.md`, `agente.md` e `orquestracao.md` para
comparar maneiras diferentes de implementar, revisar código, configurar um agente e orquestrar vários agentes. Os
critérios não dependem das skills e dos agentes de hoje: o texto que cada variante devia seguir entra pelas variáveis,
como `regras` e `papel`.

## Como Funcionam

- **Um critério por juiz:** o resultado é Pass ou Fail, e a justificativa vem antes do veredito, como pede
  `.agents/skills/opik-evaluate/references/write-judge-prompt.md`.
- **Variante:** o que você quer comparar, como uma skill, um prompt, um modelo ou um desenho de orquestração. Todas as
  variantes rodam a mesma lista de tarefas.
- **Os mesmos juízes:** cada variante é avaliada pelos mesmos critérios, e a diferença de Pass por critério mostra onde
  uma variante é melhor.

| Arquivo            | Avalia                                             | Juízes |
| ------------------ | -------------------------------------------------- | ------ |
| `implementacao.md` | um diff contra a tarefa e as regras                | 6      |
| `revisao.md`       | um relatório de revisão contra defeitos conhecidos | 6      |
| `agente.md`        | um agente no papel que recebeu                     | 4      |
| `orquestracao.md`  | vários agentes conduzidos por um orquestrador      | 5      |

## Criar o Juiz no Opik

1. Em *AI Providers*, na configuração do workspace, cadastre a chave de um provedor com acesso ao modelo do juiz, o
   mesmo caminho da regra `code_quality`.
2. Crie um evaluator do tipo *LLM-as-judge* por critério e cole o bloco `text` como prompt.
3. Mapeie cada `{{variável}}` ao campo do item do dataset ou do trace e defina a saída: o nome do critério, tipo
   `BOOLEAN`, em que `true` é Pass.

Para cadastrar as seis regras de implementação, com o prompt de cada uma e o mapa das variáveis, veja
[Configurar as Regras no Opik](../configurar_regras_no_opik.md). O modo *Agent as a Judge* lê o trace inteiro e dispensa
o mapeamento de variáveis. O que o mercado faz está em [Padrão de Mercado](./padrao-de-mercado.md).

## Comparar Variantes

1. Monte um dataset com as tarefas. Os campos do item e os valores a passar estão em [Configuração](./configuracao.md).
2. Rode cada variante sobre a mesma lista e guarde, em cada item, o que ela produziu (`diff`, `revisao`, `resposta` ou
   `trajetoria`).
3. Rode os juízes sobre cada variante, um experimento por variante, e compare os experimentos no Opik (skill
   `opik-compare`).

Como alternativa, o texto do PASS de cada critério vira uma assertion de uma *test suite* (`opik-evaluate/SKILL.md`,
passo 3).

## Métricas Por Código

Algumas medidas dispensam juiz e saem de contas sobre o trace ou sobre o resultado.

| Domínio       | Medidas                                                                 | Existe hoje no Opik                                  |
| ------------- | ----------------------------------------------------------------------- | ---------------------------------------------------- |
| Implementação | testes passam, achados de lint, linhas do diff, arquivos fora do escopo | custo e tokens (`score.*`)                           |
| Revisão       | achados por severidade, recall e precisão contra os defeitos conhecidos | nenhuma                                              |
| Agente        | ferramentas com falha, chamadas idênticas repetidas, duração, custo     | custo, tokens e falha de ferramenta                  |
| Orquestração  | despachos, voltas por unidade, spans sobrepostos, custo por agente      | `agent_type` nos spans, para filtrar e somar o custo |

## Antes de Confiar

Nenhum juiz daqui foi validado. Cada um precisa de 2 a 4 exemplos rotulados no prompt (um Pass, um Fail e um limítrofe)
e de uma medida contra rótulos humanos, com TPR e TNR, antes de a nota decidir algo:
`.agents/skills/opik-evaluate/references/validate-evaluator.md`.
