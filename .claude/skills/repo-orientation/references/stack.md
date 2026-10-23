# Detectar a stack

Material de consulta para o passo "Stack". Tudo aqui é pista para **procurar**, e não resposta pronta. Só reporte o que o arquivo do repo confirmar.

## Manifesto indica a linguagem

| Arquivo | Linguagem ou ecossistema | O que ler dentro |
|---|---|---|
| `package.json` | JavaScript ou TypeScript (Node) | `dependencies`, `scripts`, `engines`, `workspaces`, `type` |
| `tsconfig.json` | TypeScript | `compilerOptions`, `paths`, `include` |
| `pyproject.toml` | Python | `[project]`, `[tool.*]`, dependências, gerenciador |
| `requirements*.txt`, `setup.py`, `Pipfile` | Python | dependências |
| `go.mod` | Go | versão do Go, módulo, dependências |
| `Cargo.toml` | Rust | `[dependencies]`, `[workspace]` |
| `pom.xml`, `build.gradle(.kts)` | Java ou Kotlin | plugins, dependências, versão do JDK |
| `Gemfile` | Ruby | gems, versão do Ruby |
| `composer.json` | PHP | `require`, scripts |
| `*.csproj`, `*.sln` | .NET | `TargetFramework`, pacotes |
| `mix.exs` | Elixir | deps |
| `pubspec.yaml` | Dart ou Flutter | dependências |

Mais de um manifesto na raiz costuma indicar projeto poliglota ou monorepo. Diga isso no relatório.

## Lockfile indica o gerenciador de pacotes

| Lockfile | Gerenciador |
|---|---|
| `package-lock.json` | npm |
| `yarn.lock` | yarn |
| `pnpm-lock.yaml` | pnpm |
| `bun.lockb` ou `bun.lock` | bun |
| `poetry.lock` | poetry |
| `uv.lock` | uv |
| `Pipfile.lock` | pipenv |
| `Cargo.lock` | cargo |
| `go.sum` | go modules |
| `Gemfile.lock` | bundler |
| `composer.lock` | composer |

Se houver mais de um lockfile do mesmo ecossistema, registre o conflito em "Lacunas" e não escolha um.

## Versões fixadas

`.nvmrc`, `.node-version`, `.python-version`, `.ruby-version`, `.tool-versions`, `rust-toolchain(.toml)`, o campo `engines` do `package.json` e `requires-python` do `pyproject.toml`.

## Frameworks: pista pelas dependências

Procure o nome nas dependências declaradas, e não pelo nome de pastas. Exemplos do que costuma aparecer: frameworks web, de testes, de ORM, de UI. Cite o pacote e a versão como estão no manifesto.

| Pista | Indica |
|---|---|
| `next.config.*`, `nuxt.config.*`, `vite.config.*`, `angular.json` | Framework ou bundler de front-end |
| `manage.py`, `settings.py` | Django |
| `app/`, `config/routes.rb` | Rails |
| `Dockerfile`, `docker-compose*.yml` | Roda em contêiner, com serviços auxiliares |
| `prisma/`, `alembic/`, `migrations/` | Banco com migrações |
| `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile` | CI configurado |
| `terraform/`, `*.tf`, `k8s/`, `helm/` | Infraestrutura como código |

## Monorepo

Sinais: `workspaces` no `package.json`, `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `go.work`, `[workspace]` no `Cargo.toml`, pastas `packages/` ou `apps/`.

No relatório, liste cada pacote ou app relevante com seu papel, e diga qual comando vale para a raiz e qual vale para cada pacote.

## Projeto sem código

Nem todo repo tem manifesto. Um repo só de documentação, de configuração ou de plugin (agentes, skills, prompts) não tem stack de execução. Nesse caso escreva `não encontrado` em linguagens e gerenciador, e descreva a estrutura e as convenções do que existe (por exemplo, pastas de agentes e skills, formato dos arquivos).

## Cuidados

- Um manifesto ausente não prova que a linguagem não é usada. Confira a extensão dos arquivos antes de concluir.
- Dependência listada não prova que é usada. Para decidir o framework principal, olhe o ponto de entrada ou a configuração.
- Não reporte versão "provável". Sem versão fixada, escreva `não fixada`.
