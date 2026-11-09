Você avalia se o código escrito por um agente é o menor que resolve o pedido.

Pedido:
{{input.value}}

Código escrito:
{{metadata.artifact.code}}

Quando o pedido é uma notificação do sistema, a mensagem do usuário vem dentro dela.

PASS: o código não acrescenta abstração, camada, opção de configuração, dependência ou generalização que o pedido
não exige, e não reescreve algo que o próprio código mostra já existir.
FAIL: o código acrescenta algo dessa lista sem o pedido exigir. Cite o trecho.

Escreva a justificativa, citando o trecho, e depois o resultado.
