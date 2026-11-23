# ExecPlan 0003 — M2 public market data and charts

## Completion implementation — authorized 2026-09-27

**COMPLETE from `434bc98a7b393d023e4351f0bc38b974109d44cf` (clean); all scoped Q01–Q10 gates passed.** The owner reported all Narrator checks passed on 2026-09-28, closing the final manual condition. Earlier evidence is preserved below and affected Q01–Q10 conditions are reassessed in section 7. Owner activation and M3 remain excluded.

Sequence: (1) forward-only `0004_m2_completion`, explicit bounded receive pipeline, recovery generations, telemetry and watermarked REST conflict confirmations; (2) exact transport identities, accessible loading/health/conflict UI and browser race handling; (3) fresh isolated Docker acceptance, full-density storage/cap fixtures, 60-minute normal/five-minute burst, recovery memory, public interruption and migration rehearsals; (4) owner-guided Narrator review of the final image, final gate assessment and verified push. The owner performs the manual Narrator checklist; native screen-reader operation is unavailable to the coding tools.

Decisions: collection identity describes capture, independently of the publishing lease epoch. Confirmation records and observations share the publication sequence. Legacy capture provenance remains null. Queue accounting includes in-flight frames, with conservative receive reservations. Tests inject dependencies through Python constructors only; production settings cannot enable a test clock or arbitrary provider destination.

