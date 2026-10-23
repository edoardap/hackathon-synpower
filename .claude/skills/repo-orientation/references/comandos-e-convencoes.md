# Comandos, convenções e armadilhas

Material de consulta para os passos "Comandos", "Convenções de código", "Commits e branches" e "Armadilhas". O relatório só leva o que o repo confirma. Esta skill **não executa** build, testes nem instalação.

## Onde achar cada comando

| Tarefa | Onde procurar |
|---|---|
| Instalar | `README`, `CONTRIBUTING`, `Makefile`, `Dockerfile`, passo de instalação no CI |
| Dev (rodar local) | `scripts` do `package.json` (`dev`, `start`), `Makefile`, `README`, `docker-compose` |
| Build | `scripts.build`, `Makefile`, `Dockerfile`, CI |
| Testes (todos) | `scripts.test`, `Makefile`, `tox.ini`, `pyproject.toml`, passo de teste no CI |
| Teste único | `README` ou `CONTRIBUTING` (o que o time documenta), documentação do runner de testes que aparece nas dependências |
| Lint e formatação | `scripts.lint` e `format`, `.pre-commit-config.yaml`, `Makefile`, CI |

Arquivos de tarefas: `Makefile`, `justfile`, `Taskfile.yml`, `tox.ini`, `noxfile.py`, `package.json`, `composer.json` (scripts), `Rakefile`.

### Regras

- Todo comando leva a coluna **Fonte** com o arquivo de onde veio.
- Se o CI e a documentação divergem, registre as duas versões e diga qual fonte é qual.
- Comando que o repo não declara fica `não encontrado`. Não preencha com o comando "padrão" do ecossistema. Se quiser sugerir, marque como `inferido` e diga por quê.
- Prefira o comando da raiz do projeto. Em monorepo, indique também o comando por pacote.

## Convenções de código

| Pergunta | Onde olhar |
|---|---|
| Lint e formatação | `.eslintrc*`, `eslint.config.*`, `.prettierrc*`, `ruff.toml`, `[tool.ruff]`, `[tool.black]`, `.editorconfig`, `rustfmt.toml`, `.golangci.yml` |
| Tipagem | `tsconfig.json` (modo `strict`), `mypy.ini`, `pyrightconfig.json` |
| Nome de arquivos | 2 ou 3 arquivos representativos de pastas diferentes |
| Imports | Os mesmos arquivos (caminho relativo, alias, ordem) |
| Onde ficam os testes | Pasta `tests/`, `__tests__/`, sufixo `.test.*` ou `_test.*`, ou ao lado do código |
| Como nomear os testes | 2 ou 3 testes existentes |

Descreva o que **existe**, e não o que seria ideal. Se a configuração e o código divergem (regra existe, mas ninguém segue), diga.

## Commits e branches

| Pergunta | Onde olhar |
|---|---|
| Padrão de mensagem | `git log --oneline -20` |
| Regra formal | `commitlint.config.*`, `CONTRIBUTING`, `AGENTS.md`, `CLAUDE.md` |
| Hooks | `.husky/`, `.pre-commit-config.yaml`, `.git/hooks/` (só os que não são `.sample`) |
| Modelo de PR e de issue | `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/` |
| Branch principal e nomes | `git branch -a`, `CONTRIBUTING`, regras no CI |

Padrões comuns de mensagem para reconhecer: Conventional Commits (`feat:`, `fix:`, `docs:`), prefixo de ticket (`ABC-123`), mensagens livres. Cite 2 ou 3 exemplos reais do log.

## Armadilhas que valem registro

| Sinal | O que registrar |
|---|---|
| `.env.example`, `.env.sample` | Variáveis de ambiente exigidas (só os **nomes**, nunca valores) |
| `docker-compose*.yml`, `Dockerfile` | Serviços externos que precisam estar de pé (banco, fila, cache) |
| Pastas `dist/`, `build/`, `generated/`, `*.pb.go`, cabeçalho "DO NOT EDIT" | Código gerado que não se edita à mão |
| `.gitignore`, `.dockerignore` | Pastas que ficam fora do controle de versão |
| `.github/workflows/` com etapas que o local não roda | O que só o CI verifica |
| Submódulos (`.gitmodules`) | Dependência de outro repositório |
| Versão de runtime exigida | Que quebra se o ambiente for diferente |

## Segurança ao ler

- Não imprima segredos. Se achar chave, token ou senha em arquivo versionado, registre **onde** está, sem copiar o valor, e sinalize em "Armadilhas".
- Leia `.env.example`, nunca `.env`.
- Não rode comandos que alterem estado (instalar, migrar, buildar) sem o usuário pedir.

## Lacunas

Tudo o que não deu para confirmar entra em "Lacunas" com o motivo: arquivo ausente, comando só em documentação desatualizada, CI e docs divergentes, repo sem testes. Isso é mais útil para o agente seguinte do que uma resposta chutada.
