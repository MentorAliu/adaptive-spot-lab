# ExecPlan 0028 — M10 coin discovery and controlled expansion

**2026-10-20 — re-scoped by [ExecPlan 0033](0033-m10-the-agents-look-beyond-btc-and-sol.md) under M8's rules ([ExecPlan 0031](0031-m8-simple-app-that-runs-itself.md)).** The owner's approvals per coin, the multi-provider registry, the PC load runs and the matched comparisons that this plan assumes are gone since M8 or deferred. Where the two plans differ, 0033 governs once the owner approves it; this plan stays as the design record, and 0033 §3 says what it keeps, defers or replaces. Nothing below is edited.

## 1. Status, order and authority

**2026-10-16 — future milestone specification; documentation authorized; application implementation NOT STARTED.** The owner authorized continuing the roadmap edits after discussing broader coin coverage, discovery and fuller use of the application's AI agents. This plan follows [M9](0027-m9-market-intelligence-and-event-driven-trading.md); it does not start either milestone, approve additional tradable coins, enable sources or authorize spending.

Start M10 application work only after M9 acceptance, verified normal-local deployment and an explicit M10 implementation instruction. Refresh this plan against that release before implementation. M9 remains independently deliverable for the approved BTC/SOL paper portfolio. The [roadmap](../../ROADMAP.md) owns order; [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md) owns permissions; [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md) owns tools. This proposed successor design does not override current contracts.

The 2026-10-16 readiness refinement strengthens this existing milestone instead of adding a later hardening milestone. B0 verifies M9-R19–R24 and their actual release evidence; M10-R15–R16 extend them to concurrent assets and discovery coverage. A new agent, more model calls or additional coins are not evidence of improved quality. The application changes and evaluations below remain NOT RUN.

