# ExecPlan 0027 — M9 market intelligence and event-driven adaptive paper trading

## 1. Status, order and authority

**2026-10-19 — re-scoped by [ExecPlan 0032](0032-m9-news-and-events-the-agents-trade-on.md) under M8's rules ([ExecPlan 0031](0031-m8-simple-app-that-runs-itself.md)).** The owner's approvals and source grants, the capability probes and the PC harness and load runs that this plan assumes are gone since M8. Where the two plans differ, 0032 governs; this plan stays as the design record, and 0032 §3 says what it keeps, defers or replaces. Nothing below is edited.

**2026-10-15 — future milestone specification; documentation authorized; application implementation NOT STARTED.** The owner requested this milestone after everything already in the roadmap, with a handoff usable by Claude Code or ChatGPT. M9 starts only after M0–M8 have their required completion evidence, M8 is accepted and the verified M8 release is running in the normal local app. This document neither declares those prerequisites complete nor authorizes implementation, activation, new source grants or spending now.

The [roadmap](../../ROADMAP.md) owns milestone order. [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md), [RISK_POLICY](../../RISK_POLICY.md), [DATA_CONTRACTS](../../DATA_CONTRACTS.md), [RUNTIME_AGENTS](../RUNTIME_AGENTS.md) and [EVALUATION](../EVALUATION.md) retain their respective authority. Requirements below are the **proposed M9 successor design**, not overrides of the current operating policy. B0 must reconcile affected canonical contracts before implementation and preserve all historical approvals and evidence.

Claude Code and ChatGPT/Codex are implementation clients for this handoff. They are not proposed replacements for the app's subscription-based Codex runtime. No paid model API fallback, live exchange execution, private exchange credentials, shorts or leverage is introduced. News coverage can extend across assets; paper trading remains the approved BTC/SOL spot, long-only universe. Trading another coin requires a separate scope decision.

**2026-10-16 refinement:** the owner authorized incorporating the intelligence/research improvements and documenting a separate [M10 discovery and expansion milestone](0028-m10-coin-discovery-and-controlled-expansion.md). M9 supplies reusable asset identities, evidence and assessment contracts; its acceptance does not depend on implementing discovery, ranking a broad coin universe or trading additional coins. The request to use AI agents fully concerns the application's agents and their permitted tools, not unrestricted runtime delegation or new authoring agents.

**2026-10-16 readiness refinement:** the owner requested researched roadmap improvements and delegated their placement. Strengthen this milestone and M10, and make existing-control closure explicit at M8; do not postpone foundational repairs until a new milestone after discovery. The informal goal of “5/5” means demonstrable engineering quality, not a rating conferred by this document. M9-R19–R24 add readiness, invalidation, decision feasibility, measured latency, semantic evaluation and runtime compatibility requirements. Implementation and activation remain separately gated.

