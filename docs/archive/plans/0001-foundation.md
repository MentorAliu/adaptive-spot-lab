# ExecPlan 0001 — M0 foundation

## Approved implementation plan — 2026-09-26

The owner authorized implementation of this reviewed M0 plan, including container builds, isolated tests, documentation, commit, and a non-forced push to `origin/main` **only after required checks and review pass**. The original starter draft remains below as planning history. This section is the execution baseline; observations belong in the verification record, not in a rewrite of the baseline.

### Scope and boundaries

Deliver a local, single-owner paper-research foundation: containerized TanStack Start web application, private FastAPI/PostgreSQL service, uv and pnpm lockfiles, one Alembic migration owner, same-origin read-only health/status path, request-scoped Query SSR, typed generated API contract with runtime validation, and an honest empty/unconfigured interface. Display PAPER and virtual USDT. Do not implement balances, funding, ledger, broker, market ingestion, model login/calls, experiments, chart series, or M1 features. Future worker, model runner, and research worker remain non-executable at M0.

### Ordered execution

1. Inspect repository ancestry, prior work, Docker capacity, authoring tools, instructions, contracts, and current official integration sources. Preserve all supplied files and existing Docker volumes. Record observations separately from proposals.
2. Build a bootstrap tooling image independent of app manifests. Install and load the official shadcn authoring skill. In a verified empty temporary directory run exactly `pnpm dlx shadcn@latest init --preset b2fms61Bqi --template start --pointer`, answer its project-name prompt, inspect the generated base, configuration, and dependencies, then merge into `apps/web` without replacing scoped instructions. Run `shadcn info --json`, search and read component docs, and use registry primitives.
3. Establish a root pnpm workspace and the generated TanStack Start application with the owner's preset. Retain `@tanstack/react-query`, `@tanstack/react-table`, Zod, React Hook Form, Lightweight Charts, and compatible lint integrations. Use a fresh QueryClient for each server router/request and a stable browser client through the official SSR Query integration. Server-only code calls the private API; client bundles contain no backend credential or private network address. M0 uses read-only status and no owner mutation/session.
4. Create uv-managed FastAPI and SQLAlchemy/PostgreSQL skeleton, one Alembic migration owner, liveness/readiness/status endpoints, and a narrow internal service credential for the BFF. Readiness reflects DB/migration loss; liveness remains independent. Keep all financial state absent. Generate TypeScript API types from the actual OpenAPI schema and validate status responses at runtime with Zod.
5. Build runtime and test images with locked dependencies and nonroot final processes. Compose only web, API, PostgreSQL, and one-shot migration as active services. Publish web on loopback only; keep API/DB private. Use durable normal DB storage, distinct test storage, no Docker socket or host home/repository mount in runtime services. The disabled future services get no entrypoint or secrets.
6. Add meaningful backend, frontend SSR/hydration, API drift, boundary, and browser tests. Run containerized lint, typecheck, unit/integration, production build, migration/start/restart, failure/readiness, browser/empty/error, port/mount/process/secret checks. Repair failures and rerun affected checks. Capture exact commands, results, and unrun checks. Do not mark a partial condition verified.
7. Review the final diff for M0 boundaries and security; update `docs/STATUS.md`, `docs/COMMANDS.md`, `docs/INTEGRATION_EVIDENCE.md`, and this plan. Commit only intended changes and push to verified `origin/main` after all required checks pass, without force. Confirm remote commit and clean working tree. Stop before M1.

### Architecture and decisions

`Browser → same-origin Start BFF → private FastAPI → private PostgreSQL`. The browser uses Query for server state, Router for URL state, and shadcn primitives for the shell/status. No production form or financial table data is invented merely to showcase a library; appropriate isolated integration tests may cover RHF/Zod and Table. Lightweight Charts remains a required dependency for M2 chart work, but no chart adapter is fabricated for empty M0 data. The official chart skill is required if chart implementation occurs. M0 has no owner session and no mutation endpoint; BFF service authorization is not equivalent to owner authentication. The M1 session and CSRF design remain gated before financial mutation.

### Acceptance evidence required

The M0 claim requires all applicable P09/A04 foundation checks, partial P10/A03 and P12/A12 boundaries, actual container builds/tests, real-browser evidence, dependency-failure/restart behavior, CLI preset discovery, and final security/diff review. No M1–M8 trading or agent acceptance condition can be claimed here. The delivery must state exact commands and outcomes, local URL and start/stop instructions, limitations, commit hash, remote confirmation, and tree status. If any required gate fails or cannot run, preserve work and report M0 incomplete; do not push as a passing milestone.

