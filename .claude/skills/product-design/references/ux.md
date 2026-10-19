# UI/UX: fluxos, telas e estados

## Roteiro

1. **Mapeie as tarefas do usuário** a partir das histórias, na ordem em que ele as faz.
2. **Fluxo ponta a ponta.** Descreva em passos numerados, do ponto de entrada ao objetivo. Marque os passos em que o usuário pode travar (decisões, passos técnicos) e como o design os ajuda.
3. **Inventário de telas.** Liste cada tela com: objetivo, origem (HU), conteúdo, ações principais e secundárias, navegação de entrada e saída.
4. **Estados de cada tela.** Vazio (primeira vez, sem dados), carregando, sucesso, erro (com mensagem e saída) e, quando houver, sem permissão ou sem conexão.
5. **Formulários.** Campos, rótulo, texto de ajuda, validação, mensagem de erro, obrigatório ou opcional. Valide cedo e perto do campo.
6. **Textos da interface.** Proponha rótulos e mensagens em linguagem simples, marcando-os como `a validar`.

## Princípios para usuário leigo

- Uma tarefa principal por tela, com uma ação primária clara.
- Progressão guiada (passo a passo) para tarefas longas ou com termos técnicos, mostrando em que passo o usuário está.
- Termos do domínio dele, não jargão técnico. Se o termo técnico for inevitável (ex.: "token"), explique no ponto de uso, com exemplo ou passo a passo.
- Confirmação antes de ações destrutivas ou que publicam algo ao público, e como desfazer.
- Mostre o resultado das ações: o usuário precisa saber que deu certo.
- Credenciais e segredos aparecem mascarados e não são reexibidos depois de salvos.

## Heurísticas para revisar

- Visibilidade do estado: o usuário sempre sabe onde está e o que está acontecendo.
- Prevenção de erro melhor que mensagem de erro.
- Reconhecer em vez de lembrar: opções visíveis, exemplos nos campos.
- Consistência de nomes, posições e comportamentos.

## Acessibilidade mínima

- Contraste suficiente entre texto e fundo (referência WCAG AA).
- Tudo que o mouse faz, o teclado também, com foco visível.
- Rótulos associados aos campos e texto alternativo em imagens com significado.
- Estado nunca indicado só por cor.
- Interface responsiva: defina o comportamento em tela pequena, e marque como pendência se o público usa mais celular ou desktop.

## Wireframe em texto

Quando ajudar, descreva o layout em blocos de texto (cabeçalho, conteúdo, rodapé, ações) em vez de desenhar. Evite ASCII complexo.
