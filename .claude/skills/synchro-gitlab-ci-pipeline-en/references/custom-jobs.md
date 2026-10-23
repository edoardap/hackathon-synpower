# Project-Authored Jobs

These jobs are not provided by the catalog — they are written directly into each project's `.gitlab-ci.yml` because
they encode rules specific to how this organization works (merge request hygiene, keeping generated artifacts in
sync, publishing an SDK). Reuse them verbatim (or close to it) so every project enforces the same conventions.

## `validate-mr-title`

Enforces that every merge request title starts with one of a fixed set of tags in brackets, followed by a
capitalized description — e.g. `[Feature] Add artifact endpoint`. Runs in `code-checks`, only on merge request
pipelines, and is not allowed to fail silently (`allow_failure: false`).

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

Some projects also strip a leading `Draft: ` prefix before validating, so draft MRs aren't rejected for the prefix
itself:

```sh
TITLE="$(printf '%s\n' "$TITLE" | sed -E 's/^[Dd][Rr][Aa][Ff][Tt]: //')"
```

Keep the valid-tags list (`Breaking|Feature|Fix|Refactor|Chore|Spike|Docs|Test`) identical across projects — it is a
shared convention, not something to customize per repo.

## Drift-check jobs (generated artifact must match source)

Pattern used whenever a project commits a file that is *generated* from source (an OpenAPI spec, Kubernetes
manifests derived from config, Docker Compose/daemon config) and must never go stale. The job regenerates the
artifact and fails the pipeline if the regenerated version differs from what's committed.

```yaml
<job-name>-check:
  extends:
    - .base-uv-full
  stage: code-checks
  allow_failure: false
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      changes:
        - "<every source path that could make the artifact stale>"
      when: on_success
    - if: '$CI_COMMIT_BRANCH == "main" || $CI_COMMIT_BRANCH == "dev"'
      when: always
    - when: never
  script:
    - PYTHONPATH=./src/ uv run python -m cli.main <command that regenerates or checks the artifact>
```

Two concrete shapes seen in practice:

- **Regenerate and diff** (used for `openapi-check`): run the generator, then fail if `git diff` is non-empty.

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

- **Dedicated check command** (used for `api-k8s-check`, `data-pipelines-k8s-check`, `data-pipelines-docker-check`):
  the project's own CLI performs the comparison internally.

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

When adding one of these for a new project, scope `changes:` to exactly the source files that feed the generated
artifact (config modules, schema files, infra manifests) so the job only runs when it could actually catch drift, but
always also run it unconditionally on `main`/`dev` as a safety net.

## `publish-python-sdk`

Generates a Python SDK from the project's committed OpenAPI spec, builds it, smoke-tests the built wheel, and
publishes it to the GitLab Package Registry. Only add this job if the project exposes a versioned OpenAPI contract
meant for SDK consumers. Runs only on tags, after the release Docker images are built.

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

This job assumes the project's CLI (`cli.main sdk validate` / `sdk generate-python`) already knows how to turn the
OpenAPI spec into a Python package under `.generated/sdk/python` — that generator is project code, not part of this
pipeline pattern.
