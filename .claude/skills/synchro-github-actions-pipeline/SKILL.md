---
name: synchro-github-actions-pipeline
description: Build, review, or migrate GitHub Actions workflows for Synchro / ia_produtos Python + uv projects, including projects migrated from GitLab CI (.gitlab-ci.yml) to GitHub. Produces fully self-contained workflows (no reusable workflows or internal action imports), publishes container images to GHCR, and publishes the Python SDK to an internal package registry. Use this skill whenever someone asks to set up CI on GitHub, migrate or translate a .gitlab-ci.yml, add or audit jobs (secret scanning, IaC scan, SBOM, ruff lint/format, mdformat, import-linter, uv lock check, pytest, SonarQube, Dockerfile lint, OpenAPI/k8s drift checks, PR title validation, Docker builds, changelog, release, SDK publishing), or asks "what is the equivalent of this GitLab job in GitHub Actions" — even if they do not mention this skill or the GitLab catalog.
disable-model-invocation: true
---

# Synchro GitHub Actions Pipeline

## Overview

Projects in the `ia_produtos` group used to compose their GitLab pipelines from an internal component catalog
(`include: component:` + `extends: .some-job`). After migrating to GitHub, that catalog is not available, and GitHub
Actions has no `include`/`extends` for jobs. So every workflow produced by this skill is **self-contained**: each job
spells out its own steps, and nothing uses `uses:` to call an internal reusable workflow or composite action. Only
public, well-known third-party actions are used, and where a plain shell command does the same job, the command wins
(fewer moving parts to pin and audit).

Because the catalog internals were never visible, the job recipes here were **rebuilt from evidence in the
repositories** (Makefile, `pyproject.toml`, tool config files, the old pre-catalog pipelines of `benchmark` and
`atena`) rather than copied from the components. Each recipe carries a confidence label so nobody mistakes a guess for
a house standard:

| Label | Meaning |
|---|---|
| **Confirmed** | The exact command or script exists in a repository file (Makefile, a self-contained old pipeline, a project-authored job). |
| **Inferred** | The repo's config files make the tool and settings clear, but the original component's exact behavior was never seen. |
| **To define** | Not knowable from the repos. Ask the user before generating it; never invent a value. |

## Fixed decisions

- **Images go to GHCR** (`ghcr.io/<owner>/<repo>/<image>`), authenticated with the workflow's `GITHUB_TOKEN`.
- **The Python SDK goes to an internal registry**, not GitHub Packages (GitHub Packages has no PyPI support). The URLs
  and credentials come from org/repo `vars` and `secrets` — see `references/custom-jobs.md`.
- **Workflows are self-contained.** If a project later wants to share steps, it can extract a composite action inside
  its own repository, but this skill never assumes one exists.

## Pipeline shape

GitHub has no `stages:`. The old stage order is preserved with `needs:` between jobs, so the same fail-fast sequence
holds: advisory security jobs run in parallel and never block; cheap checks gate the tests; tests gate the builds.

```
changes ─┬─> lint, format, markdown-lint, import-linter, uv-lock-check, dockerfile-lint, <drift checks>
         │            └──────────────> code-checks (aggregate gate) ──> pytest ──> sonarqube ──> docker-build-dev
         └─> (path filters feed the jobs above)

gitleaks, checkov, sbom            advisory (continue-on-error), run in parallel, block nothing

pr-title.yml     separate workflow, PRs only
release.yml      on tag v*: docker-build-release ─┬─> publish-python-sdk (optional)
                           generate-changelog ────┴─> create-release
```

Three workflow files, because their triggers differ and a PR-title edit must not re-run the whole CI:

| File | Trigger | Contains |
|---|---|---|
| `ci.yml` | push to `main`/`dev`, pull requests, schedule | security, code-checks, tests, sonarqube, dev image build |
| `pr-title.yml` | pull request opened/edited/synchronize/reopened | PR title convention check |
| `release.yml` | push of tag `v*` | release image build, changelog, GitHub release, SDK publish |

## Step-by-step: bootstrapping a project

1. **Read the repo's own configuration first.** The recipes are thin wrappers around these files, and they decide
   which jobs apply and with what settings. See the table in `references/job-recipes.md` (config file → job).
   Generate nothing until you know whether the project has Dockerfiles, an OpenAPI spec with a generator command,
   generated k8s/compose artifacts, a `sonar-project.properties`, a `cliff.toml`, and a private `[[tool.uv.index]]`.

2. **Copy the templates** from `assets/workflows/` into `.github/workflows/` and replace every `<PLACEHOLDER>`.
   Delete the jobs that do not apply instead of leaving them commented out, except the drift-check skeleton.

3. **Pin actions.** The templates use major version tags (`@v4`) for readability. Check each action's current major
   version and, if the organization requires it, pin full commit SHAs. Do this before the first run.

4. **Wire the private package index** if `pyproject.toml` has an explicit `[[tool.uv.index]]` (the `ai-agents` and
   `ai-tools` repos do, pointing at the old GitLab PyPI group). After the migration that URL must point at the
   internal registry, and every job that runs `uv sync` needs the index credentials as environment variables
   (`UV_INDEX_<NAME>_USERNAME` / `UV_INDEX_<NAME>_PASSWORD`, with `<NAME>` the uppercased index name). The Docker
   build needs the same credential as a BuildKit secret. Changing the index URL changes what the lockfile records,
   so re-run `uv lock` and commit `uv.lock` in the same PR; otherwise `uv sync --locked` and `uv-lock-check` fail on
   the first run. Also check the Dockerfile for a hardcoded username (the existing ones use `__token__`).

