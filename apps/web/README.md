# Adaptive Spot Lab web app

The TanStack Start app the owner opens at <http://localhost:3000>: four pages (Cockpit, Trades, Backtest and Settings) over the spot account that buys and sells Bitcoin by `SPOT_RULE_V1` ([ExecPlan 0060](../../docs/plans/0060-spot-trading-only.md)). Its server functions call the private engine's API with the service key; the browser never sees the key and never sets a balance, a price or a fill.

- What each page shows and how: [FRONTEND](../../docs/FRONTEND.md).
- How to build, test and check it: [COMMANDS](../../docs/COMMANDS.md#web-cloud).
- Before a UI change, read [AGENTS.md](AGENTS.md) and the [shadcn workflow](../../docs/SHADCN_WORKFLOW.md).
