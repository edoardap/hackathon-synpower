# Job Recipes and Evidence

Contents: [Config file → job](#config-file--job) · [Security jobs](#security-jobs) · [Code-check jobs](#code-check-jobs) ·
[Test jobs](#test-jobs) · [Build and release jobs](#build-and-release-jobs) · [Not migrated](#not-migrated)

The runnable YAML for each job is in `assets/workflows/`. This file explains **why** each job looks the way it does,
how sure we are, and what to verify. Confidence labels: **Confirmed**, **Inferred**, **To define** (see `SKILL.md`).

## Config file → job

These files in the repository drive the jobs. Read them before generating a workflow.

| Repo file | Drives | What to extract |
|---|---|---|
| `pyproject.toml` | lint, format, import-linter, pytest | `[dependency-groups]` (the `lint` group), `[tool.pytest.ini_options]` (`addopts` already adds `--cov`, `--cov-report=xml`, `--cov-fail-under`), `[tool.importlinter]`, `[[tool.uv.index]]` |
| `uv.lock` | uv-lock-check, every `uv sync --locked` | must be committed |
| `.python-version` | every Python job | `uv` picks it up automatically |
| `Makefile` | all QA jobs | the exact commands developers run locally (CI variants differ only where noted) |
| `.mdformat.toml` | markdown-lint | wrap width, plugins, excludes |
| `sonar-project.properties` | sonarqube | project key, sources/tests paths, `coverage.xml` path, `qualitygate.wait` |
| `.gitleaks.toml` | gitleaks | allowlists; uses `useDefault = true` |
| `.checkov-iac.yml` | checkov | frameworks, skip paths, `soft-fail` |
| `cliff.toml` | changelog, create-tag | commit parsers keyed on `[Feature]`, `[Breaking]`, `[Fix]`…; `[bump]` rules |
| `renovate.json` | renovate | portable as-is |
| `docker/*.Dockerfile` | docker builds, hadolint | targets, BuildKit secrets (`--mount=type=secret,id=gitlab_token`) |
| `.pre-commit-config.yaml` | cross-check | mirrors the local equivalents of lint/format/mdformat/import-linter and the drift checks |

## Security jobs

All run in parallel, never block, and use `continue-on-error: true` (the equivalent of `allow_failure: true`).

### gitleaks — Inferred
Evidence: `.gitleaks.toml` exists with `useDefault = true`. The recipe runs the gitleaks container against the whole
history (`fetch-depth: 0`). `gitleaks/gitleaks-action` is avoided because it demands a license on organization repos.
Pin a gitleaks image version instead of `latest`.

### checkov — Inferred
Evidence: `.checkov-iac.yml` with `soft-fail: true`. **The config lists the frameworks `gitlab_ci` and
`gitlab_configuration`; replace them with `github_actions`** (keep `dockerfile`, `kubernetes`, `helm`, `openapi`,
`secrets`, `json`), otherwise checkov scans files that no longer exist and misses the new workflows.

### sbom (cdxgen → Dependency-Track) — Inferred
Evidence: the old job set `CDXGEN_TARGET_DIRECTORY=src`, `ENABLE_DEPENDENCY_TRACK=true`, and `DTRACK_PROJECT_*`
variables. The recipe generates a CycloneDX BOM with `cdxgen` over `src` and uploads it to Dependency-Track's
`/api/v1/bom` endpoint with `autoCreate`. **To define:** URL, API key secret, and whether `parentName` is supported
by the server version. The project version is `github.head_ref || github.ref_name` (the old `CI_COMMIT_REF_NAME`
was the branch name even on merge requests; `github.ref_name` on a PR is `<n>/merge`).

### renovate — Inferred
Evidence: `renovate.json` is complete and portable (commit prefix `[Chore]`, which also satisfies the PR title rule).
Preferred: install the Renovate GitHub App on the repository; then no job is needed. A self-hosted alternative is in
`custom-jobs.md`.

## Code-check jobs

### changes (path filters) — Confirmed pattern
GitLab's `rules: changes:` becomes a `dorny/paths-filter` job whose outputs feed job-level `if:`. The filter lists are
copied verbatim from the old `changes:` blocks (OpenAPI and k8s/docker drift paths, Dockerfile glob).

### lint — Confirmed
`uv run ruff check src/ --output-format=github` after `uv sync --locked --no-default-groups --group lint`. Evidence:
`benchmark` pipeline (`--output-format=gitlab` there) and the Makefile. Never `--fix` in CI.

### format — Confirmed
`uv run ruff format --diff`. Exits non-zero when files would change.

### markdown-lint — Confirmed with a fix
Evidence: `benchmark` ran `mdformat . --exclude …` **without** `--check`, which reformats and passes — a gate that
never fails. The recipe adds `--check`. Same `lint` dependency group (`mdformat`, `mdformat-gfm`).

### import-linter — Confirmed
`PYTHONPATH=./src uv run lint-imports` (Makefile); the `PYTHONPATH` is required for the contracts to resolve. Use the full sync
(`--all-groups`) so contract modules import cleanly; the `lint` group alone is often enough but the full sync is safe.

### uv-lock-check — Confirmed
`uv lock --check` (this is also the only job ever recovered from a locally expanded GitLab pipeline). Needs `uv`, no
sync. The failure message tells the developer to run `uv lock` and commit.

### dockerfile-lint — Inferred
Evidence: the old job ran only on `dev` when `docker/**/*.Dockerfile` changed. The linter is assumed to be hadolint
(no config file in the repos confirms it). The recipe loops over every Dockerfile and keeps the original trigger
(push to `dev` with Dockerfile changes). Extending it to pull requests is a cheap improvement the user may want.

### drift checks — Confirmed (project-authored)
`openapi-check`, `api-k8s-check`, `data-pipelines-k8s-check`, `data-pipelines-docker-check` were written in the
project pipelines, so they migrate fully. Differences from GitLab: no `apt-get install git` (the runner has git), and
the `changes:` lists become path-filter outputs. Details in `custom-jobs.md`.

### code-checks (aggregate gate) — New
No GitLab equivalent; it exists because skipped jobs would otherwise skip everything downstream (see pitfalls in
`SKILL.md`). It is the one status check to require in branch protection.

## Test jobs

### pytest — Confirmed command, To define scope
`uv sync --locked --all-groups` then `uv run pytest`. The `pyproject.toml` `addopts` already produce `coverage.xml`
and enforce `--cov-fail-under` (80 in `data-pipeline-orchestrator`), so no extra flags. **To define:** whether
integration tests need services (database, MinIO). If yes, add `services:` containers to the job; if unsure, run
`tests/unit` only and say so in the PR.

### sonarqube — Inferred
Evidence: `sonar-project.properties` (`sonar.qualitygate.wait=true`, `sonar.python.coverage.reportPaths=coverage.xml`).
The job downloads the `coverage.xml` artifact from `pytest` and runs `SonarSource/sonarqube-scan-action` with
`fetch-depth: 0`. **To define:** `SONAR_HOST_URL`, `SONAR_TOKEN`, edition (pull request analysis needs a paid
edition). `scripts/run_sonarqube.sh` is a local-only helper and is not part of CI.

## Build and release jobs

### docker-build-dev — Inferred
Evidence: the `atena` pipeline contains a full self-contained build script: tag `v<YYYY.MM.DD>.<shortsha>`, extra
`latest` tag when building from `dev`, optional `--target`, `--cache-from`. It pushed to Harbor; this skill pushes to
GHCR with `docker/build-push-action`, no Docker-in-Docker needed. **To define:** the trigger (default: push to `dev`).

### private package index secret — Confirmed
`DOCKER_BUILD_USE_GITLAB_TOKEN: "true"` in `ai-agents` and `ai-tools` maps to a BuildKit secret: their Dockerfiles
read `/run/secrets/gitlab_token` to set `UV_INDEX_PROJETOS_IA_USERNAME/PASSWORD`, so `uv sync` can install private SDK
packages from the explicit index `projetos-ia`. In GitHub the matrix field is `private_index: true`; the secret id
stays `gitlab_token` so Dockerfiles need no change, but its value is the **internal registry** credential. Renaming the
secret id (and the index) is worth doing in a follow-up, not in the migration PR.

### docker-build-release — Inferred
Same build, triggered by tag `v*`, tagged with the git tag as-is. The old `atena` script prefixed `v` to
`$CI_COMMIT_TAG`; because the SDK job strips a leading `v` from the tag, tags are assumed to be `vX.Y.Z` already, so
no extra prefix is added. Confirm.

### create-tag — To define
Opaque in GitLab. A skeleton lives in `custom-jobs.md`; it needs a token that can trigger the release workflow.

### generate-changelog — Inferred
Evidence: `cliff.toml` (Portuguese headings, commit groups keyed on `[Feature]`, `[Fix]`…). Recipe:
`uvx git-cliff --latest --strip header -o RELEASE_NOTES.md` with full history checked out.

### create-release — Inferred
`gh release create "$GITHUB_REF_NAME" --notes-file RELEASE_NOTES.md --repo "$GITHUB_REPOSITORY"` using the
`GITHUB_TOKEN` with `contents: write`. The `gh` CLI ships on the runner, so no third-party action is needed.

### publish-python-sdk — Confirmed, destination changed
The generation, build, and smoke-test steps are project code and unchanged. The publish step now targets the internal
registry (`vars` for URLs, `secrets` for credentials). Details in `custom-jobs.md`.

## Not migrated

- **`ai-code-review` stage:** nothing concrete is known; `scripts/run_pr_agent.sh` exists but was not analyzed.
- **`sast` stage:** it was declared but had no job in any pipeline. GitHub has no stage list to reserve, so there is
  nothing to carry over. If SAST is wanted, CodeQL is the usual GitHub-native option.
- **`.standard-rules`, `.base-uv-*` hidden jobs:** replaced by workflow triggers, `permissions`, and repeating the
  checkout + `setup-uv` + `uv sync` steps in each job.
- **`interruptible: true`:** replaced by the workflow `concurrency` block (cancel superseded runs on PRs only).
