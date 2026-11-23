# ExecPlan 0018 — Ended-run cause note

## Goal and observed starting point

OBSERVED 2026-09-29 in isolated run `m4f-0929c` ([ExecPlan 0015 §16](0015-evaluation-fixed-pilot.md#16-completion-evidence), finding 1): the detail page of a `COMPLETED` experiment showed the red "Paused by latched causes" alert. It read "OWNER since 19:10:13 UTC — an owner resume can close it under its rule" and "New entries are blocked; exits continue". The Owner controls card on the same page correctly said "No control is available in state COMPLETED".

The cause was still open in the data: the flatten opened an `OWNER` cause, and stop does not close causes. The API derives `causes` from append-only records whatever the run state, and `resumable` describes the cause kind, not whether a resume is on offer. The page presented both as a live pause.

Goal: an ended run never shows a pause or a resume claim, and no page claims a resume that its controls do not offer. The API is unchanged.

## Scope, decision and trust boundary

- **Files.**
  - `apps/web/src/experiments/parts.tsx` adds `CausesAlert` next to `OutcomeAlert`.
  - `experiment-detail.tsx` renders it in place of the inline alert.
  - `experiments.test.tsx` adds three unit tests.
  - `e2e/m4.spec.ts` extends the BrowserPilot case.
  - FRONTEND, ExecPlan 0015, STATUS, COMMANDS, INTEGRATION_EVIDENCE and the docs map record the change.
- **Ended runs (IMPLEMENTED).** For `STOPPED`, `COMPLETED` and `FAILED` (the engine's `states.TERMINAL`), the open causes appear in a neutral `default` Alert with `role="note"`:
  - title "Causes still recorded as open";
  - each cause with its `since` time;
  - "The run is COMPLETED, so it is not paused and no control applies to it. These causes are shown as a record only."
  - There is no resume wording and no "New entries are blocked" line. A discard moves DRAFT or READY to `STOPPED`; such a run was never activated, so the API returns no causes.
- **Why not "Causes open when the run ended".** Only `OWNER` and `APPROVAL_REVOKED` come from the run's own events.
  - `DAILY_LOSS` and `DRAWDOWN` are the mode's unresolved `risk_latches`.
  - `INTEGRITY` is the account's current reconciliation or pause flag.
  - Both are evaluated at read time (`app/experiments/causes.py`), so a time-of-end claim could be false for them. The note claims only what the page knows as of its evaluation time.
- **Live runs (IMPLEMENTED).** The destructive "Paused by latched causes" alert remains. Its per-cause wording now follows the page's `actions.resume`:
  - resume offered (only `PAUSED`): "an owner resume can close it under its rule";
  - a resumable cause with no resume offered (for example `STOPPING`): "no resume is offered in state STOPPING";
  - `INTEGRITY`: "not resumable in M4", as before.
- **Unchanged.** API, OpenAPI, generated types, schema, engine, controls, financial authority and the Owner controls card. The shadcn Alert (`default` and `destructive` variants) and the existing Badge, Card and Table were reused. No component, dependency or preset changed.

## Verification

- **shadcn (VERIFIED).** The official skill was read from the installed Codex skill directory; its `SKILL.md` SHA-256 `DEBA6C51…09E4` matches the M0 record.
  - `pnpm exec shadcn info --json` ran in the pinned `asl-m4-m4f-0929c-engine-web-tools` image on bridge networking. It confirmed TanStack Start, `base-nova`, Base UI, preset `b2fms61Bqi`, Lucide and 17 installed components including `alert`.
  - `shadcn search @shadcn -q alert -t ui` found `@shadcn/alert` and `@shadcn/alert-dialog`.
  - `shadcn docs alert` resolved the [Base UI Alert guide](https://ui.shadcn.com/docs/components/base/alert), which documents the `default` and `destructive` variants used here.
- **Preflight (not counted).** In the same image, with only `src` and `e2e` mounted read-only and no network, typecheck, lint and 41 unit tests passed. Prettier flagged two test files; they were formatted in the image before the commit.
- **Isolated run `m4w-0930a` (VERIFIED).** It ran from this worktree at commit `0db0a2a`, in Windows PowerShell 5.1, driven by a sequence that stops at the first failed phase; logs are in `.cache/m4/m4w-0930a/`. All times are UTC on 2026-09-29.
  - `Prepare`, `Snapshot` (01) and `Build` passed for all seven targets.
  - `Checks` passed (22:17–22:18): lint, typecheck, 41 web unit tests (11 files, including the three new ones), `api:check`, Ruff, OpenAPI drift, the full Prettier check, the production build and relative doc links. The build kept its known nonfatal `"use client"` directive warnings.
  - `PilotLifecycle` passed (22:18–23:00), then `PilotFaults` (23:00–23:04), `PilotDowntime` with 300 s of downtime (23:04–23:09) and `Evaluation` (23:09–23:15, flatten, stop, FINAL report and `COMPLETED`).
  - `BrowserPilot` passed (23:15–23:16): one Chromium case, none skipped. On the completed pilot it asserts:
    - "No control is available in state COMPLETED.";
    - a `note` with "Causes still recorded as open" and an `OWNER since …` item;
    - no "an owner resume can close it", "Paused by latched causes" or "New entries are blocked";
    - the existing timeline, report, chart, URL-state and 390-pixel checks.
  - `Snapshot` 02 reported 0 source differences, still on `0db0a2a`.
- **Own browser inspection (VERIFIED).** Before `Stop`, the in-app browser opened the isolated pilot (`127.0.0.1:58400`), signed in as the synthetic acceptance owner. The accessibility tree of Experiment #1 (`COMPLETED`, version 25) showed:
  - a `note` "Causes still recorded as open" with "OWNER since Sep 29, 2026, 23:10:02 UTC" and the neutral sentence;
  - "No control is available in state COMPLETED." below it, and no alert role for the causes.
  - The screenshot showed a neutral card-coloured note, not a destructive one.
- **Cleanup.** `Stop` exited 0. The run's synthetic feed (`compose run -d`, 3-hour lifetime) is not removed by `down`; its empty container log was saved, the container stopped and removed, and `Stop` rerun. No run container or network remains; the pilot's PostgreSQL volume is retained.
- **Not run for this display-only change.**
  - Isolated: `Generate`, `Regression`, `Migration`, `ActivationRehearsal`, `BrowserApprovals`, `ApprovalAuth`, `BrowserError`, the four performance phases, `Replay`, `ReplayIsolation` and `SecretScan`.
  - No engine, API, schema or dependency file changed. The approvals and error browser cases do not reach an ended run with causes.
  - BrowserPilot's existing 390-pixel no-overflow check reloads this detail page, so it covers the note. A screen-reader review is not claimed; it was retired by owner decision.

## Normal deployment — web only (VERIFIED)

- **Authority.** The owner gave an explicit go-ahead in chat on 2026-09-30 for a web deployment once BrowserPilot passed.
- **Procedure.** A scripted sequence stopped at the first failure and logged to `.cache/deployments/ended-run-causes-20260930a/deploy.log` in the primary checkout. It built from this worktree, using the primary checkout's `.env` and secrets directory; no secret value was read. The primary checkout's branch and files were not changed.
- **Preflight (23:18 UTC).** Running images were:
  - API `sha256:2835309c…4dc`, web `sha256:833a512b…c43` and market worker `sha256:a8138cbb…641`, all healthy or running;
  - schema `0006_m4_fixed_pilot`, both feeds `CONNECTED` with a current quote;
  - identities `asl_evaluation:false,asl_execution:false`, M4 counts all 0, lease epoch 0, no pilot container.
- **Backup.** `pg_dump -Fc` of `asl` produced `ended-run-causes-20260930a.dump`: 135,548,597 bytes, SHA-256 `5e4902dec419cae53f122baa9a5e99b76c37de406cdd3269ad7726a7dd8bf99d`. The checksum matched inside and outside the container, and the folder ACL is the owner account only. No schema change, so no restore rehearsal.
- **Rollout (23:19 UTC).**
  1. The worktree was clean at `0db0a2a`.
  2. `adaptive-spot-lab-web:pre-ended-causes` was tagged at `sha256:833a512b…c43`.
  3. `compose config --quiet` and `build --quiet web` produced `sha256:3206fdaef32d5db03b03811dd73d99575b8a73e8a23ef38b98230b07a568b5da`.
  4. Its compiled `/app/.output` payload hash `61a4bb1c…cb5a` equals that of the BrowserPilot-tested image `asl-m4-m4w-0930a-pilot-web`.
  5. Only web was recreated (`up -d --no-deps --force-recreate --wait web`).
- **Verified after rollout.**
  - Web runs `sha256:3206fdae…b5da` and is healthy.
  - PostgreSQL, API and market-worker container and image IDs are unchanged. Schema, identities, M4 counts, lease epoch and the absence of pilot containers are unchanged; both feeds are `CONNECTED` with a current quote.
  - The note text is in the client and SSR bundles. API readiness returned 200. `/`, `/system`, `/approvals`, `/experiments`, `/risk?mode=FORWARD_PAPER` and `/orders?status=ALL&symbol=ALL` returned 200.
  - In the in-app browser, signed out, `/experiments` showed "Owner session required". System read Account funded, Market data ready, Model runtime unconfigured, Paper trading disabled, Evaluation reports disabled, Paper execution worker not running.
  - The normal app has no experiment, so the note itself was verified only in isolation. No owner sign-in, approval, Start or activation was performed.
- **Rollback.** Recreate web from `adaptive-spot-lab-web:pre-ended-causes`. It is schema-compatible because nothing else changed.

## Affected gates

- **Q01.** The ended-run state is now distinct from the live pause state; covered by unit tests and BrowserPilot.
- **Q02.** An ended run's causes are a `note`, not an `alert` live region. Automated accessibility-tree assertions and the implementer's own tree and screenshot inspection passed. Screen-reader behavior is not claimed.
- **Q03.** Displayed states mirror the engine's `TERMINAL` and `ACCEPTS` tables. No resume is claimed unless `actions.resume` is true.
- **Q07.** Docker checks, unit tests and the isolated real-time BrowserPilot passed on one snapshot.
- **Q09.** Frozen build, payload identity with the tested image, protected backup, web-only rollout and a retained rollback image.
- **Q10.** No dependency or API change; contracts and records are updated.
- **Not affected.** Q04, Q05, Q06 and Q08.
