# ExecPlan 0031 — M8: a simple app that runs itself

**Status: APPROVED FOR IMPLEMENTATION by the owner on 2026-10-19; not implemented.** The owner picked "Cut to essentials" on the card "Cut the app down to the protections paper trading actually needs?" at 11:37:19 UTC ([DECISIONS](../../DECISIONS.md#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031)), so §4 to §9 are M8's plan and §13 records the option not picked. Written by the project thread "Hands-off milestones" from `main` at `b7d51a6`, on the owner's messages of 2026-10-19 (§1). M7, its run and its records are not touched: M7 closed under [ExecPlan 0026](0026-m7-agent-driven-main-decisions.md) as it was ([DECISIONS](../../DECISIONS.md#2026-10-19--m7-closes-without-the-decision-probes-and-the-first-live-decision)).

Labels: `OBSERVED` (seen in code, records or the project's threads), `INFERRED`, `PROPOSED`, `NOT RUN`.

## 1. Goal and observable outcome

The owner, 2026-10-19:
- 11:08 UTC: "why am I doing all of this tinkering when you could decide for me, I don't want any of this enable, disable, start, do this do that, I want you to handle it, you have my authorization for everything";
- 11:10 UTC: "I want you do complete m7 as soon as possible and simplify the app as much as possible so I don't have to do all of this";
- 11:15 UTC: "this is to complex and honestly unecessary, why can't the app just use agents, why does it need all of this complexity ?";
- 11:37:19 UTC, the pick on the card "Cut the app down to the protections paper trading actually needs?": "Cut to essentials".

The goal: the app runs its agents on paper money by itself. The owner switched it on once and installs updates; nothing else is asked of them. Five protections stay, because on paper they are the ones that protect anything (§4.1). Everything else the owner has had to do goes, or the app does it itself.

Observable after M8:
1. After an update the agents keep running, with no click: no approval screen, no Start, no probe button, no Enable. The app records each version it runs by its hash, as `SYSTEM`, never as the owner.
2. The owner's controls are an on/off switch for the agents, Stop for the run, and Top up. The Approvals page shows history only.
3. A usage-limit refusal pauses model calls, and the app resumes by itself after the reset. Nothing latches, and no button needs pressing.
4. A new policy version starts a new segment of the same paper run, not a new experiment. The first is `AGENT_POLICY_V2`, with hourly entry checks when the app holds no position.
5. Each update is one double-click on one file. The file backs up, installs, migrates, restarts and checks, waits for the safe minutes by itself, keeps the PC awake and says what the update changes. There are no other starter files, time windows, watches or typed go-aheads.
6. Tests run in the cloud. The PC runs only the update's own checks, so there are no multi-hour test runs on the PC, and the fast lane ([ExecPlan 0029](0029-fast-lane-pc-runs.md)) is not built.

## 2. Why the app has so many layers (OBSERVED unless marked)

- **The founding rules assume high stakes.** [AGENTS.md](../../../AGENTS.md) treats the app as if real money and untrusted AI were at stake: the owner approves every permission by exact version (rule 4, line 10; [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md): "Approval is for exact versions and permission scope"), each milestone passes quality gates with test evidence (rule 13, line 19), and the standing deployment authorization excludes "enabling disabled collection/trading/agents ... changing approvals" (rule 14, line 20). Every command against the running app needs the owner's approval in chat ([DECISIONS](../../DECISIONS.md#2026-09-30--m5-a-implementation-authorized-execplan-0020), repeated by later entries).
- **Each milestone added a layer.** M3: the paper broker and ledger. M4: experiments, manifests with eight definition approvals, the owner's Start, latched pauses and activation scripts. M5: the runtime profile, capability probes, Enable and the Codex login. M6: the research envelope, source versions, sealed datasets, promotions and research activation. M7: the policy and protocol approvals, decision probes, the agent's entry pause and the experiment boundary. On top of these, the PC test harness grew windows, watches and phases to protect the M4 pilot, which ended on 2026-10-18.
- **Size on `main` at `b7d51a6`.** The API has 24 owner `POST` routes (`services/engine/app/main.py`), and every control among them requires the owner's session (`require_owner_session`, for example lines 1150-1153, 1192-1196 and 1924-1952). The engine is about 44,000 lines of Python (`services/engine/app`). `tools/` holds about 23,000 lines of PowerShell in 55 files (harness, deploy and activation scripts). The documents are about 625,000 words. By 2026-10-18 16:26 UTC M7 had taken 9.2 days, of which 21% was waiting for a go-ahead and 19 hours were failed PC runs (measured by the thread "Why M7 is so slow").
- **What the owner did to switch M7 on** (thread "Build M7" and [ExecPlan 0026 §18](0026-m7-agent-driven-main-decisions.md#18-completion-evidence)):
  - approved the research envelope;
  - composed a profile, approved it, allowed probes and started the capability probes, again after each failed run until they passed at 09:14 UTC (a usage limit, then single slipped checks);
  - double-clicked the release starter (2026-10-18 20:31 UTC) and the boundary starter, which waited for its window;
  - approved the policy and the evaluation protocol;
  - created the experiment, approved its manifest and pasted its details;
  - double-clicked the activation starter;
  - pressed Start, Start decision probes and Enable;
  - after the decision probes failed on the usage limit (11:13 UTC), would have had to start them again after the reset;
  - reported each step in the thread.
- **What an approval checks in practice.** The owner compares a 64-character hash that Claude prepared against the one on screen (thread "Build M7", 10:19 UTC). INFERRED: on paper money the approval adds a pause, not a review the owner can make.
- **Why the owner's hands are needed today.** The routes refuse anything but the owner's session. Approval rows require one (`owner_approvals.session_id ... REFERENCES owner_sessions`, `services/engine/alembic/versions/0006_m4_fixed_pilot.py:69`). The activation scripts run "ONLY on an explicit owner instruction" (`tools/pilot-activate.ps1:12`). The Claude desktop app's safety check refused an agent's activation run ([DECISIONS](../../DECISIONS.md#2026-09-30--m4-pilot-approvals-activation-and-checkpoint-execplan-0015)) and an irreversible step even after the owner allowed it ([DECISIONS](../../DECISIONS.md#2026-10-03--this-projects-old-test-runs-removed-other-projects-docker-resources-left-to-the-owner)), so threads hand the owner `.cmd` files.

## 3. Scope and exclusions

**In scope (M8):** the cuts of §4; the parts of [ExecPlan 0030](0030-agent-models-and-effort-per-role.md) that remain (the model table in code, the usage-limit block, the token summary); `AGENT_POLICY_V2` as the first version under the new rules; the rule changes of §4.9.

**Not in scope:**
- M7 and its records.
- The five protections (§4.1). They are kept, with their tests.
- Real trading of any kind: [AGENTS.md](../../../AGENTS.md) rule 1 does not change.
- Deleting history: old approvals, experiments and probe runs stay readable.
- M9 and M10. They are scoped again under the new rules afterwards.

## 4. Design (approved 2026-10-19)

### 4.1 What stays, and why

| Protection | What it protects on paper | Where it lives |
|---|---|---|
| Paper only: no exchange keys, no private exchange API | There is no route to real money, which is why the rest can go | Rule 1; no credential exists anywhere |
| The agents propose; the code fills at observed market prices with fees, in an exact ledger | Honest results: no model can invent a fill, a price or a balance | Rule 2; `app/execution`, `app/accounting.py` |
| Hard limits, and a stop on every position that works without the model | No absurd bets, and the paper account keeps its protection when a model call fails | [RISK_POLICY](../../RISK_POLICY.md); the policy's limits (two entries in any 24 hours, one per coin); rule 11 |
| Version tags on every decision and trade | Results stay comparable when versions change by themselves | [ExecPlan 0026 §5.11](0026-m7-agent-driven-main-decisions.md#511-evaluation-segments-and-comparisons) segments |
| An off switch | The owner can stop the agents, or the run, at once | Disable (the permission epoch); Stop |

Also kept, and invisible to the owner:
- least-privilege database identities;
- a backup before every update;
- reconciliation;
- the code's check of every tool call against the role's grants and schemas.

The agents still cannot change their own tools, limits or code.

### 4.2 Each layer: what it guards, and what M8 does

| Layer | Guards against | On paper, for one owner on one PC | M8 |
|---|---|---|---|
| Exact-hash owner approval of definitions, policy and protocol | An agent acting under rules the owner did not see | The owner compares hashes Claude prepared | The app records what the installed code ships as in force, as `SYSTEM` with its hash (§4.5). The screens become history |
| Experiment draft, manifest approval, Start | Results mixing configurations | Version tags do this | The app keeps one main run going and starts it itself (§4.6) |
| A new policy version needs a new experiment (0026 §5.1) | Two policies in one result | Segments do this | A new version starts a segment in the same run, and open positions keep their terms (R08) |
| Runtime profile: compose, approve, Allow probes | A model the owner did not choose | The owner delegated the model choice (10-19 08:30 UTC) | The model table in code (0030 §4.1, §4.2), with no approval |
| Capability probes (up to 70 calls) and decision probes (up to 40), gating Enable and decisions; a failure latches | A model that misuses its tools | Every tool call is checked by code anyway. The probes spent the shared allowance on 10-19 and latched on the usage limit | A short automatic check after a change (§4.7). It retries by itself and never latches. No button |
| Enable, `PROBE_ONLY` | Model calls before the checks | — | One on/off switch. An update does not turn it off. `LOGIN_REQUIRED` stays: that is the Codex sign-in |
| Research envelope and source-version approvals | Research on unapproved data or over budget | The sources are fixed endpoints set in code (`app/sources/registry.py:9-14`). The budgets protect the PC | The budgets stay in code; the approvals go |
| Promotion approval (`PROMOTION_V2`) | A research candidate reaching the main account unseen | The coordinator still decides each entry, reviewed and limited | A candidate that passes the code's evidence checks becomes eligible by itself |
| The agent's entry pause, which only the owner can resume | An agent that stops itself and resumes unreviewed | Nothing real | The pause carries an end that the agent picks from a closed set (at most 24 h). It ends by itself, the agent may lift it early, and so may the owner |
| Latched pauses: `OWNER`, `DAILY_LOSS`, `DRAWDOWN`, `INTEGRITY`, `APPROVAL_REVOKED` ([OPERATIONS](../../OPERATIONS.md), line 136) | Runaway losses, broken books | — | `DAILY_LOSS` clears at the next UTC day. `INTEGRITY` clears when reconciliation passes after a fix. `APPROVAL_REVOKED` goes with the approvals. `OWNER` stays the owner's. `DRAWDOWN` still ends the run, which is a real result, and a new run starts on the owner's word |
| Activation scripts, environment flags, identities switched on per subsystem | A subsystem touching the database before it is switched on | Every subsystem runs since M7 | The update keeps everything on. The scripts stay in the repository for manual recovery |
| Several starter files, time windows, the pilot watch | The M4 pilot's evidence, which ended on 10-18 | — | One update file (§4.4). It waits for the safe minutes by itself. The watch and the quiet windows go |
| Multi-hour PC gate runs | Bugs and slowdowns reaching the running app | On paper a bug costs paper results until it is fixed. The cloud has already run the database and browser suites on a scratch PostgreSQL ("Build M7") | Cloud tests plus the update's own checks (§4.8). Load is measured only when the engine's step path changes |
| The owner's approval in chat for every command against the running app | An agent changing the running app unasked | — | Read-only checks need no approval. Changes go only through the update file the owner double-clicks |
| The process: plans of 80,000 words, a review per batch, a decision entry per step, a STATUS of 1,900 lines | — | The Claude usage limit paused M7 for 44% of its time (10-18); INFERRED: large records drain it | Short plans, a STATUS of one screen, decision entries only for the owner's choices, and an independent review only for money paths |

### 4.3 What the owner does after M8

- **Per update:** one double-click on the file the thread names. Its window lists what changes and says when it is done, or stops at the first problem and says what it left.
- **When Codex asks:** sign in. It is the owner's own account, and Claude never signs in.
- **Rarely:** after a drawdown stop, say whether a new run starts.
- **Never:** approvals, Start, probes, Enable, pasting ids, writing "done", watching time windows, starting watches or typing go-aheads.

### 4.4 The update file

`tools/update.ps1`, started from a `.cmd` file the thread prepares, in this order:
1. The folder check. The update runs from the owner's main folder, which holds the normal app's settings, and does not assume which branch it is on: on 2026-10-19 the coordinator session reported it on `codex/m9-m10-readiness`, and the branch clean-up's switch to `main` was not confirmed. With no uncommitted changes to tracked files, the update switches the folder to `main` and fast-forwards it to `origin/main`. With any, it stops before changing anything and names the files.
2. A read-only preflight.
3. A protected backup with its SHA-256, and rollback tags.
4. Build.
5. Forward migrations.
6. Recreate the changed services.
7. Verify: the source and images that run, readiness, reconciliation `OK`, the pages answering, and the agents' switch as it was.
8. Write a record, and print what the update changes, from the release note in the commit.
9. Tidy GitHub: delete each branch that `main` already contains, never `main` and never a branch with commits `main` lacks, then list any local branch with unmerged work. Claude's cloud and device sessions are refused branch deletion, so the owner's own run does it.

It never asks for input. Before it changes anything, it waits by itself while the clock is within a few minutes of the hourly bar close. It keeps the PC awake while it runs (`SetThreadExecutionState`, read from Microsoft's reference when built: [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m8-update-1--2026-10-19-execplan-0031)).

For routine use it replaces `m7-deploy.ps1`, `m7-boundary.ps1`, `pilot-activate.ps1`, `research-activate.ps1` and `agent-activate.ps1`. They stay in the repository.

**Why one double-click stays.** The Claude desktop app's safety check refuses a Claude session's production update on the PC ([DECISIONS](../../DECISIONS.md#2026-09-30--m4-pilot-approvals-activation-and-checkpoint-execplan-0015), [DECISIONS](../../DECISIONS.md#2026-10-03--this-projects-old-test-runs-removed-other-projects-docker-resources-left-to-the-owner)). Rule 9 forbids weakening it, and it protects the PC itself, not the trading. A scheduled task that installed whatever reaches `main` would go around that check, and would run any merged change on the PC without anyone seeing it, so this plan does not propose one.

### 4.5 In-force records instead of approvals

After each update, the agent worker records every definition the installed code ships as in force, with its hash: the policy, the protocol, the profile composed from the model table, the research envelope and the source versions. Each row has actor `SYSTEM` and cites the owner's decision on this plan.

An additive migration gives `owner_approvals` and `agent_approvals` an actor column (`OWNER` or `SYSTEM`) and lets a `SYSTEM` row carry no owner session. The existing checks that read those rows stay as they are. Whether every guard of migration `0009` accepts such a row is checked when this is built (NOT RUN). The pages label `SYSTEM` rows, and no row claims the owner.

### 4.6 One continuous run

The main paper run stays `RUNNING` across updates. In M8 the engine binds the newest in-force policy version at a bar boundary, and every decision and trade records the version. Results split into segments as 0026 §5.11 already does for the profile, sources, envelope and candidates. Open positions keep their original terms (R08).

The engine's binding through the manifest's strategy slot is read first. If switching inside a run proves a large change, the fallback is that the app ends the run without flattening it (`STOPPING` until its positions close under their own terms) and starts the next one itself, with no owner step.

### 4.7 The agents: models, the usage limit and the short check

- **Models.** `MODEL_TABLE_V1` lives in code, as in [ExecPlan 0030 §4.1 and §4.2](0030-agent-models-and-effort-per-role.md#41-the-table-from-the-vendors-guidance), and the worker composes from it. No picker and no approval: the table is code the owner installs.
- **The usage limit.** [0030 §4.5](0030-agent-models-and-effort-per-role.md#45-the-usage-limit-block) applies to every model call, including the short check. It starts by reading the stored text of the 2026-10-19 refusals, read-only.
- **The short check.** One call per role, on a fixed case, that checks the output schema and the tool use.
  - It runs after a change of model, prompt, definitions, runner or account.
  - New entries wait for it to pass; exits and stops never wait.
  - After a failure it runs again by itself, with growing intervals, and after a usage-limit block clears.
  - It never latches, and every failure stays visible on the Agents page.
  - The live suites of 70 and 40 calls stay as an on-request diagnostic.

### 4.8 Tests, and the fast lane

- **Per change, in the cloud:**
  - web lint, typecheck, unit tests and build;
  - Ruff, the OpenAPI drift check and the database-free pytest;
  - the PostgreSQL pytest and browser suites on a scratch PostgreSQL, as "Build M7" ran them. That is PostgreSQL 16 against 17 on the PC; the update's checks catch what differs.
- **On the PC:** only the update file's checks. No acceptance-harness run from M8 on.
- **Load:** measured only when a change touches the engine's step path, as a cloud measurement or one PC phase on request.
- **The fast lane** ([ExecPlan 0029](0029-fast-lane-pc-runs.md)) is not needed, because the long PC runs it shortens go. It is withdrawn (the owner's pick, 2026-10-19). Its one idea that carries over, going on past a failure and listing every failure, applies to the cloud runs.

Not covered after the cut: suites the cloud cannot run, such as M6's research browser suite below its 40 GiB disk floor. A fault there reaches the running app, and is fixed forward.

### 4.9 Rule changes (made in part 1, §9)

- **[AGENTS.md](../../../AGENTS.md):**
  - Rule 3: "under an approved policy" becomes "under the policy the installed code ships".
  - Rule 4: the agents still cannot change their own tools, limits or code, the owner's switch, or a latch the code does not clear. There are no owner approvals in the app; new strategies and wider ranges arrive only in updates the owner installs.
  - Rule 13: the quality gates become the cloud tests and the update's checks, and unrun checks are still recorded.
  - Rule 14: the standing authorization covers leaving the agents, trading and research on, and the app's in-force records. The owner's double-click is the consent to each update.
  - Work discipline: read-only checks of the running app need no approval in chat.
- **[DECISIONS](../../DECISIONS.md):** [the entry of 2026-10-19](../../DECISIONS.md#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031) holds the owner's words and pick. Part 1 names the entries it supersedes, without editing them.
- **[AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md):**
  - `OWNER` keeps the off switch, Stop, Top up, the resume of an `OWNER` pause and a new run after a drawdown stop.
  - `SYSTEM` gains the in-force records, Start, the short check, the entry pause's end, and the clearing of `DAILY_LOSS` and `INTEGRITY`.
  - The model roles gain one thing: lifting their own entry pause.
- **OPERATIONS, RUNTIME_AGENTS, API_CONTRACTS, FRONTEND, ACCEPTANCE_CHECKLIST, PLANS, TESTING and COMMANDS:** changed with the part that changes them.

## 5. Requirements and tests (PROPOSED)

| ID | Requirement | Test |
|---|---|---|
| S1 | After an update the agents run again with no owner action | Worker test: new definitions, then `SYSTEM` in-force rows, then the short check, then decisions |
| S2 | No path lets a model or the browser set a fill, price, balance or limit | The existing tests, unchanged and passing |
| S3 | Stops and exits work while the model is down | The existing intent-engine and protection tests |
| S4 | Every decision and trade carries the versions in force; a policy version starts a segment in the same run | Segment and engine-binding tests |
| S5 | Off stops model work at once; Stop ends the run | The existing disable and epoch tests |
| S6 | A usage-limit refusal blocks model work without a latch and lifts after the reset; the short check reruns by itself | A runner test on the verified pattern; worker tests |
| S7 | The entry pause ends at its end; `DAILY_LOSS` clears at the next UTC day; `INTEGRITY` clears on a passing reconciliation; `DRAWDOWN` still ends the run | Engine tests |
| S8 | The update file puts its folder on `main` or stops on uncommitted changes, backs up, installs, migrates and verifies, never reports success after a failed step, and deletes only branches `main` contains | A model test with a stand-in `docker` and a scratch Git repository, as `tools/m6/pilot-check-model.ps1` does, under `pwsh` in the cloud; its first real run is the PC's first update |
| S9 | No `SYSTEM` row claims the owner, and the pages label it | View and browser tests |
| S10 | The removed owner buttons are gone, and the history pages still read | Browser tests at 390 px |

## 6. Official sources and versions

No new dependency. `SetThreadExecutionState` was read from Microsoft's Win32 reference when the update file was built (update 1, [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m8-update-1--2026-10-19-execplan-0031)).

## 7. Data and trust-boundary changes

- Authority over what the agents may do moves from the owner's per-hash approvals in the app to the code the owner installs. The model roles gain only the lifting of their own entry pause.
- New `SYSTEM` writes: the in-force rows, Start, the entry pause's end and two latch clears. One additive migration.
- **The risk the owner takes:** a bad change installed with the double-click trades on paper until it is fixed, and nobody reads a policy before it runs. On paper this costs results, not money.

## 8. Proposed file edits

- **Engine:**
  - `app/agents/`: the model table, the worker's composition, in-force records, the short check, the entry pause's end, the usage-limit block;
  - `app/execution/`: the binding of the newest version, two latch clears;
  - `app/main.py`: the owner routes that go;
  - one additive migration;
  - `services/agent-runner/runner/jsonl.py`.
- **Web:** the Agents, Approvals and Experiments pages lose their controls and keep their history; Home shows the switch.
- **Tools:** `tools/update.ps1` and its model test.
- **Documents:** §4.9; [ExecPlan 0030](0030-agent-models-and-effort-per-role.md)'s text trimmed to what §4.7 keeps. [ExecPlan 0029](0029-fast-lane-pc-runs.md) was marked withdrawn with the owner's pick.

## 9. Implementation sequence

Each part is its own pull request, merged by its thread once ready, and its own update.
1. **The rules** (documents only): §4.9, 0030's text trimmed, STATUS on one screen. 0029 and 0030 carry the pick at their top since 2026-10-19.
2. **First update:** the update file, plus the hands-off agents: the usage-limit block, the short check, no latch, and no probe button; Enable becomes the on side of the one switch. This ends the click of 2026-10-19, where the decision probes wait for a person after the usage reset.
3. **Second update:** in-force records instead of approvals, the model table with the profile the app composes from it, the pause and latch rules, and research and promotions without approvals.
4. **Third update:** one continuous run, with `AGENT_POLICY_V2` (hourly entry checks when flat) as its first version change.

The reliability and evidence items of the roadmap's M8 follow these parts, under the new rules, and are scoped again then.

## 10. Verification commands (PROPOSED)

In the cloud, for each part:
- `pnpm --dir apps/web lint`, `typecheck`, `test` and `build`;
- `uv run ruff check` in `services/engine`;
- the OpenAPI drift check;
- `uv run pytest` without a database, then with the scratch PostgreSQL;
- the browser suites.

On the PC: the update file's own checks. The exact commands go into [COMMANDS](../COMMANDS.md) once the scripts exist, and none is VERIFIED yet.

## 11. Failure and rollback

- Each update takes a backup and rollback tags, and its migration is additive.
- The owner's off switch stops the agents at any time.
- A version that misbehaves is fixed forward. Its segment stays in the history, labeled.
- If a cut turns out to have hidden a real fault, the plan records it and that protection comes back as code, not as an owner step.

## 12. Q01–Q10 (affected gates)

| Gate | Applies | Condition |
|---|---|---|
| Q01, Q02 | Yes | The pages that lose controls keep their history, labels and states at 390 px (S10) |
| Q03 | Yes | S1, S4, S7: in-force records, segments, pause and latch rules |
| Q04 | Yes | S2, S3, S5: the money path and the off switch, unchanged |
| Q05 | Yes | S6: the usage limit, visible and self-clearing |
| Q06 | Yes | S9: no row claims the owner, and the trust change of §7 is recorded |
| Q07 to Q10 | Yes | §4.8's tests replace the PC gate runs, and the documents follow §4.9. This plan proposes these gates themselves to be slimmed (rule 13) |

## 13. The option not picked: "Automate, keep all"

The card's other option, recorded as it was offered; the owner picked "Cut to essentials" instead (2026-10-19 11:37:19 UTC). Every layer stays, and the owner's work per milestone shrinks to two actions:
1. **One approval card per milestone.** It lists every hash the milestone needs (policy, protocol, profile, envelope, sources, manifest), and approving it writes each approval in its own store. Then the app itself starts the run, runs the probes within a stated call budget and enables decisions.
2. **One double-click per release.** A single starter replaces the separate deploy, boundary and activation starters.

The other parts:
- The threads check the PC themselves.
- [ExecPlan 0029](0029-fast-lane-pc-runs.md) is built as written, its watch guarding the M7 run.
- [ExecPlan 0030](0030-agent-models-and-effort-per-role.md) is built as written, its approval folded into the card.
- The usage-limit block and automatic probe reruns come with it.

The PC gate runs stay.

## 14. Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-10-19 | The owner picks "Cut to essentials" (11:37:19 UTC): cut to the five protections of §4.1 | On paper money the other layers guard nothing real, yet they cost most of the time and every click |
| 2026-10-19 | One double-click per update stays | The Claude desktop app's check on production updates protects the PC itself, and rule 9 forbids weakening it |
| 2026-10-19 | `DRAWDOWN` still ends the run and waits for the owner | It is rare, and it is the one result a person should look at |
| 2026-10-19 | `SYSTEM` rows never claim the owner | A record naming the owner for a step Claude or the app took would break rule 5 |
| 2026-10-19 | The fast lane (0029) is withdrawn | The PC runs it shortens go |
| 2026-10-19 | The model table moves from the first update to the second | A new profile needs an in-force record, which the second update brings; the first then changes no profile and needs no approval |
| 2026-10-19 | The update file checks its folder's branch itself and deletes merged branches on GitHub | The folder's branch after the branch clean-up was not confirmed, and only the owner's own run may delete a branch (the coordinator session, 11:43 UTC) |
| 2026-10-19 | Update 3 builds §4.6's fallback: the app stops the run without flattening and starts the next run itself | The engine binds a run's policy through its hashed manifest, which the run's reports and evidence cite; one run per policy version keeps each report on one version, and nothing waits for the owner |
| 2026-10-19 | The app asks for that stop only while the account holds no position, open order or exit obligation | The agents decide only for a `RUNNING` run; a stop with a position open would leave it to the engine's stops and time exits alone |
| 2026-10-19 | The agent's own pause end and early lift, and candidates as an entry basis under `AGENT_POLICY_V2`, are not built in M8 | Each needs a generation-3 tool text changed; new agent definitions change every definition hash and are not part of M8's three updates |

## 15. Progress

- 2026-10-19: PROPOSED on pull request #80, with the owner's card to decide between §4 and §13.
- 2026-10-19 11:37:19 UTC: the owner picked "Cut to essentials". The pick is recorded in DECISIONS, 0029 is marked withdrawn and 0030 trimmed at their tops, and §4.4 gained the folder check and the GitHub tidy-up. Nothing implemented or run.
- 2026-10-19: part 1, the rules (documents): [AGENTS.md](../../../AGENTS.md) rules 3, 4, 13 and 14 and its work discipline, the [AUTONOMY_MATRIX](../contracts/AUTONOMY_MATRIX.md#m8-the-app-runs-itself-execplan-0031) section on M8, the gates Q07 and Q09, [PLANS](../../PLANS.md), [STATUS](../../STATUS.md) on one screen with [its history](../STATUS_HISTORY.md) kept, 0030 trimmed, and a [DECISIONS](../../DECISIONS.md#2026-10-19--m8-part-1-the-rules-for-an-app-that-runs-itself-execplan-0031) entry naming the entries it supersedes. The model table moved to the second update (§14).
- 2026-10-19: update 1, built on branch `claude/hands-off-milestones-dsskxl` from `main` at `0e47495`, without Docker. What it holds:
  - **The agents' check** (§4.7): suite `CHECK` (migration `0010`, additive), cases `SC-02` (a decision that holds) and `SC-01` (a brief and its review), 12 calls at most. The worker starts it after a switch-on, drift or a violation, while the policy's entries wait, and after a usage-limit block; 15 minutes after a failure, doubling up to 6 hours. A pass enables the runtime and opens entries; nothing latches. New entries wait for it (`CHECK_PENDING`, and `POLICY_PAUSED` for an `ENTER`); exits never wait.
  - **The usage-limit block** ([0030 §4.5](0030-agent-models-and-effort-per-role.md#45-the-usage-limit-block)): `QUOTA_BLOCKED` with no latch, retried by the check, lifted by the first completed call; the runner's pattern marked verified from the PC's stored outcomes.
  - **One switch:** Enable is its on side and needs only the approved profile; the probe buttons are gone, their routes stay as a diagnostic. No hashed definition changed, so the profile in force stays approved.
  - **The update file** (§4.4): `tools/update.ps1`, its starter `tools/update.cmd` (copied as `update-app.cmd` into the owner's folder), and its model test `tools/m8/update-model.ps1`.
  - The documents: [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-the-agents-check-the-usage-limit-and-one-switch-execplan-0031), [API_CONTRACTS](../contracts/API_CONTRACTS.md#m8-update-1-one-switch-and-the-agents-check-execplan-0031), [FRONTEND](../contracts/FRONTEND.md#m8-update-1-the-agents-switch-execplan-0031), [OPERATIONS](../../OPERATIONS.md#the-update-file-m8), [TESTING](../TESTING.md#m8-update-1-the-agents-check-and-the-update-file), [COMMANDS](../COMMANDS.md#m8-update-1-the-agents-check-and-the-update-file--2026-10-19), AGENT_TOOL_CONTRACTS, AUTONOMY_MATRIX, CONFIGURATION and [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m8-update-1--2026-10-19-execplan-0031).
  - **Deviations.** The check has no researcher case: research needs an approved envelope and a sealed dataset and does not trade, so a case would test nothing a trade waits on. §4.7's "one call per role" is two cases over three roles (coordinator, analyst, evaluator), about seven calls. The model test runs under PowerShell 7.4.6 on Linux, where the backup folder's Windows ACL step is skipped in its scratch copy; Windows PowerShell 5.1 runs the file first on the PC.
  - **Checks** ([COMMANDS](../COMMANDS.md#m8-update-1-the-agents-check-and-the-update-file--2026-10-19)): VERIFIED in the cloud are the engine's M5 to M8 database tests on scratch PostgreSQL 16 (the 10 new pass; the 2 failures and 61 errors are those of `main`), Ruff, the OpenAPI check, the database-free pytest, the runner's tests (its three image-only failures are those of `main`), the web's lint, typecheck, Prettier, 251 unit tests, the generated-type check and build, and the update file's model test (10 scenarios, 32 expectations). NOT RUN: anything on Docker, and on the owner's PC until its first update.
  - **Independent review** (a separate session, read-only, after the tests above). Fixed:
    - A violation elsewhere now fails every open decision, so an accepted entry without a fill is withdrawn at once, as the M7 latch withdrew it; a new test fails without the fix.
    - The contract now says exits wait while the runtime is `PROBE_ONLY`, where no decision runs and only the engine's stops act.
    - The update file now also recreates a service whose Compose settings changed without a new image, keeps rollback tags only after a stop that had set them, reads git's output apart from its warnings, deletes a GitHub branch only at the tip it checked, and migrates the research stores on every run. The model test has two more scenarios for these.
    - Not changed: Git Credential Manager may show its sign-in window if its token expired; the update waits for it rather than failing.
- 2026-10-19 17:01 to 17:13 UTC: update 1 installed on the PC by the owner's double-click on `update-app.cmd`. Its record (`.cache/deployments/update-20261019T170505Z/update.json`) reads `COMPLETE` at `18cdad3`: backup taken, `0009` to `0010_m8_short_check`, eleven services recreated, the api ready, reconciliation OK, the pages answering and the agents' switch on (OBSERVED from its transcript and record). Its transcript showed one fault, fixed in update 2: Windows PowerShell 5.1 ignores `-Include` beside `-LiteralPath`, so the search for the previous update read every file under `.cache/deployments`, the half-gigabyte database dumps included; the two searches now filter by name.
- 2026-10-19: update 2, built on the same branch from `main` at `18cdad3`, without Docker. What it holds:
  - **In-force records** (§4.5): migration `0011` (additive) gives both approval tables an `actor`, and the agent worker records as `SYSTEM`, after each update, every execution definition the code ships, the research envelope and the code-owned source versions, never over the owner's latest `REJECT` or `REVOKE`.
  - **The model table** ([0030 §4.1, §4.2](0030-agent-models-and-effort-per-role.md)): `MODEL_TABLE_V1` in code, bound by the profile's hash; the app composes the version-4 profile from it and the discovery, records it in force, and carries the owner's switch to it (the agents' check then enables it). The compose form, its route and the owner's profile approval are gone.
  - **Promotions:** an entry-basis request that passes the B6 rules is approved by `SYSTEM`; one outside the policy's sets stays pending.
  - **Pauses and latches** (§4.2): the agent's entry pause ends after 24 hours; `DAILY_LOSS` clears at the next UTC day and `INTEGRITY` on a passing reconciliation; a main run with no cause left resumes by itself. `OWNER` and `DRAWDOWN` are unchanged.
  - **Pages:** Agents, Approvals (with Research and sources), Policies and the texts of Research, Evidence, Decisions and Experiments show history and who recorded it; only the experiment manifest keeps its decision until update 3.
  - The documents: [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-in-force-records-the-model-table-and-pauses-that-end-execplan-0031), [API_CONTRACTS](../contracts/API_CONTRACTS.md#m8-update-2-in-force-records-execplan-0031), [FRONTEND](../contracts/FRONTEND.md#m8-update-2-history-instead-of-approvals-execplan-0031), [RISK_POLICY](../contracts/RISK_POLICY.md#m8-latch-clears-execplan-0031-update-2), [TESTING](../TESTING.md#m8-update-2-in-force-records-and-latches-that-clear), [COMMANDS](../COMMANDS.md#m8-update-2-in-force-records-and-latches-that-clear--2026-10-19), AUTONOMY_MATRIX, AGENT_TOOL_CONTRACTS, OPERATIONS and [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m8-update-2--2026-10-19-execplan-0031).
  - **Deviations, until update 3:** the pause ends at a fixed 24 hours (the agent's own end and lift need `AGENT_POLICY_V2`, and generation 3's hashed tool text "only the owner resumes entries" stays); the owner's approval routes stay as a recovery lever with no buttons, so `APPROVAL_REVOKED` can still latch; the evaluator falls back to `medium` without `high`; 0030's token summary and "Home shows the switch" (§8) are not built.
  - **Checks** ([COMMANDS](../COMMANDS.md#m8-update-2-in-force-records-and-latches-that-clear--2026-10-19)): VERIFIED in the cloud are migration `0011` up, down and up; the whole engine suite on scratch PostgreSQL 16 (the 16 new cases pass; two older tests that pinned what this update changes were updated and pass; the remaining failures and errors are `main`'s on that cluster), Ruff, the OpenAPI check, the database-free pytest, the web's lint, typecheck, Prettier, 262 unit tests, the generated-type check and build, and the links. M7's browser selections on a scratch stack (`@decisions` 12 passed, `@profile` 1 passed), with the decision samples rewritten from this API. NOT RUN: anything on Docker, the M4 to M6 browser suites, and the owner's PC until its second update.
  - **Independent review** (a separate session, read-only; nothing blocking). Fixed:
    - An `INTEGRITY` latch a NAV check opened is no longer cleared by a later passing reconciliation, which proves only the newest valuation right; it waits for an update. A new test fails without the fix.
    - The worker's in-force records take the owner route's lock before reading the latest decision, so an owner's revocation cannot slip between; `0011`'s guards also refuse a `SYSTEM` approval after the owner's no; the Recorder writes one approval table per transaction, so no lock order inverts.
    - A profile with a role the discovery cannot serve is stored with its unset list, so the Agents page shows why nothing is in force; the automatic resume reads the account's flags afresh; the 24-hour pause end looks only at live runs; the profile's data scope no longer names owner-approved sources; SECURITY and DATA_CONTRACTS now say what update 2 changed.
    - Definitions are recorded through `asl_m8_record_definition`: the agent identity keeps no privilege on `owner_approvals`, as the M5 to M7 privilege tests require.
    - Not changed: the resume after a cleared latch waits for the next step (fail-safe); the database does not refuse an `OWNER` profile approval (the route does, with `PROFILE_RECORDED_BY_THE_APP`).
- 2026-10-19 17:34 to 17:41 UTC: update 2 installed on the PC by the owner's double-click on `update-app.cmd`. Its record (`.cache/deployments/update-20261019T173426Z/update.json`) reads `COMPLETE` at `2834026`: backup taken, `0010` to `0011_m8_in_force`, eleven services recreated, the api ready, reconciliation `OK`, the pages answering, the agents' switch on (`PROBE_ONLY`, `CHECK_PENDING`, which the agents' check ends by itself). Its last step deleted the merged branch `claude/hands-off-milestones-dsskxl` on GitHub; update 3 pushes it again (OBSERVED from its record and transcript, read-only).
- 2026-10-19: update 3, built on the same branch from `main` at `2834026`, without Docker. What it holds:
  - **`AGENT_POLICY_V2`** ([STRATEGIES](../contracts/STRATEGIES.md#agent_policy_v2-hourly-entry-checks-m8-update-3-proposed)): V1 with a decision at every finalized hourly bar, installed by migration `0012` (additive) and recorded in force by the agent worker.
  - **The run the app keeps going** (§4.6, `app.experiments.runs`): the main account's execution worker stops a run whose policy a newer one replaced, once the account holds no position, without flattening; drafts the next run of the policy in force with the previous cost scenario; records its manifest in force; marks it ready and starts it. The engine applies the app's requests as the owner's. The owner's Stop, discard and pause, a drawdown stop and the owner's rejection of a manifest stay the owner's.
  - **Pages:** Experiments shows who created each run and starts a new one from the policy in force; a run's detail lists the app's requests beside the owner's; Approvals offers no decision on a manifest the app keeps, only on the reference's.
  - The documents: [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-the-main-run-the-app-keeps-going-execplan-0031), [API_CONTRACTS](../contracts/API_CONTRACTS.md#m8-update-3-the-run-the-app-keeps-going-execplan-0031), [FRONTEND](../contracts/FRONTEND.md#m8-update-3-the-run-the-app-keeps-going-execplan-0031), [TESTING](../TESTING.md#m8-update-3-the-run-the-app-keeps-going), [COMMANDS](../COMMANDS.md#m8-update-3-the-run-the-app-keeps-going--2026-10-19), AUTONOMY_MATRIX, AGENT_TOOL_CONTRACTS, STRATEGIES, OPERATIONS, DATA_CONTRACTS, ROADMAP and [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m8-update-3--2026-10-19-execplan-0031).
  - **Deviations** (§14): runs follow each other instead of one run switching at a bar boundary; the switch waits for a flat account; update 2's fixed 24-hour pause end stays, and the agent's own end and early lift are not built; under V2 a promoted candidate is not an entry basis. Hourly decisions cost up to 24 decisions a day with no position instead of 4 (not measured).
  - **Independent review** (a money path changes): four findings and smaller notes, all fixed before the merge. The switch now waits for a flat account, so a position stays with the policy that opened it; an owner's request after the app's stop, and the owner's revocation of the run's manifest, keep the next run for the owner; the run keeper takes the owner route's lock before the run; a draft of other code is discarded only when nothing waits on it; a rejected start is retried with a growing wait (up to 4 hours). Running the whole suite then showed `0012` letting the execution identity stop a ready run of the reference: the app now readies or discards only a run of an operating policy.
  - **Checks** ([COMMANDS](../COMMANDS.md#m8-update-3-the-run-the-app-keeps-going--2026-10-19)): migration `0012` up, down and up; the whole engine suite, then the changed and targeted modules again after the fixes (every failure left is `main`'s); ruff, OpenAPI, the web checks and build; M7's `@decisions` browser selection `12 passed`. NOT RUN: Docker, PostgreSQL 17, R19 and the PC until the owner's double-click.
- 2026-10-19 18:57 to 19:12 UTC: update 3 installed on the PC by the owner's double-click on `update-app.cmd` (it waited for a quiet minute until 19:05). Its record (`.cache/deployments/update-20261019T190515Z/update.json`) reads `COMPLETE` at `3ee103a`: backup taken, `0011` to `0012_m8_one_run` (and the research stores), eleven services recreated, the api ready, reconciliation `OK`, the pages answering, the agents' switch on (`PROBE_ONLY`, `CHECK_PENDING`). Its last step deleted the merged branch on GitHub (OBSERVED from its record and transcript, read-only). The main run's move to `AGENT_POLICY_V2` was not observed: the app's database is not reachable from the update records. With it, M8's three updates are installed; M8's acceptance and the go-ahead for M9 are the owner's.
