# Strategy registry and reference strategy

## Role

A strategy/decision policy is a versioned executable contract. `FIXED` and `ADAPTIVE_SELECTOR` policies have explicit mathematical rules. `AGENT_DRIVEN` has an explicit operating/tool/evidence/management contract while permitting model discretion for entry and exit decisions. Free-form prose alone is never executable authority. Each version declares universe, horizon, features and evidence, management/maximum-hold policy, costs, allowed action/parameter domains, model/prompt/tool versions where relevant, and approval. Hash its implementation and configuration into the experiment manifest.

Use the candidate lifecycle in [RESEARCH_WORKFLOWS.md](../RESEARCH_WORKFLOWS.md). Research/shadow eligibility is distinct from main approval. A research result never approves itself. The owner can approve an operating policy or bounded selection/domain once; introducing new main logic or widening that domain requires approval. Runtime candidates are declarative; new executable operators use reviewed development.

## First reference: TREND_REFERENCE_V1

The following is an **untested engineering/research seed**, chosen to exercise the system with explicit rules. None of its parameters is claimed profitable or optimal. It must be displayed and approved before forward use.

| Property | Proposed seed definition |
|---|---|
| Instruments | BTCUSDT and SOLUSDT, and under `AGENT_POLICY_V3` also ZECUSDT, NEARUSDT and XRPUSDT, each independently, subject to portfolio caps |
| Timeframe | Finalized 1h candles |
| Signal | Enter on an upward crossing of EMA(20) over EMA(50): previous fast <= slow and current fast > slow |
| Warm-up | At least 100 consecutive valid finalized bars; both EMA values and ATR available; reset/rebuild after a material gap |
| Volatility | Wilder-smoothed ATR(14), with explicitly tested initialization |
| Initial protective stop | Entry reference minus 2 × signal-time ATR; validate positive price and execution-gap risk |
| Trend exit | Finalized-bar downward EMA crossing under the symmetric rule |
| Time exit | At most 72 elapsed hours from first fill, generating an exit intent at the first eligible observation thereafter |
| Re-entry | A new upward crossing after the position is closed; no immediate looping on the same event |
| Position ownership | One position per symbol; no averaging down/pyramiding |
| Allowed parameter range initially | Exact seed values only; other values are separate research versions until approved |

EMA seed uses the simple average of its first complete period, then alpha = 2/(n+1). ATR uses true range max(high-low, abs(high-prev_close), abs(low-prev_close)); seed from the first complete set of 14 true-range observations, then Wilder's recurrence. State the initial prior-close requirement and compare implementation against hand-calculated fixtures. Warm-up length is a declared engineering choice, not evidence of convergence/edge.

A stop reference is part of the pretrade proposal. Sizing includes approved entry/cost uncertainty. Recheck stop distance and risk at modeled fill; an unfavorable fill cannot silently exceed the accepted entry envelope. Original stop and time/trend exit mandate are immutable for the position. Protective stop observation uses fresh executable-side evidence, not only candle closes. Specify precedence when stop and signal/time exits coincide: one position-closing intent, no double sell.

The reference is useful even if it loses money: it tests accounting, simulation and baseline comparisons. Do not tune it on the evaluation period and continue calling the result the original reference.

## Later candidate families

### M6 candidate grammar and engine interface (ExecPlan 0023 B2)

