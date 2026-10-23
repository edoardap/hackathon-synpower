# Boas práticas de ADR

Material de consulta para escrever e manter ADRs. O modelo a preencher está em `assets/adr.md`.

## Quando escrever (e quando não)

Escreva quando as três condições valem: é difícil de reverter, seria surpreendente sem contexto e nasceu de um trade-off real.

| Escreva ADR | Não escreva ADR |
|---|---|
| Escolha de stack, banco, fila, provedor | Nome de variável, formatação, lint |
| Estilo de arquitetura (monolito modular, eventos) | Detalhe interno fácil de trocar |
| Contrato público ou integração externa | Bug fix |
| Estratégia de dados, multi-tenancy, segurança | Decisão que já está óbvia no código |
| Padrão que o time vai seguir daqui para frente | Preferência pessoal sem alternativa real |

## Ciclo de vida do status

```
Proposto → Aceito → Substituído por ADR-NNNN
        ↘ Rejeitado
```

- `Proposto`: escrito, ainda sem aprovação. Em dúvida, use este.
- `Aceito`: o usuário confirmou. Passa a valer para as próximas decisões.
- `Rejeitado`: foi avaliado e descartado. Mantenha o ADR: ele evita rediscutir a mesma ideia.
- `Substituído por ADR-NNNN`: outra decisão tomou o lugar. Só o campo de status do antigo muda, o resto fica como estava.

Um ADR aceito não é editado para "corrigir a história". Se a decisão mudou, o ADR novo explica o que mudou e por quê.

## Como escrever cada seção

- **Título:** diga a decisão, não o tema. "Usar Postgres com RLS para isolar tenants", e não "Banco de dados".
- **Contexto:** os fatos que forçaram a decisão (requisitos, prazo, time, restrição legal). Cite a origem (PRD, conversa). Sem opinião aqui.
- **Decisão:** uma ou duas frases no tom afirmativo. "Vamos usar X", e não "poderíamos usar X".
- **Alternativas:** só as que alguém considerou de verdade, incluindo a mais simples. Cada uma com um motivo específico para ter sido descartada. "Mais complexo" sozinho não é motivo.
- **Consequências:** liste o lado ruim com a mesma honestidade do bom. Um ADR sem custo declarado normalmente está escondendo um.
- **Gatilho de revisão:** a condição observável que reabre a decisão ("se passarmos de N tenants", "se o provedor mudar o preço"). Se o valor de N não existe, escreva `A definir`.
- **Relacionados:** RF-xx, HU-xx, diagramas em `docs/architecture/` e outros ADRs. É o que mantém a rastreabilidade.

## Sinais de ADR fraco

- Só tem a decisão, sem contexto nem alternativas.
- As alternativas são espantalhos, escritas só para a escolhida parecer boa.
- Os números (carga, custo, prazo) não vieram de ninguém.
- Mistura duas decisões no mesmo arquivo.
- Passa de uma página.

## Exemplo curto (ilustrativo, não é dado do projeto)

```markdown
# ADR-0007: Usar fila para envio de notificações

- **Status:** Proposto
- **Data:** AAAA-MM-DD
- **Decisores:** A definir

## Contexto
O envio de e-mail acontece dentro da requisição e derruba a resposta quando o provedor está lento (origem: conversa).

## Decisão
Enviar notificações por uma fila, em um worker separado da API.

## Alternativas consideradas
- **Manter síncrono:** mais simples, mas a lentidão do provedor continua chegando ao usuário.
- **Chamar o provedor em thread da própria API:** perde mensagens se o processo cair.

## Consequências
- **Positivas:** a API deixa de depender do tempo de resposta do provedor.
- **Negativas / custos:** mais uma peça para operar e monitorar.
- **Riscos e gatilho de revisão:** reavaliar se o volume ficar pequeno demais para justificar o worker (limite: A definir).

## Questões em aberto
- Qual tecnologia de fila usar.

## Relacionados
- Nenhum
```

## Índice

Mantenha `docs/adr/README.md` com uma linha por ADR (`| ADR | Título | Status | Data |`). Ao substituir um ADR, atualize o status dos dois no índice.
