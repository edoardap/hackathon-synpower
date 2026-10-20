# Gestão de contratos: monolito ou microsserviços?

## Decisão

**Monolito modular**: um único deploy, um único banco, com módulos separados por domínio dentro do código.

Escolhi assim porque, sem dados sobre prazo, time e carga, esta é a opção mais barata de errar:

- Microsserviços cobram de entrada: orquestração, observabilidade distribuída, consistência entre serviços, pipelines múltiplos e um time com maturidade operacional. Isso só se paga com times grandes e independentes ou com cargas muito diferentes entre partes do sistema.
- Gestão de contratos é um domínio de transações e regras fortemente ligadas (contrato, partes, cláusulas, versões, aprovações, vencimentos, anexos). Separar cedo em serviços cria transações distribuídas onde um simples `COMMIT` resolveria.
- Um monolito modular é reversível. Se um módulo precisar escalar ou ser de outro time, ele pode ser extraído depois. O caminho inverso (juntar serviços mal cortados) é bem mais caro.

## Módulos sugeridos (limites internos)

Contratos (ciclo de vida e versões), Partes/Cadastros, Aprovações/Workflow, Prazos e Alertas (vencimento, renovação), Documentos (anexos e geração), Auditoria, Identidade/Permissões. Cada módulo expõe uma interface própria e não acessa as tabelas dos outros diretamente. Isso é o que mantém a extração futura possível.

## Os números que você pediu

Não tenho base para afirmar nenhum deles. Os valores abaixo são **premissas minhas**, para você confirmar ou corrigir. A decisão acima vale para uma faixa larga e não depende deles.

| Item | Premissa de trabalho | Observação |
|---|---|---|
| Time | 3 a 8 pessoas | Abaixo de uns 15 a 20 devs, microsserviços quase nunca compensam |
| Prazo para a primeira versão | 3 a 6 meses | A definir com o negócio |
| Usuários | centenas a poucos milhares | Uso interno de empresa, não consumo em massa |
| Contratos | dezenas de milhares | Crescimento lento |
| Requisições | dezenas por segundo no pico | Um servidor e um Postgres comuns aguentam com folga |
| Armazenamento de documentos | alguns GB a poucos TB | Em object storage, fora do banco |
| Disponibilidade | 99,5% a 99,9% | Sem exigência de 24x7 crítico (premissa) |

Também são premissas, não fatos: exigência de assinatura eletrônica, integração com ERP e requisitos de LGPD e retenção. Elas mudam o escopo mais do que a carga muda.

## O que me faria rever a decisão

Gatilhos para extrair um módulo (e só ele):

- Dois ou mais times travando um ao outro no mesmo deploy.
- Um módulo com perfil de carga muito diferente (por exemplo OCR ou geração de documentos em lote) que precise escalar sozinho.
- Requisito de isolamento, como dados de clientes com regras regulatórias distintas.
- Carga medida (não estimada) que um único banco não aguente depois de otimizações normais.

Dica barata: processamento pesado e assíncrono (alertas, geração de PDF) pode ficar numa fila com um worker separado, sem virar microsserviço.

## Perguntas em aberto (as que realmente mudam o desenho)

1. Quantas pessoas vão desenvolver e manter? E há prazo fixo?
2. Quantos usuários e contratos no ano 1 e no ano 3?
3. É para uma empresa só ou multiempresa (vários clientes no mesmo sistema)?
4. Há integrações obrigatórias (ERP, assinatura eletrônica, e-mail)?
5. Há exigências legais ou de auditoria específicas?

Com 1 a 3 respondidas, dá para trocar as premissas por números reais e, se for o caso, registrar a decisão em um ADR.
