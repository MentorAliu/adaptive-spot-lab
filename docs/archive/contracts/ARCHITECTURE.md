# Architecture and trust boundaries

## The shape in use since ExecPlan 0060 (M12)

IMPLEMENTED by [ExecPlan 0060](../../plans/0060-spot-trading-only.md); NOT RUN on the owner's PC until its update. One account trades Bitcoin spot on paper by a code rule; no model, agent runner, research runner or source fetcher exists.

| Service | Responsibility | Access |
|---|---|---|
| `web` | TanStack Start SSR pages (Cockpit, Trades, Backtest, Settings) and the same-origin BFF; relays the live trades as one event stream per browser | The private API with its internal key; no database or exchange access |
| `api` | Projections, the owner's requests (Pause, Resume, Stop and sell, Start) and top-ups; the account's starting 10,000 USDT at its first start; the live trades stream | Role `asl_api`: reads the spot and account tables, inserts the owner's requests and the funding requests |
| `market-worker` | Binance's public spot feed (`app.spot_market`): the order book each second, 1-minute candles, every final daily candle since 2017-08-17, the instrument and the clock | Role `asl_market_worker`: writes the spot market tables only; the `market_egress` network to Binance's market-data-only hosts ([MARKET_DATA](MARKET_DATA.md)) |
| `execution-worker` | The single fenced paper-execution authority (`app.spot.worker`): the one-second step, the fills, the postings, reconciliation every 5 minutes; the backtest beside it, outside the step | Role `asl_execution`; the private network only |
| `postgres` | The ledger, the account, the runs, readings, fills and backtests; the retired tables in the `archive` schema, readable by the migration role only | The private network only |
| `migrate` | Alembic to head, run by the update | The migration role |

```text
Binance's public spot data -> market-worker -> spot_quotes, spot_bars, spot_daily_bars, spot_instruments, spot_feed_state
                                                   |
execution-worker step, one fenced transaction a second:
  owner requests -> first run -> stopping run's sale -> valuation, day reference, latches -> run state -> SPOT_RULE_V1
                                                   |
        fill on the stored book (SPOT_COST_V1) -> journal postings (app.spot.ledger) -> account_state, account_holdings
                                                   |
        announcement on asl_spot_live -> api listener -> event stream -> web (toasts; pages read again)
execution-worker, outside the step: SPOT_BACKTEST_V1 on spot_daily_bars -> spot_backtests
```

The browser and the API cannot set a balance: the owner's requests are rows the engine validates and applies in its own transaction; top-ups go through M1's funding path ([LEDGER](LEDGER.md)). The sections below are the design up to M11, kept as history.

## Deployment shape

One repository and a modular Python engine, with separately managed processes. This is not an unrestricted swarm or a large distributed trading platform.

