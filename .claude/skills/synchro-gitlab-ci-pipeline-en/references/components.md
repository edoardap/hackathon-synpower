# CI/CD Components Catalog

Every entry below is pulled in through `include: component: $CI_SERVER_FQDN/<path>@${VERSION_VAR}`. `$CI_SERVER_FQDN`
resolves to the organization's GitLab instance, so the same `include:` block works unchanged across projects. Never
hardcode a version string in place of `${VERSION_VAR}` — the variable is already defined where the pipeline runs, and
bumping it centrally is how every project picks up catalog updates at once.

## `include:` block (copy as a starting point)

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

Keep this order: security/SAST components first, then Python QA, then release/Docker. It mirrors the stage order and
makes the file easy to scan.

## `devsecops/*` components

### `secret-detection/gitleaks`
- **Purpose**: scans the repository history/working tree for hardcoded secrets and credentials.
- **Job produced**: `gitleaks`.
- **When to use**: on every project, with no exceptions.
- **How it's used in practice**: placed in the `security` stage; override it with `allow_failure: true` so a finding
  surfaces as a warning the team can triage instead of blocking the pipeline outright.

```yaml
gitleaks:
  allow_failure: true
```

### `checkov-iac/checkov-iac`
- **Purpose**: scans Infrastructure-as-Code definitions (Dockerfiles, Kubernetes manifests, Terraform, etc.) for
  misconfigurations.
- **Job produced**: `checkov`.
- **When to use**: any project that ships `docker/`, `infra/`, or similar IaC files — which in practice means almost
  every project.
- **How it's used in practice**: same advisory treatment as `gitleaks`.

```yaml
checkov:
  allow_failure: true
```

### `cdxgen/cdxgen`
- **Purpose**: generates a CycloneDX Software Bill of Materials (SBOM) for the project's source tree, and, when
  dependency tracking is enabled, uploads it to the organization's Dependency-Track instance under a given
  project/group/version.
- **Job produced**: extend `.generate_source_sbom_template` as a job named `sbom`.
- **When to use**: on every project with a `src/` tree.
- **Inputs to set**:
  - `CDXGEN_TARGET_DIRECTORY`: the source folder to scan (typically `"src"`).
  - `ENABLE_DEPENDENCY_TRACK`: `true` to publish to Dependency-Track.
  - `DTRACK_PROJECT_GROUP`: the organizational group (e.g. `"IA Produtos"`).
  - `DTRACK_PROJECT_NAME`: the project's own name (matches the repo name).
  - `DTRACK_PROJECT_VERSION`: `"$CI_COMMIT_REF_NAME"` so each branch/tag gets its own tracked version.
  - `DTRACK_PROJECT_PARENT_NAME`: the parent grouping in Dependency-Track (e.g. `"IA_Produtos"`).

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
- **Purpose**: runs Renovate to open automated dependency-update merge requests based on the project's own
  configuration file.
- **Job produced**: extend `.renovate-job` as a job named `renovate`.
- **When to use**: any project that wants automated dependency bumps instead of manual ones — standard across the
  fleet.
