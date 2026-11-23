# Evidence, research and feedback workflows

**Since [ExecPlan 0035](plans/0035-a-simpler-app-that-trades-by-itself.md) (2026-10-21), Workflow B and the promotion half of Workflow C are off** ([DECISIONS](../DECISIONS.md#2026-10-21--the-owner-asks-for-fewer-pages-and-no-research-execplan-0035)): the agent worker queues no scheduled research, records no follow-on, starts no `RESEARCH_V1`, `CANDIDATE_REVIEW_V1` or promotion workflow, and ends what was open with `RESEARCH_OFF`; the update retires the research runner, bridge and cluster ([DOCKER](contracts/DOCKER.md#research-services-retired-execplan-0035)). Workflow A (event investigations and market decisions), the approved sources and the outcome reviews run as before. The definitions still name the research templates, so what this document says of them is the design they were built to, kept for history.

## Purpose

Turn agent discretion into recorded, testable research rather than unconstrained speculation. These workflows are project design proposals, not a vendor strategy or a demonstrated trading edge. Agents may pursue alternate hypotheses and request permitted evidence; every consequential operation uses the application tool gateway.

## Approved evidence universe

Market observations remain the first mandatory input. Add external event/news sources through a versioned source registry: publisher, exact HTTPS host, GET-only path templates with typed parameters, no redirects, symbol/topic scope, update semantics, license/terms, retention rights, size/rate/time budgets, code-registered parser, timestamp/availability behavior and quality checks. A source is enabled only after its adapter and rights are reviewed and the owner approves its exact version hash. A disabled source must be shown as unavailable, not silently replaced by generated news.

Possible source categories to evaluate are exchange status/announcements, project network-status/release reports and official scheduled macro releases. These categories are not claims that any particular feed is connected. Store the publisher's event time, publication/update time when actually available, local receipt and earliest usable time separately. No timestamp may be invented to make an event appear predictive.

The analyst can search the approved local corpus and request a refresh of registered endpoints. It cannot browse arbitrary URLs, log into private accounts or buy data. The external fetcher enforces the source definition and SSRF controls; an article's instructions cannot become a tool policy. Independent corroboration is required only by a declared rule for the claim type; do not invent a second confirmation or count syndication twice.

### B5 implementation boundary (ExecPlan 0023)

IMPLEMENTED in `app/sources/`: the registry, the fetcher, the evidence corpus, search and `SOURCE_REVISION` trigger records. Isolated evidence is in [ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#18-completion-evidence).

- **Registry.** A source version is usable only when the code knows its exact hash, its document passes validation and the owner's latest approval of that hash is `APPROVE`. The two seeded release feeds are `PROPOSED`, so they are shown as unavailable and are never fetched.
- **Polling.** The fetcher queues one request per approved version and registered poll interval, inside the version's hourly budget. A failed, timed-out or rate-limited fetch is recorded and spends the budget; the next poll waits for the stated reset, or for the registered back-off when none is stated.
- **Evidence.** Each new release or revision becomes one immutable item with the publisher's times as supplied, the local receipt time and the availability time. A repeated answer adds nothing.
- **Triggers.** A fetch creates at most one trigger per symbol in the source's scope. The trigger carries every item stored since the previous one, led by the newest. Inside the cooldown of a source and symbol, new items are stored and searchable and the trigger is deferred: the first successful fetch after the cooldown creates it, so nearby revisions are coalesced and none is dropped. A trigger is a record: nothing in B5 starts a workflow from it.
- **Search.** Plain terms over approved items, limited by the scope's cutoff before ranking, with at most ten results. Ranking is over the newest 500 matching items the scope may see ([ExecPlan 0025](plans/0025-research-job-cost-and-search.md#54-search)), so what a search costs does not grow with the corpus. Prior artifacts are returned as labeled references, never as text.
- **Not in B5.** The `search_evidence` and `request_source_refresh` tools, the completion that returns a refresh to a waiting workflow, the scheduler that consumes a trigger and the cutoff of a `RESEARCH_V1` context are B6. The owner routes and pages are B7 and B8. No real feed has been fetched: that path is NOT RUN until the owner approves a source version and activates the fetcher in M6-B.

## Workflow A: event investigation and market decision

1. Ingestion/scheduler emits a validated trigger with event ID, source and receipt/availability times, affected symbols, quality and snapshot reference. M6 implements source revisions and scheduled research only. Finalized 1h bars, portfolio/order events and scheduled trading reviews are M7 trigger families. A 4h or new event trigger requires the corresponding policy scope.
2. Deduplicate by source/event revision and coalesce nearby low-priority triggers. Enforce code-owned cooldowns and budgets. Do not call every role on each market tick.
3. Analyst reads the snapshot, requests needed evidence and records `MarketAssessment`: known observations, calculations, hypotheses, competing explanations, missing inputs, invalidation and expiry. A bullish/bearish label is interpretation, not a calibrated probability.
4. A material unresolved thesis can become a bounded research request, after the fixed assessment review. M6 ends with research/review or a pending promotion. Steps 5–7 and direct main-policy decisions require M7; a fresh backtest is not required before every permitted M7 trade.
5. Coordinator drafts an action or abstention. The required evaluator sees exact evidence and draft hash. It checks support, contradictory evidence, stale inputs, policy scope and unsupported claims; its review is not authority to violate hard limits.
6. Coordinator submits a qualifying draft. The server recomputes current state and financial constraints; the paper broker and ledger perform the effect. Rejected drafts remain in the decision record.
7. Link outcome observations/fills/costs to the original decision. Preserve the original hypothesis and uncertainty; do not rewrite a thesis after the result.

## Workflow B: hypothesis to isolated experiment

`ResearchEnvelopeVersion` is owner-approved before autonomous research. It constrains datasets and time partitions, supported strategy operators/templates, search domains, candidate/trial counts, CPU/memory/time/storage, concurrent jobs and allowed experiment modes.

A research request contains a falsifiable hypothesis, why the feature should matter, competing null/baseline, exact candidate declaration, data requirements, registered metrics, development/validation periods, cost scenarios, resource estimate, and stopping criteria. The runtime cannot invent measured values to complete required fields.

Candidate lifecycle: `DRAFT` -> `VALIDATED` -> `TEST_QUEUED` -> `TESTED` -> `SHADOW_ELIGIBLE` -> `SHADOW_RUNNING` -> `EVIDENCE_READY` -> `MAIN_APPROVAL_PENDING` -> `MAIN_APPROVED`, with `REJECTED`, `SUSPENDED` and `RETIRED` branches. State transitions are server-controlled and carry gate evidence. Early research eligibility does not imply main eligibility.

M6 implements the lifecycle only through `MAIN_APPROVAL_PENDING`. As ExecPlan 0023 §5.2 specifies, `MAIN_APPROVED` remains a defined lifecycle value, but every M6 transition to it is refused; it becomes reachable only with M7 authority. M7's migration `0009` (B6 of ExecPlan 0026) admits `MAIN_APPROVAL_PENDING` -> `MAIN_APPROVED` only when the agent worker applies the owner's current approval of a `PROMOTION_V2` request, citing its row; a revocation moves the candidate to `SUSPENDED`. The researcher's request queues the registered screening set; SYSTEM owns nominated full tests/holdout and eligible shadow scheduling.

Within the research envelope, the researcher can register and test candidates automatically. New code/operators or larger domains need reviewed development and approval. A candidate that is syntactically valid but fails risk/data/resource checks does not run. Identical normalized candidate/dataset/partition/cost/protocol/code inputs reuse an existing result unless a new explicitly identified experiment is warranted. A result from one cost scenario cannot stand in for another.

Use only the registered declarative grammar for automatic runtime research. Indicator operators, boolean rule composition, bounded parameters and registered exit templates must be enumerated and implemented with tests. No eval, arbitrary imports, generated shell, SQL, unbounded recursion or downloaded executable strategy plugins. A novel algorithm outside the grammar becomes a development proposal, not an automatic production patch.

Backtests run on recorded public quotes in a separate research PostgreSQL cluster, through the existing paper engine and replay path, with their own clocks and virtual funds. M6 has no research on bar history and no multi-account ledger. Stores are append-only, versioned `asl_m1_replay_` databases; staging copies published collections, payloads, observations, confirmations and publications in dependency order, without pilot evidence pins. Drop a store whole only when no dataset or shadow references it.

Until the pilot ends, M6 shadows are **SHADOW — deferred replay**, under M6-OD6. A frozen candidate is replayed only over observations available after its freeze, with earlier bars feeding indicators only. Engine rows stay `HISTORICAL_RESEARCH`; a live shadow engine and engine-level `SHADOW` mode wait for the experiment boundary. Every shadow states the three advantages over live execution: zero processing delay, reduced quote eligibility without feed/lease/clock state, and research downtime omitted. Compare only against a reference replay on the same window and rule; persist hashed marks, trade lists and portable prefix fingerprints in the catalog. A prefix mismatch suspends the shadow. Never replay a candidate's hindsight trades into the main account.

Once the pilot has ended, SYSTEM also keeps the **control replay** (ExecPlan 0026 §5.11, M7-OD5 (a), built in B6c): the reference alone, replayed as a shadow's reference over each agent-driven main-account run's window, in consecutive 21-day periods from the run's activation, each frozen at its start and starting flat. The bridge starts and advances periods in its daily schedule with the shadows, on an idle runner, under the approved envelope; its advances are `CONTROL` research jobs that test no hypothesis, write no trial and spend neither the trial day nor the queue of four. It is labeled `CONTROL — deferred replay of the reference, not a forward result`, is never a candidate's evidence, and no owner or agent read names it in M7 ([plan §17, B6c](plans/0026-m7-agent-driven-main-decisions.md#17-decision-log)).

## B3 implementation boundary (ExecPlan 0023)

IMPLEMENTED; runner/holdout gates VERIFIED in `m6-b3b`: `app/research/jobs.py` records catalog requests,
reservations, refusals and reuse in one transaction. The daily reservation uses
UTC midnight independently of the database session time zone. The research-only worker
uses a durable `research_runtime` inbox, attempt journal and outbox outside the
public replay-reset tables. A lost worker gets one reset/retry; its epoch is
checked inside each financial batch transaction. B4 owns transport, staging,
store rotation and shadows (below); B6 owns dispatcher/workflow integration. These
entrypoints do not expose a new model tool or activate a service.

Nominal dataset partitions retain the frozen chronological 60/20/20 split.
Replay ends each earlier partition one candidate maximum-hold interval before
the next boundary. A partition consumed by that gap remains empty and reports
INSUFFICIENT_SAMPLE. The holdout begins at the immutable 80% boundary. Warm-up
reads use only the sealed publication range and precede experiment activation;
all market reads are bounded before revision selection. Every nonempty cell
resets the engine, uses its existing candidate/replay path and generates the M4
evaluation document with unchanged sample minimums and baselines.

The single holdout evaluation retains its original evaluation ID on the one
permitted retry. A worker retry consumes that allowance too. Failed holdout
work leaves TESTED unchanged. A successful test is not a profitability gate or
permission to start a shadow.

## B4 implementation boundary (ExecPlan 0023)

IMPLEMENTED in B4; the isolated evidence is in
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#18-completion-evidence).
Four points the plan left open were decided by the owner on 2026-10-04
([DECISIONS](../DECISIONS.md#2026-10-04--m6-b4-handed-over-and-four-points-the-plan-left-open-execplan-0023)).

- **Bridge.** `app/research/bridge.py` is the only research process that reaches
  both databases. Each pass relays results, then cancellations and expiry, then
  at most one new job; stages published rows; keeps the store versions; and
  looks at the daily work. Disabled, it idles without a connection. When it is
  down nothing is staged or relayed: jobs stay queued and shadows wait.
- **Relay.** A job leaves the catalog as one immutable message and enters the
  inbox of the store its dataset names. The store refuses a message whose
  identity, dataset or code identity does not check; the catalog job then ends
  `FAILED` with that reason. A result is taken from the outbox, its bytes are
  hashed again, and the catalog accepts it once. A repeated relay is a no-op, a
  changed result is refused, and a result for a canceled or expired job is kept
  as history only.
- **Stores.** A new version becomes current once the current one spans 28 days
  or 12,271,335,131 bytes. A retiring version is staged only while a running
  shadow is bound to it and never past its cap. It is dropped whole when no
  queued or running job or shadow uses it. The catalog then refuses new work on
  its datasets as `STORE_UNAVAILABLE`; the manifests, results and marks stay.
- **Datasets.** One tuning dataset is sealed per UTC day on the current version
  after staging has caught up. A hypothesis binds to the newest of these and
  never to a shadow window.
- **Shadows.** SYSTEM freezes an eligible candidate at the catalog's clock,
  binds it to the current store version and advances it once per UTC day, or on
  demand. One advance replays the candidate and the reference strategy under
  `H1` from the freeze and stops at every recorded mark. A mark is immutable and
  holds both subjects' hourly marks, trade lists and portable fingerprints. An
  advance is not a trial and spends none of the researcher's budget. It is
  recorded only when no other job is queued or running, so advances run one
  after another and each has its full hour; one that never ran is recorded
  again the same day.
- **Not in B4.** No model tool, route or page. The candidate review that makes
  a candidate eligible is written by B6; B4's check reads a stored review whose
  `review_type` is `CANDIDATE_REVIEW`, whose `target_sha256` is the full
  result's hash and whose `verdict` is `ACCEPTABLE`. The owner's on-demand
  advance and stop requests reach the bridge through the catalog in B7; until
  then `python -m app.research.bridge --advance <shadow>` is the entry point.
  What becomes of a candidate whose shadow ended without the evidence minimum
  is not decided here. (Decided on 2026-10-05 and implemented in B6, below. B6
  also changed how the review binds the full result.)

## B6 implementation boundary (ExecPlan 0023)

IMPLEMENTED in B6; the isolated evidence is in
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#18-completion-evidence).
Four points the plan left open were decided by the owner on 2026-10-05
([DECISIONS](../DECISIONS.md#2026-10-05--m6-b6-definition-generations-schedule-and-ended-shadows)).
Everything here ran on synthetic fixtures with scripted or recorded providers.
No model was called and no real source was fetched.

- **Workflow A in M6.** A `SOURCE_REVISION` trigger, or the owner, starts
  `EVENT_INVESTIGATION_V1`. The analyst searches approved evidence at its cutoff,
  may queue a refresh of a registered source and waits for it without the
  inference slot, and records a `MarketAssessment` that cites what it was
  given. The fixed `ASSESSMENT_REVIEW_V2` follows. If the assessment names a
  research question and the review is not `REJECT`, one `FOLLOW_ON` trigger is
  recorded. Steps 5–7 of Workflow A stay M7.
- **Workflow B in M6.** `RESEARCH_V1` binds the newest sealed dataset when it
  starts and takes that dataset's holdout start as its information cutoff. It
  has one hypothesis. The researcher registers declarations (each refusal is a
  recorded trial), queues the screening set, waits, reads the result in its
  projection and records a `ResearchProposal` that may nominate one screened
  candidate. It never reads a holdout or shadow result and cannot name the
  holdout in a request.
- **From nomination to shadow.** SYSTEM (the bridge, as the research identity)
  queues the full test once, with one retry after a failed or expired first
  evaluation. When a valid result is recorded, the orchestrator creates
  `CANDIDATE_REVIEW_V1`, bound to the proposal's hash and to the hashes of the
  candidate's screening and full-test results. B4's eligibility check now reads
  a stored review of type `CANDIDATE_REVIEW` with verdict `ACCEPTABLE` whose
  `results` contain the full result's hash (in B4 the fixture carried that hash
  as `target_sha256`; the target is now the proposal). An eligible candidate is
  frozen and shadowed as B4 describes.
- **After the shadow.** A shadow that reaches the evidence minimum makes the
  candidate `EVIDENCE_READY`, and SYSTEM starts one `PROMOTION_V1`. The
  coordinator may record one `PENDING` promotion or abstain. A shadow that ends
  without the minimum (stopped, incomplete, or complete with too little
  evidence) retires the candidate, with the shadow's end reason as the gate
  evidence. Nothing in M6 approves a promotion.
- **Follow-on context.** The follow-on research workflow receives the symbols.
  It receives the question text only if the assessment's recorded provenance
  is at or before the research cutoff, which a present-time investigation
  cannot satisfy for a past holdout start. The question is therefore withheld,
  and so is the fact that one existed.
- **Scheduled research.** One `RESEARCH_V1` per newly sealed dataset, at most
  one a UTC day, only while the runtime is `ENABLED` and the envelope is
  approved.
- **Not in B6.** Owner routes and pages (B7, B8), saturation and coexistence
  runs (B9), deployment (B10) and every activation, approval and live probe
  (M6-B). The real model path and the real source path are NOT RUN.

## B7 implementation boundary (ExecPlan 0023)

IMPLEMENTED 2026-10-05: what the owner can do to research, and what it ends.
The routes are in [API_CONTRACTS](contracts/API_CONTRACTS.md#m6-owner-routes-execplan-0023-b7);
three owner decisions of that day settle the lifecycle questions
([DECISIONS](../DECISIONS.md#2026-10-05--m6-b7-experiment-read-codes-canceled-jobs-and-rejected-promotions)).

- **Start.** The owner may start an investigation, a research workflow or a
  promotion workflow. Each takes only its template's registered parameters; a
  promotion workflow takes the ID of an `EVIDENCE_READY` candidate. Research
  needs the approved envelope and a sealed dataset.
- **Cancel a job.** The owner's request is recorded on the job and applied by
  the research identity. **A canceled job is final for its input**: an equal
  request returns that job and nothing is queued again. A screening canceled
  before it ran leaves its candidate in `TEST_QUEUED` for good; a full test
  canceled before it ran leaves its hypothesis without a holdout evaluation
  and its parent without a review. This also holds for a job canceled by a
  permission-epoch change or because it was an hour old when it would have
  been dispatched; whether an aged-out job may be queued again is decided with
  B9's measurement of when a job's hour starts.
  - The job records `OWNER_CANCEL`, not a revocation. The research workflow
    that asked for a canceled screening receives the `CANCELED` completion and
    goes on; it can end with a proposal that nominates nothing. A workflow is
    ended as revoked only by a revocation.
- **Stop a shadow.** The request is recorded on the shadow; the bridge ends it
  `STOPPED`, cancels its queued advance and retires its candidate, unless the
  candidate already reached `EVIDENCE_READY`. The stop counts from the moment
  it is recorded: an advance result that arrives after it is history only, so
  it cannot become the mark that makes the candidate `EVIDENCE_READY`.
- **Reject a promotion.** The owner's `REJECT` is an exact-hash record of the
  pending request. The agent worker applies it as SYSTEM: the promotion
  becomes `REJECTED` and the candidate moves from `MAIN_APPROVAL_PENDING` (or
  any state that is not already final) to `REJECTED`, with the owner's record
  as gate evidence. `REJECTED` is final: the candidate keeps its whole history,
  no promotion can be started for it again, and an equal declaration registered
  later returns it. A promotion the owner leaves pending stays pending; only
  such a one can be approved once M7 exists.
- **Revoke the envelope or a source version.** The permission epoch rises in
  the transaction that records the revocation. Every queued job and refresh is
  then canceled, a late result is history only and every waiting research or
  investigation workflow fails `CAPABILITY_REVOKED`, whichever was revoked.
- **Not in B7.** Pages (B8). An on-demand shadow advance has no route: the
  plan lists none, and `python -m app.research.bridge --advance <shadow>`
  remains its entry point. `WITHDRAWN` is a defined promotion state that
  nothing writes yet.

## Workflow C: evaluation and promotion

Deterministic evaluation calculates metrics from stored financial data. The evaluator inspects those calculations, data lineage, leakage, test results, parameter trials, negative results and uncertainty. A model's favorable review cannot fabricate missing tests or accept a strategy based only on a persuasive explanation.

Retain all attempted candidates, including failed/incomplete/refused/canceled/unprofitable trials, before they run. Bind each hypothesis immutably to a dataset version and an information cutoff at its holdout start. Apply the cutoff to all market reads, artifacts and search before ranking. ANALYST/RESEARCHER receive no holdout/shadow results; reviews consulting them disclose only verdict and enumerated deficiency codes, never free text. SYSTEM queues one holdout evaluation per hypothesis (one recorded retry after failure); show reuse counts without claiming a statistical correction. A research agent seeing final-holdout results cannot continue to tune on that segment and call it untouched. Historical LLM knowledge can leak later outcomes despite clean inputs; forward timestamped decisions remain primary evidence.

The same hypothesis cutoff applies to source content in a research workflow's own refresh completion and its initial/follow-on context. Do not carry a current assessment or research question derived from late source evidence into that historical context. An event investigation may receive its own refresh via completion; this exception does not apply to research. A later-created typed artifact may still expose only the authorized pre-cutoff inputs from which it was derived. [The owner clarification](../DECISIONS.md#2026-10-03--m6-b0-research-cutoff-clarification) resolves the plan's former refresh/cutoff ambiguity.

A promotion request includes candidate/domain/policy hashes, correctness/fidelity evidence, out-of-sample and shadow reports, matched baselines, costs, uncertainty, risk changes, operating constraints and rollback/suspension plan. In M6 only COORDINATOR may request one for an EVIDENCE_READY candidate; it stays PENDING or is rejected/withdrawn. No role, route or database statement can approve it. Only M7 owner approval makes a new strategy/domain eligible for the main account. *M7 (M7-OD4 a), IMPLEMENTED in B6 of ExecPlan 0026 and tested offline only ([§18](plans/0026-m7-agent-driven-main-decisions.md#b6a--promotion-approval-and-the-candidate-basis-2026-10-12)):* the owner's approval of a `PROMOTION_V2` request makes the exact candidate an entry basis inside `AGENT_POLICY_V1`: the coordinator may name it in an entry, code checks the candidate's own entry signal (its entry condition holds and its exit signal does not), and the stop and hold stay inside the policy's sets. The candidate does not trade by itself and its exit rule is not run for the position; an approval is refused when the candidate's exit values lie outside the policy's sets ([ExecPlan 0026 §5.10](plans/0026-m7-agent-driven-main-decisions.md#510-promotion-approval-and-main-eligibility-m7-od4-option-a)). Existing positions retain the original policy and management mandate. As built: once the policy is installed SYSTEM asks with `PROMOTION_V2` and the server writes the request's scope; a pending `PROMOTION_V1` of the same candidate is withdrawn when it is recorded and can still only be rejected; a revocation raises the permission epoch, suspends the candidate and refuses every later entry naming it, while a position already entered keeps its terms; a research suspension of an approved candidate withdraws its entries the engine has not answered or filled at the agent worker's next pass ([AUTONOMY_MATRIX](contracts/AUTONOMY_MATRIX.md#m7-agent-driven-decisions-approved-contract-execplan-0026)).

An approved bounded adaptation rule may choose among already eligible versions automatically. A newly generated version cannot label itself “same family” to evade approval. Semantic domain membership is code-validated against the approved envelope.

## Workflow D: outcome review and adaptation

Use scheduled reviews, trade closures, data-integrity incidents and preapproved material events. The reviewer links original intent, evidence, review, risk outcome, fills, subsequent observations and modeled costs. Separate signal error, regime hypothesis failure, execution-model weakness, missing data, downtime and random variation; causal claims remain hypotheses unless supported.

Recommendations may be abstain, reduce discretionary exposure, select an approved candidate/timeframe, propose a new isolated experiment, or request owner review. They cannot increase hard risk, average down outside policy, loosen protection or erase a loss. Losing recently does not automatically establish that a strategy is invalid; a winning trial does not establish future edge.

Every automatic selection/update uses a predeclared rule, bounded domain and versioned record. For discretionary model decisions, record the policy/model/prompt identity and evidence; evaluate the entire decision process rather than retrospectively inventing deterministic rules.

## Required research artifacts

`EvidenceItem`, `MarketAssessment`, `Hypothesis`, `CandidateVersion`, `ExperimentManifest`, `ExperimentResult`, `EvaluationReview`, `TradeIntent`, `PortfolioDecision`, `OutcomeReview`, `PromotionProposal` and `ApprovalRecord`. Shared fields and ownership are in [DATA_CONTRACTS.md](../DATA_CONTRACTS.md). A source-linked rationale is sufficient; hidden reasoning is not required.

## Failure, resource and human boundaries

Research cannot starve protection or consume an unspecified API budget. Suspend tool work at the configured bounds; persist incomplete status and actual measured resource use. On PC downtime, record missed events and expired investigations instead of backdating them. If a required source is stale or a reviewer unavailable, abstain from dependent new exposure.

Owner approval is exceptional scope control, not a prompt for every lookup or ordinary paper trade. Approval queues are deduplicated and explain exact requested authority. The UI must distinguish a research candidate, a shadow run, main eligibility and actual execution.

## Bounded-domain promotion clarification

`MAIN_APPROVED` denotes valid owner-derived authority, not necessarily a new click for every parameter value. Where an owner-approved main policy already covers a bounded parameter domain and its automatic eligibility checks, code may record a validated member as eligible with the original approval ID, membership proof and test evidence. Exact new logic, expanded domains or changed mandates still enter `MAIN_APPROVAL_PENDING`. Research-only grants cannot produce either main eligibility path by themselves.