IMPLEMENTED in `app/research/grammar.py`, `interpreter.py`, `strategy.py` and
`app/strategies/interface.py`, `operators.py`; verification state is recorded in
[ExecPlan 0023 §18](../plans/0023-m6-research-investigations.md#18-completion-evidence).
The frozen `CANDIDATE_GRAMMAR_V1` and `RESEARCH_ENVELOPE_V1` seeds own the supported
operators, domains and complexity limits; B2 changes neither definition/hash.

A declaration contains exactly `grammar_id`, `symbols`, `timeframe`, `entry`,
`exit`, `warmup_bars`. `entry` is a list of AND condition lists joined by OR.
`exit` contains exactly `atr_period`, `stop_multiple`, `max_hold_hours`, `signal`;
`signal` is the same group shape or null. Each condition contains exactly `left`,
`op`, `right`. Features contain `operator` and `period` (null only for CLOSE).
The right operand contains `feature` and `constant`, exactly one non-null.
Constants and stop multiples are decimal strings, never binary floats.
Unknown fields, arbitrary code/SQL, recursive expressions, duplicate JSON keys,
nonfinite numbers, out-of-domain values and excess complexity are rejected.
The existing 16-KiB final-output transport bound also bounds a declaration.

Normalization orders symbols by the fixed engine priority, sorts/deduplicates
identical conditions and groups, and removes decimal trailing zeros and negative
zero. Raw group/condition counts are checked before deduplication. The normalized
declaration's full SHA-256 is its candidate identity (and the 64-character
research strategy ID); the separately hashed execution definition binds this
declaration and the frozen grammar/envelope hashes. Boolean reorderings and
duplicate predicates normalize identically; no general algebraic-equivalence
solver is claimed. Protection's ATR counts toward the eight distinct features.

All windows are trailing, include the current finalized bar and restart with
the contiguous hourly run. EMA uses the reference's SMA seed and ATR its existing
prior-close/Wilder recurrence. SMA is the arithmetic mean of n closes;
RETURN(n) is `close[t] / close[t-n] - 1`; HIGHEST/LOWEST are the maximum high and
minimum low over n bars; ZSCORE is `(close - mean) / sqrt(population variance)`
of n closes. Zero variance and an unusable return denominator are unavailable.
Arithmetic uses the engine's Decimal context (96 digits, half-even), without
intermediate monetary quantization. A missing current operand or required
crossing predecessor yields WARMUP_INCOMPLETE, even after declared warm-up.
Crossings use inclusive previous comparisons and strict current comparisons.
If entry and exit both match, the exit signal takes precedence.

The native adapter delegates to the unchanged reference functions and preserves
its feature shape, identity and mandate texts. Candidate evaluation supplies
`close`, `atr` and the engine-added `stop` for existing sizing. Candidate mandates
store `CANDIDATE_ENTRY_V1` and `CANDIDATE_SIGNAL_EXIT_V1` (or NONE), resolving the
actual rules through their immutable strategy ID/hash; manifests and evaluation
reports also carry the actual declaration. The existing TREND_EXIT reason owns
candidate signal exits. Stops, time protection, risk, order mechanics, rounding
and accounting remain the existing engine path.

Installation and engine startup require both explicit replay isolation and the
actual `asl_m1_replay_` database matching the environment. The candidate adapter
is refused for MAIN, OFFLINE_TEST and live market views. Forward manifests keep
their fixed strategy slot and exact-hash approvals; only HISTORICAL_RESEARCH
can select a validated candidate. Historical manifests/reports name the reduced
recorded-quote eligibility rule. No B2 tool exposes trading or approval authority.

Research breakout and mean-reversion candidates as separately documented hypotheses. Each needs exact entry/exit rules, feature definitions, costs, parameter search space, invalidation conditions and tests before becoming runnable. No free-text “use mean reversion” action is valid.

A 4h variant is a separate approved strategy version, not an ad hoc response to a losing 1h position. Multiple strategies can run in shadow accounts with separate balances. The main account uses one approved owner per symbol; portfolio exposure is checked globally.

## Position mandates and adaptation

A position retains strategy ID/version, original entry reason, entry evidence, stop policy, time horizon and exit rules. Later selector/parameter changes apply only to future entries unless the original approved mandate explicitly included a rule. Do not reclassify a failed short-term trade as a long-term holding.

Every accepted/rejected signal records its input snapshot, availability time, rules evaluated and reason. Explanations should be concise, reproducible evidence—not hidden reasoning transcripts or uncalibrated claims of certainty.

## Promotion record

Use [STRATEGY_PROPOSAL.md](../templates/STRATEGY_PROPOSAL.md). Require correctness checks, point-in-time data, full trial history, cost sensitivity, forward shadow evidence, risk/operational checks, and the exact owner-approved scope. Strategy suspension for integrity/risk failure can be automatic; reapproval cannot be automatic.

## AGENT_POLICY_V1 template — to complete before M7 activation

