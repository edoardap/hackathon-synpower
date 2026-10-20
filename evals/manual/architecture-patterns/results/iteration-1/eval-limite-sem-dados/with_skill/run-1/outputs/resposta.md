## Decisão: monolito ou microsserviços no sistema de gestão de contratos

### Contexto
Sistema novo de gestão de contratos. Não há PRD, repositório nem ADRs `Aceito` (não existe `docs/adr/`), então não há decisão anterior a respeitar ou substituir.

Sobre os números: **não vou inventar prazo, tamanho de time nem carga.** Você pediu que eu estime, mas qualquer valor que eu desse seria chute e poderia levar a uma arquitetura errada com cara de justificada. O que dá para fazer com segurança: decidir o ponto de partida, que **não depende desses números**, e dizer quais números mudariam a decisão e a partir de que ponto.

### Forças e restrições
- Confirmado: sistema novo (sem legado a preservar), domínio de contratos.
- **Desconhecido:** prazo, time, carga. Tratados como `A definir`.
- Presumido (a validar): contratos têm dados sensíveis (partes, valores), então LGPD, controle de acesso e trilha de auditoria provavelmente pesam. Possíveis integrações (assinatura eletrônica, ERP, e-mail), ainda não confirmadas.
- Pontos cegos a checar: concorrência na edição do mesmo contrato, versionamento e ciclo de vida dos dados (retenção, exclusão), idempotência em integrações, observabilidade.

### Opções
| Opção | Ganha | Paga | Reversível? |
|---|---|---|---|
| Monolito simples | Menor custo e prazo | Acoplamento cresce sem disciplina | Sim, mas fica caro se as fronteiras forem ruins |
| **Monolito modular** | Um deployable, fronteiras explícitas, dá para extrair um módulo depois | Exige disciplina nas fronteiras | Sim (extração gradual) |
| Microsserviços | Escala e deploy independentes por parte, times autônomos | Rede, consistência eventual, observabilidade, operação | Difícil (dados e contratos entre serviços) |

### Recomendação
**Monolito modular**, com fronteiras explícitas entre módulos (por exemplo contratos, partes, documentos, notificações; os nomes finais dependem do PRD) e integrações externas atrás de interfaces/adapters. Motivo: sistema novo, domínio ainda não validado e nenhum requisito conhecido que force microsserviços (escala independente, times independentes, isolamento de falha). Microsserviços sem esses motivos são custo sem retorno, e a recomendação vale mesmo sem saber prazo, time e carga, porque o monolito modular é o ponto de partida mais barato e reversível em todos os cenários plausíveis.

**Gatilhos de revisão** (os "números" que importam, sem eu inventar o valor):
| Número a levantar | Por que muda a decisão | Quem responde |
|---|---|---|
| Prazo até a primeira versão | Prazo curto reforça o monolito; só prazo longo com time grande abre espaço para outra opção | Patrocinador/produto |
| Tamanho e nº de times que vão mexer no código | Times que não conseguem coordenar deploy num só código são o motivo mais comum para dividir | Gestão de engenharia |
| Carga: usuários simultâneos, nº de contratos, volume de documentos/anexos, picos (ex.: fim de mês) | Só justifica separar uma parte se ela precisar escalar de forma diferente do resto; carga baixa ou moderada não justifica | Produto/negócio, com dados de uso se houver |
| Disponibilidade exigida (o que não pode cair) | Se um módulo precisa sobreviver à falha de outro, avalie isolá-lo | Negócio |
| Exigências de compliance (LGPD, retenção, auditoria) | Afetam isolamento de dados e modelo de tenant, decisões caras de reverter | Jurídico/segurança |
| Multi-cliente (vários clientes no mesmo sistema?) | Define isolamento por linha, esquema ou banco, difícil de mudar depois | Produto |

Regra prática: revisar para extrair um módulo só quando um desses números mostrar uma pressão concreta e medida, não por previsão.

### Perguntas em aberto
- Qual o prazo para a primeira versão? (produto)
- Quantas pessoas e quantos times vão desenvolver e operar? (engenharia)
- Quantos usuários, contratos e anexos esperados, e há picos? Se não houver estimativa, posso propor uma forma barata de medir após o lançamento. (negócio)
- O sistema atende uma só organização ou várias? (produto)
- Quais integrações externas são obrigatórias? (negócio/TI)
- Há stack ou nuvem já definidas? (engenharia)

### Próximos passos (opcionais)
- Diagramas C4 (Contexto e Container) do monolito modular: posso gerar, marcando o que está `a validar`.
- Registrar a decisão com a skill `adr-writer` (status Proposto até você responder as perguntas acima).
- Se você trouxer ao menos uma estimativa grosseira de prazo, time e carga, eu reavalio os gatilhos acima.
