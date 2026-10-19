# Catálogo de padrões

Use como lembrete de quando cada padrão vale a pena. Cada entrada: quando usar, o que custa.

## Estilos de implantação

- **Monolito**: um deployable. Use quando time pequeno e prazo curto. Custo: acoplamento cresce se não houver disciplina.
- **Monolito modular**: um deployable com módulos de fronteiras explícitas. Use como ponto de partida na maioria dos casos. Custo: exige disciplina para não cruzar as fronteiras.
- **Microsserviços**: serviços implantáveis separadamente. Use com times independentes, escala ou ciclo de release distintos por parte. Custo: rede, consistência eventual, observabilidade, operação.
- **Serverless/funções**: cargas esporádicas ou orientadas a eventos. Custo: limites de execução, dependência do provedor, cold start.

## Organização interna

- **Camadas (apresentação, domínio, dados)**: simples e conhecido. Custo: lógica de negócio vaza para as camadas de cima e de baixo.
- **Hexagonal (portas e adapters)**: isola o domínio de detalhes externos. Use quando há várias integrações trocáveis (canais de mensagem, provedores de IA). Custo: mais interfaces e indireção.
- **Plugin/Strategy**: comportamento escolhido em execução por um contrato comum. Use para extensibilidade controlada (ex.: novo canal sem mudar o fluxo central).

## Comunicação e dados

- **Síncrono (HTTP/RPC)**: simples, resposta imediata. Custo: acoplamento temporal.
- **Fila / mensageria**: desacopla produtor e consumidor, absorve picos, permite reprocessar. Custo: ordenação, duplicidade, idempotência.
- **Event-driven**: módulos reagem a eventos. Use para fluxos independentes e auditoria. Custo: difícil de rastrear e depurar.
- **CQRS**: modelos separados para leitura e escrita. Use só quando leitura e escrita têm necessidades muito diferentes. Custo: duplicação e consistência eventual.
- **Event sourcing**: estado como sequência de eventos. Use quando histórico completo é requisito. Custo: complexidade alta, difícil de migrar.
- **Webhook vs polling**: webhook é mais eficiente e exige endpoint público e validação de origem; polling é simples e gasta recursos.

## Multi-tenant e segurança

- **Isolamento por tenant**: por linha (coluna de tenant), por esquema ou por banco. Quanto maior o isolamento, maior o custo operacional. Escolha pelo risco de vazamento e por exigências de compliance.
- **Segredos de terceiros (tokens de integração)**: guarde fora do código, criptografados em repouso, sem exibir em listagens e logs. Detalhes de implementação ficam para o responsável por segurança.

## Perguntas úteis para decidir

- O que não pode falhar e o que pode degradar?
- Quem precisa implantar de forma independente?
- Que dado é caro de migrar depois?
- Qual fronteira, se errada, custa mais para corrigir?
- O que o time atual sabe operar?
