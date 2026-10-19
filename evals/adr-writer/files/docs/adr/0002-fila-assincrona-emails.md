# ADR-0002: Enviar e-mails de notificação por fila assíncrona

- **Status:** Aceito
- **Data:** 2026-10-01
- **Decisores:** Time

## Contexto
Notificações de oportunidade não podem bloquear a requisição.

## Decisão
Enviar e-mails por uma fila assíncrona (worker separado).

## Alternativas consideradas
- **Envio síncrono:** descartado por bloquear a requisição.

## Consequências
- **Positivas:** Requisições rápidas.
- **Negativas / custos:** worker extra para operar.
- **Riscos e gatilho de revisão:** volume de e-mails baixo.

## Questões em aberto
- Nenhuma

## Relacionados
- Nenhum
