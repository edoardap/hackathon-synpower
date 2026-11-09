---
name: synchro-gitlab-ci-pipeline
description: Cria, revisa ou corrige pipelines .gitlab-ci.yml de projetos Synchro / ia_produtos compondo o Catálogo de Componentes CI/CD interno da organização (ia_produtos/ci-catalog, devsecops) em vez de escrever a lógica do pipeline do zero. Use esta skill sempre que alguém pedir para iniciar o CI de um projeto novo, adicionar ou auditar stages do pipeline (security, code-checks, tests, sast, docker-build, release), configurar a validação do título de merge request, SBOM/Dependency-Track, Renovate, QA Python com uv (lint, format, pytest, import-linter, uv-lock, sonarqube), builds Docker de múltiplas imagens, criação de tags Git, automação de changelog/release ou publicação de um SDK Python gerado a partir de uma spec OpenAPI — mesmo que a pessoa diga apenas "configure o CI" ou cole um .gitlab-ci.yml existente pedindo alterações, sem citar esta skill ou o catálogo explicitamente.
---

# Synchro GitLab CI Pipeline (v2 — Português)

## Visão Geral

Os projetos do grupo GitLab `ia_produtos` não montam seus pipelines manualmente. Todo `.gitlab-ci.yml` é uma
composição de um **Catálogo de Componentes CI/CD** compartilhado (`ia_produtos/ci-catalog/*`, mais alguns componentes
`devsecops/*`) incluído via `include: component:`, acrescida de um pequeno conjunto consistente de jobs escritos no
próprio projeto (validação do título do MR, drift checks, publicação de SDK). É por isso que os pipelines de
`ai-agents`, `data-pipeline-orchestrator`, `ai-tools` e repositórios semelhantes são quase idênticos: os mesmos
stages, os mesmos nomes de jobs ocultos, a mesma ordem de jobs.

Criar um novo pipeline significa **reaproveitar esse formato**, não desenhar um novo. Isso mantém a varredura de
segurança, o QA Python, a geração de SBOM, os builds Docker e os releases consistentes em toda a organização, e faz
com que o projeto se beneficie automaticamente quando o catálogo é atualizado (basta alterar uma variável de versão
em vez de mexer em cada repositório).

## Quando Usar Esta Skill

- Iniciar o `.gitlab-ci.yml` de um projeto `ia_produtos` totalmente novo (Python + `uv`, FastAPI, Dagster, servidor
  MCP etc.).
- Adicionar um stage/job que falta em um pipeline existente (ex.: "precisamos de build de imagens Docker" ou
  "adicione o relatório de SBOM").
- Revisar ou depurar um pipeline com aparência de escrito à mão, para trazê-lo de volta ao padrão compartilhado.
- Adicionar jobs específicos do projeto que devem seguir o estilo da casa: validação do título do MR, jobs de
  "drift check" que verificam se um artefato gerado está atualizado (spec OpenAPI, manifests Kubernetes, arquivos de
  Docker Compose) ou publicação de um SDK Python versionado a partir de um contrato OpenAPI.

## Formato do Pipeline (Ordem dos Stages)

Mantenha os stages nesta ordem. Nem todo projeto precisa de todos os stages — remova o que realmente não se aplica,
mas nunca reordene o que ficar, pois os `needs:`/`rules:` dos jobs do catálogo assumem essa sequência.

| # | Stage | Finalidade |
|---|---|---|
| 1 | `security` | Varredura de secrets, varredura de IaC, geração de SBOM, automação de atualização de dependências. Roda primeiro e é majoritariamente consultivo (`allow_failure: true`) para nunca bloquear o feedback rápido. |
| 2 | `code-checks` | Tudo que pode falhar rápido sem rodar a suíte de testes: convenção de título do MR, lint, format, markdown-lint, fronteiras de import, atualização do lockfile, lint de Dockerfile e quaisquer "drift checks" específicos do projeto (artefato gerado está atualizado). |
| 3 | `tests` | `pytest` (e a análise do SonarQube, que precisa da saída de testes/cobertura). |
| 4 | `sast` | Reservado para testes estáticos de segurança de aplicação (SAST). Mantenha o stage mesmo que nenhum job o utilize hoje, para que um componente de SAST possa ser adicionado depois sem reorganizar o arquivo. |
| 5 | `ai-code-review` | Opcional. Inclua este stage apenas se o projeto já adotou revisão assistida por IA; caso contrário, omita-o em vez de deixar um stage vazio "por simetria". |
| 6 | `tag` | Criação automática de tag Git que dispara o fluxo de release. |
| 7 | `docker-build` | Constrói e publica todas as imagens de container que o projeto entrega. |
| 8 | `release` | Geração de changelog, criação do GitLab Release e (se aplicável) publicação do SDK. |

