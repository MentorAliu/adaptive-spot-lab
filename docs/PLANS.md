# Execution plan standard

Use a scoped ExecPlan for a multi-file feature, new dependency/integration, migration, risk/accounting change, or consequential refactor. A plan is a living implementation record, not a replacement for tests.

Each plan must contain: goal and observable outcome; current repository facts; scope and exclusions; requirements mapped to tests; official source/version evidence; data and trust-boundary changes; proposed file edits; implementation sequence; verification commands; failure/rollback plan; progress; decision log; and completion evidence.

Milestone plans must assess the [Q01–Q10 quality gates](ACCEPTANCE_CHECKLIST.md#quality-gates-for-every-milestone), recording applicability, concrete acceptance conditions and planned evidence. Small scoped changes cover affected gates only. At completion, resolve each assessed gate to a result with evidence or a specific missing check; preserve open requirements when a broader readiness claim is unsupported.

Separate `PROPOSED`, `OBSERVED`, `IMPLEMENTED`, and `VERIFIED`. Do not invent command results. Where a command is not yet implemented, say so and include implementing it in the work.

Keep plans short: the decisions, the design and the tests, each result recorded once; [DECISIONS.md](DECISIONS.md) takes only the owner's choices ([ExecPlan 0031](archive/plans/0031-m8-simple-app-that-runs-itself.md)). Plan only the approved milestone in detail. Ask about a genuinely blocking owner decision only when it cannot be resolved from [DECISIONS.md](DECISIONS.md). Do not reopen answered questions or defer ordinary reversible engineering decisions to the owner.

UI plans require the official shadcn skill, registry lookup evidence, actual preset configuration, and browser validation. Financial plans require invariants, concurrency/failure cases, and replay evidence. Model plans require output schema, authority boundaries, quota behavior and explicit external-data permissions.

At completion, record observed test output, residual limitations, and the next task. No automatic transition from a research milestone into live trading is permitted.

Every M-numbered implementation plan must include [normal local deployment](OPERATIONS.md#milestone-completion-deployment) as a completion step: protected backup, forward migration when needed, verified running release, health/browser check and retained operating controls. Record the running source/image identity and URL separately from the implementation commit and isolated test results. An older normal app left running means delivery is incomplete even when implementation/acceptance passed. The [standing owner decision](DECISIONS.md#2026-09-28--completed-milestones-must-run-locally) authorizes routine deployment without another confirmation; explicit holds and planning-only requests retain their scope.

For an agent change, also name the affected permission/tool schema, source/clock scope, model/prompt version, workload bounds and exact positive/negative tests. Verify that the previous restriction is removed or explicitly retained for a distinct mode, rather than appending contradictory instructions. Use [ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md) IDs for release traceability. Historical approvals and run manifests remain immutable during a documentation or implementation migration.
