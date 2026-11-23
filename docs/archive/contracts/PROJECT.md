# Product contract

## Goal and audience

Create a single-owner local research application that tests whether agent-driven BTC/SOL spot trading improves capital growth after costs, under an approved risk policy. The objective includes possible income generation, but no return target, fixed payout, success probability or guaranteed loss ceiling has been established.

## Release scope

Use real public Binance observations and an internal paper broker. Initialize 10,000 virtual USDT exactly once and support explicit virtual top-ups. USDT is a disclosed interpretation of the owner's informal dollar notation, not an assumed USD conversion. Show `USDT (virtual)`; real USD conversion and withdrawals/distributions are deferred.

Provide an operational terminal covering market observations, funding, positions/orders/fills, evidence, agent workflows, hypotheses, research experiments, proposals/approvals, performance and health. The approved main-paper policy may operate without approval for each routine trade. Owner approval is still required for new strategies or wider parameter domains in the main portfolio and any expansion of authority.

## End-to-end agent capability

The required workflow is: detect an eligible event; inspect approved evidence; formulate or reassess a thesis; request permitted research; obtain a critique when policy requires; propose buy/hold/reduce/exit or abstain; pass server-side permission/risk checks; simulate execution; reconcile outcomes; review performance; adapt within the approved domain. The decision policy can be discretionary and model-driven, not merely selection of a prewritten indicator strategy.

Four logical roles use the tools in [AGENT_TOOL_CONTRACTS.md](../AGENT_TOOL_CONTRACTS.md). No role directly spends funds. The application orchestrates bounded steps and owns all side effects. Per-role permissions, human approval and prohibition rules are in [AUTONOMY_MATRIX.md](AUTONOMY_MATRIX.md). The runtime is fully useful only when research, decision, execution and feedback requirements have been implemented and tested; M0 is not that state.

## Requirements

| ID | Requirement | Primary acceptance evidence |
|---|---|---|
| P01 | Paper-only, no exchange account access | Static capability and denied-request tests |
| P02 | Spot, long-only, for BTC, SOL and the coins the installed operating policy names; from M11's second update, one simulated BTCUSDT perpetual, long or short, at most 2x ([DECISIONS](../../DECISIONS.md#2026-10-23--m11-approved-bitcoin-futures-on-paper-execplan-0039)) | Universe, quantity, direction and leverage checks |
| P03 | One-time funding and idempotent top-ups | Ledger and NAV neutrality tests |
| P04 | Independent hard risk | Boundary/concurrency/fencing/policy tests |
| P05 | Faithful paper execution and accounting | Recorded replay, fill and reconciliation checks |
| P06 | Verifiable data and evidence lineage | Availability, gap, revision and provenance tests |
| P07 | Bounded strategy/horizon adaptation | Domain, promotion and position-mandate checks |
| P08 | Measured incremental AI value | Fixed, selector, single-agent and multi-role comparisons |
| P09 | Exact frontend/skills/preset requirements | Official integration and real-browser evidence |
| P10 | Local Docker operation and recovery | Clean build/start, resource isolation and restore |
| P11 | Subscription Codex runtime | Authorized login, capability preflight and failure tests |
| P12 | Honest performance | Flow-neutral returns, all-trial history and cost labels |
| P13 | Multi-step role-scoped agent tools | Bounded tool/action loops and authenticated dispatch |
| P14 | Event-driven evidence investigation | Approved-source fetch, deduplication, cooldown and provenance |
| P15 | Autonomous isolated research | Preauthorized experiment requests, budgets and quarantined outputs |
| P16 | Agent-driven trade/position decisions | Approved-policy intents, no per-trade owner prompt, independent risk gate |
| P17 | Durable role coordination and memory | Typed artifacts, server-owned role identity, restart/replay |
| P18 | Permission revocation and human approval | Exact-hash approvals, cascading cancellation and no escalation |
| P19 | Agent observability and controls | Role/tool/decision/evidence timelines, queue and authority UI |
| P20 | Adversarial and resource resilience | Injection, repeated actions, stale plans, starvation and leakage tests |

[ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md) maps these requirements to concrete scenarios. Empty checkboxes are not completed tests.

## Exclusions and preserved boundaries

No stocks, derivatives, margin, shorting, leverage, staking, real deposits/withdrawals, exchange credentials, Testnet/Demo, public multi-user product, remote hosting, external notifications or paid API fallback. No unrestricted browsing/shell tools, automatic plugin installation, agents modifying production code, or self-approved new main strategies. Automatic research supports only a registered declarative experiment language with bounded resources; new executable code uses the reviewed authoring workflow.

A future live Binance adapter is a separately reviewed project, not a switch implemented now. Interfaces may be portable without containing live capability.

## Product success and research success

Operational correctness and trading advantage are separate. A faithful experiment may lose money or find no AI benefit. A profitable curve with unknown fills or cherry-picked trials is not successful validation. No requirement is satisfied merely by increasing agent count. Use [EVALUATION.md](../EVALUATION.md) and [ROADMAP.md](../../ROADMAP.md).
