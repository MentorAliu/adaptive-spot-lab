# Library policy and integration plan

## Version policy

The lockfiles (`services/engine/uv.lock`, `pnpm-lock.yaml`) are the record of what is installed; a version named in a document is not a claim about an environment unless it cites the lock or an installed check. Installs use the committed lockfiles, and every dependency change is reviewed.

Use a pnpm workspace for TypeScript code and a uv-managed Python environment; consult the official container workflow [BE-05](REFERENCES.md#be-05). Avoid duplicate React versions and incompatible Start, Router, Vite and plugin combinations. Add a package only for a concrete need.

## Required frontend

| Package / family | Responsibility | Integration evidence |
|---|---|---|
| Generated TanStack Start/React stack | Routing, SSR, server boundary and application shell | Preserve preset scaffold; verify hosting and route conventions [TS-01](REFERENCES.md#ts-01), [TS-02](REFERENCES.md#ts-02) |
| shadcn components and generated dependencies | Accessible primitives and preset styling | Mandatory official skill; inspect actual base [UI-01](REFERENCES.md#ui-01) |
| `@tanstack/react-query` | Server-state cache and mutations | Per-router/request integration; no process-global SSR cache |
| `@tanstack/react-router-ssr-query` | Official Router/Query SSR integration | Install a compatible version; avoid duplicate hydration/providers [TS-01](REFERENCES.md#ts-01) |
| `@tanstack/react-table` | Headless table state and row/column model | Compose with shadcn Table [UI-06](REFERENCES.md#ui-06) |
| `zod` | Runtime frontend/config boundary validation | Strict input rules; financial decimal strings [TS-06](REFERENCES.md#ts-06) |
| `react-hook-form`, `@hookform/resolvers` | Forms and Zod resolver | shadcn form recipe; verify Zod/RHF resolver compatibility [UI-05](REFERENCES.md#ui-05), [FE-01](REFERENCES.md#fe-01) |
| `lightweight-charts` | The Bitcoin, equity and backtest charts | Client-only lifecycle, skill, attribution [FE-02](REFERENCES.md#fe-02), [FE-03](REFERENCES.md#fe-03) |

The user's informal `tanstack@react-query` and `tanstack@react-table` requests mean the actual scoped packages above. Do not substitute TanStack Form for RHF without approval. Do not add Recharts just because a shadcn chart example happens to use it.

## Linting and quality

Use ESLint flat configuration compatible with the actual scaffold. Add `@tanstack/eslint-plugin-query` and `@tanstack/eslint-plugin-router` with their official recommended configuration [TS-04](REFERENCES.md#ts-04), [TS-05](REFERENCES.md#ts-05). Add `eslint-plugin-react-hooks` and appropriately scoped type-aware `typescript-eslint` checks [FE-05](REFERENCES.md#fe-05), [FE-06](REFERENCES.md#fe-06).

Do not invent dedicated ESLint plugins for Table, Zod, RHF, or Lightweight Charts. Check whether suitable official integrations exist at implementation time; absence is acceptable. Consider an accessibility lint plugin only after reviewing its current official package/documentation and compatibility. Browser accessibility tests remain necessary.

Respect framework control-flow exceptions such as Router redirects/not-found behavior when configuring type-aware throw rules. If React Compiler is enabled by the preset and a library is documented as incompatible with an optimization, verify the precise issue and use the narrow supported remedy. Do not broadly disable compiler/lint rules to hide integration errors.

Use Vitest for frontend logic/component tests, Testing Library for behavioral components, and Playwright for real-browser checks. Use Testing Library's official React setup [FE-10](REFERENCES.md#fe-10) and verify the actual installed integration. Match the Playwright container/browser version to the installed test package [FE-07](REFERENCES.md#fe-07), [FE-08](REFERENCES.md#fe-08).

## Supporting tools

- Generate TypeScript types from FastAPI's versioned OpenAPI contract using `openapi-typescript`; use typed fetch wrappers rather than hand-copying financial DTOs. Generation is not runtime validation [FE-09](REFERENCES.md#fe-09).
- Use Python FastAPI, Pydantic, SQLAlchemy, Alembic and PostgreSQL. Use explicit transaction boundaries, not ORM behavior assumed from memory [BE-01](REFERENCES.md#be-01), [BE-02](REFERENCES.md#be-02), [BE-03](REFERENCES.md#be-03).
- Use pytest plus property-based tests for financial invariants. Use the official pytest/Hypothesis guidance [BE-07](REFERENCES.md#be-07), [BE-08](REFERENCES.md#be-08) and verify compatible setup before installation. HTTP/WebSocket client and retry utilities must have bounded timeouts and documented behavior.
- Structured application logging and local operational state; database-backed schedules and one execution worker. A message broker only if a measured need justifies it.

For Table, read the official data/API guidance alongside the shadcn recipe [TS-07](REFERENCES.md#ts-07). Do not paste remembered v8 APIs into a different installed major, or upgrade a major merely to match a moving documentation page. Table data/columns need appropriate stable references; test sorting, paging and compiler behavior on the selected version. Use Alembic's documented migration environment with one owner [BE-06](REFERENCES.md#be-06).

No Redux or Zustand, agent or LLM framework, vector database, Redis, Celery, Kafka, exchange or news SDK, second charting stack, or client-side financial arithmetic library. Date handling starts with explicit UTC ISO timestamps and platform formatting; add a date library only for a concrete missing capability.

## Dependency review record

What the spot app uses (from the lockfiles; [INTEGRATION_EVIDENCE](INTEGRATION_EVIDENCE.md) records the official sources and installed checks):
- **Engine** (`services/engine/pyproject.toml`): FastAPI and uvicorn, SQLAlchemy 2.0, Alembic, psycopg 3, HTTPX `0.28.1` (the REST client for Binance's public data, MIT) and `websockets` `17.0.1` (the stream client, BSD-3-Clause); for development pytest, Hypothesis and Ruff.
- **Web** (`apps/web/package.json`): the preset's TanStack Start, Router, Query and its SSR integration, Table, Zod, React Hook Form with its resolvers, Lightweight Charts (Apache-2.0: keep its LICENSE and NOTICE and the visible TradingView attribution), shadcn with Base UI, Tailwind and Lucide; for development Vite, Vitest, Testing Library, Playwright, ESLint with the TanStack and React Hooks plugins, Prettier, `openapi-typescript` and the TanStack devtools' Vite plugin.

**ExecPlan 0061** removed three packages nothing imported: `argon2-cffi` from the engine (the owner's sign-in went with [ExecPlan 0042](archive/plans/0042-no-owner-sign-in.md)), and `@tanstack/react-devtools` and `@tanstack/react-router-devtools` from the web (`@tanstack/devtools-vite` stays: `vite.config.ts` uses it). The lockfiles were regenerated with `uv lock` and `pnpm install`; no package was added or upgraded. The agents' dependencies (the Codex and Claude Code CLIs, the runner's own HTTP client) went with their code in ExecPlan 0060; their records are in the [archived copy](archive/contracts/LIBRARIES.md).

For every material addition, record purpose, official documentation and source, exact version, licence, supported runtime, transitive security concerns, test integration, and why existing dependencies are insufficient. Never pin invented digests or claim an audit ran without its output.