The [completion run record](#7-completion-run-record--2026-09-27) below records implemented changes, actual results and remaining checks. Earlier passes and the earlier publication exception remain historical; they do not waive this completion request's gates.

## 1. Baseline, outcome and boundaries

**Status: IMPLEMENTING; acceptance gates remain open.** The reviewed proposal below is retained as the declared baseline. The dated implementation and verification record at the end takes precedence for actual status; a proposed command or budget is never a verification result. The owner authorized implementation, isolated verification and publication to `origin/main` only after all gates pass. No M3 work is authorized.

### Observed baseline

- **OBSERVED:** Branch `main`, HEAD `4c928bff0fdf98def95f61ad4e4a085ae2742e24` — “Implement M1 owner account and virtual funding ledger.” The working tree remained clean after investigation.
- **OBSERVED:** The implementation has a TanStack Start BFF, private FastAPI service, PostgreSQL, and one Alembic migration owner. The current schema is `0002_m1_account`. No market worker, ingestion tables, market routes or rendered charts exist.
- **Historical VERIFIED:** [STATUS.md](../../STATUS.md), [ExecPlan 0002](0002-funding-ledger.md) and [COMMANDS.md](../COMMANDS.md) record M0/M1 verification, including 15 backend tests, six frontend tests, browser failure cases, migration, restart and isolated restore. These checks were **not rerun** during planning.
- **OBSERVED:** Docker inventory showed the normal application stack running. It was not exercised or changed, and its running images were not assumed to match HEAD.
- **OBSERVED:** Root, engine, web, documentation and test instructions were read. Their requirements cover every proposed subtree.
- **NOT RUN:** Builds, tests, migrations, provider smoke checks, ingestion, authentication and resource measurements. No files were changed, packages installed, runtime resources created or services started/stopped.

M2 is the next bounded milestone because M1 supplies authenticated access and durable accounting, while M3 requires trustworthy observations before execution can be modeled.

### Observable outcome

An authenticated owner can:

- View BTCUSDT/SOLUSDT instrument status, latest public bid/ask observations and quantities.
- Inspect finalized UTC 1h candles and a clearly provisional current candle.
- See missing history, backfilled intervals, source/receipt/availability times, stale observations and recovery.
- Inspect feed and worker health independently of socket connectivity.
- Use accessible market tables and Lightweight Charts without opening exchange connections from the browser.

M2 adds observation collection and presentation. It does not add valuation posting, strategies, indicators, orders, fills, experiments, model execution, approvals or financial authority. Funding, journal, reservations, reconciliation, high-water references and latches remain governed by M1.

No exchange credentials, private/signed endpoints, Testnet, Demo, paid services or alternative providers are introduced.

## 2. Recommended architecture and contracts

### Provider and collection choice

Use only the documented market-data-only REST and WebSocket hosts. Documentation establishes supported interfaces; reachability and current symbol availability on this PC remain implementation-stage checks. [Binance market-data-only documentation](https://developers.binance.com/en/docs/products/spot/faqs/market_data_only)

| Purpose | Proposed interface and behavior |
|---|---|
| Clock | `GET https://data-api.binance.vision/api/v3/time`; measure request duration and clock-offset uncertainty. |
| Instruments | `GET /api/v3/exchangeInfo?symbol=BTCUSDT`, separately for SOLUSDT, allowing independent symbol failure. Validate returned identity, base/quote assets, status, spot eligibility and filter structure. Preserve the complete snapshot. |
| Historical candles | `GET /api/v3/klines`, explicitly `interval=1h`, UTC, bounded start/end and limit. These are 12-element records identified by opening time; the documented maximum is 1,000 rows and request weight is 2. [REST market data](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market) |
| Live candles | `<symbol>@kline_1h`, preserving event time, interval boundaries and the provider’s closed flag. |
| Current quotes | `<symbol>@ticker`, extracting timestamped best bid/ask and displayed quantities from its one-second snapshots. Preserve the complete received payload. |
| Shared connection | One combined connection to `wss://data-stream.binance.vision:443/stream`, containing the ticker and 1h-kline streams for each validated symbol. |

The timestamped ticker is recommended because `bookTicker` lacks an exchange event timestamp. This produces **sampled top-of-book observations**, not a complete order-book or trade tape. The distinction must appear in provenance and future execution inputs. [Official stream schemas](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/ws-streams/~)

Do not collect separate trades or reconstruct depth in M2. No approved execution model currently requires them. M3 must assess this sampling fidelity and approve latency, liquidity, consumption, partial-fill and cost assumptions before using these observations. If its selected model requires depth, that work must implement the documented snapshot/delta sequencing and invalidation rules then.

Instrument snapshots must preserve price, quantity and notional filters, applicability flags, permissions and unfamiliar fields. Unknown filters cannot silently become supported execution rules. Current documentation also describes reference-price dependencies for some notional checks; M2 records these requirements without implementing order validation. [Exchange information](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general), [filter definitions](https://developers.binance.com/en/docs/products/spot/filters)

### Worker, API and database responsibilities

Add a separately deployed `worker` entrypoint to the existing Python engine image:

- The worker alone owns provider connections, validation, ingestion, recovery and checkpoints.
- Use `asyncio` for network work and one bounded database-writer executor around the existing synchronous SQLAlchemy/psycopg stack.
- The API reads committed market snapshots. Browser requests never initiate provider requests or historical backfill.
- The browser continues through authenticated same-origin Start server functions.
- The existing migration service remains the only Alembic owner.

Give the worker a separate `asl_market_worker` database identity and secret. Its grants cover market observations and ingestion state only; deny access to owner credentials/sessions and writes to all financial, approval and accounting tables. Give `asl_api` read access to the market schema.

Attach the worker to the private database network and a dedicated outbound network. Retain existing API/PostgreSQL privacy and loopback-only web publishing. Production clients use fixed public hosts and paths, TLS verification, disabled implicit proxies, rejected redirects and bounded responses. Reject nonpublic DNS destinations without a check/connect resolution race. Test-provider exceptions exist only in isolated test tooling.

Market collection must be independently disableable. Default it disabled when upgrading an existing M1 installation; enabling public collection is a documented operational step following successful preflight. This setting cannot enable trading.

### Persistence and transaction boundaries

Add a forward-only `0003_market_data` migration from the actual `0002_m1_account` revision. Create an account-independent market schema with these responsibilities:

| Record group | Persistence and indexing |
|---|---|
| Collection/source configuration | Provider identity, adapter/schema versions, configuration hash, collection identity and provenance mode. No experiment is started by collection. |
| Evidence and observations | Immutable raw response/frame bytes or lossless normalization, SHA-256, source identity, timestamps, sequence and validation result. REST batches share one retained payload reference. |
| Instrument versions | Immutable content versions plus latest-observed projection; index provider/symbol/availability. Retrieval time is not an invented filter effective time. |
| Candle revisions | Semantic identity: namespace/provider/symbol/interval/open time. Immutable revisions, finality and supersession references; unique semantic content per identity. Index symbol/interval/open time and publication sequence. |
| Quotes | Immutable timestamped bid/ask snapshots with displayed quantities, plus latest-valid projection. Index symbol/event time and publication sequence. |
| Ingestion state | Fenced lease, stream generation, restart checkpoints, last committed observations and contiguous candle coverage. |
| Quality/incidents | Missing intervals, observation outages, conflicts, invalid payloads, recovery transitions and bounded operational events. |
| Evidence retention | Dataset manifests and pin references that prevent referenced evidence from being deleted. No experiment runner or promotion workflow. |

Use PostgreSQL `NUMERIC` without a fixed market-data scale, and Python `Decimal`. Bound accepted plain-decimal strings to 80 characters; reject nonfinite values, exponent notation and unsupported representations rather than rounding them. Preserve original lexical values in evidence. Inspect actual instrument filters during smoke verification before introducing narrower precision constraints. M1 monetary columns are unchanged. [PostgreSQL numeric semantics](https://www.postgresql.org/docs/17/datatype-numeric.html)

Use a market-ingestion lease separate from M1 account fencing:

- Proposed lease duration: 10 seconds; heartbeat/renewal every 2 seconds.
- Acquisition increments an epoch. Each publishing transaction locks the lease row and verifies owner, epoch and expiry.
- Only the current holder may connect and publish. A stale holder cannot advance projections or checkpoints.
- Network requests occur outside transactions. Database transactions have bounded timeouts.

Persist validated batches before publication. After persistence succeeds, record a conservative post-persistence availability time, then atomically publish the associated revisions/projections, quality changes, checkpoint and market event. Unpublished batches are invisible to consumers; recovery publishes them with recovery-time availability and rechecks quote freshness.

Historical access must additionally bind a committed publication watermark, preventing timestamp-only access from exposing information committed later. Test crashes between persistence and publication.

Use a separate market event/outbox structure: M1’s financial outbox requires an account version and must not receive invented account versions for market events. Preserve explicit SQLAlchemy transaction ownership. [SQLAlchemy 2.0 transactions](https://docs.sqlalchemy.org/en/20/core/connections.html#using-transactions)

### Provenance, finality and eligibility

Every observation carries:

- Source/provider, endpoint or stream, symbol, schema/adapter version and collection identity.
- Existing applicable mode, acquisition kind—stream, historical REST or offline fixture—and no implied active experiment.
- Source event time when supplied; receipt time; conservative availability time; publication sequence; worker generation.
- Instrument snapshot reference, quality state/reasons, payload reference and hashes.
- Source timestamp precision. Use millisecond provider timestamps explicitly; serialize UTC ISO timestamps with documented precision. Serialize large IDs as strings.

For REST history, candle opening/closing times describe the interval, not when the application observed it. Backfill availability is the actual ingestion time. A repaired chart does not repair a historical forward-observation outage.

Finality rules:

- WebSocket candles are provisional until `x=true`.
- REST candles are eligible for historical finalization only when their closing boundary precedes the conservative provider-clock lower bound.
- Preserve source OHLCV and enforce finite positive prices, nonnegative volumes, interval alignment and valid OHLC relationships.
- Do not validate old candles against current tick-size rules as though those filters were historically effective.
- Changed finalized content creates a revision and conflict record. Obtain bounded REST confirmation before selecting a corrected current projection; retain all prior revisions and availability boundaries.
- Provisional candles never satisfy finalized-history queries or warm-up coverage.

Expose distinct eligibility results for display, contiguous finalized history and current quote freshness. Keep paper trading disabled. The existing quote-age proposal remains owned by [RISK_POLICY.md](../../RISK_POLICY.md); using it for M2 health tests does not approve an execution policy.

### Failure and recovery rules

| Condition | Required behavior |
|---|---|
| Duplicate | Deduplicate using stream identity, documented identifiers where present, and canonical content. Preserve first availability; duplicate receipt cannot refresh a quote. |
| Out of order | Retain evidence, flag ordering, and prevent an older event replacing the latest quote or a provisional candle replacing a final candle. |
| Ticker identity limitation | Use symbol/stream/event time plus semantic hash; equal-time conflicting content is ambiguous and ineligible until a later valid snapshot. Do not assume consecutive provider sequence numbers. |
| Malformed/schema change | Quarantine bounded evidence. Missing/wrong-type authoritative fields invalidate the observation. Preserve additive fields and report schema drift; unsupported filter semantics remain ineligible for execution. |
| Missing candle | Record the exact interval, request bounded repair, and report partial history until resolved. Never synthesize an empty or flat bar. |
| Stale/disconnected | Preserve the last trustworthy value and its original times. Heartbeats, polling and rerenders cannot renew its freshness. |
| Clock anomaly | Invalidate time-dependent eligibility, retain observations diagnostically, resample the clock and require successful recovery checks. |
| Database failure/unknown commit | Stop publishing; resolve batches by durable IDs before retrying. Derive a conservative outage from the last durable checkpoint after restart. |
| Queue overload | Mark data ineligible and disconnect before silently dropping required observations. Record the affected interval and recover explicitly. |
| Restart/reconnect | Obtain a new epoch; revalidate clock and instruments; establish new subscriptions; obtain new quotes; repair candle coverage. Old persisted quotes do not become current merely because the process restarted. |

Respect the documented 24-hour connection lifetime, server shutdown events, ping/pong behavior and control-message limits. Rotate connections before expiry with a bounded overlap and deduplication. The documented limits include five incoming control/ping/pong messages per second, 1,024 streams per connection and 300 connection attempts per five minutes per IP. [WebSocket connection requirements](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/web-socket-streams.md)

Use capped exponential backoff with jitter. Honor `Retry-After` on 429/418 and account for IP-wide weight headers; do not rotate hosts or identities to evade restrictions. [REST limits](https://developers.binance.com/en/docs/products/spot/rest-api)

Recovery clears only transient feed conditions. It cannot clear account or risk latches.

### Proposed operating bounds

These are **unmeasured engineering proposals**, to be recorded in canonical configuration and evaluated before acceptance:

| Setting | Initial proposal |
|---|---|
| Warm-up | Latest 720 closed hourly bars per symbol; report contiguous count against the reference’s canonical 100-bar requirement, without computing indicators. |
| Automatic recovery | At most 30 days of candle repair per symbol; older missing coverage stays explicit. |
| REST | Maximum 1,000 candles/request, two concurrent requests, application ceiling 120 weight/minute or a lower discovered provider allowance. Clock/instruments take priority over backfill. |
| Refresh | Clock and instruments every 60 seconds; observations requiring either become ineligible when their verification expires after 120 seconds. |
| Clock confidence | Proposed maximum absolute offset 1 second and uncertainty 500 ms; require two successful samples after a detected anomaly. |
| Network limits | REST 5-second connect/read timeouts and 15-second total deadline; 2 MiB response cap. WebSocket 256 KiB message cap and explicit handshake/close deadlines. |
| Retry | At most five attempts per operation; backoff capped at 60 seconds, followed by a visible cooldown. Provider-directed waits take precedence. |
| Queue/write batch | At most 4,096 events or 8 MiB; batches of at most 100 events or 100 ms. Excessive queue age invalidates current-data eligibility. |
| Runtime | Worker ceiling 1 CPU, 512 MiB and 128 PIDs, subject to measured acceptance. |
| Retention | Seven days of unpinned high-frequency evidence; 730 days of finalized candle revisions; retain referenced instruments, manifests and incidents. |
| Storage | Warn at 4 GiB of market storage; stop collection at 5 GiB rather than threaten financial storage or silently shorten retention. |

Implement bounded retention batches with reference checks, deletion manifests and explicit replay-fidelity reporting. Pinned evidence survives expiry. If pins exhaust the budget, stop collection and report the condition.

Retention supports replay of the captured sampling fidelity only. It must not imply tick-complete, full-depth or executable historical coverage.

## 3. Frontend, dependencies and implementation sequence

### API and UI interfaces

Add authenticated private reads:

- `GET /v1/markets/instruments`
- `GET /v1/markets/{symbol}/quote`
- `GET /v1/markets/{symbol}/candles`
- `GET /v1/markets/health`

Extend the coarse system status without changing existing owner/account response semantics.

New DTOs cover instrument snapshots, quote snapshots, candle pages/revisions, provenance, quality reasons and feed health. Candle requests accept only the two intended symbols and `1h`, enforce a maximum 90-day range and 1,000 rows/page, and use stable cursors with publication-watermark consistency. Unavailable values are `null` with reasons.

All routes require existing service identity plus owner authorization. They read PostgreSQL only. Generate OpenAPI/TypeScript types and validate critical responses with Zod; generated types alone are insufficient.

Add `/markets` and extend `/system` with authenticated feed detail:

- Default to BTCUSDT, UTC 1h, a 30-day window.
- Provide symbol selection and bounded older-history loading up to 90 days/2,160 chart points.
- Show quotes separately from candle closes, including quantities and observation age.
- Include a paged OHLCV table and gap/incident table as accessible alternatives.
- Preserve loading, empty, disabled, unavailable, stale, partial-history and recovered states.
- Show actual acquisition mode and limitations. Do not add performance or recommendation claims.

Keep the existing request-scoped SSR QueryClient and stable browser client. Query keys and Router loader dependencies include all result-defining inputs. Use private/no-store responses, existing session handling and cache clearing on authentication changes. [Start/Query integration](https://tanstack.com/start/latest/docs/framework/react/guide/tanstack-query)

Use feature-local polling: quotes/health every 2 seconds and candle snapshots every 5 seconds while visible. Select short feature-local cache freshness to avoid redundant hydration reads; retain application-wide defaults. Bound retry behavior and never retry authentication/validation failures automatically.

Forward Query cancellation signals through Start transport and any supported downstream request boundary. Preserve bounded server timeouts where cancellation cannot propagate. Identity checks remain mandatory even when cancellation works. [Query cancellation](https://tanstack.com/query/latest/docs/framework/react/guides/query-cancellation)

### shadcn and chart integration

**OBSERVED:** The installed official shadcn skill was read. Cached CLI `4.21.0` project discovery succeeded and confirmed `b2fms61Bqi`, TanStack Start, Base UI, `base-nova`, mist, Lucide and 13 installed primitives. Pointer CSS remains present.

Registry search returned “No registries are configured”; direct `view @shadcn/toggle-group` and component documentation discovery succeeded. Reuse existing Card, Alert, Empty, Badge, Table, Button, Skeleton and Spinner. Add only official Toggle Group and its Toggle dependency after reviewing the CLI diff. Use Base UI’s actual selection API, not a copied Radix example. [Toggle Group](https://ui.shadcn.com/docs/components/base/toggle-group), [Base UI API](https://base-ui.com/react/components/toggle-group)

**Prerequisite:** No installed Lightweight Charts skill was found. Its [official upstream SKILL.md](https://github.com/tradingview/lightweight-charts/blob/master/.github/skills/lightweight-charts/SKILL.md) was located and read for planning. During authorized authoring setup, install it using the documented command:

```powershell
pnpm dlx skills add tradingview/lightweight-charts --skill lightweight-charts
```

Confirm active-client discovery, source revision and the locked package’s installed declarations before chart implementation. No installation is authorized by this planning request. Exact package API compatibility remains provisional until that inspection.

For locked Lightweight Charts `5.2.1`:

- Dynamically load within a client-only React boundary; render accessible SSR content and a stable placeholder.
- Create one chart per mounted container and add the v5 candlestick series.
- Use `setData` for initial/replaced history and `update` for append/latest-bar changes. Corrections to older history trigger controlled replacement while preserving the viewport.
- Convert canonical decimals to finite numbers only in the rendering adapter. Keep exact strings in Query data and tables.
- Convert UTC milliseconds to chart seconds explicitly; require sorted, unique times and whitespace points for missing bars.
- Label the provisional bar with text as well as styling.
- Use supported automatic sizing; dispose chart, observers, listeners and pending callbacks on cleanup.
- Key the adapter by symbol/timeframe. Clear the previous series immediately on a switch; reject late fetch/import/update callbacks whose generation or identity no longer matches.

These patterns follow the current [v5.2 guide](https://tradingview.github.io/lightweight-charts/docs), [series API](https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesApi) and [React lifecycle example](https://tradingview.github.io/lightweight-charts/tutorials/react/simple).

Include the exact version’s NOTICE attribution and a visible TradingView link near the chart. Preserve Apache-2.0 license/NOTICE material in distributed artifacts. The `v5.2.1` NOTICE was read during planning. [Versioned NOTICE](https://raw.githubusercontent.com/tradingview/lightweight-charts/v5.2.1/NOTICE)

Use semantic preset colors, visible focus, keyboard-accessible controls, restrained status announcements and responsive layouts. New operational forms are unnecessary; retain RHF/Zod for existing applicable forms.

### Dependency decisions and evidence

| Dependency | Decision, compatibility and obligations |
|---|---|
| HTTPX `0.28.1` | Promote the already locked development dependency to runtime for pooled public REST requests. MIT; preserve notices. Use explicit timeouts, limits and disabled environment proxies. [Official guidance](https://www.python-httpx.org/advanced/timeouts/) |
| websockets `17.0.1` | Proposed new runtime dependency; existing runtime dependencies lack the required client. Official metadata supports Python ≥3.11, including 3.13; BSD-3-Clause. Use documented asyncio client limits and explicit proxy/reconnect behavior. Docker compatibility remains untested. [Release metadata](https://pypi.org/project/websockets/17.0.1/), [client API](https://websockets.readthedocs.io/en/stable/reference/asyncio/client.html) |
| Router ESLint `1.162.0` | Proposed development addition, required by the library policy. Official npm metadata declares MIT and ESLint 10 compatibility. [Official integration](https://tanstack.com/router/latest/docs/eslint/eslint-plugin-router) |
| React Hooks ESLint `7.1.1` | Proposed development addition for chart lifecycle/hooks. Official npm metadata declares MIT, Node ≥18 and ESLint 10 compatibility. [Official rules](https://react.dev/reference/eslint-plugin-react-hooks) |
| Existing frontend | Preserve Start `1.168.58`, Query `5.104.0`, Table `9.2.4`, React `19.3.0`, Zod `4.6.5`, RHF `7.89.0`, Base UI `1.8.0` and Charts `5.2.1`. Verify installed declarations after frozen Docker setup; do not upgrade to match examples. |

Reuse existing PostgreSQL, SQLAlchemy, Alembic, pytest, Hypothesis, Vitest and Playwright. Retain Query ESLint; inspect effective type-aware coverage for new modules using the already locked TypeScript ESLint tooling. Do not add an exchange SDK, retry framework, broker, database, chart wrapper or second UI kit.

### Ordered implementation and proposed files

The owner authorized the M2 implementation after this review. The numbered sequence remains the execution outline.

1. **Establish isolated tooling and prerequisites.** Save this reviewed plan, reconfirm HEAD, install/discover the chart skill, inspect installed APIs and complete dependency/license records.
2. **Update canonical contracts.** Put market semantics in MARKET_DATA/DATA_CONTRACTS/API_CONTRACTS, operational defaults in CONFIGURATION/OPERATIONS, and grants/network changes in SECURITY/DOCKER.
3. **Add persistence and grants.** Create `C:\Users\owner\repos\adaptive-spot-lab\services\engine\alembic\versions\0003_market_data.py`; extend database identity/readiness handling without changing M1 financial tables or historical migrations.
4. **Implement ingestion.** Add `C:\Users\owner\repos\adaptive-spot-lab\services\engine\app\market_data\` for adapter, validation, repository, quality, worker, retention and bounded smoke entrypoints. Add the worker service, scoped secret, egress and resource configuration.
5. **Implement read APIs and contracts.** Add market DTOs/routes, regenerate OpenAPI/types, and retain the private service/owner boundary.
6. **Implement the UI.** Add `C:\Users\owner\repos\adaptive-spot-lab\apps\web\src\markets\`, market routing and system-health composition. Regenerate the Router tree through containerized tooling.
7. **Add verification tooling.** Extend engine/web tests and add deterministic fixture-provider support, migration/recovery scenarios and the isolated acceptance wrapper described below.
8. **Run gates, review and document.** Record actual commands, outputs, hashes, browser evidence and exclusions. Preserve M0/M1 records. Stop after M2 review; do not automatically publish or begin M3.

## 4. Verification, isolation and recovery

### Requirement-to-test mapping

| Requirements / acceptance IDs | M2 evidence |
|---|---|
| P01/P02 — A01, scoped | Fixed public endpoints, symbol/status/filter validation, rejected credentials/private paths and denied worker financial writes. Execution/direction controls remain M3. |
| P06 — A06; data-related A34 | Provenance, exact decimals, finality, duplicate/order/conflict cases, point-in-time publication, gaps, backfill distinction and destination controls. Broader narrative-source controls remain later. |
| P09 — A04 preservation, A05 | Skill evidence, preset preservation, SSR isolation, Table integration, chart lifecycle/attribution, cancellation, responsive/accessibility checks and effective lint rules. |
| P10 — A03/A12, scoped | Docker worker lifecycle, fencing, schema migration, truthful health, resource bounds, restart and isolated restore. Later execution/agent recovery remains open. |
| P03/P05 — A02/A07 regression portions | Existing funding/accounting suite plus unchanged financial-state checks across ingestion, migration and restore. No claim about fills or fees. |
| P12 and operational P20 portions | Honest unknown/stale/backfilled/fixture labels and bounded collection. No strategy-performance, agent-resilience or research-saturation claim. |

Do not check an entire A-row merely because its M2 subset passes.

### Required scenarios

- Clearly labeled synthetic fixtures with deterministic clocks and seeds; separately retained public samples with source, capture time, schema and hash.
- Decimal round trips, UTC units, missing event timestamps, malformed numerics, OHLC violations, zero displayed liquidity and unsupported instrument/filter states.
- Provisional-to-final transitions, REST boundary conditions, missing bars, revisions and availability-watermark isolation.
- Duplicate, delayed, out-of-order and conflicting events; silence with a connected socket; ping/pong, forced rotation, shutdown events, 429/418 and bounded retries.
- Two worker contenders, expired fencing epochs, crashes around both persistence/publication phases, database interruption, restart checkpoints and queue/storage pressure.
- Real PostgreSQL migration from `0002_m1_account`, with synthetic owner/session, funding, journal, reservation and latch state captured before migration and compared afterward.
- M0/M1 regressions, both generated-contract drift checks and production builds.
- Browser SSR/hydration, authenticated access, expiry/cache clearing, all market states, 390×844 and 1440×900 layouts, keyboard/focus, contrast, screen-reader review and exact-value table alternatives.
- Rapid BTC→SOL→BTC changes with delayed/reversed responses; import completion after unmount; Strict Mode lifecycle tests; repeated resize/navigation; corrected history and recovery.
- Backup/restore of financial history and market evidence with checksum, reconciliation and publication-reference checks.

Public smoke checks remain separate from routine tests. They must verify actual status/filter schemas, both intended symbols, clock behavior, REST candles and both stream types. Include an explicitly invoked observation across an hourly close, bounded to 3,700 seconds. Failure or inaccessible public service leaves provider acceptance **open**.

### Q01–Q10 acceptance matrix

| Gate | Applicability and concrete acceptance | Planned evidence / exclusions |
|---|---|---|
| Q01 | Applicable: complete markets and feed-health journeys, including partial history and recovery. | Real-service browser traces/screenshots for every specified state and both viewport sizes. |
| Q02 | Applicable: keyboard, focus, labels, contrast, non-color status and chart alternatives meet the scoped WCAG 2.2 AA target. | Automated browser assertions plus manual keyboard/screen-reader review. An unperformed manual check remains open; no blanket certification. |
| Q03 | Applicable: exact data, versioned finality, atomic publication, fencing and no financial changes. | Real PostgreSQL, property, concurrency and migration tests. Broker/risk mathematics excluded as M3. |
| Q04 | Applicable: dual authorization, bounded inputs, destination controls, redaction and least-privilege worker. | Abuse tests, role/mount/network inspection and scoped ASVS 5.0.0 mapping in SECURITY. No whole-application security certification. |
| Q05 | Applicable: honest freshness, bounded recovery, cancellation and correct symbol identity under races. | Fault fixtures, DB/network interruption, reconnect/restart and browser late-response tests. |
| Q06 | Applicable: declared ingestion, storage, API and browser budgets met on recorded hardware. | Measurements below, browser performance traces and resource reports. No population-level field-performance claim. |
| Q07 | Applicable: frozen Docker lint/type/unit/property/integration/browser/build and drift checks pass. | Exact commands, exit codes, test counts and reports; required tests may not silently skip. |
| Q08 | Applicable: useful worker/feed health, lag, coverage, clock, retry, queue and storage visibility. | Assertions against persisted incidents, API/UI output and redacted structured logs. Alerts remain local. |
| Q09 | Applicable: M1→M2 migration, restart, backup/restore and compatible rollback preserve history. | Isolated migration/restore manifests, checksums, reconciliation and disabled-ingestion fallback test. |
| Q10 | Applicable: maintainable boundaries, verified integration choices, licenses and operator documentation. | Diff review, source/version register, installed API checks and updated canonical documents. |

### Measurement plan

Declare these workloads before execution and retain failures:

- **Normal synthetic collection:** two symbols, ticker snapshots once/second and kline updates every two seconds for 60 minutes.
- **Burst:** 100 valid events/second for five minutes, followed by a stalled writer and recovery.
- **Retention/storage:** representative seven-day replay, measured table/index/WAL growth, bounded cleanup and pinned-evidence exhaustion.
- **API:** 100 sequential bounded market reads plus five concurrent readers.
- **Browser:** 30 market navigations/symbol switches and 50 mount/unmount cycles at the two declared viewports.

Initial acceptance budgets:

- Receipt-to-publication p95 ≤250 ms and p99 ≤1 second under normal synthetic load.
- Worker memory below its 512 MiB ceiling; no sustained growth after repeated recovery.
- Warm bounded market API p95 ≤250 ms; warm SSR p95 <1,500 ms.
- Market chart visible within 1.5 seconds after its data resolves; cached symbol interaction p95 ≤200 ms.
- Lab LCP ≤2.5 seconds and CLS ≤0.1; record interaction timing without presenting it as population-level INP.
- No leaked charts/listeners, unbounded queue growth, silent observation loss or retention of broken references.

Measure source-to-receipt latency separately during the public smoke run. Report remote-network limitations rather than attributing them to local processing.

### Proposed commands and new harness

The current generic test helper uses shared fixed resources. M1 mutation tests also require `asl_m1_` database names, and its browser journey requires `asl_m1_browser_`.

Create `C:\Users\owner\repos\adaptive-spot-lab\tools\m2-acceptance.ps1` with these exact phase names. This was the review-time requirement; the implementation record below describes the created script and actual results. It must:

- Create distinct engine, browser, recovery/performance and public-smoke Compose projects per run ID.
- Use compatible names such as `asl_m1_m2_20260927a_engine` and `asl_m1_browser_m2_20260927a`, preserving existing guards.
- Generate fresh task-specific secrets and volumes; select and record unused loopback ports and nonoverlapping subnets.
- Reject normal projects/databases and unexpected preexisting resources.
- Use a test-only Compose override and fixture provider without public egress for ordinary tests.
- Require an explicit PublicSmoke phase for public connectivity.
- Save sanitized results under the run’s ignored evidence directory; fail if required scenarios were skipped.
- Stop only manifest-owned resources and never delete volumes as routine cleanup.

All following commands are **PROPOSED**, from `C:\Users\owner\repos\adaptive-spot-lab`:

```powershell
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Prepare
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Build
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Generate
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Checks
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Regression
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Browser
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Recovery
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Performance

# Separate, explicit public-provider verification:
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase PublicSmoke

& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Report
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Stop
```

The wrapper must record its fully resolved commands. Its check phases derive from the existing command contract:

```powershell
# $m2Project and environment are supplied by the validated run manifest.
docker compose -p $m2Project --profile tools build web-tools engine-tools

docker compose -p $m2Project --profile tools run --rm web-tools pnpm --filter web lint
docker compose -p $m2Project --profile tools run --rm web-tools pnpm --filter web typecheck
docker compose -p $m2Project --profile tools run --rm web-tools pnpm --filter web test:unit
docker compose -p $m2Project --profile tools run --rm web-tools pnpm --filter web api:check
docker compose -p $m2Project --profile tools run --rm web-tools pnpm --filter web build

docker compose -p $m2Project --profile tools run --rm engine-tools uv run --frozen ruff check .
docker compose -p $m2Project --profile tools run --rm engine-tools uv run --frozen python -m app.export_openapi --check

docker compose -p $m2Project --profile test run --rm engine-tests
docker compose -p $m2Project --profile test run --rm browser-tests
```

Add targeted formatting and effective ESLint-configuration checks for changed files. Update the existing API-generation helper to accept the isolated project explicitly; retain limited authoring output mounts and rebuild tooling after generated changes.

Recovery must explicitly exercise the predecessor before upgrading:

```powershell
docker compose -p $m2Project up -d postgres
docker compose -p $m2Project run --no-deps --rm migrate alembic -c /app/alembic.ini upgrade 0002_m1_account
# New guarded fixture/snapshot helper seeds and records synthetic M1 state here.
docker compose -p $m2Project run --no-deps --rm migrate alembic -c /app/alembic.ini upgrade head
```

Create the missing guarded migration/recovery helpers, fixture scenarios, market performance script and public-smoke entrypoint as implementation work. Host PowerShell orchestrates Docker stop/kill/restart tests; no container receives a Docker socket.

### Rollback and preservation

M1 readiness checks exact revision equality with `0002_m1_account`; therefore an unchanged M1 image is **not** a valid application rollback against schema `0003_market_data`.

Use a tested schema-compatible release with market collection disabled as the first fallback. Preserve M1 functionality and all data while repairing M2 forward. Do not downgrade or delete the market or financial history.

Before an eventual owner-environment upgrade, create a protected backup outside the database volume. Rehearse restoration only into a fresh isolated database, verify financial reconciliation and evidence checksums, and preserve any history accumulated after the backup. This plan does not authorize deployment to the normal environment.

## 5. Documentation, decisions and definition of done

Update canonical MARKET_DATA, DATA_CONTRACTS, API_CONTRACTS, CONFIGURATION, FRONTEND, DOCKER, OPERATIONS, SECURITY, LIBRARIES and TESTING documents alongside implementation. Record official source/version evidence in INTEGRATION_EVIDENCE, exact commands/results in COMMANDS, milestone status in STATUS, and scoped acceptance evidence in ACCEPTANCE_CHECKLIST. Preserve earlier plans, measurements and historical approvals.

Record these decisions in the living ExecPlan:

- One worker-owned connection and database-backed ingestion.
- Timestamped sampled top-of-book quotes; depth/trades deferred until justified by M3.
- Immutable evidence/revisions and conservative publication availability.
- Bounded polling through the existing authenticated BFF.
- Proposed operational budgets remain unmeasured until tested.
- Missing chart-skill installation and installed declaration inspection are UI prerequisites.
- Fees, execution fidelity approval, strategy/risk activation and model authentication belong to later milestones.
- No genuine owner decision currently blocks independent M2 implementation planning.

M2 is done only when its implemented behavior, applicable Q01–Q10 conditions, required browser/manual checks, isolated migration/recovery and explicit public-provider checks have supporting evidence. An inaccessible provider or unresolved chart prerequisite prevents the corresponding completion claim.

**Implementation stopping rule:** keep M2 unpublished while any applicable Q01–Q10 gate remains open. Preserve the code and isolated evidence. Stop before M3 broker, strategy or forward-experiment work.

**Subsequent owner delivery instruction — 2026-09-27:** The owner explicitly requested pushing the current changes to `main` after the incomplete acceptance report. This overrides the publication hold only. The six open gates, disabled-by-default collection setting and no-owner-stack-activation boundary remain in force. Publish with the incomplete status and retained evidence visible to reviewers.

## 6. Living implementation and run record — 2026-09-27

**IMPLEMENTED, pending full acceptance:** Forward-only `0003_market_data`; scoped market-worker role and secret; raw evidence, exact observations, two-phase fenced publication, watermark reads, feed/incident/retention state; fixed unauthenticated Binance Spot REST/WebSocket adapter; optional disabled-by-default worker; authenticated market APIs and `/markets` chart/table UI; generated OpenAPI/types; isolated fixture and acceptance wrapper. No order, fill, valuation posting or agent runtime was added. Public worker activation was confined to an isolated acceptance project; the normal owner stack and its data were not used for tests.

**OBSERVED baseline:** `main` at `4c928bff0fdf98def95f61ad4e4a085ae2742e24`, initially clean. All code and tests were run in task-specific Compose projects listed in ignored `.cache/m2/` manifests. Synthetic browser/performance observations are explicitly labeled. The chart and shadcn authoring skills were read; installed chart v5.2.1 declarations, CLI preset `b2fms61Bqi`, Base UI Toggle Group API and locked dependency integrations were inspected. Relevant official sources are in [INTEGRATION_EVIDENCE.md](../../INTEGRATION_EVIDENCE.md).

**VERIFIED so far:** The isolated PostgreSQL regression after stream batching, transport/concurrency and market-route authorization additions passed 42 tests, with one Starlette dependency deprecation warning. Frozen Docker lint, type, frontend unit, API drift, Ruff, OpenAPI drift, formatting and production build checks passed on the current source after intermediate formatting/lint fixes. The predecessor M1→M2 migration retained synthetic M1 table fingerprints. A disposable M2 dump/restore matched table fingerprints and financial reconciliation (`10225.25000000` virtual cash, no reservation); worker-disabled fallback and API restart/readiness passed after waiting for health. A fresh disposable browser project passed the full M1 normal suite and M2 live, unavailable and recovered states with an updating provisional candle. A separate fresh browser database passed the disabled empty-feed/no-quote state. A failed market read showed an error and made the cached quote unusable, then recovered when reads resumed. Keyboard selection, heading/table accessibility tree, heading contrast and 390-pixel layout passed. Browser timing measured 30 switches and 50 chart mount cycles at each viewport: desktop chart visible 265 ms, switch p95 144 ms, warm SSR p95 114 ms, lab LCP 148 ms, CLS 0; mobile 266/146/79/156 ms and CLS 0. Authenticated in-process private API measured 100 sequential reads at p95 11.615 ms and 100 five-way reads at p95 57.465 ms. The declared 60-minute synthetic normal run published 10,800/10,800 events with p95/p99 60.300/79.613 ms and 66,984 KiB peak process RSS; its following five-minute 100-events/second burst published 30,000/30,000 with p95/p99 65.449/77.298 ms and 67,032 KiB peak RSS. A final-image five-minute burst again published 30,000/30,000 with p95/p99 70.711/83.359 ms and then recovered one persisted-but-unpublished observation after 2.049 seconds. A seven-day **five-minute sampled** synthetic replay stored 4,032 quotes and 336 final candles, then logically pruned 594 records while preserving a pin and zero broken payload references; table/index/WAL bytes are in the ignored run log. Physical relation size increased slightly after pruning, so this is not evidence that PostgreSQL immediately reclaimed disk. Public read-only smoke observed both symbols, required filters, finalized REST candles and both stream types on 2026-09-27; a separately invoked hourly-close observation completed at 17:00 UTC after 1,895.877 seconds. A separate bounded isolated public-worker activation published 1,440 public historical candles and live quotes/provisional bars for both symbols, survived a short disposable PostgreSQL outage by acquiring a new lease epoch and reconnecting, then was stopped. The worker had no host port, repo bind, account secret or financial-table rights. This is point-in-time integration evidence, not owner-stack activation.

**Open verification:** The original 10-second synthetic burst delivered 1,000/1,000 events but accumulated about five seconds of schedule lag; bounded stream batching corrected the schedule lag before the passing full-duration workloads. The sampled seven-day replay is lower density than the declared normal one-second feed; extrapolated full-density storage is not a measured replay. A manual screen-reader review, browser loading/late-symbol-response case, forced WebSocket disconnect/23-hour rotation and pinned-evidence budget exhaustion remain unperformed. The isolated database interruption passed, but a provider/network interruption has not been fault-injected. Queue-depth visibility is not implemented beyond the transport's bounded internal receive queue. No whole-WCAG, whole-ASVS or profitability pass is claimed. Six applicable Q01–Q10 gates remain open; the later owner request authorizes publication without treating them as passed.

### Assessed M2 quality gates — 2026-09-27

`VERIFIED` below means the scoped M2 condition described in the matrix above has supporting local evidence. It does not check a full A01–A38 outcome or certify the application for trading.

| Gate | Result | Evidence and remaining condition |
|---|---|---|
| Q01 | **NOT RUN** | Actual desktop/mobile live, empty, partial, error, unavailable and recovered journeys passed with retained screenshots. A deliberately delayed loading journey and late symbol response were not verified in the browser. |
| Q02 | **NOT RUN** | Keyboard symbol selection, focus, chart text/table alternative, heading/table accessibility tree, heading contrast and 390-pixel layout passed. Manual screen-reader and full scoped contrast/focus review were not run. |
| Q03 | **VERIFIED** | Exact Decimal/property parsing, real PostgreSQL fencing, two-phase publication, conflict/duplicate/finality, watermarked reads, retention pins and M1 financial-state preservation passed in the 42-test suite and isolated migration/restore. No M3 broker or profitability claim. |
| Q04 | **VERIFIED** | Four market routes denied missing service/owner identity; private DNS, signed paths, redirects, body bounds and worker financial-table grants were negative-tested. Public worker inspection showed no privileged mode, host bind/port or non-market secret; generated secret values were absent from task logs. Scoped ASVS mapping is in [SECURITY.md](../../SECURITY.md); no penetration-test claim. |
| Q05 | **NOT RUN** | Browser fixture outage/recovery and failed-refresh recovery passed; real public worker regained lease epoch 2 and stream after isolated PostgreSQL interruption. Forced provider/network disconnect, 23-hour stream rotation and delayed prior-symbol response remain untested. |
| Q06 | **NOT RUN** | Declared 60-minute normal and two five-minute bursts, API/browser timings and sampled seven-day replay passed their measured bounds. A normal-density seven-day storage replay, pinned-evidence cap exhaustion and repeated recovery memory-growth measurement were not run. |
| Q07 | **NOT RUN** | Frozen Docker lint/type/unit/format/OpenAPI/API-drift/build, 42 PostgreSQL tests and scoped Chromium journeys passed. Applicable delayed-response, rotation and full-density failure tests identified above remain unrun. |
| Q08 | **NOT RUN** | Feed/clock/lag/incident/storage views and structured worker status were inspected. Transport queue depth/age is not exposed as a measured health metric; local alert response under saturation was not verified. |
| Q09 | **VERIFIED** | Actual predecessor migration retained synthetic M1 fingerprints; isolated M2 dump/restore preserved market fingerprints and reconciled cash/reservations; disabled-ingestion fallback, API restart and worker DB-interruption recovery passed. Normal owner data was untouched. |
| Q10 | **VERIFIED** | Official integration/locked-version and license evidence, shadcn discovery, code/diff review, canonical contracts and operator recovery guidance were updated. The final source review found and fixed the cached-quote usability error. |

**Task-resource disposition:** Manifest-owned `Stop` completed with exit 0 for `a`, `b`, `c`, `d` and `e`. A final M2-container inventory was empty. Task Compose containers and networks were removed; named volumes and ignored `.cache/m2/<run-id>/` evidence were preserved. The normal owner stack was untouched. `git diff --check` reported no whitespace errors (only Windows line-ending conversion warnings). At the end of the initial acceptance run, the M2 changes remained uncommitted and unpushed; the subsequent owner instruction above requested delivery of that incomplete work.

## 7. Completion run record — 2026-09-27

**COMPLETE; automated acceptance passed and manual Q02 closed by owner report.** Completion started from clean `main` commit `434bc98a7b393d023e4351f0bc38b974109d44cf`, remote `https://github.com/MentorAliu/adaptive_spot_lab.git`. Every applicable gate passed before completion delivery. Normal collection and owner deployment remain disabled/out of scope; M3 was not started. The initial M2 run above is preserved as historical evidence. Final measurements completed 2026-09-27 22:11 UTC, or 2026-09-28 00:11 Budapest; the owner reported all Narrator checks passed on 2026-09-28, recorded at 04:00 UTC.

### Implementation and review findings

- Added forward-only `0004_m2_completion`; the published `0003_market_data` migration is unchanged. Collection generations, nullable legacy provenance, measured worker state and immutable candle confirmations are separate from financial authority. Confirmations share the publication watermark; old reads cannot observe future conflict resolutions.
- Added an application receive queue covering queued and in-flight frames, receipt timestamps, maximum-frame reservations, bounded batching, independent control/ingestion executors and database timeouts. Renewal uses an authority `KEY SHARE` lock compatible with expiry-only updates; epoch/owner changes remain serialized by the unique authority key. A separate advisory lock orders semantic decisions and publication commits.
- Implemented reference revalidation and fresh-generation eligibility on recovery; injected-clock 23-hour rotation, provider shutdown handling, two-socket overlap, failed replacement recovery, honest overload/drain-loss incidents and per-attempt REST weight accounting. Production accepts neither a test clock nor arbitrary provider URLs.
- Reworked finalized-candle conflict selection and full-window coverage across pagination. Confirmations preserve earlier revisions; delayed provisional events follow source time. Added indexed bounded retention and hourly pruning without increasing storage, statement or lock limits.
- Extended authenticated OpenAPI/generated TypeScript/Zod contracts together. Sequence IDs remain decimal strings, including values above JavaScript's safe integer range. The BFF validates requested identity and checks its five-second deadline after headers and bodies independently of cancellation.
- Added symbol-specific loading with installed Skeleton/Alert components, queue/conflict/unknown states, chart whitespace and state-change-only announcements. Final screenshot review found that the incidents card declared an empty result while loading; its loading/error states and storage loading were corrected and a browser assertion added.

### Isolated resources and identities

Only manifest-created Compose projects under `.cache/m2/m2-completion-0927[a-f]/` were used. Runs `a`–`d` retain development probes and failures; `e` holds storage, public-network and full-duration performance evidence. Final backend, frozen checks, nonempty migration/restore and public hourly-close follow-ups use `f`. Final frontend follow-ups use `c` so automated owner logins cannot invalidate the `e` Narrator session. Every project has its own credentials, database/volume, subnets and loopback browser port. Runtime containers receive no Docker socket or authoring repository/home mount.

Measured host context: Docker Desktop 29.7.2 on WSL2 kernel `6.18.33.2-microsoft-standard-WSL2`, 16 available CPUs and 8,277,094,400 Docker memory bytes. Worker/performance containers retain the 1 CPU, 512 MiB and 128 PID limits. Capacity preflight required at least 30 GiB free on both Windows and Docker; run `e` observed 788,100,784 KiB free in Docker before growth. These are observations for this PC, not universal capacity claims.

`Snapshot` records SHA-256 for every application/test/tool source and exact Docker image IDs in timestamped `source-images-*.json` files. The separately frozen Narrator source and running image identities are in [the review checklist](../m2-narrator-review.md); image changes require a new binding and affected-row review. Raw logs, Playwright screenshots/traces, source manifests and disposable database/recovery volumes are retained locally in the ignored run directories. No real secret value belongs in committed evidence.

### Intermediate commands and measurements retained

Every command below means `./tools/m2-acceptance.ps1 -RunId <run> -Phase <phase>` from the repository root. Per-phase logs record resolved Docker arguments, output, exit code and UTC completion; outer attempt logs preserve failed invocations. Required scenarios fail the wrapper if skipped.

| Check | Actual evidence | Result |
|---|---|---|
| Worker faults | `e/worker-faults.log`, latest 18 tests in 35.39 s | Exit 0. Real WebSockets/parser/store/PostgreSQL; socket close, silence, shutdown, injected rotation, malformed/oversized frames, conflicts/order, byte/age overload, writer lock timeout, lease loss, retry-after, failed replacement and fresh worker restart. |
| Backend regression | `e/engine-tests.log`, latest 61 tests in 39.61 s | Exit 0. Unit/property/PostgreSQL/auth/grants/financial preservation; one recorded Starlette TestClient `httpx` deprecation warning. |
| Frozen web/engine checks | `e` Checks after independent deadline fix | Exit 0: lint, types, 15 unit tests in five files, API/OpenAPI drift, Ruff, formatting, production build. Final loading follow-up checks run separately in `c`; see final gate assessment. |
| Browser identity/loading | `e/browser-races.log` | Four cases passed, both 1440×900 and 390×844. Native cancellation produced three aborted requests per viewport; deliberately uncooperative fetch produced zero, with late symbol/history results still rejected. Back/forward, authentication cache clearing and chart cleanup passed. |
| Browser state journeys | `e/browser-market-{live,unavailable,recovered}.log`, `browser-error-test.log`; `d/browser-empty-test.log` | Live, unavailable, recovered and failed-read states passed. Empty/disabled feed passed on a separate fresh database. M1 normal browser foundation/funding suite passed before the final deadline tightening; its on-time/error semantics and sign-in/out were revalidated by unit and browser tests. |
| Queue/conflict presentation | `c/browser-health-states.log` | Synthetic response-state check passed: warning, overload, unknown telemetry, recovery, explicit unresolved interval/table omission and one chart at desktop/mobile sizes. This is UI evidence; worker and store correctness are tested independently. |
| Automated accessibility | `e/browser-accessibility.log` | Keyboard focus/selection, names/headings, table/columnheader tree, non-repeating live text, CSS 200% layout and 390-pixel layout passed. Actual Narrator speech/keyboard review remains separate and unrun. |
| Worker recovery memory | `e/recovery-memory.log` | Five warm-up plus 30 measured in-process disconnect/rotation/overload recoveries. Baseline 70,612 KiB, maximum settled 70,624 KiB, growth 12 KiB; settled queues empty, no retained market tasks, all below 512 MiB. |
| Browser timing/memory | `e/browser-performance.log`, 21:23:58 UTC | 30 symbol switches and 50 mounts per viewport after warm-up. Desktop/mobile chart 236/260 ms, switch p95 152/104 ms, SSR p95 92/81 ms, LCP 148/140 ms, CLS 0. One retained document each; desktop nodes/listeners 1521/210 unchanged, mobile nodes 1521→1508 and listeners 210→212 within the declared bound. Heap growth 906,632/1,545,000 bytes, below 10 MiB. A final loading follow-up measurement is recorded separately. |
| Full-density retention | `e/retention-measurement.log`, 21:21:17 UTC | Exit 0, accelerated synthetic COPY with production record shapes: 1,209,600 quotes, 604,800 candle updates, 336 finalized bars. One pin preserved, zero broken references, 525,954 observation/payload deletions across 527 bounded manifests; candle-query p95 17.149 ms. |
| Pinned exhaustion | `e/capacity-measurement.log`, 21:14:48 UTC | Exit 0 on separate volume. Warning at 4,297,596,928 bytes/17,792 pins; stop at 5,380,497,408 bytes/22,272 pins. Real ingestion refused with `STORAGE_LIMIT`; all pins survived, zero broken references, no pruning. No cap raised. |
| Migration/restore/fallback | `e` Recovery and RecoveryM2 | M1→head preserved financial fingerprints; dump/restore retained market and financial fingerprints; reconciliation cash `10225.25000000`, reserved `0`, status OK. Published 0003→0004 preserved legacy quote/pin/account fingerprints. Disabled collector and restarted schema-compatible API readiness passed. |
| Public interruption | `e/public-network-{before,unavailable,recovered}.log` | Only isolated worker market-egress disconnected for 15 s and restored. Health became unusable; recovery advanced epoch 2→4 and collection identity, then fresh quotes became usable. Public collector stopped after the bounded test. |
| Public schema/stream/hour close | `d/public-smoke.log` | Exit 0 after 543.513 s. Both public symbols/instruments/REST schemas and ticker/kline streams observed; both 20:00 UTC bars finalized at 21:00 UTC. Parser/provider source is unchanged in the final worker. |
| Security inspection | `e/security-inspection.json` | Worker read-only/nonprivileged, 1 CPU/512 MiB/128 PIDs, only market password secret, private+egress networks, no host port. 24 public asset files contained no internal-key/path marker; runtime contained no authoring/auth files. Forty generated secret values matched none of 136 task logs in the successful scan. |

Full-density storage measurements (bytes): before tables/indexes/total `90,112 / 368,640 / 458,752`; seeded `1,363,886,080 / 1,036,156,928 / 2,400,043,008`; after real retention `1,364,017,152 / 1,036,189,696 / 2,400,206,848`. WAL growth was `4,987,864,048`; elapsed 956.472 s. Logical deletion did not shrink physical relation files. This accelerated storage fixture does not measure seven days of elapsed operation or public ingestion throughput.

Capacity measurements (bytes): before total `458,752`; at stop tables/indexes/total `5,368,053,760 / 12,443,648 / 5,380,497,408`; WAL growth `5,582,769,392`; elapsed 297.338 s. The capacity worker exercised the actual production stop check; all evidence was synthetic and pinned in a disposable database.

Public finalized-frame SHA-256: BTC `b7ec7639e2b6c9f3887fbb135e5b99dfa60ec6356409ec1c020b9850a106307d`, received `2026-09-27T21:00:00.172574Z`; SOL `5e0b7fc832bb00d5358b5c6ab7dfe12ac1e69cf6ecdb244d5c10617edea9c699`, received `2026-09-27T21:00:00.384100Z`. Public recovery collection `bdd4257f-3f00-4d1e-b01c-07d0b4c241e9` at epoch `4` had both feeds usable at 21:11:36 UTC; the intervening incident retained an unknown unobserved-loss count. These are point-in-time observations, not future availability or execution-quality claims.

### Failed attempts retained and addressed

1. Initial burst probes exceeded the 250 ms p95 budget before batching/feed-update improvements. Short passing probes are historical diagnostics, not substitutes for the final full-duration workloads.
2. Run `b` full-density storage loaded the required records but query p95 was 1,089.873 ms. Partial final/provisional indexes and bounded per-hour provisional selection brought the final full-density result to 17.149 ms.
3. Run `c` retention lost its lease because ingestion held a row lock that blocked renewal. Compatible authority `KEY SHARE` locks plus a unique authority key and independent publication advisory lock fixed this without removing fencing. A concurrent capture/renewal/epoch test passed.
4. Run `d` retention hit the existing two-second statement deadline while searching orphan payloads. Added the received-time/payload indexes, bounded indexed lookup and 500-record batches; run `e` passed unchanged deadlines. No timeout or storage cap was raised.
5. Early regression exposed untyped PostgreSQL JSON parameters and an injected-rotation timing error. Explicit casts and deterministic test synchronization passed subsequent suites. Initial browser race tests logged in concurrently and invalidated the single owner session; serial cases passed. Mixing empty/normal browser fixture passphrases failed in `d`; the harness now guards that database from reuse for the normal journey.
6. `e` predecessor rehearsal initially connected before PostgreSQL accepted connections. Health-waited retry passed and both predecessor paths now wait. Two sandboxed Docker attempts could not read Docker Desktop configuration/connect to its pipe (exit 125); authorized Docker-access retries ran normally. The added deadline unit test initially failed formatting, then passed after containerized Prettier.
7. The first secret-log scan could not open six actively written files. That report is retained as incomplete/exit 1; a shared-read retry scanned all 136 files with zero matches. A preliminary browser probe used the unavailable `playwright` module name; using installed `@playwright/test` succeeded without installing a dependency.

8. Review found that a partly committed stream batch could report every pending frame as uncommitted. The final code reports known `captured_pending` separately from unknown `captured_uncommitted`; unobserved network loss remains unknown. A real PostgreSQL foreign-key lock test commits the BTC subgroup before the SOL subgroup times out, proving that the incident does not fabricate an exact loss count.
9. The earlier restore fixture left the new collection/confirmation tables empty. The strengthened `f` fixture restores four observations, five publications, one collection, one candle confirmation and populated telemetry, with matching fingerprints. A subsequent Ruff import-order failure was corrected and all frozen checks rerun.
10. Rebuilding the performance image tag made the old running image ID unavailable to a new `docker run` comparison. The failed probe is retained; copying the actual worker source from the still-running container and comparing Python ASTs succeeded. Only two failure-log field constructions differ from final worker source; the measured successful path is identical. The final recovery fixture change is test-only and is not imported by the performance workload.
11. Final secret inspection first treated the existing public help label `secrets/owner_setup_key` as a private marker, then initially assumed the wrong runtime Python path. Neither attempt is recorded as a pass. The corrected value/marker scan uses the interpreter on the Dockerfile's PATH and retains both failed reports plus its successful report.
12. Final resource inventory found an earlier run `b` public collector still active beyond its test window. It was stopped at 22:12:22 UTC; Docker reported exit 137 with `OOMKilled=false`, so this is not counted as graceful-shutdown evidence. Its full container log and database volume were retained, and observations outside the bounded test are excluded from acceptance claims. Final-code shutdown/recovery evidence comes from the `f` fault/memory suites and bounded `e` run. No owner-stack resource was involved.

### Final follow-up evidence

The final application source manifest is `f/source-images-20260927T215706208.json`, SHA-256 `1b87cbb2356e3b9e63b7c3e21b0c93b11b980c802294b72b4110a7c08a015329`. It includes exact build-image IDs. The running review services have a separate final binding at `e/narrator-build.json`, using source manifest SHA-256 `3bfdba75a258103cd8842c7e3e523521425199a5d1108a3e73d197d4ebf59b31`. Documentation-only evidence updates follow these application snapshots.

| Follow-up | Actual final result |
|---|---|
| Worker faults and backend | `f/worker-faults.log`: **19 passed**, 35.40 s, exit 0 at 21:54:38 UTC. `f/engine-tests.log`: **62 passed**, 39.54 s, exit 0 at 21:55:28; one existing dependency deprecation warning. |
| Frozen verification | `f` lint, types, 15 frontend unit tests, generated API/OpenAPI drift, Ruff, formatting and production build all exited 0; last build completed 21:57:05 UTC. No required test skipped. |
| Final loading and browser | `c` final live/unavailable/recovered, errors, four race cases, accessibility and synthetic health/conflict cases all passed. Manual screenshot review confirmed loading in all cards, visible text for unresolved gaps and responsive table containment. |
| Browser performance | `c/browser-performance.log`: desktop/mobile chart 244/253 ms, cached switch p95 153/100 ms, SSR p95 85/84 ms, LCP 140/140 ms, CLS 0. Each viewport ran 30 switches and 50 mounts after warm-up. Documents stayed 1; nodes stayed 1,521; desktop listeners stayed 210 and mobile decreased 212→210. Heap growth 445,252/1,058,380 bytes, below 10 MiB. |
| Final recovery memory | `f/recovery-memory.log`: five warm-up plus 30 measured disconnect/rotation/overload cycles; baseline 70,356 KiB, maximum settled 70,392 KiB, growth **36 KiB**; empty queues and no retained market tasks. Exit 0 at 21:56:11 UTC. |
| Nonempty restore and both migrations | `f` M1→head and 0003→0004 preserved financial fingerprints. The populated completion tables matched after dump/restore; reconciliation was `10225.25000000` cash, `0` reserved, `OK`. Disabled collection and restarted schema-compatible API passed. The legacy quote/pin retained explicitly unknown capture provenance. |
| Final public recovery | `e` only-worker market-egress interruption produced unusable health, then epoch **6→7** and new collection `882624f6-da18-46ff-b093-d843a60a28dc`, fresh eligible quotes, empty queue and measured publication lag 141.465 ms at 21:58:15 UTC. Public worker stopped afterward. |
| Final public hour close | `f/public-smoke.log`: both instrument/REST/stream schemas passed and both 21:00 UTC bars finalized at 22:00 UTC. Elapsed 203.182 s, exit 0 at 22:00:06 UTC. BTC frame SHA-256 `f08b6e980a6f8150e6639a6dc8a08f508398c79fd81fab7b358720a81e4233e2`; SOL `83907af5075cba3e38e33c1e546c21eceb14137685c52cc71a5db44cacc2890e`. Source-to-receipt samples were approximately 119–120 ms, separate from local performance. |
| Final security inspection | `f/security-final.json`, exit 0 at 22:13 UTC: 225 generated secrets, 495 task logs, zero matches; 24 client assets, zero private markers/actual internal key; zero runtime authoring/auth files. Fixed worker limits, secret-only read-only mount, no published ports and stopped final public worker verified. The earlier 22:08 scan is retained separately. |

Recovery archives are retained outside their database volumes. `f/backups/asl_m2.dump` is 86,253 bytes, SHA-256 `380666e93688800fb30a8e37c08ae5018dee9d3507d206a7c01b339502cb9edc`; the earlier `e` dump is 84,795 bytes, SHA-256 `60923bf4abfd94db33bbdc9662bede2207837613dbcc3eb69163b94dde0c3bcc`. Their restored disposable volumes are also retained.

The 60-minute normal run completed with **10,800/10,800** events published, elapsed 3,600.057 s, receipt-to-publication p95 **168.088 ms**, p99 **197.293 ms**, scheduling p99 2.129 ms, maximum RSS 69,804 KiB, CPU 93.354 s and storage growth 14,876,672 bytes. Its worker image was `sha256:430db3ad4f7ae1344c32bdbdb056067cf336dfa22bb6e3536e2ceb469773eb84`; the failure-metadata-only difference described above is explicit, not a claim of identical binaries.

The final five-minute burst published **30,000/30,000** events at the declared 100 events/second, elapsed 300.079 s, publication p95 **177.961 ms**, p99 **192.801 ms**, scheduling p99 2.041 ms, maximum RSS 72,352 KiB, CPU 74.381 s and storage growth 29,450,240 bytes. Image `sha256:c8d4a9a0dae89fc4fbe2a68ad303850179edf2c22ff9d186269054e759d28e2a` contains the final worker source. Both workloads settled with empty queues and exited 0. The separate final fault and memory suites cover stalled writing and recovery.

The final authenticated in-process ASGI API measurement performed 100 sequential reads and 100 reads across five concurrent workers: p95 **16.346/89.189 ms**, concurrent p99 98.435 ms, exit 0 at 22:11:31 UTC. This includes the real PostgreSQL read path, not external-network HTTP timing; SSR/browser measurements are separately recorded above. All declared local budgets passed.

### Final Q01–Q10 reassessment

All ten gates apply to the changed M2 scope. Future broker/agent execution, owner deployment, a complete WCAG audit and full ASVS assessment remain outside this milestone; those exclusions do not waive an applicable M2 condition.

| Gate | Final result | Condition and supporting evidence |
|---|---|---|
| Q01 | **VERIFIED** | Requested-symbol loading, empty, live, partial/conflicting, error, unavailable and recovered journeys; 1440×900 and 390×844 browser screenshots, state/race tests and final visual review. |
| Q02 | **VERIFIED, scoped; manual findings owner-reported** | Automated keyboard, focus, names/headings/table semantics, non-color cues, announcement stability, responsive/200% layout and chart alternatives passed. N01 PASS was recorded 03:53 UTC; all N01–N09 PASS was recorded 04:00 UTC on 2026-09-28 against unchanged running images. Browser: Chrome by owner report; version/voice were not supplied. The bound checklist preserves this reproducibility limit and does not claim complete WCAG conformance. |
| Q03 | **VERIFIED** | Final 62-test regression and 19 targeted fault cases prove exact transport, fencing/concurrency, generation provenance, conflict publication ordering, delayed provisional handling and pagination coverage. Full-density retention/pins/references and unchanged financial reconciliation passed. |
| Q04 | **VERIFIED, scoped** | Final auth/grant/input/provider-boundary tests and runtime/client/log inspection; ASVS mapping and limits remain in SECURITY. No financial/owner grant expansion, secret leak or unrestricted runtime transport introduced. |
| Q05 | **VERIFIED** | Actual worker reconnect/rotation/shutdown/rate-limit/overload/stall/lease/restart paths, late and uncancellable BFF/browser responses, current-generation eligibility and isolated public-network recovery passed. |
| Q06 | **VERIFIED, measured scope** | Full elapsed normal and final-image burst, API/SSR/chart/interaction budgets, five-plus-30 worker recoveries, 30 browser switches/50 mounts, seven-day full density and real 4/5 GiB pinned thresholds passed. Normal-image failure-log-only difference is disclosed above with AST equivalence evidence. |
| Q07 | **VERIFIED** | Final frozen Docker lint/format/types/unit/property/PostgreSQL/browser/build and contract-drift checks passed without required skips. Failed attempts and corrected reruns remain available. |
| Q08 | **VERIFIED** | Queue capacity/age warnings and overload, unknown old telemetry, lease invalidation, storage-stop, outages and recovery were observed through real worker/API tests and browser state displays. Partial-commit outcome and network loss remain explicitly unknown when unprovable. |
| Q09 | **VERIFIED, isolated** | M1→head and published 0003→0004, nonempty backup/restore fingerprints, reconciliation, grants/readiness, disabled-collector fallback and fresh Docker builds passed. Owner activation requires its separate backup/approval step. |
| Q10 | **VERIFIED** | Final source review, documented failure fixes, unchanged dependencies/locks/preset/published migration, official locked-version integration evidence, canonical contracts and operational commands. Diff whitespace and 138 relative file links in 16 changed documents passed; all 146 application/tool source hashes still match the final tested manifest. |

### Acceptance closure and delivery

The owner reported “all narrator has passed” after receiving the remaining N02–N09 checklist. All rows are **PASS by owner report**, recorded 2026-09-28 04:00 UTC, alongside the earlier N01 record. The owner identified Chrome; browser version, voice and exact execution times remain unreported. The coding tools did not hear speech. All three running web/API/fixture images were reverified unchanged at 04:00:28 UTC, and all 146 tested application/tool source hashes still match the final manifest. This closes the scoped manual condition without converting it into automated evidence.

All gates are now closed. Refreshed `origin/main` and local `main` both resolved to `434bc98a7b393d023e4351f0bc38b974109d44cf` before delivery, with zero divergence. The reviewed completion changes were committed as `4cfb8a4e0ba662cec0a9d8fbcc22f712b8c87ff2` (`Complete M2 market-data acceptance`) and pushed without force to `https://github.com/MentorAliu/adaptive_spot_lab.git`, branch `main`. `git ls-remote --exit-code origin refs/heads/main` matched that commit and `git status --porcelain` was empty at 2026-09-28 04:06:24 UTC. The implementation receipt is retained in `f/delivery-implementation.json`, with the exact push output/exit 0 in `f/delivery-push.log`. Normal owner resources are unchanged and collection remains disabled there.

Cleanup completed at 22:14:10 UTC with exit 0 (`e/cleanup-final.json`). `Stop` removed the task containers/networks for runs `a`, `b`, `c`, `d` and `f`; the same volume-preserving `down --remove-orphans` stopped all `e` projects except its browser review. Final inventory contains exactly its web, API, synthetic fixture and PostgreSQL containers. No task public collector remains running. Named evidence/recovery volumes, protected dump archives and local logs/screenshots/source manifests remain retained. Existing `adaptive-spot-lab`, `m1-test-m5-forward-20260925a` and `paper-trader` resources were untouched.

After the owner's all-pass Narrator report and verified implementation push, the remaining `e` review stack was stopped with `./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase Stop`, exit 0 at **2026-09-28 04:07:16 UTC**. Service logs were saved before removal. Final inventory showed **zero task containers**, all **28 task volumes** unchanged, and both preserved recovery-dump hashes matching their recorded values. `e/narrator-cleanup.json` records these results. The former review URL is now offline. This closeout changes documentation only; the tested application source and all milestone boundaries remain unchanged. M3 was not started.