5. **Add drift checks** for each committed generated artifact (OpenAPI spec, k8s manifests, compose/daemon config)
   using the pattern in `references/custom-jobs.md`, and list them in the `code-checks` gate's `needs:`.

6. **Add the Docker matrix entries**, one per image/target, and decide per image whether it needs the private index
   secret (`private_index: true`).

7. **Resolve the open questions below with the user** before enabling tag creation, SonarQube, SBOM upload, and SDK
   publishing.

8. **Run the checklist** at the bottom, then open the PR.

## Open questions (ask, do not guess)

- **Where is the release tag created and how is the version computed?** The old `create-tag` job is opaque.
  `cliff.toml` suggests `git-cliff --bumped-version` driven by `[Feature]`/`[Breaking]` PR titles, but where it ran
  (merge to `main`? `dev`?) is unknown. See the `create-tag` skeleton and its token caveat in
  `references/custom-jobs.md`.
- **When does `docker-build-dev` run?** Default here is push to `dev`; the original rule is unknown (the `atena`
  pipeline made it a manual job on `dev`).
- **Image tag scheme.** The `atena` pipeline pushed `v<YYYY.MM.DD>.<shortsha>` plus `latest` from `dev`, and release
  images with the git tag. The templates follow that; confirm it is still wanted.
- **Which registry, URLs, and credentials for the SDK and the private index?** Expected as `vars`
  `INTERNAL_PYPI_PUBLISH_URL` / `INTERNAL_PYPI_SIMPLE_URL` and secrets `INTERNAL_PYPI_USERNAME` /
  `INTERNAL_PYPI_PASSWORD`; rename to what the org actually uses.
- **Dependency-Track:** the URL, API key, and how the old `DTRACK_PROJECT_GROUP` maps onto the upload API.
- **SonarQube:** server URL, token, and edition (pull request analysis needs a paid edition). `docker-build-dev`
  needs `sonarqube`, so dev images do not build until Sonar is configured; if it is not ready, drop `sonarqube` from
  that job's `needs:` and say so in the PR.
- **Do the tests need services** (database, MinIO) in CI? The old `pytest` job's scope is unknown.
- **The old `ai-code-review` stage.** A `run_pr_agent.sh` exists in some repos and is probably its basis; its
  migration is out of scope until someone defines it.

## GitHub-specific pitfalls

These bite on the first real run, so the templates already handle them; keep them when editing:

- **Never interpolate PR titles, branch names, or other event text into `run:` with `${{ }}`.** Pass them through
  `env:` and read the shell variable. Interpolation is a script-injection hole.
- **Skipped jobs skip their dependents.** A job whose `needs:` includes a skipped job is skipped too. That is why
  `code-checks` is an aggregate job with `if: ${{ !cancelled() }}` that inspects `needs.*.result`; it is also the one
  status check to require in branch protection.
- **Do not use workflow-level `paths:` filters on a workflow that provides required checks.** The workflow never
  starts, the checks stay "pending", and the PR cannot merge. Use the `changes` job and job-level `if:` instead.
- **Tags pushed with `GITHUB_TOKEN` do not trigger other workflows.** If a job creates the release tag, it needs a
  PAT or GitHub App token, or the release must run in the same workflow.
- **GHCR image names must be lowercase.** Use `${GITHUB_REPOSITORY,,}` in shell.
- **`permissions:` start at `contents: read`** and each job raises only what it needs (`packages: write`,
  `contents: write`, `pull-requests: read`).
- **`gitleaks/gitleaks-action` requires a license for organization repos.** The template runs the gitleaks container
  directly to avoid that.
- **`mdformat` without `--check` rewrites files and always passes.** The old `benchmark` pipeline did exactly that;
  the migrated job uses `--check`.
- **`ruff check --fix` (the Makefile target) is wrong for CI.** CI must not modify files.

Detailed GitLab → GitHub equivalences (keywords, variables, rules) are in `references/gitlab-migration-map.md`.

## References

- `references/job-recipes.md` — every job, its confidence label, the evidence behind it, and which config file drives
  it. Read before editing any job.
- `references/custom-jobs.md` — project-authored logic (PR title check, drift checks, `create-tag` skeleton, SDK
  publish to the internal registry, optional Renovate workflow).
- `references/gitlab-migration-map.md` — keyword, variable, and trigger translation table; read when converting an
  existing `.gitlab-ci.yml` line by line.
- `assets/workflows/ci.yml`, `pr-title.yml`, `release.yml` — the starting templates.

## Checklist before opening the PR

- [ ] No `uses:` points at an internal reusable workflow or composite action.
- [ ] Every action version was checked and pinned according to org policy.
- [ ] `permissions:` is minimal at workflow level and raised per job only where needed.
- [ ] Security jobs are advisory (`continue-on-error: true`); `code-checks` is the single required status.
- [ ] No event text (PR title, branch, tag) is interpolated into `run:` — only via `env:`.
- [ ] Docker matrix covers every Dockerfile; image names are lowercase; private-index secret set where required.
- [ ] Private package index URL and credentials point at the internal registry, not GitLab.
- [ ] Every committed generated artifact has a drift check listed in the `code-checks` gate.
- [ ] `markdown-lint` uses `--check`; `lint` does not use `--fix`.
- [ ] Every **To define** item was answered by the user or left out, never guessed.
