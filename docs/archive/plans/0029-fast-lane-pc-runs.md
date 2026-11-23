# ExecPlan 0029 — The fast lane for PC test runs from M8 on

**Status: WITHDRAWN 2026-10-19; never built.** The owner picked "Cut to essentials" for M8 at 11:37:19 UTC ([DECISIONS](../../DECISIONS.md#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031)): the multi-hour PC gate runs this plan would shorten go, so it is not needed ([ExecPlan 0031 §4.8](0031-m8-simple-app-that-runs-itself.md#48-tests-and-the-fast-lane)). Its one idea that carries over, going on past a failure and listing every failure, applies to the cloud test runs. The pick supersedes the owner's choice of the fast lane on 2026-10-18 ([DECISIONS](../../DECISIONS.md#2026-10-18--the-fast-lane-for-pc-test-runs-from-m8-on)). This plan stays as the record of the design. Earlier status (2026-10-18): PROPOSED; to be built after M7 was switched on and before M8's first run on the owner's PC, as tooling rather than an M-numbered milestone. Written by the project thread "Why M7 is so slow" from `main` at `be495c4`.

Labels: `OBSERVED` (seen in code or records), `INFERRED` (reasoned from observations), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

## 1. Goal and observable outcome

M7 needed nine runs on the owner's PC. Six of its seven full runs failed, and every fix started every phase again. A full gate run takes about 7 hours (the decision's context). The goal: a fix costs the PC time of what it changes, not of a whole run, and no pass is accepted that the current files did not earn.

Observable on the owner's PC, for a profile with the fast lane on (M8's is the first):
1. After a fix, the next run runs Build, the phases whose fingerprint changed, the phases those need (§4.4), then SecretScan and Report. Every other Required phase keeps the pass of an earlier run of the same profile. Report lists each kept pass with the run, commit and time that earned it.
2. A change the fast lane cannot tie to fewer phases reruns every phase.
3. A run that meets a failed phase goes on with every phase that does not need it, and ends with a list of every failure.
4. Each phase's time reservation comes from its measured durations.
5. The owner starts one watch per milestone, and it stops any running test stack of that milestone. The owner types one standing go-ahead per milestone.
6. With the fast lane off (the `m6` and `m7` profiles), every check gives the result it gives today.

## 2. Current facts (OBSERVED in code at `be495c4`)

