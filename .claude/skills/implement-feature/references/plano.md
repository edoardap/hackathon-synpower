# Plano da Rodada

Como o `software-engineer` escreve a change do OpenSpec de uma rodada a partir da entrada (PRD, histórias e design).
Para o modelo de cada arquivo, rode `openspec instructions <artefato> --change <change> --json`; o
`openspec/config.yaml` do repositório alvo acrescenta as regras abaixo às instruções.

## Origem de Cada Arquivo

| Arquivo                      | O que escrever                                                                                                                                                                                 | De onde vem                                                              |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `proposal.md`                | Por que a rodada existe, o que entra e o que fica de fora, e as capacidades (`Capabilities`) que ela cria ou muda                                                                              | O recorte, o PRD e as histórias citadas por número (`HU-01`)             |
| `specs/<capacidade>/spec.md` | Os requisitos e cenários da rodada, no formato `### Requirement:` e `#### Scenario:` com `WHEN` e `THEN`                                                                                       | Os critérios de aceite das histórias do recorte, um cenário por critério |
| `design.md`                  | Link para o design técnico da entrada, as decisões que valem só para esta rodada, os pontos de teste e, se o recorte muda o schema, o plano de migração no modelo da `database-migration-plan` | O design técnico e o código do repositório alvo                          |
| `tasks.md`                   | As fases da rodada                                                                                                                                                                             | O plano de implementação do design, limitado ao recorte                  |

Capacidade que já existe em `openspec/specs/` (de uma rodada anterior) entra como `MODIFIED`, com o requisito inteiro
copiado e alterado; capacidade nova entra como `ADDED`.

## Formato do `tasks.md`

```markdown
## 1. <título da fase>

- **Depende de:** nenhuma
- **Aceite:** <cenários das specs que esta fase prova>
- **Skill:** <backend-patterns | frontend-patterns | database-migration-plan>

**Tarefas:**

- [ ] 1.1 <tarefa com o arquivo que ela toca>
- [ ] 1.2 <tarefa>

**Verificação:** `<comando que roda no repositório alvo e prova o aceite>`
```

## Regras

1. **Fase é um commit.** Cada fase tem um conjunto de mudanças que faz sentido sozinho.
2. **Dependência explícita.** `Depende de:` lista as fases de que esta precisa, ou `nenhuma`. Fases sem dependência
   entre si editam arquivos disjuntos, porque rodam em paralelo.
3. **Aceite rastreável.** Cada cenário das specs aparece no `Aceite:` de pelo menos uma fase, e nenhuma fase traz
   trabalho que o recorte não pede.
4. **Uma skill por fase.** Fase que mistura backend e frontend vira duas fases.
5. **Banco primeiro.** Mudança de schema é a primeira fase, e as outras dependem dela.
6. **Verificação real.** O comando roda de verdade no repositório alvo e falha se o aceite não estiver cumprido. Ele
   cita só comandos do projeto e das skills pelo nome, sem caminho absoluto da máquina.
7. **Pontos de teste públicos.** Cada ponto de teste é uma interface pública (rota, função exportada, tela).
8. **Isolamento.** Rodada com dado de organização tem, no `Aceite:`, o teste de isolamento entre duas organizações da
   `backend-patterns`.

## Antes de Devolver

Confira cada regra acima e rode `openspec validate <change> --strict`. A change só volta para a sessão principal com a
validação passando.
