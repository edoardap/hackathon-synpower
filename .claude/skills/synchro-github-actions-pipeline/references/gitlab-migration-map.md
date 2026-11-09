# GitLab CI → GitHub Actions Translation Map

Use this when converting an existing `.gitlab-ci.yml` line by line. Contents: [Structure](#structure) ·
[Triggers and rules](#triggers-and-rules) · [Job keywords](#job-keywords) · [Variables](#variables) ·
[Registries and credentials](#registries-and-credentials) · [Tool-specific changes](#tool-specific-changes)

## Structure

| GitLab | GitHub Actions | Notes |
|---|---|---|
| `stages:` | `needs:` between jobs | There is no stage list. Order comes from the dependency graph. |
| `include: component:` | nothing (inline steps) | Self-contained workflows; recipes are in `job-recipes.md`. |
| hidden job `.base-uv-full` + `extends:` | repeat checkout + `setup-uv` + `uv sync` | `uv sync --locked --all-groups`; the lint variant is `--no-default-groups --group lint`. |
| `.standard-rules` | `on:` triggers + job `if:` | See below. |
| `default:` / `before_script:` | `defaults:` / explicit steps | Keep steps explicit per job. |
| `needs: [{job, artifacts: true}]` | `needs:` + `actions/download-artifact` | Artifacts are not passed implicitly. |
| `trigger:` (child/downstream) | `workflow_call` / `workflow_dispatch` | Not used by these projects. |

## Triggers and rules

| GitLab | GitHub Actions |
|---|---|
| `$CI_COMMIT_BRANCH == "main" \|\| == "dev"` | `on.push.branches: [main, dev]` (+ `if: github.ref_name == 'dev'` per job) |
| `$CI_PIPELINE_SOURCE == "merge_request_event"` | `on.pull_request` (+ `if: github.event_name == 'pull_request'`) |
| `$CI_COMMIT_TAG` | `on.push.tags: ['v*']` (+ `github.ref_type == 'tag'`) |
| `$CI_PIPELINE_SOURCE == "schedule"` | `on.schedule: - cron: ...` |
| `rules: changes:` | `dorny/paths-filter` job output + job `if:` |
| `when: never` (final catch-all) | not needed; jobs that do not match `if:` are skipped |
| `when: manual` | `workflow_dispatch` or an environment with required reviewers |
| `allow_failure: true` | `continue-on-error: true` |
| `interruptible: true` | `concurrency: { group, cancel-in-progress }` |
| `parallel: matrix:` | `strategy.matrix.include` with `fail-fast: false` |
| `image: astral/uv:...` | `astral-sh/setup-uv` (or `container:` if a specific image is needed) |
| `services:` | `services:` (containers on the job network, addressed by service name) |
| `artifacts:` / `expire_in` | `actions/upload-artifact` with `retention-days` |
| `artifacts:reports:codequality` | ruff `--output-format=github` annotations (or SARIF to code scanning) |
| `coverage:` regex | not needed; Sonar reads `coverage.xml` |
| `environment:` | `environment:` (same idea; adds protection rules and approvals) |

Workflow-level `paths:` filters are **not** a substitute for `rules: changes:` on a workflow that provides required
checks: if the workflow does not start, the checks never report and the PR is blocked. Use the `changes` job.

## Job keywords

| GitLab | GitHub Actions |
|---|---|
| `script:` | `steps: - run:` (one step per logical command; use `name:`) |
| `variables:` (job) | `env:` (job or step) |
| `tags:` (runner selection) | `runs-on:` (runner label) |
| `cache:` | `setup-uv` `enable-cache: true`; `cache-from: type=gha` for Docker |
| `after_script:` | a step with `if: always()` |

## Variables

| GitLab | GitHub Actions |
|---|---|
| `$CI_PROJECT_DIR` | `$GITHUB_WORKSPACE` (usually unnecessary; `uv` defaults work) |
| `$CI_PROJECT_NAME` | `${{ github.event.repository.name }}` |
| `$CI_PROJECT_ID`, `$CI_API_V4_URL` | no equivalent; use explicit registry `vars` |
| `$CI_COMMIT_REF_NAME` | `github.ref_name` (branch/tag); on PRs use `github.head_ref` |
| `$CI_COMMIT_TAG` | `github.ref_name` when `github.ref_type == 'tag'` |
| `$CI_COMMIT_SHA` / `$CI_COMMIT_SHORT_SHA` | `github.sha` / `${GITHUB_SHA::7}` |
| `$CI_MERGE_REQUEST_TITLE` | `github.event.pull_request.title` (pass via `env:`) |
| `$CI_PIPELINE_SOURCE` | `github.event_name` |
| `$CI_SERVER_FQDN` | not needed (no components) |
| `${..._COMPONENT_VERSION}` group variables | not needed; pin action versions instead |
| group/instance CI variables | organization/repository `vars` (non-secret) and `secrets` |
| `$CI_JOB_TOKEN` | `GITHUB_TOKEN` (with `permissions:`) for GitHub APIs and GHCR; internal registry credentials for the SDK |

## Registries and credentials

| Need | GitLab | GitHub |
|---|---|---|
| Container images | GitLab registry / Harbor | **GHCR**: `docker/login-action` with `github.actor` + `GITHUB_TOKEN`, job `permissions: packages: write`, lowercase image name |
| Python SDK | GitLab Package Registry (`/packages/pypi`) | **internal registry** via `vars`/`secrets` (GitHub Packages has no PyPI support) |
| Private uv index in Docker build | BuildKit secret `gitlab_token` | same BuildKit secret id, value from the internal registry credential |
| Private uv index in CI jobs | provided by the old components (unknown) | `UV_INDEX_<NAME>_USERNAME` / `_PASSWORD` env from `secrets` |

## Tool-specific changes

| Tool | Change |
|---|---|
| checkov | in `.checkov-iac.yml` replace frameworks `gitlab_ci`, `gitlab_configuration` with `github_actions` |
| ruff | `--output-format=gitlab` → `--output-format=github` |
| mdformat | add `--check` (the old pipeline reformatted and passed) |
| gitleaks | run the container/CLI directly; the official action needs a license for org repos |
| Dependency-Track upload | explicit `curl` to `/api/v1/bom` instead of the cdxgen component's built-in upload |
| `apt-get install git` in drift jobs | remove; GitHub runners include git |
| Draft MR title prefix `Draft: ` | remove the stripping; GitHub drafts do not alter titles |
| `renovate.json` | unchanged; prefer the Renovate GitHub App |