- **One run, one tree.** `Prepare` writes `.cache/<profile>/<run>/manifest.json` (`tools/lib/acceptance-harness.ps1:284-329`). `Get-SourceSnapshot` (108-130) hashes the working-tree bytes of the files under `apps/ services/ tools/ tests/ docs/`, `compose.yaml`, the package files and `.dockerignore`. `Get-M6TreeDigest` (`tools/m6/api.psm1:54-76`) makes one digest of that list without `docs/`. It includes `tools/`, so any harness edit changes it. M7-A is accepted on every phase on one fresh run and one image (M7-OD9, owner decision of 2026-10-09, `tools/profiles/m7.psd1:62`). That rule stays M7's.
- **Attempts.** Under the heavy lock, `Start-PhaseAttempt` (152-185) refuses a phase if a harness file changed after the process loaded it (the hashes of 56-65). It then writes `attempts/<Phase>-<stamp>-<pid>.json` with the tree digest. `Complete-PhaseAttempt` (221-270) adds the end digest and the outcome.
- **Records.** `Write-M6Record` (`api.psm1:23-40`) writes a `VERIFIED` result as `<Name>.json` and anything else as `<Name>-failed-<stamp>.json`. No record names the files its phase read.
- **Report** (`tools/m6/report.psm1:1001-1563`) accepts a run only when:
  - every Required phase has a `VERIFIED` record of that run, made after that run's Build and on Build's images;
  - Build saw no uncommitted change;
  - every attempt's digests equal Build's tree digest;
  - no phase was started again after an attempt that passed.
  A failed or interrupted phase may be rerun in the same run on the same tree ([2026-10-07](../../DECISIONS.md#2026-10-07--m6-b9-a-full-test-at-the-21-day-cap-and-reruns-in-an-accepted-run)). Nothing is carried from one run to another.
- **The gate.** Report refuses any run that started an activation-gate phase (1269-1278). A gate's evidence is its phase records ([COMMANDS](../COMMANDS.md), the gate run `m7-g1e`).
- **What a phase runs.** A phase's test files are listed in its module (for example `tools/m6/engine.psm1:185-188`, `tools/m6/agents.psm1:201-222`), not in the profile. Only Build's static tests and lint are profile data (`tools/profiles/m7.psd1:57-61`).
- **Images.** Build makes the run's images. Later phases look them up by name and compare their IDs with Build's record (`api.psm1:42-52`). Some phases build images that others need: Generate for `Checks`, and BrowserResearch and BrowserDecisions for their error phases.
- **Reservations.**
  - A phase's `Window` in the profile is the minutes it reserves inside HH:07-HH:58 UTC (`Test-HeavyWindow`, `acceptance-harness.ps1:132-147`).
  - DecisionSaturation reserves 50 minutes for its setup and 50 for its measurement, each in its own window (`tools/m6/performance.psm1:1155-1186`).
- **One failure ends a run.** The harness runs one phase per process. The sequence on the PC is a script the PC session writes and does not commit, and the run stops at the first failure ([ExecPlan 0026 §18](0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1a-and-the-held-steps-cost-2026-10-17-and-18)).
- **The watch** (`tools/m6-pilot-watch.ps1`) is bound to one run:
  - it needs that run's manifest to start;
  - it compares every reading with the baseline it took at its start;
  - it runs for at most 96 hours;
  - on a difference, it runs `-Phase Stop` for its own run only (lines 255-268).
  Nothing in the harness checks that a watch is running. The PC session waits for the owner's "watch started" ([2026-10-11](../../DECISIONS.md#2026-10-11--the-owner-starts-the-pilot-watch-for-the-m7-run-on-the-pc)).
- **No test runs the harness code itself.** `tools/profiles/check-profiles.ps1` checks the profiles' values. The harness refuses any PowerShell but Windows PowerShell 5.1 (`acceptance-harness.ps1:51-53`), and the cloud container has none.

## 3. Scope and exclusions

**In scope:**
- the shared harness: `tools/lib/acceptance-harness.ps1`, `tools/m6/*.psm1` and a new `tools/lib/FastLane.psm1`;
- a committed sequence script;
- `tools/profiles/check-profiles.ps1`;
- the watch: `tools/m6-pilot-watch.ps1`, and its stop target in `tools/lib/Research.psm1`;
- the operator documents: TESTING, COMMANDS and OPERATIONS.

**Not in scope:**
- M7, `m7.psd1`, M7's records and its gate. M6 likewise.
- What the watch checks once the M4 pilot has ended. M8's plan sets it, and the milestone watch waits for it (§4.6).
- Anything that stays as it is today:
  - every budget, judgment or check inside a phase;
  - the quiet window HH:58-HH:07 UTC and one heavy stack at a time;
  - the watch's stop rule, and the owner's `-Execute` of it;
  - the approvals in the application;
  - the normal application.
- A finer split of the engine's own code by its imports. It is not in this version (§4.2).

## 4. Design (PROPOSED)

### 4.1 Fingerprints

A phase's fingerprint is one SHA256 over the sorted `path sha256` lines of its input files (§4.2). The list and the hashing are the snapshot's, as today. Added to it:
- the phase's profile entry, without the scheduling keys `Window`, `StartFrom`, `StartUntil` and `Label`;
- the fingerprints of the phases it needs (§4.4);
- the content listing of each image it uses (§4.3).

The attempt file and the record both carry the fingerprint and the list of files it covers.

### 4.2 Which files count for a phase

The decision's rule: a file counts for a phase unless the harness can show that the phase does not read it. A file it cannot tie to fewer phases counts for every phase.
- **Every phase:**
  - the profile's shared keys, the entry script and `acceptance-harness.ps1`;
  - `tools/lib/*.psm1`, `isolation.psm1` and `cleanup.psm1`;
  - `compose.yaml`, `.dockerignore` and the root package files;
  - every file of the snapshot that no rule below ties to fewer phases.
- **Product, by component.** A phase names its components in the profile.
  - The engine (`services/engine/` without `tests/`: its code, migrations, `pyproject.toml`, `uv.lock` and Dockerfile) counts for every phase that runs the engine.
  - `apps/web/` counts for the phases that build or drive the web.
  - `services/agent-runner/` counts for the agent phases.
- **Tests.** A phase's test files move into its profile entry (`Tests`), and its module reads them from there, so the list that is fingerprinted is the list that runs.
  - A test file named there counts for its phases.
  - Every other file under `services/engine/tests/` (helpers, `conftest.py`, fixtures) counts for every engine phase.
- **Harness modules.** The module that holds a phase's function counts for the phase. So does every module whose functions that function reaches, found with the PowerShell parser's syntax tree. If the tree cannot resolve a call (a script block, or a command name built at run time), every module counts.
- **Documents.** `docs/` counts for no phase, as today.

INFERRED from these rules:
- A fix in one phase's test file or harness module reruns that phase.
- A web fix reruns the web phases.
- A fix in the engine's code reruns every engine phase, the long measurements among them.

A finer split of the engine's code waits until M8's runs show how often engine fixes rerun everything.

### 4.3 Images

Every run still starts with Build: the images are named per run, and Clean removes them by exact name. A kept pass was earned on an earlier run's images. So Build records a content listing for each image: the base image digest and the installed Python, Node and operating-system packages. A kept pass needs the same listing for every image its phase uses. If an unpinned package changed, the phases on that image rerun.

### 4.4 What a run runs

- A phase *needs* the phases whose results or images it uses (the profile key `Needs`). Everything needs Build. `Checks` needs Generate, the error phases need their browser phases, and `PerformanceBrowser` needs `PerformanceApi`.
- A run runs:
  1. Build;
  2. every Required phase without a kept pass, and every phase those need, since images are per run;
  3. SecretScan and Report, which never keep a pass.
- If a phase with a kept pass runs again because another phase needs it, the new result replaces the pass.

### 4.5 Report and the gate

Report accepts a Required phase on one of two grounds:
- a `VERIFIED` record of this run, judged as today;
- a kept pass: a `VERIFIED` record of an earlier run of the same profile, where
  - its fingerprint equals the phase's fingerprint on this run's tree;
  - its own run met today's checks for it: a clean Build, its attempts on that Build's tree, and its last attempt returned;
  - its record and attempt files still have the hashes stored with the pass.

Report lists each kept pass with its run, commit and time.

For a profile with an activation gate, a new `GateReport` operation judges the gate phases the same way, on the build to be activated. The decision's condition, that a kept pass counts when its fingerprint is that of the activated build, is then checked by code.

### 4.6 The watch for a milestone

`tools/m6-pilot-watch.ps1` gains a milestone mode: `-Milestone m8` in place of `-RunId`. In that mode:
- it writes to `.cache/m8/watch/` and needs no manifest to start;
- on a difference, it stops every running `asl-m8-` project by its exact name, found the way the harness finds them today (`acceptance-harness.ps1:187-204`);
- it writes a heartbeat at every reading, and the sequence starts a phase only while that heartbeat is fresh, so no phase starts unwatched;
- `-MaxHours` may go up to 336.

The owner starts it once, at the milestone's first run. It is started again only after the PC restarts, or after an owner-approved step on the normal application, which gives it a new baseline.

What it compares stays as it is today until M8's plan sets what it guards after the pilot. It is not used beside M8's runs before that.

### 4.7 The sequence and its go-ahead

`tools/acceptance-sequence.ps1 -Profile m8 -RunId <run>` is committed and runs on Windows PowerShell 5.1.
1. It prepares the run and lists each phase as kept, to run, or skipped.
2. It runs the phases one per process, in profile order, with `-WaitForWindow`.
3. When a phase fails, it stops the run's stacks with `-Phase Stop` and marks the phases that need the failed one as skipped because of it. Then it goes on with the rest.
4. It ends with Clean and a list of every failure.

The PC session runs it under one standing go-ahead, which the owner types in that session's thread at the start of the milestone. Draft, for the owner to paste:

> Standing go-ahead for M8's test runs on my PC: run the acceptance sequence whenever a fix is ready, keep the passes the fast lane allows, and rerun a failed phase after its fix, until M8 is accepted. It does not cover starting the watch, approvals in the application or the normal app.

### 4.8 Reservations from measurements

The `Window` values and DecisionSaturation's two reservations become profile values set from measured durations:
- the longest of the phase's last three passed attempts, plus 20 percent and at least 3 minutes;
- never past the end of the window.

A helper prints the proposed values from the run roots, and the profile change is a commit. Scheduling keys do not count in fingerprints (§4.1), so a new reservation reruns nothing.

## 5. Requirements and tests (PROPOSED)

| ID | Requirement | Test |
|---|---|---|
| FL1 | A change to a file reruns every phase it counts for, and only those | Unit checks of `FastLane.psm1` on a synthetic tree, with one change per file class and the expected set of phases. The classes: the shared core, each component, a named test file, a test helper, each harness module, a document and a new file no rule claims |
| FL2 | An unclear case reruns | A run-time call in a phase function makes every module count. A new file no rule ties counts for every phase |
| FL3 | A kept pass needs the same fingerprint, the same image listing and unchanged evidence files | Report on copied run roots: change each in turn and expect a refusal |
| FL4 | With the fast lane off, results are today's | `check-profiles.ps1` keeps the `m6` and `m7` values. Report on copies of a real M7 run's records gives the same verdict as before |
| FL5 | One failure does not hide another | The sequence on a run where one phase fails on purpose: the phases that need it are skipped, the rest run, and every failure is listed |
| FL6 | No phase starts unwatched | The sequence refuses to start a phase while the heartbeat is stale |
| FL7 | The milestone watch stops every running stack of the milestone | A model of the watch with a stand-in `docker`, as `tools/m6/pilot-check-model.ps1` does |
| FL8 | Reservations follow measurements | The helper's values on M7's attempt durations. A change to `Window` alone keeps every pass |

## 6. Official sources and versions

No new dependency.
- Windows PowerShell 5.1, as today.
- The parser `[System.Management.Automation.Language.Parser]::ParseFile` already runs under 5.1 in this repository ([COMMANDS](../COMMANDS.md)). The parts of its syntax tree that §4.2 uses will be checked against the installed 5.1 when this is built, and recorded in [INTEGRATION_EVIDENCE](../../INTEGRATION_EVIDENCE.md). Until then they are NOT RUN.
- `Get-FileHash` and SHA256, as today.

## 7. Data and trust-boundary changes

- No product code, schema or data changes, and nothing addresses the normal application.
- New files stay under the gitignored `.cache/`.
- A kept pass is as trustworthy as the records it points to: local files on the owner's PC. Their hashes guard against accidental change, not against a deliberate edit, as today.
- The watch's stop reaches every running test stack of the milestone, instead of one run's.
- By the owner's decision, the standing go-ahead replaces the go-ahead the owner typed for each run.

## 8. Proposed file edits

- `tools/lib/FastLane.psm1` (new): fingerprints, the file rules of §4.2, and kept passes.
- `tools/lib/acceptance-harness.ps1`: fingerprints in attempts and records, image listings in Build, and `GateReport`.
- `tools/m6/report.psm1`: kept passes (§4.5).
- `tools/m6/engine.psm1`, `agents.psm1`, `migration.psm1` and `browser.psm1`: read test lists from the profile when it holds them. Today's lists stay for `m6` and `m7`.
- `tools/acceptance-sequence.ps1` (new), `tools/m6-pilot-watch.ps1` and `tools/lib/Research.psm1`: §4.6 and §4.7.
- `tools/profiles/check-profiles.ps1`: the new keys, with `m6` and `m7` unchanged.
- `docs/TESTING.md`, `docs/COMMANDS.md` and `docs/OPERATIONS.md`: the fast lane and the milestone watch.
- M8's profile, written with M8's plan, gets `FastLane`, `Components`, `Tests`, `Needs` and its measured windows.

## 9. Implementation sequence

1. After M7 is switched on: `FastLane.psm1` and its unit checks, on synthetic trees.
2. Records, attempts, Build's image listings and Report's kept passes, with the Report checks on copies of an M7 run (FL3, FL4).
3. Test lists as profile data, for the phases M8 keeps.
4. The sequence script and the watch's milestone mode (FL5 to FL7).
5. Reservations (FL8).
6. One pull request, which the thread merges once its checks pass.
7. The PC part of §10, under the owner's go-ahead in the PC session's thread, before M8's first measured run.

## 10. Verification

- **In the cloud:**
  - `python3 tools/check_links.py .`;
  - the parser and ASCII checks with PowerShell 7, if it can be installed. This is not acceptance evidence.
- **On the owner's PC (Windows PowerShell 5.1):**
  - `check-profiles.ps1` and the unit checks;
  - the Report checks on copies of an M7 run;
  - the sequence's failure case;
  - the watch model.
- **M8's first two runs:** the first is the first fast-lane run. The second, after a commit that changes only documents, must run only Build, SecretScan and Report.

The exact commands go into COMMANDS once the scripts exist. None is VERIFIED yet.

## 11. Failure and rollback

- The fast lane is a profile key. With it off, a profile works as it does today: one run, every phase, and Report as now.
- Rerunning a phase is always allowed.
- If a kept pass turns out to have hidden a fault:
  1. the plan records it;
  2. the affected phases rerun;
  3. the file rule that missed it is made wider.

## 12. Q01-Q10 (affected gates)

| Gate | Applies | Condition and planned evidence |
|---|---|---|
| Q05 | Yes | No kept pass on a changed or unclear input, and failures stay visible (FL1 to FL3, FL5) |
| Q07 | Yes | The harness's own checks, FL1 to FL8 |
| Q08 | Yes | Report lists kept passes, the sequence lists every failure, and the watch writes a heartbeat |
| Q09 | Yes | `check-profiles.ps1` validates the new keys, and rollback is by the profile key (§11) |
| Q10 | Yes | TESTING, COMMANDS and OPERATIONS are updated, with no new dependency |
| Q01 to Q04, Q06 | No | No change to the user interface, product data, the application's security surface or a product budget |

## 13. Decision log

- 2026-10-18: the owner chose the fast lane ([DECISIONS](../../DECISIONS.md#2026-10-18--the-fast-lane-for-pc-test-runs-from-m8-on)).
- 2026-10-18, this plan:
  - Build, SecretScan and Report always run.
  - Scheduling keys do not count in fingerprints.
  - Harness modules are tied to phases by the parser, and test files by the profile.
  - The engine's code is one component in this version.
  - `m6` and `m7` stay as they are.
  - The two run changes that need no decision are built here: going on past a failure, and measured reservations, the latter under the [2026-10-08 ask for the least waiting](../../DECISIONS.md#2026-10-08--m6-b9-the-owner-asks-for-the-least-waiting).

## 14. Progress and completion evidence

- 2026-10-18: PROPOSED. Not implemented, and nothing run.
