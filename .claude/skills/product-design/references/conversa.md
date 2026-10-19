# Design de conversa: roteiros e comportamento de agentes

Serve para dois casos: (a) a conversa guiada que leva o usuário a configurar algo (ex.: criar um agente) e (b) o comportamento de um agente de IA que conversa com o público final.

## Roteiro: conversa guiada de configuração

1. **Defina o objetivo e a saída.** O que a conversa precisa produzir (ex.: um contrato com camadas definidas) e quais campos são obrigatórios.
2. **Uma pergunta por vez.** Em linguagem do usuário, com exemplo de resposta. Evite perguntas abertas demais quando uma escolha guiada resolve.
3. **Ordem.** Comece pelo mais fácil e pelo que dá contexto para as próximas perguntas. Agrupe por camada e mostre o progresso.
4. **Para cada pergunta, registre:** texto, por que pergunta, campo que preenche, exemplo, validação e o que fazer se a resposta for vaga ou vazia.
5. **Revisão final.** Mostre um resumo do que foi capturado e permita corrigir antes de concluir.
6. **Casos limite:** usuário não sabe responder, sai no meio e volta, muda uma resposta anterior, responde fora do assunto.

## Roteiro: comportamento do agente

Siga as camadas que o projeto definiu (ex.: identidade, contexto, modo de resposta, comportamento). Para cada uma, especifique o que o usuário configura e como isso vira instrução para o agente.

- **Identidade:** nome, papel, tom. Mantenha consistência ao longo da conversa.
- **Contexto:** o que o agente sabe sobre o negócio. Ele só afirma o que está no contexto.
- **Modo de resposta:** tamanho, formalidade, formato, idioma.
- **Comportamento:** como trata dúvidas, objeções e pedidos fora do escopo.

### Casos que todo agente precisa de um roteiro para

- **Não sabe a resposta:** admite e oferece caminho (encaminhar a um humano, pedir mais detalhes). Não inventa.
- **Fora do escopo:** recusa com educação e volta ao assunto.
- **Pedido sensível ou inadequado:** não atende, não ofende, e indica a saída apropriada.
- **Usuário irritado ou confuso:** reconhece, simplifica e oferece atendimento humano quando houver.
- **Abertura e encerramento:** saudação inicial e despedida coerentes com a identidade.
- **Revelar que é uma IA:** o agente não finge ser pessoa quando perguntado diretamente.

## Tom e texto

- Frases curtas, voz ativa, sem jargão. Um tom por agente, coerente com a identidade.
- Exemplos de fala são `a validar`. Quem define o tom final é o dono do negócio.

## Como verificar

Proponha um conjunto de conversas de teste (3 a 5 por camada e por caso limite), com a fala do usuário e o comportamento esperado. Sem critério de aprovação definido pelo usuário, marque como `a validar`. Não invente métricas de qualidade.
