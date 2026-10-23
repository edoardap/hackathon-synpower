---
name: prd-writing
description: Escreve um PRD (Documento de Requisitos de Produto) completo a partir do resumo gerado pela skill product-discovery, de notas soltas ou de uma descrição de produto. Identifica lacunas, faz poucas perguntas só sobre o que falta e nunca inventa números ou decisões. Use sempre que o usuário pedir um PRD, "documento de requisitos", "especificação do produto", "transforma isso em PRD", "escreve o PRD", ou colar o resumo de uma descoberta de produto querendo o próximo passo, mesmo que não diga "PRD" explicitamente.
---

# Escrita de PRD

Transforme o que já se sabe sobre um sistema em um PRD que um time consiga usar para planejar e construir. Um PRD bom
define o problema e o resultado esperado, não a solução técnica. Quem lê precisa saber o que construir, para quem, como
medir o sucesso e o que ainda está em aberto.

## Idioma

Escreva o PRD e converse em português do Brasil. Mantenha termos técnicos e identificadores no original.

## Entrada

A entrada ideal é o resumo da skill `product-discovery`. Procure-o na conversa; se o usuário indicar um arquivo, leia-o.
Aceite também notas soltas ou uma descrição simples. Mapeie o que existe para as seções do PRD (veja a tabela) e
descubra o que falta.

| Seção do relatório da descoberta (Resumo para o PRD) | Vai para a seção do PRD |
| -- | -- |
| Resumo, Problema, Usuários e contexto | Visão geral, Problema e oportunidade |
| Usuários e contexto | Usuários |
| Escopo do MVP (dentro/fora) | Objetivos e não objetivos, Escopo |
| Fluxo principal | Fluxos do usuário |
| Requisitos funcionais | Requisitos funcionais |
| Requisitos não funcionais | Requisitos não funcionais |
| Dados e integrações, Restrições | Dependências e restrições |
| Métricas de sucesso | Métricas de sucesso |
| Riscos e premissas, Hipóteses, Perguntas em aberto | Riscos, Premissas, Perguntas em aberto |
| Partes interessadas, Marcos e dependências | Partes interessadas, Marcos |

## Fluxo

1. **Verifique as lacunas.** Antes de escrever, veja quais seções ficariam vazias ou vagas. Se faltarem itens que mudam o
   escopo, faça uma rodada de no máximo 3 perguntas (com AskUserQuestion, se disponível). Para o resto, não pergunte.
2. **Escreva o PRD** com o modelo abaixo. Onde a informação não existir, escreva `A definir` e liste em "Perguntas em
   aberto". Um espaço honesto é melhor do que um número inventado, porque o time pode tomar decisões em cima dele.
3. **Revise com o usuário.** Mostre o PRD no chat, destaque as seções com `A definir` e pergunte se ele quer salvar em
   arquivo. Se quiser, salve em Markdown no caminho que ele indicar (por padrão `docs/prd/<nome-do-sistema>.md`).

## Regras de qualidade

- **Rastreabilidade:** todo requisito funcional deve ligar-se a um problema ou a uma necessidade de usuário. Requisito
  sem origem costuma ser escopo que escorregou.
- **Testabilidade:** cada requisito funcional leva um critério de aceite observável ("o usuário consegue X e vê Y"), e
  não adjetivos vagos como "rápido" ou "intuitivo". Requisitos não funcionais levam um número ou um limite.
- **Priorização:** classifique requisitos como Essencial, Importante ou Desejável. Só o Essencial define o MVP.
- **Sem solução técnica:** não escolha tecnologia nem desenhe arquitetura. Restrições técnicas que o usuário já impôs
  entram em "Dependências e restrições", como fatos.
- **Fiel à fonte:** não acrescente funcionalidades que o usuário não mencionou. Sugestões vão em "Perguntas em aberto".

## Modelo do PRD

Leia `assets/prd.md` e preencha o modelo mantendo os títulos. Não copie texto de exemplo como se fosse dado real.
Consulte `references/qualidade-de-requisitos.md` ao escrever e revisar as seções (problema, métricas, RF, RNF, prioridade, riscos) e para a checagem final antes de mostrar o PRD.
