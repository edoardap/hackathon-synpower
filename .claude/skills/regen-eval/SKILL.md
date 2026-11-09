---
name: regen-eval
description: 'Avalia uma skill por regeneração: usa um projeto real como gabarito, apaga da cópia tudo o que a skill deveria produzir (e o git, para o agente avaliado não ver histórico nem diff), roda a skill numa sala limpa e compara o resultado com o original via diff + juiz LLM. Use ao "testar/avaliar uma skill num projeto real", "ver se a skill reproduz a documentação/os testes do projeto", "rodar um eval de regeneração", "comparar o que a skill gera com o que já existe". É um método complementar ao `claude plugin eval` (que fica em evals/plugin-eval/), não o substitui.'
---

# Regen Eval

Avalia uma skill medindo o quão perto ela chega de recriar algo que um projeto real **já tem**. O projeto original é o
gabarito: apaga-se dele a cópia do artefato que a skill produz (a documentação, os testes, o ADR...), roda-se a skill nesse
estado "antes", e compara-se o que ela gerou com o que existia. É um eval de regeneração — útil quando o acerto é
subjetivo e um gabarito pronto vale mais que uma assertiva.

Exemplo: para testar uma skill de documentação no `atlas`, copia-se o `atlas`, apaga-se toda a documentação, roda-se a
skill, e vê-se se a documentação regenerada ficou parecida ou satisfatória perto da original.

É **complementar** ao `claude plugin eval`: aquele é prompt → assertiva (`evals/plugin-eval/`, regra do `AGENTS.md`); este
é regenerar sobre um projeto real e comparar com o gabarito. Não substitui nem altera a convenção de lá.

Nos caminhos abaixo, `${CLAUDE_SKILL_DIR}` é a pasta desta skill (`.claude/skills/regen-eval/`). O trabalho mecânico fica
no script `${CLAUDE_SKILL_DIR}/scripts/regen_eval.sh` (`prepare` e `diff`).

## Princípios

- **O original é sagrado.** O eval nunca escreve no projeto de origem. Tudo acontece em cópias dentro de um `workdir` de
  trabalho (use o scratchpad da sessão). O script se recusa a rodar se o `workdir` já existir, para não misturar runs.
- **Sala limpa de verdade.** O agente avaliado só pode enxergar a cópia "antes": sem o `.git` original (sem histórico nem
  diff que revele a resposta) e sem o gabarito por perto. Quem roda a skill é um subagente que recebe só o caminho da sala
  limpa — assim o resultado reflete a skill, não o acesso ao gabarito.
- **Sugere, confirma, só então apaga.** Deleção é irreversível na cópia. A skill propõe o conjunto de caminhos a remover a
  partir do que a skill-sob-teste produz, mostra ao usuário e só apaga o que ele confirmar. Nunca apaga por conta própria.
- **Gabarito é referência, não verdade absoluta.** "Parecido" não é "idêntico": uma documentação regenerada pode estar boa
  sem bater palavra por palavra. Por isso o veredito final é humano — o diff e o juiz LLM informam, não decidem.
- **Reprodutível.** Mesmo projeto, mesmo recorte apagado, mesma skill → dá para rodar de novo e comparar runs. O `workdir`
  por run mantém isso separado.

## Fluxo

### 1. Qual skill está sendo avaliada

Identifique a skill-sob-teste e **o que ela produz** — é isso que será apagado e regenerado. Leia o `SKILL.md` dela para
saber o tipo de saída (documentação, testes, ADR, migração, instrumentação...). Não altere a skill durante o eval: aqui
só se testa e reporta (regra do `AGENTS.md`).

### 2. Qual projeto de referência

Pergunte ao usuário, nesta ordem:

1. **É para rodar no projeto em que esta skill está instalada / no repositório atual?** Se sim, use-o.
2. **Senão, qual o caminho do projeto de referência?**

