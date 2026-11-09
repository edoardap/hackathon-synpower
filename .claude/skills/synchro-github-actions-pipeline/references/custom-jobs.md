# Project-Authored Logic

Contents: [PR title validation](#pr-title-validation) · [Drift checks](#drift-checks) ·
[create-tag skeleton](#create-tag-skeleton-to-define) · [SDK publishing](#sdk-publishing-to-the-internal-registry) ·
[Renovate (self-hosted)](#renovate-self-hosted-alternative)

This is logic that lived in the project pipelines (not in the catalog), so it migrates with its original behavior. User-facing
messages stay in Portuguese, as they were.

## PR title validation

Lives in its own workflow (`assets/workflows/pr-title.yml`) so that editing a title does not re-run the whole CI.
Same rules as the GitLab `validate-mr-title`: a tag from `Breaking|Feature|Fix|Refactor|Chore|Spike|Docs|Test` in
square brackets, a space, then a capitalized description — e.g. `[Feature] Adicionar endpoint de artifacts`.

Differences from GitLab:

- The title arrives through `env: TITLE: ${{ github.event.pull_request.title }}` and is read as `$TITLE`. Interpolating
  the title directly into the script would let a crafted title run commands.
- The `Draft: ` prefix stripping from the `ai-agents` version is dropped: GitHub draft PRs do not alter the title.
- `types: [opened, edited, synchronize, reopened]` — without `edited`, fixing a bad title would not re-validate.
- The `[Chore]` prefix produced by `renovate.json` already satisfies the rule, and `cliff.toml` groups changelog
  entries by the same tags, so keep the tag list identical across projects.

## Drift checks

Used when the project commits a file generated from source. The job regenerates it and fails if the result differs
from what is committed. Drift jobs must be listed in the `code-checks` gate's `needs:`.

Pattern (regenerate and diff — the old `openapi-check`):

```yaml
  openapi-check:
    needs: changes
    if: ${{ github.event_name == 'pull_request' && needs.changes.outputs.openapi == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
      - run: uv sync --locked --all-groups
      - run: PYTHONPATH=./src/ uv run python -m cli.main openapi generate -o docs/api/openapi.yaml -f yaml
      - name: Fail if the generated spec is out of date
        run: |
          if ! git diff --quiet -- docs/api/openapi.yaml; then
            echo ""
            echo "❌ O arquivo docs/api/openapi.yaml está desatualizado."
            echo "   Execute 'make api-specs' localmente, commite o arquivo atualizado e rode o pipeline novamente."
            exit 1
          fi
          echo "✅ docs/api/openapi.yaml está atualizado."
```

Pattern (dedicated check command — the old `api-k8s-check`, `data-pipelines-k8s-check`,
`data-pipelines-docker-check`): the project CLI does the comparison itself. These also ran unconditionally on
`main`/`dev` in GitLab, so the condition covers both cases:

```yaml
  api-k8s-check:
    needs: changes
    if: >-
      ${{ (github.event_name == 'pull_request' && needs.changes.outputs.api_k8s == 'true')
          || (github.event_name == 'push' && (github.ref_name == 'main' || github.ref_name == 'dev')) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
      - run: uv sync --locked --all-groups
      - run: PYTHONPATH=./src/ uv run python -m cli.main api check-k8s
```

Add the matching filter to the `changes` job (`api_k8s:` with the same paths as the old `changes:` list, for example
`src/api/config.py`, `src/shared/config/**/*.py`, `infra/api/dev/**/*.yaml`, `.env.example`). Scope each filter to the exact
source files that feed the artifact, so the job runs only when it could catch drift.

## create-tag skeleton (To define)

The original `create-tag` job is opaque. Do not enable this until the user confirms **where** tags are created and
**how** versions are computed. `cliff.toml` hints at `git-cliff --bumped-version` with `[Feature]` (minor) and
`[Breaking]` (major) rules and `initial_tag = "1.0.0"`, so this skeleton follows that hint:

```yaml
# .github/workflows/tag.yml — SKELETON, confirm before use
name: Tag
on:
  push:
    branches: [main]   # confirm the branch
permissions:
  contents: read
jobs:
  create-tag:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          # Tags pushed with GITHUB_TOKEN do NOT trigger release.yml. Use a PAT or GitHub App token.
          token: ${{ secrets.RELEASE_PUSH_TOKEN }}
      - uses: astral-sh/setup-uv@v6
      - name: Compute and push the next tag
        run: |
          next="$(uvx git-cliff --bumped-version)"
          if git rev-parse "$next" >/dev/null 2>&1; then
            echo "Tag $next already exists; nothing to do."
            exit 0
          fi
          git tag "$next"
          git push origin "$next"
```

Check that `--bumped-version` yields the same `v` prefix style as existing tags (the SDK job strips a leading `v`).

## SDK publishing to the internal registry

`publish-python-sdk` is in `assets/workflows/release.yml`. Generation, build, and smoke-test steps are the original
project commands; only the destination changed. GitHub Packages does not support PyPI, so the destination is the
organization's internal registry, configured entirely through variables so no URL is hardcoded:

| Name | Kind | Purpose |
|---|---|---|
| `INTERNAL_PYPI_PUBLISH_URL` | `vars` | upload endpoint (what the old job passed as `--publish-url`) |
| `INTERNAL_PYPI_SIMPLE_URL` | `vars` | simple index (what the old job passed as `--check-url`) |
| `INTERNAL_PYPI_USERNAME` | `secrets` | replaces `gitlab-ci-token` |
| `INTERNAL_PYPI_PASSWORD` | `secrets` | replaces `$CI_JOB_TOKEN` |

Rename them to the organization's real names. Notes:

- `--no-attestations --trusted-publishing never` are kept: the internal registry is not PyPI, so neither applies.
- `SDK_VERSION` is `${GITHUB_REF_NAME#v}` (the old `${CI_COMMIT_TAG#v}`), passed through `env`.
- **Reverse dependency:** `ai-agents` and `ai-tools` *consume* these SDKs through the explicit uv index
  `projetos-ia`. When the SDK moves, update that `[[tool.uv.index]]` URL in the consumers, re-lock, and provide the new
  credentials to both CI (`UV_INDEX_PROJETOS_IA_USERNAME/PASSWORD`) and the Docker build secret.
- The job only runs for projects that expose a versioned OpenAPI contract for SDK consumers; delete it otherwise.

## Renovate (self-hosted alternative)

Prefer the Renovate GitHub App: it reads `renovate.json` and needs no workflow. If the organization self-hosts
Renovate, use a scheduled workflow:

```yaml
# .github/workflows/renovate.yml
name: Renovate
on:
  schedule:
    - cron: "0 5 * * 1-5"
  workflow_dispatch:
permissions:
  contents: read
jobs:
  renovate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: renovatebot/github-action@v41
        with:
          token: ${{ secrets.RENOVATE_TOKEN }}   # PAT or GitHub App token; GITHUB_TOKEN cannot open PRs that trigger CI
        env:
          RENOVATE_REPOSITORIES: ${{ github.repository }}
          RENOVATE_ONBOARDING: "false"
```

`renovate.json` stays unchanged. Verify the action's current major version before use.
