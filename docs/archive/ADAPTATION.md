# Bounded adaptation and agent-driven trading

## Objective and authority

Test whether adaptive/agent-driven decisions improve after-cost capital growth under the fixed hard policy. Adaptation is itself a versioned decision policy. No promise of correct regime detection, stable income or profitable forecasts is part of the product.

The risk controller owns hard limits; the coordinator proposes decisions; research explores without main authority; the evaluator challenges evidence but cannot approve financial exceptions. [AUTONOMY_MATRIX.md](../AUTONOMY_MATRIX.md) governs permission changes. [STRATEGIES.md](../STRATEGIES.md) governs policy/position definitions.

## Three policy kinds

| Kind | Decision authority | Role in experiments |
|---|---|---|
| `FIXED` | Exact predeclared executable strategy rules | Financial reference and baseline |
| `ADAPTIVE_SELECTOR` | Approved deterministic or AI-assisted selection among eligible strategy versions | Tests bounded strategy selection separately |
| `AGENT_DRIVEN` | Coordinator chooses permitted trade/position intents from available evidence and research under an approved discretionary policy | Full agent workflow; does not require the EMA reference entry rule |

Do not mix these kinds inside a headline performance result without explicit version/segment attribution. Only one approved execution policy owns the main account at a time; per-symbol positions have immutable ownership.

## AGENT_DRIVEN operating envelope

The approved policy declares model/prompt/tool versions, admissible evidence/features, allowed symbols, horizons, decision triggers, objective, candidate/parameter domains, minimum evidence predicates, reviewer policy, entry/exit management templates, target-exposure interpretation, action/turnover/work budgets, missing-data/failure behavior and evaluation protocol. Hard numbers are linked from risk policy, not copied into prompts as editable authority.

Within this envelope agents can investigate, select permitted next steps, buy/hold/reduce/exit or abstain, and propose supported allocation targets. Code sizes and checks every action. The model may formulate its own thesis without a hand-coded technical entry signal, but cannot bypass hard constraints or turn a free-text rationale into a new approved domain.

The pilot permits finalized 1h decision triggers and approved source/position events; hours-to-days remains the intended horizon. An approved 4h policy is separate. A model can choose only an approved horizon, not extend an open trade because it lost money. Initial action-management and trigger thresholds must be declared before activation; no optimal values are fabricated.

## ADAPTIVE_SELECTOR retained baseline

1. Run eligible strategy versions in isolated shadow accounts with identical admissible observations, cost model and external-flow schedule.
2. At the approved checkpoint (daily UTC for the initial selector baseline), calculate declared rolling/expanding performance and quality features using only earlier available information.
3. Remove candidates that fail integrity, freshness, risk, sample or promotion predicates; include `FLAT`.
4. Use a frozen rule covering after-cost performance, drawdown, exposure, turnover, switching costs and uncertainty. Define tie-breaks, tenure and minimum advantage using development data only.
5. AI-assisted selection may choose eligible IDs or abstain; a deterministic selector with explicitly implemented formulas provides the non-LLM comparison.
6. Changes apply only to new entries. Existing positions retain their approved management mandate.

Selector windows, thresholds, uncertainty method, penalties/tenure and evidence sample rules remain unset until calibration and approval at M7. They are not needed to scaffold M0 or to test a fixed reference. No vague “pick the best” selector can be activated.

## Permitted automatic changes

Allow abstention, reduced requested exposure, selection among approved strategy/parameter/horizon alternatives, and management actions explicitly authorized in an existing position mandate. Record before/after version, evidence cutoff, reason, expected impact, and actual result. Temporary discretionary reductions cannot exceed hard caps when restored and must follow the policy's predeclared action rules.

New strategy families, wider parameter domains, new model/prompt decision policies, changed source/tool authority, higher risk ceilings or revised experiment-success criteria require approval. The system must not repeatedly rebrand a new candidate as an existing strategy to bypass the gate. Isolated research under its approved envelope can run automatically before any main-promotion request.

## Position management

Each filled position records entry policy/model/strategy, evidence, stop definition, maximum-hold deadline, permitted early reductions/exits and permitted stop tightening. The original contract is immutable. Current stop state may move only under its predeclared monotonic rule; changes are appended with version checks. No stop loosening, protection cancellation, mandate replacement or holding-period extension. A partial fill/reduction remains protected. Account-level pause/revocation does not erase position obligations.

Code determines quantity from current equity, approved risk/cost envelope, requested upper bounds, liquidity and filters. One owner per symbol; no overlapping conflicting positions or averaging down in the pilot. Agent confidence is not a calibrated probability and cannot determine unbounded size.

## Event-driven work and budgets

Full agent workflows are not limited to the selector baseline's daily checkpoint. Approved finalized-bar, source revision, fill/position and periodic review events may trigger reassessment. The durable scheduler deduplicates/coalesces events, applies priority and code-owned cooldowns, limits recursive work and expires obsolete snapshots. Research cannot monopolize the runner or financial worker.

The agent may request relevant research or permitted reassessment, not schedule infinite self-calls. A material event needs a registered source and declared detection rule; an LLM declaring “urgent” is not priority authority. The exact cadence, event thresholds and workflow budgets are run configuration, not an inferred best trading frequency.

## Failure, evaluation and rollback

Unavailable model/reviewer/required source means no new dependent exposure. Deterministic protection continues when the running engine has valid market observations. A separately approved non-AI fallback is its own evaluated policy; no silent fallback to yesterday's best strategy.

Suspension for a hard-policy or integrity failure can be automatic; clearing a latched pause requires owner review. Restoring an approved version cannot rewrite earlier losses, filled positions or trial history. Compare fixed, deterministic adaptive, single-role agent and full multi-role policies on matched data/costs/flows. Include operational costs, latency, model failures, turnover and uncertainty; multiple roles must earn their complexity through evidence.

Runtime research produces declarative candidates/artifacts. Generated executable code uses isolated reviewed authoring, not self-modifying production jobs. See [RESEARCH_WORKFLOWS.md](RESEARCH_WORKFLOWS.md) and [EVALUATION.md](EVALUATION.md).