**2026-10-17 research findings:** the owner recorded findings from trading-bot builder communities and LLM-trading studies as PROPOSED requirements in the earliest milestone each affects ([DECISIONS](../../DECISIONS.md#2026-10-17--builder-and-llm-trading-findings-recorded-as-proposed-m8m10-requirements)); no new milestone. M9-R25–R28 add an audit of remembered outcomes in historical cases, decision repeatability with an isolated agreement variant, code-computed point-in-time news base rates before a category may raise trigger priority, and search intensity in a successor promotion-request version. M8's warm-up measurement, entry placebo and exit what-if live in [EVALUATION](../EVALUATION.md#m8-onward-warm-up-sensitivity-and-decision-level-controls), not here. Implementation and activation remain separately gated.

## 2. Goal and observable outcome

Help the app identify worthwhile opportunities and manage risk promptly, with the long-term owner goal of growing capital through automation. M9 tests whether timely information and adaptive decisions improve **after-cost paper results**. It does not promise profits or optimize for the largest possible number of trades.

While the local app is running, bounded collectors maintain approved information sources. A background market-intelligence agent checks important changes, researches gaps and produces sourced assessments for the other agents. The coordinator can propose buying, holding, reducing or selling when approved criteria are met, without waiting for an hourly review. Five minutes and three hours are examples of possible holding periods, not fixed targets or service guarantees. Code still enforces permissions, sizing, costs, position mandates and paper execution.

An operator can inspect a complete example from source evidence through an assessment, decision, review, risk result, modeled fill and outcome. The same record explains abstention, rejection, expiry or missing data. Normal UI remains quiet: health, significant decisions and expandable evidence, without a continuous agent-chat dashboard.

## 3. Repository facts and mandatory post-M8 refresh

OBSERVED during documentation preparation: checkout `claude/m6-performance` at `50ef1c0` contained the M0–M8 roadmap and [M7 ExecPlan 0026](0026-m7-agent-driven-main-decisions.md). The locally cached `origin/main` at `5e86b44` contained later M7 work. Neither snapshot establishes current deployment or M8 completion. No normal-app state was inspected or changed for this documentation task.

The existing design already supplies four logical roles, approved-source research, typed tool calls, durable jobs, policy-bound intents, risk/accounting boundaries and operational records. M9 extends those facilities; B0 must inspect actual post-M8 code and reuse the working paths. The checked-out runner pins `rust-v0.159.2` in [invocation.py](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/agent-runner/runner/invocation.py); that observation is not a pin for future M9 implementation or proof of web-search capability.

B0 records the accepted M8 commit, deployed source/image identities, unresolved limitations, actual provider/model/prompt/tool versions, database schema, resource baseline and relevant approvals. Read current owner decisions and scoped instructions before choosing file locations. Recheck official documentation against installed versions. Do not transplant obsolete M6/M7 snapshots or silently overwrite intervening work.

### M8 readiness evidence required before M9

At `0a7866bddc1c18c27c97660a9b3b3e4def8fd1ee`, source inspection and retained records identify the following prerequisites. They are not observations of today's running app. Refresh each against the accepted release; link an existing resolution instead of reimplementing it.

| Finding and evidence | Required closure before accepting the prerequisite |
|---|---|
| [M7 recorded gaps](0026-m7-agent-driven-main-decisions.md#19-open-risks) include unrun real-model generation-2/3 checks, scripted-only role comparisons and incomplete forward-control work. [Prior publication evidence](../COMMANDS.md#m9m10-publication-preparation--2026-10-16) records CI startup failure without jobs. | Complete applicable intended Docker/PostgreSQL-version checks, actual provider capabilities and M8 forward/role evidence. Reproduce and resolve relevant failures; preserve unrelated limitations explicitly. CI evidence must identify jobs/tests that actually executed against the release source. Startup failure, skipped jobs or a merge alone cannot satisfy a required check. Do not infer the historical CI failure's cause or claim a fresh remote observation. Since 2026-10-17 the repository has no CI ([DECISIONS](../../DECISIONS.md#2026-10-17--github-ci-removed-from-the-repository)); until it is added back, the required checks are the local harness's, executed against the release source under the same rule. |
| [Candidate withdrawal](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/app/agents/decisions.py) currently propagates automatic research suspension through the agent worker; owner revocation uses a different, epoch-protected path. | Resolve invalidation at the execution boundary as specified in section 7. Test agent-worker loss, commit/fill races and already-partially-filled positions. A queued withdrawal or eventual notification alone cannot establish immediate eligibility enforcement. |
| [Older M5/M6 guard functions](../../../services/engine/alembic/versions/0008_m6_research.py) and the M7 risk record identify unqualified object lookup without a fixed function search path. | Inspect the actual function ownership, caller privileges, writable schemas and temporary-table rights on the intended PostgreSQL release. Prove object shadowing cannot bypass a guard; use a reviewed forward migration and least-privilege grants where needed, with restore/regression evidence. Do not assume all functions are SECURITY DEFINER, that an exploit was observed, or that a blanket privilege change is approved. |

Address these findings in scoped M7/M8 follow-up work: repair authority/security defects before affected activation, run provider/environment checks at their existing activation gates, and finish comparative/forward evidence by M8 closure. Authorized probes and forward observations proceed under those staged gates; completed forward evidence is not a prerequisite for starting the observation that produces it. M9 B0 verifies closure. Inventory the remaining M7 risks too, including cancellation propagation and permission-update contention. Record a repair or tested bounded behavior for each material risk; an old comment or a planned fix is not closure. Historical acceptance records and policy approvals remain immutable.

Two further observations shape M9 work rather than retroactively promising M8 speed: the [portfolio snapshot](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/app/agents/portfolio.py) labels missing risk headroom, and the [scheduler](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/app/agents/orchestrator.py) has one inference slot and an hourly quiet window. The [recorded step probe](0026-m7-agent-driven-main-decisions.md#18-completion-evidence) is a small historical sample, not full decision-workflow latency. Section 7 owns their successor requirements.

## 4. Information coverage

These are the six information categories requested in the Benzinga discussion. They are coverage requirements, **not a claim that free sources reproduce Benzinga's paid products, proprietary reporting, completeness or speed**. No Benzinga subscription or scraping integration is required by this plan.

| Priority and category | Collection and agent responsibilities | Required limits and acceptance evidence |
|---|---|---|
| Very important — crypto news | Approved exchange/status, project/protocol, regulator and reputable reporting feeds/pages; investigate incidents, security exploits, regulation and ecosystem developments. | Entity relationships extend beyond ticker keywords and BTC/SOL. Test aliases, ambiguous symbols, exchange-wide and cross-asset effects. Unverified reports remain labeled. |
| Very important — economic calendar | Collect official schedules and releases; normalize release times, actual results, previous values and revisions. Obtain consensus only from an approved source that supplies it. | Test time zones, DST, delays, cancellations, units, seasonal adjustments and revisions. Freeze a forecast's provenance and availability before release. Missing consensus is unknown; previous values are not forecasts. A later API snapshot is not evidence of what was known at release time. |
| Very important — selected financial and macro news | Central-bank, statistical-agency, policy/regulatory and selected broader financial reporting; investigate plausible channels affecting crypto markets. | Include an explicit geographic/topic coverage register. US and euro-area examples below are a starting set, not worldwide coverage. Unknown impact is valid. |
| Important — explanations of price movement | Market anomalies trigger targeted searches and comparison with contemporaneous events; distinguish a publisher's explanation from the agent's hypothesis. | “No reliable explanation found” is valid. Correlation, repeated headlines and movement already observed do not establish cause or predict the next move. |
| Important — press releases | Collect original issuer, exchange, project and relevant business announcements; verify authenticity and look for independent context where needed. | Preserve the interested party's attribution. A press release is evidence of a claim, not automatic verification of that claim. |
| Important for selected topics — SEC filings | Monitor selected issuer/product identifiers and relevant filing types through approved public EDGAR interfaces. | Preserve filing/accession identifiers, amendments and availability time. Filings do not directly measure live ETF purchases or flows. Avoid ingesting the entire issuer universe. |

Before activation, every category must have a tested collection/investigation path, a declared watchlist/topic scope, current coverage status and an outage/fallback test. A missing required path remains open; it cannot be relabeled complete. Field-level gaps such as unavailable consensus may be explicitly accepted in a narrowed policy that does not depend on them. Proprietary attention data, sentiment products, transcripts, broad earnings coverage and prediction-market reporting are optional later additions, not hidden M9 dependencies.

Candidate primary sources reviewed for this plan are SEC public submissions data, Federal Reserve and ECB feeds, and BLS schedules/releases/public data. Their official documentation is registered under [M9 references](../contracts/REFERENCES.md#m9-documentation-research--2026-10-15). B0 must select and document actual crypto, issuer and secondary-reporting sources; their APIs, RSS availability, rights and latency are not assumed here.

### Source catalog and collection

Extend the existing approved-source catalog with exact provider/endpoints, permitted domains/paths, entity/topic/geographic scope, format/schema/parser version, authentication requirement, cost, terms/retention permissions, official limit reference, measured latency/freshness, polling/stream capability, fallback, approval identity and health. Free and keyless are separate properties; public sources can still impose limits. A fallback needs its own grant and truthful provenance.

Use the cheapest reliable transport appropriate to each source: an existing stream where available and permitted; otherwise scheduled API/RSS requests or bounded page retrieval. Share results across agents. Use advertised ETag/Last-Modified validators, incremental cursors, deduplication, timeouts, bounded retries with jitter and provider-aware budgets. Honor applicable `Retry-After`; conditional requests still count toward request budgets unless the provider explicitly says otherwise. Do not hammer blocked sites, evade limits or bypass access controls/paywalls.

Collectors run as background application services while the PC, Docker and network are available. RSS usually means polling, not a permanent pushed connection. Cadence is per source and priority, with scheduled-release windows where useful. Calendar changes and outages alter collection work within approved bounds. No universal “every minute” or instant detection promise is made. B0/B1 must freeze and measure cadence, freshness and recovery targets before claiming coverage.

## 5. Background agent and handoffs

The market-intelligence agent is a dedicated background workflow using the existing ANALYST permissions and a versioned specialist prompt. Reuse the four logical roles unless implementation evidence justifies a separately approved role; a fifth name alone grants nothing. Persist typed artifacts and durable wake-up events rather than relying on agents continuously talking to each other.

*PROPOSED 2026-10-18:* the owner's idea of more agent roles and a coordinator that the other agents report to is recorded with suggestions in [a note](../ideas/agent-roles-and-coordinator.md). B0 weighs it against M8's role-value evidence; it adds no requirement row and changes nothing in this section.

```text
Approved APIs / RSS / permitted pages     Existing market observations
                   |                                 |
          Collect, validate and deduplicate       Detect changes
                   +---------------+-----------------+
                                   |
                         Durable event/evidence store
                                   |
                  Background intelligence analyst workflow
                    | targeted search / bounded page read
                    | corroboration / impact / uncertainty
                                   |
                  Assessment -> coordinator draft -> required review
                                   |
                  Code checks authority, data, costs and risk
                                   |
                     Paper broker -> ledger -> outcome feedback

Deterministic existing-position protection remains independent of AI.
```

The analyst handles both returned API/feed data and web evidence. Ordinary refresh is automated; the agent may request a bounded refresh or search when evidence is missing, contradictory, stale or relevant to an unexplained move. It does not repeat every collector request. The coordinator consumes assessments and current portfolio/market state and remains the discretionary trade proposer. The evaluator checks the exact draft and evidence under policy. The researcher uses retained outcomes for approved isolated experiments, never a slow mandatory dependency of every trade.

### Active investigation and bounded feedback

Make existing roles useful through explicit, testable work rather than additional names or repeated summaries:

| Role | Required contribution within its approved tools |
|---|---|
| ANALYST | Identify a material question, select relevant permitted evidence/searches, investigate competing explanations, and revise or abstain when evidence changes. |
| RESEARCHER | Turn an unresolved thesis or recurring outcome pattern into a falsifiable hypothesis and registered experiment inside the approved research envelope; retain negative results. |
| EVALUATOR | Inspect the exact draft and supporting source records in a separate context; identify concrete unsupported claims, contradictions, missing evidence and review conditions. |
| COORDINATOR | Compare assessments with current portfolio state, costs and permitted actions; record the basis for action or abstention and obtain the required exact-draft review. |

An investigation records its decision-relevant question, known evidence, unresolved claim, next permitted evidence request and stopping reason. A model may choose follow-up queries and competing hypotheses inside the granted scope. SYSTEM routes a review's evidence deficiency back to a registered analyst/research workflow when useful; it never gives the evaluator or coordinator an implicit search grant. Define and test any new handoff/tool/artifact in the canonical contracts before implementation. Reuse bounded workflow templates, not arbitrary agent-created delegation graphs.

Freeze budgets for steps, follow-ups, repeated-query detection, wall time and shared source/model usage. Stop when the question is adequately resolved, further permitted evidence is unavailable or unlikely to change the decision, the opportunity expires, or the budget is exhausted. The last assessment must state remaining uncertainty; budget exhaustion cannot become fabricated certainty. A material evidence revision supersedes stale work and requires the applicable fresh review. Routine permitted investigations need no per-query owner prompt.

Keep urgent position assessment separate from slower exploratory research. A fresh experiment is not a prerequisite for every already-permitted trade. Compare the bounded feedback workflow with a simpler analyst workflow at matched data and total inference budgets; extra roles or turns must earn their cost through measured results.

Web search remains an explicit M9 requirement, distinct from searching the local evidence database. Provide controlled search and page-reading capabilities at the application broker boundary, with query/result/page/time budgets, allowlisted destinations, provenance and revocation. Search can discover candidate sources, but source text and links do not approve themselves: fetching an unapproved destination waits for the applicable source grant. A preapproved bounded domain/path scope can cover routine pages without per-article owner prompts.

**Search provider/transport is UNSET.** B0/B3 must prove a supported, permitted transport under the then-installed Codex profile and existing cost policy. Current official CLI guidance distinguishes cached search from live retrieval; cached results do not ensure current news. Do not assume the paid Responses API search tool is included in a Codex subscription, or enable native shell/browser/MCP capabilities merely to make search work. If a native search exception is proposed, reconcile its exact permission contract and run positive/negative capability probes before activation. No available compliant search path means this M9 capability is blocked, with other completed work reported separately.

## 6. Evidence, trust and event lifecycle

Extend shared contracts with the following concepts; these are proposed responsibilities, not existing schema/table names:

| Record | Minimum information and invariants |
|---|---|
| Source observation | Source/approval/fetch IDs; canonical URL/provider identifier; permitted retained content or excerpt and hash; original publication/update time; first app receipt, fetch completion and availability time; parser/version; language; quality/rights state. Unknown times stay unknown. |
| Canonical event and revision | Stable event ID; original source and syndication lineage; event/effective time distinct from observation time; entities and relationships; category; immutable revision history; detected, confirmed, corrected, retracted, resolved or expired state. |
| Analyst assessment | Exact evidence revisions; facts versus hypotheses; source independence and contradictions; relevance and possible impact per asset and horizon; event certainty distinct from directional confidence; uncertainty, invalidation, expiry, prompt/model/tool versions. Mixed/neutral/unknown are valid; no invented calibrated probabilities. |
| Asset research record | Stable asset reference; current and competing theses; supporting and opposing evidence revisions; scheduled catalysts; unresolved questions; horizon, invalidation and expiry; linked experiment/decision/outcome IDs. Versioned, scoped retrieval; a remembered model statement is not a new primary source. |
| Trigger and decision | Cause, priority, event/portfolio versions, enqueue/start/deadline/cancel times, dedupe key, considered evidence, action or abstention reason, policy/grant/review binding and current execution checks. |
| Outcome | Join to risk decisions, orders, partial fills, fees, position mandates and realized/unrealized results; evaluation window, baseline and attribution limits; mode clearly distinguishes observation, calculation, model output, modeled fill and synthetic fixture. |

Persist normalized observations and their durable notification atomically or with an equivalent recoverable outbox. Delivery can repeat; handlers must be idempotent. A revised/retracted item invalidates dependent pending assessments and reviews where material. Do not overwrite history or deduplicate away a material correction. Out-of-order receipt and syndicated copies must not create false independent corroboration or multiple trades.

### Assessment dimensions and comparable calculations

For each relevant asset and declared horizon, keep project/protocol fundamentals, broader market and macro conditions, relative strength and execution conditions distinct. Do not compress mixed evidence into a single bullish/bearish label that hides a material change. Store what changed since the previous assessment and why it matters; an unchanged summary label must not suppress a material risk/catalyst update. Repeated unchanged news must not create another independent signal.

Separate four judgments: whether an event occurred; its hypothesized effect on token demand/supply or risk; the contemporaneous market response; and whether a current action qualifies under policy after costs. Authentic project announcements do not by themselves establish implementation, adoption, token-holder benefit or remaining price upside. Check announced versus effective dates, available usage/value-transfer evidence, competing explanations and missing inputs. An absence of adverse news is not positive evidence. State uncertainty about how much information is already reflected in price rather than asserting it is known.

Compute relative returns and other numeric comparisons in code from versioned observations with matching cutoffs, interval endpoints, quote currencies/conversions, finalized-data rules and benchmark definitions. Keep absolute price direction separate from relative outperformance. A missing/stale benchmark, an unavailable currency conversion or mismatched periods makes the comparison unavailable; the model cannot fill it from memory. Benchmark selection and any new features require the applicable source/feature policy, not permission to trade the benchmark asset. Unvalidated market-cap, sentiment or arbitrary composite scores are not return probabilities.

Confidence in source authenticity, interpretation and forecast direction are separate fields or explicit statements. If a policy proposes numeric probabilities, first define the forecast event, horizon, outcome label and abstention coverage, then freeze the calibration/scoring protocol and collect forward evidence before treating the numbers as calibrated. Non-probabilistic assessments remain valid; M9 does not require invented percentages.

### Evidence-backed working memory

Retrieve compact, task-relevant asset research records with links to their source revisions, not entire prior chats. Recheck current source permissions, time cutoffs, expiry and correction/retraction state on retrieval. Invalidate dependent remembered claims and queued actions when their evidence changes; retain the original record for audit. Carry contradictory evidence and unresolved questions through summaries and restarts. Test that a retrieved summary or another agent's output cannot launder stale, revoked or out-of-scope material into a current fact or privileged instruction. This is structured application memory, not model training, native file access or permission to edit prompts/policy at runtime.

A fast first stage records and prioritizes a potential event; a second stage researches and assesses it. An unverified alert is not automatic trading authority. The approved policy determines the corroboration needed for the consequence in question; a rigid universal count of two URLs is not proof of independence. Relevant existing-position alerts can receive urgent review while uncertainty still blocks new exposure.

External content is untrusted data, including tool results and another agent's summaries. Enforce bounded response size/time, safe parsing, HTML/XML sanitization, no external entity expansion, URL validation and DNS/private-address protections in code and network policy. Retain the existing fetcher's disabled redirects/environment proxies and connection to the validated address with the original TLS name. No page can instruct an agent to reveal credentials, change tools/policy, execute code or access arbitrary destinations. Keep credentials out of queries, model context, error bodies and logs. Existing M6 protections must be reused and extended, not bypassed.

## 7. Event-driven decisions and policy reconciliation

Separate four clocks: source collection, analysis features/candles, decision scheduling, and position holding. Multiple approved analysis horizons can inform a decision at any eligible time. A rule requiring a finalized candle still waits for that candle; intrabar observations never masquerade as closed-bar data. Add new data resolutions only after their provenance, workload and execution usefulness are verified.

Eligible triggers include material price/volume/liquidity changes, new or corrected relevant events, calendar releases, changed position risk/thesis, and periodic fallback review. Detect cheap changes in code before invoking a model. Thresholds, freshness, hysteresis, deduplication, minimum decision spacing and deadlines belong to a versioned policy. Coalesce redundant work, preserve urgent material changes, cancel superseded jobs and expire late outputs. Do not run an LLM on every tick.

B0/B4 must produce an explicit old-to-new policy map for M7's hourly-bar intent binding, workflow cooldown, protected quiet window, intent/review expiry, entry/re-entry controls, daily entry/submission limits and turnover budgets. State which constraints remain, which are mode-specific and which require a successor value and owner approval. Removing an hourly scheduling restriction is not permission to remove financial caps or bypass resource protections. Do not copy M7's numeric settings as M9 defaults or quietly raise them to achieve more trades.

Every proposed entry states its thesis, supporting/contradicting evidence, horizon, invalidation/exit criteria and permitted management template. The coordinator can abstain, cancel an unfilled entry, hold, reduce, exit or tighten a stop only within the applicable policy and original mandate. Existing positions retain their immutable mandates across upgrades: no loosening stops, extending hold limits or adding new management rights retrospectively. A new story is a reason to reassess, not a command to buy or sell.

Preserve independent deterministic protection and its reserved resources. Prioritize existing-position safety and urgent decisions ahead of ordinary entries and background research, with bounded fairness and starvation tests. AI timeout/quota exhaustion must not disable executable protective actions. Protective actions do not consume a depleted discretionary trading budget. New exposure needs valid required evidence and authority; fallback behavior must be explicit, not a silent switch to another strategy.

Revalidate at the appropriate proposal, commit and fill boundaries: policy/grant/lease epoch, exact review binding, current portfolio/reservations, event revisions, executable quote age, spread/depth/liquidity, costs, risk and original mandate. The paper broker retains exact Decimal accounting, atomic reservations, fencing and idempotency. Cancel/reassess an opportunity that expired while the model worked. Never turn an old quote or historical headline into a backdated forward fill.

### Execution invalidation and decision feasibility

Define the ordering between an eligibility-invalidating commit and each risk-increasing reservation, order acceptance and fill. Once invalidation commits, a later such effect cannot use the invalidated authority. Cover automatic candidate suspension, owner revocation, applicable source/evidence invalidation and cancellation under their declared semantics. Use a code-owned validity version, fenced transaction or equivalent proven mechanism visible to execution even when agent/research workers are stopped. Do not grant execution arbitrary research-table writes or rely solely on asynchronous delivery. Already-committed fills keep their original mandates; cancel the invalid remainder according to policy and continue valid protection. Test both serial orderings, concurrent commits, partial fills, restart and delayed/duplicated notifications.

Extend the existing permitted portfolio read with **code-calculated advisory feasibility**, not another permission-bearing agent or model-owned sizing tool. Show the state/policy/evidence versions and observation time; available and reserved funds; remaining applicable risk/exposure/action capacity; permitted position actions; and explicit blockers. Where supported, include executable instrument constraints and costs with units, provenance and assumptions. Unknown capacity or cost is unavailable, never a model estimate or unlimited capacity. Reuse the risk engine's definitions rather than maintaining a second calculation in prompts.

The advisory read reserves nothing and cannot promise acceptance. Concurrent reservations, price moves, partial fills, permission changes and expired observations require authoritative revalidation. Code may suppress a provably ineligible entry request before inference, while leaving useful investigation and permitted existing-position work available. Do not reset submission counts or weaken limits to improve rejection metrics. Test sufficient, exhausted, stale and unavailable capacity, including two individually plausible proposals whose combined exposure exceeds the shared cap.

### Latency and quota acceptance

B0/B4 freeze a workload and service-budget matrix in [OPERATIONS](../../OPERATIONS.md) and [CONFIGURATION](../../CONFIGURATION.md), with supported hardware, input rates, urgency classes, measurement method, sample-adequacy rule and pass/fail/stop conditions. Measure trustworthy publication-to-receipt lag separately from local receipt, enqueue, start, evidence-ready, draft, review, risk result and modeled execution times. Use monotonic elapsed timing for local durations and preserve clock-quality limits for cross-source comparisons. Record counts and distributions, including tail latency, timeout, expiry and dropped/coalesced work; completed calls alone exclude important failures.

Exercise normal traffic, scheduled-release/news bursts, cold starts, competing research, provider throttling/auth expiry and host recovery. Allocate bounded resources to urgent position work and ordinary entries; measure fairness as well as protection isolation. Admission uses the remaining opportunity deadline and measured queue/service needs. If the approved workflow cannot finish usefully, expire or abstain with a reason rather than trade late. The decision path consumes already prepared evidence where valid; it does not wait for a fresh research experiment on every event. Coalesce equivalent work and parallelize only independent operations within measured and approved limits.

Measure actual subscription capacity and supported usage visibility; no unlimited-calls assumption or paid fallback. When tokens/quota are unavailable, retain known call/step/work limits and mark missing usage unknown. Reconcile the old quiet window only after replacement resource/capture protections pass; shortening an interval by itself is not a latency improvement. An observation-to-action target is not a guaranteed holding period or proof that competing market participants have not already reacted.

The app runs only while the local host and required services run. After downtime, reconcile state, restore valid observations, expire obsolete work and reassess. Do not claim continuous protection while the engine or valid executable data was unavailable. Agent-written conditional execution plans are **not required M9 scope**; consider them later only if measured latency justifies a separately specified and approved policy.

## 8. Visibility, feedback and evaluation

Provide a durable join from source event to evidence, assessment, decision/review, rejection or order/fill and outcome. Record HOLD/ABSTAIN, risk refusal, expiry, duplicate/coalesced/dropped triggers and reasons as first-class results. Track source coverage/health, missing fields, correction handling, queue age, collection-to-assessment-to-decision-to-fill latency, quota exhaustion, failures and usage when actually reported. Publication-to-receipt lag is measurable only when publication time is reliable. Missing usage is unknown, not zero.

Keep decision evidence and audit history under explicit retention and access rules, independently of rotating container logs. Preserve required records before pruning; record content-rights/retention gaps and resulting replay limits. Expose scoped structured histories and outcome summaries to agents through approved read tools. This is not arbitrary server-log access, automatic model training or permission to rewrite policy. Exportable redacted diagnostic bundles should help an implementer reconstruct an incident without credentials or private chain-of-thought.

Use existing UI patterns for a compact health summary and expandable event/decision details. Show stale/unavailable/paused states, material incidents and actual reasons. Do not stream every internal message or imply all world events are covered. When UI work begins, load the official shadcn skill, perform project discovery and reuse the established primitives/preset; use the chart skill only for actual chart changes.

Freeze an evaluation protocol before viewing the final results. Compare (a) the accepted pre-M9 baseline, (b) event-driven decisions without the new news inputs, and (c) the combined system, plus existing useful single-role/full-workflow comparisons. Match market availability, starting capital/contributions, cost assumptions, allowed exposure and evaluation windows. Keep all trials, failures, model/prompt/policy/source versions and tuning decisions. Reserve untouched validation and authorized forward-paper evidence.

Evaluate factual accuracy and unsupported claims, event detection coverage against a declared reference set, false/missed alerts, relevance, correction propagation and calibration where justified. Also measure net returns after modeled costs, drawdown, turnover, holding periods, latency, stale/expired opportunities, resource use and behavior during outages. Report denominators and uncertainty; higher trade count, win rate or a positive backtest alone is not success. A skipped trade's later price move does not prove a tradable missed profit.

Historical tests must use information actually available to the app by the simulated decision time, including publication/collection/processing lag, revisions and pre-release consensus. A modern model may know later historical outcomes from training; disclose this contamination risk and use forward evidence before claiming predictive value. Explanations and performance attribution are hypotheses unless the evaluation supports them. Negative or inconclusive results are valid outcomes; do not loosen gates after seeing results to manufacture acceptance.

Outcome reviews distinguish source/correction errors, unsupported interpretation, late assessment, modeled execution/cost effects and an unfavorable outcome despite policy compliance. Their causal explanations remain hypotheses until tested. Route useful recurring questions into approved isolated research; keep all trials and never rewrite the original thesis after the result. Adaptation inside an already approved policy/envelope may continue; new operators, prompt/model/profile versions or wider policy domains follow their canonical change/approval rules. A model review cannot modify production code or train itself.

Grade recorded tool choices, claim support, evidence-gap handling, handoffs, correction propagation and stopping behavior in addition to final prose and financial metrics. Use deterministic checks for identities, timestamps and calculations; labeled evidence cases and sampled human review calibrate model-assisted grading. Two agents agreeing is not independent confirmation. Segment comparisons by asset, horizon, event class, data quality and model/prompt/policy versions so aggregate results do not conceal failures. No hosted evaluation API or new SDK is required; extend the existing local Docker harness.

The [future agent-quality protocol](../EVALUATION.md#future-m9m10-agent-quality-and-release-evidence) owns semantic cases, repeated-trial methodology, reviewer false acceptance/refusal, matched-budget role comparisons and release/forward claims. Build its cases before tuning the new workflow. Evaluate useful action, justified abstention and useful search restraint, not a prescribed number of model turns. Evidence of no incremental benefit is a reason to retain a simpler approved workflow; it cannot silently remove a mandatory review or promote an unapproved comparison variant.

## 9. Requirements mapped to verification

These are M9 specification IDs, not existing test names. B0 maps them to concrete Docker test commands and the changed implementation. Existing [A01–A38](../../ACCEPTANCE_CHECKLIST.md) remain applicable; M8 acceptance is not a waiver for regressions introduced by M9.

| ID | Observable acceptance test | Existing contracts |
|---|---|---|
| M9-R01 | All six categories have tested permitted paths and visible scope/gaps; ambiguous entities and cross-asset news do not expand tradable symbols. | A01, A06, A15 |
| M9-R02 | Concurrent agents share collection/cache/budgets; 304, 429, malformed payload, timeout, outage and fallback preserve provenance and bounded retries. | A06, A24, A33, A34 |
| M9-R03 | Calendar timezone/DST/reschedule/cancel/actual/previous/revision fixtures preserve vintages; absent consensus cannot produce a fabricated surprise score. | A06, A10, A34 |
| M9-R04 | Analyst requests real web search and approved page/refresh tools, consumes returned evidence and cites exact revisions; denied URLs/native tools have no side effects. Fixture and authorized provider smoke evidence are separate. | A11, A13–A15, A28, A34 |
| M9-R05 | Duplicate/syndicated/out-of-order/retracted events survive restart without false corroboration or repeated effects; material changes invalidate stale review. | A06, A22, A24 |
| M9-R06 | A permitted entry and exit can occur between hourly boundaries; finalized-bar rules still hold; multiple horizons, expiry and old-position mandates are enforced. | A09, A16, A20–A22, A31 |
| M9-R07 | Urgent position work is serviced during a news burst, research load and model outage; queue bounds, fair scheduling, cancellation and reserved protection capacity meet frozen budgets. | A16, A24, A30, A32, A33 |
| M9-R08 | Split/retried/concurrent intents, revocation, changed event/quote/review and partial fills cannot bypass caps, reservations, fencing or exact ledger reconciliation. | A07–A09, A22, A25, A29–A31 |
| M9-R09 | No unauthorized source approval, paid fallback, secret disclosure, native capability, injection-directed action, SSRF or arbitrary code/SQL execution; adversarial fixtures include redirects and DNS changes. | A01, A11, A14, A27, A28, A34 |
| M9-R10 | Each action and no-action outcome is reconstructable through retained structured records; redaction, missing usage, retention gaps and health states remain truthful. | A06, A12, A23, A26, A36 |
| M9-R11 | Matched comparisons include costs, point-in-time vintages, latency, all trials and forward evidence; withheld data and results cannot leak into tuning. | A10, A18, A35, A36, A38 |
| M9-R12 | End-to-end recorded workflow and separately authorized real-input paper workflow traverse evidence, decision, review, risk, modeled execution and outcome without per-trade approval. A valid abstention remains a valid result. | A13, A20–A24, A37, A38 |
| M9-R13 | Network/model/database/host failures, backup/restore, retention saturation and deployment preserve controls and mandates; no catch-up fills or hidden downtime. | A03, A07, A12, A25, A32–A34 |
| M9-R14 | An evidence deficiency causes a relevant permitted follow-up, changed conclusion or explicit abstention. Repeated searches, expired opportunities and exhausted budgets terminate visibly; evaluator/coordinator search attempts remain denied. Compare with a simpler workflow at matched input and total inference budgets. | A13–A18, A23–A25, A33, A38 |
| M9-R15 | An authentic announcement with no demonstrated token benefit remains uncertain; announcement/effective dates, contrary evidence and horizons stay distinct. A material incident triggers reassessment despite an unchanged sentiment label; recycled headlines do not. | A06, A15, A20, A22, A34 |
| M9-R16 | Relative-strength fixtures use matching times/currencies/benchmarks and code-calculated values; stale/missing references refuse the metric. Relative outperformance during an absolute decline does not become an absolute price-rise observation. | A06, A10, A15, A34 |
| M9-R17 | Restart and selective memory retrieval preserve opposing evidence and questions. Corrected/revoked/expired evidence invalidates dependent claims/reviews; injected text in a saved summary cannot gain tool or financial authority. | A06, A14, A22–A26, A28, A34 |
| M9-R18 | Outcome review yields a bounded testable hypothesis or justified no-follow-up without rewriting history. Preserve failed trials, exact forecast targets if probabilities are used, grading limitations and forward evidence; a feedback record cannot auto-change prompts, policy or risk caps. | A10, A17–A19, A26, A35–A38 |
| M9-R19 | B0 links release-specific M8 closure: intended Docker/PostgreSQL checks, real-model capabilities, actual execution of the required checks (CI, or the local harness while the repository has none), forward/control evidence and disposition of material inherited risks. Mock/schema success, stale results and skipped/startup-failed jobs cannot pass required gates. | A03, A11, A12, A35–A38; Q04, Q07, Q09 |
| M9-R20 | Committed invalidation blocks later risk-increasing effects with agent/research workers down. Suspension/revocation/cancel races, delayed delivery, partial fills and restart preserve exact reservations and original mandates; unsafe database object shadowing is denied. | A07–A09, A14, A24, A25, A28–A32 |
| M9-R21 | Versioned code-calculated feasibility exposes real capacity/blockers without reserving or granting authority. Unknown/stale inputs, simultaneous intents and changed costs/state cannot bypass the final risk gate or suppress valid protection. | A06–A09, A20, A21, A25, A29–A32 |
| M9-R22 | End-to-end stage timings and outcome denominators meet frozen per-class latency/resource budgets under normal, burst, cold, research and quota/auth-failure workloads. Infeasible or expired decisions stop visibly; no faster-scheduling claim hides quiet-window or queue delay. | A12, A16, A24, A30, A32, A33 |
| M9-R23 | Actual-model semantic trials and human-calibrated reviewer tests include correct/incorrect claims, relevant/irrelevant events, action/abstention and search/no-search cases. Matched-budget comparisons retain failures, uncertainty and no-benefit findings without changing main-policy review requirements. | A13–A18, A22, A23, A35–A38 |
| M9-R24 | Runtime records bind exact CLI/profile/prompt/tool/schema versions and the model identifier/version actually exposed; unavailable provider provenance stays unknown. Authorized probes cover useful tool loops, auth/quota failure, late replies and retry identity; changed intent under the same key is rejected. Vendor examples cannot establish installed capability or authorize migration. | A11, A13, A14, A24, A27, A28, A32 |
| M9-R25 | Every actual-model historical case records its date against the model's stated training cutoff or release date as the runtime exposes it; an unknown date counts every case as exposed. A predeclared sample reruns cases with the date removed or shifted and asks, without evidence, what happened next. Flagged cases still grade evidence handling and abstention, never predictive value. | A10, A35, A36, A38 |
| M9-R26 | Repeated trials of a frozen decision report action agreement and flip rate; isolated runs report the turnover and cost that disagreement adds. An "act only when most samples agree" variant is compared in isolation at the same total inference budget; no main-policy change without approval. | A10, A30, A35, A38 |
| M9-R27 | Before a news or calendar category may raise trigger priority, code computes a point-in-time event study on development data: BTC/SOL forward returns and volatility at approved horizons after its events versus matched windows without them, with counts, overlap handling and uncertainty. It informs the trigger-materiality freeze and cannot enable or disable a category or set a threshold by itself. | A06, A10, A16, A36 |
| M9-R28 | A successor promotion-request version (`PROMOTION_V2` unchanged) states how many hypotheses, candidates and trials were registered in the same envelope and family before this candidate, how often the holdout was reused, and the candidate's rank, and links the trial ledger; the evaluator addresses best-of-N selection. No overfitting or deflation estimator (such as PBO or the Deflated Sharpe Ratio) or threshold is imported without checking its assumptions (MI-15, TB-03); time boundaries and locked holdouts stay the primary control. | A10, A18, A19, A36 |

## 10. Implementation sequence and configuration gates

Implement one bounded batch at a time after M8 and M9 implementation authorization. Refresh this plan's progress/evidence at each checkpoint; do not execute the whole milestone from this deferred document without the B0 reconciliation.

| Batch | Work and exit evidence |
|---|---|
| B0 — reconcile and freeze | Verify section 3's M8 readiness evidence and deployment; stop affected work for unclosed material prerequisite defects. Map actual code/source rights, reconcile contracts/policy, freeze semantic evaluation cases and service-budget measurement procedure, and record the runtime integration choice. Define schemas, grants, versions and migration strategy; separate engineering choices from new authority. |
| B1 — collectors and source catalog | Reuse ingestion/security; implement selected APIs/RSS/page adapters, shared caching/limits, source health and permission-safe refresh. Deterministic fixtures first; authorized source smoke checks separately. |
| B2 — evidence and calendar | Implement event/revision/entity model, asset research records, timestamps, release vintages, dedupe/corrections, retention and recoverable event delivery. Prove replay, safe memory invalidation, comparable numeric features and no invented fields. |
| B3 — intelligence workflow and web tools | Add versioned analyst specialization, controlled search/page tools, bounded feedback and handoffs; prove pinned provider/profile capability and retry/cancel semantics, injection defenses and useful sourced assessments. Run the semantic cases prepared in B0, not only parser tests. |
| B4 — event scheduling and successor policy | Add cheap detectors, priority/coalescing/expiry/fairness and approved horizons; reconcile M7 schedule/limits. Instrument all latency stages, enforce bounded admission and test service budgets under bursts and quota/research pressure. |
| B5 — decisions and execution integration | Wire existing roles into the paper path with versioned advisory feasibility and authoritative revalidation. Extend the accepted predecessor's execution invalidation to M9 evidence/events; prove worker-down races, partial fills, immutable mandates and independent protection. |
| B6 — observability and compact UI | Join decisions and no-action outcomes to evidence/results; expose scoped feedback, truthful health and diagnostic export. Verify actual browser behavior, accessibility and redaction. |
| B7 — comparative evaluation | Run the frozen actual-model semantic/reviewer trials, isolated matched-budget comparisons and workload acceptance. Record failures, uncertainty and evidence for keeping or simplifying optional workflows; retain policy-required reviews. Apply the canonical agent-quality protocol without inventing a profitability threshold. |
| B8 — software release checks | Run affected M8 regressions and the implementation/isolated portions of M9-R01–R28 and Q01–Q10 against the intended release. Verify actual execution of the required checks (CI jobs, or the local harness while none exist), migration/restore/recovery, resources and authorized provider capability. Keep deployment/forward requirements pending B9; failed or unrun checks remain open. |
| B9 — deploy and observe | Deploy the accepted software to the normal app per the standing milestone procedure, preserving controls/data/secrets. Activate only with exact source/policy/runtime approvals and completed applicable checks; run the approved forward protocol, report results and close remaining acceptance evidence. Software deployment alone does not authorize activation or imply M9 acceptance. |

Freeze the following in their canonical locations; this plan deliberately does not invent numeric settings:

| Decision group | Required values/evidence before relevant activation |
|---|---|
| Sources/search | Selected endpoints, approved scopes and rights, authentication/cost, provider/global quotas, cache/retention, refresh/fallback behavior, search transport, capability probes and coverage gaps. |
| Scheduling/resources | Trigger materiality/hysteresis, source cadence/freshness, job/query/page/step and follow-up limits, investigation stopping rules, priorities/fairness, queue/concurrency bounds, reserved protection resources and overload/cancellation rules. |
| Trading policy | Approved horizons/features, evidence/review requirements, expiry, entry/exit/hold rules, original-mandate compatibility, re-entry/action/turnover limits and uncertainty handling. Financial values remain in RISK_POLICY and approved policy versions. |
| Evaluation/operations | Dataset/reference-set scope, benchmark/currency rules, forecast targets and calibration if used, grading protocol, untuned acceptance thresholds, supported PC/load, latency/freshness/resource budgets, memory/retention, incident triggers, forward observation protocol and stop conditions. |

Unresolved fields are **UNSET**, not defaults of unlimited/zero. Choose routine reversible engineering details from evidence; only genuinely new authority, spending or policy expansion needs the applicable owner decision. A missing key blocks that provider's activation, not offline scaffolding and fixtures. A missing required capability prevents a full M9 completion claim.

### Runtime integration decision

Keep the existing application broker as the authority boundary. B0 records why the then-installed `codex exec` integration remains suitable or why a bounded SDK/app-server comparison is warranted. Current OpenAI guidance supports bounded CLI jobs and offers SDK/app-server lifecycle interfaces; it does not prove lower latency, compatible capabilities or subscription access for this app. A new integration is not required merely to complete M9.

If proposing a change, compare the same permitted task/context/model where available: task correctness, full latency, context growth, cancellation/recovery, duplicate/unknown outcomes, auth refresh, quota behavior, tool isolation and maintenance cost. Record version/purpose/license and permission differences before adoption. Preserve role-bound tools, isolated credentials and disabled paid fallback. Prove positive and negative capabilities against the actual installed release; a model alias does not prove immutable provider weights. Bind durable operation keys to canonical request identity and reject changed intent under a reused key. Resolve uncertain outcomes through status lookup or idempotent retry of that same bound request, never a new key to bypass uncertainty or an invented success.

## 11. Proposed file and trust-boundary changes

B0 replaces this responsibility map with an exact file/migration inventory based on the accepted M8 tree. Read each nearest `AGENTS.md` before editing its subtree. No migration number, class name or future test command is asserted to exist now.

| Area | Canonical contracts and intended implementation responsibility |
|---|---|
| Source and evidence | [DATA_CONTRACTS](../../DATA_CONTRACTS.md), [MARKET_DATA](../../MARKET_DATA.md), [SECURITY](../../SECURITY.md); extend engine source adapters, validation, event persistence and migrations. Keep external network access in the approved fetch/broker service. |
| Agent orchestration | [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md), [RUNTIME_AGENTS](../RUNTIME_AGENTS.md), [RESEARCH_WORKFLOWS](../RESEARCH_WORKFLOWS.md); engine dispatcher/jobs and vetted runner prompts. No authoring skills, home directories or credentials enter runtime context. |
| Decisions and money | [ADAPTATION](../ADAPTATION.md), [STRATEGIES](../../STRATEGIES.md), [RISK_POLICY](../../RISK_POLICY.md), [PAPER_EXECUTION](../../PAPER_EXECUTION.md); evolve existing scheduling/intents/risk interfaces, leaving ledger posting exclusively in accounting. |
| Feedback and interface | [API_CONTRACTS](../../API_CONTRACTS.md), [FRONTEND](../../FRONTEND.md), [EVALUATION](../EVALUATION.md); scoped read APIs, typed UI state and reproducible outcome/evaluation records. |
| Delivery | [CONFIGURATION](../../CONFIGURATION.md), [OPERATIONS](../../OPERATIONS.md), [TESTING](../TESTING.md), [ACCEPTANCE_CHECKLIST](../../ACCEPTANCE_CHECKLIST.md), [COMMANDS](../COMMANDS.md), [INTEGRATION_EVIDENCE](../../INTEGRATION_EVIDENCE.md); isolated harnesses, official/version evidence, migration/restore and operating instructions. |

New tables must carry the same mode/account/approval/time boundaries as existing evidence and financial records. Preserve immutable historical approvals, manifests and position mandates. Typed schemas do not prove semantics: test code-enforced joins, privileges, deadlines, clocks and negative cases. Record each new dependency's purpose, compatible locked version, official source and license obligations; do not introduce another framework or parallel orchestration system without need.

## 12. Quality gates and verification commands

All Q01–Q10 apply to implemented M9. Their state here is **NOT RUN**; this documentation delivery assesses only Q07 documentation checking and Q10 specification/source traceability. It does not pass application gates.

| Gate | M9 acceptance evidence |
|---|---|
| Q01 | Actual event/evidence/decision/health workflows, including loading, empty, stale, error, unavailable and recovery states; compact default presentation. |
| Q02 | Keyboard/focus/labels/contrast/responsive and automated accessibility/browser evidence for changed UI, under the existing accessibility contract. |
| Q03 | M9-R01–R08 and M9-R14–R28 as applicable, exact accounting, feasibility/invalidation races, mode isolation, policy authority, assessment/benchmark semantics and memory revision/clock rules. |
| Q04 | Broker and UI authorization, SSRF/injection/redaction/adversarial probes; no broadened native capability or source/financial grants. |
| Q05 | Idempotent delivery/retry, corrections, malformed/stale input, cancellation, unknown commit, outage and restart tests. |
| Q06 | Section 7's frozen workload/service matrix, stage and tail latency, deadline admission, quota/cold/burst/research cases, fairness and protection isolation on declared hardware. |
| Q07 | Applicable containerized checks and real-model semantic/reviewer trials, including remembered-outcome audits and repeatability (R25–R26); release-bound execution of the required checks (CI or, while none exists, the local harness), repeated-trial results and authorized forward evidence distinguished from fixtures. |
| Q08 | Complete joined decision/no-action histories, health/coverage gaps, measured usage/delay, redacted diagnostics and actionable failure signals. |
| Q09 | Backup/isolated restore, forward migrations, reconciled restart and verified normal-app release with operating controls preserved. |
| Q10 | Official-version/source evidence, canonical contracts, scoped modules/dependencies, maintainable tests and Claude/ChatGPT handoff. |

Use actual commands from [COMMANDS](../COMMANDS.md) and the post-M8 test harness. B0 must implement/document any missing M9 harness phases before listing them as runnable. Run fixture tests in disposable, exactly named Docker resources with recorded responses and no paid calls; retain evidence before exact-name cleanup. Honor existing normal-app/pilot holds. No global prune, normal database reuse or runtime Docker socket/home/repo mount.

For documentation only, the existing `tools/check_links.py` checks relative Markdown targets/anchors in a network-disabled, read-only container, followed by `git diff --check`. The original handoff's command/output remain in [the M9 documentation record](../COMMANDS.md#m9-roadmap-documentation--2026-10-15); the 2026-10-16 additions have [their own verification record](../COMMANDS.md#m9m10-documentation-refinement--2026-10-16). External URL retrieval and a passing link check do not demonstrate provider capability or application correctness.

## 13. Failure, rollback and completion

An adapter or search failure records degraded coverage and its retry state; it cannot fabricate empty-as-complete data, silently switch to a paid service or widen destination permissions. Model/queue failure cancels or expires dependent decisions and preserves deterministic protection where the running engine and executable observations permit it. Required evidence failure blocks affected new exposure. Recovery does not replay old opportunities as new trades.

Before migrations, preserve data/secrets and verify backup/restore. Prefer forward-compatible additive migrations and staged feature enablement. Document which old/new software versions can manage every existing mandate. Roll back software only when schema and mandate compatibility is proven; otherwise stop new exposure, retain compatible protection and apply a reviewed forward fix. Never delete financial/event history or clear safety latches as rollback. Restoration must reconcile post-backup obligations rather than silently discard them.

Complete M9 only with its required implementation, resolved applicable gates, retained evidence, truthful forward findings and the accepted release running in the normal local app under [the deployment procedure](../../OPERATIONS.md#milestone-completion-deployment). Record source/image identities, URL, health/browser checks and actual activation state separately. An inactive deployment can deliver software while activation/forward acceptance remains open; say so explicitly. No automatic transition to real trading follows success.

## 14. Official guidance and implementation handoff

The [M9 official references](../contracts/REFERENCES.md#m9-documentation-research--2026-10-15) and [documentation evidence](../contracts/INTEGRATION_EVIDENCE.md#m9-planning-guidance--2026-10-15) distinguish vendor-documented behavior from this project's engineering decisions. Guidance supports scoped plans, verifiable checkpoints, instruction discovery, HTTP behavior, source interfaces and evaluation methods. It does not endorse this trading strategy, prove free-feed equivalence or establish future version compatibility.

The [shared M9/M10 research register](../contracts/REFERENCES.md#m9m10-agent-and-discovery-research--2026-10-16) adds official orchestration, context and evaluation guidance plus primary forecasting research. Apply the patterns through existing runtime contracts; vendor SDK examples do not establish subscription entitlements or justify replacing the runtime. [Evidence and limits](../contracts/INTEGRATION_EVIDENCE.md#m9m10-design-refinement--2026-10-16) distinguish source reads from unrun capability/performance tests.

The [readiness research register](../contracts/REFERENCES.md#agent-readiness-research--2026-10-16) adds official evaluation, latency, runtime, database-function and retry/check guidance for this refinement. [Its evidence record](../contracts/INTEGRATION_EVIDENCE.md#agent-readiness-refinement--2026-10-16) distinguishes inspected source, historical run records and unrun release requirements. Use the canonical [agent-quality protocol](../EVALUATION.md#future-m9m10-agent-quality-and-release-evidence) for acceptance claims.

The [2026-10-17 builder and study register](../../REFERENCES.md#trading-bot-builder-and-llm-trading-research--2026-10-17) and [its evidence record](../contracts/INTEGRATION_EVIDENCE.md#builder-and-llm-trading-findings--2026-10-17) support R25–R28. Most entries are preprints or self-reported builder accounts and are labeled as such; they motivate tests, not trading claims. The [additions](../EVALUATION.md#additions-proposed-on-2026-10-17-m9-r25r28-m10-r17) to the agent-quality protocol carry their method.

For Claude Code, retain existing `CLAUDE.md` imports of shared `AGENTS.md`; for Codex, follow repository/scoped instructions. For another ChatGPT implementation environment, supply repository access or the relevant files and require it to inspect them before edits. An assistant without the repository, Docker or provider access must report that limit rather than claim implementation/testing. Maintain progress and evidence in this plan so a context or usage-limit interruption can resume the exact next batch without reconstructing authority from chat memory.

Suggested implementation request, **to be used only after M8 and explicit M9 implementation authorization**:

> Implement M9 under ExecPlan 0027. First read the repository instructions, STATUS, DECISIONS, README and this plan; verify M8 acceptance and normal-local deployment. Complete B0 against the actual current tree and reconcile canonical contracts before changing behavior. Work one bounded batch at a time with concrete positive/negative checks and retained evidence. Preserve paper-only scope, existing position mandates, source/financial authority and the approved runtime boundary. Keep PROPOSED, OBSERVED, IMPLEMENTED, VERIFIED and NOT RUN distinct. Ask only for genuinely missing authority or a blocking owner decision. Do not enable collection, new tools or trading merely because code is deployed. Follow the milestone deployment procedure when software is accepted, report remaining activation/forward gates, and leave a precise next step if interrupted.

## 15. Progress, decisions and completion evidence

- OBSERVED 2026-10-15: owner authorized finalizing the M9 roadmap and handoff after the prior discussion; implementation remains deferred until after M8 and a subsequent implementation instruction.
- OBSERVED publication instruction, 2026-10-15: owner requested “merge this to main”. This authorizes committing, publishing and merging these M9 documents, without application implementation, deployment or activation. Preserve newer M7 work when integrating the documentation with current main.
- VERIFIED publication preparation: the nine-file change was integrated with main at `7b661a0`, preserving newer M7 records. The Docker link checker then examined 98 Markdown files with zero broken links and the same four historical warnings; the diff whitespace check passed and the disposable container was removed. PR/merge completion is not asserted by this preparation entry.
- DECIDED scope: hybrid collection plus active bounded web research; six information categories; extensible entity coverage; event-driven paper decisions; existing-role cooperation; complete decision/outcome records; minimal UI; measured evaluation and preserved authority/protection.
- IMPLEMENTED documentation: this future plan, roadmap/index/status/decision links, official source register and documentation verification record. No application code, configuration, source approval, migration, login, runtime capability or trading state is changed by this handoff.
- VERIFIED documentation checks: the existing Docker checker examined 94 Markdown files with zero broken links and four unchanged historical Windows-path warnings. `git diff --check` exited 0; the separate new-file comparison reported no whitespace errors (its new-file difference exits 1). Exact commands/results are in [COMMANDS](../COMMANDS.md#m9-roadmap-documentation--2026-10-15). Recheck closing evidence edits before delivery. This is Q07/Q10 documentation evidence only.
- NOT RUN: every M9 application test, provider capability probe, source integration, evaluation, migration, deployment and activation. B0–B9 are not started.
- Next implementation step, after the prerequisite/authorization gate: B0 post-M8 inspection and contract reconciliation. No polling cadence, search entitlement, risk value, latency target or return result is invented by this plan.

### 2026-10-16 — intelligence refinements and M10 boundary

- OBSERVED owner instruction: “continue editing now”, followed by continuation after a usage-limit interruption. Authorization covers the discussed documentation refinement and separate M10 specification, not implementation or activation. The owner clarified that fuller AI use refers to the app's agents.
- OBSERVED subsequent publication instruction: “Create pr and merge it”. Commit/publish/merge this documentation under [the publication record](../COMMANDS.md#m9m10-publication-preparation--2026-10-16); implementation, deployment and activation remain deferred.
- IMPLEMENTED documentation: active investigation/feedback, distinct assessment dimensions, token-impact reasoning, code-calculated relative strength, evidence-backed working memory, outcome research and M9-R14–R18. Broad coin discovery and trading expansion belong to ExecPlan 0028; M9 remains independently deliverable.
- VERIFIED documentation: the Docker checker examined 99 Markdown files with zero broken links and four unchanged historical warnings. Tracked-file and new-plan whitespace checks found no whitespace errors; the disposable container was removed. Actual commands/results and their limits are in [COMMANDS](../COMMANDS.md#m9m10-documentation-refinement--2026-10-16). Earlier checks above remain historical. This verifies only the scoped Q07/Q10 documentation work.
- NOT RUN: all new application requirements, runtime/provider probes, financial evaluation, migration, deployment and activation. No source, native-tool, asset or policy permission is expanded by these documents.

### 2026-10-16 — readiness and measured agent value

- OBSERVED owner instruction: research deeply and add a milestone or revise M9/M10, choosing the better placement. This authorizes documentation changes, not runtime implementation or activation.
- DECIDED: retain milestone order; require existing-control closure at M8, strengthen M9 with R19–R24, and carry those capabilities into M10. No additional role or late hardening milestone is required.
- IMPLEMENTED documentation: prerequisite closure, execution invalidation, advisory feasibility, measurable latency/quota behavior, semantic/reviewer evaluation and runtime choice/compatibility evidence. Canonical evaluation and roadmap links are updated with the handoff.
- VERIFIED first documentation pass: 99 Markdown files, zero broken links and four unchanged historical warnings; whitespace and exact-name cleanup checks passed. [COMMANDS](../COMMANDS.md#agent-readiness-documentation--2026-10-16) retains the commands and review refinements. All new application requirements remain NOT RUN; no current engineering score or profitability claim is upgraded by editing this plan.

### 2026-10-17 — builder and study findings

- OBSERVED owner instruction ([DECISIONS](../../DECISIONS.md#2026-10-17--builder-and-llm-trading-findings-recorded-as-proposed-m8m10-requirements)): record each finding as a PROPOSED requirement in the earliest milestone it affects; no new milestone; M7 is not touched while its final run is in progress. It authorizes documentation edits and an optional read-only measurement, not implementation, new strategy/grammar/envelope versions, approvals, activation or deployment.
- IMPLEMENTED documentation: M9-R25–R28, the status note in section 1 and the [protocol additions](../EVALUATION.md#additions-proposed-on-2026-10-17-m9-r25r28-m10-r17). No application, strategy, grammar, envelope, evaluation-protocol or promotion-request version changed.
- VERIFIED documentation: `python3 tools/check_links.py .` and `git diff --check` in the cloud session; results in [COMMANDS](../COMMANDS.md#builder-and-llm-trading-findings-documentation--2026-10-17).
- NOT RUN: every new requirement, and the optional real-candle warm-up measurement (the session's network policy denied the Binance hosts). B0–B9 are not started.

### 2026-10-18 — owner idea: agent roles and a coordinator

- OBSERVED owner request in the project thread, 2026-10-18 09:06 UTC: record the idea of adding roles to the agents, including a Coordinator agent that all other agents report to and that takes decisions and other important things, as a note to reference and implement later, with suggestions. It authorizes the note, not implementation or activation.
- IMPLEMENTED documentation: [the note](../ideas/agent-roles-and-coordinator.md), a pointer in section 5 and PROPOSED lines in the M8 and M9 roadmap entries. No requirement row, role, tool, grant, prompt or policy changed.
- VERIFIED documentation: `python3 tools/check_links.py .` and `git diff --check` in the cloud session; results in [COMMANDS](../COMMANDS.md#agent-roles-and-coordinator-idea-documentation--2026-10-18).
- NOT RUN: every suggestion in the note. B0–B9 are not started.
- OBSERVED 2026-10-18 09:21 UTC, owner's "do it" on the thread's four enhancements: the note gains E1–E4 (mistakes as research questions, disagreement as a signal, confidence checked against outcomes, fresher inputs before more agents), each PROPOSED and placed in M8 or M9. Documentation only; nothing else changed.