## Passo a Passo: Criando um Novo Pipeline

1. **Parta do template.** Copie `assets/gitlab-ci.template.yml` para o `.gitlab-ci.yml` do projeto em vez de escrever
   a partir de um arquivo em branco — ele já traz o `include:`, a ordem de stages e os jobs ocultos base corretos.

2. **Confirme o que o projeto realmente tem** antes de ligar os jobs: um projeto Python gerenciado com `uv`? Um ou
   mais Dockerfiles? Uma spec OpenAPI versionada mais uma CLI que a regenera? Manifests Kubernetes ou arquivos Docker
   Compose derivados de configuração? Um `renovate.json`? Isso determina quais jobs opcionais abaixo se aplicam.

3. **Mantenha as versões do `include:` como variáveis, nunca fixas.** Todo componente é fixado com
   `@${ALGUMA_VERSAO_DO_COMPONENTE}` (ex.: `${PYTHON_QA_VERSION}`, `${RELEASE_COMPONENT_VERSION}`). Essas variáveis
   são definidas centralmente (nível de grupo/instância) — um projeto novo apenas as referencia, não cria novos pins
   de versão.

4. **Defina `UV_CACHE_DIR` / `UV_PROJECT_ENVIRONMENT`** em caminhos locais ao projeto (`$CI_PROJECT_DIR/.uv-cache`,
   `$CI_PROJECT_DIR/.venv`) para que o `uv` faça cache corretamente no CI.

5. **Configure o stage `security`**: `gitleaks` e `checkov` só precisam de overrides com `allow_failure: true`;
   `sbom` precisa de `CDXGEN_TARGET_DIRECTORY` (normalmente `"src"`) e das variáveis de identidade `DTRACK_PROJECT_*`
   com o nome/grupo do próprio projeto; `renovate` precisa de `renovate_config_path` apontando para o
   `renovate.json` do projeto. Veja `references/components.md` para os campos exatos.

6. **Configure o stage `code-checks`**:
   - `validate-mr-title`, `lint`, `format`, `markdown-lint`, `import-linter`, `uv-lock-check`, `dockerfile-lint` são
     padrão em todos os projetos — adicione-os como estão (veja `references/components.md` e
     `references/custom-jobs.md` para o corpo exato de cada job).
   - Se o projeto versiona um **artefato gerado** que precisa permanecer sincronizado com o código-fonte (spec
     OpenAPI, manifests Kubernetes, configuração de Docker Compose/daemon), adicione um job de drift check dedicado
     seguindo o padrão de `references/custom-jobs.md`. Restrinja o `rules: changes:` aos caminhos de origem exatos
     que tornariam o artefato desatualizado e rode-o também incondicionalmente em `main`/`dev`, para que o drift
     nunca seja mergeado silenciosamente.

7. **Configure o stage `tests`**: `pytest`, mais `sonarqube` assim que houver saída de cobertura.

8. **Configure o stage `docker-build`**: uma entrada de `parallel: matrix` por imagem construída (uma por
   Dockerfile, ou por build target em Dockerfiles multi-stage), duplicada entre `docker-build-dev` (pushes em
   branches) e `docker-build-release` (tags). Defina `DOCKER_BUILD_USE_GITLAB_TOKEN: "true"` somente para imagens
   cujo build precise baixar pacotes privados hospedados no GitLab; caso contrário, `"false"`.

9. **Configure `tag` e `release`**: `create-tag`, `generate-changelog`, `create-release` (os dois últimos com
   `needs: [{job: generate-changelog, artifacts: true}]`). Adicione `publish-python-sdk` apenas quando o projeto
   expuser um contrato OpenAPI versionado destinado a consumidores de SDK externos/internos — veja
   `references/custom-jobs.md` para o job completo.

10. **Valide a pertinência dos stages**: o `stage:` de cada job deve ser um da tabela acima, e as `rules:` devem
    reaproveitar o padrão compartilhado "merge request OU main/dev OU tag OU pipeline agendado"
    (`references/components.md` o descreve como `.standard-rules`), a menos que o job tenha um gatilho mais
    restrito e intencional (como uma guarda `changes:`).

11. **Aplique as regras de escrita** da seção "Regras Obrigatórias para o `.gitlab-ci.yml` Gerado": sem comentários
    de marcação de seção e com todas as mensagens de `echo` em português.

## Componentes CI/CD Conhecidos

As notas completas de finalidade/uso, as entradas `include:` exatas e os inputs aceitos por cada componente estão em
`references/components.md`. Leia-o antes de adicionar ou modificar qualquer bloco `include:`. Resumindo, os
componentes se dividem em três famílias:

