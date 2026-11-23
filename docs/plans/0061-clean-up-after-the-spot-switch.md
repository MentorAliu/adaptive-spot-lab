# ExecPlan 0061 — Clean up after the spot switch

**Status: APPROVED by the owner on 2026-11-12 at 22:57:09 UTC, on the thread's card "Approve the cleanup plan for the spot app?": "Approve", which the thread recommended ([DECISIONS](../DECISIONS.md#2026-11-12--clean-up-after-the-spot-switch-execplan-0061)).** Written on 2026-11-12 in the project thread "Clean up the app after the spot switch", on the owner's ask of 2026-11-12 at 22:45:11 UTC: "now do a full app cleanup since we moved to spot trading, make sure to cleanup,refactor anything that is a leftover and improve, enhance the app". Part of M12 ([ExecPlan 0060](0060-spot-trading-only.md)), not a new milestone: it changes no rule, policy, cost, limit, latch or money path.

Labels: `OBSERVED` (seen in code, records or on the PC), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

## 1. Goal

After one update:
1. The repository describes and holds only the spot app: what served the futures account, the perpetual, the AI agents, the research and the pre-futures engine is gone from the code, the tools, the configuration and the current documents. Their history stays, moved to `docs/archive/`, and their records stay read-only in the database's `archive` schema.
2. A future task reads about half as much: each current contract describes the spot app alone; the finished plans and the retired sections are searchable in the archive.
3. Two modest improvements, neither touching how the app trades:
   - **Updates wait less.** The update file and the Docker clean-up pause only around the daily close and the rule's reading (23:55 to 00:10 UTC) instead of near every hour (HH:55 to HH:05 UTC), which served M3's hourly bars and the futures' 15-minute decisions.
   - **The Cockpit compares the run with holding Bitcoin.** Beside the account's value: the run's return since it began and Bitcoin's change over the same span, paired by day on the stored daily references and daily candles ([0060 §4.10](0060-spot-trading-only.md#410-the-measure-pre-registered)'s descriptive comparison, "the account against holding Bitcoin from the run's start").

## 2. What the audit found

