# Frontend instructions

Read the root instructions, current task, and [frontend architecture](../../docs/FRONTEND.md). **For every UI task load the installed official shadcn skill first**, obtain project context, and inspect available components before writing code. Follow [the mandatory workflow](../../docs/SHADCN_WORKFLOW.md); an unavailable skill blocks UI implementation, not unrelated backend work.

Preserve the exact owner preset and TanStack Start scaffold. Inspect `components.json` and actual base/icon/token configuration. Reuse shadcn primitives; domain composition and Lightweight Charts adapters are allowed. Do not mix Next.js APIs, another UI kit, or unsupported base-specific patterns.

Use Query for server state, Router for validated URL state, RHF/Zod for forms, Table with shadcn primitives, and Lightweight Charts for financial series. Load the official Lightweight Charts skill for chart tasks. Verify official documentation against installed versions for every material integration and update [integration evidence](../../docs/INTEGRATION_EVIDENCE.md).

Keep Query clients request-scoped on SSR. Keep secrets/backend clients server-only. Use same-origin authenticated BFF mutations with CSRF protections. Financial decimals are strings; the browser never owns account balances. Do not optimistically confirm funding or trades.

Show actual freshness, unknown states and cashflow-neutral performance. No page carries a disclaimer: no PAPER badge and no "paper", "virtual" or "simulated" wording, and no notice that fills are modeled, that a figure is hindsight or a model's, or that a page changes nothing or touches no account ([DECISIONS](../../docs/DECISIONS.md#2026-10-30--no-disclaimers-on-the-pages)). No fabricated default profit or hidden synthetic market fallback. Run applicable lint/type/component and real-browser checks, including hydration, empty/error/stale states and chart cleanup. Report checks not run.

Controls read the [autonomy matrix](../../docs/AUTONOMY_MATRIX.md): the owner's Pause, Resume, Stop, Stop and sell, Start and top-ups are requests the engine applies; the page shows the request's outcome and the run's new state as the engine reports them, never an optimistic one. Display the rule's readings, the in-force records and the fills separately; no page asks for an approval. Preserve missing evidence and actual status; tests cover stale records and request races.
