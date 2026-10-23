# Revisão do PR da Rodada

Referência do `code-reviewer`, do `qa-engineer` e do `security-reviewer`. A gravidade, o escopo (`IN_SCOPE` ou
`OUT_OF_SCOPE`), o veredito e o modelo do relatório são os da skill `code-review-reliability`.

## Alcance

A revisão cobre o diff inteiro da rodada, `git -C <repo> diff <commit base>..HEAD`, mais o que ainda não foi commitado,
e roda os testes e o lint completos do repositório alvo. O requisito é a change do OpenSpec: os cenários das specs, as
decisões do `design.md` e o `decisoes.md`.

## Focos

Os caminhos desta seção partem da raiz do plugin, o diretório de onde vem este arquivo.

| Foco             | Quem                | Checklist                                                                  | Skills                                                                                |
| ---------------- | ------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Qualidade        | `qa-engineer`       | `.claude/skills/code-review-reliability/references/checklist-qualidade.md` | `code-review-reliability`, `test-generation`                                          |
| Segurança        | `security-reviewer` | `.claude/skills/code-review-reliability/references/checklist-seguranca.md` | `code-review-reliability`, `secret-handling-review`                                   |
| Arquitetura e PR | `code-reviewer`     | `.claude/skills/code-review-reliability/references/checklist-pr.md`        | `code-review-reliability` e a skill de área (`backend-patterns`, `frontend-patterns`) |

Além do checklist:

- **Qualidade:** cada cenário das specs tem teste que passa; com o campo `Sonar:`, em arquivo do diff, *vulnerability* é
  `CRITICAL`, *bug* é `WARNING` e *code smell* é `SUGGESTION`.
- **Arquitetura:** o diff segue o design e o manual vivo (`openspec/specs/`), e `git status --short` não mostra
  alteração fora do repositório alvo.

## Conferência

Depois de uma correção, cada foco confere só os próprios findings, com o que o `software-engineer` diz ter corrigido, e
o `code-reviewer` emite o relatório de novo. Finding novo aparece só se a correção o criou.

## Formato do Relatório

Use o modelo `assets/relatorio.md` da `code-review-reliability`, com o título `Revisão do PR: <change>, volta <n>` e o
revisor `code-reviewer`, `qa-engineer` ou `security-reviewer`. Sem findings, a seção Findings traz a linha `Nenhum.`
