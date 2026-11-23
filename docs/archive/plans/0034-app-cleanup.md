# ExecPlan 0034 — Clean up the app

**Status: APPROVED by the owner on 2026-10-20 ([DECISIONS](../../DECISIONS.md#2026-10-20--the-owner-asks-for-a-full-cleanup-execplan-0034)); part 1 built, parts 2 and 3 in progress ([§12](#12-progress)).** Written by the project thread "App cleanup" from `main` at `cf6360d`. Not a milestone: it changes no protection, limit, policy or agent definition.

Labels: `OBSERVED` (seen in code, records or on the PC), `INFERRED`, `PROPOSED`, `NOT RUN`.

## 1. Goal

The owner, 2026-10-20:
- 19:11 UTC: "I want you to deeply research the app and do a thorough cleanup of the app as because it has been running and developed for quite some time and a lot has been added, what would be the most important things to cleanup ?"
- 19:13 UTC: "Cleanup without my approval, cleanup everything that is redundant, leftovers and other"
- 19:29 UTC, after Claude offered to shrink Docker's disk file: "Yes clean up docker as well"

The goal: remove what M1 to M7 left behind and M8's cut made pointless, on the PC, in the code and in the documents, without touching the five protections ([ExecPlan 0031 §4.1](0031-m8-simple-app-that-runs-itself.md#41-what-stays-and-why)) or the app's history.

## 2. What the audit found

**On the PC** (`OBSERVED` 2026-10-20 19:20 to 19:35 UTC, read-only, through the owner's device session):
- Docker's data disk `docker_data.vhdx` is 316.4 GB and not sparse, while Docker reports about 57 GB in use: images 22.7 GB, volumes 7.8 GB, build cache 26.3 GB (21 GB of it reclaimable; most of it another project's).
- This app's leftover images: the test and tool images of the old PC test runs (`adaptive-spot-lab-test-*`, `-browser-tests` 4.12 GB, `-engine-tests`, `-engine-tools`, `-web-tools`, `-public-smoke`, `-bootstrap:m0`, `-web-source:m0`, `-engine-test:m0`, `-engine-tooling:m0`), 30 old rollback tags (`:pre-m7`, `:pre-m6`, `:pilot-d779fbf4`, `:pre-00xx`, `:pre-m3`, `:pre-m4`) and 149 untagged builds; the volumes `adaptive-spot-lab-test_postgres_data` (48 MB, no container) and `adaptive-spot-lab-pnpm-cache` (empty).
- `.cache\deployments` holds 27 database dumps, 9.1 GB: every update and every pre-M8 deploy kept one, and nothing deletes them. The PC test-run folders `.cache\m2`, `m3`, `m3dev`, `m4`, `m6` and `m7` hold about 320 MB, with 296 folders of scratch test passwords.
- The database `asl` is 3.4 GB at `0015_m10_coins`, nearly all of it live market data (`market_payloads` 1.6 GB, `market_observations` 1.3 GB). No leftover test database. 13 containers up.

**In the repository** (`OBSERVED` at `cf6360d`):
- `tools/`: 77 files, 25,823 lines. The update path uses 3 of them (921 lines); about 23,300 lines serve PC test runs and deploy, boundary and activation scripts that M8 ended, several of which refuse today's schema (`m7-boundary.ps1` wants `0009`, `research-activate.ps1` `0008` or `0009`, `agent-activate.ps1` `0007`).
- Engine: 19 of 183 modules under `app/` are reached by no service, only by the PC test scripts or by tests, and the research runner imports test fixtures through `execution/acceptance.py`. The probe suites (CP-01 to CP-27, the decision probes), the owner's workflow Start, the agent-approval write routes and the M7 `boundary-check` have no page and no caller since M8.
- Web: a "Start a workflow" dialog for the owner (about 1,300 lines with its tests), text that still asks for approvals, Start or activation, unused exports and two unused devtools packages.
- Documents: about 696,000 words. `COMMANDS.md` (86,000 words) is 98% run logs; `TESTING.md`, `DECISIONS.md`, `STATUS_HISTORY.md` and `INTEGRATION_EVIDENCE.md` are mostly history; the pack-era root files (`START_HERE`, `MANIFEST`, `MIGRATION`, `CHANGELOG`, `PACK_VALIDATION`) describe an app that did not exist yet; `STATUS.md` and the root `README.md` are out of date. The agents read part of this at the start of every task.

## 3. Scope and exclusions

**In scope:** the PC's leftovers (part 1 and the update file), the repository's leftovers (part 2), the contract documents and the API file's layout (part 3).

**Not touched:**
- The five protections, every limit, the policies and every generation of agent definitions (the worker refuses to start without them, and history pages read them).
- Text inside hashed definitions, including the document paths they cite.
- The database: no table, column or row is dropped. The largest tables are live market data, and history stays readable.
- Migrations `0001` to `0015`, and migration `0016`, which [ExecPlan 0033](0033-m10-the-agents-look-beyond-btc-and-sol.md) reserves for M10's update 2.
- Other projects' Docker containers, images and volumes, and Docker's build cache ([DECISIONS](../../DECISIONS.md#2026-10-03--this-projects-old-test-runs-removed-other-projects-docker-resources-left-to-the-owner); rule 9 of [AGENTS.md](../../../AGENTS.md): exact names, no prune).

## 4. Design

### 4.1 Part 1: the Docker clean-up file

`tools/docker-cleanup.ps1`, started by double-clicking `docker-cleanup.cmd` in the app folder (a copy of `tools/docker-cleanup.cmd`, which runs the script as GitHub's `main` has it). Windows asks once for administrator rights, before anything changes; only the compaction uses them. In order:
1. Read-only checks: Docker and `docker desktop status` answer, the data disk exists, the app runs.
2. A wait while the clock is within HH:55 to HH:05 UTC.
3. A protected backup of the main database, by the update file's own function.
4. This app's images that no current service of `compose.yaml` uses, its untagged images and the two leftover volumes are removed, each by exact name or id and never with `-f`.
5. `fstrim` inside Docker's VM, then `docker desktop stop`, `wsl --shutdown` only while the disk stays in use, diskpart's `compact vdisk` on the disk attached read-only, and `docker desktop start`. The app's containers come back by their restart policy, and the run waits for each one that ran before.
6. After a clean run only: the dumps older than the newest three are deleted (the one the run took stays as well), and the old test-run folders.
7. The disk size before and after, and a JSON record beside the backups.

The app is down while the disk is compacted, and the downtime stays visible (rule 11). A failure at any step starts Docker again and keeps the old backups.

### 4.2 Part 2: the cleanup update (as built)

- **Update file:** after a `COMPLETE` run it keeps the three newest dumps and deletes older ones (with their `.sha256` files), and removes this app's images that no current service uses and this app's untagged images, by exact name or id, never with `-f`. A failure there is reported and the update stays complete. The backup root no longer grows by one dump per update. The `admin` and `agent-admin` profiles leave its list.
- **Tools and Compose:** the PC test-run, deploy, boundary, activation and deactivation scripts go, with their modules and model tests (`tools/` keeps 9 files: the update path and its model test, the link checker, the Codex sign-in script, `setup-local.ps1`, `lib/Pilot.psm1` trimmed to what the update and the clean-up use, and the Docker clean-up). Compose loses `market-fixture`, `public-smoke`, `pilot-admin` and `agent-admin`. The test and tool services (`web-tools`, `engine-tools`, `engine-tests`, `browser-tests`, the `agent-test` services) stay: rule 9 keeps the build and test paths containerized.
- **Engine:** the modules nothing reaches go: the market-data and execution performance and smoke harnesses and 15 harness-only files under `tests/` (found by an import walk from the services' entry points, the migrations, every pytest file and the browser fixtures). The routes nothing calls go ([API contracts](../contracts/API_CONTRACTS.md#cleanup-routes-nothing-calls-are-removed-execplan-0034)): the probe routes, the owner's workflow Start, `GET /v1/account/funding`, `POST /v1/account/reconcile` and `boundary-check`, with the functions only they used and their tests. Reconciliation, the short check, the probe-run history and every read path stay, and so do the owner's approval write routes: no page calls them, but they are the owner's recovery lever to reject or revoke what the app recorded (AUTONOMY_MATRIX). `execution/acceptance.py` and the browser fixtures stay: the research runner and the browser suite use them.
- **Web:** the Start dialog and its code, schemas and tests; the probe actions; the promotion link to it. The Playwright specs of closed milestones' timing measurements (`*-performance.spec.ts`) go with the harnesses that seeded them.
- **Prompts:** the four unversioned role prompts in `services/agent-runner/prompts/*.md` go; nothing reads them (the versioned `m5` to `m10` ones are what the app hashes).
- **Documents:** the run logs, finished plans, pack-era files and the M3 to M7 operating records move to `docs/archive/` with their links rewritten; `COMMANDS.md` and `TESTING.md` keep only what is current; `README.md`, `STATUS.md`, the documents index and the reading order in `AGENTS.md` are rewritten.

### 4.3 Part 3: after M10's update 2 (PROPOSED)

The contract documents describe the current app only (their milestone-by-milestone layers go to the archive); `main.py` is split by area with an unchanged OpenAPI; the schema check accepts the head and the one before it instead of a hand-kept list; the canonical-JSON hash helpers are shared, with a byte-identity test and an independent review because accounting uses one. These touch files M10's update 2 changes, so they wait for it.

## 5. Requirements and tests

| ID | Requirement | Test |
|---|---|---|
| C1 | The Docker clean-up removes only this app's images and volumes that nothing uses, by exact name, and keeps `:latest` and `:before-update` of every current service | Dry run against a stand-in `docker` (part 1); a dry run on the PC before the real one |
| C2 | It changes nothing before Windows grants administrator rights, and restarts Docker after any failure once Docker was stopped | Code reading; its first real run is on the PC |
| C3 | Old backups go only after a clean run; the newest three and the run's own stay | Stand-in run of the file plan |
| C4 | No service, page or test loses a path it uses | The cloud suites (part 2): web lint, typecheck, unit tests and build; Ruff, the OpenAPI check, pytest with and without a database |
| C5 | Every relative link in the documents resolves | `python3 tools/check_links.py .` |

## 6. Official sources

- Microsoft, [compact vdisk](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/compact-vdisk) (updated 2024-11-01): "Reduces the physical size of a dynamically expanding virtual hard disk (VHD) file"; it works on a disk that is detached or attached read-only.
- Docker, [Docker Desktop CLI](https://docs.docker.com/desktop/features/desktop-cli/) and [docker desktop stop](https://docs.docker.com/reference/cli/docker/desktop/stop/): `start`, `stop` (`--timeout`, `--detach`, `--force`) and `status`.
- No new dependency.

## 7. Data and trust-boundary changes

None to the app. The Docker clean-up runs on the owner's double-click with one administrator prompt, removes only this app's leftovers by exact name, and runs one privileged `busybox:1.37` container for `fstrim` inside Docker's own VM (no host folder mounted).

## 8. Failure and rollback

- Part 1: a backup is taken before anything changes; a failure after Docker stopped starts it again; the old backups stay unless the whole run succeeded. A disk that fails to compact is left as it was.
- Part 2: the update file's own backup and rollback tags. Removed code and scripts stay in Git history.

## 9. Q01–Q10 (affected gates)

Q-gates of [ACCEPTANCE_CHECKLIST](../../ACCEPTANCE_CHECKLIST.md#quality-gates-for-every-milestone) that apply: tests and lint (C4), documentation links (C5), deployment through the update file (part 2). No money path changes in parts 1 and 2; part 3's accounting helper gets an independent review.

## 10. Verification commands

Part 1, `OBSERVED` in the cloud (PowerShell 7.4.6 on Linux, not Windows PowerShell 5.1):

```bash
/opt/pwsh/pwsh -NoProfile -Command '$e=$null;$t=$null;[void][System.Management.Automation.Language.Parser]::ParseFile("tools/docker-cleanup.ps1",[ref]$t,[ref]$e);$e.Count'
PATH=<stand-in docker>:$PATH LOCALAPPDATA=<scratch> /opt/pwsh/pwsh -NoProfile -File tools/docker-cleanup.ps1 -Repository <scratch app folder> -KeepBackups 2 -DryRun
```

On the PC (proposed): `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\docker-cleanup.ps1 -DryRun` (read-only), then the owner's double-click on `docker-cleanup.cmd`.

## 11. Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-10-20 | The owner's go-ahead covers every cleanup item; Claude decides the items | The owner's words (§1) |
| 2026-10-20 | No table is dropped and no row deleted | The large tables are live market data; dropping history saves little and cannot be undone |
| 2026-10-20 | Other projects' Docker resources and the build cache stay | They are not this app's; the build cache is mostly another project's |
| 2026-10-20 | Keep the three newest backups, plus the one a run takes | Enough to go back past a bad update; each dump is about 0.5 GB |
| 2026-10-20 | Compaction through diskpart, not `Optimize-VHD` | diskpart is on every Windows edition; `Optimize-VHD` needs the Hyper-V module |
| 2026-10-20 | The contract rewrite and the API file split wait for M10's update 2 | Both touch files that update changes |
| 2026-10-20 | The test and tool Compose services stay | Rule 9: the build and test paths stay containerized; their images are rebuilt only when a test run needs them |
| 2026-10-20 | Dead code is found by an import walk, not by name | A module a browser fixture or the research runner still imports stays even when its name says "acceptance" |
| 2026-10-20 | The read-only fields `actions.probe`, `actions.start_workflow`, `actions.decision_probe`, `owner_startable` and `actions.start_promotion` stay for now | The web schemas, samples and database tests assert them; they go with part 3's contract rewrite |
| 2026-10-20 | The owner's approval write routes stay | The independent review: they are the owner's recovery lever (AUTONOMY_MATRIX); removing one is a change of authority, not a cleanup |
| 2026-10-20 | Each update keeps the backups of runs that stopped since the last completed one | The independent review: the rollback tags may still name the release before the first of them |
| 2026-10-20 | The history pages keep their place in the menu | Moving them is a design change, not a cleanup; not taken |

## 12. Progress

- 2026-10-20: **part 1 built** on branch `claude/project-thread-bcjt6n`: `tools/docker-cleanup.ps1` and `tools/docker-cleanup.cmd`. It parses (0 errors) and holds only ASCII. A dry run against a stand-in `docker` listed exactly the leftovers it should (an old rollback tag, two test images, a tool image, the pilot's tag, the unused volume, two untagged images; it kept `:latest` and `:before-update` of the current services and another project's image) and the two oldest of four scratch dumps, and changed nothing. `NOT RUN`: Windows PowerShell 5.1, diskpart, the Docker Desktop CLI and the administrator prompt; their first run is the owner's.
- 2026-10-20: **part 1 reviewed, hardened and run dry on the PC.** An independent review found that closing the window during the compaction could leave Docker stopped, and that Docker could start while diskpart held the disk: a hidden watchdog now starts Docker again, the wait has no deadline and prints progress, and old-file deletion reports failures and continues ([#94](https://github.com/MentorAliu/adaptive_spot_lab/pull/94)). The PC dry run (OBSERVED, 19:49 UTC, exit 0, nothing changed) found 44 old image tags, 64 untagged images of the app, 2 volumes, 33 old backups (7.5 GB) and 6 old test-run folders; it also showed 85 untagged images of the old `asl-m7-*` test stacks, now included ([#95](https://github.com/MentorAliu/adaptive_spot_lab/pull/95)); Windows PowerShell 5.1 dropped the quotes of the label template, fixed in [#96](https://github.com/MentorAliu/adaptive_spot_lab/pull/96). The dry run of the fixed main (OBSERVED, 19:55 UTC, exit 0): 44 tags, 149 untagged images, 2 volumes, 33 backups. The real run is the owner's double-click.
- 2026-10-20: **part 2 built** on branch `claude/project-thread-bcjt6n` (§4.2). VERIFIED in the cloud: ruff passes; the no-database pytest run matches main (the same 2 failures); the database suite on a scratch PostgreSQL 16 gave 3 failed and 74 errors on main and 5 failed and 74 errors on the branch, with the same errors (setup of the M1 account and replay suites in this container); the two extra failures (`test_m2_reference_checks.py::test_clock_unverified_for_minutes_stays_closed_on_one_collection`, `test_m6_agents.py::test_an_investigation_refreshes_a_source_waits_without_the_slot_and_cites_what_it_was_given`) pass when run again alone (2 passed), and the second is the known HH:59:30-HH:06 window test. Web: typecheck, lint, 266 unit tests and the API check pass; `update-model.ps1` passes every case, including the new ones for the tidy step (a mutation that drops the stopped-run guard fails its case). Links: 0 broken. An independent review found the approval write routes are the owner's recovery lever (kept), the stopped-run backups (kept), the untested tidy step (now modeled) and stale references (fixed). `NOT RUN`: the Playwright suites, PostgreSQL 17, Docker and Windows PowerShell 5.1; the update file runs them on the PC.
- 2026-10-20: **part 1 run by the owner** (OBSERVED from its record `docker-cleanup-20261020T205758Z.json`, read-only): `COMPLETE`; 195 images and volumes removed, none refused; fstrim trimmed 283 MiB; diskpart compacted in 2.6 minutes; Docker's disk file went from 339,728,138,240 to 62,084,087,808 bytes (316 GB to 58 GB); 33 old backups deleted (8,044,669,182 bytes) and the six old test-run folders; every container that ran before ran again. The owner's update right after it (`update-20261020T210511Z`, `1c2f7f2`) completed: reconciliation OK, agents' switch on, main run `2580d8ea` running on `AGENT_POLICY_V2`.
- 2026-10-20: **part 2 installed** by the owner's update (`update-20261020T213515Z`, OBSERVED read-only from its transcript): `62af44c`, no migration (schema `0015_m10_coins`), every running service recreated, reconciliation OK, pages answer, agents' switch on, main run `2580d8ea` running on `AGENT_POLICY_V2`. The new tidy step deleted 3 old backups (1.4 GB) and removed 24 old images; 3 backups remain. The GitHub branch tidy was not done this time (`git fetch` could not reach github.com); it runs again with the next update.
- 2026-10-20: **fix after a cross-check by another thread.** The stopped-run guard of the tidy step met this run's own `update.json` (saved at step 8) first and stopped there, so it protected nothing; its model case passed only when both runs shared one stamp folder (the model's `Start-Sleep` is its fake clock), and the earlier mutation check passed for the same reason. The guard now skips this run's own record folder, and the model's second run waits a real second. VERIFIED: the case passes 5 of 5 runs, the mutation that drops the skip fails it 2 of 2, the full model passes. It reaches the PC with the next update.
