# Qualidade de requisitos

Material de consulta para escrever e revisar as seções de um PRD. O modelo a preencher está em `assets/prd.md`.

## Problema, não solução

| Em vez de (solução) | Escreva (problema e resultado) |
|---|---|
| "Criar um dashboard" | "O gestor não consegue ver o andamento sem pedir relatório a alguém" |
| "Usar IA para responder" | "O atendente repete as mesmas respostas e perde tempo" |
| "Adicionar login com Google" | "O usuário desiste do cadastro por ter que criar mais uma senha" (só se o usuário disse isso) |

Se o usuário chegou com uma solução, registre-a como restrição ou como pergunta em aberto, e escreva o problema por trás dela.

## Objetivos e não objetivos

- **Objetivo:** resultado que o produto precisa alcançar, ligado a uma métrica quando existir.
- **Não objetivo:** algo plausível que fica de fora de propósito. Serve para o time não ampliar o escopo sem perceber. Só escreva os que o usuário confirmou.

## Usuários

Descreva por papel e contexto (quem é, o que quer fazer, com que frequência), não por demografia inventada. Se há mais de um tipo, diga qual é o principal. Persona sem fonte é suposição: marque como premissa.

## Métricas de sucesso

| Campo | Regra |
|---|---|
| Métrica | Algo mensurável (taxa, tempo, contagem) |
| Valor atual | Número real ou `A definir`. Nunca estimado sem fonte |
| Meta | Veio do usuário. Se não veio, `A definir` |
| Como medir | Onde o dado nasce (evento, relatório, pesquisa) |

Distinga métrica de resultado (o que muda para o usuário) de métrica de atividade (quanto o sistema foi usado). Prefira a primeira.

## Requisitos funcionais (RF)

- Um comportamento por requisito. Se tem "e" ligando duas ações, provavelmente são dois.
- Formato sugerido: "O sistema permite que [usuário] [ação] para [resultado]".
- Critério de aceite observável: "o usuário consegue X e vê Y".
- Toda linha tem **origem** (problema, necessidade, conversa). Sem origem, vai para "Perguntas em aberto".

### Prioridade

| Nível | Pergunta que define |
|---|---|
| Essencial | Sem isso o produto não resolve o problema? Define o MVP |
| Importante | Faz falta logo depois do lançamento? |
| Desejável | É bom ter, mas ninguém para por causa disso? |

Se tudo é Essencial, nada é. Se o usuário marcar tudo assim, pergunte o que ficaria de fora numa primeira entrega.

## Requisitos não funcionais (RNF)

Todo RNF tem um limite ou uma meta. Sem número, vira adjetivo.

| Vago | Verificável |
|---|---|
| "Rápido" | "A resposta aparece em até N segundos em P% das requisições" (N e P vêm do usuário, ou `A definir`) |
| "Seguro" | "Dados pessoais só acessíveis por quem tem permissão X" |
| "Disponível" | "Disponibilidade de N% no mês" (N: `A definir`) |

Categorias para conferir se falta alguma: desempenho, disponibilidade, segurança e privacidade (LGPD, se aplicável), acessibilidade, idioma, auditoria, compatibilidade.

## Riscos e premissas

- **Risco:** pode acontecer e machuca. Leva impacto e mitigação.
- **Premissa:** estamos tratando como verdade sem ter verificado. Se for falsa, o plano muda.
- **Pergunta em aberto:** precisa de resposta de alguém. Diga quem, se souber.

Hipótese de risco alto não validada na descoberta entra como premissa ou risco.

## Perguntas em aberto

Cada pergunta indica o que ela bloqueia (qual RF, qual decisão). Sem isso a lista vira um depósito de dúvidas sem dono.

## Checagem antes de mostrar o PRD

- [ ] Nenhum número sem fonte
- [ ] Todo RF tem origem, prioridade e critério de aceite
- [ ] Todo RNF tem limite ou `A definir`
- [ ] Nenhuma tecnologia escolhida (restrição imposta pelo usuário entra como fato)
- [ ] Nada que o usuário não mencionou foi acrescentado como requisito
- [ ] Seções com `A definir` repetidas em "Perguntas em aberto"
