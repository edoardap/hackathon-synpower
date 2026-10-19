# Documento de design técnico

Entregável que liga o PRD à implementação: é o que o time de código lê para saber o que construir, onde e em que ordem. Salve em `docs/architecture/<nome>/design.md` (mesmo `<nome>` do PRD, em minúsculas e com hífens). Os diagramas C4 e os ADRs ficam ao lado, em `docs/architecture/<nome>/` e `docs/adr/`.

## Quando usar

Só para mudança com decisão de arquitetura, componente novo ou interação entre componentes. Em mudança pequena e óbvia, a recomendação da `architecture-patterns` basta e não precisa deste documento.

## Antes de escrever

1. Leia o PRD, as histórias e os critérios de aceite. Cada componente deve apontar para um `RF-xx`/`HU-xx`.
2. Leia os ADRs com status `Aceito` em `docs/adr/`. Cada um é uma restrição: o design deve **seguir** ou **substituir** (novo ADR, antigo marcado `Substituído por ADR-NNNN`). Nunca ignore em silêncio.
3. Rode `repo-orientation` se houver código que você ainda não conhece. A análise de reuso depende dela.
4. Pesquise o que for desconhecido nesta ordem: código do repositório, docs do projeto, documentação oficial da tecnologia, web. Se não achar, escreva "não verificado". Não invente API, padrão ou comportamento.

## Modelo

```markdown
# Design: <nome>

- **Status:** Rascunho | Aprovado
- **Origem:** <PRD e histórias, ex.: docs/prd/<nome>.md, HU-01 a HU-05>

## Visão geral da arquitetura
<Duas ou três frases e um diagrama Mermaid `graph TD` com os componentes e como conversam.>

## Reuso do que já existe
| Componente existente | Local | Como usar (estender, importar, referenciar) |
|---|---|---|

| Sistema / ponto de integração | Como integra |
|---|---|

## Componentes
### <Componente>
- **Propósito:** uma frase
- **Local:** caminho do arquivo ou módulo
- **Interfaces:** assinaturas ou endpoints que expõe
- **Depende de:**
- **Reaproveita:**
- **Atende:** RF-xx, HU-xx

## Modelos de dados
<Entidades, campos e relações. Omita se não houver dados.>

## Cobertura de dimensões
Cada dimensão recebe uma decisão (com o componente que a resolve) ou "N/A porque…". Em mudança média, cubra só as que se aplicam.
| Dimensão | Decisão ou N/A |
|---|---|
| Validação de entrada | |
| Falha e falha parcial | |
| Idempotência e retry | |
| Autenticação, autorização e rate limit | |
| Concorrência e ordem | |
| Ciclo de vida dos dados (retenção, expiração) | |
| Observabilidade (logs, métricas) | |
| Falha de dependência externa | |
| Integridade de transição de estado | |

## Tratamento de erros
| Cenário de erro | Tratamento | Impacto para o usuário |
|---|---|---|

## Riscos e preocupações
| Preocupação | Local (`arquivo:linha`) | Impacto | Mitigação |
|---|---|---|---|
Categorias: código frágil, dívida técnica, segurança, desempenho, lacuna de teste. Toda preocupação tem mitigação. "Nenhuma encontrada" é válido.

## Decisões técnicas
| Decisão | Escolha | Motivo | ADR |
|---|---|---|---|
Só as não óbvias. Decisão que vale para o projeto todo vira ADR (`adr-writer`); a local fica só aqui.

## Plano de implementação
Um passo por entrega (um componente, endpoint ou arquivo), em ordem. A dependência nunca aponta para um passo posterior.
1. **<passo>**
   - **Onde:** caminho
   - **Depende de:** passo anterior ou "nenhum"
   - **Reaproveita:** código existente
   - **Atende:** RF-xx, HU-xx
   - **Pronto quando:** critérios binários (passa ou não passa)

## Decisões fixadas e critério do implementador
- **Fixadas** (pelo usuário ou por ADR aceito; não reabrir): ...
- **Critério do implementador** (liberdade explícita): ...

## Premissas
Tudo o que você assumiu sem confirmação. Nada fica em silêncio.
| Tema | Padrão adotado | Motivo | Confirmada? |
|---|---|---|---|

## Perguntas em aberto
```

## Regras

- **Reuso primeiro.** Todo componente cita o que reaproveita. Se nada existe, diga isso.
- **Componente pequeno.** Se faz três coisas ou mais, divida.
- **Interface antes de implementação.** Defina as assinaturas aqui, não deixe para o código.
- **Prefira diagrama a texto longo.**
- **Só o que foi pedido.** Sem abstração ou configuração que nenhum requisito justifique.
- **Tamanho.** Até cerca de 4.800 palavras. Perto de 3.800, apare ou divida (por exemplo, um design por módulo).
- **Aprovação.** O design só vira `Aprovado` com a confirmação do usuário, antes de seguir para a implementação.
