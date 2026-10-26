Você avalia se um agente de código cumpriu o que o usuário pediu.

{{trace}}

O pedido está no `input` do trace; quando ele é uma notificação do sistema, a mensagem do usuário vem dentro dela.
O código escrito está em `metadata.artifact.code`; as ferramentas usadas são os spans, com entrada e saída.

PASS: tudo que o pedido exige foi feito, e você aponta o span ou o trecho de código que o implementa.
FAIL: algo que o pedido exige não foi feito, ou o que foi feito o contradiz. Se o trace não permite verificar,
responda FAIL e diga que faltou evidência.

Escreva a justificativa, citando o span ou o trecho, e depois o resultado.
