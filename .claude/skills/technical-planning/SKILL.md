---
name: technical-planning
description: Decompõe requisitos de um PRD (ou de uma lista de requisitos) em épicos, histórias de usuário e critérios de aceite testáveis, com rastreabilidade até cada requisito, dependências entre histórias e ordem sugerida de entrega. Use sempre que o usuário pedir para quebrar requisitos em histórias, "criar histórias de usuário", "critérios de aceite", "backlog a partir do PRD", "planejamento técnico", "decompor em épicos", "transformar o PRD em tarefas", ou colar um PRD gerado pela skill prd-writing querendo o próximo passo, mesmo que não use essas palavras.
---

# Planejamento Técnico

Transforme requisitos em histórias pequenas, entregáveis e verificáveis. O objetivo é que cada história caiba numa
entrega curta e que qualquer pessoa do time consiga dizer, sem discutir, se ela está pronta. Histórias vagas viram
discussões no meio do desenvolvimento, e critérios de aceite fracos viram retrabalho depois.

## Idioma

Converse e escreva em português do Brasil. Mantenha termos técnicos e identificadores no original.

## Entrada

A entrada ideal é o PRD da skill `prd-writing`, principalmente a tabela de requisitos funcionais (`RF-01`, prioridade,
critério de aceite, origem), os requisitos não funcionais (`RNF-01`), os usuários e o escopo do MVP. Procure o PRD na
conversa ou leia o arquivo que o usuário indicar. Aceite também uma lista simples de requisitos.

Se faltar critério de aceite, usuário ou prioridade em algum requisito, não invente. Pergunte em uma rodada curta (no
máximo 3 perguntas) ou registre como pendência na história.

## Fluxo

1. **Agrupe em épicos.** Junte requisitos que entregam um objetivo de usuário em comum (por exemplo, "Cadastro e acesso"
   ou "Ingestão de documentos"). Dê a cada épico um nome em linguagem de negócio.
2. **Quebre em histórias.** Cada requisito funcional gera uma ou mais histórias. Quebre quando uma história não couber em
   poucos dias de trabalho, tiver mais de um comportamento principal ou misturar usuários diferentes. Prefira fatias
   verticais, que entregam valor de ponta a ponta, a fatias por camada técnica.
3. **Escreva os critérios de aceite** de cada história no formato Dado, Quando, Então. Inclua o caminho feliz e os
   casos de erro e de borda relevantes, porque são os que costumam ser esquecidos.
4. **Trate os requisitos não funcionais.** Se um RNF vale para todo o sistema (segurança, desempenho, LGPD), registre-o em
   "Critérios transversais" e referencie nas histórias afetadas. Se vale só para uma história, vire critério dela.
5. **Mapeie dependências e ordem.** Indique o que bloqueia o quê e sugira uma ordem de entrega que coloque o MVP
   (requisitos Essenciais) primeiro. Dependências externas, como outra equipe ou outro sistema, ganham destaque.
6. **Verifique a cobertura.** Todo requisito do PRD deve aparecer em pelo menos uma história, e toda história deve citar
   o requisito de origem. Liste qualquer requisito sem história e qualquer história sem origem.
7. **Revise com o usuário.** Mostre o resultado no chat e pergunte se quer salvar em arquivo. Se quiser, salve em
   Markdown no caminho indicado (por padrão `docs/planejamento/<nome-do-sistema>.md`).

## Regras de qualidade

- **Boa história (INVEST):** independente quando possível, negociável, com valor claro, pequena, estimável e testável.
- **Formato da história:** "Como [usuário], quero [ação], para [benefício]". O benefício não pode ser só repetir a ação;
  se não houver benefício claro, questione se a história é necessária.
- **Critérios verificáveis:** cada critério descreve algo observável e tem um resultado que pode ser conferido. Evite
  "rápido", "fácil" e "amigável"; use números, mensagens e estados concretos.
- **Sem solução técnica:** não decida tecnologia, tabela ou arquitetura. Descreva o comportamento esperado. Se o usuário
  pedir tarefas técnicas, liste-as separadamente por história, sem misturar com os critérios de aceite.
- **Sem estimativas inventadas:** só dê pontos ou prazos se o usuário pedir, e deixe claro que são palpites.
- **Prioridade herdada:** mantenha a prioridade do requisito (Essencial, Importante, Desejável) e não promova nem rebaixe
  sem avisar.

## Modelo de saída

Leia `assets/planejamento.md` e preencha o modelo mantendo os títulos. Não copie texto de exemplo como se fosse dado real.
Consulte `references/historias-e-criterios.md` ao agrupar épicos, quebrar histórias, escrever critérios Dado/Quando/Então e conferir a cobertura.
