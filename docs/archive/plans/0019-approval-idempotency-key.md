# ExecPlan 0019 — Approval idempotency key after a failed call

## Goal and observed starting point

OBSERVED 2026-09-30 by reading `main` at `784a67d`. On the Approvals page, `confirm()` in [approvals-page.tsx](https://github.com/MentorAliu/adaptive_spot_lab/blob/3dd5011/apps/web/src/experiments/approvals-page.tsx) built the idempotency key inline in the request (`idempotency_key: newIdempotencyKey()`). Its client-side `catch` then recorded `{ kind: "UNKNOWN", key: "unavailable" }`.

That `catch` runs when the browser-to-Start server-function call itself rejects. The POST may already have reached the private API, for example when the connection drops while the response is on its way. Two things then went wrong:
- the key that was sent is lost;
- "Check outcome" looks up the literal key `unavailable`, which passes the key pattern `^[A-Za-z0-9_-]{8,64}$` ([schemas.ts](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/apps/web/src/experiments/schemas.ts)).

The API answers NOT_FOUND for that key, and the page says "Not recorded … It is safe to submit again". That is a false statement about an owner-authority record.

The server path was already correct. When the private API call fails, `recordApproval` → `classify` in [experiments.server.ts](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/apps/web/src/experiments/experiments.server.ts) returns UNKNOWN with the real key. Only the client `catch` lost it.

Goal: an unknown approval outcome always carries the key that was sent, and "Check outcome" resolves that key.

## Scope, decision and trust boundary

- **Change (IMPLEMENTED).** `confirm()` now takes `const key = newIdempotencyKey()` before the call, sends `idempotency_key: key`, and records `{ kind: "UNKNOWN", key }` in its `catch`. This is the shape `Controls.confirm()` in [experiment-detail.tsx](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/apps/web/src/experiments/experiment-detail.tsx) already uses.
- **Other mutation call sites (OBSERVED correct, unchanged).**
  - Experiment controls (`experiment-detail.tsx`) capture the key before `postControl`.
  - The draft card (`experiments-page.tsx`) receives the key as an argument of `send(key, cost)`. Its `catch` and its idempotent re-send both use it.
  - Account funding (`account/account-home.tsx`) builds the payload, key included, and persists it as a durable funding intent before sending.
- **Test (IMPLEMENTED).** [approvals-page.test.tsx](https://github.com/MentorAliu/adaptive_spot_lab/blob/3dd5011/apps/web/src/experiments/approvals-page.test.tsx) renders the page with the server functions mocked and a labeled synthetic approvals fixture. `postApproval` rejects with `TypeError("Failed to fetch")`, and `resolveApproval` returns a recorded APPROVE, standing for "the API did record it". The test asserts:
  - the `alert` reads "Outcome unknown";
  - its text contains the key that was sent and not `unavailable`;
  - "Check outcome" looks up `{ data: { key } }` with that key and shows "APPROVE was recorded for PAPER_PILOT_V1.".
- **Unchanged.** API, OpenAPI, generated types, schema, engine, markup and components. Financial and approval authority are unchanged. The private API's idempotency key and `expected_version` still guard duplicates, and nothing is shown as recorded before the API says so. No dependency or preset changed.
- **Records.** By owner decision on 2026-09-30, this plan holds the evidence. STATUS.md and COMMANDS.md are left to the M4 session, which owns them while the pilot runs.

## Verification

- **shadcn (VERIFIED).** The official skill was read from the installed Codex skill directory; its `SKILL.md` SHA-256 `deba6c51…09e4` matches the M0 record. `pnpm exec shadcn info --json` ran in the pinned isolated image `asl-m4-m4w-0930a-engine-web-tools` on bridge networking. It confirmed:
  - TanStack Start, `base-nova` and Base UI;
  - preset `b2fms61Bqi` and Lucide;
  - 17 installed components, including `alert-dialog`, `alert` and `button`.

  No component was added or changed, so no registry search was needed.
- **Test-first preflight (not counted).** It used the same image with no network, and the worktree's `apps/web/src` mounted read-only. Times are UTC on 2026-09-30.
  - 09:54: before the fix, the new test failed. The alert read "… check its outcome by its key (unavailable)." rather than the sent key.
  - After the fix, the test passed.
  - The full unit suite passed: 42 tests in 12 files. `typecheck` and `lint` passed.
  - Prettier reformatted one line of the new test inside the image, then `prettier --check` passed on both files.
- **Isolated run `m4k-0930a` (VERIFIED).** It ran from this worktree at commit `6c548c5`, in Windows PowerShell 5.1, driven by a sequence that stops at the first failed phase. Logs are in the worktree's `.cache/m4/m4k-0930a/`, and times are UTC on 2026-09-30.
  - **Load timing.** The heavy phases were held until 10:05, outside the running pilot's HH:00–HH:05 bar-close and snapshot window. None of these targets runs a public worker.
  - **`Prepare` and `Snapshot` 01** passed at 09:56–09:57.
  - **`Build`** passed for all seven targets (10:05:07–10:05:45).
  - **`Checks`** passed (10:05:45–10:06:31):
    - lint and typecheck;
    - **42 web unit tests in 12 files**, including the new one;
    - `api:check`, Ruff and the OpenAPI check;
    - the full Prettier check;
    - the production build, with its known nonfatal `"use client"` directive warnings;
    - relative doc links: 79 files, 0 broken.
  - **`BrowserApprovals`** passed (10:06:31–10:07:26): 1 Chromium case, none skipped. It is "owner approves exact hashes and requests Start; nothing is shown as applied early", the real approvals journey through the changed `confirm()`, and every decision reads "APPROVE recorded for …".
  - **`Snapshot` 02** reported 0 source differences, still on `6c548c5`.
  - **`Stop`** exited 0 at 10:07:54. No run container remains, and the volumes are kept.
  - **Tested web image.** `asl-m4-m4k-0930a-browser-web` is `sha256:2711f0122bc411d42f2cee92ad9a052407d378b0280d7b8f76e022e681e8d02e`, and its compiled `/app/.output` payload hash is `597184bc…9b39`.
- **Not run.** No engine, API, schema or dependency file changed, and the approvals failure path is covered by the unit test. So these phases were not run: `Generate`, `Regression`, `Migration`, `ActivationRehearsal`, `ApprovalAuth`, `BrowserError`, the pilot phases, the performance phases, `Replay`, `ReplayIsolation` and `SecretScan`.

## Normal deployment — web only (VERIFIED)

- **Authority and timing.** The owner gave an explicit go-ahead in chat on 2026-09-30. The rollout ran at 10:09–10:12 UTC, outside HH:00–HH:03 (OD-12), while the M4 pilot (experiment `d779fbf4…`) was RUNNING.
- **Procedure.** A Git Bash script (`MSYS_NO_PATHCONV=1`) ran one step per invocation and stopped at the first failure; each step refused to run within HH:55–HH:04 UTC. It logged to `.cache/deployments/approvals-key-20260930a/deploy.log` in the primary checkout. It built from this worktree at the pushed PR head `7855573`, which has no app change after the tested `6c548c5`, using the primary checkout's `.env` and secrets directory; no secret value was read. The primary checkout's branch and files were not changed.
- **Preflight (10:09 UTC).**
  - Running images: web `sha256:3206fdae…b5da` (ExecPlan 0018), API `4fba1a87…`, market worker `73df98a6…`, execution worker `5b02dbe1…`, evaluation worker `6e2d4e6a…` and PostgreSQL `b0f9560a…`. All were healthy or running.
  - Schema `0006_m4_fixed_pilot`.
  - Experiment `d779fbf4…` RUNNING at version 3; execution lease epoch 1; the `FORWARD_PAPER` checkpoint's last step 2 s old.
  - Experiment events: `CREATED`, `MARKED_READY`, `START_REQUESTED` and `ACTIVATED`, one each. Execution incidents: 0.
- **Backup.** `pg_dump -Fc` of `asl` produced `approvals-key-20260930a.dump`: 153,894,346 bytes, SHA-256 `a37299cca9521baceadcf63c14dd448d54e167a398e9f7ad32a7c84f13ba2a7c`. The checksum matched inside and outside the container, and the folder ACL is the owner account only (`icacls /inheritance:r`). No schema change, so no restore rehearsal.
- **Rollout (10:10–10:11 UTC).**
  1. The running web image was confirmed to be `adaptive-spot-lab-web:latest` and tagged `adaptive-spot-lab-web:pre-approvals-key`.
  2. `compose config --quiet` and `build --quiet web` produced `sha256:773d7c45e5a4d153f187893cb8bab0f8df67b8c88446ba1732bb22ec3805917e`.
  3. Its compiled `/app/.output` payload hash `597184bc…9b39` equals that of the `BrowserApprovals`-tested image `asl-m4-m4k-0930a-browser-web`. The previous image's payload hash is `ae74aabb…2aa3`.
  4. Only web was recreated: `up -d --no-deps --force-recreate --wait --wait-timeout 120 web`, with no profile.
- **Workers.** No worker was stopped or recreated. The code identity covers only the engine's `app/` tree, which is unchanged, so no evaluation segment started.
- **Verified after rollout (10:11–10:12 UTC).**
  - Web runs `sha256:773d7c45…917e` and is healthy.
  - PostgreSQL, API, market worker and both pilot workers keep the same container IDs, images and start times.
  - Schema `0006_m4_fixed_pilot`; experiment `d779fbf4…` still RUNNING at version 3; lease epoch 1; the checkpoint's last step at 10:11:40, advancing.
  - No new experiment event of any kind, and 0 execution incidents.
  - API readiness returned 200. `/`, `/system`, `/approvals`, `/experiments` and `/experiments/d779fbf4…` returned 200.
  - In the in-app browser, signed out, `/approvals` showed "Owner session required". No owner sign-in, approval or control was performed.
- **Rollback.** Recreate web from `adaptive-spot-lab-web:pre-approvals-key`. It is schema-compatible because nothing else changed.

## Affected gates

- **Q03.** The idempotency key used to resolve an unknown outcome is the key that was sent.
- **Q05.** A failed mutation call now resolves by its real key, and no false "not recorded" can follow.
- **Q07.** Unit test and Docker checks as recorded above.
- **Q09.** Frozen build, payload identity with the tested image, protected backup, web-only rollout with the pilot untouched, and a retained rollback image.
- **Q10.** No dependency or API change; this plan, the docs map, TESTING and INTEGRATION_EVIDENCE are updated.
- **Q01.** The failure path is covered by the unit test only. The browser phase covers the success path.
- **Not affected.** Q02, Q04, Q06 and Q08.