### Execution record

- 2026-09-26: Baseline `main` and `origin/main` matched at `a6e5009dc5d794b854cab5b884e864421e6fd178`; working tree clean before edits. Docker 29.7.2 and Compose v5.5.1 responded with authorized host access. Host Node 24.19.0, pnpm 11.19.0, and uv 0.12.5 were observed; no host Python on PATH.
- 2026-09-26: Installed the official `shadcn-ui/ui` `skills/shadcn` into the active Codex authoring environment and read its `SKILL.md`. The documented `pnpm dlx skills add shadcn/ui` failed with `ERR_MODULE_NOT_FOUND: yaml` in `skills` CLI 1.7.0; the bundled Codex skill-installer fetched the same official source successfully. The skill becomes automatically discoverable on the next turn; this turn loaded it explicitly from disk.
- 2026-09-26: Bootstrap image with pnpm 10.28.2 built independently of app manifests. Initial noninteractive scaffold invocation reached the name prompt and created no files. The next invocation exposed missing `git`; the image was repaired with git. The exact scaffold command succeeded interactively in a verified empty temporary directory, with project name `web`. CLI 4.21.0 generated TanStack Start, Base UI, `base-nova`/mist, Roboto Slab/Public Sans, Lucide and the pointer CSS rule; final `shadcn info --json` confirmed preset `b2fms61Bqi` and six registry primitives. The bootstrap and web base images were later aligned to Node 24.19.0 after installed jsdom 30.1.1's Node engine declaration was inspected.
- 2026-09-26: pnpm 10.28.2 and uv 0.12.5 lockfiles, a TanStack Start/Nitro server, request-scoped Query SSR, read-only same-origin BFF, private FastAPI health/status, PostgreSQL/Alembic revision `0001_foundation`, offline API generation, isolated test project, and honest shadcn empty/error UI were implemented. No funding, balances, broker, market prices, chart, model login, agent execution, or paid call was added. Installed versions, official integration sources and license declarations are in [INTEGRATION_EVIDENCE.md](../../INTEGRATION_EVIDENCE.md).
- 2026-09-26: Startup initially failed because Docker's automatic subnet pool was exhausted; explicit separate normal/test subnets restored startup without changing unrelated Docker state. API health then failed because the trusted-host list excluded its own loopback probe; a regression test and host-list repair fixed it. Test discovery was repaired by invoking `python -m pytest`, and browser locators were scoped to the main region. These failures were not treated as passing evidence.
- 2026-09-26: Containerized lint/type/unit/API drift/build checks passed; isolated backend tests passed 5/5; Chromium passed 2 normal cases and a separately run database-outage case. Stopping only the isolated PostgreSQL container left liveness at HTTP 200, changed readiness to HTTP 503, and displayed the error state; restart restored HTTP 200 readiness and the empty UI. Final runtime inspection showed only loopback web exposure, nonroot web/API/PostgreSQL processes, intended secret/DB mounts, and no private credential markers in the public bundle. Exact commands and caveats are in [COMMANDS.md](../COMMANDS.md).
- 2026-09-26: `apps/web/package.json` direct dependencies were exact-pinned to their tested lockfile resolutions. A fresh frozen install succeeded. The final Docker images use Node 24.19.0 because the locked jsdom version requires Node 24.15 or newer. Focused staged review corrected sample web-manifest metadata and removed the test-only Host alias from the private API's runtime allowlist. Backend lint/OpenAPI checks, 5 backend tests, 2 normal Chromium tests, the outage Chromium case, final Docker startup, and the loopback UI were rerun after the relevant changes. No other actionable M0 finding remained. Commit and non-forced push are the authorized delivery steps after this local gate.

## Historical starter status before implementation

The starter draft below was DRAFT / NOT EXECUTED when the specification pack was prepared. The approved plan and observed M0 record above supersede that historical state. Read root instructions, [decisions](../../DECISIONS.md), [architecture](../../ARCHITECTURE.md), [Docker contract](../../DOCKER.md), [UI skill workflow](../../SHADCN_WORKFLOW.md), and applicable scoped instructions for future work.

## Goal and observable outcome

A locally containerized foundation with the owner's actual TanStack Start/shadcn preset, FastAPI/Postgres skeleton, verified library/SSR/tooling integration, honest empty/status UI and passing applicable build/test checks. No trading, funding effects, runtime model login, paid calls or live exchange capability.

## Current repository facts

Only Markdown specifications and instruction files are supplied. There are no package manifests, lockfiles, source modules, Dockerfiles, skills installed by this pack, databases or test results. The preset is named but unexecuted. Any environment observation must be gathered by the implementing agent, not copied from this draft as fact.

