# Jobs Escritos no Projeto

Estes jobs não vêm do catálogo — são escritos diretamente no `.gitlab-ci.yml` de cada projeto porque codificam regras
específicas do modo de trabalho desta organização (higiene de merge requests, manter artefatos gerados em sincronia,
publicar um SDK). Reaproveite-os literalmente (ou quase) para que todo projeto imponha as mesmas convenções.

## `validate-mr-title`

Garante que todo título de merge request comece com uma tag de um conjunto fixo entre colchetes, seguida de uma
descrição com inicial maiúscula — ex.: `[Feature] Adicionar endpoint de artifacts`. Roda em `code-checks`, apenas em
pipelines de merge request, e não pode falhar silenciosamente (`allow_failure: false`).

```yaml
validate-mr-title:
  stage: code-checks
  image: registry.synchro.com.br/library/alpine:latest
  allow_failure: false
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      when: on_success
    - when: never
  script:
    - |
      TITLE="${CI_MERGE_REQUEST_TITLE:-}"
      VALID_TAGS="Breaking|Feature|Fix|Refactor|Chore|Spike|Docs|Test"

      if [ -z "$TITLE" ]; then
        echo "❌ Erro: Título do Merge Request não encontrado (variável vazia)."
        exit 1
      fi

      # Valida apenas se a Tag existe e está no formato correto
      if ! echo "$TITLE" | grep -Eq "^\[($VALID_TAGS)\] "; then
        echo "❌ Erro: O título do MR usa uma tag inválida ou ausente."
        echo "   Tags aceitas: $VALID_TAGS"
        echo "   Exemplo válido: [Feature] Adicionar endpoint de artifacts"
        exit 1
      fi

      # Valida se a primeira letra após a Tag é maiúscula
      if ! echo "$TITLE" | grep -Eq "^\[($VALID_TAGS)\] [A-Z]"; then
        echo "❌ Erro: A descrição do título deve começar com letra maiúscula."
        echo "   Exemplo válido: [Refactor] Ajustar validação do pipeline"
        echo "   Exemplo inválido: [Refactor] ajustar validação do pipeline"
        exit 1
      fi

      echo "✅ Título do MR validado com sucesso: $TITLE"
```

Alguns projetos também removem um prefixo `Draft: ` no início antes de validar, para que MRs em rascunho não sejam
rejeitados apenas por causa do prefixo:

```sh
TITLE="$(printf '%s\n' "$TITLE" | sed -E 's/^[Dd][Rr][Aa][Ff][Tt]: //')"
```

Mantenha a lista de tags válidas (`Breaking|Feature|Fix|Refactor|Chore|Spike|Docs|Test`) idêntica em todos os
projetos — é uma convenção compartilhada, não algo a customizar por repositório.

## Jobs de drift check (artefato gerado deve bater com o código-fonte)

Padrão usado sempre que um projeto versiona um arquivo *gerado* a partir do código-fonte (spec OpenAPI, manifests
Kubernetes derivados de configuração, configuração de Docker Compose/daemon) e que nunca deve ficar desatualizado. O
job regenera o artefato e falha o pipeline se a versão regenerada diferir do que está commitado.

```yaml
<job-name>-check:
  extends:
    - .base-uv-full
  stage: code-checks
  allow_failure: false
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      changes:
        - "<todo caminho de origem que possa tornar o artefato desatualizado>"
      when: on_success
    - if: '$CI_COMMIT_BRANCH == "main" || $CI_COMMIT_BRANCH == "dev"'
      when: always
    - when: never
  script:
    - PYTHONPATH=./src/ uv run python -m cli.main <comando que regenera ou verifica o artefato>
```

Dois formatos concretos vistos na prática:

