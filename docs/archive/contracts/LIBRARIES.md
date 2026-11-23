# Library policy and integration plan

## Version policy

No package versions in this pack are claims about an installed environment. M0 must inspect the scaffold, verify compatible runtime/package versions using official docs and manifests, and lock the result. Keep the exact user bootstrap command, but record the resolved `@latest` CLI version. Later installs and CI use the committed lockfile and explicit dependency-update review.

Use a pnpm workspace for TypeScript code and a uv-managed Python environment; consult the official container workflow [BE-05](REFERENCES.md#be-05). Verify both tool versions and Docker base images during M0. Avoid duplicate React versions and incompatible Start/Router/Vite/plugin combinations. Do not install every optional package below before its milestone requires it.

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
| `lightweight-charts` | Candles, equity and research time-series charts | Client-only lifecycle, skill, attribution [FE-02](REFERENCES.md#fe-02), [FE-03](REFERENCES.md#fe-03) |

The user's informal `tanstack@react-query` and `tanstack@react-table` requests mean the actual scoped packages above. Do not substitute TanStack Form for RHF without approval. Do not add Recharts just because a shadcn chart example happens to use it.

## Linting and quality

Use ESLint flat configuration compatible with the actual scaffold. Add `@tanstack/eslint-plugin-query` and `@tanstack/eslint-plugin-router` with their official recommended configuration [TS-04](REFERENCES.md#ts-04), [TS-05](REFERENCES.md#ts-05). Add `eslint-plugin-react-hooks` and appropriately scoped type-aware `typescript-eslint` checks [FE-05](REFERENCES.md#fe-05), [FE-06](REFERENCES.md#fe-06).

Do not invent dedicated ESLint plugins for Table, Zod, RHF, or Lightweight Charts. Check whether suitable official integrations exist at implementation time; absence is acceptable. Consider an accessibility lint plugin only after reviewing its current official package/documentation and compatibility. Browser accessibility tests remain necessary.

Respect framework control-flow exceptions such as Router redirects/not-found behavior when configuring type-aware throw rules. If React Compiler is enabled by the preset and a library is documented as incompatible with an optimization, verify the precise issue and use the narrow supported remedy. Do not broadly disable compiler/lint rules to hide integration errors.

Use Vitest for frontend logic/component tests, Testing Library for behavioral components, and Playwright for real-browser checks. Use Testing Library's official React setup [FE-10](REFERENCES.md#fe-10) and verify the actual installed integration. Match the Playwright container/browser version to the installed test package [FE-07](REFERENCES.md#fe-07), [FE-08](REFERENCES.md#fe-08).

## Proposed supporting tools

- Generate TypeScript types from FastAPI's versioned OpenAPI contract using `openapi-typescript`; use typed fetch wrappers rather than hand-copying financial DTOs. Generation is not runtime validation [FE-09](REFERENCES.md#fe-09).
- Use Python FastAPI, Pydantic, SQLAlchemy, Alembic and PostgreSQL. Use explicit transaction boundaries, not ORM behavior assumed from memory [BE-01](REFERENCES.md#be-01), [BE-02](REFERENCES.md#be-02), [BE-03](REFERENCES.md#be-03).
- Use pytest plus property-based tests for financial invariants. Use the official pytest/Hypothesis guidance [BE-07](REFERENCES.md#be-07), [BE-08](REFERENCES.md#be-08) and verify compatible setup before installation. HTTP/WebSocket client and retry utilities must have bounded timeouts and documented behavior.
- Use structured application logging and local operational metrics. Start with database-backed jobs and one worker; introduce a broker only if a measured need justifies it.

For Table, read the official data/API guidance alongside the shadcn recipe [TS-07](REFERENCES.md#ts-07). Do not paste remembered v8 APIs into a different installed major, or upgrade a major merely to match a moving documentation page. Table data/columns need appropriate stable references; test sorting, paging and compiler behavior on the selected version. Use Alembic's documented migration environment with one owner [BE-06](REFERENCES.md#be-06).

No initial Redux/Zustand, agent orchestration framework, vector database, Redis, Celery, Kafka, paid news SDK, separate charting stack, or client-side financial arithmetic library is required. Date handling starts with explicit UTC ISO timestamps and platform formatting; add a date library only for a concrete missing capability.

## Dependency review record

M2's isolated Docker lock resolves HTTPX `0.28.1` as a runtime public REST client (MIT), `websockets` `17.0.1` as the asyncio public-stream client (BSD-3-Clause), TanStack Router ESLint `1.162.0` (MIT) and React Hooks ESLint `7.1.1` (MIT). No exchange SDK, broker, retry framework, chart wrapper or second UI kit was added. The existing Lightweight Charts `5.2.1` package (Apache-2.0) is now used with the v5 installed declarations; keep its LICENSE/NOTICE and visible TradingView attribution in distributed output. The installed shadcn CLI confirmed preset `b2fms61Bqi`; official Base UI Toggle Group semantics were used. Exact official source links, installed declaration checks and command evidence are in [INTEGRATION_EVIDENCE.md](INTEGRATION_EVIDENCE.md). Lockfiles were updated within Docker and frozen checks remain required.

For every material addition, record purpose, official documentation/source, exact version, license, supported runtime, transitive security concerns, test integration, and why existing dependencies are insufficient. Never pin invented digests or claim an audit ran without its output.

The M2 completion work adds no dependency and changes neither lockfile nor preset. The queue uses Python's standard asyncio/concurrency APIs with the existing websockets client; loading uses the already installed Skeleton/Alert primitives. Browser tests use the installed Playwright package and observed locked Start serialization for labeled UI-only response fixtures. Production does not depend on that test transport helper. Existing license/NOTICE obligations and the chart attribution remain unchanged; see [completion integration evidence](INTEGRATION_EVIDENCE.md#m2-completion-integration-review--2026-09-27).

The 2026-09-29 CI work ([ExecPlan 0016](../plans/0016-ci-checks.md)) adds build-time-only GitHub Actions dependencies, pinned by full commit SHA: `actions/checkout` v7.0.1 (MIT), `docker/setup-buildx-action` v4.4.1 and `docker/build-push-action` v7.4.0 (Apache-2.0), and `actions/upload-artifact` v7.0.1 (MIT). It also runs the workflow linters actionlint 1.7.12 and zizmor 1.30.1 (both MIT) from images pinned by digest. None ships in a runtime image or touches application code. Existing tools cannot run checks on GitHub, and Dependabot keeps the pins current, updating only GitHub Actions and waiting 7 days after release. On 2026-10-17 the owner had CI removed ([DECISIONS](../../DECISIONS.md#2026-10-17--github-ci-removed-from-the-repository)): the workflow and the Dependabot configuration were deleted, so none of these dependencies is used now.

## Agent-driven revision dependencies

The expanded workflow does not require a new LLM framework. Start with the existing Python schemas, PostgreSQL jobs and a small typed application-tool dispatcher around Codex CLI. Add the resource-isolated research-worker entrypoint before CPU-heavy experiments. Use registered data/indicator operators and verify any new numerical library against official docs, license and reproducibility needs; do not add a package merely because an agent suggested it.

Optional native MCP integration must use the official Codex/MCP guidance [AI-11](REFERENCES.md#ai-11) and the same server-side tool contract; it is not part of the default transport. No framework installation establishes subscription authentication or API entitlement. The required frontend and official shadcn/chart skill workflows remain unchanged.

M3 (ExecPlan 0011) adds **no dependency** and changes neither lockfile nor the shadcn preset. The engine uses the standard library (`decimal`, `hashlib`, `uuid`, `threading`) with the existing SQLAlchemy/psycopg stack; the web uses the installed TanStack Start/Router/Query/Table, Zod and shadcn primitives (Card, Table, Badge, Alert, Empty, Skeleton, ToggleGroup, `buttonVariants` for link buttons). No chart code changed.

M5 (ExecPlan 0020) adds **one runtime dependency**: the official OpenAI Codex CLI release binary for `x86_64-unknown-linux-musl`, used only inside the isolated `agent-runner` image.
- **Pin.** Version `rust-v0.159.2`, the latest stable release on 2026-09-30.
- **License.** Apache-2.0. The notice obligation is met by copying the upstream LICENSE into the image.
- **Download.** The image downloads only that release asset over HTTPS during the build, and verifies it against a SHA-256 digest pinned in the Dockerfile. The digest's source (the GitHub release asset digest, a sigstore bundle, or a local computation) and the pinned version's own `--help` output are recorded in [INTEGRATION_EVIDENCE](INTEGRATION_EVIDENCE.md#m5-agent-runtime-execplan-0020).
- **Everything else.** The egress gateway, the runner's job server, the mock Responses provider and the fake CLI are in-repo Python standard-library code, with no new Python or npm package. The web pages reuse the installed TanStack, React Hook Form, Zod and shadcn primitives. Any primitive added through the shadcn CLI is recorded with its dry run.
- **No LLM framework.** No orchestration SDK, API client library or paid-provider SDK is added.

## ExecPlan 0049: no new library

The plan proposed the `anthropic` (MIT) and `openai` (Apache-2.0) Python SDKs in the runner image. They were not added: the runner calls the Claude API and the OpenAI API with its own standard-library HTTP client (`services/agent-runner/runner/api_http.py`), keeping the image free of a package manager and third-party packages, and one structured request per call needs no SDK feature ([INTEGRATION_EVIDENCE](INTEGRATION_EVIDENCE.md#execplan-0049-four-providers--2026-10-31)). The Claude Code CLI binary comes back to the runner image at update 1's pinned `2.1.308` with its recorded digest and licence ([INTEGRATION_EVIDENCE](INTEGRATION_EVIDENCE.md#claude-code-cli)). The web adds no package or shadcn component.

