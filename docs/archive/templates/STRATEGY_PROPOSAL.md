# Strategy / selector change proposal

Status: DRAFT — no approval or result is implied by this template.

## Identity and scope

Record proposal ID, author, timestamp, existing/new version, code/parameter hash, affected symbols/horizons, and whether this is new logic, a bounded parameter selection, an expanded range, or a selector policy change.

## Hypothesis and exact rules

State the testable hypothesis without promising returns. Define every feature, available-at constraint, warm-up, signal, position sizing input, exit/maximum-hold mandate and failure/abstention rule. List exact parameter domains and explain their provenance as design choices or measured calibration outcomes.

## Data and execution assumptions

Identify datasets/sources/time windows/quality limits, cost model, latency/fill fidelity, benchmark policy, point-in-time risks and historical LLM contamination. Unknown values stay explicitly unknown.

## Tests and evaluation

List invariants, indicator/strategy fixtures, concurrency/risk implications and actual test results. Record chronological splits, every attempted variation, untouched/forward segments, uncertainty method, matched baseline/AI ablation and cost sensitivity. Distinguish proposed tests from executed checks.

## Change authority and deployment

Explain the effect on new entries and prove existing positions retain their original mandate. Record hard-risk invariants, rollback/suspension conditions, required shadow phase and exact owner approval. A generated proposal is not approval. Attach a version-bound approval only after it actually occurs.

## Decision

Outcome: pending, rejected, shadow-only, or approved-for-stated-scope. Record evidence, limitations, owner identity/time and the immutable approved hash. Keep rejected versions in the experiment history.

## Agent-policy and research extension

For agent-driven policies, record model/provider, role-prompt hashes, tool schemas/grants, evidence sources, trigger/debounce/expiry rules, allowed actions, reviewer binding, discretionary turnover/re-entry controls, stop/hold mandate and failure behavior. Separate testable hypotheses from uncalibrated model confidence.

Identify the approved ResearchEnvelopeVersion authorizing isolated work and, separately, the owner authorization needed for the main portfolio. A bounded parameter choice can inherit eligibility only from an already approved main policy domain with exact membership and predeclared promotion checks. New logic or wider domains never inherit authority merely by reusing a strategy name. Describe all trial attempts, holdout access and proposed comparisons.