## Proposed steps

1. Inspect repository, Docker/Compose and authoring-client environment within existing permissions. Record actual versions/capability failures. Resolve only genuine M0 blockers; do not ask the owner to repeat confirmed scope/stack decisions.
2. Verify official bootstrap, skill, Start/Query, shadcn/Table/RHF, chart, lint and Docker integration docs against proposed dependencies. Record compatibility choices and package-manager/runtime versions. Distinguish planned from installed versions.
3. Establish a bootstrap tooling image that does not require app manifests. Plan temporary scaffolding and safe file merge preserving all supplied documents and scoped instructions. Run the exact preset command only after implementation is authorized.
4. Install official shadcn skill for the active authoring client(s), verify discovery, inspect actual components.json/base/styles/icons. Install/plan the official Lightweight Charts skill for later chart work. Do not mount either into runtime agent jobs.
5. Create the pnpm workspace and Start application; preserve preset configuration. Add verified required dependencies and lint/test configuration. Establish request-scoped Query SSR and a minimal tested canonical query without fake financial state. Implement a shadcn-composed shell and honest unconfigured health view.
6. Create the uv-managed engine skeleton, FastAPI health/schema endpoints and PostgreSQL/Alembic skeleton with one migration owner. Propose the local single-owner session/BFF authorization boundary; no financial mutation can be enabled without it.
7. Implement runtime/build/tool/test Compose structure, nonroot services, loopback-only web port, private DB/API, durable state, readiness/migration ordering and isolated test volumes. Agent-runner is absent/disabled or an honest unconfigured capability, not a fake successful model service.
8. Implement OpenAPI-to-TypeScript contract generation, baseline unit tests and a real-browser SSR/health/empty-state check. Build the actual Start production server using verified output paths.
9. Run applicable commands, inspect ports/mounts/images for secrets, restart the stack, review the diff and update status/commands/integration evidence. Report failures and checks not run. Stop before M1.

## Expected file areas

Root package/workspace/lock/config/ignore/Compose files; `apps/web` source/config/tests; `services/engine` source/pyproject/lock/migrations/tests; Docker tooling/test definitions; shared generated API type location; documentation updates. Choose exact paths after inspecting the scaffold. Do not invent that a generated router/output file already exists.

## Requirements and tests

M0 directly addresses P09/P10 and establishes boundaries for P01/P11/P12. Test actual preset preservation, skill discovery, lint/type/build, Query SSR request isolation/hydration behavior, safe server-only imports, API readiness, Compose networking and honest empty states. Financial requirements are future tests, not claimed passed at M0.

Use the proposed commands in [COMMANDS.md](../COMMANDS.md), updating them to actual verified service names and scripts. Record test names and observed results. No paid/live service calls are necessary.

## Risks and remedies

- Nonempty scaffold target: create temporarily and merge; never delete specifications.
- Unknown preset/base/version: inspect generated artifacts; report upstream failure rather than selecting another theme.
- Skill available only on host or only in container: make actual authoring execution/discovery explicit.
- Docker/sandbox unavailable: report a blocker; never enable privileged runtime/Docker socket or claim native checks prove Docker works.
- Framework integration drift: use installed-version official docs and minimal regression tests before adding product features.
- Auth/secret leakage: no runtime login in M0, safe ignored placeholders only; verify final image/mount boundaries.

## Historical draft verification placeholder

Record observed environment; changed files; source/version evidence; exact commands and actual output; browser evidence; known failures/not-run checks; requirement coverage; decisions/deviations; and readiness for M1. Keep this section explicitly unexecuted until those observations exist.

## v2 architecture compatibility

This draft remains the M0 foundation plan. The expanded target has role-scoped application tools, approved-source research and agent trade intents; none is permission to implement M5–M7 during M0. Read [AUTONOMY_MATRIX.md](../../AUTONOMY_MATRIX.md), [AGENT_TOOL_CONTRACTS.md](../AGENT_TOOL_CONTRACTS.md) and [ROADMAP.md](../../ROADMAP.md) before selecting service boundaries. Reserve the later research-worker entrypoint/resources without adding a paid provider, vector store or orchestration framework by default.

For an existing repository, the statement “only Markdown is supplied” describes this pack, not observed repository state. Follow [MIGRATION.md](../pack-2.0.0/MIGRATION.md), preserve completed work and actual evidence, and revise this plan to the real next bounded task rather than rerunning setup. The empty-repository M0 path still ends before account funding, runtime login and trading.
