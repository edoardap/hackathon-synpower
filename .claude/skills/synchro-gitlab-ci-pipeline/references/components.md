# Catálogo de Componentes CI/CD

Cada entrada abaixo é incluída via `include: component: $CI_SERVER_FQDN/<caminho>@${VAR_DE_VERSAO}`.
`$CI_SERVER_FQDN` resolve para a instância GitLab da organização, então o mesmo bloco `include:` funciona sem
alterações em todos os projetos. Nunca fixe uma string de versão no lugar de `${VAR_DE_VERSAO}` — a variável já está
definida onde o pipeline roda, e atualizá-la centralmente é como todos os projetos recebem as atualizações do
catálogo de uma só vez.

## Bloco `include:` (copie como ponto de partida)

```yaml
include:
  - component: $CI_SERVER_FQDN/devsecops/secret-detection/gitleaks@${SECRET_DETECTION_COMPONENT_VERSION}
  - component: $CI_SERVER_FQDN/devsecops/checkov-iac/checkov-iac@${CHECKOV_IAC_COMPONENT_VERSION}
  - component: $CI_SERVER_FQDN/devsecops/cdxgen/cdxgen@${CDXGEN_IAC_COMPONENT_VERSION}
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/renovate/renovate@${RENOVATE_COMPONENT_VERSION}
    inputs:
      stage: security
      renovate_config_path: renovate.json
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/python-qa/uv@${PYTHON_QA_VERSION}
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/python-qa/rules@${PYTHON_QA_VERSION}
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/python-qa/lint@${PYTHON_QA_VERSION}
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/python-qa/test@${PYTHON_QA_VERSION}
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/python-qa/import-linter@${PYTHON_QA_VERSION}
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/python-qa/uv-lock@${PYTHON_QA_VERSION}
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/python-qa/sonarqube@${PYTHON_QA_VERSION}
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/release/base-docker@${RELEASE_COMPONENT_VERSION}
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/release/docker-build@${RELEASE_COMPONENT_VERSION}
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/release/git-tag@${RELEASE_COMPONENT_VERSION}
  - component: $CI_SERVER_FQDN/ia_produtos/ci-catalog/release/release@${RELEASE_COMPONENT_VERSION}
```

Mantenha esta ordem: componentes de segurança/SAST primeiro, depois QA Python, depois release/Docker. Ela espelha a
ordem dos stages e facilita a leitura do arquivo.

## Componentes `devsecops/*`

### `secret-detection/gitleaks`
- **Finalidade**: varre o histórico/árvore de trabalho do repositório em busca de secrets e credenciais hardcoded.
- **Job produzido**: `gitleaks`.
- **Quando usar**: em todo projeto, sem exceções.
- **Como é usado na prática**: posicionado no stage `security`; sobrescreva com `allow_failure: true` para que um
  achado apareça como aviso a ser triado pelo time, em vez de bloquear o pipeline.

```yaml
gitleaks:
  allow_failure: true
```

### `checkov-iac/checkov-iac`
- **Finalidade**: varre definições de Infrastructure-as-Code (Dockerfiles, manifests Kubernetes, Terraform etc.) em
  busca de más configurações.
- **Job produzido**: `checkov`.
- **Quando usar**: qualquer projeto que entregue `docker/`, `infra/` ou arquivos IaC semelhantes — o que, na prática,
  é quase todo projeto.
- **Como é usado na prática**: mesmo tratamento consultivo do `gitleaks`.

```yaml
checkov:
  allow_failure: true
```

### `cdxgen/cdxgen`
- **Finalidade**: gera um Software Bill of Materials (SBOM) CycloneDX da árvore de código-fonte do projeto e, quando
  o rastreamento de dependências está habilitado, o envia ao Dependency-Track da organização sob um determinado
  projeto/grupo/versão.
- **Job produzido**: estenda `.generate_source_sbom_template` em um job chamado `sbom`.
- **Quando usar**: em todo projeto com uma árvore `src/`.
- **Inputs a definir**:
  - `CDXGEN_TARGET_DIRECTORY`: a pasta de código a varrer (normalmente `"src"`).
  - `ENABLE_DEPENDENCY_TRACK`: `true` para publicar no Dependency-Track.
  - `DTRACK_PROJECT_GROUP`: o grupo organizacional (ex.: `"IA Produtos"`).
  - `DTRACK_PROJECT_NAME`: o nome do próprio projeto (igual ao nome do repositório).
  - `DTRACK_PROJECT_VERSION`: `"$CI_COMMIT_REF_NAME"`, para que cada branch/tag tenha sua própria versão rastreada.
  - `DTRACK_PROJECT_PARENT_NAME`: o agrupamento pai no Dependency-Track (ex.: `"IA_Produtos"`).

