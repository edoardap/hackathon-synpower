Você avalia o código que um agente escreveu para atender a um pedido.

Pedido do usuário:
{{pedido}}

Código escrito no turno:
{{codigo}}

Critérios:

1. O código atende ao pedido: faz o que foi pedido, sem deixar parte de fora e sem fazer o que não foi pedido.
2. O código evita abstração desnecessária: sem camada, opção ou generalização que o pedido não exige, e com o que a
   biblioteca padrão e o próprio código já oferecem.

Nota de 0 a 1:

- 1,0: atende ao pedido por completo e é o mínimo necessário.
- 0,5: atende em parte, ou atende com excesso claro de abstração.
- 0,0: não atende ao pedido.

Se o código termina com um marcador de truncamento, julgue só o que aparece e não puna o que falta por causa do corte.

Dê a nota e uma justificativa de uma ou duas frases que cite o trecho que a motivou.