This is a proposed policy identifier, not an implemented or tested strategy. Unlike TREND_REFERENCE_V1 it does not require an EMA crossover to enter. It must declare:

| Contract | Required content |
|---|---|
| Inputs | Approved numerical features/evidence sources; availability/freshness predicates; missing/conflicting evidence behavior |
| Model process | Role prompt/schema/model versions, tool catalog, bounded workflow and reviewer requirements |
| Action domain | ENTER/HOLD/ABSTAIN/REDUCE/EXIT/CANCEL_ENTRY/TIGHTEN_STOP within the tool contract |
| Entry intent | Evidence-linked thesis, invalidation, approved horizon, requested target/spend bound, protective mandate and execution envelope |
| Exit management | Deterministic stop/time protection, whether discretionary early exits and monotonic stop tightening are allowed; never loosen/extend |
| Adaptation | Permitted strategy/parameter domains and trigger rules; versioned records and owner gates for expansion |
| Tests and reporting | Recorded decision/tool fixtures, adversarial and concurrency cases, matched baselines, model/latency cost and forward-evidence protocol |

The initial protection-template geometry, maximum-hold choices, discretionary turnover/cooldown settings and action validity/deviation thresholds require explicit declared values and owner approval before this policy runs. Reuse a previously approved template only by referencing its exact version. Do not silently copy reference-strategy seeds and claim they are optimal for agent decisions.

Hard caps are unchanged and remain in [RISK_POLICY.md](RISK_POLICY.md). An agent can choose an eligible trade within that envelope; deterministic sizing need not mean deterministic selection. Routine authorized paper trades do not require human approval. An LLM's unsupported number, novelty claim or confident narrative cannot create a new feature, fee, stop mandate or strategy approval.

### AGENT_POLICY_V1 as built (ExecPlan 0026 B2, PROPOSED)

The document is `AGENT_POLICY_V1` in `services/engine/app/execution/definitions.py`; `app/policy/document.py` checks and parses it, and code reads every value from it. A field that states a rule the code implements (the failure rule, the review an entry needs, the entry evidence and others) can only restate V1's rule: a version with another rule comes with the code for it. It holds the values of [ExecPlan 0026 §5.2 and §5.7](../plans/0026-m7-agent-driven-main-decisions.md#52-agent_policy_v1-values-proposed-engineering-defaults-no-measurement-stands-behind-them) as written: PROPOSED engineering defaults with no measurement behind them. Its action domain has no `REDUCE` (M7-OD7). It reports under `EVALUATION_PROTOCOL_V2` and `BASELINE_SET_V1`.

