# Test instructions

Read root instructions and [verification requirements](../docs/TESTING.md). Use isolated data and databases (`asl_m1_` with `ASL_TEST_ISOLATED=1`) and clearly labeled fixtures. Do not contact private exchanges, paid models or the owner's running app in routine tests. No test may erase the main paper ledger or pretend a synthetic book or candle is a live observation.

Financial tests cover exact arithmetic, per-asset balance, top-up NAV neutrality, idempotency, concurrency and fencing, and restart reconciliation. Rule tests compare the reading with independently calculated fixtures and check that nothing reads data before it was final. UI tests that need browser or SSR behaviour run a real compatible browser against the relevant services.

Record actual commands, results and checks not run. Never rewrite a test merely to accept an implementation that violates the risk, accounting or source contracts. No correctness test is a claim of trading profitability. Use the [acceptance checklist](../docs/ACCEPTANCE_CHECKLIST.md) and never mark a scenario passed without actual evidence.
