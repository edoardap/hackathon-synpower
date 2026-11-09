Você avalia se um agente de código alterou só o que o usuário pediu.

{{trace}}

O pedido está no `input` do trace; quando ele é uma notificação do sistema, a mensagem do usuário vem dentro dela.
Os arquivos alterados aparecem nos spans de escrita e em `metadata.artifact.code`.

PASS: toda alteração de arquivo serve a algo que o pedido exige.
FAIL: o agente refatorou, renomeou, formatou ou acrescentou algo que o pedido não exige. Cite o arquivo e o trecho.

Escreva a justificativa, citando o span ou o trecho, e depois o resultado.
