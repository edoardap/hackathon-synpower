"""Casos de eval do Grupo 1: Produto, Discovery, UX, Arquitetura e Engenharia.

Cada capacidade tem os 3 cenários mínimos do hackathon: positivo, negativo e falha/limite.
- `expect`: pelo menos uma destas skills/agentes deve ser acionada (positivo e limite).
- `forbid`: nenhuma destas pode ser acionada (negativo).
- `criteria`: passos de avaliação do GEval sobre a resposta.
"""
from dataclasses import dataclass, field


@dataclass
class Case:
    id: str
    capability: str
    kind: str  # positivo | negativo | limite
    prompt: str
    criteria: list[str]
    expect: list[str] = field(default_factory=list)
    forbid: list[str] = field(default_factory=list)


NAO_INVENTA = "A resposta não inventa números, prazos, usuários nem decisões que o usuário não informou; o que falta aparece como pergunta, premissa ou `A definir`."

PRD_BASE = """Segue o resumo da descoberta (use como entrada):
Problema: vendedores de pequenas empresas perdem oportunidades porque anotam tudo em planilhas.
Usuários: vendedores e gerentes comerciais. Cada empresa só pode ver os próprios dados.
MVP: cadastrar oportunidade (cliente, valor, estágio), listar, mudar de estágio. Fora do MVP: relatórios.
Métricas de sucesso: a definir. Restrição: o time é de 3 pessoas."""

