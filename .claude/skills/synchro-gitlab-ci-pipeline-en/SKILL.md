---
name: synchro-gitlab-ci-pipeline
description: Build, review, or fix .gitlab-ci.yml pipelines for Synchro / ia_produtos projects by composing the organization's internal CI/CD Components Catalog (ia_produtos/ci-catalog, devsecops) instead of writing pipeline logic from scratch. Use this skill whenever someone asks to bootstrap CI for a new project, add or audit pipeline stages (security, code-checks, tests, sast, docker-build, release), wire up merge-request title validation, SBOM/Dependency-Track reporting, Renovate, uv-based Python QA (lint, format, pytest, import-linter, uv-lock, sonarqube), multi-image Docker builds, git tagging, changelog/release automation, or publishing a Python SDK generated from an OpenAPI spec — even if they only say "set up CI" or paste an existing .gitlab-ci.yml and ask for changes, without naming this skill or the catalog explicitly.
---

# Synchro GitLab CI Pipeline

## Overview

Projects under the `ia_produtos` GitLab group do not hand-roll their pipelines. Every `.gitlab-ci.yml` is a
composition of a shared **CI/CD Components Catalog** (`ia_produtos/ci-catalog/*`, plus a few `devsecops/*`
components) pulled in through `include: component:`, topped with a small, consistent set of project-authored jobs
(MR title validation, drift checks, SDK publishing). This is why pipelines across `ai-agents`,
`data-pipeline-orchestrator`, `ai-tools` and similar repos look almost identical: the same stages, the same hidden
job names, the same job ordering.

Building a new pipeline means **reusing this shape**, not designing a new one. Doing so keeps security scanning,
Python QA, SBOM generation, Docker builds and releases consistent fleet-wide, and means the project automatically
benefits when the catalog itself is updated (bump one version variable instead of touching every repo).

## When to Use This Skill

- Bootstrapping `.gitlab-ci.yml` for a brand-new `ia_produtos` project (Python + `uv`, FastAPI, Dagster, MCP server,
  etc.).
- Adding a missing stage/job to an existing pipeline (e.g., "we need Docker image builds" or "add SBOM reporting").
- Reviewing or debugging a pipeline that looks hand-written, to bring it back in line with the shared pattern.
- Adding project-specific jobs that must follow the established house style: MR title validation, "drift check" jobs
  that verify a generated artifact is up to date (OpenAPI spec, Kubernetes manifests, Docker compose files), or
  publishing a versioned Python SDK from an OpenAPI contract.

## Pipeline Shape (Stage Order)

Keep stages in this order. Not every project needs every stage — drop what genuinely doesn't apply, but never
reorder what you do keep, since job `needs:`/`rules:` across the catalog assume this sequence.

| # | Stage | Purpose |
|---|---|---|
| 1 | `security` | Secret scanning, IaC scanning, SBOM generation, dependency-update automation. Runs first and mostly advisory (`allow_failure: true`) so it never blocks fast feedback. |
| 2 | `code-checks` | Everything that can fail fast without running the test suite: MR title convention, lint, format, markdown-lint, import boundaries, lockfile freshness, Dockerfile lint, and any project-specific "generated artifact is up to date" drift checks. |
| 3 | `tests` | `pytest` (and SonarQube analysis, which needs test/coverage output). |
| 4 | `sast` | Reserved for static application security testing. Keep the stage even if no job currently targets it, so a SAST component can be dropped in later without reshuffling the file. |
| 5 | `ai-code-review` | Optional. Only include this stage if the project has adopted automated AI-assisted review; omit it otherwise rather than leaving an empty stage "for symmetry". |
| 6 | `tag` | Automatic Git tag creation driving the release flow. |
| 7 | `docker-build` | Builds and pushes every container image the project ships. |
| 8 | `release` | Changelog generation, GitLab Release creation, and (if applicable) SDK publishing. |

## Step-by-Step: Bootstrapping a New Pipeline

1. **Start from the template.** Copy `assets/gitlab-ci.template.yml` to the project's `.gitlab-ci.yml` rather than
   writing one from a blank file — it already has the correct `include:`, stage order, and hidden base jobs.

2. **Confirm what the project actually has** before wiring jobs: a `uv`-managed Python project? One or more
   Dockerfiles? A committed OpenAPI spec plus a CLI that regenerates it? Kubernetes manifests or Docker Compose
   files derived from config? A `renovate.json`? This determines which optional jobs below apply.

3. **Keep the `include:` versions as variables, never hardcoded.** Every component is pinned with
   `@${SOME_COMPONENT_VERSION}` (e.g. `${PYTHON_QA_VERSION}`, `${RELEASE_COMPONENT_VERSION}`). Those variables are
   defined centrally (group/instance level) — a new project just references them, it does not invent new version
   pins.