`OBSERVED` on `main` at `105c8ef` (2026-11-12) unless marked:
- **Engine** (`services/engine/app`, 6,853 lines): the spot switch already removed the futures, agents and research packages. Left: the dependency `argon2-cffi`, imported by nothing since ExecPlan 0042 removed the owner's sign-in; `accounting.funding_snapshot` and four helpers of `app/execution/numbers.py` (`ceil_to_step`, `floor_amount`, `ceil_to_digits`, `fits_money`, with its `MONEY_MAX`) called and tested by nothing (vulture at 60%, then each checked by search; `div` and `ceil_amount`, which only the number policy's tests call, stay as part of that policy); `app/models.py`'s `SystemMetadata`, which only Alembic's `env.py` imports for a metadata nothing compares; the `app.execution` package's docstring still describing M3's broker.
- **Web** (`apps/web/src`): ten shadcn primitives no file imports (`avatar`, `breadcrumb`, `button-group`, `checkbox`, `collapsible`, `dialog`, `hover-card`, `popover`, `progress`, `switch`), the hook `use-hash-scroll.ts` and the script `scripts/measure-ssr.mjs`, used by nothing; the packages `@tanstack/react-devtools` and `@tanstack/react-router-devtools`, imported by nothing (knip 5; the Vite plugin `@tanstack/devtools-vite` is used and stays); `apps/web/README.md` still describes M0's read-only status page.
- **Compose:** `browser-tests` builds from `tools/browser/Dockerfile`, which does not exist in any commit of the visible history (since `89954ed`); the browser suites run in the cloud ([COMMANDS](../COMMANDS.md#browser-suites-cloud)).
- **Tools:** `tools/update.ps1` (1,283 lines) still carries the futures account's preflight (before migration `0041`), the futures clean start of [ExecPlan 0039 §5.1](../archive/plans/0039-bitcoin-futures-on-paper.md) with its undo and `app.migrate --keep-logins`, the stop and removal of the retired services' containers and networks, and the removal of the Claude sign-in's starter. On the PC (`OBSERVED` read-only on 2026-11-12 at 22:50 UTC, the update's record `update-20261112T180830Z/update.json`): schema `0041_spot`, `futures_account` `none`, `clean_start` false, no retired container or network left (`"retired": {"containers": {}, "networks": []}`), and no `sign-in-claude.cmd` in the app folder; the update took 2 min 54 s and its dump is 145 MB. Its model test `tools/m8/update-model.ps1` models the futures app of 2026-11-12. `.gitignore` still names `sign-in-claude.cmd`.
- **Documents:** 27 finished plans (0033 to 0059) in `docs/plans/`; each contract (`API_CONTRACTS`, `DATA_CONTRACTS`, `AUTONOMY_MATRIX`, `FRONTEND`, `TESTING`, `SECURITY`, `CONFIGURATION`, `DOCKER`, `ARCHITECTURE`, `OPERATIONS`, `RISK_POLICY`, `LEDGER`, `PAPER_EXECUTION`, `MARKET_DATA`, `ACCEPTANCE_CHECKLIST`, `INTEGRATION_EVIDENCE`, `REFERENCES`, `LIBRARIES`, `PROJECT`, `STRATEGIES`) has its M12 section on top of the sections of M2 to M11; the root `README.md` describes the agents trading BTC and SOL; `tests/AGENTS.md` asks for agent tests; three of the five ideas and two of the three templates serve the agents and the research. `CONFIGURATION.md` lists about 30 settings nothing reads.
- **Database:** the `archive` schema holds 131 tables and 62 views of the futures app (`OBSERVED` on the PC at 17:24 UTC). Kept (§13).

## 3. Scope

In: the deletions and edits of §2; the update file and its model test; the Docker clean-up's quiet time; the Cockpit's comparison (an API field and the value card); the documents' move to the archive and the current contracts rewritten to the spot app; the contracts this plan changes (§5).

Out: any change to `SPOT_RULE_V1`, `SPOT_POLICY_V1`, `SPOT_COST_V1`, the backtest, the latches, the money path or a migration; the `archive` schema (kept, unless the owner's card says otherwise, §13); `DECISIONS.md` and `TRADING.md` (the owner's and the trader's records, unchanged but for this plan's entry); the PC's old update records and the `before-futures` dump (the owner's); other projects' Docker resources.

## 4. Design

### 4.1 Code

- Engine: remove `argon2-cffi` from `pyproject.toml` and relock (`uv lock`); delete the unused helpers; keep `app/models.py` (Alembic's `env.py` needs a metadata) but drop `SystemMetadata`; fix the `app.execution` docstring (the shared fencing, lease, identities, numbers and daily reference the spot engine uses); keep `db.ACCEPTED_REVISIONS`, which looks like an alias of `SPOT_REVISIONS` but is what the update file asks the built code for ("which schemas the built api accepts"). No change to any module the money step runs but the deletions.
- Web: delete the ten primitives, the hook, the script and the two devtools packages (relock with pnpm); rewrite `apps/web/README.md`.
- Compose: remove `browser-tests`. `.gitignore`: drop `sign-in-claude.cmd`.

### 4.2 The update file

- Removed: the futures account's preflight; the clean start, its undo and the `before-futures` copy it makes (the copy on the PC stays, and the tidy step still never deletes it); `app.migrate --keep-logins` and its use; the stop, restart and removal of the retired services; the sign-in starter's removal.
- `Wait-QuietTime`: a change begins at or after 00:10 UTC and ends its declared minutes before 23:55 UTC. The same window in `tools/docker-cleanup.ps1`.
- Kept as it is: the folder check, the preflight, the backup and rollback tags, the builds, the migration with the workers stopped before a contract migration and started again when it fails, the recreations in order, the verify, the read-out, the record and the tidy.
- The model test (`tools/m8/update-model.ps1`) models the spot app as the PC runs it now (schema `0041_spot`, the four app services, no retired service), with a hypothetical contract migration `0042_model` for the stop-and-restart scenarios; the scenarios of the removed paths go. It runs on the owner's PC through a Remote Control session in a temporary clone (Windows PowerShell 5.1, no Docker), as for 0060; the cloud cannot install PowerShell (refused by the session's permission check, 2026-11-12).

### 4.3 The Cockpit's comparison

