# ExecPlan 0016 — Pull-request CI on GitHub Actions

**Status: REMOVED at the owner's request (2026-10-17); it never ran on GitHub.** The owner asked to remove CI from the repository for now, possibly to add it back later ([DECISIONS](../../DECISIONS.md#2026-10-17--github-ci-removed-from-the-repository)). The workflow, the Dependabot configuration and the Compose override were deleted; `main` at `05d8ef9` still has them, so `git checkout 05d8ef9 -- .github tools/ci` restores them. This plan stays as the record of the design. Earlier status (2026-09-29): IMPLEMENTED; not yet run on GitHub. GitHub started no workflow run on the account (§8). The owner chose to merge this now. Owner request: "ok let's setup CI using most modern best practices". Branch `claude/ci`; delivered by pull request.

Labels: `OBSERVED`, `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

## 1. Goal and observable outcome

Every pull request to `main`, and every push to it, runs the repeatable release checks that Q07 asks to automate "where supported" ([ACCEPTANCE_CHECKLIST](../../ACCEPTANCE_CHECKLIST.md)). The checks run in the same containers as the local harness's `Checks` and `Regression` phases, and one final `CI result` status summarizes them. CI never deploys: deployment stays the local, owner-authorized procedure in [OPERATIONS](../../OPERATIONS.md#milestone-completion-deployment).

## 2. Current facts (OBSERVED, 2026-09-29)

- `MentorAliu/adaptive_spot_lab` is private, on GitHub Free.
  - It had no workflows and reported no checks for PR #1.
  - Branch protection and rulesets return "Upgrade to GitHub Pro or make this repository public", so a failing check cannot technically block a merge.
- Actions settings:
  - Actions are enabled with all actions allowed, and `sha_pinning_required` is false.
  - The default `GITHUB_TOKEN` permission is already `read`, and workflows cannot approve pull requests.
- The local harness runs these checks in Docker:
  - web: `web-tools`, which is `apps/web/Dockerfile` target `source`, with no network
  - engine: `engine-tools` / `engine-tests`, which is `services/engine/Dockerfile` target `test`
  - integration: Compose `postgres` + `migrate` + the pytest suite + `mode-guard`

  It requires that no test is skipped (`tools/m3-acceptance.ps1`, `tools/lib/Acceptance.psm1`).

## 3. Scope and exclusions

**In scope**
- `.github/workflows/ci.yml` and `.github/dependabot.yml`
- `tools/ci/compose.images.yaml`
- records in TESTING, LIBRARIES, INTEGRATION_EVIDENCE, COMMANDS, README and this plan

**Excluded**
- Continuous deployment and self-hosted runners. A runner on the owner's PC with Docker access would let GitHub-triggered jobs run code next to owner data and secrets. Hosting is deferred (DECISIONS).
- The long performance workloads (60-minute engine run, seven-day replay) and the browser suites. They stay local harness phases. Budgets are defined for the owner's host, and shared runners are noisy. A browser job is a possible follow-up.
- Repository secrets, and code scanning that needs GitHub Advanced Security.
- Any application change.

## 4. Design (IMPLEMENTED)

**Triggers and concurrency**
- Triggers: `pull_request` to `main`, `push` to `main`, and `workflow_dispatch`.
- `pull_request_target` is never used.
- A newer run for the same pull request cancels the older one. Runs on `main` are never cancelled.

**Hardening**, following [GitHub's security hardening guide](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions):
- Every action is pinned to a full-length commit SHA, with its version in a comment.
- Workflow permissions are `contents: read` only.
- Checkout uses `persist-credentials: false`.
- No `${{ }}` expressions appear inside shell scripts. The one computed value reaches the shell through an environment variable.
- Runners are pinned to `ubuntu-24.04`, and every job has a timeout.
- The workflow uses no secrets. The engine job generates six random 64-hex-character test credentials per run under `$RUNNER_TEMP`. They exist only in that ephemeral runner.

**Jobs.** The four check jobs run in parallel; `ci-ok` runs last.

| Job | What runs |
|---|---|
| `workflow-lint` | actionlint 1.7.12 and zizmor 1.30.1, from images pinned by digest, with no network |
| `web-checks` | Build the `source` image (Buildx, GitHub Actions cache), then lint, typecheck, unit tests, `api:check`, Prettier and the production build, with no network. These are the harness `Checks` phase's web commands. |
| `engine-checks` | Build the `test` image, then Ruff and the OpenAPI drift check, with no network |
| `engine-tests` | Build the `runtime` and `test` images. Use the Compose file with a small image override (`tools/ci/compose.images.yaml`) so Compose reuses the cached builds. Then start PostgreSQL, migrate, and run the full pytest suite. The job fails if any test is skipped, as the harness does. The mode guard runs last. On failure, pytest and service logs are uploaded for 7 days. |
| `ci-ok` (`CI result`) | Passes only if every job succeeded. It is the single status to check before merging, and to require if the plan ever allows branch protection. |

**Dependabot** proposes grouped monthly updates for GitHub Actions only. A 7-day cooldown means versions are proposed only after they have been public for a week. Docker base images and packages remain pinned in their lockfiles and Dockerfiles, and change only through plans.

## 5. Sources and versions (OBSERVED 2026-09-29 via the GitHub API)

| Dependency | Version | Commit / digest | License | Purpose |
|---|---|---|---|---|
| `actions/checkout` | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` | MIT | Check out the commit |
| `docker/setup-buildx-action` | v4.4.1 | `f87e5991a6d7451dcb8d9637bfbc97413f497069` | Apache-2.0 | Buildx builder for the `gha` cache |
| `docker/build-push-action` | v7.4.0 | `c3c9e263c25d99ce0380d002d59b67737d91b0dc` | Apache-2.0 | Cached image builds, loaded locally (never pushed) |
| `actions/upload-artifact` | v7.0.1 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | MIT | Failure logs |
| actionlint | 1.7.12 | `sha256:b1934ee5…5667` | MIT | Workflow syntax and shellcheck lint |
| zizmor | 1.30.1 | `sha256:a2eb396d…8101` | MIT | Workflow security audit (offline) |

