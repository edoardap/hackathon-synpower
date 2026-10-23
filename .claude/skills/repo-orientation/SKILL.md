---
name: repo-orientation
description: Identifica a estrutura e as convenções de um repositório (layout de pastas, stack, comandos de build/teste/lint, convenções de código, commits e branches) e devolve um relatório estruturado, pensado para ser consumido por outro agente. Use sempre que o usuário entrar em um repositório novo ou desconhecido, pedir para "entender o projeto", "me oriente nesse repo", "como esse projeto é organizado", "quais as convenções", ou antes de implementar, corrigir ou revisar código em um repo que ainda não foi explorado, mesmo que ele não peça orientação explicitamente.
---

# Repo Orientation

Mapeia um repositório e entrega um relatório que outro agente consegue usar sem reexplorar o projeto. Somente leitura: não crie, edite nem apague arquivos, e não instale dependências.

## Princípios

- **Evidência, não suposição.** Cada afirmação cita o arquivo de onde veio (`package.json`, `Makefile`, `.github/workflows/ci.yml`...). Quem consome o relatório não consegue conferir o que você "achou".
- **Marque o que não encontrou.** Escreva `não encontrado` ou `inferido` em vez de preencher lacunas. Um comando inventado quebra o agente seguinte.
- **Seja curto.** Liste só o que muda a forma de trabalhar no repo. Não descreva arquivo por arquivo.
- **Documentação do repo manda.** Se houver `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` ou `README`, leia primeiro e priorize o que estiver lá sobre a sua dedução.

## Passos

1. **Visão geral.** Liste a raiz (`ls -la`) e as pastas de primeiro nível. Verifique se é git (`git rev-parse --is-inside-work-tree`), a branch atual, e se é monorepo (workspaces, `packages/`, `apps/`, `go.work`, `Cargo.toml` com `[workspace]`).
2. **Docs de orientação.** Leia `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `README*` e `docs/` quando existirem. Se existir `graphify-out/`, leia o `GRAPH_REPORT.md` e use `graphify query` para perguntas de dependência e impacto; o grafo não traz comandos nem convenções, e pode estar desatualizado (compare o commit do relatório com `git rev-parse HEAD`).
3. **Stack.** Detecte pelos manifestos: `package.json`, `pyproject.toml`, `requirements*.txt`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `Gemfile`, `composer.json`, `*.csproj`. Anote linguagens, frameworks, versões fixadas (`.nvmrc`, `.python-version`, `.tool-versions`) e gerenciador de pacotes (pelo lockfile).
4. **Comandos.** Extraia de `scripts` do `package.json`, `Makefile`, `justfile`, `Taskfile`, `tox.ini`, `pyproject.toml` e CI. Cubra instalar, rodar em dev, build, testes (todos e um só), lint e formatação. Se CI e docs divergirem, registre as duas versões.
5. **Convenções de código.** Leia configs de lint e formatação (`.eslintrc*`, `prettier`, `ruff`, `black`, `.editorconfig`, `rustfmt.toml`). Olhe 2 ou 3 arquivos representativos para nome de arquivos, imports e estilo de testes. Localize onde ficam os testes e como são nomeados.
6. **Commits e branches.** Veja `git log --oneline -20` para o padrão de mensagem (Conventional Commits, prefixos de ticket etc.), `commitlint`, hooks (`.husky/`, `.pre-commit-config.yaml`) e modelos de PR (`.github/`).
7. **Armadilhas.** Anote o que pode surpreender: variáveis de ambiente exigidas (`.env.example`), serviços externos (Docker, banco), código gerado que não deve ser editado, pastas ignoradas.

## Referências

- `references/stack.md`: no passo 3, para ler manifestos, lockfiles e versões, reconhecer monorepo e tratar repo sem código.
- `references/comandos-e-convencoes.md`: nos passos 4 a 7, para saber onde achar cada comando, convenção, padrão de commit e armadilha, e como registrar lacunas sem chutar.

## Formato da saída

Responda em português, neste formato exato, para que o agente seguinte consiga ler por seção. Omita seções sem conteúdo só se escrever `não encontrado`.

```
# Orientação do repositório: <nome>

## Resumo
<1 a 3 linhas: o que é o projeto e seu tipo (app, lib, monorepo...)>

## Estrutura
- <pasta/>: <papel>
(só pastas relevantes)

## Stack
- Linguagens/frameworks: ...
- Gerenciador de pacotes: ...
- Versões: ...

## Comandos
| Tarefa | Comando | Fonte |
|---|---|---|
| Instalar | ... | ... |
| Dev | ... | ... |
| Build | ... | ... |
| Testes (todos) | ... | ... |
| Teste único | ... | ... |
| Lint/format | ... | ... |

## Convenções
- Código: ...
- Testes (onde ficam, nomes): ...
- Commits: ...
- Branches/PR: ...

## Armadilhas
- ...

## Lacunas
- <o que não foi possível confirmar e por quê>
```

Não proponha mudanças no repo nem execute build ou testes por conta própria; rodar comandos de verificação só se o usuário pedir.