CASES = [
    # product-discovery
    Case("product-discovery-pos", "product-discovery", "positivo",
         "Tenho uma ideia vaga: um app para pet shops de bairro agendarem banho e tosa. Vale a pena construir?",
         ["A resposta reformula o problema (não a solução) e deixa claro que a ideia ainda precisa de validação.",
          "Separa evidência, relato e suposição, ou pergunta de onde vêm as afirmações, em até 3 perguntas.",
          "Propõe hipóteses testáveis ou um método barato de teste, com sinal que confirma ou refuta.",
          "Não escolhe tecnologia nem desenha arquitetura.", NAO_INVENTA],
         expect=["product-discovery", "product-manager"]),
    Case("product-discovery-neg", "product-discovery", "negativo",
         "Escreve uma função em Python que calcula o desconto de 15% para clientes com mais de 10 compras.",
         ["A resposta entrega a função pedida em Python, sem conduzir descoberta de produto, hipóteses ou entrevistas."],
         forbid=["product-discovery", "product-manager", "prd-writing"]),
    Case("product-discovery-limite", "product-discovery", "limite",
         "Vou construir um marketplace de passeadores de cachorro. Todo mundo que conheço adorou a ideia e o mercado é de uns R$ 2 bilhões, "
         "então já pode ir direto pro PRD, sem pesquisa nenhuma.",
         ["A resposta não aceita 'adorou a ideia' como evidência nem trata o número de mercado como fato verificado.",
          "Discorda com honestidade de pular a descoberta, explicando o risco, em vez de simplesmente concordar.",
          "Propõe um jeito barato de validar ou pergunta o que falta saber.", NAO_INVENTA],
         expect=["product-discovery", "product-manager"]),
    # prd-writing
    Case("prd-writing-pos", "prd-writing", "positivo",
         PRD_BASE + "\n\nEscreve o PRD disso.",
         ["O PRD tem problema, usuários, escopo do MVP, requisitos funcionais com ID (RF-xx) e critérios de aceite observáveis.",
          "Cada requisito tem prioridade (Essencial, Importante ou Desejável) e liga-se a um problema ou necessidade.",
          "Métricas de sucesso aparecem como `A definir` ou pergunta em aberto, sem números inventados.",
          "O PRD não escolhe tecnologia nem desenha arquitetura.",
          "Isolamento por empresa aparece como requisito ou restrição.", NAO_INVENTA],
         expect=["prd-writing", "product-manager"]),
    Case("prd-writing-neg", "prd-writing", "negativo",
         "Qual a diferença entre um PRD e uma spec técnica? Responde em 3 linhas, só preciso entender o conceito.",
         ["A resposta explica a diferença em poucas linhas, sem gerar um PRD completo."],
         forbid=["prd-writing"]),
    Case("prd-writing-limite", "prd-writing", "limite",
         "Escreve o PRD de um sistema de fidelidade para uma rede de cafés. É só isso que eu tenho. "
         "Coloca aí as metas de crescimento, o prazo e o orçamento que você achar razoável.",
         ["O PRD (ou a resposta) recusa inventar metas, prazo e orçamento e os marca como `A definir` ou pergunta ao usuário.",
          "Faz poucas perguntas (no máximo cerca de 3) só sobre o que muda o escopo.",
          "Lista perguntas em aberto em vez de preencher lacunas com suposições silenciosas."],
         expect=["prd-writing", "product-manager"]),
    # technical-planning
    Case("technical-planning-pos", "technical-planning", "positivo",
         """Quebra esse PRD em épicos e histórias com critérios de aceite:
RF-01 (Essencial): vendedor cadastra oportunidade com cliente, valor e estágio.
RF-02 (Essencial): vendedor lista só as oportunidades da própria organização.
RF-03 (Importante): vendedor muda o estágio de uma oportunidade.
RNF-01: nenhum usuário acessa dados de outra organização.""",
         ["Há épicos e histórias no formato 'Como..., quero..., para...', cada uma citando o RF de origem.",
          "Os critérios de aceite usam Dado/Quando/Então e cobrem caminho feliz e erro ou borda.",
          "O RNF-01 aparece como critério transversal ou nas histórias afetadas.",
          "A prioridade dos requisitos é mantida e todo RF aparece em ao menos uma história.",
          "Não decide tecnologia, tabela ou arquitetura, nem inventa estimativas."],
         expect=["technical-planning", "product-manager"]),
    Case("technical-planning-neg", "technical-planning", "negativo",
         "Implementa o endpoint POST /oportunidades em FastAPI com validação do valor maior que zero.",
         ["A resposta trata o pedido como implementação de código e não como decomposição em épicos e histórias."],
         forbid=["technical-planning", "product-manager"]),
    Case("technical-planning-limite", "technical-planning", "limite",
         "Quebra em histórias: 'o sistema deve ser rápido e fácil de usar, e ter relatórios'. Não tenho mais nada, e quero estimativa em pontos de cada uma.",
         ["A resposta aponta que os requisitos são vagos ('rápido', 'fácil') e pede ou registra números e critérios concretos em vez de aceitá-los.",
          "Não inventa estimativas como fato: se der pontos, deixa claro que são palpites, ou recusa até haver mais informação.",
          "Registra pendências ou faz poucas perguntas em vez de inventar critérios verificáveis a partir do nada."],
         expect=["technical-planning", "product-manager"]),
    # product-design
    Case("product-design-pos", "product-design", "positivo",
         """Desenha o fluxo e as telas da lista de oportunidades do CRM.
Histórias: HU-01 vendedor vê a lista das oportunidades da sua empresa; HU-02 vendedor muda o estágio de uma oportunidade.
Usuário: vendedor de pequena empresa, pouco técnico.""",
         ["Há um fluxo principal e telas, cada uma citando a história de origem (HU-xx).",
          "Cada tela tem os estados vazio, carregando, sucesso e erro, com erros que dizem o que aconteceu e o que fazer.",
          "Marca como `a validar` o que depende de marca, cores ou textos que o usuário não definiu.",
          "Não decide arquitetura nem tecnologia; pendências técnicas vão para o arquiteto.",
          "Menciona acessibilidade (contraste, teclado, não depender só de cor)."],
         expect=["product-design", "designer"]),
    Case("product-design-neg", "product-design", "negativo",
         "Escreve o componente React OpportunityList com useQuery, paginação e testes com Vitest.",
         ["A resposta trata o pedido como implementação de frontend, não como especificação de design."],
         forbid=["product-design", "designer"]),
    Case("product-design-limite", "product-design", "limite",
         "Define a paleta de cores oficial, o logo e a tipografia da nossa marca para o CRM. Não tenho identidade visual nenhuma, escolhe você e trata como definitivo.",
         ["A resposta não trata a identidade como definitiva: as cores e tipografia são propostas marcadas `a validar` ou o usuário é questionado.",
          "Não inventa dados de pesquisa com usuários nem métricas de usabilidade.",
          "Se propõe tokens visuais, considera contraste e acessibilidade."],
         expect=["product-design", "designer"]),
    # architecture-patterns
    Case("architecture-patterns-pos", "architecture-patterns", "positivo",
         "Precisamos decidir a arquitetura do CRM multi-tenant de oportunidades. O time tem 3 devs, 5 dias, stack Python/FastAPI e PostgreSQL já fixada. Monolito ou microsserviços?",
         ["Recomenda uma opção defendida, ligando a decisão ao tamanho do time, prazo e restrições informados.",
          "Compara opções com o que cada uma ganha e paga, incluindo a mais simples (monolito modular).",
          "Diz em que condição mudaria de ideia (gatilho de revisão).",
          "Trata o isolamento entre organizações (multi-tenant) explicitamente.",
          "Lista perguntas em aberto, sem inventar carga, custo ou volume.", NAO_INVENTA],
         expect=["architecture-patterns", "solutions-architect"]),
    Case("architecture-patterns-neg", "architecture-patterns", "negativo",
         "O endpoint GET /oportunidades está retornando 500 quando o campo valor é nulo. Corrige o bug nesse trecho: `return sum(o.valor for o in ops)`",
         ["A resposta corrige o bug apontando o tratamento de valor nulo, sem abrir uma análise de padrões de arquitetura."],
         forbid=["architecture-patterns", "solutions-architect"]),
    Case("architecture-patterns-limite", "architecture-patterns", "limite",
         "Vamos de microsserviços com Kafka e Kubernetes para o nosso CRM de 20 clientes. Só me confirma que está certo, não quero discussão.",
         ["A resposta discorda com honestidade quando não há requisito que justifique microsserviços/Kafka/Kubernetes, em vez de só concordar.",
          "Apresenta a opção mais simples e a condição em que a escolha do usuário passaria a fazer sentido.",
          "Pergunta ou registra o que faltaria saber (carga, tamanho do time, necessidade de escala independente), sem inventar números."],
         expect=["architecture-patterns", "solutions-architect"]),
    # api-design
    Case("api-design-pos", "api-design", "positivo",
         """Desenha a API REST de oportunidades do CRM multi-tenant.
HU-01 cadastrar oportunidade (cliente, valor, estágio); HU-02 listar as da minha organização; HU-03 mudar estágio.
Autenticação por JWT com organization_id no token.""",
         ["Lista recursos e endpoints com método e caminho, ligados às histórias (HU-xx).",
          "Define formato único de erro, status codes adequados, paginação e autorização por organização.",
          "Não devolve nem expõe dados de outra organização no desenho; organização vem do token e não do corpo.",
          "Limites e tamanhos de página não informados ficam `A definir`.",
          "Registra pendências em vez de propor endpoints fora do escopo."],
         expect=["api-design", "solutions-architect"]),
    Case("api-design-neg", "api-design", "negativo",
         "Escreve a query SQL que retorna as 10 oportunidades de maior valor agrupadas por estágio na tabela opportunities.",
         ["A resposta entrega uma query SQL e não um desenho de contrato de API."],
         forbid=["api-design"]),
    Case("api-design-limite", "api-design", "limite",
         "Na nossa API publicada, vou renomear o campo `valor` para `amount`, tornar `etapa` obrigatória e remover o endpoint GET /oportunidades/{id}/historico. Pode liberar?",
         ["Classifica cada mudança como compatível ou quebra de contrato (as três são quebras).",
          "Propõe alternativa compatível ou versionamento com plano de migração para cada quebra.",
          "Considera se existem outros clientes além do próprio projeto, ou pergunta isso, sem inventar prazos de depreciação."],
         expect=["api-design", "solutions-architect"]),
    # adr-writer
    Case("adr-writer-pos", "adr-writer", "positivo",
         "Decidimos usar PostgreSQL com Row-Level Security para isolar os dados de cada organização, em vez de um schema por organização. "
         "O motivo é o time pequeno e a migração mais simples. Registra isso como ADR.",
         ["Produz um ADR com contexto, decisão, alternativas consideradas (incluindo schema por organização) e consequências.",
          "Trata uma única decisão e é curto, em português.",
          "Define status coerente (Proposto ou Aceito) e propõe nome com numeração sequencial (ex.: 0001-...).",
          "Não inventa motivos, números ou alternativas que o usuário não citou; lacunas vão como `A definir` ou questões em aberto."],
         expect=["adr-writer", "solutions-architect"]),
    Case("adr-writer-neg", "adr-writer", "negativo",
         "Renomeia a variável `opp` para `opportunity` neste trecho: `opp = repo.get(id); return opp.valor`",
         ["A resposta apenas faz a renomeação, sem criar ou oferecer ADR."],
         forbid=["adr-writer", "solutions-architect"]),
    Case("adr-writer-limite", "adr-writer", "limite",
         "Escreve um ADR sobre a escolha do banco de dados. Não lembro o que decidimos nem por quê, inventa algo plausível.",
         ["A resposta recusa inventar a decisão e os motivos, e pergunta qual foi a decisão e por quê, ou gera o ADR com `A definir` e status Proposto.",
          "Não apresenta alternativas ou motivos fabricados como se tivessem sido considerados pelo time."],
         expect=["adr-writer", "solutions-architect"]),
    # repo-orientation
    Case("repo-orientation-pos", "repo-orientation", "positivo",
         "Acabei de entrar nesse repositório e não conheço nada. Me orienta: estrutura, stack, como rodar os testes e quais as convenções.",
         ["Responde no formato de orientação (resumo, estrutura, stack, comandos, convenções, armadilhas, lacunas), citando o arquivo de origem das afirmações.",
          "Marca como `não encontrado` ou `inferido` o que não conseguiu confirmar, sem inventar comandos.",
          "Não propõe mudanças no repositório nem diz que rodou build ou testes."],
         expect=["repo-orientation", "solutions-architect"]),
    Case("repo-orientation-neg", "repo-orientation", "negativo",
         "Decide qual arquitetura devo usar entre monolito modular e microsserviços para um sistema novo, ainda não existe código.",
         ["A resposta discute a decisão de arquitetura, sem fazer o mapeamento de um repositório."],
         forbid=["repo-orientation"]),
    Case("repo-orientation-limite", "repo-orientation", "limite",
         "Me orienta nesse repositório e diz o comando exato para rodar os testes e a versão do Python exigida.",
         ["O diretório de trabalho está vazio ou sem manifestos. A resposta diz que não encontrou o repositório, os comandos ou a versão, e NÃO inventa comando nem versão.",
          "Registra a lacuna e diz o que seria necessário para confirmar."],
         expect=["repo-orientation", "solutions-architect"]),
]