4. **Set `UV_CACHE_DIR` / `UV_PROJECT_ENVIRONMENT`** under project-local paths (`$CI_PROJECT_DIR/.uv-cache`,
   `$CI_PROJECT_DIR/.venv`) so `uv` caches correctly in CI.

5. **Wire the `security` stage**: `gitleaks` and `checkov` just need `allow_failure: true` overrides; `sbom` needs
   `CDXGEN_TARGET_DIRECTORY` (usually `"src"`) and the `DTRACK_PROJECT_*` identity variables set to the project's
   own name/group; `renovate` needs `renovate_config_path` pointing at the project's `renovate.json`. See
   `references/components.md` for the exact fields.

6. **Wire the `code-checks` stage**:
   - `validate-mr-title`, `lint`, `format`, `markdown-lint`, `import-linter`, `uv-lock-check`, `dockerfile-lint` are
     standard across every project — add them as-is (see `references/components.md` and
     `references/custom-jobs.md` for the exact job bodies).
   - If the project commits a **generated artifact** that must stay in sync with source (an OpenAPI spec, Kubernetes
     manifests, Docker Compose/daemon config), add a dedicated drift-check job following the pattern in
     `references/custom-jobs.md`. Scope its `rules: changes:` to the exact source paths that would make the
     artifact stale, and also run it unconditionally on `main`/`dev` so drift can never merge silently.

7. **Wire the `tests` stage**: `pytest`, plus `sonarqube` once coverage output exists.

8. **Wire the `docker-build` stage**: one `parallel: matrix` entry per image the project builds (one per
   Dockerfile, or per build target for multi-stage Dockerfiles), duplicated between `docker-build-dev` (branch
   pushes) and `docker-build-release` (tags). Set `DOCKER_BUILD_USE_GITLAB_TOKEN: "true"` only for images whose
   build needs to pull private GitLab-hosted packages; otherwise `"false"`.

9. **Wire `tag` and `release`**: `create-tag`, `generate-changelog`, `create-release` (the latter two with
   `needs: [{job: generate-changelog, artifacts: true}]`). Add `publish-python-sdk` only when the project exposes a
   versioned OpenAPI contract meant for external/internal SDK consumers — see `references/custom-jobs.md` for the
   full job.

10. **Sanity-check stage membership**: every job's `stage:` must be one from the table above, and `rules:` should
    reuse the shared "merge request OR main/dev OR tag OR scheduled pipeline" pattern (`references/components.md`
    calls this out as `.standard-rules`) unless the job has a narrower, intentional trigger (like a `changes:`
    guard).

## Known CI/CD Components

Full purpose/usage notes, the exact `include:` entries, and the inputs each one accepts live in
`references/components.md`. Read it before adding or modifying any `include:` block. In short, components fall
into three families:

- **`devsecops/*`** — secret scanning (`gitleaks`), IaC scanning (`checkov-iac`), SBOM generation (`cdxgen`).
- **`ia_produtos/ci-catalog/python-qa/*`** — the `uv` toolchain setup, shared job `rules`, lint/format/markdown/
  Dockerfile linting, `pytest`, `import-linter`, `uv.lock` freshness, and SonarQube reporting.
- **`ia_produtos/ci-catalog/release/*`** and **`renovate/renovate`** — Docker image builds, Git tagging, changelog +
  GitLab Release creation, and automated dependency-update merge requests.

## Project-Authored Jobs (Not From the Catalog)

A handful of jobs are written directly in each project's `.gitlab-ci.yml` because they encode project- or
org-specific business rules rather than generic CI/QA behavior:

- **`validate-mr-title`** — enforces the `[Tag] Capitalized description` merge request title convention.
- **drift-check jobs** (`openapi-check`, `*-k8s-check`, `*-docker-check`, …) — regenerate a committed artifact and
  fail the pipeline if it differs from what's checked in.
- **`publish-python-sdk`** — generates a Python SDK from the project's OpenAPI spec, builds it, smoke-tests it, and
  publishes it to the GitLab Package Registry on tag.

Full, ready-to-adapt job bodies for all three are in `references/custom-jobs.md`.

## Checklist Before Opening the MR

- [ ] `include:` only adds components, no bespoke reimplementation of what a component already provides.
- [ ] Stage list matches the canonical order; no stage declared without at least one job (except `sast`, which is
      intentionally reserved).
- [ ] `security` stage jobs are advisory (`allow_failure: true`) unless the project explicitly wants to block on
      them.
- [ ] Every `docker-build-*` job's matrix covers every Dockerfile the project ships, with correct
      `BUILD_CONTEXT`/`BUILD_TARGET`.
- [ ] Any committed generated artifact has a matching drift-check job.
- [ ] Version variables (`${PYTHON_QA_VERSION}`, `${RELEASE_COMPONENT_VERSION}`, etc.) are referenced, never
      hardcoded to a specific tag.