- API: `GET /v1/spot`'s `run` gains `since_start`, paired by day as 0060 §4.10 says: between the run's first and newest `TIMELY` daily references (the account's first valid valuation within five minutes after a UTC midnight, `spot_daily_references` joined to its valuation, of this run, up to its stop), `account` = newest NAV / first NAV − 1 against `bitcoin` = Bitcoin's daily close of the day before the newest / the same of the first − 1 (each close is Bitcoin's last price at that midnight), each a ratio to 8 places as the page's other ratios; with both valuations' times and both closes; `null` until the run has two such days. A top-up does not move it (NAV per unit). Both sides are kept records (the references and the daily candles are never pruned), so it holds for a run of any length; a reference made late (the PC off at midnight) is left out rather than paired with a price from another moment.
- Web: a line under "Today" on the value card: "Since 13 Nov · Run +0.42% · Bitcoin −2.10%", each signed and colored, each with a tooltip (the run's span, after fees, a top-up is not a gain; Bitcoin's two closes); nothing when `since_start` is `null`.
- The trading review ([TRADING](../TRADING.md#how-to-judge-a-trading-change); the `trading-review` skill): "a yardstick or a page": nothing the rule does changes; the clock of M1 holds; the comparison is 0060's descriptive one, not a pass or fail. No disclaimer is added ([DECISIONS](../DECISIONS.md#2026-10-30--no-disclaimers-on-the-pages)).

### 4.4 The documents

- `docs/plans/0033` to `0059` move to `docs/archive/plans/` (0034's part 3 is moot: its routes and modules went with 0060).
- Each contract of §2 is copied verbatim to `docs/archive/contracts/<NAME>.md` (as it stood at `105c8ef`), then rewritten to the spot app: what still holds of its general rules, and its M12 section. `DECISIONS`, `TRADING`, `STATUS`, `COMMANDS`, `PLANS`, `SHADCN_WORKFLOW` and `ROADMAP` stay in place (`COMMANDS` and `ROADMAP` lose only what no longer runs or was condensed).
- The agents' ideas and the research templates move to `docs/archive/ideas/` and `docs/archive/templates/`.
- Every link that pointed into a moved file or a removed section is rewritten to its archived copy by a script, and the link check finds none broken.
- The root `README.md` and `tests/AGENTS.md` describe the spot app.

## 5. Authority

No authority changes. The contracts changed by this plan: the documents of §4.4; [AGENTS.md](../../AGENTS.md) only for its links. `RISK_POLICY`'s M12 section, `AUTONOMY_MATRIX`'s M12 section and the definitions' text are kept word for word.

## 6. Requirements and tests

| ID | Requirement | Test |
|---|---|---|
| R1 | Nothing imports a removed module, package or primitive; the engine and web build | Ruff, `tsc`, ESLint, the production build, the whole engine suite on a scratch database, Vitest |
| R2 | `since_start` paired by day on fixed references and daily closes: the run's first and newest `TIMELY` references, NAV per unit through a top-up, a late reference left out, `null` with fewer than two days, the stop's bound | `tests/test_spot_db.py::test_the_run_against_holding_bitcoin_is_paired_by_day` on a scratch database; the OpenAPI drift check and `api:check` |
| R3 | The value card's line: signed and colored values, the tooltip, nothing when `null` | `src/cockpit/cockpit.test.tsx`, the browser chain's Cockpit test |
| R4 | The update file: the scenarios kept pass on the spot model; the quiet time's window (the scenario `quiet`) | `tools/m8/update-model.ps1` on the owner's PC |
| R5 | The documents: no broken link or anchor; the current contracts name no removed service, route, setting or table as in use | `tools/check_links.py`; a search of the current documents for the removed names |

## 7. Official sources

No new library, provider or host. The relocks use the registries' current metadata for the packages already locked (`uv lock`, `pnpm install`). shadcn: removing a primitive needs no registry call; the remaining ones are unchanged (preset `b2fms61Bqi`).

## 8. Data and trust boundaries

Unchanged: the API's role reads `spot_runs` and `spot_valuations`, as today. No new secret, setting, service or network.

## 9. Implementation sequence

1. This plan, and the owner's card.
2. The code (§4.1), the Cockpit (§4.3), the update file (§4.2), the documents (§4.4), in one pull request.
3. The cloud checks (§10); the model test on the PC (with the owner's word in the thread).
4. Merge on the owner's word, then one update by the owner's double-click; the thread checks the install read-only on the PC: the folder at `main`, the four pages, the Cockpit's line, the update's record and its wait.

## 10. Verification commands

The commands of [COMMANDS](../COMMANDS.md): the web checks, Ruff, the OpenAPI drift check, pytest without a database and on a scratch PostgreSQL, the browser chain on a seeded scratch database, the link check, the ASCII check of the update file; the model test on the PC. `NOT RUN` in the cloud: Docker, the update itself.

## 11. Failure and rollback

- The update file fails on the PC: it stops and records `FAILED` with what it left; a fix is the next update (fixed forward), and the backup it took restores the database whole.
- Nothing in the database changes: no migration; the rollback tags name the images before it.
- A document link broken after the move: the link check fails before the merge.

## 12. Q01–Q10

Q01, Q02: the value card's line in the browser chain (its role and name, the tooltip). Q03: R1 to R3. Q04: no new input, route, secret or host; one field more in one read. Q05: `null` when a valuation is missing; nothing guessed. Q06: two indexed reads of the run's valuations per Cockpit read. Q07: §10. Q08: unchanged. Q09: the update file's model test; no migration. Q10: §4.4; two packages fewer.

## 13. Decision log

- 2026-11-12, the thread (engineering choices the owner delegates, [DECISIONS](../DECISIONS.md#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031)): what is removed (§2, §4); keep `app.execution`'s name (the compose service and the health check run it, and the update file's checks name it); keep the update file's tidy of dumps and images, and its protection of the `before-futures` copy; the archive's layout (§4.4); the two improvements, chosen because the owner dislikes waiting and has asked whether the app makes money: neither changes a trade.
- 2026-11-12, the owner: "Approve" (22:57:09 UTC), the thread's recommendation on the card "Approve the cleanup plan for the spot app?" (posted 22:55 UTC), keeping the `archive` schema: [RISK_POLICY](../RISK_POLICY.md#loss-reference-and-pause-semantics) keeps a run's loss history visible and the engine's rules forbid deleting losing runs; the whole backup is 145 MB. The other options: "Approve, cleanup only" (without §1.3) and "Approve, delete old records" (a migration that drops the archive after a dump kept beside the update's backups, changing that rule).

- 2026-11-12, the thread, while building §4.3: the first draft compared the run's first and newest valuations that carry a best bid. A valuation carries a bid only while Bitcoin is held (`spot_valuations.bid` is null in cash), so a run that starts in cash, as the PC's run #1 did, would have been compared from its first buy, not from its start. The comparison is now paired by day, as 0060 §4.10 words it, on the daily references and the daily candles, both kept for good.

## 14. Progress

- 2026-11-12: plan written (`PROPOSED`); audit of §2 `OBSERVED`; approved by the owner at 22:57:09 UTC; the build starts on the thread's branch `claude/project-thread-1e0k3v`.
- 2026-11-12, `IMPLEMENTED` on the branch: §4.1 to §4.4 as written, with two more removals found while building, both dead code: Alembic's `env.py` branch that ran the migrations on a caller's connection (only `--keep-logins` passed one), and the two tests of `--keep-logins` (`tests/test_clean_start.py` keeps its one remaining test as `tests/test_migration_guard.py`, migration `0008`'s guard). The comparison was built paired by day (§13). On the phone the line wraps between its two values, never inside one.
- 2026-11-12, `VERIFIED` in the cloud (Python 3.13, uv's locked environment, PostgreSQL 16 on a scratch cluster, Node with pnpm's locked packages, Playwright's Chromium):
  - Engine: Ruff `All checks passed!`; `FastAPI OpenAPI schema matches`; without a database `1 failed, 133 passed, 82 skipped` (the expected failure and skips, [COMMANDS](../COMMANDS.md#engine-without-a-database-cloud)); on a fresh scratch database `216 passed` in 39 s (218 before: the two tests of `--keep-logins` went, `test_the_run_against_holding_bitcoin_is_paired_by_day` came).
  - Web: `tsc` clean, ESLint clean, Prettier clean, `Generated TypeScript API types match`, Vitest `144 passed` (20 files), the production build.
  - The browser chain on the build: the pages (9) and the live suite (4) on a seeded database, then again on a freshly seeded one after the line's last change; the funding and account suites (5), M1's outcome suites (unknown, before dispatch, pending) and the API-down suite (4) on two fresh databases: `22 passed`, none skipped.
  - The line in the browser, by inspection: the fixture's runs are younger than two days, so its Cockpit shows no line (as designed). After the suites, on that disposable database, run #3's start was moved back and two SYNTHETIC `TIMELY` references were added (10 and 11 Nov, NAV 0.995 and 0.99917): the API answered `account` `0.00419095` and `bitcoin` `-0.01319647` (closes 61,776.37 and 60,961.14), and the Cockpit showed "Since 10 Nov Run +0.42% Bitcoin -1.32%" at 1280 px (light) and 390 px (dark), without sideways scroll or console error, each value a button named by its tooltip's words, the tooltip shown on keyboard focus.
  - `tools/check_links.py`: 146 files, 0 broken links. The update file, the clean-up file and the model test: plain ASCII. A search of the current documents, code and tools for the removed services, settings, functions and packages finds them only where a document says they were removed, in history (the roadmap's earlier milestones, the migrations' frozen records), in the model test that checks they are gone, and in the tests' warning never to touch the PC's `codex_home` folder, which is still there.
  - Cleaned up by exact name: the five scratch databases, the cluster `/var/tmp/asl0061pg`, the scratch secret files, the servers by process ID, `apps/web/.output` and `test-results`.
  - `NOT RUN` in the cloud: the update file's model test (R4; no PowerShell here), Docker and the update itself.
- 2026-11-13, R4 `VERIFIED` on the owner's PC, on the owner's "go ahead" (07:40 UTC): a Remote Control session cloned the branch at `cd5cc34` into a new folder under `%TEMP%` and ran `tools\m8\update-model.ps1 -Repository . -Work ..\work` in Windows PowerShell 5.1.26100.9818: exit 0 in 63 s, 14 scenarios and 61 expectations (update 26, dirty 4, early 1, ahead 1, migration 8, undofail 3, expand 2, halfway 2, readings 3, stoppedweb 4, settings 3, quiet 2, pages 1, relaunch 1), `"failed":[]`; the folder was removed after. The app, its folder and Docker were not touched.
- 2026-11-13, merged (PR #198, `f1cc2dc`, 07:44 UTC) on the owner's "go ahead" and installed by the owner's double-click; the install `OBSERVED` read-only on the PC at 07:48 to 07:50 UTC by a Remote Control session:
  - The update's record `update-20261113T074449Z`: `COMPLETE`, source `f1cc2dc` (from `d246473`), 07:44:43 to 07:47:46 UTC; no quiet-time wait (outside 23:55 to 00:10 UTC); no migration (`0041_spot` before and after); the api, the web and both workers recreated, postgres untouched; the backup 149.9 MB; the verify: schema `0041_spot`, reconciliation OK, the four pages 200, no problem; the read-out: feed `CONNECTED`, 3,375 days to 2026-11-12, run #1 `RUNNING`, today's reading `CASH` `NO_CHANGE`, the backtest recomputed (3,375 days), the archive's 131 tables. Its tidy deleted two merged branches on GitHub and the 2026-11-10 dump and removed four old images.
  - The folder at `f1cc2dc`, clean, equal to `main`. Containers: api, web, execution-worker and postgres healthy; the market worker up (it has no health check); no `browser-tests` container.
  - The database, in a read-only transaction: the three definitions' hashes unchanged; one run, #1 `RUNNING` with no cause; the account valid, not paused, reconciled; the feed connected with a current quote; the daily references 2026-11-13 `TIMELY` (791 ms) and 2026-11-12 `LATE_CONSERVATIVE` (the install); no fill yet.
  - The API's `GET /v1/spot`: `READY`, run #1 `RUNNING`, `since_start` present and `null` (one `TIMELY` day so far; the Cockpit's line appears after 2026-11-14's reference).
  - The workers' logs since the install: no error.