Docker's [GitHub Actions cache backend](https://docs.docker.com/build/cache/backends/gha/) is used with per-image `scope` and `mode=max`. It is subject to GitHub's cache limits and eviction.

## 6. Verification

- **Local:**
  - actionlint on the workflow: no findings.
  - zizmor `--offline`: "No findings to report".
- **GitHub:** the first run on this pull request is recorded in §8.

## 7. Q01–Q10 (affected gates)

| Gate | Result |
|---|---|
| Q04 | No secrets, read-only token, SHA pins, no `pull_request_target`, no deployment. The linters enforce the patterns. |
| Q07 | The repeatable harness checks now run automatically on every pull request and on `main`. |
| Q10 | Versions, licenses and sources are recorded here and in LIBRARIES and INTEGRATION_EVIDENCE. Dependabot keeps the pins current. |
| Other gates | Not affected: no application change. |

## 8. Progress and evidence

- 2026-09-29 IMPLEMENTED: workflow, Compose override, Dependabot configuration and documentation. Local actionlint and zizmor passed.
- 2026-09-29 OBSERVED: the first runs for PR #2 (push and pull_request) ended in `startup_failure` with no jobs created.
  - All four pinned action commits exist, and a throwaway branch with a one-step workflow also ended in `startup_failure`. So the cause is account-level, not this workflow. The probe branch was deleted afterwards.
  - GitHub's message named an account setting, not this workflow.
  - The owner chose to merge this PR and look at the account separately.
- **NOT RUN:** the first successful GitHub run. Once Actions runs, check the first `CI result` on `main` or on the next pull request, and record it here.
- 2026-10-17 REMOVED: the owner asked to remove the GitHub CI checks from the app for now, to be added back later. `.github/workflows/ci.yml`, `.github/dependabot.yml` and `tools/ci/compose.images.yaml` were deleted; no workflow ever ran. To add CI back, restore those three files from `05d8ef9`, re-check the pinned versions in §5 against current releases, run actionlint and zizmor, and record the first real `CI result` here.

**Residuals**
- **No merge blocking.** Merges are not technically blocked on a red check, because this is a private GitHub Free repository. Process rule while CI existed: do not merge unless `CI result` passed. Since the removal, a pull request's evidence is what its body records ([TESTING](../TESTING.md#continuous-integration)).
- **Optional repository settings need the owner's approval:**
  - require SHA-pinned actions (`sha_pinning_required`)
  - allow only GitHub-owned actions plus `docker/*`

  The token default is already read-only.
- **Actions minutes.** The repository is private, so runs use the account's included Actions minutes.