- **`devsecops/*`** — detecção de secrets (`gitleaks`), varredura de IaC (`checkov-iac`), geração de SBOM (`cdxgen`).
- **`ia_produtos/ci-catalog/python-qa/*`** — configuração do toolchain `uv`, `rules` compartilhadas de jobs,
  lint/format/markdown/Dockerfile, `pytest`, `import-linter`, atualização do `uv.lock` e relatório do SonarQube.
- **`ia_produtos/ci-catalog/release/*`** e **`renovate/renovate`** — builds de imagens Docker, criação de tags Git,
  changelog + GitLab Release e merge requests automáticos de atualização de dependências.

## Jobs Escritos no Projeto (Fora do Catálogo)

Alguns jobs são escritos diretamente no `.gitlab-ci.yml` de cada projeto porque codificam regras específicas do
projeto ou da organização, e não comportamento genérico de CI/QA:

- **`validate-mr-title`** — impõe a convenção de título de merge request `[Tag] Descrição com inicial maiúscula`.
- **jobs de drift check** (`openapi-check`, `*-k8s-check`, `*-docker-check`, …) — regeneram um artefato versionado e
  falham o pipeline se ele diferir do que está commitado.
- **`publish-python-sdk`** — gera um SDK Python a partir da spec OpenAPI do projeto, faz o build, executa um smoke
  test e o publica no GitLab Package Registry em tags.

Os corpos completos, prontos para adaptar, dos três estão em `references/custom-jobs.md`.

## Regras Obrigatórias para o `.gitlab-ci.yml` Gerado

Estas regras valem para todo arquivo criado ou alterado por esta skill e têm precedência sobre qualquer exemplo que
pareça contradizê-las.

1. **Proibido comentário de marcação/separação.** Nunca gere comentários decorativos que apenas rotulem ou dividam
   seções, como `# --- stage security ----------`, `# ==== tests ====`, `# ##### docker #####` ou variações. O próprio
   `stage:` e o nome do job já indicam a seção; separe blocos apenas com uma linha em branco.
   - Só mantenha um comentário quando ele explicar algo **não óbvio** (ex.: por que um job é `allow_failure: true`) e
     seja curto, em linha própria.
   - Os comentários de instrução do template (cabeçalho "Ponto de partida...", blocos `# <artefato>-check:` e
     `# publish-python-sdk:` comentados, `# - ai-code-review`) servem apenas de guia para quem aplica a skill: ao
     criar o arquivo final, resolva-os (descomente e preencha o que se aplica) e **remova** o restante. Não os copie
     para o `.gitlab-ci.yml` do projeto.

2. **Toda mensagem de `echo` deve estar em português do Brasil.** Isso inclui mensagens de progresso, sucesso, erro e
   dicas de correção, em jobs novos e nos copiados de `references/custom-jobs.md`. Exemplos:
   - ✅ `echo "Validando a spec OpenAPI..."` — ❌ `echo "Validating OpenAPI spec..."`
   - ✅ `echo "❌ Erro: Título do Merge Request não encontrado."` — ❌ `echo "Error: MR title not found."`
   - Mantenha em inglês apenas literais técnicos (nomes de comandos, flags, variáveis, caminhos, nomes de
     ferramentas), como em `Execute 'make api-specs' localmente`.
   - Ao revisar um pipeline existente, traduza também os `echo` em inglês que encontrar.

## Checklist Antes de Abrir o MR

- [ ] Nenhum comentário de marcação/separação de seção (`# --- stage ... ---`) no arquivo, e nenhum comentário de
      instrução do template sobrando.
- [ ] Todas as mensagens de `echo` estão em português do Brasil.
- [ ] O `include:` apenas adiciona componentes, sem reimplementação própria do que um componente já fornece.
- [ ] A lista de stages segue a ordem canônica; nenhum stage declarado sem ao menos um job (exceto `sast`, que é
      reservado intencionalmente).
- [ ] Os jobs do stage `security` são consultivos (`allow_failure: true`), a menos que o projeto queira
      explicitamente bloquear por eles.
- [ ] A matrix de cada job `docker-build-*` cobre todos os Dockerfiles que o projeto entrega, com
      `BUILD_CONTEXT`/`BUILD_TARGET` corretos.
- [ ] Todo artefato gerado e versionado tem um job de drift check correspondente.
- [ ] As variáveis de versão (`${PYTHON_QA_VERSION}`, `${RELEASE_COMPONENT_VERSION}` etc.) são referenciadas, nunca
      fixadas em uma tag específica.
