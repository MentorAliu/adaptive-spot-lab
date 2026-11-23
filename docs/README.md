# Documentation map

Read root [AGENTS.md](../AGENTS.md), [STATUS.md](STATUS.md) and the current task or ExecPlan, then only the contracts the task touches. Before editing a subtree, read its local `AGENTS.md`. Do not load every document into every task.

## Authority and duplication

PROJECT owns product IDs; AUTONOMY_MATRIX owns permissions and what is in force; RISK_POLICY owns financial limits and the rule's definitions; TRADING owns trading judgment; DATA_CONTRACTS owns shared records; ROADMAP owns milestones. A material contradiction blocks the affected work; it is never permission to pick the least restrictive paragraph. Since [ExecPlan 0060](plans/0060-spot-trading-only.md) the app runs no model: the agents' runner, prompts and contracts are removed or archived.

## Current contracts

**Scope and authority**
- [PROJECT](PROJECT.md): the product, its fixed requirements and IDs.
- [DECISIONS](DECISIONS.md): the owner's decisions, newest first.
- [ROADMAP](ROADMAP.md): milestones M0 to M12 and their gates.
- [AUTONOMY_MATRIX](AUTONOMY_MATRIX.md): who may do what, and how a definition comes into force.
- [RISK_POLICY](RISK_POLICY.md): every financial limit.
- [SECURITY](SECURITY.md): trust boundaries and secrets.
- [ARCHITECTURE](ARCHITECTURE.md): services and how they connect.

**Trading**
- [TRADING](TRADING.md): the trading knowledge Claude holds as the project's systematic trader: the principles with their evidence, the yardsticks in force, the record so far and how to judge a trading change (the `trading-review` skill).
- [STRATEGIES](STRATEGIES.md): the rule in force and the earlier strategies.

**Money, data and APIs**
- [LEDGER](LEDGER.md): the ledger and virtual funding.
- [PAPER_EXECUTION](PAPER_EXECUTION.md): the paper broker and its fill model.
- [MARKET_DATA](MARKET_DATA.md): market data collection and its rules.
- [DATA_CONTRACTS](DATA_CONTRACTS.md): shared records and provenance.
- [API_CONTRACTS](API_CONTRACTS.md): the private API's routes and its live stream.

**Frontend**
- [FRONTEND](FRONTEND.md): the four pages and user experience.
- [SHADCN_WORKFLOW](SHADCN_WORKFLOW.md): the mandatory shadcn and chart skill workflow.
- [LIBRARIES](LIBRARIES.md): library policy and versions.

**Running and verifying**
- [OPERATIONS](OPERATIONS.md): the update file, the Docker clean-up, scheduling and recovery.
- [DOCKER](DOCKER.md): the local Docker deployment and clean-up rules.
- [CONFIGURATION](CONFIGURATION.md): settings and activation.
- [COMMANDS](COMMANDS.md): the verified commands in use now.
- [TESTING](TESTING.md): how tests run, and the requirement-to-test map.
- [ACCEPTANCE_CHECKLIST](ACCEPTANCE_CHECKLIST.md): the acceptance checklist and the Q01 to Q10 quality gates.
- [INTEGRATION_EVIDENCE](INTEGRATION_EVIDENCE.md): what was verified against each library and provider.
- [REFERENCES](REFERENCES.md): the official sources.
- [PLANS](PLANS.md): how to write an ExecPlan.

## Active plans

- [ExecPlan 0060](plans/0060-spot-trading-only.md) (`APPROVED` 2026-11-12, M12): spot trading only: the main account holds USDT and BTC and buys and sells Bitcoin spot by the slow rule, long or cash, at 0059's 5% volatility target, trading the difference once a day; the app backtests the same rule on Bitcoin's whole spot history by itself; the futures account, the perpetual's feed, the AI agents and everything the futures app had switched off are removed, their records archived in the database. Installed on 2026-11-12, with the fix of its daily history ([STATUS](STATUS.md)).
- [ExecPlan 0061](plans/0061-clean-up-after-the-spot-switch.md) (`APPROVED` 2026-11-12, part of M12): clean up after the spot switch: the leftovers of the futures, the agents and the research removed from the code, the tools and the documents (their history moved to the archive), the update file's quiet time cut to 23:55 to 00:10 UTC, and the Cockpit's run against holding Bitcoin.

The finished plans 0001 to 0059 are in [archive/plans/](archive/plans); [ExecPlan 0059](archive/plans/0059-the-slow-rule-trades-the-main-account.md) holds the slow rule's research and [ExecPlan 0039](archive/plans/0039-bitcoin-futures-on-paper.md) M11's futures.

## Ideas and templates

- [ideas/](ideas): the owner's ideas, not scheduled; nothing in them is decided ([the slow trend twin's follow-ups](ideas/slow-trend-follow-ups.md); [three strategies checked on 2026-11-10](ideas/strategies-checked-2026-11-10.md), [eight on 2026-11-13](ideas/strategies-checked-2026-11-13.md) and [a sideways-market mode on 2026-11-17](ideas/strategies-checked-2026-11-17.md), none passing).
- [templates/](templates): [feature task](templates/FEATURE_TASK.md).

## History

[archive/](archive/README.md) holds the finished plans, run records, the status history, the original pack files, the AI's contracts retired by ExecPlan 0060 and the contracts as they stood before ExecPlan 0061 rewrote them to the spot app, verbatim. Search it for what you need; never read it whole at the start of a task.