**2026-10-17 research findings:** under the [owner's instruction](../../DECISIONS.md#2026-10-17--builder-and-llm-trading-findings-recorded-as-proposed-m8m10-requirements), M10-R17 makes universe size a declared factor: at the same total inference budget, compare the same workflow on BTC/SOL with each larger coin set, separately from specialist benefit. B0 also verifies M9-R25–R28. These are PROPOSED; no asset, source or policy is approved, and no milestone is added.

M10 has two separately gated stages. **Stage A discovers and researches assets; Stage B permits controlled expansion of the paper-trading universe.** A Stage A completion claim must name that scope; it cannot be reported as full M10 completion. Before behavior exceeds current BTC/SOL restrictions, reconcile the affected root instructions, [PROJECT](../../PROJECT.md) P02, [ACCEPTANCE_CHECKLIST](../../ACCEPTANCE_CHECKLIST.md) A01 and canonical contracts under an explicit owner scope decision. Preserve their historical versions and approvals. Planning additional coins now does not approve them for collection or trading.

Retain spot, long-only, local paper execution, exact accounting and independent risk controls. No private exchange credentials, live switch, leverage, shorts, paid model fallback, arbitrary native tools, runtime code generation or policy self-modification. Claude Code and ChatGPT/Codex are authoring clients; the runtime remains the approved subscription-based provider behind application-brokered tools.

## 2. Goal, outcomes and exclusions

Help the app find assets worth investigating, explain why and under what conditions their tokens might benefit, reject weak or untradeable candidates, and consider eligible opportunities alongside existing holdings. Discovery supplies evidence and hypotheses; neither a promising narrative nor a high rank is an instruction to buy. Success means measurable improvement in decision quality or after-cost paper outcomes under approved risk, not more assets, calls or trades by themselves.

| Stage | Observable outcome | Boundary |
|---|---|---|
| A — discovery and research | An approved broad scan yields a bounded shortlist, sourced investment hypotheses, opposing evidence, missing information, horizons and reasons for inclusion/rejection. An evaluator can challenge it and trigger a permitted follow-up. | Research/watchlist records only. No added main-portfolio trading eligibility or reserved funds. |
| B — controlled paper expansion | Explicitly approved assets with usable market data, execution assumptions and policy support can enter the existing event-driven decision/review/risk/paper-broker path. Existing holdings retain their mandates. | Technical eligibility, owner universe approval, policy approval and a current valid trade decision are separate checks. No per-trade owner prompt for routine already-approved actions. |

Coverage remains declared and bounded. Do not promise to monitor every coin, chain, website or event. DEX execution, wallets, chain-wide indexing, an on-chain trading adapter and comprehensive paid-data replacement are outside this milestone. Individual public on-chain or token-supply observations may be evaluated as approved evidence adapters; their semantics, rights, cost and reliability must be verified first. Conditional autonomous policy changes or a new financial authority are not implied by discovery.

## 3. Observed baseline and required post-M9 inspection

OBSERVED in the source based on `6bfe21ab85462e3b1df7f8f2ecd06ebb3bc66a06`, inspected for this documentation update:

- [Runtime roles](../RUNTIME_AGENTS.md) are ANALYST, RESEARCHER, EVALUATOR and COORDINATOR. One concurrent inference step is the initial local design choice, not a provider limit. [Runner invocation](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/agent-runner/runner/invocation.py) pins `rust-v0.159.2` and disables native web search in its current profile.
- [Engine API](../../../services/engine/app/main.py) has BTCUSDT/SOLUSDT literal types and two-symbol request bounds; [accounting](../../../services/engine/app/accounting.py) contains mappings specific to the present two-asset scope. [Market migration 0003](../../../services/engine/alembic/versions/0003_market_data.py) has explicit symbol constraints; [frontend schemas](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/apps/web/src/agents/schemas.ts) also enumerate two symbols.
- [MARKET_DATA](../../MARKET_DATA.md) describes the fixed two-symbol public collector, sampled quotes and no depth book or trade tape at that implemented boundary. Aggregate market-cap/volume data is not venue-specific executable liquidity.
- M9 is documented, not implemented by this task. [STATUS](../../STATUS.md) records the existing implementation evidence; this inspection is not a fresh observation of the deployed application.

These facts identify work, not defects in the approved current scope. B0 must enumerate the actual post-M9 constraints across data collection, ledger currencies, valuations, strategy grammar, policies, worker subscriptions, schemas, generated clients, UI, replay and tests. No ticker-only or prompt-only change can establish additional-asset support. Recheck installed provider versions and effective capabilities instead of assuming current online documentation matches the pinned runtime.

## 4. Shared sources, asset identity and screening

Reuse M9's source catalog, collectors, evidence store, event revisions, clock rules and global request budgets. Ordinary code fetches and normalizes shared feeds; the analyst chooses targeted follow-ups through the same approved tool broker. Separate per-source keys/rights/cost/limits from model-provider entitlement. A free endpoint or demo key is not proof of a sufficient production quota; record provider outages, retry/back-off, missing coverage and ingestion latency. No implicit paid fallback or access-control bypass.

Source candidates and their documented limits are in the [shared research register](../contracts/REFERENCES.md#m9m10-agent-and-discovery-research--2026-10-16). CoinGecko can provide provider identifiers and aggregate screening metrics; its keyless service is not proposed as a dependable scheduled production feed. Binance public market-data endpoints can provide venue metadata/quotes without private account access, subject to availability and limits. Neither establishes verified token fundamentals or executable depth by itself. Select actual providers and grants at B0; no provider is mandatory or approved by this document.

Create a versioned asset/instrument registry in [DATA_CONTRACTS](../../DATA_CONTRACTS.md). It must distinguish provider asset ID, chain and contract where applicable, native assets, aliases, venue pair, base/quote currency and instrument status. Preserve known-at/effective dates, provenance, migrations, redenominations and delistings. A symbol alone cannot join evidence: collisions, wrapped assets, bridges and reused tickers need explicit identity resolution. Ambiguous matches remain unresolved; do not transfer evidence or an approval automatically to a replacement token.

Persist the universe actually observable at each scan, including rejected, inactive and later-delisted entries when available. Do not reconstruct historical eligibility from today's surviving coin list. If historical membership, supply or venue metadata is unavailable, record the gap and narrow the evaluation claim. Provider plan restrictions on inactive listings are a coverage constraint, not permission to synthesize missing assets.

Screen cheaply before inference using approved, versioned rules and code-calculated features: identity quality, data age/coverage, permitted venue/instrument status, price history, supply fields, aggregate activity and venue spread/depth when available. Define comparable windows, timestamps, quote conversions and benchmarks explicitly. Metrics must retain their units and uncertainty; missing/stale inputs cannot silently become zero or a pass. Aggregate volume, popularity, search attention and recent returns are candidate signals, not proof of real liquidity, safety or future appreciation.

Screening bounds and exclusion reasons are recorded, including assets omitted by a capacity limit. Risk limits remain in [RISK_POLICY](../../RISK_POLICY.md). B0 freezes source scope, shortlist bounds and eligibility rules from measured evidence; this plan invents no minimum capitalization, volume, ranking weights or refresh interval.

## 5. Discovery workflow and full use of existing agents

Begin with a dedicated discovery workflow **under ANALYST authority**, using a versioned specialist prompt, scoped state, tools, budget and triggers. It is not automatically a fifth permission-bearing role, another provider/container or one agent per coin. Reuse shared records and avoid duplicate model analysis. Add a distinct role or concurrency only if evaluation shows benefit and the contracts, resource measurements and applicable approvals support it.

| Participant | Useful work | Permitted handoff |
|---|---|---|
| SYSTEM and collectors | Maintain source/identity records, cheap screens, candidate states, schedules and priority queues. Validate all model requests and results. | Deliver bounded evidence and commit authorized state transitions; no model-authored approval. |
| Discovery ANALYST | Select promising questions, seek primary evidence, compare alternatives, investigate contradictory claims, revise/reject a thesis and explain what would change it. | Propose a research/watchlist artifact or evidence-gap request. Cannot create trading eligibility or financial effects. |
| RESEARCHER | Turn an eligible hypothesis into a reproducible experiment using the existing registered grammar and approved research envelope; compare alternatives and retain failed attempts. | ResearchProposal/results through existing isolation. New operators/datasets/domains need their own grants; no generated-code execution. |
| EVALUATOR | Independently inspect exact evidence, shortlist methodology and drafts; challenge token-benefit claims, source independence, selection bias and unsupported confidence. | Version-bound review and deficiencies for SYSTEM to route to the appropriate permitted workflow. No new direct web-search grant. |
| COORDINATOR | Compare already-eligible opportunities with current positions, available capital, portfolio concentration and the option to do nothing. | Routine approved intents through the existing review/risk/accounting path; a request for expanded universe/policy remains pending owner approval. |

Distinguish an **asset candidate** from the existing **strategy candidate** and its promotion approval. Approving a strategy does not approve a new coin; approving a coin does not approve a strategy, source or higher cap. B0 defines the precise new artifact/tool schemas and handoffs in their canonical documents. Role text alone cannot grant a write, scheduling or network capability.

An investigation asks a concrete decision-relevant question, retrieves only necessary evidence, states alternatives and stops when it reaches a supported conclusion, cannot obtain decisive evidence, reaches its budget/deadline or is no longer relevant. Independent review can return specific deficiencies for bounded follow-up; this is not an endless consensus loop. Every round retains its evidence revision, reason and effect on the conclusion. Do not launch a formal experiment before every trade or require all four roles on every scan.

Use four assessment dimensions from M9: fundamentals/token economics, macro conditions, relative market behavior and execution conditions. Explain the hypothesized mechanism connecting an event to token demand/supply/value, its horizon, effective dates, prerequisites and invalidation evidence. Authentic partnerships or announcements do not prove adoption, revenue or token-holder benefit. Unlock schedules, circulating supply, governance powers, network activity or concentration metrics are usable only with verified definitions and provenance; unknowns stay unknown. Distinguish source reliability, entity match, causal uncertainty and action confidence. A sentiment label or unexplained aggregate score is insufficient.

Reuse M9's evidence-backed asset research record for concise theses, contrary evidence, open questions, catalysts, decisions and invalidation conditions. Retrieval rechecks source grants, as-of clocks, expiry and revisions; memory is not an authority or a way to leak a locked holdout. Preserve superseded reasoning for audit without treating it as current truth. Outcome review may propose bounded research; it cannot rewrite previous decisions or self-edit risk, policy, prompts or tool permissions.

## 6. Triggers, candidate lifecycle and resource limits

The application schedules low-cost scans and wakes the workflow on material approved events, identity/status changes, significant screening changes, an approaching verified catalyst or a prior review becoming invalid. Agents run bounded jobs; they do not think continuously or wait in a loop. Scheduled cadence and event thresholds are frozen from source limits, measured latency and useful horizon. Local downtime remains visible and cannot be repaired with backdated decisions.

Use separate recorded states for discovered, screened/rejected, under investigation, watchlisted, technically eligible and owner-approved for a specific paper universe/policy. These are proposed concepts, not current enum names. Store the applicable version, evidence/review, reason, expiry and scope for every transition. SYSTEM validates and commits transitions; the model can propose them. Watchlisting never reserves money, schedules an executable order or grants market/source permissions.

Corrections, contract migrations, instrument suspension, source revocation, stale data or changed eligibility invalidate affected recommendations and pending intents. An expired or withdrawn recommendation cannot return through cached context or a late job. Existing positions retain their original mandate and deterministic protection; removing entry eligibility cannot orphan a holding. Represent stale/unresolved protection honestly if the engine lacks usable executable observations.

Before dispatch and each side effect, recheck role, source and universe scope, job lineage, budget, cancellation and deadline. Coalesce duplicate events and shared lookups across coins. Reserve capacity for ingestion, protection and urgent existing-position decisions before discovery; avoid both discovery starvation and discovery monopolizing the runtime. Freeze queue/step/query/page/experiment/token or available-usage limits and any concurrency from measurements on the supported PC. Missing provider usage stays missing, not zero. No increased provider entitlement or available parallel inference is assumed.

## 7. Controlled expansion of the paper engine

Stage B must explicitly reconcile current scope before enabling additional assets, then implement and verify the required code changes. Do not globally remove the two-symbol checks and regard the resulting unrestricted universe as approved.

| Boundary | Required behavior |
|---|---|
| Universe and policy | Versioned owner approval identifies permitted assets/instruments and policy domains. Source/observation permission, research permission, technical eligibility and trading approval remain separate. Unknown/newly listed symbols default ineligible. Recheck exact versions at decision, review, reservation and execution. |
| Market/execution evidence | Verify instrument status, base/quote identities, precision, filters, observation continuity, freshness, fees and the paper-fill model's needed liquidity inputs. A non-tradable benchmark can inform analysis under its source grant without becoming a trading asset. |
| Accounting and valuation | Replace scope-specific asset mappings safely; use exact Decimal/NUMERIC and code-owned currency/quantity validation. Prove reservations, partial fills, fees, pending sells, mark-to-market and NAV across multiple holdings and unchanged funding rules. Unsupported quote currencies or conversions fail explicitly. |
| Portfolio policy | Evaluate aggregate and per-asset exposure, concentration, shared catalysts/correlations and correlated liquidity stress. Multiple coin names do not establish diversification. New policy limits require owner approval and cannot raise existing hard caps implicitly. |
| Position mandates | Store original universe/instrument/policy versions and permitted management actions. Universe removal blocks new exposure but does not remove existing obligations, loosen stops or force an unauthorized exit. Delisting or unavailable quotes follow a declared truthful incident policy, never a fabricated fill. |
| API and UI | Replace fixed enums and array limits only with validated approved-registry semantics; regenerate applicable clients and migrate schemas. Show coverage, eligibility and approval separately, with compact discovery summaries and expandable evidence. |

Retain atomicity, idempotency, fencing and reconciliation across simultaneous assets; several small trades cannot bypass shared caps. Revalidate fast-changing evidence and costs before acting, including when an opportunity has expired during research. Benchmark/screen prices and web headlines cannot be used as fill observations. Material changes invalidate required evaluator reviews. Existing deterministic protection continues independently of model availability within the engine/data limits.

Reuse M9's code-calculated advisory feasibility and execution invalidation, then prove their multi-asset behavior. A candidate/source/universe suspension must block later affected risk-increasing effects with discovery and agent workers stopped. Concurrent proposals for different coins compete against one current portfolio capacity; isolated per-coin capacity is not permission to exceed a shared cap. Unsupported valuation/conversion or stale cost inputs remain unavailable. After a partial fill or universe removal, cancel invalid new exposure under policy while preserving the existing holding's original mandate. M10 must not introduce a second prompt-based risk calculation or weaken M9's fencing to increase scan throughput.

## 8. Evaluation and evidence of added value

Freeze a staged evaluation protocol before interpreting results. Use chronological information availability, actual source vintages/universe membership, explicit decision latency and conservative, labeled execution assumptions. Include inactive/delisted/rejected candidates and all attempted screens/research trials where observable; disclose missing history rather than invent it. Point-in-time retrieval alone cannot remove a pretrained model's possible knowledge of later historical outcomes, so distinguish historical tests from separately authorized forward evidence.

Compare a cheap deterministic screen, the general analyst and the specialist discovery workflow on the **same universe, available evidence, observation period and total inference/work budget**. Isolate extra-coin access as another comparison, rather than crediting specialization for access to more assets or more calls. For trading comparisons retain matched contributions, costs, timing and policy constraints. Report workload/coverage differences explicitly when exact matching is impossible. M10-R17 (PROPOSED 2026-10-17) declares universe size as such a factor. A repeated headline, copied announcement or same-model agreement is not independent confirmation.

Measure trace/tool correctness, citation/claim support, unresolved identity errors, review usefulness, decision staleness, retained/rejected candidates, shortlist coverage, churn, resource cost and downstream outcomes. Numeric features and financial results are calculated in code. Use deterministic checks and sampled human-calibrated grading for interpretive claims; model grading alone cannot certify correctness. If forecasting probabilities is approved, define the outcome/horizon and label availability first, then assess proper scoring/calibration on held-out and forward observations; qualitative confidence must not be presented as a calibrated probability.

Measure net results, drawdown, turnover, execution feasibility and opportunity cost with uncertainty, including failed investigations, abstentions and missed opportunities under a declared denominator. Never assume rejected assets would have been profitably executable. Segment material model/prompt/source/universe/policy changes; preserve all trials and holdout boundaries to avoid selecting a favorable backtest. Define acceptance/stop criteria before tuning; no universal profit, trade-count, duration or statistical threshold is supplied by this plan. Lack of evidence can support keeping the simpler workflow or leaving Stage B inactive.

Apply the canonical [agent-quality protocol](../EVALUATION.md#future-m9m10-agent-quality-and-release-evidence): repeated actual-model trials, evaluator false acceptance/refusal, calibrated grading, and a permitted bounded audit of candidates excluded by the cheap screen. Freeze reference-set coverage and denominators before assessing missed opportunities; measuring only shortlisted candidates cannot establish discovery coverage. Preserve unavailable/ambiguous cases rather than labeling them failures or negatives without evidence.

Repeat M9's service-budget workloads at the proposed asset/scan scale: correlated news bursts, one noisy asset, simultaneous position events, shared quotas and competing experiments. Verify urgent position work across assets, bounded fairness and expiry, while deterministic protection remains independently resourced. Keep discovery inactive or at the last measured supported scope when budgets or quality gates fail; do not buy capacity, add concurrency or approve coins automatically. Expansion's benefit and specialist-agent benefit remain separate comparisons.

## 9. Requirements mapped to verification

All rows are **PROPOSED / NOT RUN**. A-row mappings refer to existing invariants; B0 must explicitly reconcile their future asset scope before claiming expanded coverage. Fixtures demonstrate behavior, not profitability.

| ID | Positive and negative acceptance cases | Existing coverage |
|---|---|---|
| M10-R01 | Resolve provider/chain/contract/pair identities and migrations as of observation time; reject symbol collisions and ambiguous mappings. Retain inactive/rejected records without present-day survivor leakage. | A06, A10, A15, A34 |
| M10-R02 | Shared bounded collectors/screens preserve provenance, units, comparable windows and missing values; quota/outage/stale/unsupported-source cases cannot invent fields, buy access or approve assets. | A06, A14, A15, A28, A33, A34 |
| M10-R03 | A specialist requests relevant evidence, distinguishes authentic news from token benefit, states contrary evidence/horizon and revises or abstains. Duplicate narratives and unsupported supply/causal claims fail review. | A13–A15, A23, A26 |
| M10-R04 | Typed handoffs and an evaluator deficiency produce a permitted bounded follow-up or visible stop. Research stays inside its grammar/envelope; no evaluator search, role escalation, arbitrary code or native-tool path. | A14, A17–A19, A22–A24, A28 |
| M10-R05 | Candidate/watchlist/eligibility/approval states stay distinct; expiration, correction, restart and revocation invalidate dependent drafts. Neither strategy promotion nor a shortlist grants asset permission or reserves funds. | A09, A22, A24, A25, A27 |
| M10-R06 | Stage B accepts only exact approved asset/instrument/policy scope, rechecked at each effect. Unknown assets, forged approvals, changed versions and late jobs create no financial effects. | A01, A09, A14, A20–A25, A27 |
| M10-R07 | Multi-asset accounting, valuation, fees, reservations, partial fills, concurrent sells and restarts reconcile exactly; old BTC/SOL records and mandates retain identical meaning. | A02, A07–A09, A21, A29–A31 |
| M10-R08 | Venue status/filter changes, stale quotes, insufficient execution evidence, unsupported conversions and delistings block affected exposure; aggregate quotes cannot fill orders or fabricate exits. | A06, A08, A12, A31, A34 |
| M10-R09 | Correlated holdings, shared catalysts, split orders and simultaneous intents cannot bypass portfolio limits. Discovery cannot raise caps or weaken original-position protection. | A08, A09, A25, A29–A33 |
| M10-R10 | Evaluation uses point-in-time membership/evidence, retained trial/rejection history and locked holdouts; survivor selection, later model knowledge and unavailable historical data remain disclosed limitations. | A06, A10, A18, A35, A36 |
| M10-R11 | Compare simple/general/specialist workflows with matched universe/data/total budget; separate universe expansion, inference cost and real-input forward evidence from fixture results. Probabilities, if used, have defined targets and calibration evidence. | A10, A26, A35, A36, A38 |
| M10-R12 | Bursts, oversized candidate sets, prompt injection, cancellation and model/quota failures stay bounded; protection and urgent position work meet frozen resource budgets without native escalation. | A03, A14, A16, A24, A28, A32–A34 |
| M10-R13 | Compact UI and redacted diagnostics reconstruct candidate inclusion/rejection, evidence/review, eligibility, approval, decision and no-action reasons; loading/stale/error/unavailable states and accessibility pass browser checks. | A04–A06, A12, A26 |
| M10-R14 | Backup/restore, migration, source/universe revocation and recovery preserve holdings/history; verified local deployment plus a separately authorized forward workflow close applicable gates. No old opportunity is replayed as a new fill. | A03, A07, A12, A24, A25, A32, A37, A38 |
| M10-R15 | Reuse M9 readiness/feasibility/invalidation and prove them across assets: worker-down suspension, partial fills, concurrent shared-capacity proposals and unavailable conversions. No per-coin risk calculation or delayed eligibility propagation bypasses portfolio authority. | A07–A09, A21, A24, A25, A29–A33 |
| M10-R16 | Test actual-model specialist/reviewer quality and the screen's missed-candidate coverage on a declared permitted reference set, including rejected/unavailable cases. Multi-asset burst/quota/noisy-asset workloads meet frozen fairness/latency budgets; unsupported scale or inconclusive benefit cannot auto-enable expansion. | A10, A13–A16, A22, A33, A35–A38 |
| M10-R17 | Universe size is a declared factor: at the same total inference budget, decision quality, review deficiencies, abstention and after-cost results of the same workflow are compared on BTC/SOL and on each larger coin set, separately from specialist benefit; a larger set's after-cost results come from isolated runs until Stage B permits trading it. A larger set's result cannot be credited to specialization or approve an asset. | A10, A35, A36, A38 |

## 10. Sequence and configuration gates

Implement one bounded batch at a time, recording actual changes/results and the exact next step. The following is a deferred sequence, not permission to start it now.

| Batch | Work and exit evidence |
|---|---|
| B0 — inspect and reconcile | Verify M9 acceptance/deployment, R19–R28 evidence and implementation instruction; inventory actual scope assumptions, grants and source rights. Reconcile Stage A scope; freeze schemas, versions, semantic/reviewer cases, rejected-candidate audit and scaled workload budgets, plus the explicit Stage B approval boundary. |
| B1 — registry and screening | Implement point-in-time identity/universe records, shared adapters and deterministic bounded screens; prove historical, missing/stale, ambiguous and quota cases in isolation. |
| B2 — discovery and handoffs | Implement analyst specialization, evidence-backed memory and candidate lifecycle; integrate permitted researcher/evaluator/coordinator handoffs and stopping rules. Prove meaningful tool use plus denied escalation and invalidated results. |
| B3 — Stage A checkpoint | Complete research-only UI/health and matched actual-model simple/general/specialist comparisons, including screen coverage and reviewer errors. Run applicable Stage A parts of R01–R05 and R10–R17 (R17 only in isolated, research-only comparisons); record source smoke evidence, burst/fairness results and negative/inconclusive findings. No expanded trading. |
| B4 — Stage B scope and migration | Obtain the broader paper-universe scope decision if still missing; reconcile root/PROJECT/A01 and every affected contract before expanding behavior. Freeze eligibility/approval/policy semantics and exact data/schema migration inventory. Prove backup/restore and preservation of existing records; missing per-asset activation settings remain UNSET. |
| B5 — engine and policy support | Implement generalized market/ledger/valuation/strategy/API paths and registry enforcement; verify R06–R09 and R15, including worker-down invalidation, shared-capacity feasibility, concurrent actions and deactivation with partial/open positions. |
| B6 — operations and interface | Finish compact owner views, scope controls, diagnostics, retention, prioritized scheduling and failure recovery. Use official shadcn discovery and chart guidance when implementing affected UI. |
| B7 — release verification | Run all implementation/isolated portions of R01–R17, affected M8/M9 regressions and Q01–Q10 against the intended release; record executed required checks (CI, or the local harness while the repository has none), real-model quality/capability, security, restore, scaled resources and comparison evidence. Keep forward/deployment requirements open for B8. |
| B8 — deploy and observe | Deploy accepted software to the normal app using the milestone procedure; preserve approved controls, data and secrets. Activate only the separately approved sources/universe/policy, then execute the frozen authorized forward protocol and report remaining gates or full completion honestly. |

Stage A can be delivered as a named checkpoint under the deployment procedure without enabling Stage B. Full M10 remains open while required Stage B or forward evidence is missing. Scaffolding and isolated synthetic tests do not need real asset activation, paid subscriptions or new credentials.

Before relevant activation, freeze source grants/rights/keys/costs and coverage; registry/identity/eligibility rules; scan/trigger/freshness/expiry values; job/concurrency/query/experiment budgets; approved universe, instruments, strategy domains and execution assumptions; retention/incident policies; evaluation baselines, total budgets, hardware, latency targets and stop criteria. Keep values in their canonical owners, not duplicated here. UNSET cannot mean unlimited, automatically approved or zero cost. Resolve routine implementation choices from evidence; ask only for missing authority or genuinely blocking owner decisions.

## 11. Proposed file map and trust boundaries

B0 replaces this responsibility map with exact files/migrations against accepted M9. Read each subtree's nearest AGENTS.md before edits. New record names in this plan describe responsibilities, not existing database objects or granted tools.

| Area | Canonical documents and implementation responsibility |
|---|---|
| Scope and grants | Root [AGENTS](../../../AGENTS.md), [PROJECT](../../PROJECT.md), [DECISIONS](../../DECISIONS.md), [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), [ACCEPTANCE_CHECKLIST](../../ACCEPTANCE_CHECKLIST.md); explicitly version the scope decision and preserve prior approvals. |
| Registry/evidence | [DATA_CONTRACTS](../../DATA_CONTRACTS.md), [MARKET_DATA](../../MARKET_DATA.md), [SECURITY](../../SECURITY.md); shared engine collectors, registry/evidence storage and forward migrations. All external content remains untrusted data. |
| Agents and research | [RUNTIME_AGENTS](../RUNTIME_AGENTS.md), [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md), [RESEARCH_WORKFLOWS](../RESEARCH_WORKFLOWS.md); engine jobs/dispatcher, vetted versioned prompts and scoped artifact schemas. |
| Portfolio and execution | [STRATEGIES](../../STRATEGIES.md), [ADAPTATION](../ADAPTATION.md), [RISK_POLICY](../../RISK_POLICY.md), [LEDGER](../../LEDGER.md), [PAPER_EXECUTION](../../PAPER_EXECUTION.md); symbol/currency semantics, policy joins, accounting and worker authority. |
| Evaluation and UI | [EVALUATION](../EVALUATION.md), [API_CONTRACTS](../../API_CONTRACTS.md), [FRONTEND](../../FRONTEND.md); point-in-time comparisons, generated schemas/clients, compact research/approval/health views and browser checks. |
| Delivery | [CONFIGURATION](../../CONFIGURATION.md), [DOCKER](../../DOCKER.md), [OPERATIONS](../../OPERATIONS.md), [TESTING](../TESTING.md), [COMMANDS](../COMMANDS.md), [INTEGRATION_EVIDENCE](../../INTEGRATION_EVIDENCE.md); reproducible harnesses, compatibility, recovery and deployment records. |

No model gains database credentials or direct ledger/state write privileges. Permissions are checked on every scoped tool call, including retrieval and cached results. Root instructions/development skills/MCP configuration and authoring credentials never enter runtime contexts. New sources, dependencies or SDKs require a recorded purpose, official guidance, compatible pinned version and license obligations; do not install orchestration machinery merely to create a specialist workflow.

## 12. Quality gates and verification commands

Q01–Q10 apply to implemented M10 and are **NOT RUN** here. This documentation delivery assesses only documentation checking under Q07 and specification/source traceability under Q10; it does not pass application gates.

| Gate | Required M10 evidence |
|---|---|
| Q01 | Discovery-to-approval-to-decision flows, all candidate/availability states and compact UI actually usable in the browser. |
| Q02 | Applicable keyboard/focus/labels/contrast/responsive and automated accessibility checks using the existing frontend contract. |
| Q03 | R01–R09 and R15 semantics, exact accounting, point-in-time registry, advisory feasibility, worker-down invalidation, immutable mandates and concurrent effect boundaries. |
| Q04 | Role/source/universe authorization, SSRF/injection/secret redaction and adversarial stored-memory/identity artifacts; no native or financial escalation. |
| Q05 | Corrections, stale data, provider failure, unknown commit, cancellation, restart, migration and invalidation recovery. |
| Q06 | R16's measured scan/correlated/noisy-asset bursts and simultaneous portfolio work; latency, fairness, quotas and protection isolation against frozen budgets. |
| Q07 | Applicable executed Docker/CI checks and repeated actual-model semantic/reviewer trials, plus R17's universe-size comparison; screen-coverage audits, capability and forward observations recorded separately. |
| Q08 | Joined candidate/evidence/review/approval/trade/no-action histories, honest gaps/usage, failures and redacted diagnostic export. |
| Q09 | Backup/restore, compatible forward migration, preserved old positions/approvals and the accepted release verified in the normal local app. |
| Q10 | Canonical scope reconciliation, official/locked-version evidence, maintainable modules/dependencies, all-trial evaluation and resumable handoff. |

Use actual post-M9 harness commands from [COMMANDS](../COMMANDS.md). B0 implements/documents missing M10 phases before calling them runnable; no fictional command or migration number is supplied here. Use disposable exactly named Docker resources and isolated databases for fixtures/replay; retain evidence before exact-name cleanup. No global prune, normal-app database reuse or runtime Docker socket/home/repository mount.

For this documentation delivery only, run the existing `tools/check_links.py` in a read-only, network-disabled container, `git diff --check` and a whitespace check of this new untracked plan. Exact commands/results are in [the documentation record](../COMMANDS.md#m9m10-documentation-refinement--2026-10-16). Link checking does not validate remote provider behavior, application correctness or trading value.

## 13. Failure, rollback and completion

Discovery failure stops or expires that work and leaves the existing approved portfolio workflow operational within its own requirements. No-source/ambiguous-identity/unusable-market cases remain visible exclusions. Lost source or universe authority stops affected new exposure and invalidates queued/late work; it cannot liquidate an unquoted asset at an invented price or disable an existing mandate. Engine downtime remains an actual protection gap.

Before state migration, retain backup/restore evidence and verify compatibility with every current holding and historical approval. Prefer additive migrations and controlled activation. Roll back code only when its schema, asset and mandate support is proven; otherwise stop new exposure, retain compatible protection and apply a reviewed forward fix. Returning to two-asset code is unsafe if it cannot represent or manage newer holdings. Do not delete assets, balances, contributions, history or safety latches to make rollback succeed.

Full M10 completion requires R01–R17, resolved applicable gates, truthful comparative/forward findings and the accepted software running in the normal local app under [OPERATIONS](../../OPERATIONS.md#milestone-completion-deployment). Record running source/image identity, URL, readiness/browser checks and actual source/universe/policy activation separately. Software acceptance, Stage A delivery or inert deployment alone cannot establish full completion, profitability or permission for real trading.

## 14. Official guidance and implementation handoff

The [research register](../contracts/REFERENCES.md#m9m10-agent-and-discovery-research--2026-10-16) covers official agent orchestration/context/evaluation guidance, candidate market-data interfaces and primary forecasting/selection research. [Integration evidence](../contracts/INTEGRATION_EVIDENCE.md#m9m10-design-refinement--2026-10-16) records what was read and what was not tested. These support engineering choices; they do not recommend a profitable trading system, certify a provider plan or establish compatibility with the runtime's pinned version.

The [readiness research](../contracts/REFERENCES.md#agent-readiness-research--2026-10-16) and [corresponding evidence](../contracts/INTEGRATION_EVIDENCE.md#agent-readiness-refinement--2026-10-16) support the inherited reliability, runtime and evaluation requirements. Keep their detailed acceptance semantics in M9 and EVALUATION; do not duplicate mutable limits or create another orchestration layer for discovery.

The [2026-10-17 builder and study register](../../REFERENCES.md#trading-bot-builder-and-llm-trading-research--2026-10-17) supports R17 and the inherited M9-R25–R28; the [protocol additions](../EVALUATION.md#additions-proposed-on-2026-10-17-m9-r25r28-m10-r17) carry the method. Those sources are mostly preprints and self-reported builder accounts, labeled as such.

Before implementation, read root/scoped instructions, STATUS, this plan, README and the relevant canonical contracts. Retain CLAUDE.md's shared imports for Claude Code; Codex follows AGENTS.md. Another ChatGPT environment needs the actual repository and execution access to make verified changes; missing access must be reported. Keep batch progress, exact evidence and unresolved authority in this plan so interruption does not depend on reconstructing chat history.

Suggested request, **only after M9 acceptance/deployment and M10 implementation authorization**:

> Implement M10 under ExecPlan 0028. Verify prerequisites and complete B0 against the current source first. Deliver Stage A within approved research permissions; keep Stage B behind its explicit scope and activation gates. Use the existing application roles for active investigation, experiments, independent review and policy-bounded decisions. Reconcile canonical contracts before changing scope, work one bounded batch at a time, and retain positive/negative verification and all-trial evidence. Preserve paper-only authority, exact accounting, original mandates and runtime isolation. Report OBSERVED, IMPLEMENTED, VERIFIED and NOT RUN separately; deploy accepted software under the milestone procedure without silently enabling new assets or sources. Record the exact next step if interrupted.

## 15. Progress, decisions and completion evidence

- OBSERVED 2026-10-16: owner authorized continuation of documentation editing after the discussion and a usage-limit interruption. The clarification about fuller agent use refers to the application's agents. No authoring-agent delegation is required by this plan.
- OBSERVED subsequent owner instruction: “Create pr and merge it”. [Publication preparation](../COMMANDS.md#m9m10-publication-preparation--2026-10-16) records the authorized commit/push/merge scope; no application work or activation is authorized by it.
- DECIDED design boundary: improve M9 intelligence within its original portfolio scope; put broad discovery and controlled additional-coin support in M10. A dedicated analyst specialization is the initial engineering proposal, subject to evaluation, rather than a new permission-bearing role by default.
- IMPLEMENTED documentation: this future handoff and its roadmap/index/acceptance/decision/source links. Stages A/B, B0–B8 and every application requirement remain unimplemented by this task.
- VERIFIED documentation: the Docker checker examined 99 Markdown files with zero broken links and four unchanged historical warnings. Whitespace checks found no errors; the disposable container was removed. [COMMANDS](../COMMANDS.md#m9m10-documentation-refinement--2026-10-16) records results and limitations. This is scoped Q07/Q10 documentation evidence, not application acceptance.
- NOT RUN: M10 code/tests, provider/model/source probes, financial evaluation, migrations, deployment, expanded asset collection or trading activation. No model accuracy, candidate quality or return claim is made.
- Next step for implementation, once its gate is satisfied: B0 post-M9 inspection, scope reconciliation and the concrete source/tool/evaluation inventory.

### 2026-10-16 — inherited readiness and discovery coverage

- OBSERVED: the owner requested deep research and delegated whether to add a milestone or refine M9/M10. The selected documentation design retains both milestones and carries M9's measurable readiness into expansion.
- IMPLEMENTED documentation: R15–R16, worker-down multi-asset invalidation and advisory feasibility, actual-model reviewer/specialist trials, screening coverage and scaled latency/fairness gates. These are proposed implementation requirements, not passed tests.
- VERIFIED first documentation pass: 99 Markdown files, zero broken links, four unchanged historical warnings and clean whitespace; exact-name cleanup confirmed. [COMMANDS](../COMMANDS.md#agent-readiness-documentation--2026-10-16) retains evidence and review refinements. Application/provider/evaluation/deployment checks and all new activation remain NOT RUN.

### 2026-10-17 — universe size as a declared factor

- OBSERVED owner instruction ([DECISIONS](../../DECISIONS.md#2026-10-17--builder-and-llm-trading-findings-recorded-as-proposed-m8m10-requirements)): record each research finding as a PROPOSED requirement in the earliest milestone it affects; this one is M10's. Documentation only; no implementation, asset or source approval, activation or deployment.
- IMPLEMENTED documentation: M10-R17, the status note in section 1, and the R01–R17 and R19–R28 references.
- VERIFIED documentation: link and whitespace checks in [COMMANDS](../COMMANDS.md#builder-and-llm-trading-findings-documentation--2026-10-17). R17 itself is NOT RUN.
