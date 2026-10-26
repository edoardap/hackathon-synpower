# Estilo das páginas de `docs/`

Leia antes de escrever `docs/architecture.md`, `development.md`, `testing.md`, `configuration.md`, `operations.md` ou qualquer página complementar. O README tem formato próprio (passo 5 do SKILL.md) e não segue este guia.

## Princípio

Escreva como um capítulo de um bom livro técnico: alguém que não conhece o projeto lê de cima para baixo e sai entendendo como ele funciona e por que está assim. A pergunta para cada seção é "o que esse leitor precisa entender primeiro?", e não "que fatos eu levantei?". Os fatos levantados na investigação sustentam o texto; eles não são o texto.

## Prosa, tabela e lista

- Explique em parágrafos curtos e encadeados. Use conectivos que mostrem relação ("por isso", "em seguida", "para evitar que"), porque é aí que mora o entendimento que uma tabela não entrega.
- Tabela é para dado de consulta com colunas homogêneas: variáveis de ambiente, comandos e seus efeitos, portas. Limite de uma ou duas por página, sempre precedidas de uma frase que diz o que o leitor vai ver.
- Não descreva componentes, módulos, camadas ou etapas de fluxo em tabela. Conte o que cada um faz e como se relaciona com os outros.
- Lista só para passos sequenciais curtos (instalação) ou enumerações realmente soltas. Evite listas aninhadas.
- Não faça uma seção que seja só uma lista de arquivos. Caminhos aparecem no meio da explicação, quando ajudam a localizar o código, e não em coluna própria.
- Títulos descrevem o assunto ("Como uma requisição é atendida"), não categorias vazias ("Componentes", "Visão geral" repetido).

## Diagramas Mermaid

- `sequenceDiagram` para qualquer interação entre três ou mais participantes ao longo do tempo: ciclo de requisição, login, processamento assíncrono, pipeline de CI, integração com serviço externo.
- `flowchart` para a visão geral de componentes e dependências, e para decisões ramificadas.
- `erDiagram` ou `classDiagram` só se o modelo de dados for central e estiver claro no código.
- Todo diagrama vem com um parágrafo antes ou depois que o conta em palavras, e usa os nomes reais que aparecem no código.
- Desenhe só o que foi observado. Etapa que não foi confirmada fica fora do diagrama e é mencionada no texto como lacuna.
- Mantenha cada diagrama pequeno (até uns oito participantes ou nós). Se crescer, divida em dois.
- Valide a sintaxe se houver ferramenta disponível (por exemplo `mmdc`); senão, registre a verificação como `skipped` com o motivo.

## Esqueleto por página

Adapte ao projeto; omita o que não tiver evidência.

**architecture.md**: comece com um ou dois parágrafos sobre o que o sistema faz e como está dividido, seguidos de um `flowchart` da visão geral. Depois, uma seção em prosa por parte relevante do sistema, explicando responsabilidade e relação com as vizinhas. Feche com o fluxo principal em `sequenceDiagram` e a explicação dele, e com um parágrafo sobre decisões de projeto visíveis no código e o que depende de confirmação humana.

**development.md**: narre o caminho de um checkout limpo até a aplicação rodando, explicando o motivo de cada etapa e o que o desenvolvedor deve ver quando funciona. Acrescente como o código está organizado para quem vai contribuir, as convenções observadas e problemas comuns que tenham evidência.

**testing.md**: explique a estratégia de testes que o repositório de fato adota (o que é testado em que nível, como os testes dependem de banco ou serviços, o que o CI roda), com os comandos no meio do texto ou em um bloco de código. Uma tabela de comandos é aceitável aqui.

**configuration.md**: explique como a configuração é carregada e em que ordem de precedência, depois as variáveis em uma tabela (nome, finalidade, obrigatória, exemplo seguro). Nunca valores reais.

**operations.md**: só com evidência de deploy, containers, logs ou monitoramento. Narre como o sistema sobe e é observado; pipeline de CI/CD vai em `sequenceDiagram` ou `flowchart`.

## Checagem antes de entregar

- Alguma página abre direto com tabela ou lista? Reescreva a abertura em prosa.
- Há mais de duas tabelas em uma página? Converta as de descrição em texto.
- Algum fluxo com vários participantes está sem diagrama?
- Cada diagrama tem texto explicando e só mostra o que foi observado?
- Toda afirmação relevante tem fonte no registro de evidências?