| Service | Responsibility | Required access |
|---|---|---|
| `web` | TanStack Start SSR/UI and same-origin BFF | Private API; no database/model/exchange credentials |
| `api` | Authenticated owner controls, projections and versioned contracts | Engine domain services and appropriately scoped DB role |
| `worker` | High-priority market/protection/paper execution; durable agent orchestration and tool dispatch (M5: a separate `agent-worker` process, below) | Operational DB, public data adapters, restricted runner interface |
| `postgres` | Ledger, policy/approval, jobs, evidence and audit state | Private application network only |
| `agent-runner` | Bounded Codex inference steps, not financial execution | Own auth state, staged inputs, provider endpoints; no DB or repo access |
| `research-runner`, `research-bridge` (M6) | Retired by [ExecPlan 0035](../plans/0035-a-simpler-app-that-trades-by-itself.md): registered backtests and shadow replays on a second cluster, and the relay to it | Gone from `compose.yaml`; the update removes their containers ([DOCKER](DOCKER.md#research-services-retired-execplan-0035)) |
| `source-fetcher` (M6) | Approved source-version fetch and evidence ingestion | Source/evidence tables and approved host/path templates only |

Research is off since ExecPlan 0035; the rest of this paragraph is the history of the M6 services. The M6 services are the approved design of [ExecPlan 0023 §5.1](../plans/0023-m6-research-investigations.md#51-services-networks-and-identities-all-new-pilot-services-untouched), not implemented by this contract amendment. A second PostgreSQL cluster isolates research writes and resources. The runner shares the existing paper engine and replay code with research-only credentials; the bridge alone spans both private networks and has no engine authority. Heavy research cannot run synchronously inside the protection loop. B3 implemented the research cluster and runner and B4 the bridge, the versioned stores and the deferred-replay shadows; both are verified in isolated fixture stacks only ([ExecPlan 0023 §18](../plans/0023-m6-research-investigations.md#18-completion-evidence)). The runner, not the bridge, creates and drops store databases, on a request the bridge records in the research cluster's registry. Services ship inert until the owner performs M6-B. One-shot migration/test/tooling services are separate profiles.

A small durable broker/dispatcher is an application component, not necessarily an extra network service. Initially the `worker` dispatches validated requests through internal functions and PostgreSQL jobs; no Redis, vector database, LangChain, multi-agent framework or native MCP server is required.

## Agent and financial paths

```text
public adapters -> time-stamped observations/evidence -> immutable snapshots
                                                 |
                                scheduler / bounded role workflow
                                  |  analyst -> researcher -> evaluator
                                  |                       -> coordinator
                                  v
                          Codex inference step (isolated)
                                  | structured application-tool request
                                  v
                    authenticated, role-scoped tool gateway
                    /                  |                 \
          approved evidence      isolated experiments     draft/submit intent
                                                          |
                          permission + mandate + review + current risk checks
                                                          |
                       fenced order/reservation transaction -> paper broker
                                                          |
                                modeled fills -> accounting -> projections
                                                          |
                                 outcomes -> review -> bounded next decision
```

The normal deterministic strategy path remains available for baselines. Both that path and agent intents converge on the same financial validation/commit service. No browser-to-exchange, model-to-ledger, research-to-main-write or direct MCP-to-broker alternative is permitted.

## Four logical model roles

Roles live in [RUNTIME_AGENTS.md](../RUNTIME_AGENTS.md), permissions in [AUTONOMY_MATRIX.md](AUTONOMY_MATRIX.md), tools in [AGENT_TOOL_CONTRACTS.md](../AGENT_TOOL_CONTRACTS.md). A single provider can execute their steps sequentially. Their separation permits restricted inputs, evaluation and audit; it is not evidence of statistically independent opinions.

The orchestrator determines identities, finite state transitions, deadlines, permitted artifacts and next roles. Agents may request reviewed services, not create unlimited children or change the workflow graph. Durable role artifacts are typed evidence, not a shared free-form conversation treated as truth.

## Exact authority sequence

1. Create an immutable task/snapshot and job capability under an approved envelope.
2. Validate each model step and each requested tool against that role, schema, mode, budget, permission epoch and as-of boundary.
3. Persist returned evidence/artifacts with server-assigned origin and status. Model-written claims remain hypotheses until independently grounded.
4. Coordinator drafts an intent; obtain the required evaluator result tied to the exact content hash. Any substantive edit requires a new review. Protective exits bypass model review, not execution checks.
5. Submit the intent: independently recompute effective permissions, account state, current observations, exit mandate, sizing, cost/turnover and pending commitments. Expired snapshots are not execution permission.
6. Under a fenced transaction, reserve funds/risk and create an order or rejection plus outbox event. Recheck execution constraints on subsequent modeled fills.
7. Replay unknown outcomes using durable IDs, never blind repeats. Invalidate old work after revocation, model/policy changes or material account updates.

## Persistence and modes

Use PostgreSQL-backed durable jobs/outbox with bounded leases and a fencing token for main execution. One active main experiment per account; each M6 deferred shadow has separate virtual capital and financial state in its own replay database. The current engine modes remain `OFFLINE_TEST`, `HISTORICAL_RESEARCH` and `FORWARD_PAPER`; M6's `SHADOW — deferred replay` is a catalog label with engine rows in `HISTORICAL_RESEARCH`, not a new engine mode. A live engine-level `SHADOW` mode and multi-account ledger wait for the experiment boundary. A policy kind (`FIXED`, `ADAPTIVE_SELECTOR`, `AGENT_DRIVEN`) is separate from experiment mode.

Proposed modules: identity/policy registry, source/evidence service, snapshot store, agent orchestrator, tool gateway, declarative research runner, risk/intent validator, broker, ledger, evaluation and projections. Their contracts are specified; exact source paths are decided in scoped implementation plans.

## Server and frontend boundaries

Browser requests go through the same-origin Start BFF. Server functions/routes are thin authorized adapters; loaders may run in the browser and are not automatically secret-safe [TS-03](REFERENCES.md#ts-03). Query caches are request-scoped on SSR. The backend validates financial/control actions independently. API data carries decimal strings, UTC timestamps, explicit quality states and generated transport types.

## Future portability

Implement only PaperBroker. No actual Binance-account integration exists. Another broker or paid model transport would require new authorization, testing, access controls and operational review. A clean interface does not itself authorize live execution.

## M3 implemented shape

The logical `worker` row above is split: `market-worker` collects public observations (M2) and `execution-worker` is the single fenced paper-execution authority (M3), built but not started on the owner installation. The execution package (`app/execution`) contains pure policy code (numbers, definitions, filters, fill model, risk, lifecycle), the fenced store, the step engine, the forward worker, a simulated/replay driver and read models; `app/strategies` holds `TREND_REFERENCE_V1`; `app/replay` holds the isolated replay runner, built-in synthetic scenarios and financial fingerprints. One engine core serves forward and replay modes; only the market view (live M2 eligibility vs the reduced recorded rule) and the clock differ. Modes: `FORWARD_PAPER` (main, structurally blocked in M3), `OFFLINE_TEST` (guarded fixtures) and `HISTORICAL_RESEARCH` (replay, displayed as REPLAY).

## M5 agent runtime shape (ExecPlan 0020)

The logical `worker` row's agent orchestration and tool dispatch runs as its own process, `agent-worker`, so the pilot's execution and evaluation workers are untouched ([ExecPlan 0020 §12](../plans/0020-m5-agent-runtime.md#12-coexistence-with-the-running-m4-pilot)). It shares the engine codebase and image and runs as its own database identity, `asl_agent`, with `app/agents` holding:
- pure schemas, definitions and hashing;
- profile, approvals, controls and the permission epoch;
- the orchestrator, dispatcher and tools;
- the providers and the runner client.

```text
browser -> Start BFF (session, CSRF, Host) -> api (service key + session) -> PostgreSQL (agent tables)
agent-worker -> PostgreSQL (agent tables, agent_read views) ; agent-worker -> agent-runner (agent_control, runner key)
agent-runner -> agent-egress (agent_provider) -> provider hosts pinned in the approved profile (model_egress)
owner terminal -> agent-auth -> agent-egress (device-code login only)
```

The runner has no database, repository or owner credential. The worker has no route to the gateway. Tools are engine handlers that read public market data through the `agent_read` views; none touches the ledger, broker, approvals or pilot records. Market assessments and reviews are immutable, untrusted artifacts, and nothing in M5 converges on the financial commit path.