```yaml
sbom:
  extends: .generate_source_sbom_template
  stage: security
  variables:
    CDXGEN_TARGET_DIRECTORY: "src"
    ENABLE_DEPENDENCY_TRACK: true
    DTRACK_PROJECT_GROUP: "IA Produtos"
    DTRACK_PROJECT_NAME: "<project-name>"
    DTRACK_PROJECT_VERSION: "$CI_COMMIT_REF_NAME"
    DTRACK_PROJECT_PARENT_NAME: "IA_Produtos"
```

## `ia_produtos/ci-catalog/renovate/renovate`
- **Finalidade**: executa o Renovate para abrir merge requests automáticos de atualização de dependências com base
  no arquivo de configuração do próprio projeto.
- **Job produzido**: estenda `.renovate-job` em um job chamado `renovate`.
- **Quando usar**: qualquer projeto que queira bumps de dependência automatizados em vez de manuais — padrão em toda
  a organização.
- **Inputs a definir** (no momento do include, não por job): `stage: security`,
  `renovate_config_path: renovate.json` (ou onde estiver a configuração do Renovate do projeto).

```yaml
renovate:
  extends: .renovate-job
```

## `ia_produtos/ci-catalog/python-qa/*`

Estes componentes fornecem o toolchain compartilhado de "QA Python" para projetos gerenciados com `uv`.

### `uv`
- **Finalidade**: provisiona a configuração compartilhada de ambiente/cache Python baseada em `uv`, sobre a qual os
  demais jobs de QA Python se apoiam.
- **Quando usar**: qualquer projeto Python gerenciado com `uv` (ou seja, praticamente todos os projetos atuais).

### `rules`
- **Finalidade**: fornece as condições de disparo compartilhadas dos jobs de QA Python — rodar nas branches
  `main`/`dev`, em merge requests, em tags e em pipelines agendados; caso contrário, pular. É o equivalente, no
  nível do catálogo, do job oculto local `.standard-rules` que alguns projetos ainda definem para seus próprios jobs.
- **Quando usar**: deixe os jobs de QA Python herdarem estas regras em vez de redefinir as mesmas quatro condições à
  mão em cada projeto.

```yaml
.standard-rules:
  rules:
    - if: '$CI_COMMIT_BRANCH == "main" || $CI_COMMIT_BRANCH == "dev"'
      when: on_success
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      when: on_success
    - if: '$CI_COMMIT_TAG'
      when: on_success
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
      when: on_success
    - when: never
```

### `lint`
- **Finalidade**: fornece os jobs de qualidade de código de um projeto Python: lint (`lint`), verificação de
  formatação (`format`), estilo de Markdown (`markdown-lint`) e estilo de Dockerfile (`dockerfile-lint`).
- **Jobs produzidos**: estenda `.lint-job`, `.format-job`, `.markdown-lint-job`, `.dockerfile-lint-job` como `lint`,
  `format`, `markdown-lint`, `dockerfile-lint`, respectivamente, todos no stage `code-checks`.
- **Quando usar**: todo projeto Python. Restrinja o `dockerfile-lint` para rodar apenas quando Dockerfiles mudarem
  na `dev`:

```yaml
lint:
  extends: .lint-job

format:
  extends: .format-job

markdown-lint:
  extends: .markdown-lint-job

dockerfile-lint:
  extends: .dockerfile-lint-job
  rules:
    - if: '$CI_COMMIT_BRANCH == "dev"'
      changes:
        - "docker/**/*.Dockerfile"
      when: on_success
```

### `test`
- **Finalidade**: executa a suíte `pytest` do projeto.
- **Job produzido**: estenda `.pytest-job` como `pytest`, no stage `tests`.
- **Quando usar**: todo projeto Python com suíte de testes.

```yaml
pytest:
  extends: .pytest-job
```