- **Inputs to set** (at include time, not per-job): `stage: security`, `renovate_config_path: renovate.json` (or
  wherever the project's Renovate config lives).

```yaml
renovate:
  extends: .renovate-job
```

## `ia_produtos/ci-catalog/python-qa/*`

These components provide the shared "Python QA" toolchain for `uv`-managed projects.

### `uv`
- **Purpose**: provisions the shared `uv`-based Python environment/cache setup that the rest of the Python QA jobs
  build on.
- **When to use**: any Python project managed with `uv` (i.e. essentially all current projects).

### `rules`
- **Purpose**: supplies the shared trigger conditions for Python QA jobs — run on `main`/`dev` branches, on merge
  requests, on tags, and on scheduled pipelines; otherwise skip. This is the catalog-level equivalent of the local
  `.standard-rules` hidden job some projects still define for their own custom jobs.
- **When to use**: let Python QA jobs inherit these rules rather than redefining the same four conditions by hand in
  every project.

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
- **Purpose**: provides the code-quality jobs for a Python project: linting (`lint`), formatting check (`format`),
  Markdown style (`markdown-lint`), and Dockerfile style (`dockerfile-lint`).
- **Jobs produced**: extend `.lint-job`, `.format-job`, `.markdown-lint-job`, `.dockerfile-lint-job` as `lint`,
  `format`, `markdown-lint`, `dockerfile-lint` respectively, all in the `code-checks` stage.
- **When to use**: every Python project. Scope `dockerfile-lint` to only run when Dockerfiles change on `dev`:

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
- **Purpose**: runs the project's `pytest` suite.
- **Job produced**: extend `.pytest-job` as `pytest`, in the `tests` stage.
- **When to use**: every Python project with a test suite.

```yaml
pytest:
  extends: .pytest-job
```

### `import-linter`
- **Purpose**: enforces the project's architectural import boundaries (e.g. routers may only depend on services,
  services may only depend on repositories), as declared in the project's `import-linter` configuration.
- **Job produced**: extend `.import-linter-job` as `import-linter`, in the `code-checks` stage.
- **When to use**: any project with layered architecture boundaries that must not be violated by new code.

```yaml
import-linter:
  extends: .import-linter-job
```

### `uv-lock`
- **Purpose**: verifies that `uv.lock` is committed and stays in sync with `pyproject.toml`, catching the case where
  someone edited dependencies without re-locking.
- **Job produced**: extend `.uv-lock-check-job` as `uv-lock-check`, in the `code-checks` stage.
- **When to use**: every `uv`-managed project.

```yaml
uv-lock-check:
  extends: .uv-lock-check-job
```

### `sonarqube`
- **Purpose**: pushes static analysis / coverage results to the organization's SonarQube server.
- **Job produced**: extend `.sonarqube-job` as `sonarqube`.
- **When to use**: every project that should show up in the org's SonarQube dashboards (in practice, all of them);
  place it after `pytest` so coverage output is available.

```yaml
sonarqube:
  extends: .sonarqube-job
```

## `ia_produtos/ci-catalog/release/*`

### `base-docker`
- **Purpose**: provides the shared Docker-in-Docker build environment (registry login, build runner wiring) that the
  `docker-build` component relies on.
- **When to use**: include it alongside `release/docker-build` any time the project builds container images; it is
  not used directly as a job, only as a dependency for the other release components.

### `docker-build`
- **Purpose**: builds and pushes one or more container images for the project.
- **Jobs produced**: extend `.docker-build-dev-job` as `docker-build-dev` (branch pushes) and
  `.docker-build-release-job` as `docker-build-release` (tags).
- **When to use**: any project that ships Docker images, including monorepos with several images.
- **How to scale to multiple images**: use `parallel: matrix` with one entry per image — `NAME` (image name),
  `DOCKERFILE` (path to the Dockerfile), `BUILD_CONTEXT`, optionally `BUILD_TARGET` for multi-stage Dockerfiles, and
  `DOCKER_BUILD_USE_GITLAB_TOKEN` (`"true"` only when that image's build needs to pull private GitLab-hosted
  packages).

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
- **Purpose**: creates the Git tag that drives the rest of the release flow.
- **Job produced**: extend `.create-tag-job` as `create-tag`, in the `tag` stage.
- **When to use**: every project that follows the tag-driven release flow (i.e. all of them).

```yaml
create-tag:
  extends: .create-tag-job
```

### `release`
- **Purpose**: generates the changelog and publishes the GitLab Release once a tag exists.
- **Jobs produced**: extend `.generate-changelog-job` as `generate-changelog` and `.create-release-job` as
  `create-release`, both in the `release` stage.
- **When to use**: every project with the tag-driven release flow.
- **Note**: `create-release` should declare `needs: [{job: generate-changelog, artifacts: true}]` so it has the
  generated changelog available.

```yaml
generate-changelog:
  extends: .generate-changelog-job

create-release:
  extends: .create-release-job
  needs:
    - job: generate-changelog
      artifacts: true
```