Seja flexível: se o usuário não decidir, **sugira** entre os projetos irmãos (liste os diretórios ao lado do projeto
atual — por exemplo os de `Projects/Synpower/`: `ai-agents`, `data-pipeline-orchestrator`, `extrator-ai-gov`) e deixe-o
escolher. O eval pode rodar em **um ou mais** projetos de referência — nesse caso, repita o fluxo por projeto, cada um no
seu `workdir`.

Um bom projeto de referência tem o artefato que a skill produz **bem feito** (é o gabarito) e representa o uso real.

### 3. Escolher o que apagar (sugerir → confirmar)

A partir do que a skill-sob-teste produz, **proponha** o conjunto de caminhos a remover e mostre ao usuário para ele
ajustar o escopo. Exemplos de ponto de partida:

| Skill-sob-teste produz | Sugestão de caminhos a apagar |
|---|---|
| Documentação | `docs/**`, `README.md`, `**/*.md` (confirme quais) |
| Testes | `tests/**`, `**/test_*.py` |
| ADR | `docs/adr/**` |
| Migração de schema | o último changeset de `resources/liquibase/tables/` |

Liste explicitamente o que vai sumir e **espere o OK** antes de apagar. O escopo é do usuário: ele inclui, exclui e corta.

### 4. Preparar a sala limpa

Com os caminhos confirmados, rode:

```bash
${CLAUDE_SKILL_DIR}/scripts/regen_eval.sh prepare <projeto_origem> <workdir> <caminho1> [caminho2...]
```

O script cria `<workdir>/golden` (gabarito intacto, com git — **não exponha à skill**) e `<workdir>/clean` (a sala limpa:
sem o `.git` original, com os caminhos apagados e um git recriado do zero com um único commit `baseline`). Use um
`<workdir>` novo no scratchpad da sessão, um por projeto/run.

### 5. Rodar a skill na sala limpa

Rode a skill-sob-teste **só sobre `<workdir>/clean`**, idealmente despachando um subagente que recebe apenas esse caminho
e a skill — sem o `golden`, sem o projeto original. Assim o resultado mede a skill, não o acesso ao gabarito. Deixe o
agente trabalhar como trabalharia de verdade; não dê dicas que o gabarito traria.

### 6. Comparar e julgar

```bash
${CLAUDE_SKILL_DIR}/scripts/regen_eval.sh diff <workdir> <caminho1> [caminho2...]
```

Isso mostra duas visões: **(a)** o que a skill produziu (git status/diff + arquivos novos da sala limpa) e **(b)** o
regenerado contra o gabarito, caminho por caminho.

Então avalie em duas camadas:

- **Diff** — a comparação crua, para o usuário ver com os próprios olhos.
- **Juiz LLM** — despache um subagente juiz que recebe o artefato **regenerado** e o **gabarito** e avalia similaridade e
  qualidade (cobriu os mesmos pontos? ficou claro? faltou algo que o original tinha? inventou algo que o original não
  tem?), com nota/veredito e justificativa. O juiz informa; não decide sozinho.

Feche com um resumo: o que ficou próximo, o que divergiu, e a recomendação. O **veredito final é do usuário** — o gabarito
é referência, não verdade absoluta.

## Rodar em vários projetos

Para avaliar a mesma skill em mais de um projeto de referência, repita os passos 2–6 por projeto, cada um no seu
`<workdir>`, e compare os resultados no fim. Vários gabaritos deixam o eval menos preso às particularidades de um repo só.

## Quando NÃO usar

- **Eval por assertiva** (prompt → resultado verificável, sem gabarito pronto num projeto real) é do `claude plugin eval`
  em `evals/plugin-eval/`. Este método é para quando o acerto é subjetivo e já existe um exemplo bom para comparar.
- **Skill cujo produto não é arquivo no repositório** (ex.: uma skill que só conversa ou só lê e reporta) não tem artefato
  para apagar e regenerar — este método não se aplica.
- **Alterar a skill-sob-teste** durante o eval. Aqui só se testa e reporta; a correção vem depois, noutro momento.
