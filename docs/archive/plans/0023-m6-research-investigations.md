# ExecPlan 0023 — M6 coordinated investigations and isolated research

**M6 is read as closed as of 2026-10-19, with M7, by the owner's decision to close M7; the live walk-through of §13.3 is a follow-up (an interpretation the owner can overrule, [DECISIONS](../../DECISIONS.md#2026-10-19--m7-closes-without-the-decision-probes-and-the-first-live-decision)).**

**Status: APPROVED FOR IMPLEMENTATION by the owner on 2026-10-03, with the recommendation of every decision in §3.3 ([DECISIONS](../../DECISIONS.md#2026-10-03--execplan-0023-approved-for-implementation-with-the-recommended-decisions)). B0 is complete: contracts and the authoring harness scaffold are IMPLEMENTED; documentation, schema-preview and engineering measurements are VERIFIED within their stated scope (§18). B1, B2, B3, B4, B5, B6, B7 and B8 acceptance are VERIFIED complete within their batch scopes, including review and cleanup (§18). B9: the acceptance evidence for M6-A, in the scope the owner decided on 2026-10-08, is VERIFIED on run `m6-b9s` (§18). B10: M6-A is deployed inert to the normal application since 2026-10-08, 22:20 UTC, VERIFIED read-only (§18). M6-B has not begun and is the owner's.** A section marked `PROPOSED` describes the approved design until its implementation evidence is recorded. Second draft of 2026-10-03. Owner request of 2026-10-03, after M5 was closed ([DECISIONS](../../DECISIONS.md#2026-10-03--m5-closed-on-the-capability-probes-live-token-refresh-becomes-a-follow-up-execplan-0020)): "merge PR #16 and draft the M6 plan". The plan follows [ROADMAP](../../ROADMAP.md) M6 as written and treats M7 and M8 only as interfaces.

**How this draft was made.** Read-only:
- No application file was edited, and no build, test, migration, install, login or model call was run.
- No Docker or Compose command was run for it, against the normal `adaptive-spot-lab` project or any other.
- `.env`, `secrets/` and `codex_home` were not read.
- The contracts in `docs/` and the code at `72ba76f` were read. A read-only search mapped the M5 code, and the facts in §2 were checked in the files they cite.
- `main` has since moved to `ed9fae3` (ExecPlan 0022, the market worker only). None of the files cited in §2 changed.
- Four official pages were read on 2026-10-03, and two public release feeds were listed once through the authenticated `gh` client (§6).
- An independent read-only review then checked the first draft against the contracts and the code. Its findings were verified in the code and changed the design; §16 lists them.

Labels: `OBSERVED` (seen in code, documents or command output), `INFERRED` (reasoned from observations), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

## 0. Summary

M5 gave the application a bounded model runtime with two working roles and three read tools. M6 adds the research loop around it. It adds **no trading authority**: trade intents, the agent-driven main policy and main approval of strategies are M7.

**What M6 delivers**
- **All four roles** with their own grants, prompts and typed artifacts: ANALYST, RESEARCHER, EVALUATOR, COORDINATOR.
- **Approved external evidence.** A source registry, a fetcher that reaches only owner-approved sources, an evidence corpus with a bounded search, and fact-versus-hypothesis records.
- **Declarative candidates.** A registered, non-executable candidate grammar that the existing paper engine evaluates through a strategy interface.
- **Isolated experiments on recorded quotes.** A research runner with its own PostgreSQL cluster and no route to the owner's database runs each candidate on the existing engine through the existing replay path. Every trial is kept. The last part of each dataset is a locked holdout, and a research workflow cannot see market data from it.
- **Shadows.** A candidate frozen at a known time is replayed over the observations published after that time, in its own virtual portfolio.
- **Reviews and promotion requests.** The evaluator reviews actual results. A promotion request goes to the owner and stays pending; M6 cannot approve one.
- **Research, evidence and approval pages.**

**What it does not deliver:** research on long bar history. The first draft's way of doing it cannot work on the unchanged engine (§5.12). It needs its own plan.

**Delivery, in two parts as for M5**
- **M6-A (implementer).** Build it, pass an isolated acceptance on synthetic and recorded data, deploy it inert beside the pilot.
- **M6-B (owner-gated, hours not days).** Approve the research envelope, the source version and the new runtime profile; activate; run the probes and one live walk-through.

**Completion** is the owner's decision M6-OD7. As recommended, M6 is complete when M6-A is deployed and the live walk-through of §13.3 is recorded, and no completion criterion depends on calendar time. That leaves one clause of the roadmap gate with isolated evidence only at completion.

**Seven decisions for the owner are in §3.3**, each with a recommendation. On 2026-10-03 the owner took every recommendation.

## 1. Goal and observable outcome (PROPOSED)

**M6-A — capability, shown in isolated stacks**
- An ANALYST workflow searches the corpus, asks for a refresh of a registered source, and records an assessment that cites the evidence items it was given. A request for an unregistered source, or for a URL, has no effect.
- A RESEARCHER workflow, held to its dataset's information cutoff, records a hypothesis, registers a candidate in the grammar and requests an experiment. The workflow waits without holding the model, and resumes when the result has been written.
- The research runner runs the candidate on the paper engine in a research database and records a result that is a pure function of its inputs.
- An EVALUATOR child reads the actual results, including the holdout the researcher cannot see, and records a review bound to their hashes.
- An eligible candidate is scheduled as a shadow and advanced as new observations are staged.
- A COORDINATOR workflow requests a promotion. The request is pending in the owner's inbox. No path approves it.
- Every negative case is rejected with no side effect (§4, §10).
- A saturated research runner does not push market publication or paper execution past their existing budgets.

**On the normal app after M6-A**
- Schema `0008`; `asl_research` and `asl_source` NOLOGIN; research and source services built and not started; `ASL_RESEARCH_ENABLED` and `ASL_SOURCES_ENABLED` at `0`.
- The pilot's containers, images, lease epoch and evaluation segment unchanged.
- The agent runtime needs a new profile approval before any model call, because the code-owned definitions changed (§5.8).

**M6-B — activation and live evidence**
- The owner's approvals and activation, the first staging, the capability probes on the new profile, and the walk-through of §13.3.

## 2. Current repository facts (OBSERVED at `72ba76f`)

**Go/no-go**
- M5 is complete by the owner's decision of 2026-10-03. Its token-refresh check is a follow-up due on or after 2026-10-10 11:20 UTC and does not gate M6.
- The M4 pilot runs until its checkpoint of 2026-11-25 on execution and evaluation worker images that must not be rebuilt. Its code identity is the SHA-256 of the whole `app/` tree in that image (`app/experiments/code_identity.py:17-27`).
- [ROADMAP](../../ROADMAP.md): "Each gate requires actual evidence; a document, model assurance or mocked success cannot mark it passed."

**The agent runtime that M6 extends** (`services/engine/app/agents/`; migration `alembic/versions/0007_m5_agent_runtime.py`)
- Four roles exist in the schema and the database check (`schemas.py:27`). Only two have templates. COORDINATOR and RESEARCHER hold the three read tools and nothing else (`definitions.py:60-67`).
- The registry accepts only the effects `READ` and `RECORD_AGENT_ARTIFACT` and refuses every M6 and M7 tool by name (`definitions.py:19-23`, `185-196`).
- One workflow template is owner-startable, `MARKET_ASSESSMENT_V1`, with one fixed child that is bound to it by name. Delegation is `NONE_MODEL_CHOSEN; FIXED_CHILD_ONLY` (`definitions.py:93-110`).
- Budgets: 120 s per step, 20 minutes per workflow, 8 model steps, 6 tool calls, depth 1, 12 parent workflows a day, one inference slot (`definitions.py:112-119`). A child shares its parent's deadline, cutoff and budget (`orchestrator.py:337-343`, `358-366`).
- Every tool's arguments are one object of nullable fields, so the output schema stays strict-compatible (`schemas.py:47-55`).
- The approved runtime profile embeds every definition hash (`profile.py:58-69`). The worker refuses to run when the seeded definitions differ from its code in either direction (`worker.py:115-127`).
- Any `as_of` up to the workflow's cutoff is readable (`tools/base.py:43-53`). The cutoff is fixed at start and immutable (0007:449-450).
- The workflow states `WAITING_TOOL` and `WAITING_REVIEW` exist (0007:242, 454-455), and the guard permits `RUNNING` to `WAITING_TOOL` and back. M5 has no tool that waits. The one workflow deadline also expires a waiting workflow (`orchestrator.py:252-260`).
- A tool call has exactly one immutable result, whose status is `SUCCEEDED`, `REJECTED` or `UNAVAILABLE` (0007:378-382).
- Checks that M6 has to widen, all on M5's own tables (0007):
  - `agent_definitions.kind` (79);
  - `agent_approvals.target_kind IN ('RUNTIME_PROFILE')` (121);
  - `agent_workflows.purpose` (209, twelve characters wide) and `created_by IN ('OWNER','ORCHESTRATOR','PROBE_RUN','FIXTURE')` (212);
  - `(purpose = 'REVIEW') = (parent_id IS NOT NULL)` (237);
  - `agent_tool_results.status` (382);
  - `agent_artifacts.kind IN ('MARKET_ASSESSMENT','EVALUATION_REVIEW')` (395);
  - the workflow guard that lets `asl_api` insert only `MARKET_ASSESSMENT_V1` rows (427-431).
- `asl_agent` reads market data only through the `agent_read` views and has no grant on any M1–M4 table.

**The paper engine**
- One account. `account_state` has `CHECK (id = 1)`, holdings are keyed by asset only, and the engine takes `account_id = 1`. Separate portfolios exist today only as separate databases.
- The engine is bound to the reference strategy in more places than its four call sites:
  - `app/execution/engine.py`: `strategy_spec()` (192); the definition row `TREND_REFERENCE_V1` (243); `evaluate(run, self.spec)` (821); `protective_stop(...)` (1261); Start is refused unless the manifest's strategy equals the engine's (1541-1544); sizing reads `close`, `stop` and `atr` from the stored features (1801-1802, 1855).
  - `app/execution/store.py`: every mandate is written with the reference's entry and exit rule texts (398-399); evaluation row identifiers derive from the strategy identity (342).
  - `app/experiments/manifest.py`: the strategy slot is fixed to `TREND_REFERENCE_V1` (20), and the manifest states the live quote rule (80).
  - `app/evaluation/report.py`: the fidelity label `SAMPLED_L1_TICKER` is a constant (24, 159).
  - `app/replay/fingerprint.py`: the stored feature blob is part of the fingerprint (54-57).
- At start the engine checks every stored definition's hash and compares with code only the identities that code seeds (`engine.py:226-233`). A definition that is not seeded passes if its own hash is right.
- Hourly marks are captured only while a run is live (`engine.py:1463-1466`), and a report needs an activated experiment (`app/evaluation/loader.py:55-64`).
- **Fills need dense quotes.** An order arrives 1 s or 2 s after its decision, and an entry can fill only from a quote inside the following 5 s that is itself at most 5 s old (`engine.py:1348-1349`, `fill_model.py:85-96`, `definitions.py:121-141`).

**Replay**
- Modes are `FORWARD_PAPER`, `OFFLINE_TEST` and `HISTORICAL_RESEARCH`. A trigger refuses the last two outside databases named `asl_m1_…` (`alembic/versions/0005_m3_paper_broker.py:34`, `511-517`). There is no `SHADOW` value.
- Replay runs the same engine through a simulated driver. It needs `ASL_REPLAY_ISOLATED=1` and a database named `asl_m1_replay_…`, resets the engine state, funds 10,000 virtual USDT and labels the evidence by its acquisition (`app/replay/run.py:56-61`, `81-113`).
- Its eligibility rule is reduced to the quote's own quality and a 5 s age; it does not see feed, lease or clock state (`app/execution/eligibility.py:52-64`).
- The reset truncates every table except the market tables and three preserved ones, as the database owner (`app/execution/fixtures.py:53-72`). A replay experiment is written `READY` and activated by a superuser (`alembic/versions/0006_m4_fixed_pilot.py:242-258`), and the final report is generated from it (`run.py:228-239`).
- The engine's roles read their passwords from fixed secret paths (`app/db.py:42-49`, `app/execution/identity.py:33-35`), and migrations 0002 and 0003 read role passwords from secret files.
- Replay is deterministic, and its fast path batches 500 steps. The seven-day full-density replay took 429.5 s and 429.0 s against a 20-minute budget, with a two-CPU PostgreSQL ([STATUS](../../STATUS.md), ExecPlan 0017).

**Market data that research can use**
- Quotes are deleted after 7 days and final candles after 730 days, unless pinned (`alembic/versions/0003_market_data.py:213-217`). The worker backfills up to 720 hourly bars per symbol.
- A market observation needs its payload row and, since 0004, may reference a collection. Collections, confirmations and evidence pins are append-only for every role (0003:169, 0004:69-71). Every engine step pins the rows it uses (`store.py:294`).
- The owner takes weekly protected dumps of the market tables (OD-14).
- On 2026-10-03 the normal database held about five days of quotes: 881,805 observations and 1.53 GB of market relations.

**Services and host**
- No research service, profile or table exists. No source registry, generic fetcher or search exists. The three outbound paths are the fixed-host Binance transport, the agent egress gateway with its two pinned hosts, and the engine-to-runner client.
- Compose limits today (`compose.yaml`): postgres 2 CPU / 2 GiB; api, web, market and execution 1 CPU / 512 MiB each; evaluation and agent-worker 0.5 / 256 MiB; agent-runner 1 / 1 GiB; agent-egress 0.5 / 128 MiB. That is about 5.6 GiB of limits.
- The Docker VM had 16 CPUs and about 7.7 GiB of memory when it was inspected on 2026-09-26. It also hosts other projects' containers and this project's isolated test stacks.

**Acceptance cost seen in M5**
- Each restart of the final M5 pass cost about 2.5 hours, most of it waiting for the HH:15–HH:55 window. The owner approved a narrower window only for a restart, and full reruns after any fix ([DECISIONS](../../DECISIONS.md#2026-10-01--m5-acceptance-quiet-period-on-a-restart-no-partial-reruns-execplan-0020-b7)).

## 3. Scope and exclusions

### 3.1 In scope (PROPOSED)
- Definitions v2: tool catalog, role grants, templates, budgets, AgentStep schema, four role prompts, the candidate grammar.
- Source registry, fetcher, evidence corpus and search; a trigger scheduler for source revisions and scheduled research.
- Research catalog (hypotheses, candidates, datasets, jobs, results, trials, shadows, promotions) in the main database.
- A research bridge, a research runner and a research PostgreSQL cluster; a strategy interface in the engine; a stager.
- Owner API routes and the evidence, research and approval pages.
- Additive migration `0008_m6_research`.
- `tools/m6-acceptance.ps1`, `tools/m6-deploy.ps1`, `tools/research-activate.ps1`, `tools/research-deactivate.ps1`.

### 3.2 Excluded
- **M7:** `draft_trade_intent`, `submit_trade_intent`, `request_entry_pause`, `request_review` as a model-chosen tool, the `AGENT_DRIVEN` and `ADAPTIVE_SELECTOR` policies, bar-close and portfolio triggers, and **approving** a promotion.
- **The pilot:** no rebuild, recreate, restart or reconfiguration of `postgres`, `market-worker`, `execution-worker`, `evaluation-worker` or `pilot-admin`; no statement that alters an M1–M4 table.
- **A multi-account ledger, an engine-level `SHADOW` mode and a live shadow engine.** They need changes to tables the pilot writes. They wait for the experiment boundary after 2026-11-25 (§5.6).
- **Research on bar history** (§5.12).
- **Generated code.** No eval, import, SQL, shell or downloaded plugin; a rule outside the grammar is a development proposal.
- **Paid, private or undocumented sources;** any source the owner has not approved by exact hash.
- **Any claim of profitability.** Fixture and replay success is functional evidence only.

### 3.3 Decisions for the owner

| ID | Decision | Recommendation |
|---|---|---|
| M6-OD1 | **A real external source for the live walk-through.** (a) One documented, key-less source family, verified in B0. (b) None in M6: the registry ships empty, and "an analyst obtains permitted evidence" has isolated evidence only. | **(a), non-blocking.** Candidate: the public release feeds of Bitcoin Core and of the Solana validator client, with the Solana status page as the alternative (§5.7, §6). If the rights review in B0 fails, (b) applies and falls under M6-OD7. |
| M6-OD2 | **Research on bar history.** (a) Plan it separately and build it as an extra batch. (b) Leave it out of M6. | **(b).** As first drafted it cannot work (§5.12). Without it, results carry "insufficient sample" until weeks of recorded quotes exist. |
| M6-OD3 | **The research envelope's values** (§5.5): budgets, domains, partitions, shadow limits. The owner approves the exact hash in the UI in M6-B. | Approve the proposed values, or name changes now so they are built in. None is claimed optimal. |
| M6-OD4 | **Acceptance rules that cost wall-clock time.** (1) The narrower quiet period HH:58–HH:07 UTC for every isolated heavy phase. (2) After a fix that changes only tests or harness files, rerun the failed phase and the phases that use the changed file; a product-code fix still reruns every phase. | **Both.** (1) only after B0 measures that an isolated heavy phase does not move the pilot's HH:05 report. Both change the rule of 2026-10-01. |
| M6-OD5 | **A promotion request in M6.** (a) The owner can reject or leave it pending; approving arrives with M7, which is what would use it. (b) Approval is recorded now with no effect. | **(a).** It matches the roadmap gate ("new main strategies remain unapproved"). |
| M6-OD6 | **What a shadow is until the pilot ends.** (a) A **deferred replay**: a frozen candidate replayed over later recorded observations, labeled as such (§5.6). (b) No shadows in M6; shadow scheduling moves behind the experiment boundary, and the roadmap is amended. | **(a).** It cannot look ahead. It is more favorable than a live engine in three stated ways, and it is not the "live shadow" the contracts name, so B0 amends them. |
| M6-OD7 | **When M6 is complete.** (a) When the live walk-through of §13.3 is recorded; the first live pending promotion is a follow-up, at the earliest seven days after the first shadow starts. (b) Only when that first live pending promotion exists. | **(a).** It closes M6 with the gate clause "a promotion request remains pending" shown in isolation only, which the roadmap does not accept as a pass by itself. That is why it is the owner's decision, as the M5 refresh was. |

**The owner's answer, in chat on 2026-10-03: "approve the plan with your recommendations".** Each decision is taken as recommended:

| ID | Decided | What still gates it |
|---|---|---|
| M6-OD1 | (a), non-blocking | The rights and retention review in B0; if it fails, (b) applies. The owner still approves the source version by exact hash in M6-B |
| M6-OD2 | (b): no bar-history research in M6 | — |
| M6-OD3 | The values of §5.5 are built in as written, including the points §5.5 and §5.10 leave to the B0 measurements | The owner still approves the envelope's exact hash in the UI in M6-B. A value changed for any other reason goes back to the owner |
| M6-OD4 | Both rules | Rule (2) applies from the start. Rule (1) applies only once B0 has recorded that an isolated heavy phase does not move the pilot's HH:05 report; until then the rule of 2026-10-01 applies |
| M6-OD5 | (a): reject, or leave pending | — |
| M6-OD6 | (a): a deferred replay | B0 amends ARCHITECTURE, EVALUATION and RESEARCH_WORKFLOWS |
| M6-OD7 | (a): complete on the recorded walk-through of §13.3 | The gate clause "a promotion request remains pending" has isolated evidence only at completion. The first live pending promotion is a follow-up |

One consequence is not a decision: **the agent runtime needs a new profile approval and probe run** after M6-A is deployed, before any model call, including the call that would show M5's token refresh.

## 4. Requirements mapped to tests (PROPOSED)

IDs in the third column are [ACCEPTANCE_CHECKLIST](../../ACCEPTANCE_CHECKLIST.md) rows. M6 contributes partial evidence; no row is checked before M8.

| ID | Requirement | Rows | Tests (phase in §10) |
|---|---|---|---|
| R01 | Each of the four roles has its own grant, prompt and typed artifact; role, workflow and grants come from server state | A23 | `DispatcherAuth6`: every tool valid once and denied once per role; role spoofing; `AgentOffline6` |
| R02 | The analyst reads only approved evidence, asks only for a registered source, and cites only items it was given | A15 | `AgentOffline6`; `DispatcherAuth6` (unregistered source, URL in arguments, citation of an item not returned) |
| R03 | The fetcher reaches only an approved source version's host and path templates; private, loopback, link-local, metadata and host-gateway addresses, IP literals, redirects, oversized, slow or wrong-type answers are refused | A34 | `SourcePolicy` |
| R04 | Text from a source or from another role cannot add a tool, a destination, a role or an approval | A28 | `EvidenceInjection` (malicious documents; an analyst artifact carrying instructions for the evaluator and the researcher) |
| R05 | Publication, update, receipt and availability times are kept apart; a revision is a new item; a duplicate does not trigger twice | A15, A16 | `SourcePolicy`; trigger dedupe and cooldown tests |
| R06 | A candidate is accepted only if it parses in the grammar, lies in the envelope's domains and is within the complexity bound; code, SQL, unknown operators and oversized rule sets are refused | A17, A18 | Grammar unit and property tests; `DispatcherAuth6` |
| R07 | The reference rule run through the candidate adapter gives the same orders, fills, positions, obligations, valuations and ledger rows as the native reference, and the same signal per bar. The forward path's own output is unchanged | — | `EngineParity`: the portable fingerprint over a stated projection, on the three built-in scenarios; the M3 and M4 regression suites and their existing fingerprints |
| R08 | A candidate strategy can run only under replay activation in an `asl_m1_replay_` database; main activation and a forward manifest refuse it | A17, A19 | Activation and manifest tests; `PilotCoexistence` |
| R09 | A research result is a pure function of candidate, dataset, partition, cost scenario, protocol and code identity; an identical request reuses the stored result | A10 | `ResearchRunner` (same inputs twice, equal fingerprints; reuse recorded as a trial) |
| R10 | Every attempt is recorded before it runs and never deleted, including failed, canceled and refused ones | A10, A36 | `ResearchRunner`; append-only trigger tests |
| R11 | A tuning role gets nothing from after its hypothesis's information cutoff: no market read, no holdout or shadow result, no summary, no search hit, no review text | A18, A36 | `HoldoutIsolation` |
| R12 | Budgets are reserved before a job is queued; an oversized or over-budget request is refused; a job stops at its bound with an honest incomplete record | A17, A18 | `ResearchRunner` |
| R13 | A waiting workflow holds no inference slot and resumes exactly once; a crash, a cancel, a revocation or a late completion cannot duplicate an effect | A24, A25 | `AgentFaults6` |
| R14 | A shadow decides and trades only on observations published after its candidate was frozen; earlier bars feed its indicators only. A recorded mark never changes | A19 | `ShadowSchedule` (portable prefix fingerprints; no evaluation of a bar closed at or before the freeze) |
| R15 | A promotion request is recorded as pending. No role, route or statement approves it in M6 | A19 | `DispatcherAuth6`; database trigger test; `ApiAuth` |
| R16 | The research and source identities have no grant on any M1–M4 table. The runner has no route and no credential to the main database | A17 | Grant tests against a real PostgreSQL; a Compose configuration test; a network reachability test |
| R17 | Research at its limits leaves market publication and paper execution inside their existing budgets | A33 | `ResearchSaturation` |
| R18 | The pages show actual roles, tools, evidence, trials and approvals with their labels; nothing is optimistic or simulated | A26 | `BrowserResearch`, `BrowserResearchError` |
| R19 | The pilot's containers, images, lease and segment are unchanged by build, migration and deployment | — | `MixedVersion`, `PilotCoexistence`, the deploy script's before-and-after check |
| R20 | Staging copies only published market rows, in dependency order, without changing a value. A replay on a staged store has the same fingerprint as on its source. Staging keeps to its batch, pause and quiet-window bounds, and records every gap | A06 | `Staging` |

Negative cases required by [TESTING](../contracts/TESTING.md#negative-and-concurrency-scenarios) and covered above: generated code or an unknown operator; an oversized experiment; holdout retrieval through a report; a redirect to a private address; source text asking for credentials; a new strategy under an existing name (the normalized hash decides identity, R09); revocation after preflight (R13).

### 4.1 Concurrency and failure cases

| Case | Required behavior | Test |
|---|---|---|
| The runner dies in a job | The lease expires. The job is queued once more, then fails as `WORKER_LOST`. A rerun starts from a reset, so it cannot double-count | `ResearchRunner` |
| The bridge is down | No staging and no relay. Jobs stay queued and shadows are not advanced. A gap longer than the main database keeps quotes ends the affected shadows as incomplete, with the gap recorded | `Staging`, `ShadowSchedule` |
| A result is relayed twice | One result per job, checked by hash; the second insert is a no-op | `ResearchRunner` |
| Two equal requests at once | One job. The other request gets the same job and a `REUSED` trial | `ResearchRunner` |
| Disable, or an envelope or source revoked, while work is queued or running | Queued work is canceled; a running job stops between batches; a late result is history only; the waiting workflow ends `CAPABILITY_REVOKED` | `AgentFaults6` |
| A wait deadline passes | The workflow is `EXPIRED`. Its job may finish; the result stays readable to a later workflow | `AgentFaults6` |
| A completion arrives twice, or after a cancel | One completion per tool call; a late one is stored as late and resumes nothing | `AgentFaults6` |
| A store version is replaced while a shadow runs | The shadow keeps its version until it ends. A version is dropped only when nothing references it | `ShadowSchedule` |
| The research cluster is lost | The catalog and every recorded result survive. Running shadows end as incomplete. Stores older than the main database's quotes can be rebuilt only from the weekly dumps | `ResearchActivationRehearsal` |
| A fetch fails, times out or is rate-limited | The outcome is recorded and the budget is spent; no trigger; the next poll waits for the stated reset | `SourcePolicy` |
| The holdout job fails | The candidate stays `TESTED`. One retry is allowed and recorded; it is still that hypothesis's single holdout evaluation | `HoldoutIsolation` |
| Migration 0008 cannot take a lock | Bounded retries, then the deployment stops before the agent worker is replaced | `Migration` |

## 5. Design (PROPOSED)

### 5.1 Services, networks and identities (all new; pilot services untouched)

| Service | Profile | What it runs | Networks and secrets | Limits (to confirm in B0) |
|---|---|---|---|---|
| `research-postgres` | `research` | A second PostgreSQL cluster of the pinned image, volume `research_postgres_data`. Working databases only | internal `research_private` | 1 CPU, 1 GiB, 128 PIDs |
| `research-runner` | `research` | Engine image, `python -m app.research.runner`: resets, replays, metrics | `research_private` **only**; research-only secrets | 1 CPU, 768 MiB, 128 PIDs; read-only root |
| `research-bridge` | `research` | Engine image, `python -m app.research.bridge`: staging, job and result relay, shadow schedule; identity `asl_research` on the main database | `private`, `research_private`; no egress | 0.5 CPU, 256 MiB, 64 PIDs; read-only root |
| `source-fetcher` | `sources` | Engine image, `python -m app.sources.worker`, identity `asl_source` | `private`, new `source_egress` | 0.5 CPU, 256 MiB, 64 PIDs; read-only root |
| `research-migrate`, `research-admin` | one-shot | Migrate a research database; enable, disable and report the identities | as needed | — |

- **Why a second cluster.** A replay writes millions of rows. In the pilot's PostgreSQL it would share that container's two CPUs, memory and write-ahead log. A separate cluster has its own limits.
- **Why two processes.** Replay needs a superuser and the engine's own role in the database it runs in (§2). The process that holds those and executes candidate-driven engine code is the runner, and it has no network path and no credential to the main database. The bridge is the only research process on `private`. It holds no engine credential.
- **Research-only secrets.** The runner and `research-migrate` get secrets generated for the research cluster, with their own values, mounted at the paths the engine code reads. A Compose configuration test asserts that no secret of the main database is mounted into a research service.
- **`asl_research`** (bridge, main database) reads market rows only through new `research_read` views: the market tables, payloads included, without the evidence pins, which would reveal pilot trades. It writes only research job, result and shadow rows. It has role-level statement and lock timeouts. As in M5, the views belong to the migration role, so no grant is issued on an existing table.
- **`asl_source`** reads the source registry and writes only fetch and evidence rows.
- **`asl_agent`** gains reads on the new tables and inserts for requests, hypotheses, candidates and promotion proposals. **`asl_api`** gains reads, and inserts for owner requests and approvals.
- **What stays in the main database:** the research catalog (§5.2), which is small, durable and covered by the normal backup.
- The agent services keep their Compose blocks. Only the agent worker's image changes; the runner image and the egress gateway are not rebuilt.

### 5.2 Research catalog and migration 0008

Additive on M1–M4: new tables, views, functions and roles only. The checks listed in §2 are widened on M5's agent tables, which no pilot process touches, with `lock_timeout = 200ms` and bounded retries.

| Record | Table | Mutability |
|---|---|---|
| Source version, research envelope, research protocol, candidate grammar | `agent_definitions` (new kinds) | Seeded, hashed, append-only |
| Exact-hash approval of an envelope or a source version; rejection of a promotion | `agent_approvals` (new target kinds) | Append-only. A trigger refuses `APPROVE` for a promotion |
| Completion of a queued tool call, with its own `result_ref` | `agent_tool_completions` | Immutable; one per tool call |
| Fetch attempt and outcome | `source_fetches` | Immutable |
| Evidence item: source version and hash, external ID, revision, times as supplied, receipt and availability, bounded plain-text extract, SHA-256, search vector | `evidence_items` | Immutable; a revision is a new row |
| Refresh request (tool, owner or schedule) with its dedupe key | `source_refresh_requests` | Transition guard |
| Trigger with family, dedupe key, cooldown and outcome | `agent_triggers` | Transition guard |
| Hypothesis, bound to one dataset version and its information cutoff | `research_hypotheses` | Immutable |
| Candidate: grammar version, canonical declaration, normalized SHA-256 (unique), envelope hash | `research_candidates` | Immutable |
| Candidate lifecycle transition with its gate evidence | `research_candidate_events` | Append-only; SYSTEM only |
| Dataset manifest: store version, sequence range, partitions, coverage, gaps, content digest, limits | `research_datasets` | Immutable once sealed |
| Job with its reservations, lease and measured resource use | `research_jobs` | Transition guard; fenced |
| Result: metrics document, SHA-256, portable fingerprint, code identity, evidence and fidelity labels | `research_results` | Immutable |
| Trial ledger: every attempt, reuse and refusal | `research_trials` | Append-only |
| Shadow; each recorded advance with its marks, trades and fingerprint as a hashed document | `research_shadows`, `research_shadow_marks` | Guarded; marks immutable |
| Staging run and every staging gap | `research_staging_runs` | Append-only |
| Promotion proposal | `research_promotions` | Guarded; `PENDING`, `REJECTED`, `WITHDRAWN` |

- Candidate lifecycle states are the canonical ones of [RESEARCH_WORKFLOWS](../RESEARCH_WORKFLOWS.md). `MAIN_APPROVED` exists in the enum and is unreachable in M6.
- Research tables never reference M1–M4 tables by foreign key, for the reason given in M5: adding one locks the referenced table.
- **Downgrade.** It is guarded like 0007's: it drops only M6 objects and refuses when a non-fixture research row exists. It must also remove the v2 rows from `agent_definitions`, which is append-only for every role, by disabling that trigger inside the migration transaction. Otherwise the M5 worker refuses to start on the extra rows. The `Migration` phase rehearses it.

### 5.3 Candidate grammar and the strategy interface

`CANDIDATE_GRAMMAR_V1` is a declaration, not a program. It is deliberately **not recursive**, so it fits the single strict argument object of §2.

- **Shape.**
  - `symbols`: a subset of BTCUSDT and SOLUSDT; timeframe 1h.
  - `entry`: up to 3 groups joined by OR; each group up to 4 conditions joined by AND.
  - `exit`: the existing mandate template with parameters (`atr_period`, `stop_multiple`, `max_hold_hours`) and an optional signal exit of the same condition form.
  - `warmup_bars`: bounded, and at least the longest lookback used.
- **Condition.** `left op right`, where `left` is a feature, `right` is a feature or a bounded decimal constant, and `op` is `GT`, `LT`, `CROSS_ABOVE` or `CROSS_BELOW`.
- **Features (registered operators).** `CLOSE`, `EMA(n)`, `SMA(n)`, `ATR(n)`, `RETURN(n)`, `HIGHEST(n)`, `LOWEST(n)`, `ZSCORE(n)`. Each is implemented in `app/strategies/` with Decimal arithmetic and hand-calculated fixtures, as the existing EMA and ATR are.
- **Domains** come from the approved envelope (§5.5). A value outside them is refused, not clamped.
- **Identity.** The declaration is normalized (group and condition order, decimal form) and hashed. Two declarations with one meaning are one candidate.
- **Protection is unchanged.** Every candidate uses the engine's existing stop, time-exit and signal-exit machinery. A candidate cannot define an order type, a size or a new exit rule. A candidate's signal exit is stored under the engine's existing `TREND_EXIT` reason; the result document names the actual rule.

**The interface.** One small strategy interface replaces every binding listed in §2:
- `spec`: identity, hash, warm-up, run length, symbol priority, validity, maximum hold, stop parameters;
- `evaluate(run)`: the signal, with `close`, `atr` and `stop` in its features, as sizing requires;
- `protective_stop(...)`;
- the entry and exit rule texts that the mandate stores.

How it is used:
- The native reference is one implementation and stays the default. For it, every stored value is what it is today.
- A candidate interpreter is the other. Sizing, risk, mandates, fills and the ledger run exactly as for the reference.
- The manifest builder accepts another strategy only for `HISTORICAL_RESEARCH`, and then states the reduced replay rule instead of the live one. A forward manifest keeps its fixed slots.
- A candidate's definition row is inserted only in a research database. Main activation keeps requiring the owner's exact-hash approvals and refuses any other strategy identity (R08).
- **Parity (R07).** Identifiers derive from the strategy identity and the feature blob differs in shape, so the full fingerprints of the two implementations cannot be equal. Parity is the equality of the portable fingerprint over orders, fills, positions, obligations, valuations and ledger rows, and of the signal per bar, on the three built-in scenarios.

### 5.4 Datasets, stores and staging

M6 has one dataset kind: **recorded public observations** at the pilot's fidelity (`SAMPLED_L1_TICKER` under the reduced replay rule).

**Stores.**
- A store is a database in the research cluster, named `asl_m1_replay_…`, so the existing mode and replay guards hold as they are.
- The bridge copies published rows from the main database through `research_read`, by publication sequence: collections, payloads, observations, confirmations and publications, in that order, with their identifiers and sequence values unchanged.
- It copies in bounded batches with pauses, and not between HH:58 and HH:07.
- **A store is append-only and versioned.** Nothing is deleted inside it, because several market tables are append-only for every role and every job pins the rows it uses (§2). When a store reaches its size cap, a new version starts at a later sequence. An old version is dropped whole once no dataset or shadow references it.
- Size (INFERRED from the 1.53 GB that about five days occupied on 2026-10-03): about 0.3 GB a day. B0 measures the disk and sets the cap.

**B4 implementation (IMPLEMENTED 2026-10-04; owner decisions of that day in [DECISIONS](../../DECISIONS.md#2026-10-04--m6-b4-handed-over-and-four-points-the-plan-left-open-execplan-0023)).**
- **Rotation, decided by the owner.** A new version becomes current once the current one spans 28 days of staged quotes (49 less the 21-day shadow) or 12,271,335,131 allocated bytes (the same share of 20 GiB). The old version is staged only while a running shadow is bound to it, never past 49 days or 20 GiB, and is dropped whole once no queued or running job or shadow uses it. At most two stores exist, which is what the 40 GiB disk floor was sized for. No envelope value changed.
- **Who does what.** The bridge decides and records a request in a registry in the research cluster's `postgres` database, which holds no engine schema. Only the runner, which owns that cluster, creates, migrates or drops a store database. The bridge writes there as `asl_bridge`, a role that exists in the research cluster only: it may insert published market rows, transport work and read the outbox, and nothing else. It mounts no volume; the runner publishes the research filesystem's free space in the registry, and a missing or stale reading stops staging.
- **At the cap.** Nothing more is staged into a store at 49 days or 20 GiB. At the day cap a shadow whose whole window is staged still gets its last advance; at the byte cap the runner refuses every job on that store, so its shadows end `INCOMPLETE`.
- **A lost cluster.** A store that no longer holds what the catalog's journal says was staged into it, or a dropped name offered again, is refused and its shadows end `INCOMPLETE`. Recovery after such a loss is B9's rehearsal.
- **Where a version starts.** At the oldest publication main still has within 21 days. Final candles reach back that far; quotes reach back only as far as main keeps them (7 days), so a new version starts thin and the manifests say so.
- **A batch** is at most 500 rows and 8 MiB of payload bodies, read in one main-database snapshot and written with its watermark in one store transaction. Rows travel as PostgreSQL's own row text and are compared with their source after the write. A row is staged once its publication has been visible for 60 seconds.
- **Gaps (engineering default, not an envelope value).** A symbol without a published quote for more than 60 seconds is a recorded gap. It is `RETENTION_LOSS` when it starts before main's 7-day horizon, because rows deleted before staging cannot be told from rows that never existed; otherwise `SOURCE_GAP`. A published row whose dependency is not published is skipped and recorded as `DEPENDENCY_UNAVAILABLE`.

**Datasets.** A dataset is a sealed range of one store version, with fixed partition boundaries and an immutable manifest: coverage, gaps, row counts, a content digest.

**Sealing (decided by the owner on 2026-10-04).** The bridge seals one dataset per UTC day on the current version, once staging has caught up. Its partitions span at most the last 21 days of staged quotes; its sequence range also includes up to 302 earlier hours, so indicators have their warm-up bars. A shadow advance seals its own window, marked `SHADOW`, which a hypothesis can never bind to.

**How a job runs.**
- A job is one candidate's registered test set (§5.5). Jobs on one store run one at a time.
- For each replay the runner resets the engine state as replay does today, installs the candidate's definition, creates and activates a research experiment, runs the replay with the fast path, and generates the report with the M4 evaluation module.
- It writes the result to an outbox in the research cluster. The bridge relays it to the catalog and checks its hash.
- **Two independent guards keep the engine off the owner's data.** The database-name check refuses any database not named `asl_m1_replay_…`. And the runner has neither a route nor a credential to the main database.
- **Compared with M3:** M3's replay runs in a separate Compose project. The runner is a service of the normal project, on a network that reaches only the research cluster.

**What is lost with the research cluster.** Recorded results, marks and trade lists are in the catalog and survive. The stores do not. The main database keeps quotes for 7 days, so an older store can be rebuilt only from the owner's weekly dumps (OD-14), as an owner step. Otherwise the affected shadows end as incomplete.

**Limits, stated in every result.**
- On 2026-10-03 about five days of quotes exist. History grows only with time.
- Every replay has zero processing delay and the reduced eligibility rule.
- Historical results carry the contamination warning that [DATA_CONTRACTS](../../DATA_CONTRACTS.md) requires: the model may know later events.

### 5.5 Protocol, envelope and holdout

**`RESEARCH_PROTOCOL_V1` (hashed).**
- Chronological partitions of each dataset: DEV 60%, VALIDATION 20%, HOLDOUT 20%, with a gap of the maximum hold between them.
- **The registered test set.** Screening is DEV and VALIDATION under the first hypothetical cost scenario (`H1`). A nominated candidate is then run on every partition, the holdout included, under both scenarios (`H1` and `H2_STRESS`).
- Metrics, baselines and uncertainty exactly as `EVALUATION_PROTOCOL_V1`, including its sample minimums and its "insufficient sample" outcome. No Sharpe ratio, no annualization, no acceptance threshold.

**`RESEARCH_ENVELOPE_V1` (hashed; the owner approves its exact hash).** The hash binds the protocol, the grammar, the domains, the budgets and the resource limits. Proposed values, all engineering defaults (M6-OD3):

| Field | Proposed value |
|---|---|
| Modes | Backtest on recorded quotes; shadow as a deferred replay |
| Dataset length | At most 21 days, shortened from the provisional 42 by the B0 research-limit replay measurement below; VALIDATION/HOLDOUT sample minimums remain unchanged and say "insufficient sample" |
| Operator lengths; warm-up | Integers 2–200; ATR period 5–50; warm-up at most 300 bars |
| Stop multiple; maximum hold | 1.0–5.0 in steps of 0.25; 6–168 h |
| Constants | Decimals in [−10, 10], at most 4 places |
| Complexity | At most 3 groups, 4 conditions a group, 8 distinct features |
| Trials | At most 12 candidates a hypothesis; 12 jobs a UTC day; a queue of 4 |
| Job bounds | One job at a time; 60 minutes wall clock; cancel between batches. B0 measures the replay rate on the research cluster's limits and may shorten the dataset to fit |
| Holdout | One evaluation per hypothesis, queued by SYSTEM; results to EVALUATOR, COORDINATOR and OWNER only |
| Shadows | At most 4 at a time; at most 21 days each; advanced once a day |
| Evidence for a promotion request | The M4 protocol's own minimums in the shadow: 168 paired hours and 10 closed positions |
| Stores | At most 49 days and 20 GiB allocated per store, measured/sized in B0; new jobs refused at the cap or with less than 40 GiB available on the research data filesystem |
| Resources | The container limits of §5.1 |

**B0 measured sizing, 2026-10-03.** OBSERVED one complete synthetic seven-day native replay at the §5.1 limits: 402.68 s replay, 340.47 s fixture acquisition, 756.763 s total measurement cycle; fixture database 2,292,979,379 bytes. INFERRED linear replay rate 57.5257 s per recorded day. Two scenarios over the provisional 42 days project to 4,832.16 s, above the unchanged 3,600 s job bound. The permitted B0 reduction to 21 days projects to 2,416.08 s, leaving 1,183.92 s for candidate/partition/report overhead and variation. This is engineering sizing, not verified candidate throughput; `PerformanceResearch` must verify actual jobs. At 49 days the measured database projects to 16,050,855,653 bytes; with 25% reserve and rounding, the store cap is 20 GiB (21,474,836,480 bytes). The filesystem pressure floor is two such caps, 40 GiB. OBSERVED VM data filesystem available 978,972,244 KiB; host C: available 551,357,804,544 bytes at 16:28 UTC. The host figure is separately observed and is not assumed equal to virtual-filesystem free space. No other envelope value changes. Protocol sample minimums and insufficiency labels are preserved. Exact-hash envelope approval remains owner-only in M6-B.

**Shadow eligibility** is a code check, not a performance cutoff: the registered test set complete, no integrity failure, an `ACCEPTABLE` candidate review, and a free slot. The plan invents no return threshold; the owner may add one to a later envelope version.

**The holdout lock is an information cutoff.**
- A hypothesis is bound to one dataset version, the newest when it is recorded. Its **information cutoff** is the start of that dataset's holdout.
- A research workflow runs with that cutoff as its workflow cutoff. Every market read, every search and every artifact it can open is limited to it. Hits are filtered before they are ranked, so a hidden item cannot shape the result list.
- A researcher can request DEV and VALIDATION only. A HOLDOUT request is `SCOPE_DENIED`.
- When a research workflow finishes with a nominated candidate, SYSTEM queues the holdout runs once for that hypothesis.
- ANALYST and RESEARCHER receive `HOLDOUT_LOCKED` for holdout and shadow results. From a review that consulted them they receive only the verdict and enumerated deficiency codes, never its free text.
- A later dataset version moves the holdout forward. Older periods then become development data for new hypotheses, whether or not an earlier hypothesis consulted them. A hypothesis never changes its dataset.
- The trial ledger counts how often each dataset's holdout was evaluated and shows it to the evaluator and the owner. M6 applies no statistical correction for repeated testing and says so in every report.
- **A limit that the cutoff does not remove:** the same model also runs analyst workflows on current data, in separate workflows with no shared memory beyond typed artifacts, which the cutoff filters. What the model knows from its training is not controllable; that is the contamination label.

### 5.6 Shadows (M6-OD6)

- **Definition.** A shadow is a candidate whose declaration was frozen at time T0, replayed over the staged observations whose availability is after T0, in its own virtual portfolio of 10,000 USDT. Earlier bars feed its indicators only, as for a forward run.
- **What it guarantees.** The candidate could not have been fitted to observations that did not exist when it was frozen, and every frozen candidate's shadow is kept, whatever it shows.
- **What it is not.** It is not a live engine, and the contracts' "live shadow" is not delivered before the experiment boundary. It is more favorable than a live run in three ways, labeled on every shadow:
  - decisions are timed at each observation's availability, with zero processing delay;
  - eligibility is the reduced replay rule, which does not see feed, lease or clock state. A minute in which the live rule refused quotes is tradable in the shadow;
  - the research services' own downtime does not show. Only missing observations do.
- **Like for like.** Promotion evidence compares a candidate's shadow with the reference strategy replayed over the same window under the same rule, never with the pilot's forward results.
- **Advance.** Once a day, and on demand, the runner replays the shadow from T0 to the newest staged publication. The bridge records the new marks, the trade list and the portable fingerprint in the catalog as a hashed document, so the evidence does not live only in the research cluster.
- **Integrity.** The engine is deterministic, so the earlier part must reproduce its recorded portable fingerprint. A mismatch suspends the shadow (R14).
- **Cost (INFERRED from B0's one-CPU research-cluster measurement).** 57.5257 seconds of elapsed native replay per recorded day projects to 1,208.04 seconds for a 21-day shadow, before candidate/report overhead. This is engineering sizing; B9 measures actual shadow/job performance.
- **Labels.** The catalog, the API and the pages say `SHADOW — deferred replay`. The engine rows carry `HISTORICAL_RESEARCH`, because adding an engine value means altering tables the pilot writes. B0 amends ARCHITECTURE, EVALUATION and RESEARCH_WORKFLOWS to say so.

**B4 implementation (IMPLEMENTED 2026-10-04; owner decisions of that day).**
- **What one advance replays, decided by the owner.** The frozen candidate and the reference strategy, over the same window and rule, under `H1`. `H2_STRESS` is not run in shadows; every mark carries `H2_STRESS_NOT_RUN_IN_SHADOWS`. The projected cost doubles to about 2,416 s at 21 days, inside the 3,600 s job bound; this is still B0's inference, and B9 measures it.
- **Budget, decided by the owner.** An advance is a SYSTEM job of kind `SHADOW` and is not a trial: it does not count toward 12 jobs a UTC day or the queue of 4. Its bounds are 4 active shadows, one queued or running advance per shadow, one scheduled advance per shadow per UTC day, and one running job at a time overall. On-demand advances stop at 42 marks. An advance is recorded only when no other job is queued or running: a job's hour runs from the moment it is recorded (B3), so an advance recorded behind other work could lose its hour before it started. Advances therefore run one after another, and one that was canceled or expired without running is recorded again the same day.
- **The freeze** is the catalog clock at the moment the shadow is recorded, never a supplied time. The experiment starts at the freeze, so the engine's existing evaluation floor leaves out every bar that closed at or before it, whenever that bar was published.
- **Prefix integrity.** Each advance replays from the freeze and stops at every recorded mark, with exactly the rows that mark's advance could see. Each stop must reproduce the recorded portable fingerprint of both subjects. A difference ends the advance as `PREFIX_MISMATCH`, suspends the shadow and the candidate, and writes no mark.
- **Eligibility** reads stored records only: the full test `SUCCEEDED` with a `VALID` result, a stored `CANDIDATE_REVIEW` of exactly that result with verdict `ACCEPTABLE` from a finished EVALUATOR workflow, a free slot and an approved envelope. B6 writes that review; B4 verifies the check with labeled fixture rows.
- **Endings.** Reaching the window end is `SUCCEEDED`. A retention gap, a lost store or a store at its cap is `INCOMPLETE`. An owner stop is `STOPPED`. Only a prefix mismatch moves the candidate (to `SUSPENDED`); what happens to a candidate whose shadow ended without the evidence minimum is left to B6 and the owner.
- **`EVIDENCE_READY`** is recorded when a mark meets the protocol's own minimums (168 paired hours and 10 closed positions). It is not a promotion and no return threshold exists.

### 5.7 Sources and evidence

- **Registry.** A source version is a hashed definition:
  - publisher, exact host, path templates with typed parameters, GET only, no redirects;
  - content type, size and time limits; a rate budget;
  - a code-registered parser; the mapping of the publisher's time fields; symbol or topic scope;
  - the rights and terms reference with its review date; retention.

  It is `PROPOSED` until the owner approves its exact hash. A source without approval is shown as unavailable.
- **Fetcher.** The technique of the Binance transport, which M2 verified: resolve the registered host itself, require every address to be global, connect to the checked address with the original TLS name, no proxy from the environment, no redirects, bounded body, bounded time, no cookies or credentials. A request is built only from a version's path templates: on a shared host such as an API gateway, the path is what identifies the publisher.
- **What a model can ask for.** A source ID and that source's typed filters. Never a URL. A link found in a document is data.
- **Evidence item.** The publisher's publication and update times only as supplied; local receipt; availability at commit. The extract is bounded plain text with markup removed. The page labels it untrusted and renders it as text.
- **What an item proves.** That this publisher published this text at that time. Not that the text is true. Interpretation stays in model-authored, labeled artifacts.
- **Search.** PostgreSQL full-text search over extracts and over prior typed artifacts, with plain query terms, a time filter that cannot pass the workflow's cutoff, the role's projection applied before ranking, and at most 10 results. No vector database.
- **Polling and triggers.** The fetcher polls each approved source at its registered interval inside its budget. A new item or revision creates a `SOURCE_REVISION` trigger, deduplicated by source, external ID and revision, with a cooldown per source and symbol.
- **Candidate for M6-OD1** (OBSERVED on 2026-10-03, §6):
  - GitHub's "List releases" endpoint for `bitcoin/bitcoin` and `anza-xyz/agave`. It is documented, needs no key for public repositories, and carries `published_at`; preserve a release `updated_at` only if supplied. B0 confirmed the documented asset update timestamp is not a release update timestamp. Unauthenticated requests are limited to 60 an hour per IP address.
  - The Solana status page documents a JSON API with incident times.
  - **B0 rights review recorded:** the two release feeds' repository-license/terms basis and attribution/retention scope are in [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m6-b0-official-guidance--2026-10-03). The alternative Solana status feed is not selected or rights-reviewed. Whether either release feed carries information about prices remains a research question that M6 does not answer. Exact-hash source approval remains an owner M6-B action.
- **Isolated tests** use a loopback mock source that exists only in test stacks, as the mock provider does.

### 5.8 Agent runtime, definitions v2

- **Tools added** (catalog v2). `request_review` and the three M7 tools stay absent and refused.

| Tool | Roles | Effect | Notes |
|---|---|---|---|
| `search_evidence` | ANALYST, RESEARCHER | `READ` | Scope `SOURCES` or `ARTIFACTS`; results can be cited by item |
| `request_source_refresh` | ANALYST, RESEARCHER | `QUEUE_SOURCE_REFRESH` | Source ID and typed filter; the workflow waits for the outcome |
| `register_candidate` | RESEARCHER | `RECORD_RESEARCH` | Hypothesis and declaration; returns the candidate ID and normalized hash, or the existing one |
| `request_experiment` | RESEARCHER | `QUEUE_RESEARCH_JOB` | Candidate and dataset; runs the screening set; the workflow waits |
| `read_experiment` | all, scoped | `READ` | Projection by role and information cutoff (§5.5) |
| `record_research_proposal` | RESEARCHER | `RECORD_AGENT_ARTIFACT`, FINISH only | May nominate one candidate for review |
| `request_promotion` | COORDINATOR | `QUEUE_OWNER_PROPOSAL`, FINISH only | Refused unless the candidate is `EVIDENCE_READY` |

- **Permissions follow [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), the canonical document.**
  - Search and refresh go to ANALYST and RESEARCHER. EVALUATOR and COORDINATOR open the evidence items that the artifacts in their scope cite, through `read_artifact`, and do not search.
  - `request_promotion` goes to the COORDINATOR only.
  - [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md) lists more roles for both; B0 reconciles it to the matrix.
- **Effects.** The registry's allowed list grows by the four new effect classes and nothing else. A static test asserts that no tool handler imports the accounting, broker or execution store modules. None of the new effects is financial.
- **Workflow graph (code-owned; no model-chosen delegation).**

| Template | Role | Started by | Then |
|---|---|---|---|
| `EVENT_INVESTIGATION_V1` | ANALYST | Owner, source trigger | Fixed child `ASSESSMENT_REVIEW_V2`. If the assessment names a research question and the review is not `REJECT`, the orchestrator may queue a research workflow inside the daily budget |
| `RESEARCH_V1` | RESEARCHER | Owner, schedule, follow-on | On a nominated candidate: the full test set with the holdout, then fixed child `CANDIDATE_REVIEW_V1` |
| `CANDIDATE_REVIEW_V1` | EVALUATOR | Orchestrator | Review bound to the proposal's and the results' hashes |
| `PROMOTION_V1` | COORDINATOR | Owner, or SYSTEM when a candidate becomes `EVIDENCE_READY` | A pending promotion, or an abstention |

- **Waiting.**
  - A tool that queues work returns at once with the job reference. The workflow moves to `WAITING_TOOL` and releases the inference slot.
  - The outcome arrives as one completion row with its own `result_ref`, which the artifact may cite. The workflow resumes once from it. There is no model polling.
  - **Cutoff.** The workflow's cutoff does not move. An `EVENT_INVESTIGATION_V1` receives what its own refresh fetched through the completion, not through a search past the cutoff. For `RESEARCH_V1`, source content in that completion and initial/follow-on context obeys the hypothesis cutoff; post-cutoff evidence and text derived from it are withheld. Later creation of a typed artifact derived only from authorized pre-cutoff inputs does not itself make those inputs unavailable. This clarification was approved in chat on 2026-10-03 ([decision](../../DECISIONS.md#2026-10-03--m6-b0-research-cutoff-clarification)).
  - **Deadlines.** Model time and waiting time are counted apart: the workflow deadline covers running time only, and each wait has its own deadline (PROPOSED 6 h). When a wait expires the workflow is `EXPIRED` and the job's result stays as history.
- **Budgets v2 (PROPOSED).**
  - A parent: 12 model steps and 10 tool calls; at most 3 experiments.
  - A child has its own budget of 4 steps and 3 tool calls, instead of drawing on its parent as in M5.
  - 24 parent workflows a day; depth 1; one inference slot; the existing quiet window.
- **Priority (code-owned).** Probes, then owner-started work, then promotion, then triggered investigations, then research. A model cannot raise its own priority.
- **AgentStep schema v2.** The single argument object gains the new nullable fields. The candidate declaration is flat and bounded. Whether the larger schema stays within the model's structured-output limits is checked in B0 against the pinned CLI and the mock provider, and again by the live probes. Every output is still fully re-validated in the engine.
- **Prompts.** `prompts/m6/analyst.v2.md`, `researcher.v1.md`, `evaluator.v2.md`, `coordinator.v1.md`: versioned, hashed, packaged as in M5.
- **Profile.** Definitions v2 change the profile hash. After deployment the M5 profile no longer matches, and the runtime needs a new approval and a probe run before any model call. Probes CP-15 onward cover the new tools: an unregistered source, an unknown operator, a holdout request by the researcher, a read past the information cutoff, a promotion without evidence, and one positive chain.

### 5.9 Owner API and pages

- **Routes** (same session, CSRF, Host, strict-body, idempotency and no-store rules as M4 and M5):
  - reads: `GET /v1/sources`, `/v1/evidence`, `/v1/evidence/{id}`, `/v1/research/status`, `/v1/research/hypotheses`, `/v1/research/candidates`, `/v1/research/candidates/{id}`, `/v1/research/experiments`, `/v1/research/datasets`, `/v1/research/shadows`, `/v1/promotions`;
  - owner requests: `POST /v1/sources/{id}/refresh`, `/v1/research/jobs/{id}/cancel`, `/v1/research/shadows/{id}/stop`;
  - `/v1/agent-approvals` and `/v1/agent-workflows` accept the new target kinds and templates.
- No route accepts a tool name, a URL or a candidate from the browser. Owner-started research names a registered template and bounded parameters only.
- `SystemStatus` gains `research` and `sources`. The web schema accepts both shapes during the rollout.
- **Pages** (official shadcn skill and project discovery at implementation; existing primitives only):
  - `/evidence`: sources with approval and health; items with their four times; an item's extract as labeled plain text.
  - `/research`: hypotheses, candidates with lifecycle, every trial including failed and refused ones, results (the M4 report view with research labels), shadows, staging gaps.
  - Approvals: a "Research and sources" section for the envelope, source versions and promotions. A promotion offers Reject only, and says why. The M4 pilot section does not change.
  - Agents: the new templates in the start dialog; the profile diff.
- **Labels:** `MODELED REPLAY`, `SHADOW — deferred replay`, `HOLDOUT — locked`, `HYPOTHETICAL COST SCENARIO`, `HISTORICAL — the model may know later events`, "model-authored — untrusted".

**B7 implementation (IMPLEMENTED 2026-10-05; owner decisions of that day).** The route contract is in [API_CONTRACTS](../contracts/API_CONTRACTS.md#m6-owner-routes-execplan-0023-b7). What the list above did not settle:
- **Four more routes.** `GET /v1/sources/requests/{key}` and `GET /v1/research/requests/{key}` resolve an unknown outcome, as the M4 and M5 mutations can. `GET /v1/research/experiments/{id}` and `/cells/{index}` return one job's result, the second one cell's evaluation document whole, so that the list stays small and no response grows with a result.
- **`/v1/research/experiments` lists requests.** Every request for an experiment is one row: queued, answered with an existing job, or refused, with its recorded reason. That is the trial ledger the page needs; a job's later events are in its detail.
- **Owner starts.** The three owner-startable M6 templates and their parameters come from the template definitions B6 seeded. `PROMOTION_V1` takes the ID of an `EVIDENCE_READY` candidate.
- **Cancel, stop and refresh are requests.** The API identity records them; the research and source identities apply them. A canceled job stays final for its input and a stopped shadow retires its candidate.
- **A promotion's rejection** is the owner's exact-hash record; the agent worker applies it to the promotion and the candidate as SYSTEM.
- **The owner reads the holdout.** §5.5 gives results to EVALUATOR, COORDINATOR and OWNER. The API marks each row that rests on the holdout or a shadow with what is locked for the tuning roles, which is what the `HOLDOUT — locked` label states.
- **`SystemStatus.research` and `.sources`** are derived from approvals, jobs, the bridge's journal and fetch records. Neither service writes a heartbeat to the database, so `unavailable` means "no recent record", not "the container is down".
- **The browser path (B8).** The same-origin functions with their Origin and CSRF checks, and the pages, are IMPLEMENTED in B8 (§18). B7's own web change was limited to schemas that accept both rollout shapes.
- **Not built, because the list has no route for it:** an on-demand shadow advance, and anything that writes the `WITHDRAWN` promotion state.

### 5.10 Resources and priority

- **Memory is the tight resource.** The limits of §5.1 add about 2.3 GiB to about 5.6 GiB of existing limits, on a VM of about 7.7 GiB that other containers share. Limits are caps, not use. B0 measures real use with the normal app and one isolated stack running. If it does not fit, the research limits are lowered, or research and isolated test stacks do not run at the same time. The plan asserts no figure before the measurement.
- **B0 resource observation, 2026-10-03.** VERIFIED the native workload completed at the unchanged 1-CPU/1-GiB cluster and 1-CPU/768-MiB engine limits while the normal app continued. Over 54 samples the VM retained 5,729,200–6,178,500 KiB available; normal-container memory reported by Docker ranged approximately 1.45–1.59 GB in aggregate. Windows free physical memory was separately observed at 1,396,180 KiB during load. This supports keeping the limits for one sequential isolated stack; it does not verify simultaneous fetcher/bridge/runner saturation. B9 must still pass that workload and coexistence budgets.
- **Saturation test (R17).** An isolated stack runs the M2 stream workload and an execution fixture while the runner and its cluster run at their limits. The budgets are the existing ones: no `QUEUE_OVERLOAD`, receipt-to-publication p99 under one second, and the execution workload's own step budget.
- **Hour boundary.** No job starts and no staging batch runs between HH:58 and HH:07 UTC (PROPOSED), which keeps research off the pilot's hourly marks and report.
- **Disk.** New jobs and staging are refused above the store cap or under disk pressure.

### 5.11 Invariants

1. No research, source or agent identity can write an M1–M4 table.
2. The process that runs candidates has no route and no credential to the main database.
3. A candidate strategy activates only under replay in a research database.
4. Same inputs, same portable fingerprint.
5. Every trial is recorded before it runs; none is deleted.
6. A tuning role sees nothing from after its hypothesis's information cutoff.
7. No promotion is approved in M6.
8. A fetch goes only to an approved source version's host and path templates.
9. A recorded shadow mark never changes.
10. Disabling the runtime, or revoking the envelope or a source, cancels queued work and makes late results history only.

### 5.12 Research on bar history: why it is not in M6

The first draft derived a few modeled quotes from each hourly bar and ran the unchanged engine on them. That cannot work:
- **The engine needs dense quotes** (§2). Each fill needs two quotes of one symbol 1 to 7 seconds apart. A few points an hour give none, so no order would ever fill.
- **Dense modeled quotes are slow.** A quote every five seconds over 730 days is about 25 million rows, about 2.5 hours a replay at the measured rate.
- **Sparse quotes are not conservative.** A stop seen at one point would sell at the next. Every held hour would also log a protection gap, and the hourly marks need a fresh quote for both symbols.
- **Labels.** A modeled availability time on a row labeled as a provider's bar, and a made-up displayed quantity, both conflict with DATA_CONTRACTS and PAPER_EXECUTION.

A workable design is a financial model of its own: timed quote clusters derived from the engine's rules, one modeled label for every modeled row, its own cost-model and fidelity definitions, a research eligibility rule, invariants and its own tests, with the replay cost measured first. Under the approved M6-OD2 (b) it gets its own ExecPlan; it is not part of M6's completion. B0 corrected the draft's option-letter typo here; the approved exclusion is unchanged.

## 6. Official source and version evidence

| Subject | Source | Status |
|---|---|---|
| GitHub "List releases" | https://docs.github.com/en/rest/releases/releases | OBSERVED 2026-10-03: "Information about published releases are available to everyone"; `created_at`, `published_at`, `updated_at`, `body`, `html_url`; `per_page` up to 100 |
| GitHub rate limits | https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api | OBSERVED 2026-10-03: 60 unauthenticated requests an hour per originating IP address; `x-ratelimit-*` headers; no retry before the reset time |
| The two release feeds | `gh api repos/bitcoin/bitcoin/releases`, `repos/anza-xyz/agave/releases` | OBSERVED 2026-10-03 through the authenticated client: both return releases with those fields. The unauthenticated path the fetcher would use is NOT RUN |
| Solana status API | https://status.solana.com/api | OBSERVED 2026-10-03: documented JSON endpoints for incidents and maintenances with `created_at`, `updated_at`, `resolved_at`. Authentication is not stated on the page |
| Terms and retention rights of both | — | NOT REVIEWED. B0 gate for M6-OD1 |
| Structured-output schema limits | https://developers.openai.com/api/docs/guides/structured-outputs | NOT VERIFIED: the page was fetched and its limits section was not retrieved. B0 |
| SSRF defenses | [SEC-01](../../REFERENCES.md#sec-01) | On record; to be re-read in B0 against the implementation |
| Container resource limits | [OPS-04](../../REFERENCES.md#ops-04) | On record; measured in B0 |
| Chronological validation | [EV-02](../../REFERENCES.md#ev-02) | On record; motivation only |
| PostgreSQL full-text search and database creation | Official documentation for the pinned major version | NOT READ for this draft. B0 |

**Dependencies.** None is expected: the fetcher uses the HTTP client already locked for the market worker, and search uses PostgreSQL. B0 confirms it; a new dependency would need its purpose, source, version and license recorded first.

**B0 M6-OD4 measurement predicate (PROPOSED operational interpretation, declared before the next loaded comparison).** The report for the next hourly as-of must be recorded during its HH:05 UTC minute, with the same pilot and generator identity; the complete bounded observer must have zero failed reads and unchanged normal container/image/start/restart identities. Compare exact offsets with the preceding baseline and disclose the loaded phase's actual interval. This verifies the report's scheduled minute for that observed workload, not identical millisecond latency or a guarantee about future workloads. If the report is missing, shifts out of HH:05, or an identity changes, the gate fails and the implementer asks the owner. Until this check is recorded, heavy phases keep HH:15–HH:55. Later coexistence/saturation gates remain mandatory.

**B0 M6-OD4 measurement result (VERIFIED for the declared predicate, 2026-10-03).** The approved observer completed 16:14:41–17:09:44 UTC: 169 Docker reads, all exit 0, 54 samples, and zero identity differences across all nine normal containers. The research-limit native sample ran 16:16:02–16:28:39 UTC. The next SNAPSHOT (as-of 17:00) was created at 17:05:30.318837 UTC, with the same pilot and generator as the 16:05 baseline. Exact baseline offsets: 14:05 27.782870 s, 15:05 28.607944 s, 16:05 29.355027 s; next offset 30.318837 s, an increase of 0.963810 s. The loaded sample did not overlap HH:05; no identical-latency or future-workload claim is made. The scheduled report minute was preserved, clearing the conditional M6-OD4 gate. Subsequent isolated heavy work may use HH:07–HH:58, sequentially; the B0 probe retains a one-minute finishing reserve. Evidence: `.cache/m6/m6-b0b/b0-measurement-summary.json`, SHA-256 `3be4063fa81c83bdfd9c9e0426c8d252a1202f8c87d1a7120d3feef71a893b7a`; it binds the original observer summary/journal and replay file hashes. B9 coexistence and saturation remain required.

**B0 refresh, 2026-10-03 (OBSERVED documentation, not runtime compatibility).** The draft observations above remain historical. The implementing engineer read the current official Structured Outputs limits, PostgreSQL 17 full-text search and `CREATE DATABASE`, OWASP SSRF, Docker memory limits, chronological split guidance, GitHub release documentation and terms, and the two repository licenses. See [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m6-b0-official-guidance--2026-10-03). The current release-documentation example supplies `published_at` at release level but places `updated_at` on assets; an absent release update timestamp must remain null. It must not be inferred from an asset. The rights-review item is recorded there (INFERRED applicability of repository licenses through GitHub D.6; local release text and attribution only). The full runtime v2 schema and live source fetching remain NOT RUN; the contract preview passed the pinned CLI/mock probe recorded in §18.

**B1 restore guidance, 2026-10-03 (OBSERVED).** PostgreSQL 17's [catalog information functions](https://www.postgresql.org/docs/17/functions-info.html#FUNCTIONS-INFO-CATALOG-TABLE) describe `pg_get_constraintdef` and `pg_get_indexdef` as reconstructed SQL. In the isolated `m6-b1b` dump/restore, 72 CHECK expressions and four partial-index predicates across 49 protected tables changed only the representation of varchar enum arrays cast to text arrays. All other metadata and all legacy/M6 row fingerprints match. The authorized harness correction canonicalizes that one observed form for restore comparisons only and records every rewrite; in-place migration/downgrade still requires the original exact structure fingerprint. Unit negatives and a PostgreSQL expression-equivalence check accompany the correction. This introduces no dependency or protected DDL change.

## 7. Data and trust-boundary changes (PROPOSED)

- **New model inputs.** Evidence extracts from approved sources; research results in the role's projection; prior typed artifacts returned by a search. Still excluded: account, ledger, owner, pilot, pin and secret data.
- **New outbound path.** `source-fetcher` to approved hosts and paths only. The research bridge, runner and cluster have no route out. The agent runner's egress does not change.
- **New stored data.** Source text (bounded, hashed, under each source's retention rule); candidate declarations; trial history; copies of public market rows in the research cluster.
- **New credentials.** Research-only secrets for the research cluster. None of the main database's secrets reaches a research service.
- **Authority.** No new financial, approval or trading authority. The only new owner approvals are of an envelope and of source versions.
- **External-data permission** ([PLANS](../../PLANS.md)): each source version states its scope, clock fields and rights. A model never widens it.

## 8. Proposed file edits

- `services/engine/app/agents/`: definitions v2, schemas v2, the new tool handlers, wait and resume in the orchestrator, the trigger scheduler, probes CP-15 onward.
- `services/engine/app/sources/` (new): registry, transport, parsers, worker.
- `services/engine/app/research/` (new): grammar, interpreter, catalog store, jobs, runner, bridge, stager, shadow schedule, projections.
- `services/engine/app/strategies/`: the new operators and the strategy interface.
- `services/engine/app/execution/engine.py`, `store.py`, `activation.py`: the interface at every binding of §2. No change to sizing, risk, fills, ledger or protection.
- `services/engine/app/experiments/manifest.py`: the strategy slot and the stated quote rule for research manifests only.
- `services/engine/app/replay/`: the research experiment for a candidate; the portable projection used by R07 and R14.
- `services/engine/app/evaluation/`: used as it is. Changed only if a research report needs a label it cannot state today; a forward report stays byte-identical.
- `services/engine/app/main.py`: the routes of §5.9.
- `services/engine/alembic/versions/0008_m6_research.py`.
- `services/agent-runner/prompts/m6/`.
- `apps/web/src/evidence/`, `apps/web/src/research/`, the approvals and agents modules.
- `compose.yaml`: the services, networks and secrets of §5.1 only.
- `tools/`: the four scripts of §3.1.
- Contracts updated with the code: AGENT_TOOL_CONTRACTS, AUTONOMY_MATRIX (owner controls), RUNTIME_AGENTS, RESEARCH_WORKFLOWS, DATA_CONTRACTS, API_CONTRACTS, SECURITY, DOCKER, CONFIGURATION, FRONTEND, OPERATIONS, TESTING, ARCHITECTURE, EVALUATION, MARKET_DATA, STATUS, COMMANDS, INTEGRATION_EVIDENCE.

Not touched: `app/market_data/`, `app/accounting.py`, every M1–M4 migration, the pilot's Compose blocks, the agent runner and its egress gateway.

## 9. Implementation sequence (PROPOSED)

| Batch | Content | Checks |
|---|---|---|
| B0 | Contracts reconciled and amended; harness skeleton; the gates of §6; host and replay-rate measurements; the M6-OD4 measurement | Documentation and measurements recorded |
| B1 | Migration 0008, roles, views, guards, seeds | `Migration`, grant and trigger tests |
| B2 | Grammar, operators, interpreter, the strategy interface | Unit and property tests; `EngineParity`; M3 and M4 regression |
| B3 | Research cluster, runner, jobs, results, trial ledger, holdout projections | `ResearchRunner`, `HoldoutIsolation` |
| B4 | Bridge, staging, versioned stores, shadows | `Staging`, `ShadowSchedule` |
| B5 | Source registry, fetcher, evidence, search, triggers | `SourcePolicy`, `EvidenceInjection` |
| B6 | Definitions v2, tools, workflows, waiting, prompts, probes | `AgentOffline6`, `DispatcherAuth6`, `AgentFaults6` |
| B7 | Owner API, OpenAPI, generated types | `ApiAuth`; contract and drift checks |
| B8 | Pages (skills loaded) | `BrowserResearch`, `BrowserResearchError` at 390 and 1440 px |
| B9 | Saturation, mixed version, coexistence, activation rehearsal; final acceptance | Every §10 phase; Q01–Q10 resolved |
| B10 | Inert normal deployment (§13.1) | Pilot untouched; identities recorded |
| B11 | M6-B (owner-gated, §13.2–13.3) | Probes and walk-through |

B3–B4 and B5 do not depend on each other and can be built in either order after B2. B6 needs both.

**B9's acceptance as the owner scoped it on 2026-10-08** ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-m6-a-is-accepted-on-what-the-inert-deployment-switches-on)). M6-A is accepted on the phases of §10 that the inert deployment of §13.1 depends on, on one fresh run and one image: `Build`, `Generate`, `Checks`, `Regression`, `Migration`, `MixedVersion`, `EngineParity`, `ResearchRunner`, `HoldoutIsolation`, `Staging`, `ShadowSchedule`, `SourcePolicy`, `EvidenceInjection`, `AgentOffline6`, `DispatcherAuth6`, `AgentFaults6` with its process part, `ResearchActivationRehearsal`, `ApiAuth`, `BrowserResearch`, `BrowserResearchError`, `BrowserRegression`, `PerformanceApi`, `PerformanceBrowser`, `SecretScan` and `Report`. `PerformanceResearch`, `ResearchSaturation` and `PilotCoexistence` measure the research services under load, which the inert deployment does not start. They are not part of M6-A; they are the gate of the M6-B activation (§13.2). Q06 is resolved for M6-A by `PerformanceApi` and `PerformanceBrowser`; R17 and the budgets of research jobs, idle dispatch and staging are NOT RUN for M6-A. One budget inside `PerformanceApi` is a condition of the activation too, by the owner's decision of the same day ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-the-search-budget-is-a-condition-of-the-activation)): the analyst's search, MEASURED at 213.36 ms at p95 against 150 ms on 10,000 items at the extract cap, is recorded against its budget and not judged for M6-A.

## 10. Verification commands (implementation recorded per batch)

```powershell
./tools/m6-acceptance.ps1 -RunId <run> -Phase <phase>
```

Phases, in order: `Prepare`, `Snapshot`, `Build`, `Generate`, `Checks`, `Regression`, `Migration`, `MixedVersion`, `EngineParity`, `ResearchRunner`, `HoldoutIsolation`, `Staging`, `ShadowSchedule`, `SourcePolicy`, `EvidenceInjection`, `AgentOffline6`, `DispatcherAuth6`, `AgentFaults6`, `ResearchSaturation`, `PilotCoexistence`, `ResearchActivationRehearsal`, `ApiAuth`, `BrowserResearch`, `BrowserResearchError`, `BrowserRegression`, `PerformanceResearch`, `PerformanceApi`, `PerformanceBrowser`, `SecretScan`, `Report`, `Stop`, `Clean`.

- **B9 additions to this list (owner decision of 2026-10-06, [DECISIONS](../../DECISIONS.md#2026-10-06--m6-b9-phase-content-images-saturation-length-job-measurement-row-counts-quiet-window-lost-store-regression-and-the-read-only-look)).** `BrowserRegression` follows `BrowserResearchError`. `AgentFaults6` has a second part, the process-level faults, with its own record. `Regression` also runs six M0–M2 files. What each B9 phase does and what makes it fail is in [TESTING](../TESTING.md#m6-b9-rollout-saturation-performance-faults-and-final-acceptance-execplan-0023).
- **B9 rollout targets.** `MixedVersion`, `PilotCoexistence`, `ResearchActivationRehearsal`, `ResearchSaturation` and `BrowserRegression` run the product Compose file under their own project name, env file, secrets and `10.253.x` subnets, because the owner's scripts act on that file. The web's frontend network is not internal there, as in M5; no test container uses it to reach a public endpoint.
- Isolated Compose projects `asl-m6-<run>-<kind>` with `asl_m1_` databases, per-run secrets, their own subnets and no Internet route, as in M5. The owner's `.env` is never inherited.
- Synthetic fixtures, the recorded provider, the fake CLI, the mock provider and the mock source only. No public endpoint and no model call.
- **Which phases M6-A is accepted on (owner decision of 2026-10-08, §9).** Every phase of the list above and `BrowserRegression`, except `PerformanceResearch`, `ResearchSaturation` and `PilotCoexistence`. Those three stay in the harness and are run for the M6-B activation gate, on a run of their own: `Report` does not require them, and it refuses an acceptance run on which one of them was started.
- A skipped test fails its phase. `Stop` never removes a volume.
- `Clean` removes the run's containers, networks, volumes and images by the names in its manifest, and nothing else. It is run for every run once its evidence is recorded, and no run is left behind when a batch is reported ([DOCKER](../../DOCKER.md#cleaning-up-disposable-resources), owner decision of 2026-10-03).
- Budgets are declared in B0 before they are measured: the existing M2–M5 budgets for the unchanged paths, and for the new ones the job wall clock, queue delay, staging rate, search latency and page budgets.
- **B0 declared engineering budgets (PROPOSED targets, 2026-10-03, before new-path measurements):** job wall clock stays at the approved 3,600 s; idle queue dispatch outside the quiet period p95 at most 5 s; staging at least 1,000 public rows/s over a one-day full-density synthetic store, with each bounded batch at most 500 rows; cutoff-filtered search over 10,000 evidence items p95 at most 150 ms. Catalog API keeps M5's p95 250 ms sequential / 500 ms at five concurrent readers; pages keep SSR p95 below 1,500 ms, LCP at most 2.5 s and CLS at most 0.1 at the two declared widths. These are engineering acceptance targets, not performance observations or research-return thresholds. Active-job and quiet-window waits are shown separately from idle queue delay. The unchanged M2–M5 budgets remain binding; none is relaxed.
- The quiet period and the rerun rule follow M6-OD4 as decided on 2026-10-03 (§3.3): the rerun rule applies from the start, and the narrower quiet period only once B0 has recorded its measurement. Until then the M5 quiet period applies unchanged.

## 11. Q01–Q10 matrix (PROPOSED)

| Gate | Applies | Acceptance condition | Planned evidence |
|---|---|---|---|
| Q01 UX | Yes | Evidence, research and approval pages with loading, empty, error, stale and unavailable states; nothing optimistic | `BrowserResearch`, `BrowserResearchError` |
| Q02 Accessibility | Yes | Keyboard, focus, labels, contrast and responsive behavior on the new pages; no screen-reader claim | Automated browser checks and inspection |
| Q03 Data correctness | Yes, core | R06–R15, R20; append-only history; exact decimals; determinism | `EngineParity`, `ResearchRunner`, `HoldoutIsolation`, `Staging`, `ShadowSchedule` |
| Q04 Security | Yes, core | R01–R05, R16; ASVS chapters mapped as in M5 | `SourcePolicy`, `EvidenceInjection`, `DispatcherAuth6`, `ApiAuth`, `SecretScan` |
| Q05 Reliability | Yes | R12, R13 and the cases of §4.1 | `AgentFaults6`, `ResearchRunner`, `Staging` |
| Q06 Performance | Yes | R17 and the declared budgets | `ResearchSaturation`, `PerformanceResearch`, `PerformanceApi`, `PerformanceBrowser` |
| Q07 Automated verification | Yes | Every phase in Docker with no skipped test | §10 |
| Q08 Visibility | Yes | Research, staging and source health, queue, budgets and incidents visible; redacted logs | Status routes; log review; `SecretScan` |
| Q09 Deployment | Yes | §13.1: backup, forward migration, verified images, pilot unchanged, rollback rehearsed | `Migration`, `MixedVersion`, the deployment record |
| Q10 Maintainability | Yes | Contracts updated with the code; official sources re-read at the pinned versions; no new dependency without a record | Diff review; INTEGRATION_EVIDENCE |

## 12. Coexistence with the running pilot

- **Never touched:** the pilot's containers, images, Compose blocks, tables, constraints and grants. The deploy script compares their rendered configuration and their container identities before and after, as M5's does.
- **Code identity.** M6 changes files under `app/`, so an execution worker built from M6 would have a new identity. None is built. The identity split recorded for M5 continues until the experiment boundary.
- **Database load on the pilot's cluster.** Only the catalog's small rows and the bridge's bounded, paused reads through views. Views take only a shared lock. Replay never runs there.
- **Migration.** 0008 touches no M1–M4 table. The pilot's workers do not check the schema revision; only the API does.
- **Hour boundary.** No research job start, staging batch or model step in the quiet windows.

## 13. Deployment and activation

### 13.1 M6-A, inert (standing authorization for milestone deployments; pilot rules apply)
1. HH:15–HH:45 UTC, never 23:50–00:20.
2. Read-only starting state; protected backup with its SHA-256; an isolated restore, because the schema changes.
3. Rollback tags on the `api`, `web` and agent-worker images.
4. Web first, then the API, then migration 0008 with its lock timeout and retries, then `agent-worker`.
5. Research and source services are built and **not started**. `asl_research` and `asl_source` stay NOLOGIN. The flags stay `0`.
6. Verify read-only: every pilot container unchanged; lease epoch and experiment version unchanged; readiness; the pages in the browser; the runtime waiting for a new profile.

### 13.2 M6-B activation (each step on the owner's instruction)
0. **Before anything is activated (owner decisions of 2026-10-08):** `PerformanceResearch`, `ResearchSaturation` and `PilotCoexistence` pass in isolation on the build that is to be activated, the performance pull request has brought the full test and the shadow advance at 14 and 21 days under the bound of 3,600 s in that measurement, and the analyst's search meets its 150 ms in `PerformanceApi` ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-the-search-budget-is-a-condition-of-the-activation); [DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-m6-a-is-accepted-on-what-the-inert-deployment-switches-on)).
1. `tools/research-activate.ps1`: backup, create the research-only secrets if missing, enable the two identities, migrate the research cluster, start the research and source services, start staging.
2. The owner approves the research envelope and, under M6-OD1 (a), the source version, by exact hash in the UI.
3. The owner composes and approves the new runtime profile and starts the probes.
4. Optionally, the owner enables the runtime.

### 13.3 The live walk-through
Run by the owner from the UI, verified read-only by the implementer:
1. An investigation in which the analyst refreshes the approved source and cites an item.
2. A research workflow in which the researcher registers a valid candidate and an experiment runs to a recorded result.
3. The evaluator's review of that result.

- A model that abstains is a valid outcome for a single run; each step needs one success within the probe and daily budgets.
- That nothing can be promoted without evidence is checked by a probe, not by the walk-through.

**What the walk-through leaves to isolated evidence** (M6-OD7):
- the gate clause "a promotion request remains pending rather than self-approved". A live one needs a shadow with at least seven days of evidence;
- under M6-OD1 (b), "an analyst obtains permitted evidence".

**Follow-ups after completion under M6-OD7 (a):**
- the first shadow that reaches the evidence minimum and the first live pending promotion;
- a live shadow engine, the engine-level `SHADOW` value and a multi-account ledger, at the experiment boundary;
- M5's token-refresh check.

## 14. Failure and rollback

- **M6-A rollback:** the previous `api`, `web` and agent-worker images by their rollback tags, after the guarded downgrade of 0008 (§5.2), which is valid while no real research row exists. An M5 agent worker cannot run on the 0008 schema's extra definitions. The backup is never restored over the running pilot without an explicit owner decision.
- **After M6-B:** fix forward. `tools/research-deactivate.ps1` stops the research and source services and returns the identities to NOLOGIN. Removing the research cluster's volume loses the stores (§5.4), not the recorded results.
- **A parity failure in B2** blocks the interface: the forward path must stay identical.
- **A schema the model cannot satisfy** (B0): the candidate declaration is split over two tool calls. The grammar does not change.
- **A source that fails its rights review:** M6-OD1 (b).
- **Research that disturbs the pilot in B9:** lower the limits and repeat. No budget of the pilot is relaxed.
- **Runtime blocks** (`AUTH_REQUIRED`, `QUOTA_BLOCKED`) stop model work only. Research jobs already queued finish; nothing financial depends on either.

## 15. Where the time goes, and what this plan does about it

- **Observed in M5:** nine batches over three calendar days, with a host outage overnight; by 2026-10-01 the final acceptance pass had been restarted four times at about 2.5 hours each; completion then waited on an 8-day criterion.
- **In this plan:**
  - no calendar-time completion criterion, if the owner chooses M6-OD7 (a);
  - the external source cannot block completion (M6-OD1);
  - bar-history research is left out (M6-OD2);
  - the two acceptance rules of M6-OD4;
  - one inert deployment, with no soak beyond the first hour boundary;
  - M6-B is a few owner actions and one sitting.
- **Not estimated.** M6-A has ten implementation batches before its deployment, several larger than M5's. There is no measured basis for a date, and this plan gives none.

## 16. Progress

- 2026-10-08, 22:30 UTC, **B10 done: M6-A is deployed inert to the normal application.** On the owner's
  approval in chat (deploy, then merge). A first start at 20:15 UTC stopped in its read-only preflight on a
  defect of the deploy script, with nothing changed; one line was fixed as the owner chose. The second start
  ran from 22:15:01 to 22:20:13 UTC on commit `583a98a` and completed. Verified read-only: the pilot's
  containers, lease and experiment unchanged, schema 0008, both flags `0`, no research or source container.
  What the deployment superseded is removed. §18 (B10) holds the record. What remains of M6 is M6-B, the
  owner's, behind the gate of §13.2.
- 2026-10-08, 18:22 UTC, **B9 delivered.** The acceptance evidence for M6-A, in the scope the owner decided
  that day, is VERIFIED on run `m6-b9s`: 25 phases, each in its first attempt, `Report` VERIFIED (§18). Pull
  request 32 was opened against `main`; every test run of the batch was removed by exact name.
- 2026-10-07, 14:00 UTC, four owner decisions taken (about 13:26 UTC) and implemented, NOT RUN in a stack: what
  stops a test run beside the pilot (a burst rule for the rows the pilot writes on its own; the rule and
  `tools/m6-pilot-watch.ps1`), the owner scripts report those rows and do not stop on them, the schema change
  stays in 0008, and the market worker's log was read once: both restarts of 2026-10-06 were its hourly
  retention canceled by a statement timeout (§19; a defect of the worker, outside this batch, flagged as a
  separate task). Test runs may resume: an authoring run with every fix comes next.
- 2026-10-07, 12:30 UTC, B9 fix round in the tree, NOT accepted, still no test run since 2026-10-06 21:18 UTC:
  the findings of a second, a third and a fourth read-only review are fixed (local commits `3d87ba0` and
  `eb1bf82`, not pushed) and checked without a stack only: the parser on every script, `ruff` on the engine tree,
  47 env file cases, and the deploy script against a model (17 scenarios, 72 expectations). No phase and no
  `pytest` has run on this tree, so every new test and every changed phase is NOT RUN. Found on the way: three
  more product defects (§18), a reader of this batch that did not read the env file as Compose does, and
  cleanups that a passed deadline would have skipped. `PerformanceResearch` now takes eight test windows. The
  owner's decisions of §19 are open; the first of them, what stops a test run beside the pilot, blocks every
  further run. At 13:03 UTC `main`, which had gained pull request #30 (`0f395a9`: the older pilot and agent tools
  write the resolved env file, and `tools/lib/Pilot.psm1` stops on its own errors), was merged into the branch
  as `73789b9`; an acceptance run will be of a tree that holds it.
- 2026-10-06, 21:30 UTC, B9 implemented, NOT accepted, test runs stopped: the phases §10 left for B9, the
  process faults, `BrowserRegression` and the owner scripts exist (local commit `3d10fec`, not pushed). Authoring
  runs `m6-b9a` to `m6-b9i` only; §18 (B9) records each. Passed at least once: every phase except
  `ResearchSaturation`, `PerformanceResearch`, the process part of `AgentFaults6`, `PerformanceBrowser`,
  `SecretScan` and `Report`. A first independent review gave 29 findings, among them two product defects (a job
  sent into a re-initialized research cluster; staging that stopped during a long job), fixed with tests. The
  year-of-rows API measurement missed its budget and passes with a PROVISIONAL schema change in 0008 that waits
  for the owner. INFERRED and not yet measured: the 21-day full test exceeds the job bound. The real market
  worker restarted twice in the afternoon; the timing says the tests did not cause it; a watch that applies
  decision 8 as written stopped the run at 21:18:38 UTC on a kind of row the pilot also writes with no test
  running. No test runs until the owner decides the points in §19. No acceptance run exists. B10 is NOT RUN.
- 2026-10-06, 12:49:48 UTC, B8 PR merged (recorded by this checkpoint, as the
  entry below left it): VERIFIED read-only at the start of B9 that pull
  request #29 is MERGED as `4ece326e29c7dd1239003b71ac8eca643159ee85`, an
  ordinary merge commit of head `26aad18` into `main` at `2043fc0`, that
  `main` and `origin/main` are at that commit with a clean tree, and that no
  pull request was open. The primary checkout was switched from the merged B8
  branch to `main` and fast-forwarded. B9 is branched from it as
  `claude/m6-b9-final-acceptance`. Before any code: the content of the phases
  §10 names without defining, and the points this plan does not decide for B9
  and B10, are put to the owner with a recommendation each. Nothing of B9 is
  run yet and no command addressed the normal app.
- 2026-10-06, 12:47 UTC, B8 PR, merge requested: OBSERVED owner instruction
  `merge it` for pull request #29
  ([decision](../../DECISIONS.md#2026-10-06--owner-asks-to-merge-the-m6-b8-pr)).
  VERIFIED read-only that `main` is still at `2043fc0`, the commit B8 was
  branched from and accepted on, and that PR #29 is open, mergeable and clean
  at head `1ab82be`. Nothing has to be merged into the branch and no phase has
  to be rerun. The PR is merged with an ordinary merge commit pinned to the
  verified head, without force, an admin bypass or branch deletion. This entry
  is written before the merge and does not claim it; the next checkpoint's
  documents (B9) record the merge commit. The instruction decides none of the
  points §19 leaves for the owner. No deployment, activation, approval or
  normal-app command follows from the merge.
- 2026-10-06, 12:32 UTC, B8 implemented, reviewed and accepted in
  isolation: IMPLEMENTED on `claude/m6-b8-owner-pages` the owner pages of
  §5.9 (`/evidence`, `/research` with its views, one candidate, one
  experiment with one result cell at a time, the "Research and sources"
  section of Approvals, the four templates of the start dialog, the grouped
  profile diff, the workflow page's marks and the two System rows), the
  same-origin server functions behind them, a browser fixture with real
  replays, and the harness phases `BrowserResearch` and
  `BrowserResearchError` with the web build in `Checks`. The API gained
  additive consequence lists only; migration 0008, every route, body and grant
  are unchanged. Six points were decided by the owner before any code, and the
  two B7 behaviors §19 had left open were decided and recorded
  ([DECISIONS](../../DECISIONS.md#2026-10-06--two-b7-behaviors-kept-an-owner-cancel-lets-the-workflow-go-on-a-recorded-shadow-stop-takes-no-further-mark)).
  OBSERVED on run `m6-b8c`: all seventeen phases passed. Two independent
  read-only reviews of that source found no injection path, no secret in what
  reaches the browser and no mark on something the API did not mark, and rated
  no product finding high. One test finding was high: the error browser test
  never reached an M6 page. What they found was fixed with tests; among it,
  the first revoke lists understated what a revocation does, and a stale read
  still offered its actions. VERIFIED on fresh run `m6-b8d`, one image,
  without a skip: Build, `Generate` (no difference, on source equal to the
  Build record), `ApiAuth` (5, 5 and 24), `Staging` (13), `ShadowSchedule`
  (11), `ResearchRunner` (15 and 17), `DispatcherAuth6` (11 and 14),
  `AgentFaults6` (11 and 17), `SourcePolicy` (249), `HoldoutIsolation` (9),
  `EvidenceInjection` (24 and 2), `BrowserResearch` (61 sample and page
  tests on this run's API responses, then 7 browser tests at 390 and 1440 px),
  `BrowserResearchError` (1 and 1), `AgentOffline6` (M5: 14 and 84; new: 16
  and 90, and the schema probe), `Regression` (169) and `Checks` (407 engine
  tests; the web checks with 155 unit tests and the build). NOT RUN:
  `Migration` and `EngineParity` (their inputs are unchanged),
  `PerformanceBrowser` and the other B9 phases, a screen reader, a browser
  other than Chromium, the M5 browser phases, any model call, any public
  source, GitHub CI, deployment and activation. Every test used a synthetic
  owner, fixtures, a scripted model on the recorded provider and the loopback
  mock source; nothing was approved outside disposable fixture databases and
  no command addressed the normal app. Evidence is in §18; the commands are in
  [COMMANDS](../COMMANDS.md#m6-b8-owner-pages-and-same-origin-functions-2026-10-06).
  B8 completes neither M6-A nor any deployment; B9 is NOT RUN. Delivered as
  commit `fe85cec` in pull request #29, created at 12:38:13 UTC, open and not
  merged; the owner decides. Points left for the owner are in §19.
- 2026-10-06, 06:12:45 UTC, B7 PR merged (recorded by this checkpoint, as the
  entry below left it): VERIFIED read-only at the start of B8 that pull
  request #28 is MERGED as `2043fc0a9ab777e36b250acd5dd311f1deb994af`, an
  ordinary merge commit of head `c4dcec3` into `main` at `d1f8d88`, that
  `main` and `origin/main` are at that commit with a clean tree, and that no
  pull request was open. B8 was branched from it.
- 2026-10-06, 06:09 UTC, B7 PR, merge requested: OBSERVED owner instruction
  `merge it` for pull request #28
  ([decision](../../DECISIONS.md#2026-10-06--owner-asks-to-merge-the-m6-b7-pr)).
  VERIFIED read-only that `main` is still at `d1f8d88`, the commit B7 was
  branched from and accepted on, and that PR #28 is open, mergeable and clean
  at head `79acde3`. Nothing has to be merged into the branch and no phase has
  to be rerun. The PR is merged with an ordinary merge commit pinned to the
  verified head, without force, an admin bypass or branch deletion. This entry
  is written before the merge and does not claim it; the next checkpoint's
  documents (B8) record the merge commit. The instruction decides none of the
  points §19 leaves for the owner. No deployment, activation, approval or
  normal-app command follows from the merge.
- 2026-10-05, 23:10 UTC, B7 implemented, reviewed and accepted in
  isolation: IMPLEMENTED on `claude/m6-b7-owner-api` the owner API of §5.9
  with its read models, the approval, rejection and revocation of the envelope
  and of a source version, the rejection of a promotion that SYSTEM applies,
  the owner starts of the three M6 templates, the two `SystemStatus` fields,
  the regenerated OpenAPI document and web types, and the harness phases
  `Generate` and `ApiAuth`; migration 0008 is unchanged. OBSERVED on run
  `m6-b7b`: all sixteen phases passed. Two independent read-only reviews of
  that source found no path by which holdout or shadow data reaches a tuning
  role and rated nothing high; what they found was fixed with tests, and five
  low-rated points are recorded in §19. One of the fixes changes what the
  owner decided nothing about and is therefore put to the owner: an owner's
  cancel of a screening is recorded as `OWNER_CANCEL` and the workflow that
  asked for it goes on, where before it ended as revoked. A first acceptance
  attempt on fresh run `m6-b7d` failed in `AgentOffline6`: one M5 test ran
  twenty probes on a single ten-second lease it never renewed and took about
  that long; the test helpers now keep the lease as the worker does, and no
  product file changed. VERIFIED on fresh run `m6-b7e`, one image, without a
  skip: Build, `Generate` (no difference, on source equal to the Build
  record), `Checks` (407 engine tests and the five web checks),
  `AgentOffline6` (M5: 14 and 84; new: 16 and 90, and the schema probe),
  `ApiAuth` (5, 5 and 21), `Staging` (13), `ShadowSchedule` (11),
  `ResearchRunner` (15 and 17), `Regression` (169), `SourcePolicy` (249),
  `EvidenceInjection` (24 and 2), `HoldoutIsolation` (9), `DispatcherAuth6`
  (11 and 14) and `AgentFaults6` (11 and 17). NOT RUN: `Migration`
  and `EngineParity` (their inputs are unchanged), the BFF functions, pages
  and any browser (B8), `PerformanceApi`, `SecretScan` and `MixedVersion`
  (B9), any model call, any public source, GitHub CI, deployment and
  activation. Every test used a synthetic owner, fixtures, a scripted model
  on the recorded provider and the loopback mock source; nothing was approved
  outside disposable fixture databases and no command addressed the normal
  app. Runs `m6-b7a` to `m6-b7e` were cleaned by exact
  name. Evidence is in §18; the commands are in
  [COMMANDS](../COMMANDS.md#m6-b7-owner-api-openapi-and-generated-types-2026-10-05).
  B7 completes neither M6-A nor any deployment; B8–B9 are NOT RUN. Delivered
  as commit `cf89f86` in pull request #28, created at 23:18:56 UTC, open and
  not merged; the owner decides.
- 2026-10-05, B7 handed over: OBSERVED owner instruction in a Claude Code
  session: implement B7 only (the owner API for M6, its OpenAPI document and
  the generated web types, verified by `ApiAuth` and the contract and drift
  checks), on a new branch from `main`, in isolated Docker stacks, delivered as
  a pull request that is not merged until the owner says so. VERIFIED
  read-only first: pull request #27 (the generation-1 trimming fix) is MERGED
  as `d1f8d88c2672404ba081e76017ee82100ef5256c` (parents `7f0268a` and
  `2671935`) at 14:06:19 UTC on 2026-10-05, `main` and `origin/main` are at
  that commit, the tree was clean and no pull request was open; this is the
  merge the entry below was written before and did not claim. Branch
  `claude/m6-b7-owner-api` was created from it in the primary checkout. Before
  any file was edited, three points were put to the owner with
  recommendations, and the owner took every one
  ([DECISIONS](../../DECISIONS.md#2026-10-05--m6-b7-experiment-read-codes-canceled-jobs-and-rejected-promotions)):
  `read_experiment` keeps its two codes; a job canceled before it ran stays
  final for its input; an owner's rejection of a promotion is applied by
  SYSTEM to the promotion and its candidate. Official pages were read for the
  discriminated request body and the lock timeouts
  ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m6-b7-owner-api-request-bodies-and-lock-waits--2026-10-05)).
- 2026-10-05, 14:05 UTC, generation-1 trimming PR, merge requested: OBSERVED
  owner instruction `merge it` for pull request #27
  ([decision](../../DECISIONS.md#2026-10-05--owner-asks-to-merge-the-generation-1-trimming-pr)).
  VERIFIED read-only that `main` is still at `7f0268a`, the commit the change
  was verified on, and that PR #27 is open, mergeable and clean at head
  `8c0c7f0`. Nothing has to be merged into the branch and no phase has to be
  rerun. The PR is merged with an ordinary merge commit pinned to the verified
  head, without force, an admin bypass or branch deletion. This entry is
  written before the merge and does not claim it; the next checkpoint's
  documents record the merge commit. No deployment, activation, approval or
  normal-app command follows from the merge.
- 2026-10-05, 13:25 UTC, generation-1 prompt trimming corrected (not a batch
  of this plan; it closes one §19 entry): VERIFIED read-only that pull request
  #26 (B6) is MERGED as `7f0268a1c128ff83087e4fbb8bfc7ba339982f2f` at
  11:51:35 UTC and that `main` is at that commit. OBSERVED owner decision to
  fix the order in which a generation-1 prompt hides results
  ([decision](../../DECISIONS.md#2026-10-05--generation-1-prompt-trimming-drops-the-oldest-result-first)).
  IMPLEMENTED on `claude/g1-prompt-trim-order` from that commit: the
  generation switch in `prompting.compose` is removed, so both generations hide
  the oldest result first, with one new pure test. VERIFIED on fresh isolated
  run `g1-trim-b`, one image, no skip: Build, `AgentOffline6` (M5: 14 and 84;
  new: 16 and 72, and the schema probe), `DispatcherAuth6` (11 and 14),
  `AgentFaults6` (11 and 17), `Checks` (389) and `EvidenceInjection` (24 and
  2). The new test fails with the old expression restored. The other phases
  were NOT RUN: none of their tests composes a prompt, and no schema, seed,
  definition or engine file changed. No definition or profile hash changes.
  Nothing was deployed; no model call, public endpoint or normal-app command.
  See [COMMANDS](../COMMANDS.md#generation-1-prompt-trimming-order-2026-10-05)
  and [ExecPlan 0020 §17](0020-m5-agent-runtime.md#correction-after-closure--which-results-an-oversized-prompt-hides-2026-10-05).
  B7–B9 remain NOT RUN.
- 2026-10-05, 11:49 UTC, B6 merge requested: OBSERVED owner instruction
  `merge it` for pull request #26
  ([decision](../../DECISIONS.md#2026-10-05--owner-asks-to-merge-the-m6-b6-pr)).
  VERIFIED read-only that `main` is still at `5da6b90`, the commit B6 was
  accepted on, and that PR #26 is open and mergeable at head `6be9ed1`. Nothing
  has to be merged into the branch and no phase has to be rerun: the
  acceptance on `m6-b6c` stands for the merged source. The PR is merged with an
  ordinary merge commit pinned to the verified head, without force, an admin
  bypass or branch deletion. This entry is written before the merge and does
  not claim it; the next checkpoint's documents record the merge commit. The
  points the pull request left for the owner stay open (§19). No deployment,
  activation, approval or normal-app command follows from the merge.
- 2026-10-05, 11:44 UTC, B6 delivered: OBSERVED `main` still at `5da6b90`.
  Commit `a65aafe` (66 files) was pushed without force to
  `claude/m6-b6-agent-workflows` and pull request
  [MentorAliu/adaptive_spot_lab#26](https://github.com/MentorAliu/adaptive_spot_lab/pull/26)
  was opened against `main`: open, mergeable, no check run because GitHub CI
  does not start. It is not merged; the owner decides. This entry is a
  documentation-only commit made after the pull request existed.
- 2026-10-05, 11:38 UTC, B6 accepted on the reviewed source: VERIFIED on
  fresh run `m6-b6c` (image `4b49f667…f610ae5b`), no skip: Build, Migration,
  Checks (388), Regression (169), AgentOffline6
  (14 and 84 M5 tests, 16 and 71 new), DispatcherAuth6 (11 and 14), AgentFaults6 (11 and 17),
  EvidenceInjection (24 and 2), SourcePolicy (249), Staging
  (13), ShadowSchedule (10), ResearchRunner (15 and 17) and
  HoldoutIsolation (9). `EngineParity` NOT RUN: the shared engine
  and replay code is unchanged. Contracts, COMMANDS, STATUS and §18 are
  updated; the documentation link check passed; runs `m6-b6a`, `m6-b6b` and
  `m6-b6c` were cleaned by exact name with their evidence files kept.
  Delivery follows this entry: the branch is pushed without force and a pull
  request to `main` is opened; it is not merged until the owner says so. B7 is next
  and NOT RUN. No normal-app command, approval, activation, login or model
  call was made.
- 2026-10-05, 09:27 to 10:45 UTC, independent review of B6: three read-only
  reviewers read the source of `m6-b6b` while that run was in progress (it
  passed every phase at 10:19 UTC). They reported 29 findings, 26 distinct:
  3 high, 9 medium, 14 low. Each was confirmed in the code. IMPLEMENTED 24
  fixes with tests that fail on the `m6-b6b` code (§18 lists them); two
  findings are left as the contract states them and recorded in §19. The high
  ones: a profile approved before definitions v2 still authorized probes,
  Enable and generation-2 work; artifacts built on the holdout or a shadow
  were marked unrestricted when their author had read nothing; a string
  PostgreSQL cannot store held the single inference slot until a deadline.
  `m6-b6b` is history.
- 2026-10-05, 09:26 to 10:19 UTC, first full pass: VERIFIED on fresh run
  `m6-b6b` (image `f8203f38…422f6629`), every phase, no skip: Build, Migration
  (19 schema tests), Regression (169 in 942.29 s), Checks (378),
  AgentOffline6 (14 and 84 M5 tests, 11 and 61 new, the schema probe),
  DispatcherAuth6 (11 and 12), AgentFaults6 (11 and 11), EvidenceInjection (24
  and 2), SourcePolicy (249), Staging (13), ShadowSchedule (10),
  ResearchRunner (15 and 17), HoldoutIsolation (9). The agent phases reserve
  up to 30 minutes, so those after Checks waited for the 10:07 window.
- 2026-10-05, 08:28 to 09:26 UTC, B6 authoring on run `m6-b6a` (history, not
  acceptance): the first Build FAILED its static step as expected, before the
  nine definition rows were frozen into migration 0008. Development checks
  then found three product defects (the approved-profile lookup took approvals
  of any kind; a completion body without a result; the M5 agent read models
  refused schema 0008) and several fixture and expectation errors in the new
  tests. Three authoring passes of the phases followed. Staging FAILED once on
  two test-side causes (a B4 assertion that lists the journal's row kinds
  exactly; a wrong column in a new test) and Migration once on its helper's
  expected seed set, which still knew only the M5 and research rows. A third
  Migration attempt stopped at the already seeded recovery fixture, which is a
  property of that phase and not a result. No product code changed during
  the three passes.
- 2026-10-05, B6 handed over: OBSERVED owner instruction in a Claude Code
  session: implement B6 only, on a new branch from `main`, verified in
  isolated Compose projects, delivered as a pull request that is not merged
  until the owner says so. VERIFIED read-only that PR #25 (B4) is MERGED as
  `5da6b90a3761abb6262dc040308cf7e9c4fb1d20` at 22:30:14 UTC on 2026-10-04 and
  that `main` is at that commit; this is the merge the entry below was written
  before and did not claim. Branch `claude/m6-b6-agent-workflows` was created
  from it in the primary checkout, which no other session was using. Four
  points the plan left open were put to the owner with recommendations, and
  the owner took every one
  ([DECISIONS](../../DECISIONS.md#2026-10-05--m6-b6-definition-generations-schedule-and-ended-shadows)):
  the M5 templates keep definitions v1; scheduled research is one per newly
  sealed dataset; a candidate whose shadow ended without the evidence minimum
  is retired; M5 tests that assert an M5-only database are updated in place.
  Official pages were read for the schema limits and three PostgreSQL 17
  behaviors ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m6-b6-agentstep-schema-v2-and-queries--2026-10-05)).
- 2026-10-04, 22:30 UTC, B4 merge requested and merged source accepted:
  OBSERVED owner instruction `merge it` for pull request #25 at 21:30 UTC
  ([decision](../../DECISIONS.md#2026-10-04--owner-asks-to-merge-the-m6-b4-pr)).
  VERIFIED read-only that PR #24 (B5) is MERGED as
  `52eab973d0de9365c8a820040aafeb53624b1ffa` (parents `6e8fbb6` and `c77e59d`)
  at 21:23:36 UTC and that PR #25 conflicted with it. `main` was merged into
  the B4 branch (local merge `35f25d9`): the harness script keeps both
  batches' phases and four documents keep both sessions' entries. On fresh run
  `m6-b4c` the first attempt FAILED one B3 test in `ResearchRunner` (14 passed,
  1 failed): it expected `asl_source` to be refused
  `research_hold_permission_epoch()`, which B5 granted on purpose and whose
  acceptance did not rerun that phase. Test-only correction to the merged
  contract. VERIFIED then on the rebuilt image `3327dd1e…75833e`, without a
  skip: Build, `Staging`, `ShadowSchedule`, `ResearchRunner`,
  `HoldoutIsolation`, `SourcePolicy`, `EvidenceInjection`, `Checks`,
  `Migration` and `Regression` (§18). `EngineParity` NOT RUN: the shared
  engine and replay code is unchanged by both batches. `Clean` removed the
  run's resources by exact name and the link check passed. The merge of PR #25
  follows with an ordinary merge commit pinned to the verified head; this entry
  is written before it and does not claim it. B6 onward remains open.

- 2026-10-04, 21:22 UTC, B5 merge requested: OBSERVED owner instruction
  `merge it` for pull request #24
  ([decision](../../DECISIONS.md#2026-10-04--owner-asks-to-merge-the-m6-b5-pr)).
  `main` was still at `6e8fbb6` and the B4 pull request (#25) open, so B5
  merges first with an ordinary merge commit pinned to its verified head. This
  entry is written before the merge and does not claim it. B4 must merge
  `main` and rerun every phase whose inputs changed; B6 onward remains open.

- 2026-10-04, 15:51 UTC: VERIFIED B4 delivery. The 34 B4 files were committed
  by an explicit list as `3e3c477` on `claude/m6-b4-bridge-staging-shadows`
  and pushed without force; the remote branch hash matches.
  [PR #25](https://github.com/MentorAliu/adaptive_spot_lab/pull/25) against
  `main` is OPEN and MERGEABLE at that head. The merge is NOT RUN: the owner
  asked for the PR only. GitHub CI did not run (both runs ended in
  `startup_failure`), so the local acceptance in §18 is the only automated
  evidence. Nothing was deployed or activated; M6-A stays incomplete.

- 2026-10-04, 15:50 UTC: VERIFIED B4 cleanup and closing checks. `Clean`
  removed seven exact-name resources from each of `m6-b4a` (15:45:53 UTC) and
  `m6-b4b` (15:46:05 UTC): two fixture containers, two networks, two volumes
  and the run's image. All eight project inventories of each run are empty, and
  all ten recorded build image IDs (eight authoring, two on `m6-b4b`) are
  absent by exact ID. No prune ran; evidence, failed attempts included, stays
  under `.cache/m6/`. `source-003.json` (15:45 UTC) differs from the
  Build-bound `source-002.json` only in two documentation files. Protected
  paths are unchanged against `6e8fbb6`, the Compose change is 39 added lines
  and none removed, the three harness scripts parse under PowerShell 5.1 and
  are ASCII, and `git diff --check` is clean. B4 is complete within its batch
  scope (§18). Delivery is a PR from `claude/m6-b4-bridge-staging-shadows` to
  `main`, not merged. OBSERVED read-only at 15:45 UTC: `main` is still
  `6e8fbb6`, and PR #24 (B5, another session) is open against it; both change
  the harness scripts and the same contracts, so whichever merges second has
  to merge `main` and rerun the phases it touches.

- 2026-10-04, 15:41 UTC: OBSERVED an independent read-only review of the
  uncommitted B4 code (14:42–15:05 UTC; it ran nothing) with ten findings.
  IMPLEMENTED nine corrections, listed in
  [COMMANDS](../COMMANDS.md#m6-b4-authoring-iterations-2026-10-04); the tenth,
  and one B3 behavior the review surfaced, are open risks in §19. `m6-b4a`
  could no longer run the bridge probe: its fixture, prepared before the
  review, still mounted the volume the bridge no longer has. Fresh run
  `m6-b4b` was prepared from the final harness. Its first `Staging` FAILED on
  one new test's own assumption (11 passed, 1 failed, image `8fe62932…1c57d9`);
  the test was corrected and the image rebuilt. VERIFIED on final image
  `ffe756c4…308da0d` between 15:20 and 15:40 UTC, without a skip: Build with
  four static tests and Ruff; `Staging` (Compose review, bridge probe,
  default-disabled start, 12 tests); `ShadowSchedule` (10 tests);
  `ResearchRunner` (15 catalog tests, runtime probe, 17 runner tests);
  `Regression` (169 tests); `Checks` (145 tests); `HoldoutIsolation` (9
  tests). `Migration` and `EngineParity` NOT RUN: migration 0008 and the shared
  engine and replay code are unchanged. Actual commands and results are in
  [COMMANDS](../COMMANDS.md#m6-b4-final-source-acceptance-2026-10-04).

- 2026-10-04, 14:41 UTC: OBSERVED the first B4 authoring iterations in fresh
  run `m6-b4a`, each on a rebuilt image; none is acceptance evidence. The first
  Build FAILED Ruff on two import blocks (formatting only). `Staging` then
  FAILED three times before its product tests finished: twice in the new
  runtime probe (a privilege query that named a table before its schema was
  filtered; a `CREATE DATABASE` refusal tested inside a transaction) and once on
  one assertion (a collection row was sent again with every batch: harmless,
  since the insert was a no-op, but it spent the batch's row bound; IMPLEMENTED
  skipping rows already staged). One run then ended with a test-reset deadlock
  on the fixture store, not a product failure; the reset was split into two
  transactions. The first `ShadowSchedule` run passed all seven tests and
  errored on a helper that pytest collected by its name. VERIFIED afterwards on
  intermediate images: `Staging` (probe, default-disabled start, 11 tests) and
  `ShadowSchedule` (7 tests), without skips. IMPLEMENTED review refinements
  (bridge schedule cadence and log volume, one engine pair per store in the
  runner, evidence files from the tests) and VERIFIED both phases again. An
  independent read-only code review and the final-source gates follow.

- 2026-10-04, 14:26 UTC, B5 delivered for review: commit `3a44777` pushed
  without force to `claude/m6-b5-source-registry`; pull request
  [MentorAliu/adaptive_spot_lab#24](https://github.com/MentorAliu/adaptive_spot_lab/pull/24)
  OBSERVED open and mergeable against `main` at `6e8fbb6`. Not merged; no
  check ran. B4 and B6 onward remain open.

- 2026-10-04, 14:25 UTC, B5 Regression and cleanup: VERIFIED on run `m6-b5b`, the same
  image: 169 M3 and M4 tests passed in 885.55 s between 14:07:05 and 14:22:03,
  one existing warning, no skipped test. With it every phase B5 owes has passed
  on the reviewed source. VERIFIED afterwards: the 437 non-documentation files
  still have the hashes recorded at that Build; Clean of `m6-b5b` at 14:23:05
  removed thirteen exact-name resources and its build image ID is absent; the
  documentation link check found no broken link in 86 files. `origin/main` was
  still at `6e8fbb6` and no pull request was open, so nothing was merged into
  the branch. The B4 session's `asl-m6-m6-b4a-*` resources were left alone.

- 2026-10-04, 13:35 UTC, B5 after the review: VERIFIED on fresh run `m6-b5b`,
  image `5cfcf2c9…5b9ec51f`: Build at 13:29:39, SourcePolicy at 13:30:49 (249
  tests, the Compose-block review and the runtime probe), EvidenceInjection at
  13:31:30 (24 tests), Checks at 13:31:49 (317 tests) and Migration at 13:34:08
  (19 schema tests and the populated migration), no skipped test. Regression
  needs a 25-minute reservation and is queued for the HH:07 window. VERIFIED
  Clean of `m6-b5a` at 13:34:47: thirteen exact-name resources removed, its
  three build image IDs absent, evidence kept.

- 2026-10-04, 13:27 UTC, B5 review: run `m6-b5a` passed every phase on image
  `a2e5d56e…62f93b5` between 13:07 and 13:26 UTC (230 SourcePolicy, 23
  EvidenceInjection, 302 Checks, 169 Regression tests in 862.41 s, Migration
  with 19 schema tests). An independent read-only review of the new modules
  then reported eight defects, listed in §18. Each was confirmed in the code.
  IMPLEMENTED the fixes with a test each; they change product code and add one
  lock call to the approval guard of migration 0008, so every phase is rerun on
  a fresh run and `m6-b5a` is kept as history (`pre-review-*.json`).

- 2026-10-04, 13:05 UTC: the trigger rule changed before any acceptance phase
  ran. As first written, items stored inside a cooldown never got a trigger.
  IMPLEMENTED the deferral instead: the first successful fetch after the
  cooldown creates the trigger that carries them. The SourcePolicy phase queued
  at 12:52 for the HH:07 window was canceled before any Docker call, because
  its image predated the change.

- 2026-10-04, 12:52 UTC, B5 first build and development checks: VERIFIED `m6-b5a`
  Build at 12:50:49 UTC (image build, four static/registry checks, Ruff). A
  development check of the new unit tests in a one-off container without a
  network then FAILED at collection: a dataclass field named `bytes` shadowed
  the built-in type in the next annotation. IMPLEMENTED the rename to `size`;
  Build passed again at 12:51:44 UTC. Development checks on that image, not
  acceptance evidence: 157 unit tests passed in 3.19 s, and 53 transport tests
  against the loopback TLS mock passed in 10.97 s (the one selected
  database-backed case could not run there). SourcePolicy is queued for the
  HH:07 window.

- 2026-10-04, B5 in progress (a second session, beside B4): OBSERVED owner
  instruction to implement B5 only, with the tools and the trigger scheduler
  left to B6 ([decision](../../DECISIONS.md#2026-10-04--owner-assigns-m6-b5-to-a-second-session-with-the-b5b6-split-of-evidenceinjection)).
  OBSERVED `origin/main` at the PR #23 merge `6e8fbb6`, no open pull request,
  and no `asl-m6-*` project running. Work is on `claude/m6-b5-source-registry`
  in its own worktree. IMPLEMENTED in `app/sources/`: the registry, typed
  requests, the transport, the release parser and plain-text extract, refresh
  requests, immutable fetch and evidence records, `SOURCE_REVISION` triggers,
  search and the fetcher, with the `source-fetcher` Compose block and the
  `SourcePolicy` and `EvidenceInjection` harness phases. Two changes to
  migration 0008, which is not applied to the normal app:
  - the two seeded source versions now carry the fields §5.7 names and B1 had
    not seeded (answer limits, extract bound, symbol scope, budget, poll and
    refresh intervals, back-offs, trigger cooldown, rate-limit policy, review
    date, `redirects`, a `page` maximum). Their hashes change:
    `RELEASES_BITCOIN_V1` `2fab5ce7…1c1e1ba9` to `40a8ee69…995e7770`,
    `RELEASES_AGAVE_V1` `41f29e4c…377e2b48` to `f6b322e5…fb07e750`. No approval
    of either hash exists anywhere;
  - `asl_source` may execute the fixed read `research_hold_permission_epoch()`.

  No table, constraint or M1–M4 object changed, and no dependency was added.
  Product gates are NOT RUN at this entry. No normal-app command, public
  endpoint or model call is part of B5.

- 2026-10-04, 12:20 UTC: OBSERVED the owner's answers to four points the plan
  left open, each as recommended: early store rotation, the candidate and the
  reference under H1 in each shadow advance, one sealed dataset per UTC day, and
  a separate budget for shadow advances
  ([DECISIONS](../../DECISIONS.md#2026-10-04--m6-b4-handed-over-and-four-points-the-plan-left-open-execplan-0023)).
  IMPLEMENTED draft bridge, staging, stores, datasets and shadows modules, the
  shadow and multi-store paths of the runner, the inert `research-bridge`
  Compose block, and the `Staging` and `ShadowSchedule` harness phases on two
  fixture clusters. Migration 0008, the shared engine and replay code, the
  envelope and every existing Compose block are unchanged. Product gates NOT
  RUN at this entry.

- 2026-10-04, 12:05 UTC: VERIFIED read-only that PR #23 is MERGED as merge
  commit `6e8fbb60fa2b7fc18576a3d67b273c9d8d5968b6` (parents `bdeac4f` and
  `56d8031`), merged at 11:55:03 UTC; local and remote `main` are at it. B0–B3
  are on `main`. OBSERVED owner instruction for B4 only (bridge, staging,
  versioned stores, sealed datasets, job/result relay, deferred-replay shadows;
  R14, R20 and the bridge part of R16). Created
  `claude/m6-b4-bridge-staging-shadows` from that commit. B5 onward, deployment
  and activation stay outside it; no normal-app command is authorized.


- 2026-10-04, 11:53 UTC: OBSERVED owner instruction in the same Claude Code
  session: `merge it`. PR #23 is merged with an ordinary merge commit pinned to
  its verified head, without force, an admin bypass or branch deletion. Written
  before the merge; GitHub records the actual result. B4 onward, M6-A
  acceptance, normal operations and activation remain outside it.

- 2026-10-04, 11:47 UTC: the Codex session reached its usage limit before the
  commit step of the entry below. OBSERVED owner instruction in a Claude Code
  session: `create a pr on this branch`. VERIFIED there: the authorization
  record committed as `4cd4979`, the branch pushed without force, and
  [PR #23](https://github.com/MentorAliu/adaptive_spot_lab/pull/23) OPEN and
  MERGEABLE against `main`. NOT RUN: the merge (that instruction asks for the PR
  only) and the publication helper, so its receipts do not exist. GitHub CI did
  not start (`startup_failure`, as in every earlier run). Actual commands are in
  [COMMANDS](../COMMANDS.md#m6-b3-checkpoint-pr-and-merge-2026-10-04).

- 2026-10-04 Europe/Budapest: OBSERVED owner instruction `create pr and merge it`
  after completed local B3 commit `85104b7`. VERIFIED clean branch/worktree,
  remote main `bdeac4f` and no existing B3 branch/PR on the remote. Publication
  of this checkpoint is authorized by the new
  [owner decision](../../DECISIONS.md#2026-10-04--owner-requests-a-b3-checkpoint-pr-and-merge).
  The native receipt under `.cache/m6/m6-b3b/publication/` and GitHub history
  record the actual result; B4 onward, M6-A acceptance, normal operations and
  activation remain outside this publication.

- 2026-10-04, 11:38 UTC: VERIFIED completion-documentation Docker check,
  86 Markdown files, zero broken links and four historical Windows-link warnings.
  B3 acceptance, review and cleanup are complete within the approved scope.
  Local delivery uses the 26-file allowlist and native receipt/journal under
  `.cache/m6/m6-b3b/`; B4 onward, full M6-A and publication remain NOT RUN.
  No further B3 owner decision is required.

- 2026-10-04, 11:36 UTC: VERIFIED all final-source B3 runtime gates: 15 catalog,
  17 runner, 9 holdout, 145 Checks, 169 M3/M4 Regression tests and all three
  EngineParity scenarios, without skips. Fresh `m6-b3c` passed 19 schema tests
  and populated Migration using the same 421 non-doc source files and identical
  image filesystem/runtime config except Compose labels. Clean removed its ten
  resources, then thirteen from `m6-b3b`; `m6-b3a` had already removed four.
  All seven recorded B3 build image IDs are absent; evidence remains. Source
  review passes, with documentation validation and local commit in progress.

- 2026-10-04, 11:10 UTC: VERIFIED final image
  `2585ef231eee7cfbe148bd406f9d8e27308d116307d9769fd070e91122c8bf28`
  Build/static/Ruff, runtime bootstrap/isolation, 15 catalog tests (16.36 s)
  and 17 runner tests (63.31 s), including the prior-image/current-image refusal
  before reset/replay. Code identity is
  `69b27b1c298e1f54ae95ca340db0998ef6624092f69f72e884c71a2c7d801057`.
  All 421 non-doc source files match the build; protected source and prior
  Compose blocks remain unchanged. The full M3/M4 Regression has started in
  the permitted window. Remaining gates and local delivery are in progress.

- 2026-10-04, 11:03 UTC: source review found that durable work could survive an
  image replacement without a fresh execution-time code-identity check.
  IMPLEMENTED refusal before reset/replay and a prior-image/current-image
  regression case. The waiting Regression was canceled before Docker started.
  Every passing intermediate-image phase and result was archived under
  `pre-execution-code-*`. All final-source gates will rerun after the unchanged
  quiet-period guard; no scope, envelope or authority changed.

- 2026-10-04, 10:43 UTC: VERIFIED populated Migration (19 schema tests; restore,
  old-image continuity and accounting/M3/M4 invariants), all three EngineParity
  scenarios and native baseline preservation, and 145 Checks without skips on
  the corrected source. The final M3/M4 Regression is queued behind the unchanged
  25-minute reservation for 11:07 UTC. Completion documents, cleanup and local
  delivery remain pending; no later batch or normal operation runs.

- 2026-10-04, 10:37 UTC: VERIFIED corrected-source `m6-b3b` Build/static/Ruff,
  15 catalog and 16 runner tests, 9 holdout tests, runtime isolation/bootstrap
  and the three new Compose blocks rendered only with fixture substitutions.
  Review found a UTC-day budget defect; IMPLEMENTED explicit UTC conversion
  and a non-UTC session regression test. The obsolete-image M3/M4 run was
  deliberately stopped (exit 137, not an assertion failure or timeout), with
  its failed phase record and all logs retained as `pre-utc-*`. Final image
  `95b0b8d11156a05b55db06fb7743ff8b964f1fe0bf3c7de673b27479c5bb818b`
  is now under broader verification. Authoring review matches all 421 non-doc
  source files to that build and proves existing Compose blocks/protected
  source unchanged; PS5.1/ASCII and whitespace checks pass. No completion claim.

- 2026-10-04, 10:17 UTC: OBSERVED owner instruction `Don't stop until b3 is
  completed`, authorizing the proposed grant-order correction and continued
  in-scope correction/verification through local delivery. IMPLEMENTED the
  grant after role creation. The prior gate failure and cleanup remain recorded
  in `m6-b3a`; a fresh `m6-b3b` run will verify the corrected source. Envelope,
  protected service/schema, activation and no-publication boundaries remain.

- 2026-10-04, 10:15 UTC: VERIFIED exact-name cleanup of `m6-b3a`, four resources
  removed, all manifest projects empty, final and replaced authoring images
  absent. Evidence remains in `Clean.json`, `Clean-historical-image.json`, the
  hashed inventory and native journal. The proposed migration-order correction
  still awaits owner approval. Product code has not changed since the failed
  gate; no rerun or local commit was made.

- 2026-10-04, 10:09 UTC: VERIFIED B3 engine image Build, four selected static
  tests (1.81 s; 75 deselected) and Ruff. FAILED ResearchRunner during catalog
  migration before product tests: `asl_research` does not yet exist when the
  new epoch-lock function grant runs. Read-only diagnosis locates role creation
  later in the same migration. PROPOSED moving that grant after role creation;
  implementation and all reruns paused for owner approval under the explicit
  failed-gate rule. Both fixture targets stopped. `m6-b3a` retains every command,
  source/image identity and failure output; cleanup is pending its stricter UTC
  window. No local commit, normal operation, activation or publication ran.

- 2026-10-04, B3 in progress: OBSERVED clean main and origin/main at the B1/B2
  merge `bdeac4f91c13e25ca190320a6def53dcd43c0817`; created the requested
  `codex/m6-b3-research-runner`. IMPLEMENTED draft catalog reservations/trials,
  research-only runtime schema/leases/outbox, existing-engine replay with batch
  fencing and scoped reads, result identity/reuse and holdout projections. The
  additive M6 epoch-lock function avoids granting the bridge epoch mutation.
  Fresh fixture run `m6-b3a` is prepared; product gates and local delivery are
  NOT RUN. Frozen definitions/envelope, protected schema/services and all four
  refused tools are unchanged. B4 transport/staging, B5 sources and B6 tools are
  outside this batch; no normal operation is authorized.

- 2026-10-03: first draft, from the code at `72ba76f` and the contracts. Nothing implemented.
- 2026-10-03: an independent read-only review of the first draft. Each finding was checked in the code and taken into this draft:
  - bar-path research cannot fill an order on the unchanged engine and was neither cheap nor conservative (now §5.12 and M6-OD2);
  - the engine is bound to the reference strategy in six more places than the first draft listed, and literal fingerprint parity is impossible (§2, §5.3, R07);
  - the shadow is a relabeled replay with three undisclosed advantages, and its rows did not survive a reset (now M6-OD6, §5.6);
  - the holdout lock covered results but not market reads, shadow results or search (now an information cutoff, §5.5, R11);
  - the research worker would have held the engine's credentials on the pilot's network (now two processes and research-only secrets, §5.1, R16);
  - the completion rule left two gate clauses to isolated evidence without saying so (now M6-OD7, §13.3);
  - waiting collided with the M5 deadline, the single tool result and the shared child budget (§5.8);
  - staging omitted two tables, and a rolling store cannot delete (now versioned stores, §5.4, R20);
  - smaller points: the sample minimum against the dataset length, the shadow's cost at its limit, memory, the wording of R14, two permission mismatches, path-scoped fetch rules, what the envelope hash binds, the downgrade, a template name, the missing failure table and the unnamed flags.
- 2026-10-03: the owner approved the plan for implementation and took the recommendation of each of the seven decisions (§3.3). Nothing implemented.
- 2026-10-03: the owner's standing cleanup rule was added to §10: the harness gets a `Clean` phase ([DECISIONS](../../DECISIONS.md#2026-10-03--docker-test-resources-are-removed-after-each-implementation)).

- 2026-10-03, B0 in progress: IMPLEMENTED the named contract amendments for role permissions, queued completions, holdout projections, reject-only promotions, separate research compute, quote-only staging and deferred replay labels. IMPLEMENTED `tools/m6-acceptance.ps1` with the exact §10 phase inventory, guarded isolated layouts, source snapshots and explicit failure for unimplemented phases. No application, migration, dependency or normal Compose change.
- 2026-10-03: OBSERVED the checkout initially lacked this plan on `main` (`ed9fae3`). The approved local `claude/m6-research-plan` branch at `b4438b9` contains it. Created `codex/m6-research-investigations` from that approved branch; the §2 engine/runtime source paths have no diff from the plan baseline. Current file facts are re-read before use.
- 2026-10-03: the owner approved only the bounded normal-app observer and process-only PowerShell 5.1 `-ExecutionPolicy Bypass` for reviewed M6 scripts ([decision](../../DECISIONS.md#2026-10-03--m6-b0-bounded-read-only-measurements-and-process-only-script-execution)). B10 still needs chat approval; B11 stays with the owner. The narrow heavy-phase window is not cleared.
- 2026-10-03: VERIFIED B0 schema preview through the pinned CLI and credential-free loopback mock, both bundled test models; 107 properties, depth 9, 76 enum values. VERIFIED the no-cache engine build and Docker link check over 86 staged Markdown files (zero broken links). The runtime v2 schema still needs its B6 comparison/re-probe; no real model was called.
- 2026-10-03: OBSERVED the first synthetic seven-day report from the initial two-cycle measurement. Canceled the second cycle because two acquisitions do not fit the provisional 20-minute wrapper; exit 143, incomplete evidence. Replaced it with a single-sample timing helper. The next sample was correctly refused by the quiet-window guard after setup; both isolated clusters were stopped, volumes retained. Complete timing/size measurements remain NOT RUN.
- 2026-10-03: OBSERVED a material cutoff conflict on final contract review: §5.8 delivers what a workflow's own refresh fetched through its completion, while §5.5/R11 and AGENT_TOOL_CONTRACTS' time-scoped-read rule prohibit post-cutoff research content. A follow-on assessment can carry the same late source content. Asked the owner to clarify that RESEARCH_V1 completion/context projections must enforce the hypothesis cutoff while an investigation can receive its own refresh. Product implementation is held under the owner's stop-on-contradiction instruction; no contract exception has been granted or implemented.
- 2026-10-03: the owner instructed continuation; independent B0 measurement work resumed at 16:15 UTC using the original quiet window. The owner then explicitly approved the cutoff clarification. IMPLEMENTED the corresponding plan/tool/research/runtime contract amendments. The single-sample replay and the next HH:05 observer are in progress; B0 is not accepted.
- 2026-10-03: OBSERVED completed single-cycle measurement `b0-replay-20261003T161602Z.json` at 16:28:39 UTC. Replay 402.68 s, fixture loading 340.47 s, database 2,292,979,379 bytes; metadata reads and fixture stop exit 0. INFERRED the B0 sizing in §5.5: dataset 21 days, store 20 GiB, data-filesystem pressure floor 40 GiB. Other envelope values unchanged. The approved observer remains running through the next HH:05 report; B0 is not accepted.
- 2026-10-03, 17:09 UTC: VERIFIED the completed B0 observer, 169 successful reads, 54 memory samples and unchanged nine normal identities. Recorded resource sizing and the exact next-report comparison in §5.10/§6/§18. The declared M6-OD4 predicate passed; the authoring guards now enforce HH:07–HH:58 (B0 probe finish reserve HH:57). Final B0 source/PS5.1/documentation checks are in progress; B1 has not started.
- 2026-10-03, B0 complete: VERIFIED final PS5.1 parsing/ASCII for four scripts, twelve quiet-window boundary cases and `git diff --check`. `Snapshot` retained `source-003.json`; the final staged Docker link check (`docs-20261003T171441044Z`) passed 86 Markdown files with zero broken links and four historical Windows-link warnings. All B0 gates have evidence; actual v2 runtime comparison, candidate throughput and every product acceptance phase remain B1–B9 work. No additional owner decision is pending.
- 2026-10-03, B1 in progress: IMPLEMENTED draft `0008_m6_research`, frozen research/source seed definitions, database guards, an operator migration retry (five attempts on a 200-ms lock timeout only), real-role schema tests and standalone isolated-target/Docker journaling helpers. Contract updated with the code. These files were not yet built, migrated or tested at this entry; no normal command or B2 work had begun.
- 2026-10-03, 17:48 UTC: VERIFIED B1 engine build, two static schema checks and corrected Ruff preflight. OBSERVED isolated migration fail its seed hash check, exit 1; cleanup exit 0. Requested owner approval for the inferred bind-parameter correction and isolated rerun under the stop-on-gate-failure rule. Answer pending; dependent work held. No B1 acceptance or B2 work is claimed.
- 2026-10-03, checkpoint publication: the owner requested `push changes to main`. Committed the partial work as `2d17dff` and integrated the newer main documentation, preserving the standing cleanup rule and its required `Clean` phase. `Clean` implementation/cleanup are NOT RUN in this publishing task. The request authorizes the current checkpoint on main, not the pending migration correction, M6-A acceptance or B10/B11.
- 2026-10-03, checkpoint pushed: VERIFIED merge commit `8f2a120` preserves remote main `4c10142`; `git push origin HEAD:main` exit 0. Main now contains completed B0 evidence and the explicitly incomplete B1 draft. Publication does not resolve the failed migration gate or the pending correction/rerun question.
- 2026-10-03, B1 resumed: the owner instructed `go ahead with b1`. IMPLEMENTED the scoped JSONB/canonical bind correction; VERIFIED the isolated migration and eleven initial schema tests (three existing Alembic configuration warnings, no skip). Expanded completion/immutability checks, the populated old-worker/lock/recovery harness and exact-name `Clean` are implemented for verification. No envelope value changed. The recovery-only database uses `asl_m1_m5_m6_<run>_recovery` so the unchanged M3-M5 fixture guards apply; it is still owned by `asl-m6-<run>-recovery` with fresh secrets and no Internet route.
- 2026-10-03, 21:40 UTC: run `m6-b1b` passed 17 schema tests and the populated upgrade/downgrade, bounded lock and old-worker continuity checks. The final restore assertion failed: legacy and M6 row fingerprints match, but the protected-structure metadata hash differs. The fixture is stopped; restored downgrade-refusal/invariant checks were not reached. Asked the owner for isolated diagnosis and a representation-only harness correction, with any real protected-schema change still blocked. The first old-run Clean attempt also exposed a PowerShell one-element-array argument construction error before deletion; no Clean pass is claimed. Full B1 remains unverified.
- 2026-10-03, 21:47 UTC: VERIFIED the corrected Clean phase on finished `m6-b0a`, `m6-b0b` and `m6-b1a`: 15 exact-name resources removed in three sequential runs, evidence retained. The latest failed `m6-b1b` alone stays stopped for diagnosis. Added absolute command deadlines with stop reserves and verified parser/ASCII/expired-deadline checks; affected Build/Migration reruns remain pending. No normal-project command ran in the B1 continuation.
- 2026-10-03, B1 diagnosis resumed: the owner instructed `don't stop until complete it`, authorizing the pending isolated diagnosis/correction/rerun. VERIFIED all 76 differences are the single PostgreSQL cast-reconstruction form recorded in §6; no unexplained metadata differences remain. IMPLEMENTED the restore-only comparator, negative tests and PostgreSQL equivalence check, with exact in-place fingerprints preserved. Prepared fresh `m6-b1c`, retained two source snapshots and passed PS5.1/ASCII/whitespace checks. Build is queued with `-WaitForWindow` for HH:07, followed by full Migration and Clean; acceptance remains pending actual results.
- 2026-10-03, 22:10 UTC: VERIFIED final-source B1 Build (four static/registry tests and Ruff) and full Migration in `m6-b1c` against `source-003.json` / engine image `612250089a2d…67c8d67`. All nineteen schema tests passed. Exact in-place protected schema/legacy data, bounded lock retries, old-image worker continuity, populated dump/restore, unchanged refused-downgrade snapshot and all accounting/M3/M4 invariants passed. Both clusters stopped. The final two Clean phases are reserved for HH:15; no normal-app operation or later batch ran.
- 2026-10-03, 22:17 UTC: VERIFIED sequential final Clean phases for `m6-b1b` and `m6-b1c`, ten exact-name resources each. All five completed runs are clean (35 resources total); evidence remains. The final Docker documentation check passed on 86 Markdown files with zero broken links and four historical warnings. All 237 service/tool files match the tested `source-003.json`; PS5.1 parsing/ASCII checks passed. B1 is complete within its batch scope; B2 is next, and full M6-A remains incomplete.

- 2026-10-04 Europe/Budapest: the owner instructed `push changes`. VERIFIED B1 source commit `7f327ae` published to `origin/codex/m6-research-investigations`, with the remote hash checked. Publication records are a documentation-only follow-up; no product source or acceptance scope changed. The single M6-A delivery PR remains after B2–B9.

- 2026-10-04, B2 in progress: OBSERVED clean `codex/m6-research-investigations` at `ffa4712`, matching the handoff. Retained pre-interface native replay baselines in isolated `m6-b2base`, including the unchanged M3 gapped-stop fingerprint; the cluster is stopped. IMPLEMENTED bounded grammar, Decimal operators/interpreter, native/candidate strategy seam, research-only install/manifest guards, truthful historical fidelity labels, unit/property fixtures and EngineParity/M3/M4 harness phases. Contracts updated with source; envelope/seeds, M1–M4 DDL, protected Compose blocks and agent tool permissions are unchanged. Product acceptance is NOT RUN at this entry. No normal-app command or B3 work began.
- 2026-10-04, 03:22 UTC: OBSERVED `m6-b2a` Build pass the image build and four static/registry checks, then fail Ruff with three I001 test import-order findings. The authoring formatter's staged module classification differed from the built image. The fixture is stopped; Checks, Regression and EngineParity are NOT RUN. Requested owner authorization for a test-import/formatter-only correction and rerun under the explicit stop-on-required-gate-failure instruction; dependent work held. No product lint error or parity result is claimed.
- 2026-10-04, B2 resumed: OBSERVED owner reply `go ahead`, authorizing the scoped import/formatter correction and remaining B2 verification. IMPLEMENTED the three test import-order fixes and explicit first-party classification in the staged formatter; product logic is unchanged by this correction. Build/Checks/Regression/EngineParity reruns and cleanup remain pending actual results; no normal operation or B3 is authorized.
- 2026-10-04, 06:50 UTC: VERIFIED corrected isolated Build, four static/registry checks and Ruff on image `62ba733d…5f10a12`; Checks passed 145 tests in 6.29 s, no skips. The corrected staged formatter passed with zero source changes. Regression is waiting for 07:07 UTC so its unchanged full reservation fits the measured window; EngineParity and final delivery remain pending.
- 2026-10-04, 07:22 UTC: FAILED Regression, 167 passed/two failed/no skips, 892.41 s, no timeout. The ordinary fixture's replay flag defeats the existing isolation-denial test; API readiness still accepts 0006/0007 and rejects the migrated 0008 fixture at System status. The fixture stopped successfully. Read-only diagnosis and evidence updates only; requested owner authorization for the scoped Regression environment and additive readiness corrections. EngineParity and delivery are held under the explicit stop-on-required-gate-failure instruction; no envelope, protected DDL or normal operation changed.
- 2026-10-04, B2 regression correction resumed: OBSERVED owner reply `Ok go ahead and fix`. IMPLEMENTED Regression-only replay flag 0 and additive 0008 readiness compatibility, retaining 0006/0007 and all identity guards/test expectations. Failed evidence was preserved before reruns; source-003 binds these corrections. Rebuilt acceptance and delivery remain pending actual results.
- 2026-10-04, 08:07 UTC: VERIFIED corrected Build/static/Ruff, three focused regression/readiness tests and all 145 B2 Checks without skips; tested image `37dea4ee…0f5ff98`. All 405 application/tool/test hashes match it and protected paths/window guards are unchanged. OBSERVED full Regression start after its 25-minute quiet-window reservation; database startup/migration passed. Regression/EngineParity and delivery remain pending actual results.
- 2026-10-04, 08:22 UTC: VERIFIED Regression, all 169 tests passed in 872.26 s, no skips; one existing Starlette warning. FAILED EngineParity at candidate installation (`candidate_definition_conflict`), before financial/signal comparison, after gapped-stop native replay. Both fixtures stopped successfully. Read-only diagnosis finds a shared JSONB/canonical-text bind, unlike the existing execution fixture installer and B1's corrected seed binding. Separate parameters are PROPOSED; owner approval is pending under the explicit required-gate-failure stop rule. No install correction, final Clean or local commit ran.
- 2026-10-04, 08:28 UTC: OBSERVED owner approval of the binding fix and completing B2. IMPLEMENTED the two-line parameter separation; earlier gate JSON and all failed parity outputs preserved before rerun. `source-004.json` and image `7cd93cff…6e64aea` bind the fix. VERIFIED Build/static/Ruff; focused research checks prove exact stored JSON/canonical/hash, idempotency and refusal of an unchanged conflicting synthetic definition. The three prior Regression/readiness cases also passed again. Checks, Regression, EngineParity and delivery reruns remain pending actual results.
- 2026-10-04, 08:48 UTC: VERIFIED final-image Checks (145 passed, 6.67 s) and all sixteen M3/M4 Regression files (169 passed, 891.28 s), no skips. EngineParity passed gapped-stop, quiet and pilot-lifecycle financial/per-bar comparisons, both pilot fast/per-step comparisons and the pre-interface native baseline. Fixture stops passed. All 405 tested source hashes, protected paths, PS5.1/ASCII and unchanged window guards pass authoring review. Clean is waiting for 09:15 UTC under its unchanged five-minute HH:15–HH:55 reserve; final documentation and local delivery remain pending. No normal-app operation or B3 ran.
- 2026-10-04, 09:15 UTC: VERIFIED Clean, seven exact-name resources removed, all isolated project inventories empty and final fixture image absent. The three historical replaced image IDs are also VERIFIED absent; that follow-up required no additional removal. Baseline Clean had already removed five resources. Evidence remains, including prior failures. Final completion documentation and local commit are in progress; no normal resource was addressed.
- 2026-10-04, 09:17 UTC: VERIFIED completion-documentation Docker check, 86 Markdown files, zero broken links and four historical Windows-link warnings. B2 acceptance/cleanup is complete within its approved batch scope. Local delivery uses the existing codex branch, an explicit 28-file allowlist and the native Git journal in `.cache/m6/m6-b2a/delivery.jsonl`. B3 is next and NOT RUN; full M6-A and its PR remain after B0–B9 acceptance. No further B2 owner decision is needed.
- 2026-10-04 Europe/Budapest: OBSERVED owner instruction `create pr and merge into main` after local B2 commit `431dff5`. VERIFIED clean branch and remote main `9241034` already an ancestor; remote codex branch still `ffa4712`. No open PR exists. The owner authorizes a completed B1/B2 checkpoint PR/merge before B3–B9, as recorded in [DECISIONS](../../DECISIONS.md#2026-10-04--owner-requests-a-b1b2-checkpoint-pr-and-merge). Publication is in progress; full M6-A acceptance, B10/B11 and every normal-app operation remain outside this request.

## 17. Decision log (PROPOSED)

1. **Research runs on the existing engine through the existing replay path.** One engine, one risk gate, one ledger model; no second simulator to drift.
2. **A second PostgreSQL cluster for research compute**, the catalog in the main database (§5.1).
3. **The process that runs candidates is cut off from the main database**: no route, no credential (§5.1).
4. **Databases stand in for accounts.** The single-account schema is the pilot's; changing it waits for the boundary.
5. **Recorded quotes only.** Bar history needs a financial model of its own (§5.12).
6. **The grammar is flat and bounded**, so it fits the strict argument object and needs no recursion.
7. **Candidates reuse the engine's protection template.** A candidate chooses signals and bounded parameters, never order mechanics.
8. **Parity is defined on a portable projection**, because identifiers derive from the strategy identity (§5.3).
9. **No performance threshold is invented.** Eligibility is completeness, integrity and review; the protocol's own sample minimums apply.
10. **The holdout is an information cutoff on the workflow**, not only a filter on results (§5.5).
11. **Stores are append-only and versioned**, because the market tables cannot be pruned (§5.4).
12. **Shadow evidence is written to the catalog**, so it does not depend on the research cluster (§5.6).
13. **Reviews stay fixed children.** `request_review` as a model-chosen tool waits for M7, where the coordinator needs it.
14. **Permissions follow the matrix** where the tool contract lists more roles (§5.8).
15. **Approvals for M6 use the agent approval store**, not the pilot's, so the pilot's approval page and the execution worker's approval poll are unaffected.
16. **Full-text search in PostgreSQL**, no new store.
17. **The fetcher follows the M2 transport technique** rather than the agent runner's gateway: no model code runs in it, and a request is a source ID, not a destination.
18. **A screening job runs one cost scenario; a nominated candidate runs both.** It halves the cost of trials that are discarded.

B4 additions (2026-10-04). Items 19–22 are the owner's decisions of that day; 23–27 are implementation choices inside the approved design.

19. **Stores rotate early**, at 28 days or the same share of 20 GiB, so a shadow bound to the old version finishes below the cap (owner).
20. **A shadow advance replays the candidate and the reference under H1** (owner).
21. **One dataset is sealed per UTC day** after staging has caught up (owner).
22. **Shadow advances are not trials** and have their own bounds (owner).
23. **The bridge has its own identity in the research cluster (`asl_bridge`) and never owns it.** The runner creates and drops stores on a recorded request. That keeps "no engine credential" true on both sides of the bridge.
24. **The registry lives in the research cluster's `postgres` database**, which has no engine schema and is never a store, so dropping any store, the first included, loses no registry.
25. **Rows are transported as PostgreSQL row text and compared after the write**, rather than re-encoded through the client, so "without changing a value" is checked on every batch.
26. **A shadow replay stops at every recorded mark with that mark's own visibility.** The prefix check is then an exact comparison, not a tolerance.
27. **Store lifecycle events are rows of the staging journal**, identified by content, so migration 0008 did not change.

## 18. Completion evidence

### B4 final-source acceptance

**VERIFIED complete within B4's scope, 2026-10-04.** The applicable gates, an
independent review, documentation validation and cleanup passed. This is B4
batch evidence; it does not complete M6-A. Nothing was deployed or activated,
and no command addressed the normal application.

IMPLEMENTED within the approved B4 boundary (R14, R20 and the bridge part of
R16; design in §5.4 and §5.6, owner decisions of the day in
[DECISIONS](../../DECISIONS.md#2026-10-04--m6-b4-handed-over-and-four-points-the-plan-left-open-execplan-0023)):

- an inert `research-bridge` Compose block in the `research` profile, the only
  process on both the main and the research network, with two secrets, no
  volume, and a default command that idles unless research is enabled;
- staging of published market rows into the current store in bounded, verified
  batches, with a store-side watermark, recorded gaps and a journal relayed to
  the catalog;
- a store registry in the research cluster, early rotation, and creation and
  removal of stores by the runner on the bridge's recorded request;
- one sealed research dataset per UTC day and sealed shadow windows, each with
  a manifest of exactly what was staged;
- relay of jobs to the research cluster and of results back, checked by hash,
  with owner cancel, expiry and late results;
- shadows as deferred replays: eligibility as a code check, the freeze, daily
  and on-demand advances of the candidate and the reference under H1, immutable
  marks, the prefix check, and every way a shadow ends.

Migration 0008, the shared engine and replay code, the envelope values and
every existing Compose block are unchanged. No dependency was added, and none
of the four deferred tools exists.

VERIFIED on final `m6-b4b` image
`ffe756c4c45c7aa76a81cab5b28b393937b9a86c861063f404005d220308da0d`, code
identity `c747ddf7bbbf86d7f3901517b4eb1e261aa42f210eb7cbf065d67287e756b81d`,
on two real PostgreSQL fixture clusters, 15:20–15:40 UTC, without a skip:

| Phase | Result |
|---|---|
| Build | Image, four static/registry tests (1.71 s) and Ruff passed |
| Staging | Compose review of four research blocks; bridge probe; default-disabled start; 12 tests in 77.62 s |
| ShadowSchedule | 10 tests in 43.20 s |
| ResearchRunner | 15 catalog tests (16.10 s), runtime probe, 17 runner tests (59.50 s) |
| Regression | 169 M3/M4 tests in 871.56 s; one existing deprecation warning |
| Checks | 145 tests in 6.77 s |
| HoldoutIsolation | 9 tests in 3.67 s |

What those runs show, by requirement:

- **R20.** Only published rows are copied, in dependency order across many
  small commits, and each table equals its source as row text (733 rows in 122
  batches over 8 passes in the recorded evidence). The same replay on an
  unstaged copy and on the staged store has the same fingerprint. Batch, pause,
  settle and quiet-window bounds hold. A source gap, rows lost to retention
  during an outage and an unpublished dependency are each recorded and never
  filled in. A repeated batch is a no-op; a changed or mismatched copy fails
  closed.
- **R16, bridge part.** Neither bridge identity holds a grant on an M1–M4 table
  or any engine authority, and the bridge identity in the research cluster
  cannot create or drop a database. The runtime-shaped bridge container runs as
  UID 10001 with exactly two secrets, no volume, a read-only root and no
  default route. The runner's own isolation probe passed again unchanged.
- **R14.** A shadow's first order is decided after its freeze; no decision,
  fill or bar evaluation exists at or before it, read from the engine's own
  rows (frozen 15:22:47.661845 UTC in the recorded evidence, bars opening
  15:00–17:00 evaluated, first order at 18:00:01.27 on the synthetic
  timeline). The second advance reproduces the first mark for both subjects,
  and a mark cannot be rewritten. A changed staged bar suspends the shadow and
  its candidate instead.
- **§4.1 "the bridge is down".** Nothing is staged or relayed, jobs stay
  queued and shadows are not advanced. An outage longer than the main
  database keeps quotes ends the shadow as incomplete with the gap recorded,
  also when the bridge stopped right after journaling it.
- **§4.1 "a result is relayed twice".** One result per job by hash; the second
  relay is a no-op. A changed result or a refused transport ends the job
  without a result.
- **§4.1 "a store version is replaced while a shadow runs".** The shadow keeps
  its version and is still advanced on it; new shadows bind to the new
  version; the old one is dropped only when nothing references it, and new
  work on it is refused.

The B3 six-cell result kept its portable fingerprint
`fca91e1d007880d0413331f2f3b30a6a7f1ea59926e94ee0c76583fd5c508858`.
Every market row in these runs is a labeled synthetic fixture row, and every
real replay reports an insufficient sample; the eligibility and
`EVIDENCE_READY` cases use labeled fixture reviews. Nothing here says anything
about a strategy's performance.

Review and history. An independent read-only review of the uncommitted code
reported ten findings; nine were corrected before the final-source run and the
tenth is an open risk (§19). Eight authoring images on `m6-b4a` and the first
`m6-b4b` attempt (one failing new test) are kept as history in
[COMMANDS](../COMMANDS.md#m6-b4-authoring-iterations-2026-10-04) and under
`.cache/m6/`; none of them is acceptance evidence.

Cleanup. Exact-name `Clean` passed for both runs, seven resources each; all
eight project inventories per run are empty and all ten recorded build image
IDs are absent. Source review: the final snapshot differs from the Build-bound
one only in documentation, protected paths are unchanged against `6e8fbb6`,
the harness scripts parse under PowerShell 5.1 and are ASCII, and
`git diff --check` is clean. The completion documentation check passed on 86
Markdown files with zero broken links and the four historical Windows-link
warnings.

| Gate | B4 applicability and result | Evidence / remaining boundary |
|---|---|---|
| Q01 UX | NOT APPLICABLE: no UI changes | B8 pages remain unimplemented |
| Q02 Accessibility | NOT APPLICABLE: no UI/browser changes | No accessibility claim |
| Q03 Correctness | VERIFIED within B4: staged rows equal their published source, staged and unstaged replays agree, manifests state what was staged, one hash-checked result per job, no shadow decision before the freeze, marks reproduced and immutable | Staging, ShadowSchedule; unchanged B3 fingerprint; all 169 M3/M4 Regression tests. Fixture volumes only |
| Q04 Security | VERIFIED within B4: no M1–M4 grant and no engine authority for either bridge identity, registry guard, bridge container UID, secrets, mounts, read-only root and routes, no main-database secret in any research service | Bridge probe, Compose review and grant tests on real PostgreSQL; B5/B6/B7 integrations remain open |
| Q05 Reliability | VERIFIED: bridge down, outage beyond retention, second relay, changed result, refused transport, cancel, unanswered deadline, late result, a failing stage or delivery that stops nothing after it, a store that lost its rows, a failed store creation | Staging, ShadowSchedule; activation rehearsal remains B9 |
| Q06 Performance | VERIFIED as bounds only: batch rows, publications and bytes, batches per pass, pause, quiet window, four shadows, one advance a day, the mark limit, rotation thresholds | NOT MEASURED: the 1,000 rows a second target, full-density volumes, a 21-day shadow's wall time, the 2 s statement limit on the normal database (§19). Saturation is B9 |
| Q07 Automation | Build/static/Ruff, Staging, ShadowSchedule, ResearchRunner, Regression, Checks and HoldoutIsolation VERIFIED without skips | Migration and EngineParity NOT RUN (schema and shared code unchanged); GitHub CI NOT RUN (it does not start) |
| Q08 Visibility | VERIFIED: the staging journal with gap kinds and store lifecycle events, recorded refusals and end reasons, the labels each shadow result carries (`SHADOW_DEFERRED_REPLAY`, `NOT_A_LIVE_ENGINE`, `H2_STRESS_NOT_RUN_IN_SHADOWS`) | No owner UI or deployed-service observability claim; B7/B8 remain open |
| Q09 Recovery | VERIFIED: staging resumes from the store-side watermark, the journal reaches the catalog exactly once, an advance that never ran is recorded again, exact-name cleanup | A lost research cluster fails closed only (§19); normal deployment is excluded from B4 |
| Q10 Maintainability | VERIFIED: no new dependency, unchanged migration and shared engine, contracts updated with the code, PostgreSQL 17 facts recorded against official pages, independent review, source checks and the 86-file documentation check | Full milestone review remains after later batches |

NOT RUN: `Migration` and `EngineParity` (nothing they cover changed); B5
sources (separate work, PR #24), B6 workflow and tool integration, B7–B9, any
real recorded data or full-density volume, normal deployment, activation,
original secrets, runtime login, and public or model calls. GitHub CI did not
run. Full M6-A remains incomplete. No envelope value or authority changed.

**Acceptance again on the source merged with `main` (2026-10-04, 22:30 UTC).**
B5 merged first, as `52eab97`, and changed migration 0008, so the B4 branch
merged `main` and every phase whose inputs changed was rerun before the B4 pull
request is merged. VERIFIED on fresh run `m6-b4c`, final image
`3327dd1e720e2bcbcea86717595c76fb0e0ad11dd970a8dda7c9316e5d75833e`,
21:40–22:27 UTC, without a skip:

| Phase | Result on the merged source |
|---|---|
| Build | Image, four static/registry tests (1.80 s) and Ruff passed |
| Staging | Compose review, bridge probe, default-disabled start; 12 tests in 79.66 s |
| ShadowSchedule | 10 tests in 43.30 s |
| ResearchRunner | 15 catalog tests (16.13 s), runtime probe, 17 runner tests (59.04 s) |
| HoldoutIsolation | 9 tests in 3.78 s |
| SourcePolicy | Compose review, runtime probe, disabled fetcher; 249 tests in 43.39 s |
| EvidenceInjection | 24 tests in 31.63 s |
| Checks | 317 tests in 7.61 s |
| Migration | 19 schema tests in 17.43 s, 3 existing warnings; populated migration VERIFIED |
| Regression | 169 M3/M4 tests in 872.85 s; one existing deprecation warning |

The counts equal the two batches' own acceptances, and the B3 six-cell
fingerprint is unchanged. One thing the rerun found: the first attempt on this
run FAILED `test_permission_lock_does_not_grant_epoch_mutation`, a B3 test that
expected the source identity to be refused `research_hold_permission_epoch()`.
B5 granted that fixed read on purpose and tests it itself, but its acceptance
did not rerun `ResearchRunner`. The test now asserts the merged contract: the
source identity may take the read and still cannot change the epoch. No product
code changed for it. `EngineParity` NOT RUN: `app/execution/`, `app/replay/`,
`app/strategies/` and `app/evaluation/` are unchanged by both batches. The run
was cleaned by exact name and its two build images are absent; the link check
passed on 86 files. Commands and the failed attempt are in
[COMMANDS](../COMMANDS.md#m6-b4-merge-of-main-and-acceptance-on-the-merged-source-2026-10-04).

### B3 corrected-source acceptance

**VERIFIED complete within B3's scope, 2026-10-04.** Applicable runtime gates,
review, documentation validation and cleanup passed. Local delivery retains
its native receipt and Git journal. This is B3 batch evidence; it does not
complete M6-A.

IMPLEMENTED within the approved B3 boundary: an inert research PostgreSQL/runner
profile; transactional catalog jobs, UTC reservations and immutable trials;
research-only inbox, leases/fencing, one lost-worker retry, reset and outbox;
deterministic registered partition/cost results and hash-checked delivery/reuse;
SYSTEM-only holdout evaluation and cutoff/role projections. The runner retains
the existing candidate interface, financial engine, replay and M4 evaluation.
The shared replay edit adds optional market/factory injection with unchanged
defaults. Migration 0008 adds only the fixed M5 epoch-lock function; no protected
M1–M4 object or existing Compose block changes. No dependency was added.

VERIFIED on final `m6-b3b` image
`2585ef231eee7cfbe148bd406f9d8e27308d116307d9769fd070e91122c8bf28`:
four Build static checks and Ruff, 15 catalog tests (16.36 s), 17 runner tests
(63.31 s), 9 holdout tests (3.78 s), runtime bootstrap/isolation, new Compose-block
validation, all 145 Checks (6.90 s), all 169 M3/M4 Regression tests (872.39 s)
and all three EngineParity scenarios with pilot fast/per-step and pre-interface
native baseline comparisons. Code identity is
`69b27b1c298e1f54ae95ca340db0998ef6624092f69f72e884c71a2c7d801057`.
The two full six-cell synthetic replays
produce identical documents/hashes, preserve all twelve reset events and report
INSUFFICIENT_SAMPLE in every cell. Worker process death, stale fences, a single
retry and a second loss, mid-replay deadline, cancellation, concurrent requests
and claims, budget exhaustion, frozen identities and indirect cutoff leakage
are exercised. A queued job accepted under a simulated prior code identity is
refused by the current worker before reset/replay. No test was skipped.

Fresh `m6-b3c` image
`9c348b16929a413edaeec271c26290c73ee975d5633a615b7364ffa00e3a80c7`
passed Build/static/Ruff, all 19 schema tests (17.53 s) and populated Migration:
upgrade/downgrade/reupgrade, bounded locks, old-image fixture worker continuity,
dump/restore, downgrade refusal, accounting/M3/M4 invariants and reconciliation.
The image IDs differ; `SourceEquivalence.json` verifies all 421 non-doc files
match the primary build, and `ImageEquivalence.json` verifies identical RootFS
layers and runtime Config except Compose labels. This fresh fixture preserved
the intermediate migration's populated data and evidence until cleanup.

Exact-name Clean passed for all three B3 runs: `m6-b3a` removed four resources,
`m6-b3b` thirteen, `m6-b3c` ten. All eight project inventories per run are empty,
and all seven recorded build image IDs are absent. Retained source snapshots,
commands, outputs and failed attempts remain under `.cache/m6/`. Source review
verifies unchanged protected paths and existing Compose blocks, all 421 final
non-doc hashes, ASCII/PS5.1 compatibility and `git diff --check`.

The implementation review fixed a grant-before-role ordering error and a
UTC-midnight reservation bug, then added the execution-time code-identity gate;
all are covered by the final-source gates.
First-attempt failures and the deliberately stopped pre-UTC Regression remain
retained, as does the pre-start cancellation for the final correction, with
their original image/source identities and exit codes. Native
commands, source snapshots, result document, phase evidence and authoring review
are under `.cache/m6/m6-b3a/`, `.cache/m6/m6-b3b/` and `.cache/m6/m6-b3c/`, summarized in
[COMMANDS](../COMMANDS.md#m6-b3-corrected-source-acceptance-2026-10-04).
The completion-documentation Docker check passed 86 Markdown files, zero broken
links and four historical Windows-link warnings. `Delivery.json` and
`delivery.jsonl` under the primary run record the actual local commit and clean
worktree; no push, PR or merge was part of that local delivery. The subsequent
owner-authorized checkpoint publication is recorded in §16 and
[DECISIONS](../../DECISIONS.md#2026-10-04--owner-requests-a-b3-checkpoint-pr-and-merge).

| Gate | B3 applicability and result | Evidence / remaining boundary |
|---|---|---|
| Q01 UX | NOT APPLICABLE: no UI changes | B8 pages remain unimplemented |
| Q02 Accessibility | NOT APPLICABLE: no UI/browser changes | No accessibility claim |
| Q03 Correctness | VERIFIED B3 transactions, identity/dedupe, deterministic output, immutable attempts and cutoff projections | ResearchRunner, HoldoutIsolation, restored invariants, all 169 M3/M4 Regression tests and EngineParity |
| Q04 Security | VERIFIED within B3: scoped roles, exact-hash/epoch gate, sealed inputs, internal network, two research secrets, UID/capabilities/read-only root | Runtime probe and negative tests; scoped ASVS 5.0.0 mapping in SECURITY; B5/B6/B7 integrations remain open |
| Q05 Reliability | VERIFIED process loss, lease expiry, stale fencing, reset/retry once, second-loss failure, cancellation, deadline and executing-code mismatch | ResearchRunner; catalog/result relay and activation rehearsal remain B4/B9 |
| Q06 Performance | VERIFIED frozen concurrency/queue/day/candidate/storage/wall limits and actual replay interruption | B0 envelope unchanged; full-density candidate throughput/saturation remain B9, not inferred from this fixture |
| Q07 Automation | Build/static/Ruff, Checks, Regression, EngineParity and scoped new tests VERIFIED without skips | Existing Checks/Regression JSON retains B2 suite metadata; full M6 and GitHub CI NOT RUN |
| Q08 Visibility | VERIFIED immutable attempts/outcomes/outbox and explicit incomplete/insufficient labels; structured failure and heartbeat source reviewed | No owner UI or deployed-service observability claim; B8/B9 remain open |
| Q09 Recovery | VERIFIED populated forward/reverse migration, bounded lock retries, old-worker continuity, restore invariants and downgrade refusal | Exact-name cleanup VERIFIED; normal deployment explicitly excluded by this B3 authorization |
| Q10 Maintainability | VERIFIED shared engine/M4 evaluator, no new dependency, versioned official references, updated contracts, source/PS5.1 review and 86-file documentation check | Local commit recorded in Delivery.json; full milestone review remains after later batches |

NOT RUN: B4 bridge/staging/stores/shadows, B5 source ingestion, B6 workflow/tool
integration, later M6 gates, normal deployment, activation, original secret or
runtime login and public/model calls. Publication was NOT RUN during B3
implementation and is separately authorized above. Full M6-A remains incomplete.
The four deferred tools remain absent/refused. No envelope or authority changed.
No further B3 decision is pending.

### B3 first attempt: historical failure, resolved after owner continuation

IMPLEMENTED draft runner/catalog/projection code and phases. VERIFIED only the
authoring checks and engine Build/static/Ruff in `m6-b3a`. ResearchRunner FAILED
before its tests on migration grant ordering. All other required B3 phases are
NOT RUN on this source. [COMMANDS](../COMMANDS.md#m6-b3-first-acceptance-attempt-2026-10-04)
records the actual commands, identities and retained failure evidence. This
table describes the first attempt only. The owner's subsequent continuation
and corrected-source verification are recorded in section 16; no first-attempt
failure is relabeled as a pass.

| Gate | B3 applicability and acceptance condition | First-attempt result |
|---|---|---|
| Q01 UX | No new UI; B8 owns its pages | NOT APPLICABLE to B3 |
| Q02 Accessibility | No UI or browser changes | NOT APPLICABLE to B3; no accessibility claim |
| Q03 Correctness | Atomic reservations, dedupe, deterministic replays, immutable attempts, holdout/cutoff and existing engine invariants | NOT RUN; ResearchRunner prerequisite failed; remaining gates pending |
| Q04 Security | Isolated network/credentials, role restrictions, bounded inputs and protected scope | Static review IMPLEMENTED; runtime isolation and negative gates NOT RUN; ASVS scope in SECURITY |
| Q05 Reliability | Worker death/expiry, stale fences, one retry, reset, cancellation and deadlines | Tests IMPLEMENTED; NOT RUN |
| Q06 Performance | Frozen one-job/queue/day/resource/storage/wall bounds; no envelope change | Bound tests IMPLEMENTED; NOT RUN; B9 saturation remains open |
| Q07 Automation | Docker build/static/lint plus required product/negative/concurrency/regression checks without skips | Build/static/Ruff VERIFIED; ResearchRunner FAILED; all other B3 gates NOT RUN |
| Q08 Visibility | Durable attempt/outcome records, redacted structured failures, heartbeat | IMPLEMENTED; runtime evidence NOT RUN |
| Q09 Recovery | Research-only bootstrap, affected schema/migration/restore checks and exact-name cleanup | Migration blocked; exact-name cleanup VERIFIED; normal deployment excluded by owner instruction |
| Q10 Maintainability | Shared engine/M4 evaluator, no new dependency, versioned official guidance and updated contracts | Guidance/source review recorded; completion review and documentation verification NOT RUN |

### B0

**VERIFIED complete within B0's scope, 2026-10-03.** These are contract, scaffold and engineering-measurement gates. They do not accept product runtime behavior or complete M6-A. Every §10 phase and Q01–Q10 remain required in the following batches.

| Item | Actual evidence | State |
|---|---|---|
| Contracts | Named contracts amended alongside the scaffold; approved cutoff clarification recorded; MAIN_APPROVED remains defined but unreachable exactly as §5.2 requires | IMPLEMENTED; no product behavior claimed |
| Harness | PS5.1 parsing/ASCII checks; `Prepare`, `Snapshot` and read-only `-Describe`; standalone B0 fixture/probe with explicit target and window guards | VERIFIED authoring scaffold only; runtime acceptance not implemented |
| Safe failure | All acceptance phases beyond `Prepare` and `Snapshot` remain explicitly unimplemented; `Report` cannot accept this scaffold | IMPLEMENTED; runtime phase checks NOT RUN |
| Baseline observation | `.cache/m6/m6-b0a/b0-observation-20261003T120500379Z/commands.jsonl` and `summary.json`: 25 commands, all exit 0; six samples 12:05:00–12:08:01 UTC; nine container/image/start/restart identities unchanged | OBSERVED |
| VM memory | Docker 29.8.1, 16 CPUs, 8,277,090,304 bytes memory; `/proc/meminfo` available 6,052,900–6,101,636 KiB during the six samples | OBSERVED baseline only |
| Host memory/disk | Windows read-only CIM: total visible 16,685,636 KiB, free 5,050,340 KiB at the baseline; during the loaded sample at 16:28 UTC free 1,396,180 KiB. C: total 999,088,451,584 bytes; loaded available 551,357,804,544 bytes. VM data filesystem available 978,972,244 KiB | OBSERVED distinct host/VM measurements; no equivalence inferred |
| HH:05 report | SNAPSHOT as-of 12:00 UTC created 12:05:26.331392; prior 09:05, 10:05 and 11:05 offsets 24.092971, 24.860433 and 25.526456 seconds | OBSERVED baseline; no heavy phase running |
| Normal schema | Metadata SELECT returned `0007_m5_agent_runtime`; no migration or financial/source text read | OBSERVED |
| Official documentation | §6 refresh and INTEGRATION_EVIDENCE; existing HTTPX and PostgreSQL suffice for the approved design, no dependency added. Rights/retention review recorded with attribution obligations | OBSERVED documentation; INFERRED license applicability |
| Schema preview | `.cache/m6/m6-b0b/b0-probe/out/schema-probe.json`; Codex CLI 0.159.2, schema SHA-256 `6df12a6ebcec18f7853c567adf5ea8e6e032a3aa1277c1cbf0ba6aff1037a06c`; gpt-6.1-sol/gpt-5.6-sol each exit 0; strict schema unchanged, valid synthetic output, no native tools/credentials | VERIFIED pinned CLI/mock preview only; real model NOT RUN; B6 must compare actual schema |
| No-cache build | `m6-b0b -Phase Build -NoCache` exit 0; engine image `sha256:56992cf506791dd0305e640e9c3c673edf74a59cac1b7eb07d29d06dbd527426`; application dependency/build steps executed, base image reused | VERIFIED isolated provisioning; no normal image rebuilt |
| Documentation links | Final network-none Docker check of `docs-20261003T171441044Z`: 86 Markdown files, zero broken links; four known historical Windows-link warnings | VERIFIED on the final B0 contract snapshot |
| Initial synthetic replay | First report in `m6-b0a/b0-probe/out/density-run1/report.json`, written 12:29:07.714 UTC; load 338.3 s, fingerprint `18011c0e…7f1198`. Second cycle canceled; overall command exit 143 | OBSERVED one completed report; two-cycle series incomplete, no timing gate passed |
| Retry/window guard | `m6-b0b -Phase Replay`: setup/migration exit 0; replay NOT RUN because its 15-minute reservation did not fit before HH:54. Stop exit 0, volume retained | OBSERVED safe refusal |
| Resumed B0 run | Observer `b0-observation-20261003T161441677Z` under existing approval; first child failed before replay on uv's temporary cache lock. With cache confined to `/tmp`, the sample completed at 16:28:39 UTC; all subsequent size/filesystem/stop commands exit 0. Observer subsequently completed at 17:09:44 UTC, exit 0 | OBSERVED complete single-cycle timing and bounded observer |
| Replay rate/store sizing | `b0-replay-20261003T161602Z.json`: 402.68 s replay / 7 days, 340.47 s load, 756.763 s total, fingerprint `18011c0e…7f1198` matches the earlier native report. Fixture DB 2,292,979,379 bytes. §5.5 records the inferred 21-day / 20-GiB / 40-GiB bounds | OBSERVED native engineering measurement; INFERRED sizing; candidate throughput NOT RUN |
| Contract conflict | §5.8 refresh completion versus §5.5/R11/time-scoped read contract; owner approved the research-cutoff clarification; canonical contracts reconciled | IMPLEMENTED clarification; runtime behavior NOT RUN |
| Stop at the conflict | Both fixture clusters stopped, volumes retained. The remaining authoring observer was stopped at 12:58 UTC after exact process/argument checks. Its partial journal has 62 successful reads and 19 memory samples; final identity/HH:05 comparisons were not reached | OBSERVED incomplete observation; all work held |
| Resource and quiet-window gates | 169 reads all exit 0; 54 samples, VM available 5,729,200–6,178,500 KiB; zero normal identity differences. Next report at 17:05:30.318837, offset +0.963810 s. Loaded sample 16:16–16:28 did not overlap HH:05. Hashed summary and limitations in §6 | VERIFIED for the measured workload and declared scheduled-minute predicate; B9 remains required |
| Final authoring guards | Four scripts PS5.1/ASCII; twelve start/finish quiet-window boundary cases; whitespace check; `source-003.json` | VERIFIED |
| Remaining milestone | B1–B9 implementation and every §10 acceptance phase; Q01–Q10 | NOT RUN; B0 complete |
| Deployment/activation | B10 requires separate chat approval; no B11 action | NOT RUN |

The first observer attempt failed at Docker pipe access in the authoring sandbox; no database query ran. The approved observer then completed with the necessary host access. Earlier `.ps1` invocations were blocked by local execution policy; the owner-approved process-only bypass resolved that block. Actual commands and limitations are recorded in [COMMANDS](../COMMANDS.md#m6-b0--2026-10-03-in-progress).

### B1 — complete

IMPLEMENTED migration 0008, sixteen catalog tables, immutable seeds/history, new NOLOGIN roles and published-only views, owner/transition/completion guards, bounded migration retries, real-role fixtures and the populated recovery/Clean harness. VERIFIED final-source run `m6-b1c` using `source-003.json` and engine image `sha256:612250089a2d83c12b73bef6bb563866cfdc8d0b2bc57f836fda4b16667c8d67`. Earlier seed-binding and restore-comparison failures remain in §16 and COMMANDS; the owner authorized both corrections.

| B1 check | Actual evidence | Result |
|---|---|---|
| Build/static/registry/lint | Build started 22:07:28 UTC; four tests passed in 1.76 s, 75 deselected, no skips; Ruff passed | VERIFIED for the B1 engine image; full M6 Build remains PARTIAL |
| Schema, real roles, grants and triggers | 19 tests passed in 18.09 s; three existing Alembic `path_separator` warnings; zero skips | VERIFIED |
| Populated static migration | 0007→0008→0007 with exact legacy row and M1–M4 structure fingerprints, then reupgrade | VERIFIED |
| Bounded lock failure/recovery | Five refused attempts in 2.463 s leave the snapshot unchanged; release after the first failure gives success on attempt two in 0.542 s | VERIFIED |
| Old fixture workers and live migration | Three container/image/start/restart identities unchanged; checkpoint 656→698 on lease epoch 2; unchanged pilot events; no worker failure lines. Migration 0.521 s; 60 lock samples, 39 observing migration locks; no protected lock stronger than AccessShare | VERIFIED, synthetic isolation only |
| Populated dump/restore | 16 catalog tables / 22 synthetic rows; every legacy/M6 row fingerprint preserved; all metadata matches with the 76 recorded cast reconstructions only | VERIFIED |
| Refused destructive downgrade | Restored non-fixture history refuses downgrade; complete snapshot unchanged | VERIFIED |
| Restored accounting | Reconciliation OK; no accounting, M3 or M4 invariant failure | VERIFIED |
| Final Stop/Clean | Both final fixture clusters stopped. Five sequential Clean phases removed 35 exact-name resources; the last two finished at 22:15:38 and 22:17:36 UTC. Inventories, journals and dumps retained | VERIFIED |
| Final documentation/source binding | Docker documentation check: 86 Markdown files, zero broken links, four historical warnings; 237 service/tool hashes match tested `source-003.json`; four harness files pass PS5.1 parsing/ASCII checks | VERIFIED |

The full Migration phase passed at 22:10:08 UTC. Its evidence file `.cache/m6/m6-b1c/Migration.json` has SHA-256 `47dbcb1e55dc9ff72980f7f42166409f6c49f3190644297d0e1fcb29a4140f91`. The retained before/after dumps are 601,701 / 747,897 bytes with hashes recorded in [COMMANDS](../COMMANDS.md#m6-b1-restore-diagnosis-and-final-rerun-2026-10-03). Final Clean inventories have SHA-256 `d27cdb2dbadf851814a239567422facd8cb097981cbc83dc000cfddb62dc01a7` (`m6-b1b`) and `41a86f5c481a45f80415d97a9a3b8f9e0e15a7901cbcc09df153ae672a0ba220` (`m6-b1c`). No dependency, envelope or protected DDL changed. VERIFIED B1 complete. NOT RUN: B2–B9, full M6-A acceptance, B10 and B11. No further B1 decision is pending.

VERIFIED publication: B1 source commit `7f327aef16eee8b32a9c2876c3205c550fee87ed` was pushed to `origin/codex/m6-research-investigations` at the owner's request on 2026-10-04 Europe/Budapest. The remote hash matched. Publication is separate from the remaining M6-A acceptance and delivery PR.

### B2 — acceptance and cleanup verified

**VERIFIED complete within B2's approved acceptance scope, 2026-10-04.**
The local Git delivery commands/receipt are separate from product acceptance;
see [COMMANDS](../COMMANDS.md#m6-b2-cleanup-and-local-delivery-2026-10-04).

IMPLEMENTED the §5.3 bounded grammar, Decimal operators/interpreter and
native/candidate strategy interface. Candidates use the existing replay engine,
risk, broker, immutable protection mandates and accounting. Research-only
install/start/manifest guards bind the actual database and declaration hash;
historical reports expose the actual rules and reduced recorded-quote fidelity.
No seed, envelope, dependency, protected DDL or Compose block changed. The four
still-refused trading/review/pause tools remain absent. B3 is NOT RUN.

Final acceptance uses `m6-b2a/source-004.json`, base `ffa4712`, and image
`sha256:7cd93cff947f876cf97d7f1cda90309d8a801e2d0bdbe9bbb5341f1d76e64aea`.
All 405 application/tool/test source hashes match the tested image. The commands
and native exit codes are retained under `.cache/m6/m6-b2a/` and summarized in
[COMMANDS](../COMMANDS.md#m6-b2-final-code-gates-2026-10-04).

| B2 check | Actual evidence | State |
|---|---|---|
| Pre-interface native baseline | `m6-b2base/NativeBaseline.json`, source `ffa4712`; three scenario reports, existing M3 gapped-stop hash unchanged | VERIFIED comparison baseline; synthetic only |
| Final Build | Completed 08:27:07 UTC; four static/registry checks and full app/tests/migration Ruff pass | VERIFIED B2 engine image; full M6 Build PARTIAL |
| Focused research installation | Exact stored JSON/canonical/hash, idempotent repeated installation, unchanged conflicting synthetic row refused; negative fixture rolled back | VERIFIED, exit 0 |
| Focused Regression/readiness | Three prior failure/readiness cases, 3 passed in 12.37 s, no skips; existing Starlette warning | VERIFIED, exit 0 |
| Unit/property/actual DB guards | Checks completed 08:29:42 UTC; 145 passed in 6.67 s, no skips | VERIFIED B2 Checks; full M6 Checks PARTIAL |
| Final M3/M4 Regression | All sixteen existing files, 169 passed in 891.28 s, no skips; one existing Starlette warning; completed 08:45:09 UTC | VERIFIED B2 Regression; full M6 Regression PARTIAL |
| EngineParity | Completed 08:48:46 UTC; gapped-stop, quiet and pilot-lifecycle match financial projections and every signal bar (143, 260 and 2 respectively); accounting/M4 invariants clean | VERIFIED, exit 0, no timeout |
| Native preservation | M3, portable and trace fingerprints unchanged against the pre-interface baseline for all three scenarios; full fingerprints also unchanged for gapped-stop and quiet | VERIFIED |
| Pilot fast/per-step preservation | Native and candidate each match their own full/M3/portable/trace and FINAL report hashes; actual candidate rules/reduced-fidelity labels asserted | VERIFIED |
| Baseline cleanup | Completed 03:23:26 UTC; five exact-name resources; inventory `f4c0aaac…8682ced`; evidence retained | VERIFIED |
| Final fixture cleanup | Completed 09:15:24 UTC; seven exact-name resources (two containers, two networks, two volumes, final fixture image); all project inventories empty | VERIFIED |
| Replaced fixture images | Completed 09:15:35 UTC; three exact historical image IDs already absent, zero additional removals; successful ownership records retained | VERIFIED; expected No-such-image inspections exit 1 |
| Authoring source review | 405 tested source hashes, protected paths/dependencies, four PS5.1/ASCII scripts, unchanged window functions and whitespace pass; seven cached helpers parse in PS5.1 | VERIFIED source review only |
| Completion documentation | Docker check completed 09:17:22 UTC: 86 Markdown files, zero broken links, four historical Windows-link warnings; only staged docs mounted, network none | VERIFIED; relative links only |
| Local delivery | Existing `codex/m6-research-investigations` branch; explicit 28-file allowlist; native command/result journal `delivery.jsonl` | Authoring Git receipt is recorded separately |

Final `Regression.json` SHA-256 is
`61da8baf94e90114a17757200540c19706867e09eba11cd45c6b63c4779a41e6`;
`EngineParity.json` SHA-256 is
`e9318772db6418cf53ed9f9b88478fa9843dfcc994f89a2396646c7b608ae47e`;
runner `research/out/parity/evidence.json` SHA-256 is
`9655beb2daf949fc986335b1c2a01c47cb4f44a5247cce527dfb10185f15c34a`.
The native gapped-stop M3 fingerprint remains
`2500c8d126e83c49976dd1ade3af27a1e4abd5bbddd44c5db03a6a1b8bf5561e`.
Financial projection rows, ledger postings, per-bar signals, immutable mandates,
reports, traces and native command logs remain beside those JSON records.

Final Clean inventory SHA-256 is
`b58a92db8562cd5b6f0bd077421092036ed965628543d75ddb97f79f0195d176`;
`Clean.json` SHA-256 is
`e61b70113b68f29eba48adf5de75be1a4bb0847c80422116eb30815ec85b9132`;
`RetiredBuildClean.json` SHA-256 is
`fa0323dcf6c6b1361c0c924cd2b45c78fd408ad11a495bf44e16a0856ae3efff`.
No forced removal, global prune, base/shared image or normal project operation
ran. The baseline's five and final run's seven named removals are recorded
separately; the three already-absent historical image IDs are not extra removals.

The scoped quality assessment preserves the full M6 requirements:

| Gate | B2 applicability and actual result | Remaining full-M6 work |
|---|---|---|
| Q01/Q02 | NOT APPLICABLE: no UI changes | Research UI/browser/accessibility gates in later batches |
| Q03 | VERIFIED: strict bounded declarations, exact Decimal calculations, immutable definition/hash guards, financial/per-bar parity and accounting invariants | Job/catalog lifecycle and full workflows |
| Q04 | VERIFIED scoped chapter-level ASVS 5.0.0 review in [SECURITY](../contracts/SECURITY.md#m6-b2-declaration-and-execution-boundary-execplan-0023); actual database/mode/forward-manifest denials and unchanged authority | Tools, grants, routes, sources, injection and SecretScan NOT RUN |
| Q05 | VERIFIED: unavailable/gapped inputs, crossings, protective exits, replay/isolation and M3/M4 failure/regression cases; failures retained | Research cancellation, saturation, source/agent faults and recovery |
| Q06 | NOT RUN: measured candidate job performance is outside B2's approved checks. Existing `test_m3_throughput.py` tests passed replay fast-path correctness, not elapsed-time budgets | Candidate job/staging/report budgets and PerformanceResearch/coexistence remain B9 gates; synthetic parity is correctness evidence |
| Q07 | VERIFIED scoped containerized Build/Ruff/static, 145 Checks, 169 Regression tests and EngineParity; no skips | Full M6 Build/Checks/Regression and remaining §10 phases NOT RUN |
| Q08 | VERIFIED actual immutable rule linkage, reduced-fidelity manifest/evaluation labels and FINAL report equality | Research services/jobs/UI operational visibility |
| Q09 | VERIFIED reproducible isolated build and additive 0008 readiness; protected DDL unchanged; B1 migration evidence preserved | Full M6 mixed-version/backup/recovery/deployment NOT RUN; B10 needs separate chat approval |
| Q10 | VERIFIED source/official-guidance/contract review, PS5.1/ASCII and completion-documentation relative-link check | Full milestone review |

Earlier failures remain visible and were corrected only after owner approval:

| Historical attempt | Retained result | Authorized correction |
|---|---|---|
| Initial image `18cec4c8…c0eef7` | FAILED Ruff with three I001 test-import findings; four static checks passed | `go ahead`: test imports and staged formatter classification; corrected image `62ba733d…5f10a12` passed Build and 145 Checks |
| First Regression on image `62ba733d…5f10a12` | FAILED, 167 passed/two failed in 892.41 s; `Regression-before-regression-fix.json`, SHA-256 `3399fa691c8940d1a7152cf291dcd5cc458c3ae3029aa03467df078b291f7a06` | `Ok go ahead and fix`: Regression-only replay flag 0 and additive 0008 API readiness; no test expectation/identity guard weakened |
| Image `37dea4ee…0f5ff98` | 169 Regression tests passed in 872.26 s; `Regression-before-binding-fix.json`, SHA-256 `e44195dba22f92e73c14a8c0717d05e49fcb34859b8640fdbe9c9789a14d833d` | Existing failed readiness/isolation cases resolved |
| First EngineParity | FAILED at candidate installation, `candidate_definition_conflict`, before comparison; `EngineParity-before-binding-fix.json`, SHA-256 `8e5f4ee7de361a657ce2d3c34e8f8e883082e1eaf2c027aae5c95e68974a17b8` | `Approve the binding fix and complete B2`: separate JSONB/text SQL bindings; canonical bytes, conflict refusal and actual DB guards retained |

Failed runner evidence remains in
`research/out/parity-before-binding-fix/evidence.json`, SHA-256
`8a57afa3f0be7411cf33f78363a4bde756691dcb71c4ef968545efac6d020eb0`.
The original proposed fix is retained as `candidate-binding-proposed.diff`.
No further B2 decision is pending. B2 acceptance, documentation and fixture
cleanup are VERIFIED. Local delivery is limited to the existing codex branch;
native Git commands/results are retained in the delivery journal. M6-A acceptance, B3–B9, B10/B11, push/PR/merge,
normal-app commands/deployment, runtime login and real model/public runtime
calls are NOT RUN in B2. The single M6-A PR remains after B0–B9 acceptance.
The subsequent owner-authorized B1/B2 checkpoint publication is recorded
separately above; it does not accept the remaining milestone.

### B5 — source registry, fetcher, evidence, search and triggers

**Scope and split.** B5 covers R03, R04, R05, the source part of R16, invariant 8
and the §4.1 case "a fetch fails, times out or is rate-limited". The owner split
`EvidenceInjection` between B5 and B6
([decision](../../DECISIONS.md#2026-10-04--owner-assigns-m6-b5-to-a-second-session-with-the-b5b6-split-of-evidenceinjection)):
B5 delivers what needs no definitions v2. It was built in a second session,
beside B4, on `claude/m6-b5-source-registry`.

**IMPLEMENTED** (`services/engine/app/sources/`; no new dependency, no new table):

- **Registry** (`registry.py`). A source version is usable only when its stored
  text, document and hash agree, the code knows that hash, the document passes
  an exact-key validation and the owner's latest approval of that hash is
  `APPROVE`. A request is the registered constant path plus typed integer
  filters; nothing accepts a URL, a host or a path.
- **Transport** (`transport.py`). The M2 technique: resolve the registered host,
  require every answer to be a public unicast address (including what mapped,
  6to4, Teredo and NAT64 forms embed), connect to the checked address while TLS
  and `Host` keep the registered name, no environment proxy, redirect, cookie
  or credential, the registered media type, no content coding, a byte limit by
  declared and actual size, one deadline over DNS, connection and body.
- **Parser and extract** (`parsers.py`). One strict JSON array; supplied times
  kept only as supplied; bounded plain text without markup, scripts, angle
  brackets, control or invisible characters; a revision hash over title,
  extract, whole-body hash and supplied times.
- **Records** (`store.py`). Requests with dedupe slots; at most one immutable
  fetch record per request; immutable items with `published_at`, `updated_at`,
  `received_at` and `available_at` kept apart; an hourly budget per version and
  a back-off per host; lost-worker recovery; a commit-time check of epoch and
  approval, so a result after a revocation is history only.
- **Triggers.** At most one `SOURCE_REVISION` trigger per fetch and symbol,
  carrying every item stored since the previous one. Inside the cooldown the
  trigger is deferred to the first successful fetch after it, so the cooldown
  limits the rate and drops nothing.
- **Search** (`evidence.py`). `plainto_tsquery` over a weighted `simple` vector;
  the cutoff, the typed filters and a join to the source versions the registry
  holds usable are applied before ranking; at most ten results; no count of
  what was hidden. `open_item` refuses hidden, unusable and unknown items
  alike. Artifact search returns labeled references for artifacts with visible
  transitive provenance, never text. `cutoff_now` waits for a publication in
  flight.
- **Service and identity.** `python -m app.sources.worker`, disabled unless
  `ASL_SOURCES_ENABLED=1`; the `source-fetcher` Compose block; the `source`
  database identity; `app.sources.identity`, which enables `asl_source` only
  in an isolated test database.
- **Harness.** `SourcePolicy` and `EvidenceInjection` in `tools/m6/sources.psm1`;
  the unit file joins `Checks`.

**Three changes to migration 0008** (not applied to the normal app; no approval
of either hash exists):

| Change | Before | After |
|---|---|---|
| `RELEASES_BITCOIN_V1` | `2fab5ce79f3fd1f7ea07d9f3aa32fdafef0e5849b192a71c0f959fc31c1e1ba9` | `40a8ee69ba5cc7453d0cc48ae7958202f54e145a5f4b3d112cbd15dc995e7770` |
| `RELEASES_AGAVE_V1` | `41f29e4c00bf98b6b08d4a18e7d85d872fa4898ea78d910ab0c3008b377e2b48` | `f6b322e500cbcb28c1089b27a90a3fe57b47ae49c7a702ed9aaf03dbfb07e750` |
| Function grant | `research_hold_permission_epoch()` to `asl_agent`, `asl_research` | also to `asl_source` |
| Approval guard | No lock | A decision on a `SOURCE_VERSION` takes the publication lock, so it waits for a result being recorded and a later result sees it |

B1 seeded the two source versions without the fields §5.7 names: answer type,
size and time limits, the extract bound, symbol scope, the fetcher's budget,
poll and refresh intervals, back-offs, the trigger cooldown, the rate-limit
policy and the review date. B5 adds them, with `redirects: REFUSED` and a
maximum for `page`, so the owner's exact-hash approval binds them. The values
are PROPOSED engineering defaults, listed in
[CONFIGURATION](../contracts/CONFIGURATION.md#research-envelope--m6); none is measured
against a real answer. The envelope, protocol and grammar hashes are unchanged.

**Review, and the first run.** Run `m6-b5a` (image `a2e5d56e…62f93b5`) passed
every phase: Build, 230 SourcePolicy tests with the probe, 23 EvidenceInjection
tests, 302 Checks, 169 Regression tests in 862.41 s and Migration with 19 schema
tests. An independent read-only review of the new modules then reported eight
defects. Each was checked in the code, fixed and given a test, so `m6-b5a` is
history and the acceptance below is on a fresh run:

1. A publisher time with any character between date and time was accepted and
   stored as given; a NUL or a lone surrogate would then make the database
   refuse every result of that source. Only the exact RFC 3339 form is now a
   time, other text is sanitized, and an answer the database still refuses is
   recorded as one `STORE_FAILED` fetch instead of a request left running.
2. A wait stated on an answer other than a limit (a 503 with `Retry-After`, a
   spent allowance on a 404 or on an unparsable 200) was replaced by the
   shorter back-off. It is now honored on every kind of failure.
3. A repeated owner key or tool call in a later time slot raised a unique
   violation. It now returns its first request, or `IDEMPOTENCY_CONFLICT`.
4. Artifact search limited its candidates before filtering, so newer hidden
   artifacts could crowd out visible ones, and it returned the whole provenance
   object. The scope's rules are now in the candidate query, and only the
   three checked fields are returned.
5. A revocation that did not raise the epoch could commit between the
   fetcher's approval read and its commit. The approval guard now takes the
   publication lock.
6. Search used the approval alone. It now joins the registry's usable set.
7. A void or unclosed script-like element silently hid the rest of an extract.
   A void element no longer hides anything, and an element left open marks
   the extract as shortened.
8. The 200 ms role lock timeout could discard a fetched answer behind a
   reader. Recording a result may now wait three seconds.

**VERIFIED on run `m6-b5b`,** image
`sha256:5cfcf2c911d1380b4217c797ec0991e939eafa94d23224e8405a514b5b9ec51f`
(built 13:29 UTC on 2026-10-04), no skipped test:

| Phase | Result |
|---|---|
| Build | Image build, four static/registry checks and Ruff: exit 0 |
| SourcePolicy | The new Compose block rendered alone with fixture substitutions: one service, `private` and `source_egress` only, both internal in the fixture, the envelope's limits, UID 10001, read-only root, no capability, one secret, no port, volume or dependency. 249 tests passed in 43.29 s (172 unit, 77 transport and database). Runtime probe as `asl_source` in the hardened shape: the unmodified worker resolved the probe source's `.test` name to one private address through the test network's DNS, refused it as `DNS_NOT_PUBLIC` and recorded the refusal; no default route; one secret; root write denied; M1–M4 reads denied. A disabled fetcher idled without connecting |
| EvidenceInjection | 24 tests passed in 29.59 s |
| Checks | 317 tests passed in 7.45 s (the 145 of B2 and B3 plus the 172 new unit tests) |
| Migration | 19 schema tests passed in 17.41 s; populated 0007 to 0008 upgrade, downgrade and re-upgrade, bounded lock retries, old-image fixture workers, dump and restore, downgrade refusal and the accounting, M3 and M4 invariants: VERIFIED |
| Regression | 169 M3 and M4 tests passed in 885.55 s, one existing warning (14:07:05 to 14:22:03 UTC) |

What the tests show, by requirement:

- **R03 and invariant 8.** Against a real TLS server on loopback: the request
  carries the registered name and only the typed filters; sixteen non-public
  or mixed DNS answers are refused before any connection; a certificate for
  another name and an unknown issuer are refused; five redirect statuses to
  four kinds of target are refused with one request and no second lookup;
  an oversized answer is refused by declared and by actual size; a slow header
  and a slow body both end at the deadline; wrong media types, a content
  coding and non-200 answers are refused. Fifty-eight malformed source
  versions, nineteen malformed filter sets and forty-five non-public address
  forms are refused in the unit tests.
- **R05.** The four times are stored apart; an absent, zone-less or unreadable
  publisher time stays null and an asset's update time is not used; a repeated
  answer adds no item and no trigger; an edited release is a new row beside
  the old one; a trigger's dedupe key is unique in the database; items inside
  the cooldown are carried by the next trigger.
- **§4.1.** A failed, timed-out, redirected, oversized, wrong-type or
  unparsable fetch is recorded, spends the budget, stores nothing and creates
  no trigger; a rate-limited poll waits for the stated reset, and a request
  made meanwhile is refused before any network exchange; a wait stated on any
  other failed answer is honored too; requests beyond the budget are refused
  without a network exchange; a back-off covers every source of the host; an
  answer the database refuses is one recorded failure, not a stuck request.
- **Invariant 10.** A changed epoch or a revoked source cancels queued work
  without a network exchange; a result recorded after a revocation is the
  fetch record `LATE_REVOKED` with no item and no trigger. A lost worker's
  request fails once and its late result is fenced.
- **R16 (source part).** `asl_source` has no privilege on any M1–M4 table, on
  `agent_read` or `research_read`, cannot insert an approval, a definition, a
  workflow or a tool call, and cannot write a request as another actor.
- **R04 (ingestion and corpus).** Nine malicious documents and three items
  with hostile addresses pass through the whole pipeline: one registered
  request left the fetcher, nothing named in a document was resolved or
  dialed, no authority-bearing row was added, and the stored text carries no
  markup or invisible character. Search filters by availability and by the
  registry's usable set before ranking; a query is bound and parsed as plain
  terms; items of a revoked source, or of an approved one the registry no
  longer accepts, are not returned; 505 newer hidden artifacts do not crowd a
  visible one out of an artifact search.

**NOT RUN, and where it belongs:**

| Case | Owner |
|---|---|
| `search_evidence` and `request_source_refresh` as dispatched tools, valid and denied per role; a role receiving source or artifact text and being unable to act on its instructions; the completion that returns a refresh to a waiting workflow; the `RESEARCH_V1` cutoff on a completion and on follow-on context; the scheduler that consumes a trigger; `cutoff_now` at workflow start; provenance written into v2 artifacts | B6 (`AgentOffline6`, `DispatcherAuth6`, `AgentFaults6`, and the dispatcher half of `EvidenceInjection`) |
| Source and evidence routes; the revocation route, which must raise the permission epoch in its transaction | B7 |
| Evidence page | B8 |
| Search latency against the declared budget; `SecretScan`; the activation rehearsal, including the main-installation identity step and the secret file | B9 |
| Any fetch of a real feed; the five release fields and the header names that are INFERRED ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m6-b5-source-fetcher-and-search--2026-10-04)) | M6-B, on the owner's activation |
| GitHub CI | Does not start on this repository ([ExecPlan 0016 §8](0016-ci-checks.md#8-progress-and-evidence)) |

| Gate | B5 applicability and result | Evidence / remaining boundary |
|---|---|---|
| Q01 UX | NOT APPLICABLE: no UI change | B8 pages |
| Q02 Accessibility | NOT APPLICABLE: no UI or browser change | No accessibility claim |
| Q03 Correctness | VERIFIED within B5: hashed definitions, typed requests, immutable fetch and evidence records with separate times, revision identity, dedupe and cooldown, cutoff before ranking | Unit, SourcePolicy and EvidenceInjection tests; Regression |
| Q04 Security | VERIFIED within B5: R03, the ingestion and corpus half of R04, the source part of R16; scoped chapter-level ASVS 5.0.0 mapping in [SECURITY](../contracts/SECURITY.md#m6-b5-source-and-evidence-boundary-execplan-0023) | Dispatcher cases B6, routes B7, `SecretScan` B9; the real path NOT RUN |
| Q05 Reliability | VERIFIED: the §4.1 fetch-failure case, budget and back-off, revocation before and after a fetch, a lost worker, fencing by request version | SourcePolicy |
| Q06 Performance | NOT RUN: the search-latency budget is `PerformanceResearch` (B9). B5 bounds the work: ten results, 500 artifact candidates, 100 items an answer, 2 MiB an answer | B9 |
| Q07 Automation | VERIFIED scoped: Build, Checks, Regression, Migration, SourcePolicy and EvidenceInjection in Docker, no skipped test | Remaining §10 phases and GitHub CI NOT RUN |
| Q08 Visibility | VERIFIED: every attempt and refusal is an immutable record with its outcome code and next permitted time; a registry status view; a heartbeat; logs carry identifiers and counts, never source text | Owner pages and routes B7/B8 |
| Q09 Deployment and recovery | VERIFIED: migration 0008 with the amended seeds, the grant and the approval-guard lock passes the populated Migration phase; the new Compose block is validated alone; exact-name Clean of both runs | Normal deployment excluded (B10) |
| Q10 Maintainability | VERIFIED: contracts updated with the code; no new dependency; documentation link check | No official page was re-read in B5, on the owner's instruction; what rests on memory is labeled INFERRED |

### B6 — definitions v2, tools, workflows, waiting, prompts and probes

**Scope.** B6 covers R01, R02, R13, R15, the dispatcher parts of R04, R06 and
R11, invariants 6, 7 and 10 and the three §4.1 cases owned by `AgentFaults6`.
It was built in a Claude Code session on `claude/m6-b6-agent-workflows`, from
`main` at `5da6b90` (the B4 merge, PR #25). Four points the plan left open were
decided by the owner
([decision](../../DECISIONS.md#2026-10-05--m6-b6-definition-generations-schedule-and-ended-shadows)).
Every test used synthetic fixtures and a scripted or recorded provider. No
model was called, no public endpoint was contacted, nothing was approved outside
disposable fixture databases, and no command addressed the normal app.

**IMPLEMENTED** (`services/engine/app/agents/`; no new dependency, no new table):

- **Generations** (`generations.py`). A workflow belongs to the generation of
  its template. The two M5 templates keep definitions v1 unchanged; the five M6
  templates use v2. The worker's start-up check, the runtime profile (version
  2) and the probes cover both.
- **Definitions v2** (`definitions_v2.py`). Catalog v2 with twelve tools, the
  seven of §5.8 added and `request_review` and the three M7 tools absent; four
  new effect classes; role grants v2 following
  [AUTONOMY_MATRIX](../contracts/AUTONOMY_MATRIX.md#m6-research-and-source-controls-approved-contract-execplan-0023);
  templates v2; budgets v2; four prompt definitions. Nine rows are frozen as
  text in migration 0008 and compared with the code by a test.
- **AgentStep schema v2** (`schemas_v2.py`). One strict object with seventeen
  nullable arguments, a flat bounded candidate declaration and four finish
  payloads. Every output is re-validated by the engine's Pydantic model.
- **Tool handlers** (`tools/`): `search_evidence`, `request_source_refresh`,
  `register_candidate`, `request_experiment`, `read_experiment` and v2 forms of
  the three M5 reads, on top of the B3, B4 and B5 modules. A static test walks
  each handler's import graph and fails on the accounting, broker, execution
  store, pilot, activation, replay, owner and research-runner modules.
- **Workflow graph, waiting and scheduler** (`workflows.py`). The five
  templates with their fixed children; the cutoff rules of §5.8; `WAITING_TOOL`
  with the inference slot released; one completion row per queued call and one
  resume; separate running and waiting deadlines; budgets v2 with a child's own
  budget; priority from stored rows; the trigger scheduler for
  `SOURCE_REVISION`, `FOLLOW_ON` and `SCHEDULED_RESEARCH`; the promotion start
  for an `EVIDENCE_READY` candidate.
- **Artifacts v2** (`artifacts_v2.py`). Assessment with an optional research
  question; review of an assessment or of a candidate, bound to the target's
  hash and, for a candidate, to the result hashes; research proposal; promotion
  request. Each stores server-computed provenance.
- **Prompts.** `services/agent-runner/prompts/m6/`: `analyst.v2`,
  `researcher.v1`, `evaluator.v2`, `coordinator.v1`, hashed and copied into the
  engine image beside the M5 prompts. The runner's code, its Dockerfile and the
  egress gateway are unchanged.
- **Probes CP-15 to CP-20** (`probes.py`), in the same run as CP-01 to CP-14,
  judged from recorded rows.
- **Harness.** `AgentOffline6`, `DispatcherAuth6` and `AgentFaults6` in
  `tools/m6/agents.psm1`, with the M5 agent tests and a schema probe through
  the pinned CLI; the B6 half of `EvidenceInjection`; the unit file in `Build`
  and `Checks`.

**Changes outside `app/agents/`,** each needed by the plan's own rules:

| Change | Why |
|---|---|
| `research/bridge.py`: `nominate()` queues the full test of a nominated candidate, once, with the one permitted retry | B3 lets only the research identity request a `FULL` job. The agent worker, which runs the model's requests, must not be able to |
| `research/bridge.py`, `research/stores.py`: the bridge records each store's size and free space once an hour | B3 reserves storage before queueing. The agent worker cannot see the research cluster, so it reserves against the bridge's record and refuses when none is recent |
| `research/shadows.py`: a candidate review is found by the full result's hash in its `results`; a shadow that ends without the evidence minimum retires the candidate | B6 defines the review artifact that B4 left to it; the owner's decision of 2026-10-05 |
| `research/jobs.py`: `request_in` runs a job request inside the caller's transaction | The decision row, the trial and the result of one tool call commit together |
| `research/protocol.py`: `estimate_seconds` | The reservation needs a time estimate; INFERRED from B0's measurement |
| `agents/approvals.py`: the latest approved profile is looked up among profile approvals only | With an envelope or source approval in the table, the newest approval of any kind was taken for the profile's |
| `agents/views.py`: the M5 agent read models accept schema 0008 | They answered `AGENT_SCHEMA_PENDING` on every revision but 0007, so the M5 owner routes could not work on the M6 schema. No route or response shape changed |
| Migration 0008: nine `agent_definitions` seed rows | Definitions v2. Nothing else in the migration changed; it is deployed nowhere |
| `services/engine/Dockerfile`: copies `prompts/m6` | Packaging, as for `prompts/m5` |

**Review, and the first full pass.** Run `m6-b6b` (image
`f8203f38…422f6629`, built 09:26 UTC on 2026-10-05) passed every phase on a
fresh run: Build, Migration with 19 schema tests, 169 Regression tests in
942.29 s, 378 Checks, AgentOffline6 (14 and 84 M5 tests, 11 workflow tests, 61
unit tests and the schema probe), DispatcherAuth6 (11 and 12), AgentFaults6 (11
and 11), EvidenceInjection (24 and 2), SourcePolicy (249), Staging (13),
ShadowSchedule (10), ResearchRunner (15 and 17) and HoldoutIsolation (9). Three
independent read-only reviewers then read that source, each with its own focus:
authorization, holdout and cutoff; the state machine, waiting and concurrency;
definitions, probes, harness and tests. They ran while `m6-b6b` was in
progress and reported 29 findings, 26 of them distinct: 3 high, 9 medium and
14 low. Each was checked in the code. Twenty-four were fixed, each with a test
that fails on the `m6-b6b` code; two were left as the contract states them and
are recorded in §19. So `m6-b6b` is history and the acceptance below is on a
fresh run.

High:

1. **A profile approved before definitions v2 still authorized work.** Nothing
   compared the definition hashes a profile binds with the code's. The M5
   profile, with its record of probes CP-01 to CP-14, could have been used to
   probe, to enable and to run generation-2 workflows. A profile that does not
   bind the code's definitions is now rejected for Probe and Enable
   (`PROFILE_MISMATCH`), removed from the runtime state at the worker's first
   pass, and permits no model step or scheduler start.
2. **Holdout-derived artifacts were marked unrestricted.** An artifact's
   `holdout` and `shadow` flags came only from the tool results its author had
   read. A candidate review whose author read nothing, and every promotion
   request, were stored with both false, so an analyst or a later researcher
   could find them by search and read their full text. The flags now cover
   what the server binds into the artifact, a review takes over its target's
   bounds, and unreadable provenance is treated as restricted.
3. **One step could hold the single inference slot.** A string with U+0000
   passed validation and failed its database insert on every tick until the
   workflow's deadline. Such a step is now rejected as output; a tool handler
   runs in a savepoint and its unexpected failure is one recorded
   `TOOL_FAILED` result; a failing completion, review advance or trigger no
   longer stops the others.

Medium:

4. The job context showed a cutoff in a spelling the step schema rejects for
   `as_of`. Every instant shown to a model is now in the accepted `Z` form.
5. A result's `available_through` was always the cutoff it was asked at, so
   probe CP-18 and one test compared the cutoff with itself. It is now the
   newest availability the result carries.
6. Only CP-19 had a test of its failing branch. Each generation-2 probe now
   has one, and a refused counterpart.
7. The reviewer's procedure used the whole child budget, so one refused finish
   lost the review for good. The target is now in the reviewer's job context.
8. A resumed workflow kept spending running time while higher-priority work
   held the slot and could expire without a step. Displaced time is credited.
9. A workflow the scheduler had queued survived a Disable and started after a
   later Enable. It now carries its permission epoch and is canceled.
10. The bridge queued the full test from a state snapshot, also for a parent
    bound to an older permission epoch. It now requires the current epoch and
    remaining wait time.
11. A full-test retry that could never be recorded left the parent waiting six
    hours. It now ends at once with the review unavailable.
12. A refresh request reused from an earlier epoch, already canceled as
    revoked, failed the new workflow as revoked. Only its own work does that.

Low:

13. Three fixed windows were cut before filtering for actionable rows, so
    requests that never end could hide finished ones. The filters now come
    before the limits.
14. A screening result told a tuning role the gap count of the whole dataset,
    the holdout window included. It is now counted to the role's cutoff.
15. A probe pointed at a real `EVIDENCE_READY` candidate would have recorded a
    promotion. A probe records none.
16. A result under the stored-size bound could still be too large for the next
    prompt and be shown as omitted. It is now refused whole.
17. After a refused first registration nothing told the researcher its
    hypothesis ID. The refusal and the prompt now do.
18. The static import test missed relative and dynamic imports and parent
    packages. It now fails on the first two, follows the third and allows
    three leaf modules of the execution package.
19. TESTING claimed that a test pins the M5 probe wording; it did not. It does
    now, by hash.
20. A phase record did not name its image, and a stale `VERIFIED` record
    survived a later failure. Both are fixed for the agent phases.
21. Several positive paths were never executed: a read reached through a
    search, the view of a real evaluation document and of a real shadow mark,
    a generation-2 feature read, two branches of the definition check. Each
    now runs in a test.
22. A store could be dropped under a research workflow between its jobs. An
    open research workflow now counts as a reference.
23. Probe CP-16 looked only at feature operators and CP-17 counted any
    refusal. CP-16 now asks the real grammar; CP-17 counts experiment tools.
24. `read_artifact` assumed "not holdout" when stored provenance was
    unreadable. It now assumes the most restricted origin.

Left unchanged and recorded in §19: `read_experiment` distinguishes a locked
experiment from an unknown one, as the contract states; and a job canceled
before it ran is final for its input, which is B3's rule.

**VERIFIED on run `m6-b6c`,** image
`sha256:4b49f66765f29e67e7247b6f0898f61290ac6e1f960dfd395c861fb8f610ae5b`
(built 10:46 UTC on 2026-10-05), no skipped test:

| Phase | Result |
|---|---|
| Build | Image build, 8 static and registry checks and Ruff: exit 0 |
| Migration | 19 schema tests passed in 17.62 s; populated 0007 to 0008 upgrade, downgrade to exactly the M5 seed set and re-upgrade, bounded lock retries, old-image fixture workers, dump and restore, downgrade refusal and the accounting, M3 and M4 invariants: VERIFIED |
| Checks | 388 tests passed in 10.96 s (the 317 of B2 to B5 and 71 new unit tests) |
| Regression | 169 M3 and M4 tests passed in 903.60 s, one existing warning (11:10:02 to 11:25:18 UTC) |
| AgentOffline6 | M5 on schema 0008: 14 passed in 45.18 s (`agent_offline`, `agent_runtime`, `agent_replay`) and 84 passed in 36.27 s (schema, API and schemas files). New: 16 workflow tests passed in 57.98 s and 71 unit tests in 7.86 s. Schema probe VERIFIED: the actual schema (111 properties, depth 9, 44 enumeration values, SHA-256 `bb328865…583aa05b`) is transmitted unchanged and strict by Codex CLI 0.159.2 to the loopback mock for both bundled test models, in a container without a network |
| DispatcherAuth6 | M5: 11 passed in 20.86 s. New: 14 passed in 51.81 s |
| AgentFaults6 | M5: 11 passed in 20.64 s. New: 17 passed in 54.80 s |
| EvidenceInjection | 24 passed in 30.36 s (B5 half); 2 passed in 9.74 s (dispatcher half) |
| SourcePolicy | 249 passed in 43.77 s; the Compose review and the runtime probe as in B5 |
| Staging | 13 passed in 84.64 s |
| ShadowSchedule | 10 passed in 45.30 s |
| ResearchRunner | 15 passed in 16.71 s (catalog); 17 passed in 63.99 s (runner) |
| HoldoutIsolation | 9 passed in 3.93 s |

`EngineParity` NOT RUN: B6 changes no file of the shared engine, the strategy
interface or the replay path.

What the tests show, by requirement:

- **R01 and invariant 6.** Every catalog tool is authorized or denied for each
  of the four roles from stored rows alone; each role has one valid and one
  denied call through the real dispatcher, and a denial changes nothing. A step
  that names another role, another generation's schema or another role's
  artifact is rejected. The agent identity holds exactly the grants migration
  0008 lists on the M6 relations and none on M1–M4.
- **R02.** An analyst's refresh of a URL, an unknown or an unapproved source is
  refused without a request row; a citation of an item it was not given is
  refused; an investigation cites what its own completion delivered.
- **R04, dispatcher half.** An analyst that obeys four hostile documents, and
  an evaluator and a researcher that obey an analyst's artifact addressed to
  them, obtain no tool, destination, role or approval: every request is
  refused by code and the authority-bearing tables are unchanged.
- **R06.** Declarations with an unregistered operator, code, SQL, an oversized
  rule set or a value outside the envelope are refused, and each refusal is a
  recorded trial without the refused text.
- **R11, dispatcher half.** A researcher is held to its hypothesis cutoff by
  every tool, by its completion and by artifact search and read; a review or
  promotion built on the holdout is locked for it whatever its author read; a
  follow-on question is not shown to it.
- **R13 and §4.1.** A waiting workflow holds no slot; one completion per call
  and one resume, also with a fenced former lease holder; a revocation while
  work is queued or running, a wait deadline, a completion after a cancel, a
  revocation during a model step, a full test that fails twice or can never be
  retried, a review that never comes, a stopped fetcher, an oversized result
  and an unstorable step each end in a recorded state without a duplicate
  effect.
- **R15 and invariant 7.** A promotion request is one `PENDING` row; every
  identity is refused an approval, and `MAIN_APPROVED` cannot be written. No
  handler can reach the accounting, broker or execution store modules.
- **Invariant 10.** A Disable or a revocation cancels queued triggers, queued
  scheduler workflows, queued jobs and refreshes, and fails waiting workflows;
  late results are history only.
- **Schema v2.** The actual schema is inside the recorded limits and passes
  through the pinned CLI unchanged to the mock; its differences from the B0
  preview are listed in
  [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m6-b6-agentstep-schema-v2-and-queries--2026-10-05).
- **M5.** All five M5 agent test files run on schema 0008 and the B6 code;
  what was updated in place, and why, is in
  [TESTING](../TESTING.md#m6-b6-agent-workflows-and-tools-execplan-0023).

**NOT RUN, and where it belongs:**

| Case | Owner |
|---|---|
| Owner routes for investigations, research, sources, evidence and promotions; the revocation route that raises the permission epoch; OpenAPI and generated types | B7 |
| Pages | B8 |
| Process-level faults with the runner image and a worker container; `ResearchSaturation`, `PilotCoexistence`, `MixedVersion`, `PerformanceResearch`, `SecretScan`, the activation rehearsal | B9 |
| Inert deployment | B10 |
| Any model call: probes CP-01 to CP-20, a real investigation or research chain, the behavior of a real model under schema v2 and budgets v2 | M6-B, on the owner's activation |
| Any fetch of a real feed | M6-B |
| GitHub CI | Does not start on this repository ([ExecPlan 0016 §8](0016-ci-checks.md#8-progress-and-evidence)) |

| Gate | B6 applicability and result | Evidence / remaining boundary |
|---|---|---|
| Q01 UX | NOT APPLICABLE: no UI change | B8 pages |
| Q02 Accessibility | NOT APPLICABLE: no UI or browser change | No accessibility claim |
| Q03 Correctness | VERIFIED within B6: hashed definitions of two generations, a strict re-validated step schema, the code-owned workflow graph, fixed cutoffs, one completion and one resume per queued call, budgets and priority, server-computed provenance | Unit, AgentOffline6, DispatcherAuth6 and AgentFaults6 tests; Regression. Correct behavior of a real model is not claimed |
| Q04 Security | VERIFIED within B6: R01, R02, R15, the dispatcher halves of R04, R06 and R11, invariants 6, 7 and 10; the profile gate; scoped chapter-level ASVS 5.0.0 mapping in [SECURITY](../contracts/SECURITY.md#m6-b6-dispatcher-and-workflow-boundary-execplan-0023) | Three independent reviews, 24 findings fixed. Routes B7, `SecretScan` B9; the real model and source paths NOT RUN |
| Q05 Reliability | VERIFIED: R13 and the three §4.1 cases; isolation of a failing handler, completion, review advance and trigger; bounded waiting in every path | AgentFaults6. Process-level faults with real containers B9 |
| Q06 Performance | NOT RUN: saturation and the performance phases are B9. B6 bounds the work: 12 steps and 10 tool calls a parent, 4 and 3 a child, 3 experiments, 24 parents a day, bounded results and completions, windows of 20 completions, 10 review advances and 20 triggers a pass | B9 |
| Q07 Automation | VERIFIED scoped: Build, Checks, Regression, Migration, AgentOffline6, DispatcherAuth6, AgentFaults6, EvidenceInjection, SourcePolicy, Staging, ShadowSchedule, ResearchRunner and HoldoutIsolation in Docker, no skipped test | Remaining §10 phases and GitHub CI NOT RUN |
| Q08 Visibility | VERIFIED: every decision, result, completion, trigger outcome, refusal and terminal reason is an immutable or guarded row with a stable code; structured logs carry identifiers and codes, never source or model text | Owner pages and routes B7/B8 |
| Q09 Deployment and recovery | VERIFIED: migration 0008 with nine more seed rows passes the populated Migration phase, including the downgrade to exactly the M5 seed set; no Compose, runner or gateway change; exact-name Clean of every run | Normal deployment excluded (B10). After deployment the M5 profile is unusable until the owner approves a new one |
| Q10 Maintainability | VERIFIED: contracts updated with the code; no new dependency; official pages read and recorded, with what could not be re-read labeled INFERRED; documentation link check | The generation split keeps M5 code paths unchanged; B7 must replace the M5-only budget figures in the owner read models |

### B7 — owner API, OpenAPI and generated types

**Scope.** B7 covers the routes of §5.9, the route halves of R15 and of
invariants 7 and 10, the items B5 and B6 left for it (the source and evidence
routes, the revocation route that raises the permission epoch in its own
transaction, the owner read models that showed M5-only budgets), `SystemStatus`
with `research` and `sources`, the OpenAPI document and the generated web
types. It was built in a Claude Code session on `claude/m6-b7-owner-api`, from
`main` at `d1f8d88` (the merge of PR #27). Three points were decided by the
owner before any code was written
([decision](../../DECISIONS.md#2026-10-05--m6-b7-experiment-read-codes-canceled-jobs-and-rejected-promotions)).
Every test used a synthetic owner, fixture data, a scripted model on the
recorded provider and the loopback mock source. No model was called, the
application contacted no public endpoint, nothing was approved outside
disposable fixture databases, and no command addressed the normal app.

**IMPLEMENTED** (no new dependency, no new table, migration 0008 unchanged):

- **Routes** (`services/engine/app/main.py`). The eleven reads and three owner
  requests of §5.9, and four routes beyond it without which a page cannot
  work: two key lookups, the experiment detail and one cell of a result. The
  contract is in
  [API_CONTRACTS](../contracts/API_CONTRACTS.md#m6-owner-routes-execplan-0023-b7). Each
  has the dual identity, the Host allowlist, a strict query, the 8 KiB cap and
  `no-store`. `POST /v1/agent-workflows` takes one of four strict bodies chosen
  by `template_id`; `POST /v1/agent-approvals` takes the three M6 target kinds.
- **Read models** (`app/research/views.py`, `app/sources/views.py`, new). The
  research status with the envelope's canonical text, hypotheses, candidates
  with their lifecycle, the trial ledger, a job with its result per cell, one
  cell's evaluation document, datasets with their holdout counts, shadows with
  their latest mark, promotions with the owner's decision; sources with their
  registry state and canonical definition, evidence items and one item with
  its extract. Lists are keyset pages of at most 100 rows.
- **Owner requests** (`app/research/controls.py`, `app/sources/controls.py`,
  new). A job cancel and a shadow stop are one immutable value on the row; an
  owner refresh is one request row. Each is applied by the identity that owns
  the row.
- **Approvals** (`app/agents/approvals.py`). The envelope and a source version
  by exact hash, with the epoch raised in the transaction of a revocation; a
  promotion by exact hash, `REJECT` only. One advisory lock and one key lookup
  across every owner store of M5 and M6.
- **Owner starts** (`app/agents/controls.py`). The three M6 templates whose
  definitions name the owner as a starter, each with its registered
  parameters.
- **Agent read models** (`app/agents/views.py`). A workflow's budget comes
  from its own generation; the runtime view adds `budgets_v2`; a queued call
  shows its completion; generation-2 results, completions and artifacts show
  server-computed provenance.
- **`SystemStatus`** gains `research` and `sources`, from recorded facts.
- **OpenAPI and types.** `services/engine/openapi.json` and
  `apps/web/src/generated/api.ts`, generated by the `Generate` phase. The web
  change is limited to schemas that accept both rollout shapes
  (`src/system/status.schema.ts`, `src/agents/schemas.ts`) and their tests.
- **Harness.** `Generate` and the web contract part of `Checks` in
  `tools/m6/api.psm1`; `ApiAuth` in `tools/m6/agents.psm1`; `Clean` removes the
  run's web tool image.

**Changes outside the API layer,** each needed by an owner decision, by a
review finding or by the plan's own rules:

| Change | Why |
|---|---|
| `agents/workflows.py`: `apply_promotion_decisions`, called from the orchestrator's tick with its failure isolated | The owner's decision of 2026-10-05: SYSTEM applies a rejection to the promotion and its candidate. Migration 0008 lets only the agent identity move a promotion |
| `agents/approvals.py`: a target ID must be spelled as the stored row spells it, also for a runtime profile | A state is looked up by that spelling. INFERRED from the M5 code: an approval sent with another spelling was recorded and authorized nothing |
| `research/jobs.py`: a job canceled for an owner request records `OWNER_CANCEL` (B3 code) | Review finding: it recorded `CAPABILITY_REVOKED`, and the waiting workflow ended as revoked although nothing was |
| `research/jobs.py`: the trial row of a request records the kind that was asked for | Review finding: a refused full test has no job, so the ledger could not mark it as resting on the holdout |
| `research/shadows.py`: a shadow with a recorded stop request takes no further mark (B4 code) | Review finding: a result delivered before the stop was applied could become the mark that made the candidate `EVIDENCE_READY` |
| `tests/test_api.py`: the two new `SystemStatus` fields | The M0 test pins the exact shape |
| `tools/m6-acceptance.ps1`: `Checks` reserves 18 minutes instead of 8, `ApiAuth` 17 | `Checks` also runs the web checks; `ApiAuth`'s three command limits add up to 13 minutes |

**The first full pass.** Run `m6-b7b` (image
`sha256:781d371f392dc2e51fa80c3728f4e71aa6a3b4a488f0c13eb2b6c699c5f8d492`,
base commit `d1f8d88`, 32 uncommitted entries), 16:22 to 17:18 UTC on
2026-10-05. Every phase passed without a skip and without a failed or
superseded record. This is the code the two reviews read; it is history, not
acceptance.

| Phase (UTC) | OBSERVED on `m6-b7b` |
|---|---|
| Build 16:22 | Image built; 8 static tests; Ruff clean |
| AgentOffline6 16:22–16:25 | M5: 14 and 84. New: 16 and 82 unit tests. Schema probe passed |
| Regression 16:25–16:41 | 169 M3 and M4 tests in 909.56 s |
| HoldoutIsolation 16:41 | 9 |
| EvidenceInjection 16:41–16:42 | 24 and 2 |
| Generate 16:42 | No drift |
| Checks 17:07–17:08 (waited for its window) | 399 engine tests; web: generated-type check, typecheck, lint, 50 unit tests, format |
| DispatcherAuth6 17:08–17:09 | 11 and 14 |
| AgentFaults6 17:09–17:11 | 11 and 17 |
| SourcePolicy 17:11–17:12 | 249 |
| Staging 17:12–17:14 | 13 |
| ShadowSchedule 17:14–17:15 | 10 |
| ResearchRunner 17:15–17:16 | 15 and 17 |
| ApiAuth 17:16–17:18 | 5 (M0 routes), 5 (M5 API), 12 (M6 API) |

Before it, authoring run `m6-b7a` (history) was built six times. Its
development checks found a model name defined twice in `app/main.py`, which
replaced the M4 experiment type in the generated file; the M6 models were
renamed and a pure test now fails on any class, function or alias defined
twice in that module.

**Independent review.** Two read-only reviews by separate agents, started
while the first pass was still running and given the code, not conclusions:
one of the routes (authorization, session handling, strict bodies,
idempotency, locking), one of the read models and the harness. Neither edited,
built or ran anything. Neither found a path by which holdout or shadow data
reaches a tuning role, a credential or session value in a read model, or a
route that writes beyond its grants; neither rated a finding high.

| Finding | What changed, and its test |
|---|---|
| Medium. An owner's cancel of a job was recorded as `CAPABILITY_REVOKED`, so the waiting research workflow ended `FAILED` as revoked | `OWNER_CANCEL`; the workflow is resumed by its `CANCELED` completion. Tests: the API test drives a waiting workflow through a cancel, and a dispatched job whose late result is history; the bridge's own cancel test asserts the reason |
| Low. A result delivered after a recorded shadow stop, before the bridge applied it, became a mark | `record_mark` returns for a shadow with a stop request. Test: the shadow suite's final-advance test in a second variant with the stop recorded first |
| Low. The owner start route answered a lock timeout with an unhandled error | `503 TRY_AGAIN`. Test: every mutation of both milestones while another transaction holds the owner lock |
| Low. Integers of the new bodies were coerced; the new mutations ignored a query string | Strict integers and a strict query. Test: `true`, `"1"`, `1.0` and `?force=1` refused, and the fields of each new body read from the published schema |
| Low. `409 REFRESH_ALREADY_QUEUED` was also the answer when the equal request had finished | Renamed `REFRESH_INTERVAL_ACTIVE`, and the contract says what it means |
| Medium. A candidate review's bound target (the hypothesis statement, the declaration and figures counted over the holdout) was shown unmarked in every workflow summary | References only, marked `holdout` and `locked_for`, for that template only. Unit and API tests |
| Medium. Every generation-1 (M5) tool result was shown as holdout and shadow material | Provenance is decided by the envelope's own generation; M5 results show none. Unit test with a real M5 envelope; API test with an M5 workflow |
| Medium. `sources` read `unavailable` after a refresh that was refused before anything was sent | Health follows the last request that was sent; `last_attempt` is shown. Test with a spent budget, with two sources (`degraded`), and with a failed attempt |
| Medium. `research` read `idle` while the bridge recorded only refused passes, and `running` for a job a stopped bridge left behind; the refusal was in no read model | Status requires a storage observation, asked before the jobs; the newest refused pass is shown per store. API test |
| Medium (labels, no leak). Holdout-derived summary fields carried no mark | Marks on a hypothesis's and a dataset's holdout figures, a candidate and its events, ledger rows and artifact references. Unit and API tests |
| Medium. `Generate` and the web checks compared an image with a working tree that could have changed after Build, in either direction | Both require the product source to equal the Build record and record its digest; the web checks require `Generate`'s engine image to be the current Build's; a run that rewrote generated files cannot verify afterwards |
| Low. A slow read, and a cursor beyond a sequence's range, ended as unhandled errors | `503 TRY_AGAIN` on every M6 read; `422 INVALID_CURSOR`. API tests |
| Low. The `Generate` record said no public endpoint was contacted, although its image build downloads packages when not cached | The record now says so |
| Test gaps: the epoch increment in the revocation's transaction, the owner lock on every mutation, the profile ID spelling, the branch that refuses a request when the row moved, identity checks on the detail and key routes, `503` before 0008 for every kind and template, a web test with an M6-shaped payload | Tests added for each |

Left as recorded in §19, each rated low: the lock order between a source
revocation and the agent worker, a row another database identity could shape
like an owner request, the coexistence of an owner-started and a
SYSTEM-started promotion workflow, the coercion kept by the M4 and M5 bodies,
and read models that are not indexed for growth.

**After the fixes.** Authoring run `m6-b7c` (history): Build; the M6 API file
with 21 tests passed; the same new file run against the first pass's image
gave 11 failed and 10 passed, the failures being the review fixes and the 10
others unchanged behavior or coverage that was missing; `Staging` and
`ShadowSchedule` passed; `Generate` rewrote both generated files (36 lines
added to the types, none removed) and failed as it must; the five web checks
passed on the regenerated types in the run's tool image (52 unit tests); 154
tests of the B6 agent files and 10 of the M0 and M5 API files passed. The
shadow suite's new variant was not run against the code before the fix.

**First acceptance attempt (failed, history).** Fresh run `m6-b7d`, 21:47 to
22:10 UTC: Build, `Generate` (no difference, on 430 product-source files
equal to the Build record) and `Checks` (407 engine tests and the five web
checks) passed. `AgentOffline6` failed in one of the 14 M5 offline tests,
`test_activation_discovery_probes_verification_enable_and_drift`, with
`Fenced: LEASE_LOST`, and the sequence stopped. OBSERVED cause: the test
builds one orchestrator, whose lease lasts ten seconds, and runs all twenty
probes on it without the renewal the worker makes every two seconds. Six runs
of the test alone took 9.61 to 10.41 s and the three over ten seconds failed.
The test helpers now build an orchestrator that renews its lease before each
tick (`Kept` in `tests/m5_agents.py`); a lease another holder took, or one
that ran out, is still not renewed, so the fencing tests are unchanged. Eight
runs with that helper took 9.10 to 10.76 s and passed. No product file
changed. INFERRED, not measured: B6's six further probes and B7's one read per
orchestrator tick together brought the test to the length of one lease.

**VERIFIED on run `m6-b7e`,** image
`sha256:f59c124a244c273a613906588571e3e593726164b778c5e2ddddea3bbb8d4963`,
base commit `d1f8d88` with 44 uncommitted entries (the B7 tree), 22:17 to
23:10 UTC on 2026-10-05. A fresh run on the final source: one image, every
phase passed, no skipped test, no failed or superseded record.

| Phase (UTC) | VERIFIED on `m6-b7e` |
|---|---|
| Build 22:17 | Image built; 8 static tests; Ruff clean |
| Generate 22:17 | The product source equals the Build record (430 files); the OpenAPI document and the types generated from the image equal the files in the tree |
| Checks 22:17–22:18 | 407 engine tests. Web, in the tool image `Generate` verified, without a network: generated-type check, typecheck, lint, 52 unit tests, format |
| AgentOffline6 22:18–22:22 | M5: 14 and 84. New: 16, and 90 unit tests. Schema probe through the pinned CLI passed |
| ApiAuth 22:22–22:24 | 5 (M0 routes), 5 (M5 API), 21 (M6 API) |
| Staging 22:24–22:26 | 13 |
| ShadowSchedule 22:26–22:27 | 11 |
| ResearchRunner 22:27–22:29 | 15 and 17 |
| Regression 22:29–22:44 | 169 M3 and M4 tests in 921.96 s |
| SourcePolicy 22:44–22:45 | 249 |
| EvidenceInjection 22:45–22:46 | 24 and 2 |
| HoldoutIsolation 22:46–22:47 | 9 |
| DispatcherAuth6 23:07–23:08 (waited for its window) | 11 and 14 |
| AgentFaults6 23:08–23:10 | 11 and 17 |

What the evidence covers, by requirement:

- **§5.9, the route contract.** Every M6 route refuses a request without the
  service key, without the owner session and with a session alone, another
  `Host`, an unknown query parameter and an oversized or loosely typed body.
  The set of M6 routes that write is asserted exactly: three.
- **R15 and invariant 7.** A promotion takes `REJECT` only, by the API's check
  and by the database guard; the rejection is applied once by the worker's
  pass, with the owner's record as gate evidence; `MAIN_APPROVED` is never
  written and no route approves.
- **Invariant 10.** A revocation of the envelope or of a source version raises
  the epoch in the transaction that records it: when the epoch cannot be
  raised, no decision is recorded. The queued refresh and the queued job are
  then canceled by the identities that own them.
- **Requests, not effects.** A cancel, a stop and a refresh are recorded by
  the API identity and applied by another; the statements with which the API
  identity would apply one itself are refused by the database.
- **Idempotency.** One key names one request of one kind across every owner
  store; while another transaction holds the owner lock every mutation answers
  `503 TRY_AGAIN` and records nothing.
- **§5.5, what the owner is shown.** A research chain through the full test
  and its review: every attempt listed, and what rests on the holdout marked
  in details and in summaries. A generation-1 workflow shows no bounds.
- **Rollout.** Every M6 route, approval kind and template answers
  `503 RESEARCH_SCHEMA_PENDING` when migration 0008 is reported absent, and
  the web schemas parse the shapes from before and after B7.
- **The generated contract.** The committed OpenAPI document and types are
  what the accepted image generates, on source that is the source it was
  built from.
- **M5 and earlier.** The five M5 agent test files, the M5 API file and the
  M0 route file run in these phases on the B7 code.

**Cleanup.** Runs `m6-b7a` to `m6-b7e` were cleaned by exact name at 23:15 to
23:16 UTC, 59 resources in all, after their evidence was recorded; the phase
verified each absence. No `asl-m6-*` container, image, volume or network
remains, the evidence files are retained, and the normal app was not touched.

**NOT RUN, and where it belongs:**

| Not run | Why, and where |
|---|---|
| `Migration` | Migration 0008, its seed lines and every grant are unchanged by B7 (`git diff main -- services/engine/alembic` is empty) |
| `EngineParity` | The shared engine and the replay are unchanged |
| The same-origin BFF functions with their Origin and CSRF checks, the pages, a browser | They do not exist before B8. B7 verifies no browser behavior and makes no accessibility claim |
| `PerformanceApi`, `SecretScan`, `MixedVersion`, the saturation and coexistence phases | B9. In particular no M5 route was run against a database that is really at 0007; B7 tests the branch those routes take |
| The M1 and M2 route tests | No M6 phase selects them; B7 changes none of their routes |
| A model call, a public source, GitHub CI | No model and no public endpoint by the batch's rules; this repository runs no CI for the branch |
| Deployment, activation, any approval | B10 and M6-B. The normal app was not addressed |
| The new shadow-suite variant against the code before its fix | Only run on the fixed code |

**Q01–Q10 for B7:**

| Gate | Result | Left for |
|---|---|---|
| Q01 UX | NOT APPLICABLE: no page. The read models carry what a page needs to label state, consequences and untrusted text | B8 pages |
| Q02 Accessibility | NOT APPLICABLE: no UI or browser change | No accessibility claim |
| Q03 Correctness | VERIFIED within B7: exact-hash approvals with their state rules, idempotency by key across every owner store, requests that only the owning identity applies, keyset pages, the status derivations from recorded facts | B9 for the full regression |
| Q04 Security | VERIFIED within B7: dual identity, Host allowlist, strict bodies and queries, the size cap, `no-store`; R15 and invariant 7 (a promotion can only be rejected), invariant 10 (a revocation raises the epoch in its transaction); what the API identity cannot write; marks on what rests on the holdout; an independent review with its findings fixed. Scoped chapter-level ASVS 5.0.0 mapping in [SECURITY](../contracts/SECURITY.md#m6-b7-owner-api-boundary-execplan-0023) | BFF Origin and CSRF checks: B8. Secret scan: B9 |
| Q05 Reliability | VERIFIED: a lock or statement timeout answers `503 TRY_AGAIN` and records nothing, on mutations and reads; the status route cannot fail on the two new fields; `503 RESEARCH_SCHEMA_PENDING` before migration 0008 | Process-level faults: B9 |
| Q06 Performance | NOT RUN. Responses are bounded (100 rows, one cell at a time); the read models are not indexed for growth (§19) | `PerformanceApi`: B9 |
| Q07 Automation | VERIFIED scoped: the phases of the table above on one image, with `Generate` and the web checks bound to the built source | Full Build and browser checks: B8 and B9 |
| Q08 Visibility | VERIFIED: every attempt, refusal, request, decision and its application is a row with a stable code and is in a read model; structured request logs carry no body | Pages: B8 |
| Q09 Deployment and recovery | VERIFIED scoped: no schema change; both rollout shapes parse in the web schemas; the web is deployed before the API | The deployment itself: B10 |
| Q10 Maintainability | VERIFIED: contracts updated with the code; no new dependency; official pages read and recorded with what was not read verbatim labeled; one name per model enforced by a test | — |

### B8 — owner pages and same-origin functions

**Scope.** B8 covers the pages of §5.9 and the same-origin server functions
behind them, the two browser phases `BrowserResearch` and
`BrowserResearchError`, and the web build. It was built in a Claude Code
session on `claude/m6-b8-owner-pages`, from `main` at `2043fc0` (the merge of
PR #28). Six points were decided by the owner before any code was written, and
two B7 behaviors §19 had left open were decided the same day
([decisions](../../DECISIONS.md#2026-10-06--m6-b8-skill-loading-consequence-lists-navigation-detail-routes-refresh-intervals-and-the-state-before-migration-0008)).
Every test used a synthetic owner, fixture data, a scripted model on the
recorded provider and the loopback mock source. No model was called, the
application contacted no public endpoint, nothing was approved outside
disposable fixture databases, and no command addressed the normal app.

**IMPLEMENTED** (no new dependency, primitive, table, route, grant or
migration):

- **Pages** (`apps/web/src/research/`, five new route files). `/evidence` and
  one item; `/research` with its views (overview, hypotheses, candidates,
  trials, shadows, datasets); one candidate; one experiment with one result
  cell at a time in the M4 report view. The contract is in
  [FRONTEND](../contracts/FRONTEND.md#m6-research-and-evidence-pages-execplan-0023-b8).
- **Existing pages.** Approvals gains the "Research and sources" section
  below the unchanged M4 section; the Agents start dialog offers the four
  registered templates and the profile diff is grouped; the workflow page
  marks what rests on the holdout or a shadow; System shows the two M6 rows;
  the navigation gains Research and Evidence.
- **Server functions** (`src/research/research.functions.ts`,
  `research.server.ts`). Fourteen reads, one key lookup and three mutations,
  each behind the Host and CSRF middleware of `src/start.ts`, with strict
  inputs and strict response schemas (`schemas.ts`). The boundary is in
  [SECURITY](../contracts/SECURITY.md#m6-b8-owner-pages-and-same-origin-functions-execplan-0023).
- **API, additive only** (`app/agents/approvals.py`, the two view modules,
  `app/main.py`). `decision_consequences` on the envelope, each source version
  and each promotion, and `refresh_consequences` on each source version:
  code-owned lists a page states before the owner confirms. The OpenAPI
  document and the web types were regenerated by `Generate`.
- **Fixture** (`services/engine/tests/m6_browser_fixture.py`). `seed` writes a
  labeled SYNTHETIC state through the real code paths, with real replays for
  the results; `samples` writes every M6 owner read as the API identity
  answers it. 41 samples are committed beside the web tests.
- **Harness.** `tools/m6/browser.psm1` with the two phases; the browser target
  gains the API, the web and Playwright (`isolation.psm1`); `Checks` runs the
  web build and compares the route tree (`api.psm1`); `Clean` removes the
  three browser images (`cleanup.psm1`). Reservations: `BrowserResearch` 35
  minutes, `BrowserResearchError` 14, `Checks` 22 instead of 18.

**Changes outside the new module,** each needed by §5.9, by a review finding
or by the plan's own rules:

| Change | Why |
|---|---|
| `agents/schemas.ts`, `agents-page.tsx`: the start input is one of four strict shapes; the dialog shows only the chosen template's fields | §5.9: the three M6 templates in the start dialog |
| `agents/agents.server.ts`: `503 RESEARCH_SCHEMA_PENDING` is a refusal, for every mutation that goes through it | Review finding: starting an M6 template before migration 0008 read "Outcome unknown" |
| `agents-page.tsx`: the page's own controls also invalidate the research and system reads | Review finding: Disable and a profile decision move the epoch those reads show |
| `agents/workflow-detail.tsx`: marks from the API's `provenance`, the review target's own fields, and the artifact list | §5.5: what the owner is shown is labeled |
| `experiments/report-view.tsx`: the report body is exported as `ReportDocumentView`; the M4 view wraps it | §5.9: "the M4 report view with research labels". The M4 page draws the same markup |
| `experiments/approvals-page.tsx`: mounts the new section | §5.9. The M4 section's code is otherwise unchanged |
| `e2e/m5.spec.ts`: the start button is now "Start workflow" | The dialog starts four templates, not an assessment. The M5 browser phases were not rerun |
| `tools/m6-acceptance.ps1`: `Checks` reserves 22 minutes | It also runs the web build |

**Before the first pass.** Authoring runs `m6-b8a` and `m6-b8b` (history).
What their development checks found, all fixed before any acceptance run:

- **The fixture.** A first API test of the consequence lists assumed two
  sources; an earlier test's mock source persists, so it asserts at least two.
- **The route tree.** The generator renames a file across devices, which
  fails on a bind mount; the tree is generated by a build on a copy, and
  `Checks` now compares it.
- **The spec.** A sign-in helper returned before the session existed; a
  focus-trap check pressed Tab faster than the primitive redirects focus; a
  publisher's text is stored already stripped of markup, so the browser can
  only show that an address in it is not linked.
- **Layout, from screenshots at 390 px.** Staging gaps as one line each; the
  cell table's link first; a shadow mark's paired hours per baseline; a
  refused staging pass compared with the later pass.

**The first full pass.** Run `m6-b8c` (image
`sha256:923f991aad14b93665ca6c0dcf7ae37ad2f419b5b36216f00dd8e49732251fc3`,
base commit `2043fc0`, 494 product-source files), 08:43 to 09:40 UTC on
2026-10-06. Every phase passed without a skip and without a failed or
superseded record. This is the code the two reviews read; it is history, not
acceptance.

| Phase (UTC) | OBSERVED on `m6-b8c` |
|---|---|
| Build 08:43 | Image built; 8 static tests; Ruff clean |
| SourcePolicy 08:43–08:45 | 249 |
| HoldoutIsolation 08:45 | 9 |
| EvidenceInjection 08:45–08:46 | 24 and 2 |
| Generate 09:07 (waited for its window) | No drift |
| BrowserResearch 09:07–09:09 | 6 browser tests |
| BrowserResearchError 09:09–09:10 | 1 and 1 |
| AgentOffline6 09:10–09:13 | M5: 14 and 84. New: 16, and 90 unit tests |
| Regression 09:13–09:29 | 169 M3 and M4 tests in 931.10 s |
| Checks 09:29–09:30 | 407 engine tests; web: generated-type check, typecheck, lint, 124 unit tests, format, build |
| ApiAuth 09:30–09:32 | 5 (M0 routes), 5 (M5 API), 22 (M6 API) |
| Staging 09:32–09:34 | 13 |
| ShadowSchedule 09:34–09:35 | 11 |
| ResearchRunner 09:35–09:37 | 15 and 17 |
| DispatcherAuth6 09:37–09:39 | 11 and 14 |
| AgentFaults6 09:39–09:40 | 11 and 17 |

**Independent review.** Two read-only reviews by separate agents, started
after the first pass's browser phases had passed and given the code, not
conclusions: one of the server functions and the browser boundary, one of the
pages and their tests. Neither edited, built or ran anything. Neither found an
injection path, a secret in what reaches the browser, a mark on something the
API did not mark, or optimistic state; neither rated a product finding high.
One test finding was rated high.

| Finding | What changed, and its test |
|---|---|
| High (test). The `@error` browser test never reached an M6 page: with the API stopped the route's own loader fails first | A new browser test, signed in, fails every server function and opens each page inside the application: each states its own failed read. The `@error` test is named for what it shows |
| Medium. The revoke lists named waiting generation-2 workflows only; a revocation fails every started workflow of either generation, cancels a model call in flight and what the system queued, and the canceled job is final. A source's approval and a refresh said nothing of the investigations new items start | The lists were rewritten and `refresh_consequences` added. Engine tests drive a revocation through the route against the list, and a fetch with a new item to its trigger. [API_CONTRACTS](../contracts/API_CONTRACTS.md#m6-owner-routes-execplan-0023-b7) corrected |
| Medium. Starting an M6 template before migration 0008 read "Outcome unknown" | The refusal is classified where every mutation passes; the start dialog disables the three templates and says why. Unit tests |
| Medium. Documents named evidence sections that did not exist yet | The sections are written with this batch |
| Medium (test). The CSRF check changed body, headers and Origin at once and left out the caller SameSite=Strict does not stop | The page's own request is sent again unchanged (accepted), then with one header changed: another Origin, cross-site, another port of the same site, another Host, and as a GET. The workflow start is covered. The documents say these are forged requests from the test driver |
| Medium (tests). Marks were mostly unproven: no test drew a page from M6 data | `pages.test.tsx` draws every page from the committed samples and derives each expectation from the sample; the browser opens a candidate review, a full test and a candidate |
| Medium. A stale read still drove actions | A stale read disables every action drawn from it; the alert says so. Unit and browser tests |
| Medium. Opening another confirmation erased an unknown outcome and its key | It stays until resolved and blocks every other confirmation; the request is held by the page, so it survives a change of view. Unit and browser tests |
| Medium (plausible). A read that never succeeded flipped between a skeleton and an alert on every poll | The error stays while it is tried again. Unit and browser tests |
| Medium. Text that overstated: a requested stop read as applied; "reads again by itself" was false on three reads; "not approved" for an invalid version; a retirement stated unconditionally; cancel consequences on ended jobs | Each corrected; the three reads are polled while pending. Unit tests for the cadence and the dialogs |
| Low. Marks worked out by the page from a kind, a purpose or a state; missing on a cell without an evaluation, in the candidate choice and on an artifact before its document arrived | Marks come from the row's own fields only; a row with `locked_for` alone gets the general mark; every cell of a locked job is marked |
| Low. Defaults that read as facts ("not final", "Unset", "None yet", "No holdout partition", "Not locked" with no result) | "Not recorded" or "Not stated"; a count is named for what it counts |
| Low. After a confirmed request focus fell to the document and the outcome could be off screen | Focus moves to the outcome. Browser test |
| Low. The dialog could show a false sentence while closing; a cell link jumped to the top of the page | The dialog keeps its text; the link keeps the scroll position. The second has a browser check, the first has none |
| Low. An upper-case UUID showed the error state for a row that exists; a source named `ALL` shared a cache entry with the unfiltered list | IDs are lower-cased at the boundary; keys hold `null` for no filter. Unit and browser tests |
| Low. A thrown parse error carried private field paths; nested stored JSON is not strict | Fixed sentences for M6 reads. The nested fields are documented as passed through |
| Low. The notice before migration 0008 asserted a cause it cannot know and shared its title with the error state | It says what the API answered, under its own title |
| Low. Headings named only by badges, identical button names, disabled reasons not tied to their button, scroll regions not reachable | Word headings, target in each button's name, `aria-describedby`, named regions. Unit and browser tests |
| Low (tests). A focus assertion that could not fail; controls reached with `.focus()`; an overflow check blind inside cards; a stop assertion satisfied by another card | Tab traversal; the focused look compared with the unfocused one; a clipping check on cards, labels and dialogs; assertions scoped to the card acted on |
| Low (harness). The source was not re-checked after the image build; two selections shared a results directory; a failing record write skipped the stop; nothing tied the samples to the current API | Each fixed; `BrowserResearch` now writes fresh samples from this run's API and runs the sample and page tests on them |

Left as recorded in §19: the missing frame policy, the promotion start that is
not gated on the envelope, the inherited "safe to submit again" answer, the
shared table primitive's scroll container, and the stop list's wording for a
candidate beyond `EVIDENCE_READY`.

**After the fixes.** Development, not acceptance:

- Authoring run `m6-b8b`: Build; `ApiAuth` with 24 M6 API tests; `Generate`
  rewrote both generated files for the new field (14 lines added to the
  types) and failed as it must.
- The web checks on a copy of the source in a tool image: typecheck, lint,
  155 unit tests, format and build, each at exit 0.
- The browser spec on the authoring stack: 7 research tests, then the two
  error selections. Three things were found there. The new error test needs a
  starting page that holds the owner's session read. The new clipping check
  found that the "Show … canonical content" buttons were wider than their
  cards at 390 px; they now wrap. It also found one M4 pilot card that cuts
  off a long definition ID at 390 px; the M4 section is not changed by B8, so
  the check speaks for the M6 section there and the card is in §19.
- The committed samples were written again from the new seed.

**VERIFIED on run `m6-b8d`,** image
`sha256:2bd935cfe17ab463dc59ff2e52f68c3d01530321b4c6871809647df84b4b8ebf`,
base commit `2043fc0` with the B8 tree uncommitted (495 product-source files,
digest `01971be0a260…`), 11:33 to 12:32 UTC on 2026-10-06. A fresh run on the
final source: one engine image, every phase passed, no skipped test, no failed
or superseded record.

| Phase (UTC) | VERIFIED on `m6-b8d` |
|---|---|
| Build 11:33 | Image built; 8 static tests; Ruff clean |
| Generate 11:33 | The product source equals the Build record (495 files); the OpenAPI document and the types generated from the image equal the files in the tree |
| ApiAuth 11:33–11:35 | 5 (M0 routes), 5 (M5 API), 24 (M6 API) |
| Staging 11:35–11:37 | 13 |
| ShadowSchedule 11:37–11:38 | 11 |
| ResearchRunner 11:38–11:40 | 15 and 17 |
| DispatcherAuth6 11:40–11:42 | 11 and 14 |
| AgentFaults6 11:42–11:43 | 11 and 17 |
| SourcePolicy 11:43–11:44 | 249 |
| HoldoutIsolation 11:44–11:45 | 9 |
| EvidenceInjection 11:45 | 24 and 2 |
| BrowserResearch 12:07–12:11 (waited for its window) | The three browser images built from this source, and the source listed again afterwards with the same digest. Database recreated, migrated to head and seeded. 41 fresh API samples; the sample and page tests on them, 61, in the tool image `Generate` verified. Chromium at 390 and 1440 px: 7 tests |
| BrowserResearchError 12:11 | On the images `BrowserResearch` verified. Database at `0007_m5_agent_runtime`: 1 test. Private API stopped: 1 test |
| AgentOffline6 12:11–12:15 | M5: 14 and 84. New: 16, and 90 unit tests. Schema probe through the pinned CLI passed |
| Regression 12:15–12:30 | 169 M3 and M4 tests in 932.27 s |
| Checks 12:30–12:32 | 407 engine tests. Web, in the tool image `Generate` verified, without a network: generated-type check, typecheck, lint, 155 unit tests, format, and the build with the committed route tree equal to the generated one |

What the evidence covers, by requirement:

- **§5.9, the pages.** Each page and view is opened in a browser at both
  widths on a seeded database: sources with their health, evidence items with
  their four times, hypotheses, candidates with their lifecycle, every trial
  including the refused and failed ones, results one cell at a time in the M4
  report view under research labels, shadows, staging gaps and the research
  status; the Approvals section, the start dialog with its four templates, the
  grouped profile diff and the two System rows.
- **States.** Loading, empty, error, stale, pending schema and not found, each
  shown as what it is. Before migration 0008 every M6 page names the pending
  schema and offers no control while the M4 and M5 parts keep working.
- **Labels and marks.** The labels of §5.9 are on the pages. What the API
  marks as holdout, shadow or locked is labeled on every page that shows it,
  drawn from this run's own API responses and compared row by row.
- **Untrusted text.** Publisher and model text is drawn as text: no element
  and no link out of the application comes from it.
- **Requests, not effects.** A refresh, a cancel, a stop and a decision show
  the recorded request and then what the read model says. Each confirmation
  states the API's consequence list first, and the cancel and stop dialogs the
  two owner decisions of 2026-10-06.
- **R15 and invariant 7 in what is drawn.** A promotion has one button,
  Reject, with its reason; no function accepts another action for it.
- **The browser boundary.** The four mutation functions refuse forged callers
  as [SECURITY](../contracts/SECURITY.md#m6-b8-owner-pages-and-same-origin-functions-execplan-0023)
  lists them, with the unchanged request accepted as a control.
- **The API change.** The consequence lists equal the code-owned ones, and a
  revocation driven through the route does what its list states.
- **Earlier batches.** Every phase B7 ran was run again on the B8 code, on one
  image.

**Cleanup.** Runs `m6-b8a` to `m6-b8d` were cleaned by exact name at 12:34 to
12:35 UTC, 73 resources in all (10, 15, 24 and 24), after their evidence was
recorded; the phase verified each absence. No `asl-m6-*` container, image,
volume or network remains, the evidence files are retained, and the normal
app was not touched. The pinned Playwright base image
(`mcr.microsoft.com/playwright:v1.63.0-noble`, named by
`tools/browser/Dockerfile`) was pulled for the browser images and is kept, as
the other pinned base images are: the next browser phase needs it.

**NOT RUN, and where it belongs:**

| Not run | Why, and where |
|---|---|
| `Migration` | Migration 0008, its seed lines and every grant are unchanged by B8 (`git diff main -- services/engine/alembic` is empty) |
| `EngineParity` | The shared engine and the replay are unchanged |
| `PerformanceBrowser`, `PerformanceApi`, `SecretScan`, `MixedVersion`, the saturation and coexistence phases | B9. No SSR, LCP or CLS budget was measured for the new pages |
| A screen reader, a browser other than Chromium | Not used. No screen-reader claim is made |
| The M5 browser phases (`BrowserAgents`, `BrowserAgentsError`) and the M3 and M4 browser phases | No M6 phase selects them. One line of `e2e/m5.spec.ts` was edited for the renamed start button and is unrun; B9's full regression decides whether they join |
| The dialog's text during its closing animation | The unit environment has no exit animation; no browser assertion was written |
| The new tests against the code before its fix | Only run on the fixed code, except where the table above says a test failed first |
| A model call, a public source, GitHub CI | No model and no public endpoint by the batch's rules; this repository runs no CI for the branch |
| Deployment, activation, any approval | B10 and M6-B. The normal app was not addressed |

**Q01–Q10 for B8:**

| Gate | Result | Left for |
|---|---|---|
| Q01 UX | VERIFIED within B8: every page has loading, empty, error, stale, pending and not-found states; labels of §5.9; what the API marks is labeled; a request is shown as recorded and then as the read model says; consequences are stated before each confirmation from the API's lists; both widths | A person's judgment of the pages on real data: the owner, in M6-B |
| Q02 Accessibility | VERIFIED scoped, automated, Chromium: Tab reaches the navigation and the view switch; visible focus; dialogs keep and return focus and fit 390 px; names on repeated buttons; reasons tied to disabled buttons; one `main` and `h1`, captions, contrast of heading and description on five pages | No screen-reader claim. The shared table primitive's scroll container (§19) |
| Q03 Correctness | VERIFIED within B8: strict inputs and response schemas; the samples of this run's API parse whole and the pages draw them; idempotency keys fixed before the call; unknown outcomes resolved by key and never dropped | B9 for the full regression |
| Q04 Security | VERIFIED within B8: the four mutation functions refuse a forged Origin, cross-site and same-site-other-port metadata, another Host and a GET, with a positive control; no secret and no private error text reaches the browser; untrusted text is text; a promotion can only be rejected in what is drawn and in what a function accepts; an independent review with its findings fixed. Scoped chapter-level ASVS 5.0.0 mapping in [SECURITY](../contracts/SECURITY.md#m6-b8-owner-pages-and-same-origin-functions-execplan-0023) | Frame policy (§19). Secret scan: B9 |
| Q05 Reliability | VERIFIED: a failed read is an error and stays one while retried; a failed refresh marks stale values and disables their actions; a pending schema is a named state on every page and a refusal for every mutation | Process-level faults: B9 |
| Q06 Performance | NOT RUN. Lists are one page of 25; one cell is read at a time; polling is 5 s for what the owner waits on and 30 s for lists | `PerformanceBrowser`, `PerformanceApi`: B9 |
| Q07 Automation | VERIFIED scoped: the phases of the table above on one image and one source, with the browser images checked against the recorded source after their build and the web tied to this run's API by fresh samples | B9 |
| Q08 Visibility | VERIFIED: every state, refusal, request and decision the API records is on a page with its stable code; when a value was read is shown; nothing is shown as done before the read model says so | — |
| Q09 Deployment and recovery | VERIFIED scoped: the pages work against a database before migration 0008 and against an API without the routes (named state, no control); the web is deployed before the API | The deployment itself: B10 |
| Q10 Maintainability | VERIFIED: contracts updated with the code; no new dependency or primitive; the official skills read and recorded with what was not re-read labeled; API samples committed and re-derived by a harness step | — |

### B9 — rollout, measurements, faults, scan and report

**State on 2026-10-08, 18:14 UTC: the acceptance evidence for M6-A is VERIFIED on run `m6-b9s`** (the last block
of this section). What follows is the record of the batch in the order it happened.

**State on 2026-10-06, 21:30 UTC: IMPLEMENTED, NOT ACCEPTED.** Every run named here is an authoring run on an
uncommitted tree. No acceptance run exists, and none is started before the owner has answered the open points in
§19. The owner's eight decisions that preceded the code are in
[DECISIONS](../../DECISIONS.md#2026-10-06--m6-b9-phase-content-images-saturation-length-job-measurement-row-counts-quiet-window-lost-store-regression-and-the-read-only-look);
what each phase claims is in
[TESTING](../TESTING.md#m6-b9-rollout-saturation-performance-faults-and-final-acceptance-execplan-0023). Every
test used a synthetic owner, generated market rows, a scripted model on the recorded provider and a loopback mock
source, on isolated Compose projects `asl-m6-<run>-<kind>`. No model was called and no public source was fetched.
The only commands that addressed the normal app were the approved read-only readings described below.

**What was built.**
- Harness: `tools/m6/rollout.psm1`, `performance.psm1`, `faults.psm1`, `regression.psm1`, `report.psm1`; four
  product target kinds (`pilot`, `rehearsal`, `saturation`, `regression`) that run the product `compose.yaml`
  under their own project, env file, secrets and subnets; one record writer for every phase.
- Owner scripts: `tools/m6-deploy.ps1`, `tools/research-activate.ps1`, `tools/research-deactivate.ps1`,
  `tools/m6-pilot-check.ps1`, `tools/lib/Research.psm1`.
- Engine: `app/research/identity.py` and the one-shot `research-admin` service; the store-loss journal and the
  owner's replacement command; the two product fixes and the provisional schema change below.

**Authoring runs, 2026-10-06 (UTC).**

| Run | Build | What ran | Result |
|---|---|---|---|
| `m6-b9obs` | none | B0 observer, read-only, 13:48:37–13:49:40 | OBSERVED: nine normal containers, no identity difference in three samples |
| `m6-b9a` | 14:07 | `PilotCoexistence`, first form | FAILED on harness defects (Compose created missing secret files as directories) |
| `m6-b9b` | 14:18 | `MixedVersion` 14:23–14:28; `PilotCoexistence` | `MixedVersion` passed in its first form; `PilotCoexistence` FAILED on three wrong checks of the harness |
| `m6-b9c` | 15:14 | `PilotCoexistence` | FAILED: a helper refused to wait longer than thirty minutes |
| `m6-b9d` | 16:10 | `PerformanceApi` | FAILED: the row clone broke a table check (two clock readings in one row) |
| `m6-b9e` | 16:17 | `ShadowSchedule`, `ResearchRunner`, `Staging`, `HoldoutIsolation`, `SourcePolicy`, `EvidenceInjection`; `PerformanceApi` | the six passed; `PerformanceApi` stopped by hand after its clone ran over twelve minutes (one function call a column) |
| `m6-b9f` | 17:07 | rehearsal (first form): a first attempt FAILED at 17:14 (the stopped runner container still held the cluster volume), the second passed 17:18–17:27; `Generate`; `Checks` (engine 407 tests, web 155 tests in 18 files); `PilotCoexistence` 17:31–18:08; `BrowserResearch`, `BrowserResearchError`, `Migration`, `EngineParity`, `AgentOffline6`, `DispatcherAuth6`, `ApiAuth`; `BrowserRegression` | all passed except `BrowserRegression`: one M5 locator matched two elements (test fixed, no page changed) |
| `m6-b9g` | never | prepared only | ten phases were started against it by a defect of the scratch runner and failed for the missing Build; the run was abandoned |
| `m6-b9h` | 19:07 | `Generate`, `Checks`; rehearsal (extended); `BrowserResearch`, `BrowserResearchError`, `BrowserRegression`; `PerformanceApi`; `MixedVersion`; `Staging`, `ShadowSchedule`, `ResearchRunner`, `HoldoutIsolation`, `SourcePolicy`, `EvidenceInjection`, `DispatcherAuth6`, `ApiAuth`, `Migration`, `EngineParity` | rehearsal FAILED in the first deployment's preflight (Compose did not list the market stand-in: it carried no config-hash label); `PerformanceApi` FAILED on its budget (below); the others passed |
| `m6-b9i` | 20:07 | rehearsal (extended) 20:07–20:25; `Generate`, `Checks`, `Migration`, `ApiAuth`, `Staging`, `ShadowSchedule`, `ResearchRunner`, `HoldoutIsolation`, `SourcePolicy`, `EvidenceInjection`, `DispatcherAuth6`, `EngineParity`, `BrowserResearch`, `BrowserResearchError`, `PerformanceApi`; `PerformanceBrowser`; `BrowserRegression` | all passed up to `PerformanceApi`; `PerformanceBrowser` FAILED on its own row lookup (an ambiguous column; fixed, not rerun); `BrowserRegression` was interrupted when the pilot watch stopped the run at 21:18:38 |

NOT RUN to the end on any run: `ResearchSaturation`, `PerformanceResearch`, the process part of `AgentFaults6`,
`SecretScan`, `Report`. `Report` was started once on `m6-b9f` to exercise its checks; it refused that run for the
right reasons (missing phases, 39 uncommitted changes at its Build, 23 files changed since its Build).

**The extended rehearsal (`m6-b9i`, VERIFIED 20:07:31–20:25:52).** Every script call carried seven shell
variables that must decide nothing (another database name, web port 1, the agents off, both research flags on,
another project and other profiles). The scripts ran with their default image checks, which name the normal
app's images.
- First deployment: its record names the commit and the 20 uncommitted product files of this authoring tree
  (allowed only with `-Rehearsal`); the Docker VM had 1,000,525,991,936 bytes free against a 14,874,291-byte
  database; backup 625,516 bytes; afterwards the runtime read `LOGIN_REQUIRED` with
  `PROFILE_DEFINITIONS_CHANGED`, both flags `0`, no research container, no helper left.
- A second deployment at 0008 was refused and changed nothing; `-Rollback` returned to 0007 through the guarded
  downgrade; an activation at 0007 was refused and created nothing.
- The migration was blocked twice by a session holding `ACCESS SHARE` on `agent_workflows`. Both times the script
  stopped with exit 1 and `STOPPED at stage 'migrate'`, wrote a FAILED record (web and api replaced, five
  migration runs, schema 0007), left the agent worker's container and the `:pre-m6` tags as they were, and named
  both ways out. The blocking session held to the end both times.
- `-Rollback` from that state recreated api and web on their `:pre-m6` images, downgraded nothing and reported
  the agent worker as already on its `:pre-m6` image.
- Run again from the second stopped state, the deployment reached 0008 and created no `:pre-m6` tag again.
- A deactivation before any activation changed nothing and created no secret directory.
- An activation with a read-only env file failed at stage `services`, returned to the deactivated state by
  itself (identities NOLOGIN, `asl_bridge` NOLOGIN, flags `0`, nothing running, volume kept) and reported the
  pilot as before.
- Activation, deactivation, activation: four research secret files, none rewritten; no fetch.
- A job queued at 20:22:45 with the bridge stopped; the cluster's volume removed; after the next activation
  `STORE_LOST` at 20:23:36 and the job `FAILED` (`STORE_UNAVAILABLE`) at the same second without a start; a new
  request `REFUSED` as `STORE_UNAVAILABLE`; a replacement while the services ran refused and nothing recorded;
  then `STORE_REPLACE` 20:24:53, `STORE_DROPPED` 20:24:59 and `_v2` `STORE_CREATED` 20:25:12; the rows recorded
  as staged into the lost store unchanged (last sequence 2176, 5,635 rows).
- The fixture pilot: its two workers, the market stand-in and postgres unchanged; lease epoch 2 held; forward
  checkpoint 682 to 2696; the incident counts of the fixture's own seeding unchanged; no failure line.

**`PilotCoexistence` (`m6-b9f`, VERIFIED 17:31:33–18:08:13, before the market stand-in and the command count
were added).** Window 17:58–18:07: 539 watermark samples inside it, none changed; last staging batch before it at
17:57:55, first after it at 18:07:02; a job requested at 17:58:25 started at 18:07:00.17; 1,082 rows were
published inside the window; the fixture pilot's hourly valuation at 18:00:00.08 VALID and its report at
18:05:10.7; the web rebuild took 8.3 s with no difference in the fixture pilot.

**`PerformanceApi`: one year of rows at the envelope's caps.** The clone took 83.5 s and the database held
436,090,547 bytes: 4,380 jobs (3,504 screenings, 438 full tests, 438 shadow advances) with 3,723 results, 365
research and 365 shadow datasets, 1,000 hypotheses, 5,000 candidates (ten left `VALIDATED`), 110,000 journal
rows, 17,520 fetches, 10,000 evidence items, the M5 measurement's 10,000 workflows. Budget: p95 at most 250 ms
sequential and 500 ms with five readers.

| Measurement | `m6-b9h`, before the schema change | `m6-b9i`, with it | Budget |
|---|---|---|---|
| all 34 routes together, sequential p95 | 281.41 ms | 43.11 ms | 250 ms |
| all 34 routes together, five readers p95 | 1,480.83 ms | 244.55 ms | 500 ms |
| `/v1/research/status` | 369.27 / 2,024.78 ms | 80.17 / 480.51 ms | 250 / 500 ms |
| `/v1/research/datasets` | 315.26 / 1,825.33 ms | 40.09 / 189.06 ms | 250 / 500 ms |
| `/v1/research/datasets?purpose=SHADOW` | 245.50 / 1,385.28 ms | 41.05 / 144.49 ms | 250 / 500 ms |
| `/v1/sources` | 90.25 / 585.91 ms | 26.36 / 204.39 ms | 250 / 500 ms |
| `/v1/system/status` | 78.09 / 697.72 ms | 43.27 / 383.99 ms | 250 / 500 ms |
| cutoff-filtered search over 10,004 items, p95 | not run (harness defect) | 32 ms | 150 ms |

The first measurement was a FAILED phase and was put to the owner before the fix was kept (decision 4). Causes,
read from query plans on the disposable database: `research_staging_runs` had only its primary key and was
scanned whole several times a request (110,007 rows, 48 MB); a dataset's purpose was read out of its manifest,
which unpacks the whole manifest for every dataset (each clone keeps the fixture's 288 gaps, 44 KB); the
datasets page unpacked every manifest before it chose its rows; `source_fetches` had no index for the newest
fetch of a source. The change, PROVISIONAL until the owner answered (on 2026-10-07: it stays in 0008, §19): in migration 0008 a stored generated column
`research_datasets.purpose` and the indexes `research_staging_journal_time`, `research_staging_journal_store`
and `source_fetch_history`; the reads use the column; the datasets page chooses its rows first. Still thin after
it: `/v1/research/status` at 480.51 ms with five readers. One more cause was found afterwards: the status read
compared `completed_at` with the running clock, which no index can serve (13.5 ms a call, twice a request; 0.085
ms with the cutoff read first). That change is in the tree and NOT yet measured.

**Product defects found by the first independent review, fixed with tests.**
- *A job could be sent into a research cluster that was lost and initialized again.* The store was compared with
  the catalog only when it was staged into, hourly and in memory, while a pass relays before it stages and does
  not stage in the quiet window. The bridge now makes the comparison before anything is sent to a store (job,
  full-test request, shadow advance), whenever the store has not been compared by this process, is empty or
  shows less than it showed, and reads recorded losses at its first refresh
  (`tests/test_m6_bridge.py::test_nothing_is_sent_or_staged_into_a_cluster_that_was_initialized_again`, three
  cases, in `Staging`: 18 passed on `m6-b9i`).
- *Staging stopped ten minutes into a long job.* The bridge stages only while the runner's free-space reading is
  at most 600 s old, and the runner published it only between jobs. It now publishes after each lease renewal
  of a running job
  (`tests/test_m6_runner.py::test_the_free_space_reading_is_renewed_while_a_job_runs_and_never_stops_the_lease`,
  in `ResearchRunner`). That staging goes on beside a long job is NOT yet shown on real services:
  `ResearchSaturation` has not run.

**The first independent review** (three read-only reviewers, 17:35–18:00 UTC) gave 29 findings. Closed in the
tree: the rollback tags a second run could move; no way back from a deployment stopped at the migration; pilot
checks that ignored a container's state, the lease and a failed listing; windows checked once; shell variables
that could override the env file; the restore helper's anonymous volume; the store-loss hole above; a secret
scan that could find its own control and several stores it did not read; an activation that did not unwind and
a deactivation that stopped at a missing secret; rehearsal gaps; records that overwrote each other or were
written only on success; a Report that accepted an uncommitted tree, unpinned owner scripts and a scan that ran
early; and the measurement defects reworked in `PerformanceResearch` and `ResearchSaturation` (random job size,
busy share taken from the catalog, staging never shown to continue, the batch bound never measured). A second
review of everything written since is in progress.

**The real pilot on 2026-10-06 (read-only; decision 8).**
- `tools/m6-pilot-check.ps1` could not run before 20:45 UTC: an internal variable collided with its validated
  parameter. No reading was therefore taken around the afternoon's phases.
- Readings at 20:45: the market worker's start time 2026-10-06T15:53:57 and restart count 2 (2026-10-03T05:22:21
  and 0 at 13:48); every other container unchanged; lease epoch 4 held; `EXECUTION_DOWNTIME` 3.
- Market incidents located by counts since an instant: a clock check failure between 12:00 and 13:30; a
  collection gap in 13:50–13:52; a gap and a silent stream in 13:58–14:00; a REST failure in 14:00–14:05; a gap
  and a silent stream twice in 14:52–14:56; a gap in 15:52–15:54 and a gap and a silent stream in 15:54–15:56;
  two gaps and two silent streams in 16:08–16:12. None from 16:12 to 21:25. No `QUEUE_OVERLOAD`.
- The runs' command logs: the last command of an earlier run at 12:35:41, the first B9 command at 14:07:18. The
  first three incidents therefore happened while no isolated test container existed, and isolated runs went on
  from 16:16 to 20:45 without an incident. INFERRED: the tests did not cause them. The cause is NOT KNOWN; the
  worker's log is outside the approved commands.
- `PROTECTION_UNAVAILABLE` rows (a start and an end each time the quote of a symbol with an open position is
  briefly not usable): 484 at 20:45–20:51, 486 at 20:54 with no isolated container running, 488 at 21:18:38
  while `BrowserRegression` ran. A watch that applies decision 8 as written stopped the run on that second pair.
  No test has run since.

**Not run, and why.** The acceptance run and its Report: the open points in §19 come first. `ResearchSaturation`,
`PerformanceResearch`, the process part of `AgentFaults6`, `SecretScan`: stopped by the pilot watch before
they were reached. B10: needs B9's acceptance and the owner's yes.

**Second independent review and its fix round (2026-10-06 21:05 to 2026-10-07 UTC; NO TEST RUN).** Three
read-only reviewers read commit `da01a04`, each with one question: can a phase pass without proving its claim;
are the budgets measured honestly; do the owner scripts fail closed and leave the pilot alone, what does the
secret scan not cover, and are the product changes sound. They ran nothing and gave 34 findings. The fixes are
IMPLEMENTED in the tree and were checked only without a stack:

- the PowerShell parser on every changed script (0 errors);
- `ruff` and byte-compilation of the changed Python files, in one container without a network;
- the scripts' env file and time rules on local files (the harness's own cases: 27 at first, 47 at the end of
  the round);
- `tools/m6-deploy.ps1` against a model of an installation: 11 scenarios and 55 expectations at first, 17 and
  72 at the end of the round, all held. A function
  answers for `docker` in a process that cannot reach Docker. OBSERVED on the model only: it shows which branch
  the script takes and what it says and records, and nothing about Docker, Compose or PostgreSQL. Its first run
  found one defect, fixed: a run that stopped before it had read the `:pre-m6` tags described every service as
  "on another image than :pre-m6".

NOT RUN: every new or changed test, and every phase. Nothing below is evidence until a run exists.

What changed, by the reviewers' question:

- **The owner scripts.**
  - `tools/m6-deploy.ps1` was rewritten around four faults. (1) A replaced service that did not run blocked both
    the next deployment and `-Rollback`, and a recreation that failed was reported as "nothing replaced": the
    rollback now accepts any state of `api`, `web` and the agent worker and treats a release with a service down
    as a repair, and a service counts as replaced from the moment its recreation is asked for. (2) The restore
    rehearsal compared whatever the fingerprint query printed, so the same error text three times passed, and the
    query built one value from a whole table: it is now the row count and the sum of a 64-bit hash per table, read
    in one pass, every read is checked and must be 32 hexadecimal characters. (3) A refused downgrade restarted
    the agent worker with a Compose `start`, which resolves dependencies: it is started by its container ID, the
    downgrade is tried up to five times when it cannot take a lock, and a refusal is told apart from a lock.
    (4) An image name that could not be read was taken for a name that does not exist, and a rollback tag was
    then created from whatever ran: an unreadable name is an error, and a tag is created only from an image the
    caller names in `-ExpectedPreM6Images`, now also for `migrate` and `agent-admin`.
  - Also: a `git` that cannot answer is an error and no longer a clean tree; a run that stops before it replaced
    anything returns the image names it had moved to their `:pre-m6` images; a deployment refuses when the
    execution worker runs and the lease is not held; the image each pilot image name points to is compared around
    the builds; the helper containers have CPU and memory limits and what is left of them is named; the market
    worker's incidents and the age of its newest publication are reported and not judged.
  - The env file is read by one reader that follows Compose (quotes, a comment, `KEY: value`, the last
    assignment) and refuses a key assigned twice, and is written to the resolved path, in every assignment of the
    flag, with every other byte kept, by replacing the file in one step.
  - `tools/research-activate.ps1` begins only between HH:07 and HH:50 UTC, refuses when the lease is not held,
    and unwinds nothing when any one of the three services ran before it. The protected backup always removes its
    dump from the postgres container.
- **The rehearsal and the other rollout phases.** New in `ResearchActivationRehearsal`: the scripts' rules on
  fixed instants and small files; the deploy model; a deployment on a database on which 0008 fails (it must stop
  in its restore rehearsal with nothing replaced and return the image name it moved); a stopped web (deployment
  refused, rollback as a repair); a rollback after research ran (refused at the downgrade, agent worker started
  again); the secret files unchanged by a second activation; a staging period that ended after that activation
  began; the lost job's reason and the absence of a result; the pilot's image names before and after; and every
  script record tied to the call that wrote it. `MixedVersion` compares the web container's image in every state
  and the pilot at the very end. `PilotCoexistence` requires the refusal of a candidate strategy at three places.
  The cluster-restart fault counts only when the job ended failed or on a second attempt.
- **Product.**
  - The bridge read a store before the catalog. A second bridge process (an on-demand advance) could therefore
    take the main bridge's staging between its two reads for a store that is behind, and record `STORE_LOST` for
    a healthy store, which only a replacement undoes. It now reads the store once more before it records a loss.
    The daily work compares the store with the catalog first, and a pass that staged nothing no longer leaves a
    claim that staging has caught up. Two tests.
  - The runner's renewal loop ended at its first failed renewal and took the free-space reading with it, while
    the job went on under its per-batch heartbeat. The reading now goes on. One test.
  - INFERRED, not measured: the replay's quote tracker held every quote it had seen until a step asked for one,
    and a cell that starts later in its dataset takes no step until then. At one quote a second and symbol a cell
    starting 12.6 days in would have held about 2.2 million rows, far above the runner's 768 MiB. The tracker now
    folds the rows it holds beyond 8,192 a symbol and keeps the time from which every folded row is visible; for
    an earlier decision time it declines and the engine reads the database, as it already did for a clock that
    went back. One test compares it with a tracker that holds everything. `EngineParity` does not reach the fold:
    its fixture holds one quote an hour.
  - `research-postgres`, `research-runner` and `research-bridge` had no log limits; they have the limits of the
    other long-running services now.
  - One more status read compared a column with the running clock (`stores.observed_storage`); it reads its
    cutoff first.

**The rest of the fix round (2026-10-07, to 12:30 UTC; NO TEST RUN).** Two helpers worked on separate files
and a third and a fourth read-only review read what they and the implementer had written. Nothing below has
run in a stack.

- **A third review, of the reworked owner scripts** (one read-only reviewer): 13 findings, fixed in the tree.
  A deployment now begins only between HH:15 and HH:35 UTC, so that its backup, restore rehearsal and builds end
  inside the window, and the window is asked again before the builds. A dump of the main database begins only
  between HH:07 and HH:50 UTC and only when the database's disk has room, in the rollback and the activation
  too, and the copy inside the `postgres` container is removed in every case. `migrate` is built once and
  migrates the copy and the installation by one image ID. A run that stops says what the release and the pilot
  look like at that moment, from the tags as they are then, and says that the release is deployed when it is.
  `-Rollback` no longer needs the baseline compose file or `git`. `-Rehearsal` is refused outside an isolated
  project and a pilot tag that a release uses is refused. A helper that cannot be looked for is recorded as not
  read. The env file is replaced with the old file kept under another name until the step is done.
- **The harness** (one helper; read by the implementer). Every phase writes an attempt record with the heavy
  lock held: process, start and end, how it ended, and one digest of the executed tree at its start and at its
  end. `Report` refuses a run in which a phase was started twice, never ended after it issued a command, threw
  or was stopped, has a record without an attempt, or ran on a tree other than the one Build recorded. A phase
  does not start when a harness module on disk is no longer the one its process loaded. No run made before this
  change can pass `Report`: it has no attempt records.
- **The secret scan's database search** (the same helper; read by the implementer). The search with the BusyBox
  `grep` of the PostgreSQL image tries every pattern on every line: with about a thousand patterns and a store of
  millions of lines that is INFERRED to take hours. The database's own container now writes the dump into a
  directory of its data volume, and GNU `grep` of the run's engine runtime image searches it in a second
  container without a network or a capability, with a control file that must be counted exactly once
  ([TESTING](../TESTING.md#m6-b9-rollout-saturation-performance-faults-and-final-acceptance-execplan-0023),
  [DOCKER](../../DOCKER.md)). NOT RUN: the phase has never run to its end in any form.
- **The measurements** (one helper; read by a fourth reviewer, next entry). `ResearchSaturation` judges the
  execution side from its numbers and on every publication of the loaded interval, and names a kill for memory.
  `PerformanceResearch` has eight parts on a 27-day store: the seals and the shadow window are built at the
  bridge's limits, the shadow advance runs after a dense warm-up of 302 hours through the product's own
  `shadows.advance`, the idle-dispatch p95 is derived from measured pass periods and labeled INFERRED, and the
  21-day projections have three parts. `PerformanceApi` holds 5,850 job rows, a ledger of 22,831 rows and
  10,000 evidence items with extracts at the registered cap of 16,384 bytes. `PerformanceBrowser` reads its
  page list from the spec. `Report` judges the new numbers.
- **A fourth review, of those measurements** (one read-only reviewer on the two changed files, 11:30 to 12:05
  UTC): nothing that must fail on a first execution; every caller matches the fixtures' dispatch tables and
  every path `Report` reads is written under that path. Three findings of weight and six smaller ones, fixed in
  the tree except where noted:
  - Once a part's work deadline has passed, every further call throws, and the cleanup of four phases made
    such calls before it stopped its containers: a part that ran into its deadline would have left its
    clusters and services running into the quiet window. The cleanups of `PerformanceResearch`,
    `ResearchSaturation`, `PilotCoexistence` and the process part of `AgentFaults6` now lift the deadline first
    and stop their targets whatever a removal does. The defect was in the code since `3d10fec`. NOT CHECKED:
    whether an authoring run of 2026-10-06 reached a deadline in one of them. No isolated container was running
    at any reading of the read-only series since 2026-10-06 21:25 UTC.
  - The judged projection of the 21-day shadow advance took its read-only rate from the full test. That rate
    is a remainder of the full test's own cells and can put the advance below what its own seconds give (the
    reviewer's example: 3,466 s judged against 3,655 s by the rates assumed in it). The advance is now judged
    with every cell second counted as stepped, from its own measurement only; no read-only rate gives a higher
    figure. The figure with the borrowed rate is recorded and not judged.
  - The share of publications the worker looked at (99 percent) passed a worker that stopped looking for the
    last seventeen seconds. The oldest publication it never looked at is now judged by its age at the end of
    the run, against the engine's freshness bound, in the fixture, in the phase and in `Report`.
  - Smaller: staging beside a long job is required after the job's 660th second, not its 600th, because a pass
    that began before the reading was too old stages for about ten seconds more; the staging rate is cut to a
    whole number and no longer rounded up, and the staging watch's own problems are the phase's problems; a
    call that a deadline ended names the seconds it ran; three texts that described another method than the
    code were corrected (seven of the eight dispatch requests are planned, not eight; the measurement, not
    `shadows.advance`, compares the advance's window with the sealed one; "every publication").
  - Not changed, and listed in §19: a full test whose later cells cost less than their stepped days at the
    first cells' rate gives a negative remainder and fails the phase as not projected; two parts hold limits
    that cannot all be used; nothing bounds how early the heartbeat reader must be ready.
- **Also by the implementer, reading the projection code:** the helper had judged a one-rate figure when a
  job's cells gave no two rates. For an advance that figure is below the one with every second counted as
  stepped, so it could pass a job the three parts would fail; it is recorded and no longer judged.
- **The env file as Compose reads it** (found by the session that corrects the older activation tools, and
  OBSERVED again here; Docker Compose 5.5.1, scratch files rendered with `config`, nothing created). On Windows
  a key in another letter case is the key when the exact spelling is absent: `asl_research_enabled=1` gave
  `${ASL_RESEARCH_ENABLED}` the value 1, and the exact spelling won in either order. A quoted value that does
  not end on its line hid the assignment on the next line. A carriage return without a line feed did not end a
  line. The reader of this batch took the first for an unset flag, so `tools/m6-deploy.ps1` would have reported
  an installation with that line as inert although Compose hands the research services their flag as 1. The
  script starts none of those services, so nothing would have started; its statement that neither flag is 1
  would have been false. That is a defect of this batch's uncommitted reader, found before any run against an
  installation, and fixed: the deployment and the
  activation refuse such a file, the deactivation reads it as Compose does, and the writer rewrites every
  spelling. The deploy model has a scenario for it.
- **A library function does not see a script's error preference when the script is started from a session**
  (OBSERVED in Windows PowerShell 5.1 on scratch files; with `-File` it does). `tools/lib/Research.psm1` sets
  its own. For `tools/lib/Pilot.psm1` this batch had first set it inside `New-ProtectedBackup`, the one library
  function of the M6 scripts in which a failing cmdlet could be passed over; pull request #30, merged into
  `main` on 2026-10-07 and into this branch the same day, sets it for the whole module, and the line inside the
  function was removed as a repetition.
- **Checks of this part of the round, all without a stack:** the parser on all 43 scripts and modules under
  `tools` (0 errors, no byte outside ASCII); `ruff check` on the whole of `app` and `tests` and
  byte-compilation of the changed files, in one container without a network (all checks passed); the env file
  cases (47 held); the deploy model (17 scenarios, 72 expectations, exit 0).
- **`main` merged into the branch (2026-10-07, 13:03 UTC, merge commit `73789b9`, local).** `main` had gained
  pull request #30 as `0f395a9` (VERIFIED read-only: merged at 12:59:54 UTC by the session that wrote it). The
  merge conflicted in STATUS, COMMANDS and DECISIONS only, where both sessions had added entries; all are kept.
  After it, without a stack: the parser on all 44 scripts under `tools`, the env file cases (47), the deploy
  model (17 scenarios, 72 expectations), and `tools/env-file-path-check.ps1` from #30 on the merged tools (12 of
  12 cases; a function stands in for `docker`). That check runs the pilot and agent tools, three of which take
  their backup through this batch's `New-ProtectedBackup`; against a PostgreSQL container that function is
  NOT RUN in its present form.
- **The owner's four decisions of 2026-10-07, about 13:26 UTC, and what was done with them**
  ([DECISIONS](../../DECISIONS.md#2026-10-07--m6-b9-what-stops-a-test-run-beside-the-pilot-the-owner-scripts-and-the-pilots-own-rows-the-schema-change-in-0008-and-the-market-workers-log);
  IMPLEMENTED, NOT RUN in a stack).
  - *What stops a test run beside the pilot.* The rule is `Get-PilotWatchVerdict` and `Get-ReportVerdict` in
    `tools/lib/Research.psm1`, with 31 cases on synthetic readings that the rehearsal runs and counts. The loop
    is `tools/m6-pilot-watch.ps1`, which replaces the scratch watch of 2026-10-06: it reads with the two
    approved read-only scripts, ends by itself, and can only stop the isolated run. That scratch watch had not
    checked the HH:05 report, which decision 8 names; the new one does, once an hour, from one sample of the B0
    observer. OBSERVED by replaying the series with no test running through the rule (local files, no
    installation read): 161 readings, no stop, at most six `PROTECTION_UNAVAILABLE` rows in thirty minutes. The
    reports the observer recorded on 2026-10-06 (created 22 to 24 s after HH:05) pass the report rule, and the
    same list read at 14:10 gives "missing", as it should.
  - *The owner scripts and the pilot's own rows.* `Get-IncidentJudgement` splits what the execution incidents
    gained into what stops and what is reported; both scripts use it, print the reported rows and record them.
    The deploy model has 74 expectations now: `PROTECTION_UNAVAILABLE` rows during a deployment are reported
    and the run completes, a row of another code stops it at its last check, and a run that stopped elsewhere
    names the pilot's own rows without calling them a difference. Its first run of these found a fault of the
    model, not of the script: a check that was meant to tell `PILOT:` from `Pilot:` ignored the letter case.
  - *The schema change.* Nothing to change: it is in 0008 and no longer provisional.
  - *The market worker's log.* Read once, read-only, at 13:27 UTC, for 2026-10-06 13:40 to 16:20 UTC (1,593
    lines). §19 records what it shows: both restarts were the hourly retention canceled by its statement
    timeout, which the worker takes as fatal. Flagged as a separate task; this batch does not touch the worker.
- **Checks after these changes, without a stack:** the parser on all 45 scripts under `tools`, the env file
  cases (47), the pilot rule cases (31) and the deploy model (17 scenarios, 74 expectations, exit 0).

**Authoring run `m6-b9j` (2026-10-07, 13:49 to 18:50 UTC; the tree of commit `2f6a3a7`; stopped by hand).**
The first run of the fix round's code. OBSERVED; isolated projects only; synthetic fixtures; no model call.

- **VERIFIED on their first attempt, sixteen phases:** `Build`, `Generate`, `Checks`,
  `ResearchActivationRehearsal` (21 minutes; 24 steps, no problem; inside it the deploy model with 17 scenarios
  and 74 expectations, 47 env file cases and 31 pilot rule cases), `MixedVersion` (migration 0008 on the live
  database in 0.55 s on its first attempt, the API replaced in 7.5 s), `Migration`, `ApiAuth`, `Staging`,
  `HoldoutIsolation`, `SourcePolicy`, `EvidenceInjection`, `PilotCoexistence` (81 minutes, through the quiet
  window of 15:58), `ShadowSchedule`, `ResearchRunner`, `DispatcherAuth6` and `EngineParity`. This is the first
  time the rewritten owner scripts, the env file reader and writer and the backup's room check ran against
  containers, and the first time the attempt records were written. The in-process part of `AgentFaults6`
  passed too.
- **FAILED, the process part of `AgentFaults6`, after four minutes: a defect of its own fixture.** Its
  `prepare` seeds a market in the catalog from a container whose environment names the research cluster's
  database, and the market fixture's guard compares the two names: `fixtures_require_disposable_asl_m1_database`.
  No case ran. The helper now names the catalog for the seeding, as the other M6 fixtures do. This part had
  never passed before.
- **HUNG, `Regression`, and with it the pass, for two hours and five minutes.** Its first command (the M3 and
  M4 files) passed in fifteen minutes. Its second, the six M0 to M2 files that B9 added and that had never run
  under M6, never ended: `test_api_lock_wait_is_bounded_and_failed_confirmation_can_retry` holds a row lock and
  expects the other session to give up after the API identity's one-second lock timeout, and this target ran
  the files under the migration role, which has none. Two sessions waited on each other in the isolated test
  database, idle. The files now run under the API role, which M5's regression gave them.
- **A defect of the harness itself, older than B9, found by that hang: a call that was cut did not end.** At a
  call's limit the harness ended `docker.exe` alone. For a Compose command that client has a child process,
  which stayed attached to its container and kept the output pipes open, and the harness waited for the pipes:
  until the container ended by itself, or for ever. So a limit was never enforced on an attached Compose run,
  and the phase's deadline with it. Here the phase should have ended at 16:45 UTC; its two containers (a test
  process and a PostgreSQL, both idle at 0.03 and 0.00 percent of a CPU when read at 18:47) stayed up through
  the quiet windows of 16:58 and 17:58, which the window rule exists to prevent. The harness now ends the
  client with every process it started and waits a bounded time for the output. OBSERVED without Docker: a
  call whose child keeps the pipes open returned 5.9 s after its start at a limit of 5 s, with the output read
  so far and no process left; a call that ends by itself is unchanged. NOT RUN in a phase yet.
- **Stopped by hand at 18:50 UTC:** the pass runner was ended, the left Compose client was ended, and
  `tools/m6-acceptance.ps1 -Phase Stop` stopped the run's containers (none running afterwards). NOT RUN in this
  run: `AgentOffline6`, the three browser phases, `PerformanceApi`, `PerformanceBrowser`, `ResearchSaturation`,
  `PerformanceResearch`, `SecretScan`, `Report`.
- **The real pilot beside the run** (`tools/m6-pilot-watch.ps1`, its first use; 50 readings from 13:49 to 18:46
  UTC): no stop. Every normal container kept its identity, the lease stayed at epoch 4 and held, the forward
  checkpoint advanced at every reading, no `PROTECTION_UNAVAILABLE` row and no other execution incident was
  recorded, and the six hourly reports from 13:00 to 18:00 were each created in their HH:05 minute. One
  collection gap was recorded between 14:45 and 14:50 UTC, with `stream_silent` and `provider_rest_unavailable`,
  while `SourcePolicy`, `EvidenceInjection` and the start of `PilotCoexistence` ran; one gap is below the
  owner's burst rule and is recorded, not judged. The estimated minute of the market worker's hourly retention
  passed five times without a restart.
- **Not this run alone on the host.** Another session ran isolated `asl-m2-ret-*` stacks for the market
  worker's retention defect on the same Docker host from 14:07 UTC (a load of 1.8 million rows between 14:10
  and 14:20, lighter work afterwards). Neither harness sees the other's work: the heavy lock is per checkout.
  It was asked to read this run's pass log and to keep its loads out of the measurement phases, none of which
  was reached. No measurement of this run is affected; the collection gap above falls into that session's
  lighter work as well as into this run's.

**Authoring run `m6-b9k`, first part (2026-10-07, 19:11 to 20:13 UTC; Build on the tree of commit `a44ccb0`; stopped by the pilot watch).**
The second run of the fix round's code, with the three harness fixes of `a44ccb0`. OBSERVED; isolated projects
only; synthetic fixtures; no model call. Tools and documents were edited while it ran (commit `85d9adf` and
the watch's rule below), so its `Report` cannot pass: an authoring run.

- **VERIFIED on their first attempt:** `Build`, `Generate`, `Checks` and `Regression`. `Regression` ended in
  17 minutes (19:14 to 19:31 UTC); on `m6-b9j` it had hung for two hours. Its six M0 to M2 files now run under
  the API role.
- **`AgentFaults6`:** its in-process part passed (19:31 to 19:32 UTC). Its process part began in the next
  window, at 20:07:00 UTC. The fault helper's `prepare` passed (two recorded days loaded in 115 s; on `m6-b9j`
  it had failed on the fixture guard), the two services started, the source case ran through its kill, and
  the agent case was waiting for its experiment when the run was stopped at 20:11:47 UTC. The record of that
  attempt is FAILED with "Timed out after 120 s waiting for: the workflow waiting for its experiment", which
  is the stop and not a finding about the product.
- **The stop.** The watch's reading of 20:11:45 UTC, the first after the quiet window, showed the normal
  market worker with start time 2026-10-07T20:01:27.77Z and restart count 3; it had been
  2026-10-06T15:53:57.83Z and 2. Same container, same image. By the rule of that morning the watch wrote the
  difference and ran `-Phase Stop` (exit 0), and the pass runner started nothing more.
- **What was running at 20:01:27 UTC.** Of this run: nothing. It had no container up and issued no Docker
  command from 19:32:51 to 20:07:00 UTC (its command log). The same check over every run of this session for
  the two restarts of 2026-10-06 (13:51:57 and 15:53:56 UTC): no command in progress at either. Of the session
  of the retention fix, by its own account: no load from 19:51:32 to 20:07:08 UTC, one test database up with
  no client, and test files, builds and small-database checks from 19:07 to 19:51 UTC.
- **The pilot at 20:11:39 UTC:** lease epoch 4 held; the forward checkpoint at 2,006,404 and stepping; the
  experiment's events and the execution incidents as at the start of the watch (no `PROTECTION_UNAVAILABLE`
  row in the hour); one `COLLECTION_GAP` on the market side; the SNAPSHOT report of 20:00 in its HH:05 minute.
- **The market worker's log** (one read-only call at 20:18 UTC with the owner's answer of 20:17, for 19:55 to
  20:05 UTC; 212 lines): `market_collection_gap` from 20:01:23.96 to 20:01:24.80 UTC with phase "maintenance";
  `QueryCanceled: canceling statement due to statement timeout` in
  `DELETE FROM market_payloads WHERE id = ANY(payload_ids)`, `asl_prune_market_evidence` line 39, reached from
  `maintain_retention`; `market_worker_fatal UNEXPECTED_EXCEPTION`; then the lease, a new collection, and
  `market_retention_pruned` with 20,460 records. The same failure as on 2026-10-06, for the third time.

**The owner's two decisions of 2026-10-07, about 20:17 UTC, and what was done with them**
([DECISIONS](../../DECISIONS.md#2026-10-07--m6-b9-a-restart-of-the-market-worker-alone-beside-a-test-run-and-its-log)).

- *One log read for each restart of the market worker during B9.* Used once so far, by hand (above). From now
  on the watch issues it: `Read-MarketWorkerLog` in `tools/m6-pilot-watch.ps1`, one `docker logs` call with a
  time range on the container id of the reading, not between HH:58 and HH:07 UTC, the text kept under
  `.cache/m6`. OBSERVED on an isolated test container, never the normal one: Windows PowerShell 5.1 returns
  both streams (75 lines for a fixture PostgreSQL), and a name that is no container id is refused.
- *A restart of the market worker alone is recorded; a second within three hours stops.* IMPLEMENTED in
  `Get-PilotWatchVerdict` with two new functions in `tools/lib/Research.psm1`: `Get-MarketWorkerIdentity`
  (the worker among a reading's identities) and `Get-MarketRestartCause` (what a log slice shows). The verdict
  says when a reading shows a restart for the first time; the watch then reads the log and asks again with the
  cause. Recorded and no stop only for: the same container and image, a later start, a restart count one
  higher than the reading before showed, a log with exactly one `market_worker_fatal` event and a statement of
  `asl_prune_market_evidence` canceled by its timeout, and no restart in the three hours before (a restart
  before the watch began counts). Every other rule of the watch is unchanged and still applies to the same
  reading.
- **Checks, without a stack:** the pilot rule cases, now 54 and counted by the rehearsal (23 new; all hold); the
  parser, ASCII and line ends of the three edited scripts. `Get-MarketRestartCause` on the two real extracts:
  the one of 2026-10-07 gives the retention statement timeout; the one of 2026-10-06, which spans both
  restarts of that day, gives "2 market_worker_fatal events", as a slice with two must. NOT RUN: the rule on a
  real restart; the rehearsal with 54 cases.
- **The run was started again at 20:20 UTC** on the same Build with the phases that have not passed, the
  measurements that have never run first. The stop record is kept as
  `.cache/m6/PILOT-DIFFERENCE-20261007T201145Z-m6-b9k.txt`. Until 20:27 UTC the watch with the rule of the
  morning ran beside it, from then on the watch with this rule. `AgentOffline6` passed (20:20 to 20:24 UTC).

**The rest of `m6-b9k` stopped by hand, and a fresh run that can count (2026-10-07, from 20:41 UTC).**

- **Why.** The owner asked whether M6 can be shortened. `m6-b9k` could not be accepted whatever it showed: its
  harness was edited after its Build. The remaining phases would have taken until about 13:00 UTC, and a full
  run of about a day would have followed. The implementer's change, told to the owner: the next run starts
  fresh on a committed tree, with the phases that have never passed first, so that it is the acceptance run
  if every phase passes and the authoring run it would have been if one fails on a defect. For the owner to
  accept or reject in the B9 report: an accepted run of this kind is also the first in which
  `PerformanceResearch` and `ResearchSaturation` ran to their end, and the independent reviews were done
  before it, not after a full pass.
- **Stopped at 20:41 UTC** while `AgentFaults6` waited for its window: the pass task was ended, no process and
  no container of the run was left, the watch ended with the end marker (4 readings, no stop). `m6-b9k` ran
  no measurement phase.
- **`Report`, tried on `m6-b9j` and `m6-b9k`** (it issues no Docker test work): it runs through in under ten
  seconds and fails both runs for the right reasons. `m6-b9j`: eleven phases without a record, seven product
  or harness files changed since the Build, `AgentFaults6` ended as THREW, `Regression` never ended. `m6-b9k`:
  every attempt after the Build on another tree, and `AgentFaults6` under `reruns` with its two attempts and
  the cause of the first. So the rerun listing is OBSERVED on a real interrupted phase; a run that `Report`
  accepts is still NOT RUN.
- **Fifth independent review, read-only, two parts (20:45 to 21:00 UTC).**
  - *The fields `Report` reads from the four measurement phases.* No mismatch: 45 row definitions, 53 rows in
    a full run, each traced from the path `Report` reads to the line that writes it, with budgets, units and
    the direction of each comparison. It is a static trace for `PerformanceResearch`, `ResearchSaturation`
    and `PerformanceBrowser`, which have no passing record to compare with. The line "stream segments
    recorded is 0, budget at least 1" on a run without a `ResearchSaturation` record is deliberate: a count
    of nothing is 0, not missing.
  - *The four commits since the fourth review* (`666cfda`, `a44ccb0`, `85d9adf`, `91b8612`). One defect that
    would have stopped a run wrongly, and smaller points; all fixed before the fresh run's Build:
    - **The restart rule missed a real retention failure.** `Get-MarketRestartCause` allowed at most 600
      characters between the cancellation and the name of the retention function. At the restart of
      2026-10-06 15:53 UTC the canceled statement was the payload selection, which runs over many lines. Now
      the first function the database names after the cancellation decides, before any other traceback
      begins. OBSERVED on the kept extracts: each of the three real restarts is classified as the retention
      statement timeout.
    - **`Report` accepted a rerun of a phase that had passed**, and the earlier VERIFIED record was replaced.
      The owner allowed a rerun of a failed or interrupted phase only. Now such a run is refused.
    - **The cause of a rerun** is taken from the attempt's own error when no failed record names one.
    - **"Execution incidents unchanged".** The owner's text for a restart alone names them. A restart that
      came with `PROTECTION_UNAVAILABLE` rows gained since the reading before now stops the run; any other
      code stopped it already.
    - **Time and phase.** The watch's log names the phase of the isolated run that had an attempt open at the
      instant of a restart.
    - **The quiet period.** No reading begins in the last half minute before HH:58, so that the log read
      that may follow it cannot fall into HH:58 to HH:07.
    - **A reused process number.** `Stop-M6ProcessTree` ended left-over children by number after `taskkill`
      had freed those numbers. It now ends only a process created at the instant its list recorded.
  - *Left as it is, by design:* a restart of the market worker within three hours of the one at 20:01:27 UTC
    stops a run whatever its log shows. On 2026-10-06 the second failure came two hours after the first.
- **Checks after the fixes, without a stack:** the pilot rule cases (57, all hold); the three real restarts
  from the kept extracts; the parser and ASCII on the five edited scripts; the cut-off test (a cut call
  returns in 5.6 s and leaves no process); `Report` again on `m6-b9k` (as before, the rerun's cause as before).
  NOT RUN: any of it in a phase.
- **Not this session's work, and the reason nothing ran from 21:03 UTC.** The session of the retention fix
  reported at 21:02 UTC that the owner had approved, in that session, deploying its fix to the normal market
  worker in an HH:15 to HH:45 window that night, with one deliberate recreation of that container. This
  session has not seen that approval and acts on nothing of the normal application because of it. A market
  worker in a new container stops any test run by the owner's rule, announced or not, so this session ended
  its queued `SecretScan` trial before it began and keeps the host free of its own work until that session
  reports the recreation done. The trial and the fresh run follow in the next windows.

**Run `m6-b9l` (Build 2026-10-07 21:24 UTC on the clean tree of commit `32de348`; an authoring run; in progress).**
Started as a run that could count, after the session of the retention fix reported the normal market worker
recreated at 21:22:06 UTC. OBSERVED; isolated projects only; synthetic fixtures; no model call. Three defects
ended its chance to count; it goes on for what its measurements show.

- **VERIFIED on their first attempt, fifteen phases:** `Build`, `Generate`, `Checks`, `Migration`, `ApiAuth`,
  `Staging`, `HoldoutIsolation`, `SourcePolicy`, `EvidenceInjection`, `ShadowSchedule`, `ResearchRunner`,
  `DispatcherAuth6`, `EngineParity` (21:24 to 21:45 UTC), then `ResearchActivationRehearsal` (22:11 to 22:31,
  with 57 pilot rule cases) and `MixedVersion` (to 22:37).
- **`SecretScan`, tried on `m6-b9j` at 22:07 UTC: FAILED in three and a half minutes, on the harness.** Nine
  problems of one kind, "the dump of (cluster roles and settings) in <container> was not searched whole", and
  two for images that run never built. Cause: the script for that search was written as two strings joined
  with `+` inside an argument list, where the comma binds first, so the shell received its second half as a
  separate argument and never ran it. No count came back, and the scan rightly called the search incomplete.
  FIXED in `Invoke-M6ClusterScan` (`tools/m6/report.psm1`): the script is one argument. Every other search of
  that trial completed: the databases of nine clusters as dumps with their control lines, the volumes, the
  images that exist, logs and container data. NOT RUN again.
- **`AgentFaults6`, process part: FAILED at 23:12 UTC, on its own reading.** "Timed out after 120 s waiting
  for: the workflow waiting for its experiment." The readings show the workflow in `WAITING_TOOL` with its
  `request_experiment` call queued for twelve readings (23:10:35 to 23:11:41), each with no job, then the
  completion at 23:11:44 and the workflow's success. The helper read jobs by `research_jobs.workflow_id`,
  which the product never writes; a job is tied to its workflow through its hypothesis. FIXED in
  `agent_state` (`tests/m6_faults.py`); the phase's record now also names the job's state at the kill. The
  cut attempt on `m6-b9k` shows the same readings. Everything after that wait has never run. NOT RUN again.
- **`Regression`: FAILED at 23:29 UTC, on the order of phases.** 46 tests failed and 8 could not start, each
  with "password authentication failed for user asl_api" on the engine target's fixture cluster. Roles belong
  to the cluster. That cluster is also the catalog of the research target, whose helpers
  (`_research_stack` in `tests/m6_performance.py`, the `clusters` fixture of `tests/m6_bridge_support.py`)
  set the passwords of `asl_api`, `asl_agent`, `asl_source` and `asl_research` there from the secrets of
  their own containers. `Regression` signs in with the engine target's secret and had no step that sets it.
  It passed on `m6-b9k` (it ran right after `Checks`) and on `m6-b9j`'s first selection (the catalog tests
  of `ResearchRunner` had set the login again in between). FIXED: `python -m tests.m6_support api-login`
  sets that one login from the container's own secret on a prepared isolated database and signs in once;
  `Regression` runs it first. NOT RUN.
- **The same dependency in `Migration`, INFERRED and not changed.** Its schema test asserts that the research
  and source identities cannot sign in and that no approval exists, which is what the migration leaves. After
  `Staging`, `ShadowSchedule`, the process part of `AgentFaults6` or `PerformanceResearch` that is no longer
  so. A reset before the test would make it pass on what the reset wrote. `Migration` therefore stays before
  those phases, as on this run.
- **`PerformanceResearch`, 00:07 UTC onward, MEASURED so far** (synthetic rows at full density, about 259,000
  publications a day; the research cluster at one CPU and 1 GiB):
  - *Load:* 27 days, 6,999,998 publications, in 1,712.7 s; the store 8.34 GB (309 MB a day).
  - *Seal:* 21 days (5,444,509 publications) in 615 s, 14 days (3,629,773) in about 420 s, in a container of
    the bridge's size (half a CPU, 256 MiB): about 8,700 rows a second.
  - *Dispatch:* eight screenings on a two-hour dataset, the bridge and the runner in their own loops; the
    judged figure is in the phase's record when it ends.
  - *Screening on 21 days: NOT FINISHED in the harness window.* The job started 8.8 s after its request, spent
    679.4 s before its first cell, and was canceled at 2,160.4 s with neither of its two cells complete. Its
    plan: `DEV` 9.6 stepped days; `VALIDATION` 1.2 stepped days after 12.6 read-only days. So 1,481 s were
    not enough for 9.6 stepped days: more than 154 s a stepped day. The estimate behind its reservation was
    975 s for the job, and B0's replay figure 58 s a recorded day. The job waiting behind it (a two-hour
    dataset) then ran in 2.7 s after 2,177 s in the queue.
  - *Full test on 14 days: NOT FINISHED in the harness window.* Started 5.5 s after its request, 454.1 s
    before its first cell, canceled at 2,699.5 s with none of its six cells complete. Its plan: `DEV` 5.4
    stepped days in each of two cost scenarios, `VALIDATION` empty after the hold gap, `HOLDOUT` 2.8 stepped
    days after 11.2 read-only days in each scenario; 16.4 stepped and 22.4 read-only days in all. So 2,245 s
    were not enough for 5.4 stepped days: more than 416 s a stepped day. Its reservation estimate was 1,625 s.
  - *Shadow window:* sealed for an advance of 14 days in a container of the bridge's size (recorded in the
    phase's record). *Shadow advance over 14 days: NOT FINISHED:* 885.1 s before its first cell, canceled at
    2,700.6 s with neither cell complete (candidate and reference, each 14 stepped days after 12.6 read-only).
  - *Projection for 21 days: none.* The phase projects from a job that succeeded within its bound; none did.
    INFERRED from the floor of 416 s alone, a full test on 21 days (30.0 stepped days) needs more than
    13,000 s, and a screening on 21 days (10.8 stepped days) more than 5,100 s.
  - *Idle dispatch:* eight direct samples from 155 to 4,712 ms (median 2,279 ms); the judged figure, inferred
    from the measured pass periods and the pass start to the store, p95 4,802.8 ms against 5,000 ms. Met, with
    4 % to spare.
  - *Staging: no result.* After a backlog of one full-density day had been loaded into the catalog fixture,
    the first batch read (`SELECT ... FROM research_read.market_publications p WHERE p.sequence > ... ORDER BY
    p.sequence LIMIT ...`) was canceled by the statement timeout of the research identity, and the helper
    ended with that error. The phase then also looked for a bridge container it had not started; that
    follow-on error is the harness's.
  - **The phase's record:** FAILED at 06:13:46 UTC with five problems (the three unfinished jobs and the two
    projections that could not be made) and the staging error. The three "not finished" lines are stated by
    the phase as "not a reading against the 3,600 s job bound": the harness cannot run a job to that bound.
- **Where the time goes, read from the code by a read-only analysis (2026-10-08, no measurement of its own).**
  CONFIRMED in code: the time before the first cell is one `content_digest` of the dataset's range for each
  job (`app/research/runner.py`, `app/research/datasets.py`: "The runner recomputes the digest on the store
  before a replay, so a manifest never vouches for rows it did not hash"), at about 8,000 rows a second. With
  a position held every quote of either symbol is a step, and a step issues about ten reads that B0's bare
  replay never issued: the experiment's state (seven, with a row lock), whether an hourly capture exists
  (one) and the pending flows (two). Rows before a cell's own window are read 1,000 at a time and cost no
  read each. The batch on the replay path is 500 steps or 0.25 s. INFERRED: caching those reads within a
  batch removes most of the difference to B0's rate; starting a cell from an exact saved state would remove
  the repeated reading of earlier rows; reusing a verified digest would remove the 679 s from later jobs at
  the price of what that digest proves. The change the owner had named on 2026-10-07 (replaying each cell
  from its start less the warm-up) alters results: two indicators run over the whole history and their run
  length is part of a stored fingerprint.
- **The owner's decisions of 2026-10-08, about 06:25 UTC**
  ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-research-jobs-that-miss-the-one-hour-bound-and-a-jobs-workflow)):
  fix the cost in B9, in the order measure small jobs to completion, cache the per-quote reads within a batch
  on the replay path with tests that results stay identical, measure again; and write a job's workflow at its
  request, with a test. NOT STARTED in code at the time of this record; a design for the cache is being read
  out of the code first.
- **`ResearchSaturation`, 07:07 to 08:44 UTC on `m6-b9l`: its first run to the end, FAILED on the product.**
  Nine problems, all of staging: 302 `research_staging_failed` lines (`OperationalError`) in the bridge's
  log since the research services started, no row staged in any minute of the watch although 2,333,534
  publications waited, and therefore no staging beside a long job. The execution workload passed its own run
  (`engine_run_passed`), and the runner was busy for the whole loaded half hour. The pass was stopped by
  hand at 08:44 UTC, before `PilotCoexistence` began its work.
- **The staging defect, OBSERVED.** On that fixture's catalog (4,148,572 publications), as `asl_research`,
  `EXPLAIN (ANALYZE, BUFFERS)` of the staging read with a lower bound and `LIMIT 160`: an index scan of every
  later row (1.1 million), a subquery scan that renders each with `to_jsonb`, a sort, and only then the limit;
  1,612 ms with two parallel workers. `research_read.market_publications` is a security-barrier view, and the
  planner does not carry a limit into one. With 2.3 million rows waiting the read does not end inside that
  identity's 2 s statement timeout, in any pass. The staging part of `PerformanceResearch` had ended on the
  same statement. B4 had recorded the risk for the normal database (§19); there, with about a week of rows,
  the first pass after activation would have failed in the same way.
- **The fix** (`app/research/staging.py`, commits `7705032` and `b82a379`; no schema change, the view is as it
  was): the read carries an upper bound as well, the next `BATCH_PUBLICATIONS` sequence numbers, which the
  planner does take into the view, as it takes the lower one. Sequences are assigned one by one, so that is
  where the next batch lies. Where those numbers hold nothing (what retention left around older candles, or
  the end of what is published), the numbers of the next batch are read without their rows, in one pass over
  the later index entries, and the rows are then read by number. Four tests in `tests/test_m6_staging.py` (a
  hole wider than a batch, a smaller hole, the plan with both bounds as the research identity, and nothing
  later). Lint passes. NOT RUN.
- **The owner's instruction of about 08:15 UTC and what was changed for it**
  ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-the-owner-asks-for-the-least-waiting)). OBSERVED for it: the
  Docker VM has 16 CPUs and 8.08 GB, of which about 5.3 GB were available at 08:22 UTC, most of it file
  cache: the processor is free and memory allows about two heavy test stacks at once. From 09:07 UTC two
  runs of the same tree (`b82a379`) are used side by side: `m6-b9m` for the functional phases of the new
  build, under the harness's lock and its watch, and `m6-b9p` for one small screening job run to completion
  by a scratch script that repeats the measurement phase's own Compose calls with a 10-day load and a 9.6-day
  dataset, and that stops at once when the watch records a difference.
- **A gap in the product, found by the reading above (since fixed in code, commit `40fc6b1`, NOT RUN):** `research_jobs.workflow_id` is never
  written (`app/research/jobs.py`, the insert of a job), and the job view returns that column
  (`app/research/views.py`). A job requested by an agent therefore shows no workflow in the API. §19.
- **The real pilot beside the run:** no stop. Every reading held the lease at epoch 4 and an advancing
  checkpoint; one collection gap with `stream_silent` was noted. By the other session's account the fixed
  market worker ran its hourly retention at 22:22 and 23:22 UTC without a failed call, beside the `SecretScan`
  trial and `AgentFaults6`.

**The new build: runs `m6-b9n`, `m6-b9p` and `m6-b9q` (2026-10-08, 09:07 to 12:13 UTC; authoring).**
OBSERVED; isolated projects only; synthetic fixtures; no model call. Commands and times are in
[COMMANDS](../COMMANDS.md#m6-b9-the-new-build-its-measurements-and-the-start-of-acceptance-run-m6-b9r-2026-10-08).

- **What the build holds beyond `m6-b9l`'s:** the research job's workflow and tool call (`40fc6b1`), the
  replay batch's reuse of the experiment's state (`1c49788`), the merge of `main` with the market worker's
  retention fix (`f967cbd`), the bounded staging read with its tests (`7705032`, `b82a379`), and the three
  fixes of the night (`4a1c020`).
- **Functional phases, VERIFIED on `m6-b9n` on their first attempt:** `Build`, `Generate`, `Checks`,
  `Migration`, `ResearchRunner`, `EngineParity`, `Staging`, `HoldoutIsolation`, `SourcePolicy`,
  `EvidenceInjection`, `ApiAuth`, `AgentOffline6`, `ShadowSchedule`, `DispatcherAuth6`,
  `ResearchActivationRehearsal`, `MixedVersion`, and `AgentFaults6` with its process part.
  - *The reuse of the experiment's state is shown by tests that ran:* in `ResearchRunner`, a job gives one
    document per step, verified, and on the fast path; reused state leaves what a step per transaction leaves
    (fingerprint, trace and every posting, with a position across two hour boundaries, a latch and a resume);
    and with one invalidation broken on purpose the verify mode raises and the plain run cannot complete. In
    `Regression`, the statements of one forward step equal the list of 39 as it was, with its row locks.
    `EngineParity` holds the native digests to the baseline.
  - *The process faults, for the first time in any run* (11:07 to 11:25 UTC): the agent worker killed while its
    workflow waits for its experiment; the runner killed once and twice; the research cluster restarted; the
    bridge killed with a result to relay and while staging; the fetcher killed in a fetch. Seven cases, no
    problem.
  - *The four tests of the bounded staging read* ran in `Staging`, the plan with both bounds as the research
    identity among them.
- **`Regression` on `m6-b9n`: its tests passed, the phase did not.** The login step VERIFIED and "172 passed"
  in 995 s (three more than before: the new tests), then the phase stopped on its guard: `app/market_data`
  differs from `ed9fae3` since `main` was merged. Decision 7 of 2026-10-06 keeps the four M2 worker-fault files
  out of this phase because that code was what the market worker ran. It still is: the worker runs the
  retention fix since 2026-10-07 21:22 UTC, and that fix's own acceptance ran the worker-fault phases and its
  new fault file on the same source. The guard now compares with `ec1d78b` and names five files as not
  selected (`525c580`). FOR THE OWNER: the commit named in decision 7 changed. The first selection's limit is
  1,400 s (it had 5 s to spare beside another stack).
- **A run's address ranges can collide with a finished run's networks.** `m6-b9m` failed its Build on
  "Pool overlaps with other one on this address space": its ranges, which follow from the run id, were those
  of `m6-b9k`, whose networks still existed. Thirteen finished runs were then removed by exact name with the
  harness's `Clean` (test networks 87 to 31), and a new run's ranges are compared with the existing test
  networks before it is used. `Clean` is refused while a phase holds the lock and works while a phase waits
  for its window.
- **MEASURED on `m6-b9p`: what the reuse is worth.** A screening job on a 9.6-day dataset: 568.2 s, VALID;
  320.7 s before its first cell (33.4 s a dataset day); the DEV cell of 2.76 stepped days in 247.5 s. Under a
  profiler that cell holds 174,768 steps, one stepped day with a position: about 230 s for such a day, where
  the full test on `m6-b9l` had needed more than 608 s. Of the stepping, by the profile: about half is one
  valuation, one account update and one step row for each second of market time with a position; about a
  quarter is the batch's cache copying the experiment's state at each step; the rest heartbeats, fences and
  commits. Before the first cell the runner's digest fetched 2.49 million rows in about 257 s and sent a
  heartbeat every 500 of them.
- **`PerformanceResearch` reworked (`30d9b38`)** to measure jobs that complete inside a window and to project
  the designed sizes ([TESTING](../TESTING.md)); the owner's four accepted misses are a list of four keys in
  the phase. Its projection ran without a database on the real screening reading and synthetic others: no
  exception; a screening at 21 days 2,963 to 3,391 s. NOT RUN as a phase before the acceptance run.
- **Reservations follow measured durations (`c105bff`, `73b853f`).** A phase of a few minutes had waited for
  the next hour because its reservation was that of a guess; with the new values the phases after the two
  long measurements fit three to four windows where they took nine.
- **The web test and the samples (`2453f68`).** `BrowserResearch` on `m6-b9q` failed on the one assertion that
  the queued screening names no workflow, as expected; the 41 samples of that run's fixture were copied whole
  and the assertion now says the job names one. The official shadcn skill was read from the Codex copy and
  `shadcn info` run in the run's web tool image first (preset `b2fms61Bqi`); no component is touched.
- **`SecretScan`, tried on `m6-b9n` (12:09 to 12:12 UTC):** the fixed search of each cluster's roles and
  settings completes (8 of 8); 34 databases searched; nothing found; the two remaining problems are images
  that run never built.
- **The real pilot beside these runs:** no stop; the lease at epoch 4 and held, the checkpoint advancing, no
  `PROTECTION_UNAVAILABLE` row and no collection gap in any thirty minutes read.
  - **CORRECTED on 2026-10-08, 13:20 UTC: that line left out a market incident.** OBSERVED in the watch's log beside run `m6-b9n`: between its readings of 09:20:39 and 09:25:41 UTC on 2026-10-08 the normal market worker recorded one `RETENTION_FAILED` incident, and by the reading of 09:30:42 one `RETENTION_RECOVERED`. None followed in that watch (to 12:11:41 UTC). At those minutes two test stacks were at work: run `m6-b9n` in `Regression` (from 09:20:18) and the scratch measurement on `m6-b9p`, whose dataset was being sealed (09:20:08 to 09:25:07) before its job started. The lease, the checkpoint, the containers and their restart counts did not change, no `PROTECTION_UNAVAILABLE` row and no collection gap was gained, and the watch does not stop on a market incident other than `QUEUE_OVERLOAD`: it noted the two codes in each line and went on. INFERRED, not known: the two stacks' reads pushed the pages of the hourly delete out of memory, and it ran into its statement timeout; the same event restarted the worker three times before the fix of ExecPlan 0024 was deployed, at moments when no test command ran. It is the first failed call seen on the normal application since that fix (the fix's own soak had seen none). The line above was written from the watch's verdicts and not from its notes; that was this session's omission, found on re-reading the logs during the acceptance run, and it is reported to the owner. FOR THE OWNER: the rule for a test run beside the pilot names restarts, not this incident (§19).

**Acceptance run `m6-b9r` (2026-10-08, from 12:13 UTC; Build of commit `2453f68`, clean tree).** IN PROGRESS
when this was written; its results follow below when it ends. Order: the short phases in the first window,
`PerformanceResearch` from 13:07 UTC, `ResearchSaturation` after it, then the fault, browser and rollout
phases, `SecretScan` and `Report`. Only documents are edited while it runs.

- **Stopped at 14:04 UTC on the owner's decision; no longer an acceptance run.** The owner asked for a simpler
  way to complete the pull request and chose to accept M6-A on the phases the inert deployment depends on
  ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-m6-a-is-accepted-on-what-the-inert-deployment-switches-on)). The run's pass was ended while `PerformanceResearch` waited for its second window:
  no container of the run was running. What the run holds: eleven phases VERIFIED on the Build of `2453f68`
  (`Build`, `Generate`, `Checks`, `Migration`, `Regression`, `ResearchRunner`, `EngineParity`, `Staging`,
  `HoldoutIsolation`, `SourcePolicy`, `EvidenceInjection`, 12:13 to 12:47 UTC) and one attempt of
  `PerformanceResearch` that never ended, whose first part loaded 27 days in 1,759.5 s. It serves as an
  authoring run for a trial of the browser and volume phases; the acceptance is a fresh run of the scoped
  list.
- **The trial on it, 14:08 to 14:22 UTC.** `BrowserResearch` (with the samples captured again and the fresh
  sample check), `BrowserResearchError` and `BrowserRegression` VERIFIED. `PerformanceApi` FAILED on one
  budget: MEASURED, 34 routes at 39.12 ms sequential and 168.14 ms with five readers at p95 (budgets 250
  and 500), and the cutoff-filtered search at 213.36 ms at p95 against 150 ms on 10,004 items, 10,000 of
  them at the extract cap. The owner decided that the search budget is a condition of the activation and
  not of M6-A ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-the-search-budget-is-a-condition-of-the-activation)). `PerformanceBrowser` did not run: it needs a passing `PerformanceApi`.
  A first start of the trial at 14:04 ended at once, correctly: the report module had been edited while
  its first phase waited for its window, and the harness refuses a phase whose harness file changed after
  it was loaded.
- **The two harness changes the decisions needed, and their review.** `Report` requires the 24 phases
  M6-A is accepted on, refuses a run on which a phase of the activation gate was started, and shows the
  search figure against its budget without judging it. `PerformanceApi` records the search against its
  budget and fails on it no longer; it still fails on a missing figure, on fewer than 10,000 items at the
  registered extract size and on a failed search. An independent read-only review of the first form of the
  report change found nothing that would throw or misjudge a run of the scoped list, and six smaller
  points; the refusal of a run with a started gate phase answers three of them. The changed report was
  then run against copies of this run's records: it completes, names the started `PerformanceResearch`
  as its reason to refuse, and reads the search row as "NOT JUDGED HERE (MISSED against 150 ms)".
- **`PerformanceBrowser`, its first full execution (15:07 UTC), and a defect of its test.** `PerformanceApi`
  was VERIFIED under the changed rule first (14:41 to 14:46 UTC: routes 38.78 and 182.26 ms at p95, the
  search 234.55 ms and recorded as missed). The browser then measured 15 of 32 page views and its test
  stopped: it required a level-one heading on every page, and the system page, which is older than the
  page header the others share, has a card title and none. MEASURED on those 15: SSR p95 at most 84 ms
  (budget below 1,500), LCP at most 192 ms (2,500), CLS 0 (0.1). The test now requires the heading where a
  page has one, and the page's content on all (`apps/web/e2e/m6-performance.spec.ts`; formatter, linter and
  type checker pass in the run's web tool image). Tried by repeating the phase's own commands on that
  run's stack with the changed file mounted over the image's copy (15:11 to 15:13 UTC): 32 page views, 16
  at each width, SSR p95 at most 101 ms, LCP at most 196 ms, CLS 0, "1 passed". No page and no component
  is changed. The official shadcn skill and project discovery were used for the web tree earlier the same
  day (above) and were not repeated for this test file.

- **The pilot beside it, as it happens.** OBSERVED in the watch's log (`.cache\m6\m6-b9r-pilot-watch.log`): its
  reading of 13:24:24 UTC shows no market incident since the watch began (12:13:53); the reading of 13:29:25
  shows "RETENTION_FAILED +1, RETENTION_RECOVERED +1". One hourly retention call of the normal market worker
  failed and a later pass completed, inside those five minutes, while `PerformanceResearch` loaded its 27-day
  store (13:07:17 to 13:36:50 UTC; 1,759.5 s). Lease, checkpoint, containers and restart counts unchanged; no
  `PROTECTION_UNAVAILABLE` row, no collection gap. It is the second such call of the day and the first beside
  one test stack alone. The owner was asked and decided at about 13:47 UTC that a failed call that recovers
  is reported and does not stop a run ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-a-failed-retention-call-that-recovers-is-reported-and-does-not-stop-a-test-run)).

**M6-A acceptance evidence: run `m6-b9s` (2026-10-08, 15:15:45 to 18:14:16 UTC). VERIFIED; acceptance and
deployment are the owner's decisions.**

OBSERVED. One fresh run and one Build, of commit `cedb6d1` with nothing uncommitted; the tree at `Report` as
at Build. The 25 phases M6-A is accepted on ([scope](../../DECISIONS.md#2026-10-08--m6-b9-m6-a-is-accepted-on-what-the-inert-deployment-switches-on)), each VERIFIED in its first attempt:
no rerun and no failed record. `Report`: "26 phase records VERIFIED on run m6-b9s; 24 phase attempts; 11
measurements, none missed". Isolated projects, a synthetic owner and fixtures, no model call, no public source;
the normal application was read by the pilot watch and not otherwise addressed. Commands and phase times:
[COMMANDS](../COMMANDS.md#m6-b9-the-acceptance-run-m6-b9s-2026-10-08).

| Phase | Measurement | Measured | Budget | Verdict |
|---|---|---|---|---|
| `PerformanceApi` | catalog and agent routes, sequential p95 | 38.91 ms | at most 250 ms | WITHIN |
| `PerformanceApi` | the same routes, five readers p95 | 145.08 ms | at most 500 ms | WITHIN |
| `PerformanceApi` | slowest route, sequential p95 (datasets_shadow) | 45.25 ms | at most 250 ms | WITHIN |
| `PerformanceApi` | slowest route, five readers p95 (system_status) | 211.95 ms | at most 500 ms | WITHIN |
| `PerformanceApi` | cutoff-filtered search over 10,000 items p95 ([decision](../../DECISIONS.md#2026-10-08--m6-b9-the-search-budget-is-a-condition-of-the-activation)) | 211.99 ms | at most 150 ms, judged at the M6-B activation gate | NOT JUDGED HERE (MISSED against 150 ms) |
| `PerformanceApi` | searched items with an extract at the registered cap | 10000 items | at least 10000 items | WITHIN |
| `PerformanceBrowser` | slowest page, SSR p95 | 95 ms | below 1500 ms | WITHIN |
| `PerformanceBrowser` | slowest page, LCP | 172 ms | at most 2500 ms | WITHIN |
| `PerformanceBrowser` | worst page, CLS | 0 | at most 0.1 | WITHIN |
| `MixedVersion` | migration 0008 on a live database | 0.53 s | none declared | REPORTED (no budget) |
| `MixedVersion` | API replacement | 7.6 s | none declared | REPORTED (no budget) |

From the phase records: `Checks` 407 engine tests and 155 web tests in 18 files; `Regression` 172 tests in
892 s; `SecretScan` "161 secrets in 808 forms; 46 databases (1575158 dumped lines) in 10 clusters; 34
container logs; 14 images; 2929 evidence files (0 archive entries); 635 source files; 0 problem(s)".

**Q01–Q10 for M6-A:**

| Gate | Result for M6-A | Evidence on run `m6-b9s` | Left for |
|---|---|---|---|
| Q01 UX | VERIFIED: the research, evidence and approval pages with their loading, empty, error, stale, pending and not-found states at 390 and 1440 px; the M1 to M5 pages behave as before | `BrowserResearch` (7 tests, 41 fresh API samples), `BrowserResearchError`, `BrowserRegression` (9 states) | A person's judgment of the pages on real data: the owner, in M6-B |
| Q02 Accessibility | VERIFIED scoped, automated, Chromium, as in B8 | `BrowserResearch` | No screen-reader claim. The system page, an older page, has no level-one heading (found by the performance test; not changed) |
| Q03 Data correctness | VERIFIED | `EngineParity`, `ResearchRunner`, `HoldoutIsolation`, `Staging`, `ShadowSchedule`, `Migration`, `Regression` (172 tests) | — |
| Q04 Security | VERIFIED | `SourcePolicy`, `EvidenceInjection`, `DispatcherAuth6`, `ApiAuth`, `SecretScan` (0 problems) | — |
| Q05 Reliability | VERIFIED | `AgentFaults6` with its seven process cases, `AgentOffline6`, `ResearchRunner`, `Staging` | — |
| Q06 Performance | VERIFIED for what the inert deployment runs: API routes and pages on a year of rows. NOT RUN for M6-A: R17 and the budgets of research jobs, idle dispatch and staging. MEASURED and not judged: the analyst's search, 211.99 ms at p95 against 150 ms | `PerformanceApi`, `PerformanceBrowser` | The M6-B activation gate: `PerformanceResearch`, `ResearchSaturation`, `PilotCoexistence`, the four job times and the search |
| Q07 Automated verification | VERIFIED: 25 phases on one fresh run and one image, each in its first attempt, no skipped test | `Report` | — |
| Q08 Visibility | VERIFIED: status routes and pages, stable codes for every state and refusal, no secret in a log, image, database or evidence file | `ApiAuth`, `BrowserResearch`, `SecretScan` | — |
| Q09 Deployment and recovery | VERIFIED in isolation: 0008 forward and back, mixed versions under requests, the deployment with its stops, its rollback and the activation scripts, on the images the pilot runs | `Migration`, `MixedVersion`, `ResearchActivationRehearsal` | The normal deployment: B10 |
| Q10 Maintainability | VERIFIED: contracts updated with the code; no new dependency; independent read-only reviews with their findings fixed | The diff; INTEGRATION_EVIDENCE | — |

**Not run for M6-A:**

- `PerformanceResearch`, `ResearchSaturation` and `PilotCoexistence`: not part of M6-A by the owner's decision; conditions of the activation.
- The analyst's search against its budget: measured, not judged.
- The real pilot under research load, a live model, a public source, a real source fetch, a screen reader.
- The scripts against the normal application: B10, after the owner's yes.
- What each phase names as not run is in its record and under `not_run` in `Report.json` (for `Checks`, `MixedVersion`, `AgentFaults6`, `ResearchActivationRehearsal`, `ApiAuth` and `BrowserResearch`).

**The pilot beside the run** (`tools/m6-pilot-watch.ps1`, 29 readings from 15:21 to 18:12 UTC): no stop. Every
reading held the lease at epoch 4 with an advancing checkpoint, no `PROTECTION_UNAVAILABLE` row and no
collection gap; the four hourly reports were there in their HH:05 minute. One note, reported as the owner
decided ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-a-failed-retention-call-that-recovers-is-reported-and-does-not-stop-a-test-run)): between the readings of 15:26:02 and 15:31:04 UTC one hourly
retention call of the normal market worker failed and a later pass completed, while the run was in
`Regression` (15:21:16 to 15:36:51). The calls of about 16:26 and 17:27 UTC left no further note.

### B10 — the inert deployment to the normal application (2026-10-08)

**VERIFIED.** `tools/m6-deploy.ps1` completed its eleven steps from 22:15:01 to 22:20:13 UTC on commit `583a98a`
(exit 0, record `COMPLETE`), on the owner's approval
([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b10-the-owner-approves-the-inert-deployment-before-the-merge)). The
product tree of that commit is the tree of the accepted Build (`cedb6d1`): the difference over `apps`,
`services`, the compose file and the package files is empty. Since that Build only documents changed, and one
line of the deploy script, after a first start at 20:15 UTC had stopped in its read-only preflight with
nothing changed
([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b10-a-deployment-that-stopped-in-its-read-only-preflight-and-the-fix-of-the-deploy-script)).
Commands and every figure:
[COMMANDS](../COMMANDS.md#m6-b10-the-inert-deployment-of-m6-a-to-the-normal-application-2026-10-08).

| §13.1 | Required | OBSERVED |
|---|---|---|
| 1 | HH:15 to HH:45 UTC, never 23:50 to 00:20 | Began 22:15:01; first replacement 22:19:42, last 22:20:06; ended 22:20:13 |
| 2 | Starting state read; protected backup with its SHA-256; isolated restore | Schema `0007_m5_agent_runtime`, lease epoch 5 held, experiment `RUNNING` at version 3. Backup `.cache\deployments\m6-deploy-20261008T221514Z\asl.dump`, 479,947,415 bytes, SHA-256 `428265791ac0075373af1e4150edd79f652e13b6ffbd37f40b1719e0e35fe0a7`. Its copy was migrated to 0008, reconciled `OK` and downgraded in a helper cluster; the M1 to M4 tables compared equal before, after and after the downgrade; no helper left |
| 3 | Rollback tags | `:pre-m6` created on `api`, `web`, `agent-worker`, `migrate` and `agent-admin`, each from the image that ran or that its name pointed to |
| 4 | Web, then the API, then migration 0008, then the agent worker | `web` 22:19:42, `api` 22:19:54, the migration applied in 1 attempt, `agent-worker` 22:20:06 |
| 5 | Research and source services built and not started; identities NOLOGIN; flags `0` | Five images built; no container of the four services; `asl_research` and `asl_source` exist without login; both flags `0`; no secret created |
| 6 | Pilot unchanged; lease epoch and experiment version unchanged; readiness; the pages; the runtime waiting | The two tables and the list below |

**The identities, before and after** (container ID on image ID; every restart count 0 at both times):

| Service | Before (22:15) | After (22:20) |
|---|---|---|
| `postgres` | `83f227fc…` on `b0f9560a…`, started 19:38:43 | the same |
| `market-worker` | `82c8f547…` on `31ee07e5…`, started 19:38:42 | the same |
| `execution-worker` | `fb1ff07e…` on `5b02dbe1…`, started 19:38:43 | the same |
| `evaluation-worker` | `5ab291a4…` on `6e2d4e6a…`, started 19:38:43 | the same |
| `agent-runner` | `ecb0a0ac…` on `421793d7…`, started 19:38:42 | the same |
| `agent-egress` | `5c9acbb7…` on `ce07199d…`, started 19:38:43 | the same |
| `web` | `76821ab5…` on `0801ab1c…` | `a4d5430c…` on `f8425683…`, started 22:19:42 |
| `api` | `9089ab48…` on `54368771…` | `26ef487f…` on `44fd430f…`, started 22:19:54 |
| `agent-worker` | `2108c5f0…` on `d715d130…` | `8ec52f29…` on `64c0bad5…`, started 22:20:06 |

| The pilot | Before | After |
|---|---|---|
| Schema | `0007_m5_agent_runtime` | `0008_m6_research` |
| Execution lease | epoch 5, held | epoch 5, held |
| Experiment `d779fbf4…` | `RUNNING`, version 3 | `RUNNING`, version 3 |
| Segments; downtime events | 0; 4 | 0; 4 |
| Execution incidents | 514 (`EXECUTION_DOWNTIME` 4, `PROTECTION_UNAVAILABLE` 510) | the same |
| Image names of the three workers and `pilot-admin` | `31ee07e5…`, `5b02dbe1…`, `6e2d4e6a…`, `c62ac138…` | the same |
| Market incidents during the run (reported, not judged) | | none |

**Verified read-only afterwards, 22:20 to 22:28 UTC:**

- **The pilot.** Lease epoch 5 and held; the forward checkpoint advancing (2278110 at 22:20:54, 2279359 at
  22:28:20); `EXECUTION_DOWNTIME` 4 and `PROTECTION_UNAVAILABLE` 510 as before; no market incident since
  22:15:00. Four identity samples over 93 s without a difference.
- **Readiness.** The script's read of the API's readiness route passed; `api`, `web` and `agent-worker` report
  healthy.
- **The pages, without signing in.** The sign-in form with the navigation that now holds Research and
  Evidence; `/research`, `/evidence`, `/agents` and `/approvals` ask for the owner session; `/system` reads
  Research `unapproved`, Evidence sources `unapproved`, Model runtime `login_required`, Paper trading
  `running`. No console error.
- **The runtime waiting for a new profile.** OBSERVED as `login_required` on the system page. Its reason,
  `PROFILE_DEFINITIONS_CHANGED`, is shown on the signed-in agents page and was NOT read by the implementer;
  it is VERIFIED in isolation by `ResearchActivationRehearsal`.

**Removed afterwards** ([DOCKER](../../DOCKER.md#cleaning-up-disposable-resources)), 22:26 to 22:28 UTC, by exact
name and never forced: the fifteen rollback tags of `api`, `web` and `migrate` older than `:pre-m6`; then the 82
untagged images and 2.353 GB of unused build cache. Kept: the five `:pre-m6` tags, every current image, the
images the pilot's workers are pinned to and the older tags of the pilot's services, every volume.

**Q09 for M6-A on the normal application:** VERIFIED: the backup, its isolated restore with the migration and
the downgrade, migration 0008 forward, the three services replaced in order, the pilot unchanged. NOT RUN
there: the rollback, rehearsed in isolation only.

**Not run:** the owner's signed-in pages; the rollback on the normal application; any activation, approval,
model call or public endpoint; the three phases of the activation gate, the four job times and the search
budget (§13.2).

## 19. Open risks

- **B9: a research job does not name its workflow (found 2026-10-08, product, not changed).** `research_jobs.workflow_id` exists in migration 0008 and the job view returns it, but the request that creates a job never writes it; the orchestrator finds a workflow's jobs through the hypothesis. Nothing financial depends on it. An owner page or an API reader that expects the workflow of a job requested by an agent gets none. For the owner: write it at the request, with a test, in this batch (a product change, so before the acceptance Build), or record it as known for M6-A and fix it afterwards. **CLOSED 2026-10-08.** The owner decided to fix it in this batch with a test ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-research-jobs-that-miss-the-one-hour-bound-and-a-jobs-workflow)). The request now writes `workflow_id` and `tool_call_id` (`40fc6b1`): a screening an agent asks for names its workflow and its tool call, the bridge's full test names the nominating workflow, and a shadow advance names none. Tests in the job, API, bridge and agent files; the committed API samples and one page test follow (`2453f68`).
- **B9: research jobs against the one-hour bound, MEASURED (2026-10-08); the owner decided to fix the cost in B9.** No job at 14 or 21 days finished inside the harness window, and the full test on 14 days shows more than 416 s a stepped day against the 58 s of B0 (§18, run `m6-b9l`). Risks that stay with the fix the owner authorized (the per-quote reads cached within a batch on the replay path). It must keep a job's results identical and must not change how the live forward engine reads its state: the engine is shared with the running pilot's worker, which is not rebuilt, and with every later rebuild of it. Its effect is INFERRED until measured; by the analysis's arithmetic it alone leaves a full test on 21 days near the bound, so a second step (a cell started from an exact saved state, or a verified digest reused across jobs) may be needed, and each of those returns to the owner. The harness cannot measure a job longer than a test window, so the rates are to be taken from small jobs run to completion and the 21-day figures projected from them. Until the measurement passes, no acceptance run can. **CONTINUED 2026-10-08.** The reuse of the experiment's state within a replay batch is in the build (`1c49788`), on the replay path only; the forward engine's statements are unchanged, which a test holds to the list of 39. MEASURED on run `m6-b9p`: a screening on a 9.6-day dataset completes in 568.2 s, and a stepped day with a position takes about 230 s where it took more than 608 s. That is not enough for the long jobs: INFERRED from that measurement, a full test at 14 and at 21 days and a shadow advance over 14 and over 21 days stay over 3,600 s. The owner accepted those four as missed for M6-A, with the engine work that remains in a pull request of its own that must pass the measurement before M6-B activation ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-research-job-times-beyond-the-one-hour-bound-are-accepted-as-missed-for-m6-a)). The bound of 3,600 s and the cap of 21 days are unchanged. What stays open until that pull request: the four job times, with the figures of the acceptance run (§18). Named so far and not done, each the owner's to decide where it changes a result or a contract: the batch's cache handing out the experiment's state without copying it at each step (about a quarter of the stepping by the profile); fewer heartbeats while the dataset is hashed; a cell started from an exact saved state; a verified hash reused across jobs.
- **B9: the staging read against the research identity's statement timeout (OBSERVED on a fixture, 2026-10-08).** The first batch read of the staging measurement was canceled at 2 s after a one-day backlog was loaded. B4 recorded this as a risk for the normal database. NOT KNOWN: whether a second read passes (a cold cache), or whether the read needs another plan or an index. If it needs an index on a table that migration 0008 creates, it would go into 0008 as the owner decided for the others; an index on an older table would be a migration and a pull request of its own, and is the owner's to decide first. **CAUSE FOUND AND FIXED 2026-10-08, no schema change.** OBSERVED with the plan of the statement on that fixture: the read asked for the rows after a sequence with a limit, through a view that is a security barrier; the planner does not carry a limit into such a view, so every later row was read and rendered before the first 160 were kept (1.6 s with 1.1 million rows waiting; no batch at all with 2.3 million). The read now names the upper sequence as well as the lower one and steps over a wider hole by numbers first (`7705032`, with four tests in `Staging`, `b82a379`). The second read, the cold cache and an index were not the cause. What reading the rest of that path adds is the next entry.
- **B9: two more staging reads go through a barrier view without an index that serves them (INFERRED by reading on 2026-10-08, before any run could show it; NOT MEASURED).** (1) *A collection the store does not hold yet.* A batch reads its collections through `research_read.market_collections`, and that view decides "published" by looking for one observation of the collection that has a publication. `market_observations` has no index on `collection_id` (B4's entry below, for the normal database). The search is a scan of the observations from the start of the table until the first such row. On the fixtures of `PerformanceResearch` the first row of the table already belongs to the one collection. In `ResearchSaturation` the backlog is a second set of rows with its own collection, behind the 1.8 million observations of the seven days loaded first: the bridge's first pass reads past all of them, twice, each read under the research identity's limit of 2 s. Whether that takes a fraction of a second or more than two depends on what the database holds in memory at that moment. If a read is canceled, the pass fails, changes nothing and is repeated, and the phase counts the line in the bridge's log as a problem: a failure of that kind in `ResearchSaturation` would be this, and would be a finding about the product on a cold cache, not about the load. (2) *Where a new store version starts.* `origin` asks the publications view for the oldest row inside the backfill, ordered, with a limit of one; for the reason found above, every publication inside the backfill is read before one is kept. That is once for a store version and renders nothing; on seven days at full density it is 1.8 million rows. NOT RUN on the normal database, where both would happen at M6-B activation and then for each new collection: before activation these two reads should be timed there read-only, with the owner's approval, or made independent of the table's size. An index on `market_observations(collection_id)` would alter an M2 table: a migration and a pull request of its own, the owner's to decide first.

- **B9: the market worker's restarts and a long test phase (the owner's decision of 2026-10-07 evening; a risk that stays).** Three restarts are OBSERVED with the same cause, the retention delete canceled by its statement timeout: 2026-10-06 13:51:57 and 15:53:56 UTC and 2026-10-07 20:01:27 UTC. No command of this session's test runs was in progress at any of them. Why the delete is slow at those times is NOT KNOWN on the normal app. INFERRED by the session of the retention fix from its isolated measurement: the first retention call of an hour reads about 11,000 pages, and it can miss its timeout when other containers' work earlier in the hour has pushed those pages out of the Docker VM's cache. If that holds, `PerformanceResearch` (eight windows) and `ResearchSaturation` (two) make a restart at the next hourly retention likelier, and the watch stops a run at a second restart within three hours. What this batch can do about it is nothing on the normal app; the fix is ExecPlan 0024, in another session, not merged and not deployed. Two consequences for later steps. For the acceptance run: a stop by a second restart costs the phase in progress, which the rerun rule then allows to start again on record. For B10: `tools/m6-deploy.ps1` still stops on any container change, so a restart of the market worker during the deployment would stop it at its last check; the hourly retention ran at about HH:01 UTC on the evening of 2026-10-07, outside the HH:15 to HH:45 deploy window, and INFERRED from two instants it moves later by about 16 s an hour, so its minute has to be read again before a window is chosen. **UPDATE 2026-10-08.** ExecPlan 0024 was merged as `ec1d78b` (PR #31) and its market worker has run in the normal app since 2026-10-07 21:22:06 UTC, deployed by that plan's session with the owner's approval ([DECISIONS](../../DECISIONS.md#2026-10-07--market-worker-deployment-approved-then-the-merge-execplan-0024)). Since then a retention call the database ends is recorded as an incident and the worker goes on; no restart of the market worker is OBSERVED by this batch's watch from that time to the start of the acceptance run. By that session's figures the hourly retention ran at about HH:22 UTC that evening and moves later by about 16 s an hour, so it now falls inside the HH:15 to HH:45 deploy window: its minute is read again before a window is chosen. `tools/m6-deploy.ps1` is unchanged and still stops on any container change.
- **B9: a failed retention call beside two test stacks (OBSERVED 2026-10-08; the owner's rule does not name it).** OBSERVED in the watch's log beside run `m6-b9n`: between its readings of 09:20:39 and 09:25:41 UTC on 2026-10-08 the normal market worker recorded one `RETENTION_FAILED` incident, and by the reading of 09:30:42 one `RETENTION_RECOVERED`. None followed in that watch (to 12:11:41 UTC). At those minutes two test stacks were at work: run `m6-b9n` in `Regression` (from 09:20:18) and the scratch measurement on `m6-b9p`, whose dataset was being sealed (09:20:08 to 09:25:07) before its job started. The lease, the checkpoint, the containers and their restart counts did not change, no `PROTECTION_UNAVAILABLE` row and no collection gap was gained, and the watch does not stop on a market incident other than `QUEUE_OVERLOAD`: it noted the two codes in each line and went on. INFERRED, not known: the two stacks' reads pushed the pages of the hourly delete out of memory, and it ran into its statement timeout; the same event restarted the worker three times before the fix of ExecPlan 0024 was deployed, at moments when no test command ran. It is the first failed call seen on the normal application since that fix (the fix's own soak had seen none). What follows from it. (1) The owner's rule of 2026-10-07 lets a test run go on after one restart of the market worker from this cause and stops it at a second within three hours. Since the fix the same cause leaves an incident and no restart, which that rule does not name, and the watch only notes it. Until the owner says otherwise this session applies the same measure by hand: a failed call beside a run is recorded with its time and phase and reported, and a second within three hours stops the run. The watch itself is not changed during an acceptance run. **DECIDED by the owner at about 13:47 UTC, after a second failed call (below): "Report only".** A failed call that recovers is recorded with its time and phase and reported, and the run goes on; the run is stopped by hand when a call has not recovered ten minutes later or `RETENTION_STALLED` appears, and on everything the stop rule already names ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-a-failed-retention-call-that-recovers-is-reported-and-does-not-stop-a-test-run)). The measure of a second within three hours is withdrawn. (2) Two heavy stacks at once are not used again beside the pilot without the owner's word: the failed call came with two, and a night of one stack (`m6-b9l`, 21:25 to 08:39 UTC) shows none. (3) For B10: the deploy script judges execution incidents and container identities; market incidents gained during a deployment are listed in its record and stop nothing, so a failed retention call in those minutes would be reported and would not stop the script.
- **B9: what M6-A is accepted without (the owner's decision of 2026-10-08; conditions of the M6-B activation).** No run has shown that the pilot's publication and execution budgets hold while the research services work at their limits (`ResearchSaturation`, R17), that research and staging keep out of the quiet window beside a pilot (`PilotCoexistence`, last VERIFIED on run `m6-b9j`, a build before the reuse of the experiment's state, the bounded staging read and the merge of `main`), or what a research job, idle dispatch and staging cost on the current build (`PerformanceResearch`: one screening on 9.6 days MEASURED at 568.2 s on run `m6-b9p`, everything else NOT RUN to completion). The bounded staging read has its four tests and no run at full density. None of this can run in the normal application before the activation: the inert deployment starts no research or source service. Each is a condition of the activation (§13.2), not of M6-A. The measurement code of those three phases is in the tree and has not passed as a whole: `PerformanceResearch` was reworked on 2026-10-08 and its first run was stopped in its first part. The analyst's search is a fourth condition: MEASURED at 213.36 ms at p95 against its 150 ms in `PerformanceApi`, on 10,000 items at the extract cap with query words that every item holds ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b9-the-search-budget-is-a-condition-of-the-activation)). INFERRED from the query, not measured: it ranks every matching item, so its cost grows with the items a common word matches.
- **B10: the owner scripts read codes into objects whose keys ignore letter case (found 2026-10-08 by the first deployment; one reader fixed).** The normal database holds the market incident code `clock_uncertain` and the code `CLOCK_UNCERTAIN`. `tools/m6-deploy.ps1` read every code of that table into one JSON object, which Windows PowerShell 5.1 refuses; the deployment stopped in its read-only preflight with nothing changed, and the script now counts those codes without regard to case ([DECISIONS](../../DECISIONS.md#2026-10-08--m6-b10-a-deployment-that-stopped-in-its-read-only-preflight-and-the-fix-of-the-deploy-script)). `tools/m6-pilot-check.ps1` reads the codes since an instant in the same form and is NOT changed: a reading that held both spellings would fail, and the watch beside a test run would then record a reading that could not be taken. No fixture holds two spellings of one code; the isolated rehearsal cannot show this class of defect until one does. **CLOSED 2026-10-09 for both readers; what stays is at the end.** By the owner's instruction ([DECISIONS](../../DECISIONS.md#2026-10-09--the-pilot-check-counts-the-market-workers-codes-without-regard-to-letter-case)) the pilot check counts the market worker's codes by `upper(code)` as well; the execution incidents and the experiment events are read as recorded, because the same risk is not shown for them. Three findings on the way. (1) *One event writes both spellings* (read from `app/market_data/worker.py`; not seen in a reading). A clock check that fails at the start of a collection, or that finds the clock out of bounds, records `CLOCK_UNCERTAIN` with its measurement and then gives `clock_uncertain` as the reason the collection cannot go on, and the worker records that reason as a code too. A collection starts again after every collection gap, and every start makes such a check. (2) *What the check as it was would have done beside a run* (INFERRED from `tools/m6-pilot-watch.ps1`; not observed). The watch counts from the instant it began, so from such an event on each of its readings would have failed, and the third failed reading in a row stops the isolated run. One failed clock check of the normal worker could have cut a phase of the activation gate that takes eight test windows. (3) *The rule already ignored letter case.* It finds a code by its name and compares two readings through PowerShell's property lookup, which ignores case; `tools/lib/Research.psm1` is unchanged, and a reading from before the change compares correctly with one from after it. `QUEUE_OVERLOAD` and `COLLECTION_GAP`, the two codes the rule looks for, have only ever been written in upper case (read from the history of `app/market_data`). IMPLEMENTED: the one changed part of the check's SELECT; a model of the normal application for the check (`tools/m6/pilot-check-model.ps1`, 4 scenarios, 15 expectations); one code in two spellings in every reading of the deploy model (17 scenarios, now 75 expectations); both models run by `ResearchActivationRehearsal`, which therefore holds the rows whose absence let the defect through. VERIFIED without the normal application ([COMMANDS](../COMMANDS.md#the-pilot-check-counts-market-incident-codes-without-regard-to-letter-case-2026-10-09)): both models pass on the changed scripts and stop on the scripts as they were, with the error of 2026-10-08; on a disposable PostgreSQL 17.11 of the product's image, with scratch tables, the changed SELECT gives one name where the SELECT as it was gives two. NOT RUN: the changed SELECT against the normal database (every use is the owner's to approve); `ResearchActivationRehearsal` as a phase with the two models in it (its lines for them were executed inside the harness module, without Docker); the watch's loop against a stand-in. **What stays.** A reading in the new form names a lower-case code in upper case (`STREAM_SILENT` for `stream_silent`), so a line of the watch's log reads differently from one written before; nothing in the repository parses those lines. One more reader of counts by code exists in the harness and is not changed: `ResearchSaturation` reads the `incidents` of its stream workload, as recorded, into one PowerShell object and would fail, not pass, on two spellings; that workload records no code from a failure reason (read from `app/market_data/performance.py`), so no path to two spellings is known there. A checkout must take the changed check between runs: it is one of the nine files whose hashes three phases record and `Report` compares with the run's Build.

- **Memory.** §5.10 records B0's single-stack observation; B9 saturation/coexistence must verify the simultaneous service workload before acceptance.
- **Schema size.** The AgentStep v2 object may exceed what the model accepts. Checked in B0; fallback in §14.
- **Model behavior.** A researcher that cannot produce a valid candidate inside its budget abstains. The walk-through then needs another run.
- **Thin history and measured capacity.** About five days of quotes on 2026-10-03. INFERRED from the B0 21-day dataset cap and unchanged 20% partitions: VALIDATION and HOLDOUT each have at most 100.8 hours before gaps, below the protocol's 168 paired-hour minimum. They remain "insufficient sample" even when the default dataset fills. A future larger envelope requires new measured capacity and owner approval; M6 does not lower the minimum. Trade statistics may be insufficient for longer. The separate 21-day shadow window can still reach the paired-hour minimum, but must meet the unchanged actual-position minimum too.
- **Replay cost.** B0 measured the native replay at the one-CPU research-cluster limits and sized the dataset. Candidate, partition, staging and report overhead remain unmeasured until B9; projected throughput alone cannot pass the job budget.
- **Shadow optimism.** §5.6. Labeled, not corrected.
- **Holdout reuse.** Counted and shown, not corrected.
- **Source value.** The candidate feeds are easy to verify and may carry no price information.
- **Boundary work.** The pilot's end on 2026-11-25 brings the worker rebuild, the live shadow engine and the account model together.
- **Staging on the normal database (found in B4, NOT RUN there).** Staging reads through the `research_read` views as `asl_research`, whose statements are limited to 2 s. The collections view decides "published" by looking for one observation of the collection, and `market_observations` has no index on `collection_id`; adding one would alter an M2 table. INFERRED: the first read of a new collection can need a scan of the retained observations and may approach that limit on a cold cache. It happens once per collection and per store, a failed pass changes nothing and is repeated, and the fixture runs cannot show it. B9 measures staging at full density.
- **Thin stores after a rotation (B4).** A new version starts with at most 7 days of quotes, because main keeps no more. For up to two weeks after a rotation the daily dataset is shorter than 21 days. Seeding a new version from the retiring one would avoid that; it is not in the plan and is not built.
- **Daily sealing cost (B4).** Each sealed dataset and each shadow advance hashes its whole range once in the bridge and once more in the runner. At full density that is INFERRED to be minutes of reading per day on the research cluster; B9 measures it.
- **A candidate whose shadow ended without evidence (B4).** The shadow row records how it ended. The candidate stays `SHADOW_RUNNING` unless a prefix mismatch suspended it; B6 and the owner decide what follows.
- **The review that makes a candidate eligible (B4).** B4 reads `review_type`, `target_sha256` and `verdict` from a stored review. B6 defines that artifact; if its fields differ, the eligibility query changes with it.
- **A job's hour runs from its request (B3 behavior, found in the B4 review, unchanged).** One job runs at a time and a queued job's deadline keeps running. A trial queued behind another job, a shadow advance included, can lose part of its hour or be canceled at dispatch after spending its place in the day's budget. B4 keeps shadow advances out of that by recording one only for an idle runner. Counting the hour from dispatch would change B3's reservation rule and is left to B9's throughput measurement and the owner.
- **The staging journal has no index on the store name (B4).** It gains about 300 rows a store a day and is read by job requests and by every seal. INFERRED to stay small for years; an index would be an 0008 change.
- **Recovery after the research cluster is lost (B4 fails closed only).** The bridge refuses a store that no longer holds what was staged and ends its shadows. Putting a new store version into service afterwards is not built; `ResearchActivationRehearsal` (B9) owns it.
- **The two B4 items above that named B6 are closed.** The owner decided on 2026-10-05 that a candidate whose shadow ended without the evidence minimum is retired. B6 defined the candidate review; the eligibility query now reads its `results` (§18, B6).
- **Model behavior under definitions v2 is unmeasured (B6).** Every B6 test used a scripted model. Whether a real model produces valid v2 steps, a valid declaration inside its budget, or useful research is unknown until the owner's probes and walk-through in M6-B. Operators are plain strings in the output schema, so a model can name an unregistered one; it is refused and recorded as a trial, and it spends a tool call.
- **Budgets v2 are proposals (B6).** Steps, tool calls, experiments, the deadlines and the daily count are the plan's values. The probe budget of 60 calls for 20 probes is this batch's proposal. None has been run against a model.
- **The daily count is shared by both generations (B6).** A workflow is held to its own generation's cap, so an M5 assessment is refused once 12 parents of any kind have started that day, including source-triggered ones. This never exceeds an approved cap, but automatic work can use up what the owner would have started by hand.
- **A follow-on question is withheld from the research it starts (B6, by the 2026-10-03 clarification).** An investigation runs at the present and research at an earlier holdout start, so the question text never qualifies. The follow-on research receives the symbols only. Whether a follow-on is then worth a daily slot is an open product question for M6-B.
- **Work that waits on the bridge (B6).** The full test of a nominated candidate and the hourly storage observation are the bridge's. While it is down, a nominated workflow waits and ends `EXPIRED` at the six-hour wait deadline, and screening requests are refused once the last observation is older than 2 h 10 min. Both are recorded honestly. The candidate then stays `TESTED`: an equal declaration in a later workflow returns the existing candidate under its first hypothesis, which the later workflow cannot nominate.
- **Triggers under a runtime that is not enabled (B6).** A trigger stays queued while the runtime is `PROBE_ONLY`, `LOGIN_REQUIRED` or blocked, and is recorded `REFUSED` as `STALE` after six hours. Until Enable, every source revision ends that way. That is the intended record of a missed event, not a failure.
- **The screening time estimate is inferred (B6).** 58 s per recorded day and cost scenario, from B0's native-replay measurement. It only sizes a reservation; B9 measures candidate jobs.
- **Owner pages and routes still describe M5 (B6; the routes CLOSED by B7 on 2026-10-05, the pages CLOSED by B8 on 2026-10-06).** The M5 agent read models now answer on schema 0008, with budgets v1 and without the M6 records. B7 and B8 add those.
- **Generation 1 trimmed its prompt from the newest result (found in B6; CLOSED 2026-10-05).** When a prompt exceeded its size bound, the M5 composer replaced the newest results first, although its description said the older ones go. B6 left it as M5 accepted it. The owner approved the correction on 2026-10-05 ([DECISIONS](../../DECISIONS.md#2026-10-05--generation-1-prompt-trimming-drops-the-oldest-result-first)); both generations now drop the oldest first (§16; [ExecPlan 0020 §17](0020-m5-agent-runtime.md#correction-after-closure--which-results-an-oversized-prompt-hides-2026-10-05)). Generation 1 still has no check that a single result fits the prompt alone, as generation 2 has. The largest catalog-v1 result sized so far, 72 hourly bars with synthetic values, takes 18,028 bytes of the 65,536.
- **A tuning role can tell a locked experiment from an unknown one (B6 review; DECIDED by the owner on 2026-10-05: both codes stay).** `read_experiment` answers an unknown ID with `SCOPE_DENIED` and an existing full test or shadow with `HOLDOUT_LOCKED`. No tuning role is given such an ID and the IDs are random, so this confirms existence only to a role that already holds one. One code for both would close it and would change the contract and CP-17's wording; that is a decision for the owner.
- **A job canceled before it ran is final for its input (B3 behavior, found in the B6 review; DECIDED by the owner on 2026-10-05: it stays final).** A queued job is canceled when it is an hour old or when the permission epoch changes, and a later request for the same input returns that canceled job. A full test canceled this way is not retried, since the one retry is for `FAILED` and `EXPIRED`, so the hypothesis has no holdout evaluation and no review; the parent ends `SUCCEEDED` with `review_status = UNAVAILABLE`. A screening canceled this way leaves its candidate `TEST_QUEUED`. Whether a never-started job may be queued again is not decided.
- **A probe run interrupts research (M5 design, found in the B6 review).** Probe CP-12 raises the permission epoch. That cancels every queued or running research job and source refresh and fails every waiting generation-2 workflow, as any revocation does. Run probes when no research is in flight; B9 or M6-B should state this in the operator procedure.
- **A failing step commit holds the slot until that workflow's deadline (B6 review, bounded, unchanged).** Completions, review advances, triggers and tool handlers are isolated. The commit of a model step's own result is not: if it raised on every tick, no other workflow would get a step for up to 20 minutes. The known cause, a string PostgreSQL cannot store, is rejected before that point.
- **A review's reserve step depends on the reviewer (B6 review).** A fixed child has four steps and three tool calls. With its target in the job context a reviewer that reads both results still has one step left for a refused finish; one that makes a third call does not, and a review that ends without an artifact is not repeated. M6-B measures whether the proposed child budget is enough.
- **Marker selections are not checked for coverage (B6 review, latent).** A phase fails on a skipped test, on a failed command and when a selection is empty. It does not prove that every test of a file carries one of the selected markers; today every test in the agent test files does.
- **The two B6 entries the owner decided on 2026-10-05 are closed (B7).** `read_experiment` keeps `SCOPE_DENIED` for an unknown ID and `HOLDOUT_LOCKED` for a locked one. A job canceled before it ran stays final for its input; whether a job that only aged out behind other work may be queued again is decided with B9's measurement of when a job's hour starts. "Owner pages and routes still describe M5" is closed for the routes by B7 and stays open for the pages (B8).
- **An owner cancel no longer ends the waiting workflow as revoked (B7 review; DECIDED by the owner on 2026-10-06: the B7 behavior stays).** A job canceled for an owner request records `OWNER_CANCEL`. The research workflow that asked for it receives the `CANCELED` completion and takes its next step, which can spend further model steps and end in a proposal that nominates nothing. Before the review it ended `FAILED` with `CAPABILITY_REVOKED`. The owner keeps this: nothing was revoked, so the workflow is not ended as revoked ([DECISIONS](../../DECISIONS.md#2026-10-06--two-b7-behaviors-kept-an-owner-cancel-lets-the-workflow-go-on-a-recorded-shadow-stop-takes-no-further-mark)). The B8 cancel dialog states it before the owner confirms.
- **A recorded shadow stop takes no further mark (B7 review, B4 code changed; DECIDED by the owner on 2026-10-06: it stays).** A result that arrives between the owner's request and the bridge applying it is kept as a result and is not a mark. A shadow whose last advance was already running when the stop was recorded therefore ends `STOPPED` and its candidate is retired, even if that advance would have completed the evidence. The owner keeps this ([DECISIONS](../../DECISIONS.md#2026-10-06--two-b7-behaviors-kept-an-owner-cancel-lets-the-workflow-go-on-a-recorded-shadow-stop-takes-no-further-mark)). The B8 stop dialog states it before the owner confirms.
- **A rejected candidate's shadow keeps running (B7, unchanged B4 behavior).** Rejecting a promotion moves the candidate to `REJECTED`. A shadow of that candidate, if one is still open, is not ended by the rejection; the owner stops it with the stop route. No B7 test has a rejected candidate with an open shadow.
- **Owner-started and SYSTEM-started promotion workflows can coexist (B7 review, INFERRED, not driven by a test).** `PROMOTION_IN_PROGRESS` is checked by the owner route under the owner lock; the scheduler that starts a promotion for an `EVIDENCE_READY` candidate does not take that lock. Both can be queued for one candidate. The second to finish is refused, because the candidate is no longer `EVIDENCE_READY`, so the cost is model steps and not a second request. Closing it means the scheduler taking the owner lock, or a partial unique index in a later migration.
- **Lock order between a source revocation and the agent worker (B7 review, INFERRED, not reproduced).** The API takes the publication lock and then raises the epoch; the worker holds the epoch and then takes the publication lock when it fixes a cutoff at the present. If both wait on each other, the API's one-second lock timeout or the deadlock detector ends the owner's request as `503 TRY_AGAIN` with nothing recorded, and it can be sent again. A test holds each lock alone; none drives both at once.
- **Another database identity can shape a row like an owner request (B7 review, low; needs a migration).** The insert guard of migration 0008 does not require a new job or shadow to have no owner request, and a refresh row of another actor may carry an idempotency key. `asl_agent` and `asl_research` hold INSERT on jobs, `asl_research` on shadows. A compromised worker identity could insert a row that reads as owner-canceled or owner-stopped, or occupy a key. It can only remove work and no tool path sets these columns. B7 changes no migration; the guard belongs in the next one.
- **M4 and M5 request bodies keep their coercion (B7 review).** B7 made the integers of its own bodies strict. The older bodies still accept `true` or `"1"` for an integer, and every body reads a duplicated JSON key as its last value. No authority follows from either; tightening them changes shipped routes and is not part of B7.
- **M5 mutations other than the workflow start still answer a lock timeout with an unhandled error (B7 review, unchanged).** `503 TRY_AGAIN` covers the approvals, the workflow start and the three M6 requests. Enable, Disable, the probe request, the workflow cancel and the profile composition keep M5's behavior.
- **Read models are not indexed for growth (B7 review, INFERRED from the code, not measured).** The status view reads the staging journal, which has no secondary index and gains several hundred rows a day; the hypothesis and dataset lists count jobs and candidates per row without an index on the columns they join; a candidate's reviews are found by JSON predicates over all artifacts. The API identity's statements are bounded at two seconds, and a read that reaches the bound now answers `503 TRY_AGAIN`. `PerformanceApi` (B9) measures them; an index is a later migration.
- **No heartbeat row for the bridge or the fetcher (B7).** `SystemStatus.research` and `.sources` are derived from what those services record while working: the storage observation and the fetch records. A bridge that has been down for less than 2 h 10 min still reads `idle`, and a fetcher that stopped reads `ready` until two poll intervals have passed.
- **The M6 routes compare the schema revision by equality (B7 review).** A migration after 0008 must move `M6_REVISION` with it, or every M6 route answers `503` and both status fields read `unconfigured`. [API_CONTRACTS](../contracts/API_CONTRACTS.md#m6-owner-routes-execplan-0023-b7) states this.
- **Rollout order: the web before the API (B7).** The web released before B7 refuses unknown fields. If the API is updated first, the status page and every agent page show their error state until the web is current. B10's deployment procedure must order them.
- **Four routes beyond §5.9, no on-demand shadow advance, `WITHDRAWN` unwritten (B7).** B7 added the two key lookups and the experiment detail and cell reads, without which a page cannot resolve an unknown outcome or show a result. §5.9 lists no route for an on-demand shadow advance and B7 adds none. `WITHDRAWN` is a defined promotion state that nothing writes.
- **No browser path reaches the M6 routes before B8 (B7; CLOSED by B8 on 2026-10-06).** The private API requires the service key and the session. The same-origin functions with their Origin and CSRF checks, and the pages, came with B8 (§18).
- **The M0 to M2 route tests are in no M6 phase except `tests/test_api.py` (B7).** `ApiAuth` runs the M0 file because it pins `SystemStatus`. The M1 and M2 route tests are not selected by any M6 phase; B7 changes none of their routes. B9's full regression decides whether they join.
- **Phase time limits add up to more than some phase deadlines (B7 review).** `Checks` reserves 18 minutes and its commands' own limits add up to more; a run that slow would be stopped at the deadline and fail, never pass. `ApiAuth` was given 17 minutes so that its three limits fit.
- **Not covered by a B7 test (B7 review).** A tool result marked `shadow: true` at the API level (the rule is tested as a pure function); the M5 routes against a database that is really at 0007 (B9 `MixedVersion`; B7 tests the branch they take); more than 100 promotions; several revisions of one evidence item; a `SHADOW` dataset in the dataset list.
- **Agent tests tick an orchestrator directly, on a lease only the test helper renews (found in B7's first acceptance attempt).** The M5 activation test runs all twenty probes on one orchestrator. Its lease lasts ten seconds and the test did not renew it, so the test failed whenever it took longer: three of six measured runs. The test helpers now renew the lease before each tick, as the worker's keeper does every two seconds. A direct call of another orchestrator method more than ten seconds after the last tick would still be fenced; no test does that today. How long the test took before B7 was not measured.
- **A fourth consequence list (B8; for the owner to confirm).** The owner approved additive consequence lists on the envelope, a source version and a promotion. The review found that a refresh and a source approval said nothing of the event investigations new items can start, so each source also carries `refresh_consequences`. It is the same kind of field (read-only, code-owned, no route, body, grant or migration changed) and one more than was named.
- **The stop list's wording is inexact beyond `EVIDENCE_READY` (B7 code, B8 review).** `CANDIDATE_RETIRED_UNLESS_EVIDENCE_READY` is right for a candidate that is `SHADOW_RUNNING` or `EVIDENCE_READY`. A stop retires a candidate only while it is `SHADOW_RUNNING`, so for one at `MAIN_APPROVAL_PENDING` or `REJECTED` with an open shadow the code says too little. The stop dialog states the candidate's own state and which case applies. Renaming the code changes a B7 response value and is left to the owner.
- **The scheduler's promotion start is not gated on the envelope (B8 review, B6 and B7 code, unchanged).** After the envelope is revoked, a promotion workflow can still be started for an `EVIDENCE_READY` candidate. It can only write a request the owner may reject; whether it should wait for the envelope is an owner decision.
- **No frame policy (older than B8).** The web sets no `X-Frame-Options` header and no `frame-ancestors` policy. A page on another local origin could frame the application, including the confirmation dialogs B8 adds. Setting one is a change to every page and is not part of B8.
- **"Not recorded … safe to submit again" can be early (M5 pattern, B8 review).** The web gives up on a private call after five seconds; the API's handler is not canceled by that. A check of the outcome right afterwards can answer "not recorded" before the first request commits. A decision is protected by the version the owner saw; a refresh repeated this way is refused by the refresh interval. The sentence is shared with M4 and M5.
- **Older server functions still send a parser's text to the browser (B8 review).** B8 gave the M6 reads fixed error sentences. The M4 and M5 functions still throw the schema library's issue list (private field paths, not values) and the JSON parser's message when a private response is not its contract.
- **Stored JSON is passed through (B8 review).** About twenty fields of the M6 read models are stored JSON values whose inner shape the web does not check (`resources`, `outcome`, `attribution`, `gate_evidence`, `document`, `evaluation`, staging gaps). They are drawn as text. No secret was found in what the current views put there.
- **The shared table primitive's scroll container (B8 review).** A wide table scrolls inside a container that is not a named region and cannot be focused. B8 made its own scrolling texts reachable; changing the primitive changes every table of M1 to M5.
- **An M4 Approvals card is cut off at 390 px (found by B8's clipping check, M4 code, unchanged).** A definition whose ID is one long word (`COST_SCENARIO_HYPOTHETICAL_H2_STRESS`) is wider than its card title at 390 px and is clipped. The M4 section is not changed by B8; its own browser phase checks the page width only.
- **Read-model observations from building the fixture (B8, engine unchanged).**
  - `research_jobs.workflow_id` is never written, so an experiment page cannot link a job to the workflow that asked for it and says "None recorded".
  - The status view lists at most 20 gaps of a staging pass and gives no total; the page says so.
  - A store's `refusal` is the newest refused pass even after a later pass staged; the page compares the two times.
  - A dataset's `fixture` flag is false for synthetic rows a code path sealed; the page shows `evidence_kind`.
  - Probe runs are ordinary rows of the workflow list and fill its first page.
- **A cursor inside its pattern and beyond the sequence shows the error state (B8 review).** The API answers `422 INVALID_CURSOR`; the page shows its read error, not an empty page. Only a hand-edited address reaches it.
- **The candidate page's shadow link opens the shadows list (B8).** The list has no filter by shadow, so the link leads to its first page, not to that shadow.
- **API samples are committed (B8).** 41 files, about 530 KB, written by the fixture from a seeded database. A reseed changes every ID in them, so they are replaced as a set. `BrowserResearch` derives fresh ones in each run and runs the same tests on them, which is what ties the web to the current API.
- **`BrowserResearch` has an order and a window (B8).** It needs this run's verified `Generate` for its sample check, and its fixture refuses to start outside HH:07 to HH:48 UTC because the seeded status reads `idle` for 2 h 10 min only. With a 35-minute reservation it starts by HH:23.
- **Not covered by a B8 test (B8 review).** The dialog's text while it closes; a double activation of a confirm button beyond its disabled state; a tool result marked `shadow: true` on the workflow page (no fixture workflow reads a shadow); more than 25 `EVIDENCE_READY` candidates in the start dialog (the note is tested with a cursor, not with 26 rows); the M5 browser phases after the start button's rename.
- **B9, DECIDED by the owner on 2026-10-07 (was open): the schema change stays in migration 0008.** The year-of-rows API measurement failed before it and passes with it (§18, B9): three indexes and the stored generated column `research_datasets.purpose` on tables that 0008 creates. The owner's answer: "All in 0008", because 0008 has never been applied to the normal database ([DECISIONS](../../DECISIONS.md#2026-10-07--m6-b9-what-stops-a-test-run-beside-the-pilot-the-owner-scripts-and-the-pilots-own-rows-the-schema-change-in-0008-and-the-market-workers-log)). Nothing changed in the migration for this answer; it is no longer provisional.
- **B9, OPEN, INFERRED, not measured: a full test on the 21-day cap does not fit the job bound.** `runner.replay_cell` replays the market from the dataset's first sequence to each cell's end, and `protocol.estimate_seconds` counts each partition's own window once. At the reference rule's 72-hour hold a full test replays 4.8 times the dataset's days minus twelve: 88.8 recorded days on 21 days (30.0 stepped, 58.8 only read before a cell's start), about 5,100 s at B0's 57.5 s a day if both kinds cost the same, against `max_job_wall_seconds` 3,600; the reservation says 2,436 s. A screening replays about 23 days. A shadow dataset begins 302 hours before its freeze, so a 21-day advance replays about twice 33.6 days. `PerformanceResearch` measures the 14-day jobs and projects 21 days; by decision 3 a projection over 3,600 s fails the phase. If it does, the choices are the owner's: replay each cell from its own start with its warm-up, a shorter dataset, or another bound. None is made here. (The memory side of the same replay, every quote before a cell's start held until its first step, was a defect and is fixed: §18, B9.)
- **B9, DECIDED by the owner on 2026-10-07 (conditional), and what the implementer found on reading the code the same evening.** The owner's answer for the case that the measurement confirms the figure above: fix the replay so that each cell is replayed from its own start with its warm-up, provided results stay identical; otherwise the question returns to the owner ([DECISIONS](../../DECISIONS.md#2026-10-07--m6-b9-a-full-test-at-the-21-day-cap-and-reruns-in-an-accepted-run)). INFERRED from `protocol.identity`, `protocol.nominal_partitions` and `runner.replay_cell`, by arithmetic and not by a run: on 21 days the two holdout cells begin 16.8 days in and the two validation cells 12.6 days in, and the warm-up is 302 hours, which is 12.58 days. Replaying a cell from its start less the warm-up therefore shortens only the holdout cells, by 4.2 days each: 8.4 of the 88.8 recorded days, under a tenth, where the gap to the bound is about three tenths if both kinds of days cost the same. The option as it was put to the owner ("about two thirds of a 21-day full test is rows read before a cell starts") is right about the share and overstated what the named change removes. A change that removes most of it would feed the warm-up from the final hourly candles alone, since the indicators read at most 300 hourly bars, and quotes only from shortly before a cell's start; whether results stay identical under that is NOT ESTABLISHED and needs the replay path read whole. Whether any change is needed is NOT KNOWN before the measurement: the figure of about 5,100 s assumes that a day that is only read costs as much as a day that is stepped, and `PerformanceResearch` now measures the two rates apart. No product change is started before that number. The measured rates and the options go back to the owner.
- **B9, OPEN, INFERRED, not measured: idle dispatch sits at its budget.** The bridge looks for a queued job once a pass, every 5 s, so the delay from a request to the work row is about uniform up to one pass and its p95 is about 0.95 of a pass period plus the pass itself, against 5 s. The day cap of twelve jobs leaves eight direct samples in one UTC day, which have no p95 of their own. `PerformanceResearch` therefore judges a p95 derived from the measured pass periods and each sample's measured time from its pass's start to the store, labeled INFERRED; the eight samples are reported. That figure may honestly exceed 5 s, and the phase then fails. A request made while the bridge seals the daily dataset waits for the seal; the seal's seconds at the bridge's limits are recorded and not judged.
- **B9, DECIDED by the owner on 2026-10-07 (was open): what stops a test run beside the pilot.** Decision 8 of 2026-10-06 lists "no new ... execution incident" and "no QUEUE_OVERLOAD or COLLECTION_GAP during the phase". OBSERVED with no isolated stack running (read-only series, 2026-10-06 21:25 to 2026-10-07 13:14 UTC, 161 readings, one every five minutes outside HH:58 to HH:07, none failed; the only test containers in that time were four lint containers without a network, for seconds each; the series was ended by hand at 13:15 UTC): `PROTECTION_UNAVAILABLE` rows went from 488 to 510, eleven start and end pairs in the first four hours and none in the twelve hours after 01:21; two collection gaps with a silent stream (between 01:06 and 01:11, and between 02:41 and 02:46 UTC); one `CLOCK_UNCERTAIN` and one `CLOCK_UNVERIFIED` row between 08:03 and 08:08 UTC; no container restarted and the lease stayed at epoch 4 and held. As written the criterion stopped `m6-b9i` at 21:18:38 on a pair the pilot wrote by itself. The owner's answer: stop at once on a container or lease change, a new segment or downtime event, `QUEUE_OVERLOAD`, a missing HH:05 report, or any execution incident other than `PROTECTION_UNAVAILABLE`; record collection gaps and `PROTECTION_UNAVAILABLE` pairs with time and phase, and stop on more than two gap episodes or more than four pairs in thirty minutes ([DECISIONS](../../DECISIONS.md#2026-10-07--m6-b9-what-stops-a-test-run-beside-the-pilot-the-owner-scripts-and-the-pilots-own-rows-the-schema-change-in-0008-and-the-market-workers-log)). IMPLEMENTED as `Get-PilotWatchVerdict` and `Get-ReportVerdict` in `tools/lib/Research.psm1` and the loop `tools/m6-pilot-watch.ps1`; replayed through the rule, the 161 readings of the series give no stop, and their densest thirty minutes hold six rows. The watch has NOT RUN beside a test yet. What it cannot see: anything between two readings five minutes apart that leaves no row, and the pilot between HH:58 and HH:07, when it reads nothing.
- **B9, DECIDED by the owner on 2026-10-07 (was open): the owner scripts report the pilot's own rows and do not stop on them.** `tools/m6-deploy.ps1` and `tools/research-activate.ps1` compared the count of execution incidents before and after their run and stopped when it changed; the deployment did so at its last step, when everything is replaced, and the activation then unwound itself. The owner's answer: a `PROTECTION_UNAVAILABLE` pair or a collection gap during the run is named by its code in the output and the record and stops nothing; any other new execution incident, and any container, lease, segment or downtime change, still stops the script ([DECISIONS](../../DECISIONS.md#2026-10-07--m6-b9-what-stops-a-test-run-beside-the-pilot-the-owner-scripts-and-the-pilots-own-rows-the-schema-change-in-0008-and-the-market-workers-log)). IMPLEMENTED in both scripts (`Get-IncidentJudgement` in `tools/lib/Research.psm1`; a count that fell, a new code, and a total no code accounts for stop too) and walked by the deploy model; NOT RUN against a pilot. The market worker's incidents during a script run were already reported and not judged.
- **B9: why the real market worker restarted twice on 2026-10-06 (OBSERVED from its log on 2026-10-07, with the owner's approval of one read-only call; outside this batch).** Both exits, at 13:51:57 and 15:53:56 UTC, are `market_worker_fatal` with `UNEXPECTED_EXCEPTION`: the hourly retention (`maintain_retention`, `store.prune_retention`, `asl_prune_market_evidence`) was canceled by the statement timeout inside `DELETE FROM market_payloads WHERE id = ANY(payload_ids)`, at its foreign-key check. The worker recorded a collection gap of under a second with the failure `OperationalError` in phase `maintenance`, closed its stream and exited; Docker restarted it, it held its lease again three to four seconds later, and the stream was connected again about 30 s after the exit. The prune right after each restart succeeded (21,547 and 21,426 records), and the one at 14:53:09 succeeded without a restart. The six other gaps of that afternoon are `stream_silent`: the provider's stream delivered nothing for ten seconds and the worker reconnected. At the first exit no isolated stack existed on the host: the first B9 harness command of that day ran at 14:07:18, and only the read-only observer had run, from 13:48:37 to 13:49:40. At the second, run `m6-b9c`'s `PilotCoexistence` stack was up and waiting through its quiet window. NOT KNOWN: why the statement exceeded its timeout at those two times, and whether load on the host played a part in the second. No restart followed in the next 21 hours (restart count 2 at 13:14 UTC on 2026-10-07). This replaces the earlier entry here, which gave the cause as not known. Its inference from the timing, that the tests had no part, holds for the first exit by every harness command log of that day and is not settled for the second. It is a defect of the market worker (M2 code): a statement timeout in its hourly maintenance ends the process. This batch does not change the worker; the finding was flagged as a separate task. For B10: the retention runs when an hour has passed since the last one, so its minute moves by about a minute an hour (13:52, 14:53, 15:54 on 2026-10-06) and will lie inside the deployment window on some days; a worker that exits during a deployment changes its restart count and stops the deployment at its last check. The deployment plan names the minute to stay away from.
- **B9: the read-only pilot check did not run around the afternoon's phases.** Its script had a defect until 20:45 UTC. The readings decision 8 asks for exist only from then on.
- **B9, DECIDED by the owner on 2026-10-07 (was open): a failed or interrupted phase may be started again on the same Build, on record.** Until then `Report` refused a run in which a phase was started twice, was interrupted, or had a failed or superseded record, so that one failure outside the product cost a fresh run of about a day; `PerformanceResearch` alone takes eight test windows and `ResearchSaturation` two. The owner's answer: a rerun is allowed on the same Build and the same tree, every attempt stays in the record, the report lists each rerun with its cause, and each one is put to the owner in the B9 report to accept or reject ([DECISIONS](../../DECISIONS.md#2026-10-07--m6-b9-a-full-test-at-the-21-day-cap-and-reruns-in-an-accepted-run)). IMPLEMENTED in `Invoke-M6Report`, NOT RUN: every attempt's tree must still be the Build's; a phase must have returned in its last attempt and its record must be of that attempt; earlier attempts are listed under `reruns` with how they ended and with the error of their failed record; failed and superseded records are kept and listed. Still refused: a tree that changed, a Build of an uncommitted tree, a phase whose last attempt did not return, a scan that started before another phase ended. What a rerun cannot repair: `Migration` cannot run twice on one run, and a second `Build` gives other images than the ones the earlier phases name. A phase that passes only on a second attempt may hide a fault that comes and goes; that is why a rerun is listed for the owner and not accepted by the report.
- **B9: where a kill lands is not chosen.** The bridge is killed three times once its session on the catalog is seen. The record counts how many kills came before the delivery committed; that count can be zero. The in-process tests place that failure exactly.
- **B9: the deactivation removes logins with `psql` inside the database containers,** as the identity that owns each cluster, not through `research-admin`. It therefore needs no secret file and no image. `app/research/identity.py` is still the only place that grants a login.
- **B9: no isolated stack runs a market worker.** A container of that service on the pilot's market image sleeps in its place. It shows that the scripts leave a container of that service alone; it shows nothing about a collecting worker.
- **B9: a rollback of a release with a service down is not held to HH:15–HH:45.** It is refused only between HH:58 and HH:07 UTC and between 23:50 and 00:20, because it builds nothing and waiting leaves the application down. At schema 0008 it still takes a backup first. The owner sees this rule again in the deployment plan before B10.
- **B9: a deployment needs the image IDs of five names.** A `:pre-m6` tag is created only from an image named in `-ExpectedPreM6Images`. The script's default holds the three services' images of 2026-10-06; the images behind the names `migrate` and `agent-admin` have to be read in the read-only look before the deployment and passed in.
- **B9: an image built twice has two IDs on this host.** OBSERVED on `m6-b9i`: four builds of the api image from one tree, four IDs. The deploy script's check that a built image is not its `:pre-m6` image can therefore never fire and proves nothing, and the secret scan can identify the rehearsal's images only by their names. The deploy script builds `migrate` once and uses that image by its ID for the restored copy and for the installation.
- **B9: branches of the deploy script that no container state of the rehearsal reaches** (a recreation that fails, a service in two containers, an agent worker without a container, a downgrade that waits for a lock, a tag that cannot be read, a `git` that does not answer, a build that moves a pilot image name, a rollback without its baseline file, a new execution incident at the last check, a helper that cannot be looked for, a flag under a key in another letter case) are walked only against a model, where a function answers for `docker`. That is not evidence about Docker.
- **B9, not changed: the older activation tools' reader and writer.** `tools/pilot-activate.ps1`, `tools/pilot-deactivate.ps1`, `tools/agent-activate.ps1` and `tools/agent-deactivate.ps1` read the env file with `Get-EnvValue`, which takes the first assignment of a key where Compose takes the last, and write it with `Set-EnvFlag`, which rewrites `KEY=` lines only. Neither refuses an env file that Compose reads differently, a key in another letter case included. The M6 scripts use this batch's reader and writer. Pull request MentorAliu/adaptive_spot_lab#30 (another session; VERIFIED read-only: MERGED on 2026-10-07 at 12:59:54 UTC as `0f395a9`, and merged into this branch as `73789b9`) corrected which file those four tools write and made `tools/lib/Pilot.psm1` stop on an error in its own functions however a tool is started. It left the reader and the writer as they are: its entry in [DECISIONS](../../DECISIONS.md#2026-10-07--pilot-and-agent-tools-the-env-file-path-and-what-was-left-out) records the owner's decision that the older tools take this batch's reader and writer only after this batch's pull request is merged, as a follow-up that is not started and not part of this batch.
- **B9: the M6 owner scripts refuse env files that Compose would read.** A key in another letter case, a quoted value over more than one line, a carriage return inside a line or a byte that is not UTF-8 stops `tools/m6-deploy.ps1` and `tools/research-activate.ps1` before anything changes, with a sentence that says what to rewrite. The owner's `.env` is never read by the implementer, so whether it holds such a line is NOT KNOWN before the first run of B10, which would stop at its read-only preflight if it does.
- **B9, NOT RUN, measurement design points for the owner (from the helper that reworked the measurements).**
  - When a measured job succeeded but its cells do not give a stepped and a read-only rate, the phase fails as "could not be projected". The helper had judged the one-rate figure in that case; the implementer removed that, because for an advance the one-rate figure is about 1.26 times the measured seconds (33.6 recorded days a cell against 26.6) where counting every cell second as stepped gives 1.5 times (21 days against 14), so it could pass a job the three parts would fail. The one-rate figure is still recorded. One case can fail a fast job this way (fourth review, by arithmetic, NOT RUN): a full test whose later cells cost less than their stepped days at the first cells' rate, for instance a holdout that holds no position, leaves a negative remainder for the read-only days. The reviewer's suggestion for that case alone is to judge the one-rate figure, which for a full test with a negative remainder lies above a projection cell by cell by their arithmetic; the implementer did not verify that arithmetic against the cell layout and judges nothing in that case. The owner decides whether a figure is judged there.
  - The 21-day shadow advance is judged with every cell second of the measured advance counted as stepped, which is 1.5 times its cell seconds plus the digest by its days. That is never below the true figure and is above it by half the cost of the days read before the freeze. A measured 14-day advance above about 2,400 s therefore fails the phase by projection, which §19 already expects (INFERRED: about 3,900 s for 21 days).
  - The saturation feeder's jobs hold for 29 hours (the measured jobs of `PerformanceResearch` keep 72). On the seven-day store of decision 2 that is INFERRED to give the longest job, 620 to 1,070 s; the phase requires rows staged after a job's 660th second (ten minutes and a margin of one) and fails as not shown when no job runs that long. A longer store needs an owner decision and a second setup window.
  - The saturation backlog's rows carry a 29-byte label, not a frame-size body; the staging rate is judged on frame-size bodies in `PerformanceResearch` only.
  - The seals are measured at the bridge's half CPU. Their part is reserved 48 minutes and their limits are 1,200 and 900 s, raised from 900 and 700 s when they moved to that container. No seal time has a budget.
  - Two parts of `PerformanceResearch` hold limits that cannot all be used (fourth review, by arithmetic): the seals and the dispatch samples (limits of about 3,400 s in a part of 2,760 s) and the staging part (about 3,250 s in 2,640 s). Each call is cut to what its part's deadline leaves, so nothing runs past its part; the parts pass only when the seals and the backlog load stay well under their limits, and fail otherwise. A seal that ends just inside its 1,200 s implies a shadow window of about 1,520 s against a limit of 1,500 s. Whether the parts fit is NOT MEASURED.
  - Nothing bounds how early the reader of the bridge's heartbeat must be ready. It starts inside the bridge's 0.5 CPU and 256 MiB twenty seconds before the first dispatch request; if its start takes longer, the first sample has too few pass instants before it and the part fails as not read. A false failure, not a false pass.
  - The store holds 27 days, one day below the rotation at 28 days of quotes, and is INFERRED to take about 8.9 GB against a rotation size of 12.3 GB. Neither figure is measured.
  - `PerformanceApi`'s 35 minutes were not re-measured against the heavier year of rows, and the search over extracts of 16 KB may miss its 150 ms; three of its thirty queries match every item.
- **B9, NOT RUN: what the secret scan's dumps cost.** A plain dump of each database is written into that database's volume, one at a time, on the disk the real pilot's database uses, and only when twice the database's size and 2 GiB are free. If the largest store of a run has no such room the database is reported as not searched and the phase fails. Its time (three Docker calls for each of about fifty databases, the dumps and one pass of `grep` each) and its effect on the pilot's latency are not measured; only an observed run shows them.
- **B9: journal reads by outcome alone scan the journal.** `any_lost` on every status request, and `catalog_live` and `replaceable` in every bridge pass, read the staging journal by outcome without a leading index column: 1.5 ms and 0.18 ms at a year of rows on the disposable measurement database, within every budget. `source_fetch_history` does not serve the fetcher's `max(next_allowed_at)` by host.
- **B9: reads that are within budget and grow with the catalog.** `/v1/research/hypotheses` counts candidates per hypothesis without an index (67 ms sequential, 285 ms with five readers at a year of rows); `/v1/research/candidates` reads every candidate's latest state before a rare-state filter can fill a page (24 ms). Neither needs a change for the declared budgets.
- **B9: the cutoff-filtered search budget is measured in `PerformanceApi`,** on the year of rows, and not in `PerformanceResearch` as §10 lists it.
- **The B8 points above stay as the owner left them.**
- **M6-B, after the performance pull request ([ExecPlan 0025](0025-research-job-cost-and-search.md), merged on the owner's decision of 2026-10-09).** Closed by it: the analyst's search, MEASURED at 87.36 ms at p95 against 150 ms on run `m6-p2a`; and `PerformanceApi` and `PerformanceResearch` now fail on a miss. **Still open, and conditions of the M6-B activation:**
  - the four job times are NOT JUDGED on the new build: the pilot watch stopped `PerformanceResearch` before its projection. One screening on 9.6 days took 168.9 s on the store of 27 days. By the implementer's estimate the shadow advance over 21 days still misses 3,600 s;
  - the measurement itself ran beside the pilot when the real market worker recorded a `QUEUE_OVERLOAD`, which stops a test run by the owner's rule. Whether the load caused it is not known. When such a test runs beside the pilot again is the owner's decision;
  - a job's renewing thread ends its renewals after one failed renewal, and a batch of a second leaves less room before that happens. A change that asks again is written and tested on a copy of the tree, and is not merged ([ExecPlan 0025 §13](0025-research-job-cost-and-search.md#13-decision-log)).