- **Regenerar e comparar** (usado em `openapi-check`): executa o gerador e falha se o `git diff` não estiver vazio.

  ```yaml
  openapi-check:
    extends:
      - .base-uv-full
    stage: code-checks
    allow_failure: false
    rules:
      - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
        changes:
          - ".gitlab-ci.yml"
          - "Makefile"
          - "src/cli/commands/openapi.py"
          - "src/api/**/*"
          - "src/shared/schemas/**/*"
          - "docs/api/openapi.yaml"
          - "pyproject.toml"
          - "uv.lock"
        when: on_success
      - when: never
    script:
      - apt-get update && apt-get install -y git
      - PYTHONPATH=./src/ uv run python -m cli.main openapi generate -o docs/api/openapi.yaml -f yaml
      - |
        if ! git diff --quiet -- docs/api/openapi.yaml; then
          echo ""
          echo "❌ O arquivo docs/api/openapi.yaml está desatualizado."
          echo "   Execute 'make api-specs' localmente, commite o arquivo atualizado e rode o pipeline novamente."
          exit 1
        fi
      - echo "✅ docs/api/openapi.yaml está atualizado."
  ```

- **Comando de verificação dedicado** (usado em `api-k8s-check`, `data-pipelines-k8s-check`,
  `data-pipelines-docker-check`): a própria CLI do projeto faz a comparação internamente.

  ```yaml
  api-k8s-check:
    extends:
      - .base-uv-full
    stage: code-checks
    allow_failure: false
    rules:
      - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
        changes:
          - "src/api/config.py"
          - "src/shared/config/**/*.py"
          - "infra/api/dev/**/*.yaml"
          - ".env.example"
        when: on_success
      - if: '$CI_COMMIT_BRANCH == "main" || $CI_COMMIT_BRANCH == "dev"'
        when: always
      - when: never
    script:
      - PYTHONPATH=./src/ uv run python -m cli.main api check-k8s
  ```

Ao adicionar um desses para um projeto novo, restrinja o `changes:` exatamente aos arquivos de origem que alimentam o
artefato gerado (módulos de configuração, arquivos de schema, manifests de infra), para que o job rode somente quando
puder de fato detectar drift, mas rode-o sempre também de forma incondicional em `main`/`dev` como rede de segurança.

## `publish-python-sdk`

Gera um SDK Python a partir da spec OpenAPI versionada do projeto, faz o build, executa um smoke test no wheel
construído e o publica no GitLab Package Registry. Só adicione este job se o projeto expuser um contrato OpenAPI
versionado destinado a consumidores de SDK. Roda apenas em tags, após o build das imagens Docker de release.

```yaml
publish-python-sdk:
  extends: .base-uv-full
  stage: release
  needs:
    - job: docker-build-release
      artifacts: false
  rules:
    - if: $CI_COMMIT_TAG
      when: on_success
    - when: never
  variables:
    PYTHONPATH: "./src/"
    UV_PUBLISH_USERNAME: "gitlab-ci-token"
    UV_PUBLISH_PASSWORD: "$CI_JOB_TOKEN"
  script:
    - export SDK_VERSION="${CI_COMMIT_TAG#v}"

    - echo "Validating OpenAPI spec..."
    - uv run python -m cli.main sdk validate -i docs/api/openapi.yaml

    - echo "Generating Python SDK..."
    - uv run python -m cli.main sdk generate-python --version "$SDK_VERSION"

    - echo "Building SDK..."
    - uv build --project .generated/sdk/python --clear

    - echo "Running smoke test..."
    - uv run --no-project --with .generated/sdk/python/dist/*.whl python -m cli.commands.sdk smoke-python --expected-version "$SDK_VERSION"

    - echo "Publishing to GitLab Package Registry..."
    - >
      uv publish .generated/sdk/python/dist/*
      --publish-url "$CI_API_V4_URL/projects/$CI_PROJECT_ID/packages/pypi"
      --check-url "$CI_API_V4_URL/projects/$CI_PROJECT_ID/packages/pypi/simple"
      --no-attestations
      --trusted-publishing never
  artifacts:
    paths:
      - .generated/sdk/python/dist/
    expire_in: 1 month
```

Este job pressupõe que a CLI do projeto (`cli.main sdk validate` / `sdk generate-python`) já sabe transformar a spec
OpenAPI em um pacote Python em `.generated/sdk/python` — esse gerador é código do projeto, não faz parte deste padrão
de pipeline.