- **Not installed and not approved.** The six hashes of the generation-3 agent definitions it is valid with are empty until ExecPlan 0026 B5 builds those definitions. Until then the install command refuses it, so no database outside a test holds it. Setting them changes its hash; that is still version 1, because no build before B5 can install it.
- **What B2 builds around it:** an agent-driven draft names it and its protocol in the manifest's slots and waits for the owner's exact-hash approvals as every draft does; the engine binds to it at the lease and evaluates no bars. Intents are B3's. Details: [ExecPlan 0026 §18, B2](../plans/0026-m7-agent-driven-main-decisions.md#b2--the-policy-documents-the-manifests-slots-and-the-engines-binding-2026-10-11).
- **The single-coordinator variant `AGENT_POLICY_V1_SOLO` (B6b, 2026-10-12; fixture only).** §5.11's variant for comparisons: V1's document with its own identity, labels and two rule words, that an entry has no market brief (`entry_evidence.assessment`, `entry_evidence.enforced`) and no intent review (`review.entry`); every value is V1's. The parser accepts it only as `FIXTURE_ONLY`, at its version, with those words, which the database admits on a disposable database only; the install command does not install it, a draft refuses it (`FIXTURE_STRATEGY_REFUSED`) and the engine refuses its start for the main account (`FIXTURE_STRATEGY_REFUSED_FOR_MAIN`). No agent workflow runs it: in B6b's fixture a script writes its intents, and the dispatcher and the database guards still ask every agent's entry for its review. Hash `cff95a275ce397c8ae6feb425f3ae3b51e63cfb88f7018944ac1708aeb5542b0`; V1's is unchanged. Details: [EVALUATION](../EVALUATION.md#m7-evaluation-protocol-v2-approved-contract-execplan-0026).

### AGENT_POLICY_V2: hourly entry checks (M8 update 3, PROPOSED)

The owner's pick "First in M8" ([DECISIONS, 2026-10-18](../../DECISIONS.md#2026-10-18--m8-starts-with-hourly-entry-checks-when-the-app-holds-no-position)), built as the first version change of [ExecPlan 0031 §9](../plans/0031-m8-simple-app-that-runs-itself.md#9-implementation-sequence). The document is `AGENT_POLICY_V2` in `services/engine/app/execution/definitions.py`, hash `28182ce16d0ccfa70032bf3de74cd86cee9d0c7279d17bb03211147ac2ee55db`. It is V1's document with one change: `cadence.decision_after` names `BAR_CLOSE_EVERY_FINALIZED_HOUR` in place of `BAR_CLOSE_WHILE_A_POSITION_OR_AN_ENTRY_IS_OPEN`, so a decision runs at every finalized hourly bar whether or not the account holds a position or an entry. Its identity, version, source and label are its own; every limit (2 accepted entries in 24 hours, 1 per coin, 6 submissions, notional at most 0.75 x equity), every rule word and the generation-3 agent definitions it binds are V1's. A document may name at most one of the two bar triggers. V1 is unchanged and stays in the build, because its run and its positions name it.
- **Installed by the update:** migration `0012` stores it (through `asl_m7_install_definition`, as the install command stores V1), the agent worker records it in force as `SYSTEM`, and the app moves the main run to it ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-the-main-run-the-app-keeps-going-execplan-0031)).
- **Cost, not measured:** up to 24 decisions on a day with no position instead of 4, inside the daily budget of 36 decisions that V1 already set; every one shares the owner's ChatGPT usage allowance.
- **Not changed:** the rule words that name the owner's approval (`model`, `adaptation`) are V1's, because a rule word can only restate V1's rule; from M8 the app's in-force record stands where they say approval ([AUTONOMY_MATRIX](AUTONOMY_MATRIX.md#m8-the-app-runs-itself-execplan-0031)). The agent's entry pause keeps update 2's fixed 24-hour end. A promotion's scope stays `ENTRY_BASIS_UNDER_AGENT_POLICY_V1`, so under V2 an entry takes a reviewed brief as its basis, not a promoted candidate (both are tool texts hashed into generation 3).
- **Under M9 ([ExecPlan 0032 §5.2](../plans/0032-m9-news-and-events-the-agents-trade-on.md#52-the-agents-and-agent_policy_v3-update-2)):** no `AGENT_POLICY_V3` was built. V2 stays in force, because it binds generation 3's hashes and update 2 leaves them unchanged. A decision also starts between hourly bars when an investigation of a feed item or a price move (generation 4) passes its review (`REVIEWED_ASSESSMENT` in `decision_after`), and that assessment can be an entry's basis, as M6's could. Every limit is V2's.

### AGENT_POLICY_V3: five coins (M10 update 2, PROPOSED)

The owner's "Research and trade" ([DECISIONS, 2026-10-20](../../DECISIONS.md#2026-10-20--m10-approved-research-and-trade)) and "go" ([2026-10-21](../../DECISIONS.md#2026-10-21--m10-update-2-zec-near-and-xrp-traded-on-paper-execplan-0033)), built as update 2 of [ExecPlan 0033](../plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#52-update-2-three-more-coins-on-paper-only-with-the-owners-yes). The document is `AGENT_POLICY_V3` in `services/engine/app/execution/definitions.py`, hash `0aaaac5a5878020d0611c38791f3ddde663874638ae16c25b0c2133c2e72406c`. It is V2's document with the coins ZEC, NEAR and XRP: only its identity, version, source, label, `universe` and `symbol_priority` (BTC, SOL, ZEC, NEAR, XRP) and the agent definitions it binds (generation 6, [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m10-runtime-generation-6-and-five-coins-execplan-0033)) differ. Every limit and rule word is V2's and covers the five coins together: 2 accepted entries in 24 hours and 1 per coin, 6 submissions, notional at most 0.75 x equity, and the risk policy's portfolio totals (total notional 0.50 of equity, aggregate stop risk 0.005, 25 % per asset). More coins add no room; a position in a new coin uses the same totals as one in BTC.
- **Installed by the update:** migration `0016` stores it `PROPOSED`, as `0012` stored V2; the agent worker records it in force as `SYSTEM`, and the app moves the main run to it once the account is flat ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-the-main-run-the-app-keeps-going-execplan-0031)). V1 and V2 stay in the build, because their runs and positions name them.
- **Counted together:** V1, V2 and V3 share the 24-hour notional window and the wait after a protective stop, so moving to V3 resets neither (`app.execution.intents.counted_with`). Entry counts already counted the whole mode.
- **Entry basis:** a reviewed brief that covers the coin, or an approved candidate, as under V2. A coin note is never one.
- **Costs:** fills in the new coins are modeled with the same cost scenario as BTC and SOL; no measurement of these coins' fees or slippage stands behind them.

## TREND_REFERENCE_V1 execution settings (M3, PROPOSED)

IMPLEMENTED in `app/strategies` and the execution engine; hashed as `TREND_REFERENCE_V1` (status `PROPOSED`, not owner-approved). Details: [ExecPlan 0011 §5.9](../plans/0011-paper-broker-reference.md#59-trend_reference_v1).

- Indicators run over the maximal contiguous run of visible, valid finalized bars (at most 720 bars); an unresolved candle conflict or missing hour breaks the run and restarts warm-up. Arithmetic is Decimal (precision 96, half-even) without intermediate quantization.
- **Checkpoint:** symbols are evaluated in priority order (`BTCUSDT`, then `SOLUSDT`); a lower-priority symbol waits for the higher one's bar-H final or `H_close + 60 s`. Trend exits are processed before entries.
- **Validity:** an entry may be decided until `bar close + 600 s`; a bar visible later (for example a REST backfill) is used for indicators only and its signal is recorded `MISSED` (`LATE_BAR`). Downtime is never hidden: at most the last 168 unevaluated bars are evaluated on catch-up and any lapsed signal is `MISSED`.
- **Time exit wording:** the exit obligation is created at the first eligible step at or after `first fill + 72 h`; the actual holding time is reported and may slightly exceed 72 h.
- The stop is `signal close − 2 × ATR14` at full precision; it is a planned engine trigger on the best bid, not a guaranteed exit price.

## TREND_REFERENCE_V1 in the M4 pilot (ExecPlan 0015)

A forward run evaluates only bars that close after its activation; earlier bars feed the indicators only, and the worker does not scan earlier history. Entry signals while the run is paused are rejected (`POLICY_PAUSED`), and while it is stopping `RUN_STOPPING`; trend exits and protective exits of open positions continue. The strategy is an untested control seed, not a profitability claim.

## Warm-up sensitivity (PROPOSED for M8, 2026-10-17)

**PROPOSED under the [owner's instruction](../../DECISIONS.md#2026-10-17--builder-and-llm-trading-findings-recorded-as-proposed-m8m10-requirements); it changes neither `TREND_REFERENCE_V1` nor `CANDIDATE_GRAMMAR_V1` nor `RESEARCH_ENVELOPE_V1`.** Indicators restart with each contiguous run. After an hour that stays missing or unresolved, the reference's EMA(50) at its 100-bar warm-up still carries 13.5% of its seed (a calculation, not a measured effect). A candidate may declare a warm-up as short as its longest feature period, and research datasets start at most 302 h before their first decision. Gaps the provider can fill are repaired by the worker's hourly backfill, whose bars already feed indicators under V1. Early M8 measures the effect on real candles ([EVALUATION](../EVALUATION.md#indicator-warm-up-sensitivity)). If it is material, the remedies are successors, each approved by exact hash:

- a `TREND_REFERENCE_V2` with a longer minimum warm-up;
- a higher candidate warm-up floor with a longer research data prefix, in a new grammar/envelope version.

V1, its approvals, mandates and history stay as they are, and the rule above that a warm-up length is a declared engineering choice, not evidence of convergence, still applies.
