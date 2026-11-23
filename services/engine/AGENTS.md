# Engine instructions

Read root instructions and the relevant contracts in `docs/`. Use explicit domain types, exact Decimal/NUMERIC accounting, immutable versions, transaction boundaries, idempotency, outbox events and reconciliation. One fenced execution authority controls the account.

Only the accounting service posts the ledger. Validate the owner's requests against current state inside the authoritative transaction. Market, cost, position and risk provenance is mandatory. No signed/private exchange calls, live adapter or real exchange credentials are permitted.

Test accounting invariants, top-up NAV neutrality, rounding, concurrency, partial fills, stale data, missed observations and crash recovery. No startup reseeding or deletion of losing runs. Nothing disables the protection of what is held, and unavailable prices cannot produce invented fills.

Use current official documentation and installed dependency APIs. Keep API/worker lifecycle separate but share one engine codebase and one Alembic migration owner. Record actual commands/results and remaining limitations.

Since ExecPlan 0060 the engine runs no model and no research: the rule (`app.spot.rule`) is code, and every trade goes through the one step's risk, fill and ledger path with current-state validation ([autonomy](../../docs/AUTONOMY_MATRIX.md)). Preserve the protection of what is held independently of every other workload, the backtest included.