### `import-linter`
- **Finalidade**: impõe as fronteiras arquiteturais de import do projeto (ex.: routers só podem depender de
  services, services só podem depender de repositories), conforme declarado na configuração do `import-linter` do
  projeto.
- **Job produzido**: estenda `.import-linter-job` como `import-linter`, no stage `code-checks`.
- **Quando usar**: qualquer projeto com fronteiras de arquitetura em camadas que não devem ser violadas por código
  novo.

```yaml
import-linter:
  extends: .import-linter-job
```

### `uv-lock`
- **Finalidade**: verifica se o `uv.lock` está commitado e sincronizado com o `pyproject.toml`, pegando o caso em
  que alguém alterou dependências sem refazer o lock.
- **Job produzido**: estenda `.uv-lock-check-job` como `uv-lock-check`, no stage `code-checks`.
- **Quando usar**: todo projeto gerenciado com `uv`.

```yaml
uv-lock-check:
  extends: .uv-lock-check-job
```

### `sonarqube`
- **Finalidade**: envia os resultados de análise estática / cobertura ao servidor SonarQube da organização.
- **Job produzido**: estenda `.sonarqube-job` como `sonarqube`.
- **Quando usar**: todo projeto que deva aparecer nos dashboards de SonarQube da organização (na prática, todos);
  posicione-o após o `pytest` para que a saída de cobertura esteja disponível.

```yaml
sonarqube:
  extends: .sonarqube-job
```

## `ia_produtos/ci-catalog/release/*`

### `base-docker`
- **Finalidade**: fornece o ambiente compartilhado de build Docker-in-Docker (login no registry, configuração do
  runner de build) do qual o componente `docker-build` depende.
- **Quando usar**: inclua-o junto com `release/docker-build` sempre que o projeto construir imagens de container;
  ele não é usado diretamente como job, apenas como dependência dos demais componentes de release.

### `docker-build`
- **Finalidade**: constrói e publica uma ou mais imagens de container do projeto.
- **Jobs produzidos**: estenda `.docker-build-dev-job` como `docker-build-dev` (pushes em branches) e
  `.docker-build-release-job` como `docker-build-release` (tags).
- **Quando usar**: qualquer projeto que entregue imagens Docker, incluindo monorepos com várias imagens.
- **Como escalar para múltiplas imagens**: use `parallel: matrix` com uma entrada por imagem — `NAME` (nome da
  imagem), `DOCKERFILE` (caminho do Dockerfile), `BUILD_CONTEXT`, opcionalmente `BUILD_TARGET` para Dockerfiles
  multi-stage, e `DOCKER_BUILD_USE_GITLAB_TOKEN` (`"true"` somente quando o build daquela imagem precisar baixar
  pacotes privados hospedados no GitLab).

```yaml
docker-build-dev:
  extends: .docker-build-dev-job
  parallel:
    matrix:
      - NAME: api
        DOCKERFILE: "docker/api.Dockerfile"
        BUILD_CONTEXT: .
        DOCKER_BUILD_USE_GITLAB_TOKEN: "false"

docker-build-release:
  extends: .docker-build-release-job
  variables:
    TAG: "$CI_COMMIT_TAG"
  parallel:
    matrix:
      - NAME: api
        DOCKERFILE: "docker/api.Dockerfile"
        BUILD_CONTEXT: .
        DOCKER_BUILD_USE_GITLAB_TOKEN: "false"
```

### `git-tag`
- **Finalidade**: cria a tag Git que conduz o restante do fluxo de release.
- **Job produzido**: estenda `.create-tag-job` como `create-tag`, no stage `tag`.
- **Quando usar**: todo projeto que siga o fluxo de release orientado por tags (ou seja, todos).

```yaml
create-tag:
  extends: .create-tag-job
```

### `release`
- **Finalidade**: gera o changelog e publica o GitLab Release assim que uma tag existe.
- **Jobs produzidos**: estenda `.generate-changelog-job` como `generate-changelog` e `.create-release-job` como
  `create-release`, ambos no stage `release`.
- **Quando usar**: todo projeto com o fluxo de release orientado por tags.
- **Observação**: o `create-release` deve declarar `needs: [{job: generate-changelog, artifacts: true}]` para ter o
  changelog gerado disponível.

```yaml
generate-changelog:
  extends: .generate-changelog-job

create-release:
  extends: .create-release-job
  needs:
    - job: generate-changelog
      artifacts: true
```
