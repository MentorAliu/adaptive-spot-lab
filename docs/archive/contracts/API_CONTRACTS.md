# HTTP, event and service contracts

## M12: the routes in use (ExecPlan 0060)

IMPLEMENTED by [ExecPlan 0060](../../plans/0060-spot-trading-only.md) and described by the engine's `openapi.json` (the drift check `python -m app.export_openapi --check`; the web's generated types `pnpm run api:check`). Every route but the two health probes needs the API's internal service key, which only the web's server holds; the browser reaches them through the web's server functions and its `/api/live` route. Unknown query parameters are refused. Every other route of the earlier sections is removed (the futures, perpetual, agent, research, source, coin, experiment, order, position and decision routes); those sections are history.

| Route | Answers |
|---|---|
| `GET /v1/health/live`, `GET /v1/health/ready` | The process and the database's readiness; no key |
| `GET /v1/system/status` | The services' health: the feed, the execution worker, the database's schema |
| `GET /v1/account`, `GET /v1/account/workspace`, `GET /v1/account/requests/{key}` | The account and its funding history (M1) |
| `POST /v1/account/topups/draft`, `POST /v1/account/topups`, `POST /v1/account/topups/{id}/retry`, `POST /v1/account/topups/{id}/cancel` | The owner's top-up: review, confirm by idempotency key, retry, cancel a pending one (M1's semantics, [LEDGER](LEDGER.md)) |
| `GET /v1/market` | Bitcoin's spot book (best bid and ask with their ages), the instrument and the feed's state |
| `GET /v1/market/candles?interval=&limit=` | Candles for the chart: `1m`, `5m`, `15m`, `1h`, `4h` from the stored 1-minute candles, `1d` from the daily candles |
| `GET /v1/spot` | The overview: the account (equity, USDT, BTC and its value, the share in Bitcoin, performance), the run, its limits, today's reading and the next one's time, the feed |
| `GET /v1/spot/trades?cursor=&limit=`, `GET /v1/spot/readings?cursor=&limit=` | The fills and the daily readings, newest first, a page at a time |
| `GET /v1/spot/activity?after=` | The toasts' feed: the fills after a cursor |
| `GET /v1/spot/live` | Server-sent events (ExecPlan 0047's stream): `ready` with the cursor, `activity` for each new fill, `change` for the rest; `Last-Event-ID` resumes |
| `GET /v1/spot/markers?since_ms=` | The buys and sells for the chart's markers |
| `GET /v1/spot/valuations?window=24h\|7d\|all` | The account's value over the window |
| `GET /v1/spot/backtest?window=SINCE_2019\|SINCE_2023\|LAST_12_MONTHS` | The newest stored backtest's window (`READY`, `NOT_COMPUTED` or `SCHEMA_PENDING`): the rule's and holding Bitcoin's totals, a row a year, the daily values and the trades |
| `GET /v1/spot/definitions` | The three definitions with their hashes and the running code's identity |
| `POST /v1/spot/requests` | The owner's `PAUSE`, `RESUME`, `STOP` (Stop and sell) or `START`, by idempotency key and bound to the run the owner saw; the answer is "accepted", and the engine applies it at its next step (`APPLIED` or `REJECTED` with reasons) |
| `GET /v1/spot/requests/{key}` | A request's outcome |

## Boundary design

The browser talks only to the same-origin TanStack Start BFF. The BFF authorizes the local owner and calls the private FastAPI service. The private service also enforces domain authorization/capabilities; private networking alone is not financial authorization. Model runners receive narrow jobs and return proposals, never generic admin endpoints.

Since [ExecPlan 0042](#no-owner-sign-in-execplan-0042) there is no owner sign-in: where a section below names the owner's session (`X-Owner-Session`), the route needs the service key (`X-Internal-Key`) alone, and the BFF on the PC's loopback is the owner.

Use versioned `/v1` routes and an OpenAPI schema generated from implemented backend DTOs. Generate frontend types; validate untrusted requests and critical responses at runtime. Financial amounts are decimal strings, time values are UTC ISO strings with documented precision, statuses are enums, and unavailable values carry explicit reasons [DATA_CONTRACTS.md](DATA_CONTRACTS.md).

The table below describes the full proposed API surface. M0/M1 routes and the M2 market reads listed immediately below are implemented; other rows remain future work.

## Implemented M2 private market reads

The private service requires both `X-Internal-Key` and `X-Owner-Session` for `GET /v1/markets/instruments`, `/v1/markets/health`, `/v1/markets/{symbol}/quote` and `/v1/markets/{symbol}/candles`. The browser reaches these through authenticated same-origin Start server functions only. Symbol is limited to BTCUSDT/SOLUSDT. Candles use UTC-millisecond `start_ms`/`end_ms`, fixed 1h interval, a 90-day maximum range, a limit of 1–1,000, an optional aligned cursor and a committed publication watermark. Invalid ranges return 422. Responses carry acquisition, exact decimal strings, quality/reason, source/receipt/availability, and sequence. A quote's `executable` is always false; missing or stale observations cannot be disguised as zero or current. OpenAPI and generated web types are updated from implemented DTOs.

The M2 completion DTOs expose `worker` on market health: collection UUID, exact epoch, sample timestamp, queue count/bytes/capacities, oldest age, publication lag, warning and overload state. A sample older than six seconds or tied to invalid lease authority has `known=false` and null measurements/status flags; its retained identity/timestamp is historical context. Current usability also requires matching generation/instrument provenance. Candle responses include full-range `coverage`, `gaps`, `conflicts` and optional confirmation sequence; all sequence identifiers are strings. OpenAPI, generated TypeScript and Zod schemas are maintained together. The BFF validates symbol, literal 1h interval, requested range and cross-page watermark, with one five-second history deadline. Cancellation propagates through supported Start/fetch signals; independent signal/deadline and identity checks reject uncancellable late results.

## Implemented M3 private execution reads

`GET /v1/orders`, `/v1/orders/{id}`, `/v1/fills`, `/v1/positions`, `/v1/positions/{id}` and `/v1/risk` require both `X-Internal-Key` and `X-Owner-Session` and return `Cache-Control: private, no-store`. There is **no** order, cancel, start, pause, resume, flatten or approval route in M3. Query parameters are strict (unknown names return 422): `status` (an order status or `OPEN`), `state` (a position state, `LIVE` or `ENDED`), `symbol` (BTCUSDT/SOLUSDT), `cursor` (an opaque decimal string over a stable identity column; pages are newest first) and `limit` 1–100; `/v1/risk` takes `mode` (default `FORWARD_PAPER`). Every order and fill carries `modeled: true`, its mode and execution fidelity; decimals are strings and times UTC ISO strings; nulls carry reasons where a value could be misread (daily return, indicative live equity). `/v1/risk` reports activation as blocked with owning milestones, the proposed policy's rule usage, the latest persisted valuation with age, latches, passive breaches, lease/identity state, per-symbol quote usability and the `UNSET` cost scenario with labeled proposals. `SystemStatus` keeps `trading: "disabled"` and adds `execution_worker` (`not_running`/`running`, from the execution lease). `AccountView` adds `holdings`, `valuation_source` and `valued_at`.

## M4 owner approval, experiment and report routes (ExecPlan 0015)

All require `X-Internal-Key` and `X-Owner-Session`, return `Cache-Control: private, no-store`, reject unknown query parameters and bodies over 8 KiB, and take strict JSON bodies. Every mutation carries an idempotency key (`[A-Za-z0-9_-]{8,64}`): the same key and payload returns the original record, and a different payload is a 409.

- `GET /v1/approvals` lists every hashed definition with its canonical content, hash, status, current exact-hash state, consequences and a diff against its predecessor; recent manifests with the approval state of each referenced definition; and the approval-set version.
- `POST /v1/approvals` `{target_kind, target_id, target_sha256, action, expected_version, idempotency_key}` records APPROVE, REJECT or REVOKE for one exact hash. A stale hash or version is a 409. Approving a manifest requires every definition it references to be approved and moves its DRAFT experiment to READY. `GET /v1/approvals/requests/{key}` resolves an unknown outcome.
- `GET /v1/experiments`; `POST /v1/experiments` `{cost_scenario_id, idempotency_key}` (one forward DRAFT at a time); `GET /v1/experiments/{id}` returns state, manifest, approval completeness, open causes, transient blocks, pending and applied requests, the timeline, reports, worker and identity state, and the allowed actions.
- `POST /v1/experiments/{id}/{start|pause|resume|flatten|stop|discard}` `{expected_version, idempotency_key, causes?, flatten?}` returns the recorded request (`ACCEPTED`), never a completed effect. `GET /v1/experiments/{id}/requests/{key}` returns it together with its SYSTEM application or rejection.
- `GET /v1/experiments/{id}/reports/{report_id|latest}` returns a stored report's canonical document and hash.
- `/v1/risk` derives main activation and its blockers from the database and shows latch resolutions and the running cost scenario. `/v1/orders` and `/v1/positions` accept `experiment`. `SystemStatus.trading` reports `disabled`, `inactive`, `running`, `paused` or `stopping`, and `evaluation` reports `disabled`, `idle`, `reporting` or `failing`.

## Implemented M1 private account routes

The private engine requires `X-Internal-Key` for owner status/bootstrap/login and both that service key and `X-Owner-Session` for account reads and mutations. The Start BFF retains the opaque session in an HttpOnly SameSite=Strict cookie; the browser never receives the service key. `POST /v1/owner/bootstrap` requires the one-time local setup key and a passphrase, and succeeds once. `POST /v1/owner/login` and `/logout`, plus `GET /v1/owner/status` and `/session`, cover owner access.

`GET /v1/account`, `/v1/account/funding` (removed in [ExecPlan 0034](#cleanup-routes-nothing-calls-are-removed-execplan-0034)), `/v1/account/requests/{key}` and `/v1/account/initialization/draft` expose authoritative state, history, idempotency lookup and initialization review. `POST /v1/account/topups/draft` reviews a positive decimal amount. `POST /v1/account/initialization/confirm` and `/v1/account/topups` require that exact draft's amount, version and hash plus a durable idempotency key. `POST /v1/account/topups/{request_id}/retry` and `/cancel` act only on a pending request. `POST /v1/account/reconcile` compares source records and latches a discrepancy. All financial numbers cross HTTP as decimal strings. The browser uses same-origin Start server functions with Host/Origin/CSRF checks; it does not call this private API directly.

There is no valuation ingestion in M1. A flat virtual-cash account is valid for immediate top-ups; the pending-valuation branch is verified using synthetic invalid-valuation state and remains reserved for later holdings/mark integration.

## Proposed resource groups

| Method / resource | Semantics |
|---|---|
| `GET /v1/health/live`, `GET /v1/health/ready` | Process liveness vs application dependencies; redacted internal details |
| `GET /v1/system/status` | Worker/feed/model/ledger/config gate states; last observed timestamps |
| `GET /v1/account` | Immutable identity/denomination, current version, contributions, cash/reservations, valuation reference |
| `GET /v1/account/valuations` | Cursor-paged valuation/NAV history and quality flags |
| `GET /v1/account/funding` | Initial funding/top-up events, pending requests and posted flows (removed in [ExecPlan 0034](#cleanup-routes-nothing-calls-are-removed-execplan-0034)) |
| `POST /v1/account/topups` | Owner-only decimal amount and idempotency key; confirmed virtual funding request |
| `POST /v1/account/topups/{id}/cancel` | Cancel an unposted pending request, never erase a posted flow |
| `GET /v1/positions`, `/v1/orders`, `/v1/fills` | Account-scoped snapshots/histories with distinct order and fill states |
| `GET /v1/markets/instruments`, `/v1/markets/{symbol}/candles` | Approved universe, validated timeframe/range and source/quality metadata |
| `GET /v1/strategies`, `/v1/strategies/{id}/versions` | Immutable strategy definitions, status, tests and eligibility |
| `POST /v1/approvals` | Owner approval/rejection of exact proposal/version/hash, never free-text authorization |
| `GET /v1/experiments`, `POST /v1/experiments` | Query/create a configured inactive experiment; starting is separate |
| `POST /v1/experiments/{id}/start` | Validate manifest, approvals, readiness and active-account exclusivity |
| `POST /v1/experiments/{id}/pause` | Latch new-exposure pause and record reason; not a promise of liquidation |
| `POST /v1/experiments/{id}/resume` | Owner-authorized readiness/risk review; cannot erase unresolved drawdown |
| `POST /v1/experiments/{id}/flatten` | Owner-confirmed modeled-exit request; retain unresolved obligations without valid prices |
| `GET /v1/experiments/{id}/report` | Frozen evidence/metric report including failures and missing costs |
| `GET /v1/agent-jobs` | Sanitized job status and validated proposals; no auth contents or raw secrets |
| `GET /v1/events` | Account-scoped event stream with cursor, snapshot recovery and authorization |

There is no generic `setBalance`, browser `placeLiveOrder`, arbitrary SQL/tool invocation, runtime code deployment or exchange-key upload endpoint. Manual paper orders are not part of the initial strategy experiment; any later manual mode must be separate and clearly affect evaluation.

## Mutation semantics

Financial/control mutations require a request ID, idempotency key, canonical body hash, expected resource/config version where appropriate, owner identity and audit reason. Enforce same-key/same-payload replay; same key with different payload is a conflict. Idempotency records must survive restart and remain valid for the financial history's retention policy.

Successful asynchronous request acceptance is not financial completion. Return the request state/resource ID; UI reads the authoritative result. Use version conflicts for stale approvals/account state. Bind approvals to the exact configuration/proposal hash; any substantive edit invalidates previous approval.

Reject unsupported symbol/timeframe, range limits, invalid decimal precision, unknown fields/schema versions and unsafe text. Cursor pagination uses stable ordering and bounded limits; do not accept arbitrary column/SQL names from table filters.

## Error format and status mapping

Return a stable error code, human-readable safe message, correlation ID, retryability and field-level details where appropriate. Use validation errors for malformed inputs, conflict for stale versions/idempotency collisions, authorization errors for absent permission, and unavailable/degraded status for missing dependencies. Domain codes distinguish `PAPER_ONLY`, `DATA_STALE`, `POLICY_PAUSED`, `COST_MODEL_UNSET`, `INSUFFICIENT_FUNDS`, `FILTER_REJECTED`, `MODEL_UNAVAILABLE` and `RECONCILIATION_REQUIRED`.

Never include SQL traces, filesystem paths containing secrets, auth tokens or raw provider credentials in browser errors. Expected no-trade/rejected-signal outcomes are auditable domain results, not application crashes.

## Events and consistency

Publish events from a transactional outbox after authoritative state commits. Event fields include schema version, ID/cursor, aggregate ID/version, mode, event time and safe payload. At-least-once delivery requires client/server deduplication. A detected gap sends a resynchronization signal or triggers snapshot retrieval; do not apply financial deltas to an unknown base.

Use one main execution lease with fencing/version checks. A queue lease is not sufficient financial authority by itself. Document retry/acknowledgment behavior and unknown-commit recovery. Stream disconnection must not interrupt the worker's market/risk loop.

## Required contract tests

Verify decimal round trips, null/unknown semantics, UTC precision, idempotent topups, stale-approval rejection, authentication/CSRF/origin controls, main-vs-shadow isolation, invalid filters, event gaps, stream cleanup, safe errors and generated-type drift. No model output is trusted merely because its JSON matches a schema.

## Agent-driven operator resources

Extend the owner-facing API in later milestones; these are proposed routes, not implemented capabilities:

| Method / resource | Purpose |
|---|---|
| `GET /v1/agent-workflows`, `GET /v1/agent-workflows/{id}` | Role/step/tool timelines, state, bounded sanitized artifacts and actual usage |
| `POST /v1/agent-workflows/{id}/cancel` | Owner cancellation of workflow/children; not a shortcut to remove accepted position protection |
| `GET /v1/policies`, `GET /v1/policies/{id}/versions` | Operating/research envelopes and capability diffs |
| `POST /v1/policies/{id}/revoke` | Owner-revoked capability version; invalidates outstanding work and invokes safe reconciliation. *Not built in M7:* the operating policy is revoked through the existing `/v1/approvals` action, which then raises the permission epoch ([M7 below](#m7-owner-routes-execplan-0026-b7)) |
| `GET /v1/evidence`, `GET /v1/evidence/{id}` | Approved scoped evidence, source/availability and quality, sanitized rendering |
| `GET /v1/research/candidates`, `GET /v1/research/experiments` | Research lifecycle and isolated results, not main approval |
| `GET /v1/trade-intents`, `GET /v1/trade-intents/{id}` | Draft/review/validation/order links and exact rejected reasons |
| `GET /v1/promotions` | Requested scope, immutable hash, tests/reports and pending owner decision |
| `GET /v1/sources` | Source registry versions, health, rights/retention metadata and approval state |

Reuse the existing exact-hash approval **semantics** for main-strategy/domain/tool/source approval; do not create a text-based alternative. Approval context includes human identity, target kind/hash, scope, permission epoch and expected current version. Create inactive drafts through validated owner configuration resources; never auto-activate them on save.

*Amended 2026-09-30 by [ExecPlan 0020](../plans/0020-m5-agent-runtime.md#58-owner-api), and for the approved M6 contract on 2026-10-03.* Runtime-profile, M6 research-envelope and source-version approvals use the same exact-hash semantics through a **separate route and store**: `/v1/agent-approvals` and `agent_approvals`. They have their own version counter and never write `owner_approvals`, so the running pilot's approval page and the execution worker's approval poll are unaffected. M6 promotions offer rejection only; their approval and later main-strategy/domain authority wait for M7. *Settled for M7 by ExecPlan 0026:* the agent-driven operating policy and `EVALUATION_PROTOCOL_V2` are approved in `owner_approvals` through `/v1/approvals`, because the execution worker reads that store in every step; a `PROMOTION_V2` approval stays in `agent_approvals`.

Application agent tools are **internal dispatch contracts**, not generic public routes. The default broker invokes registered engine handlers with a server-assigned capability context. No browser endpoint accepts arbitrary `tool_name` and grants a model owner authority. If a future transport exposes internal tool RPC, authenticate the service and job separately, bind role/account/mode/version, and preserve the same dispatcher tests.

Financial/control endpoints remain inaccessible to runtime model identities unless the autonomy matrix expressly permits the corresponding internal action. `submit_trade_intent` is the single coordinator request path to existing risk/broker validation, not `setBalance` or direct order placement.

Add events for workflow/step/tool state, evidence availability, review, intent validation, promotion and capability revocation. Use transactional outbox/cursors and do not broadcast secrets, raw prompts or hidden reasoning. UI observes durable state; cancellation acknowledgments do not claim a raced fill never happened. *M5 and M6 built no such stream, and M7 builds none either:* its pages poll durable state as theirs do; the engine's answers are `decision_events` rows ([ExecPlan 0026 §3.4](../plans/0026-m7-agent-driven-main-decisions.md#34-where-the-documents-disagree-and-what-b0-writes)).

Contract tests cover cross-role/mode/account references, locked holdout reports, stale hash approvals, revoke-during-request races, pagination/retention gaps, idempotent cancellation, event resync and no generic privileged dispatch. See [AGENT_TOOL_CONTRACTS.md](../AGENT_TOOL_CONTRACTS.md).

## M6 owner routes (ExecPlan 0023 B7)

IMPLEMENTED in B7 of [ExecPlan 0023](../plans/0023-m6-research-investigations.md#59-owner-api-and-pages); the isolated evidence is in its §18. These are private-API routes. Since B8 the browser reaches them only through the same-origin server functions of `apps/web/src/research/` and `src/agents/`, behind the web's Host and CSRF middleware ([FRONTEND](FRONTEND.md#m6-research-and-evidence-pages-execplan-0023-b8), [SECURITY](SECURITY.md#m6-b8-owner-pages-and-same-origin-functions-execplan-0023)).

All routes below:
- require `X-Internal-Key` and `X-Owner-Session`, and a `Host` on the private allowlist;
- return `Cache-Control: private, no-store`;
- reject unknown query parameters, on reads and on the three new mutations alike, and bodies over 8 KiB;
- take strict JSON bodies. The integers of the new bodies (`expected_version`, `horizon_hours`, a filter value) are JSON integers only: `true`, `"1"` and `1.0` are `422`. The M4 and M5 bodies keep the coercion they shipped with (plan §19);
- answer `503 RESEARCH_SCHEMA_PENDING` until migration 0008 is applied;
- answer `503 TRY_AGAIN` (retryable) when a statement or lock times out or no connection is free, on reads as on mutations. The database's own error text is never returned.

No route accepts a tool name, a URL, a host, a role, a candidate declaration or free text. No route sets a state, a balance or a definition, and none approves a promotion.

**Idempotency.** Every mutation carries a key (`[A-Za-z0-9_-]{8,64}`) with the M4 semantics: the same key and payload returns the first record, a different payload is `409 IDEMPOTENCY_CONFLICT`. One key names one request of one kind across every owner store of M5 and M6: approvals, runtime requests, workflows, profiles, refresh requests, job cancels and shadow stops. A lock or statement timeout is `503 TRY_AGAIN` and records nothing.

**What the owner sees.** The owner is not a tuning role. Holdout and shadow results are returned, and whatever rests on them says so (`holdout`, `shadow`, `locked_for: ["ANALYST", "RESEARCHER"]`), so a page can label what is locked:
- a job, a result cell, a shadow, a review and a promotion;
- a hypothesis's holdout summary, a dataset's holdout counts, and a `SHADOW` dataset whole;
- a candidate once a full test, a shadow or a promotion exists for it, and each of its events from the first one that needed the full test;
- a ledger row that asked for a full test or a shadow advance, also when it was refused and led to no job;
- a tool result, a completion and an artifact (also in a workflow's artifact list) through `provenance`.

**Consequence lists (B8).** A page states what an owner action leads to before the owner confirms it, from lists the API returns. The lists are code-owned stable codes (`DECISION_CONSEQUENCES` and `REFRESH_CONSEQUENCES` in `app/agents/approvals.py`); they describe what the approval record and the workers do and grant nothing. Both fields are additive: no route, body, grant or migration changed for them.

- `decision_consequences` on the envelope in `GET /v1/research/status`, on each source version in `GET /v1/sources` and on each promotion in `GET /v1/promotions`: one list for each action the target takes (`APPROVE`, `REJECT` and `REVOKE`; `REJECT` only for a promotion), as a job states `cancel_consequences` and a shadow `stop_consequences`.
- `refresh_consequences` on each source version: what an owner refresh leads to. One fetch is requested, the fetcher decides whether and when, and new items may start an event investigation while the runtime is enabled.
- **What a `REVOKE` list states.** Only a `REVOKE` list names the permission epoch. Both revoke lists say what the epoch change does to work of every kind, not only to research:
  - queued and running jobs and refreshes are canceled, and a job canceled this way is final for its input;
  - every started workflow bound to the older epoch fails as revoked, of either generation and of every template, and a model call in flight is canceled;
  - a workflow the system had queued is canceled; a late result is history only.
- **What an `APPROVE` list states.** The envelope's list names the scheduled research and the full tests and shadows SYSTEM may then start. A source's list names the fetcher's polling and the event investigations new items may start.
- A promotion's `REJECT` list says that an open shadow of the candidate is not ended by the rejection.

A source's text (title, extract, link) carries the label `UNTRUSTED_SOURCE_TEXT`; a hypothesis statement, a proposal and a promotion's rationale carry `MODEL_AUTHORED` and `UNTRUSTED`. Both are returned as text and never interpreted. A tool call's `arguments` can hold model-authored text (a hypothesis statement, a search query) and carry no label of their own, as in M5.

**Reads**

- `GET /v1/sources`: every stored source version with:
  - its registry state (`APPROVED`, `PROPOSED`, `REJECTED`, `REVOKED`, `INVALID`) and the reason when it is unusable;
  - its canonical definition and hash, which is what the owner approves;
  - host, path, typed filters, budget, symbol scope and the rights record;
  - the last fetch record (`last_fetch`), the last one for which a request was actually sent (`last_attempt`), the last successful fetch, the item count and its five most recent refresh requests. A request the fetcher refused before sending anything (`BUDGET_EXHAUSTED`, `BACKOFF_ACTIVE`) is a fetch record and says nothing about the source;
  - `current`: a successful fetch within two poll intervals, and no failed attempt after it;
  - a `status` over all approved versions and the approval-set version.
- `GET /v1/evidence` (`source_id`, `cursor`, `limit` 1–100, newest availability first): stored items with the publisher's two times as supplied and this installation's two, without the extract. `usable` says whether a model could be given the item now.
- `GET /v1/evidence/{id}`: one item with its extract, link and attribution, the fetch that stored it, its other revisions, and what an item proves: that its publisher published that text at that time, not that it is true.
- `GET /v1/research/status`: the envelope with its canonical text, hash and approval state; the protocol and grammar it binds; the queue and the day's trial budget; the running job; the bridge's newest journal record and its newest storage observation; each store's lifecycle events, storage observation, staging watermark and newest refused staging pass with its reason code; recent staging gaps; dataset and shadow counts.
- `GET /v1/research/hypotheses`, `/v1/research/candidates` (`state`, `hypothesis_id`), `/v1/research/datasets` (`purpose`), `/v1/research/shadows` (`state`): keyset pages, newest first, ordered by time and then by ID. A page never repeats a row. A row whose transaction commits after an earlier page was read, with an earlier time than that page's last row, is not in that paging session; the next first page shows it.
  - A hypothesis shows its information cutoff and its one holdout evaluation.
  - A dataset shows how often its holdout was evaluated. The count is shown, not corrected.
  - A shadow shows its label (`SHADOW — deferred replay`), its latest mark and how it ended.
- `GET /v1/research/candidates/{id}`: the declaration, every lifecycle event with its gate evidence, the candidate's jobs and its reviews.
- `GET /v1/research/experiments` (`subject`, `kind`, `state`, `candidate_id`): the trial ledger, newest first. Every recorded attempt is listed: a candidate registration (accepted or refused), a request for an experiment (queued, answered with an existing job as `REUSED`, or refused) and a shadow advance, each with its recorded reason code and, if it led to one, its job. `requested_kind` is the kind that was asked for; a request recorded before B7 that led to no job states none.
- `GET /v1/research/experiments/{id}`: one job with its attempt history, its cancel request and its result as figures per cell. `GET /v1/research/experiments/{id}/cells/{index}` returns one cell's stored evaluation document whole, so no response grows with a result's size.
- `GET /v1/promotions`: the newest 100 promotion requests, each with its canonical document and hash, the candidate's state, the owner's recorded decision and whether SYSTEM has applied it. The list has no cursor; a candidate has at most one pending request.

**Owner requests.** Each answers with the recorded request, never a completed effect.

- `POST /v1/sources/{id}/refresh` `{filters?, idempotency_key}` queues one fetch of an approved source as actor `OWNER`. `filters` are that source's typed integer filters; without them the request is the source's registered poll. The fetcher decides, under its own budget, back-off and approval checks, whether and when a fetch happens. A fetch that stores new items queues a `SOURCE_REVISION` trigger, which the scheduler turns into an event investigation while the runtime is enabled. The B8 page sends the key only: an owner refresh from the browser is always the registered poll.
  - An unknown source is `404 SOURCE_NOT_FOUND`; an unapproved or invalid one `409 SOURCE_UNAVAILABLE`.
  - A refresh equal to one already requested in the same refresh interval, whether that one is still outstanding or has finished, is `409 REFRESH_INTERVAL_ACTIVE`: it would be answered by a row that does not carry the owner's key. The answer names no request; the source's recent requests are listed by `GET /v1/sources`.
- `POST /v1/research/jobs/{id}/cancel` `{expected_version?, idempotency_key}` records the cancel on a queued, dispatched or running screening or full test. The research identity applies it: at dispatch for a queued job; for one that reached the runner the bridge relays the cancel and the runner stops between batches. The job ends `CANCELED` with reason `OWNER_CANCEL`; a result that arrives after the request is kept as history only.
  - **A canceled job is final for its input** (owner decision of 2026-10-05): an equal request returns that job. A screening canceled before it ran leaves its candidate untested; a full test canceled before it ran leaves its hypothesis without a holdout evaluation. Each job states this in `cancel_consequences`.
  - **The workflow that asked for a canceled screening goes on.** It receives the completion `CANCELED` with reason `OWNER_CANCEL` and takes its next step; it is not ended as revoked, because nothing was revoked. A canceled full test ends its parent workflow without a review. If the envelope is revoked while a cancel is outstanding, the revocation is what the job records (`CAPABILITY_REVOKED`).
  - A shadow advance is refused with `409 USE_SHADOW_STOP`: the schedule would record it again.
- `POST /v1/research/shadows/{id}/stop` `{expected_version?, idempotency_key}` records the stop on a queued or running shadow. The research identity ends it `STOPPED`, cancels its queued advance and retires its candidate unless that candidate already reached `EVIDENCE_READY`. The stop counts from the moment it is recorded: an advance result that arrives after it, before the research identity has applied it, is kept as history and becomes neither a mark nor evidence.
- Cancel and stop only remove work, so a stale `expected_version` is recorded and does not block them, as for Disable. Each takes one request: a second with another key is `409 CANCEL_ALREADY_REQUESTED` or `409 STOP_ALREADY_REQUESTED`.
- `GET /v1/sources/requests/{key}` and `GET /v1/research/requests/{key}` resolve an unknown outcome. A research request reports `ACCEPTED`, `APPLIED` or `ENDED_OTHERWISE`.

**Approvals** (`POST /v1/agent-approvals`, the same store, counter and `expected_version` as M5)

- `target_kind: "RESEARCH_ENVELOPE"` or `"SOURCE_VERSION"` with the definition's ID and exact hash: `APPROVE`, `REJECT` or `REVOKE`, with the M5 state rules.
  - An envelope that is not the one this code runs is `409 DEFINITION_NOT_CURRENT`. A source version the registry holds invalid is `409 SOURCE_INVALID`.
  - **A revocation raises the permission epoch in the transaction that records it.** The epoch is one number, so the effect does not depend on which source or envelope was revoked: queued jobs and refreshes are canceled, a late result is history only, every started workflow bound to the older epoch fails `CAPABILITY_REVOKED` (generation 1 and generation 2 alike, with a model call in flight canceled), and a workflow the scheduler had queued is canceled. B7 described only the waiting generation-2 workflows here; the behavior is unchanged, the description was incomplete (B8 review).
- `target_kind: "PROMOTION"` with the promotion's ID and exact hash takes `REJECT` only (M6-OD5). `APPROVE` and `REVOKE` are `409 PROMOTION_REJECT_ONLY`; a promotion that is not pending, or already has a decision, is `409 PROMOTION_NOT_PENDING`. The agent worker then applies the rejection as SYSTEM: the promotion becomes `REJECTED` and its candidate `REJECTED`, which is terminal. A rejection moves no epoch.
- A target ID must be spelled as the stored row spells it; any other spelling is `404 TARGET_NOT_FOUND`.

**Owner-started workflows** (`POST /v1/agent-workflows`). The body is one of four strict shapes chosen by `template_id`, each with exactly the parameters its code-owned template registers:

| `template_id` | Parameters | Refused when |
|---|---|---|
| `MARKET_ASSESSMENT_V1` | `symbols`, `horizon_hours` | as in M5 |
| `EVENT_INVESTIGATION_V1` | `symbols`, `horizon_hours` | — |
| `RESEARCH_V1` | `symbols` | `409 ENVELOPE_UNAPPROVED`; `409 NO_DATASET` |
| `PROMOTION_V1` | `candidate_id` | `404 CANDIDATE_NOT_FOUND`; `409 EVIDENCE_NOT_READY`; `409 PROMOTION_IN_PROGRESS` |

A review child is not startable. These refusals keep an owner from queueing work that cannot run; the authority stays with the worker and the tools. A research workflow's envelope approval and dataset are checked again when it starts, and a promotion request is recorded only for a candidate that is `EVIDENCE_READY` at that moment. `PROMOTION_IN_PROGRESS` is checked by this route only: an owner start and SYSTEM's own start for the same candidate can both be queued, and the second to ask finds the candidate no longer `EVIDENCE_READY` and records nothing (INFERRED from the code by the independent review; no test drives both, plan §19). `PROMOTION_V1` takes the ID of a registered candidate, never a declaration, and the request it leads to can only stay pending.

**Changed M5 read models.** The M5 response shapes gained fields and enum values; nothing was removed.
- `GET /v1/agent-runtime` adds `budgets_v2`, the code-owned budgets of the five generation-2 templates. `budgets` stays generation 1.
- A workflow shows the budget of its own generation, `usage.experiments`, and the new purposes and creators. Its cutoff adds `dataset_id` and `rule`.
- A tool call may be `QUEUED` and then carries its one `completion`. Generation-2 results, completions and artifacts carry server-computed `provenance` (`available_through`, `holdout`, `shadow`); anything but an explicit false, and a missing object, is shown as restricted. A generation-1 (M5) result or artifact records no such bounds and has `provenance: null`: M5 reads no research result.
- A `CANDIDATE_REVIEW_V1` child shows what it is bound to as `params.review`: the proposal, the hypothesis, the candidate and the experiments by ID and hash, marked `holdout` and `locked_for`. The stored target's statement, declaration and holdout-derived figures are not part of a workflow summary; they are read on the hypothesis, the candidate and the experiment, where they are labeled.
- An approval record's `target_kind` is one of the four kinds. A runtime-profile approval now also requires the profile ID in the stored row's own spelling.

**`SystemStatus`** adds two fields, both from recorded facts only:

| Field | Values |
|---|---|
| `research` | `unconfigured` (before migration 0008), `unapproved` (the envelope this code runs is not approved), `unavailable` (approved, and the bridge recorded no storage observation in the last 2 h 10 min, which is what a job reservation requires; a bridge that only records refused staging passes, or one that stopped with a job still dispatched, reads `unavailable`), `running` (a job is dispatched or running), `idle` |
| `sources` | `unconfigured`, `unapproved` (no approved source version), `ready` (every approved version is `current`: a successful fetch within two poll intervals and no failed attempt after it), `degraded` (some are), `unavailable` (none is). A refresh refused before anything was sent changes none of these |

Either field reads `unavailable` when its own query fails; the route itself does not fail.

**Rollout order.** The web schemas accept both shapes: a field M6 added is optional there and a new enum value is additional. The web released before B7 refuses unknown fields, so the web is deployed before the API, or the status and agent pages show their error state until both are current.

**Later migrations.** The M6 routes, both status fields and the research identity command accept the revisions in `M6_REVISIONS` (`app/agents/views.py`) and `REVISIONS` (`app/research/identity.py`): `0008_m6_research` and, from M7 B1, `0009_m7_agent_decisions`. A migration after 0009 must add itself to both sets and to `ACCEPTED_REVISIONS` in `app/db.py`, or every M6 route answers `503`, both status fields read `unconfigured` and readiness fails.

**New error codes:** `RESEARCH_SCHEMA_PENDING`, `TRY_AGAIN`, `SOURCE_NOT_FOUND`, `SOURCE_UNAVAILABLE`, `SOURCE_INVALID`, `INVALID_FILTERS`, `REFRESH_INTERVAL_ACTIVE`, `JOB_NOT_FOUND`, `JOB_FINISHED`, `CANCEL_ALREADY_REQUESTED`, `USE_SHADOW_STOP`, `SHADOW_NOT_FOUND`, `SHADOW_ENDED`, `STOP_ALREADY_REQUESTED`, `DEFINITION_NOT_CURRENT`, `PROMOTION_REJECT_ONLY`, `PROMOTION_NOT_PENDING`, `ENVELOPE_UNAPPROVED`, `NO_DATASET`, `CANDIDATE_NOT_FOUND`, `EVIDENCE_NOT_READY`, `PROMOTION_IN_PROGRESS`, `INVALID_PARAMETERS`, `EVIDENCE_NOT_FOUND`, `EXPERIMENT_NOT_FOUND`, `CELL_NOT_FOUND`, `INVALID_CURSOR`.

Four routes beyond the list in §5.9 were added, because a page cannot work without them: the two key lookups, and the experiment detail and cell reads.

OpenAPI and the generated TypeScript types are produced from the implemented models by the `Generate` phase. It runs only while the product source in the working tree is the source this run's Build recorded, and it fails when the generated files in the tree differ from what the built image generates. A generated schema is not authorization evidence; `ApiAuth` is.

## M5 agent runtime routes (ExecPlan 0020)

All routes below:
- require `X-Internal-Key` and `X-Owner-Session`;
- return `Cache-Control: private, no-store`;
- reject unknown query parameters and bodies over 8 KiB;
- take strict JSON bodies.

Every mutation carries an idempotency key (`[A-Za-z0-9_-]{8,64}`) with the M4 semantics: the same key and payload returns the original record, and a different payload is a 409. API readiness never depends on the agent services. No route accepts a tool name, and no route exposes auth contents, raw prompts, reasoning or runner secrets.

- `GET /v1/agent-runtime` returns:
  - the runtime state and blocks;
  - auth and quota as observed, never inferred;
  - runner and worker status, the CLI version, binary digest and config hash;
  - the approved profile and its hash;
  - the permission epoch;
  - the latest discovery and capability verification;
  - draft profiles with their diff and consequences;
  - probe runs;
  - the actions currently allowed.
- `POST /v1/agent-runtime/profiles` `{discovery_id, model, reasoning_effort, idempotency_key}` composes a DRAFT profile. `model` must appear in that discovery's list; nothing is inferred from a display name.
- `POST /v1/agent-runtime/enable` `{profile_sha256, target, expected_version, idempotency_key}`. `target` is `ENABLED` (needs a VERIFIED capability record for exactly that profile; since M8 update 1 only the approved profile, [M8](#m8-update-1-one-switch-and-the-agents-check-execplan-0031)) or `PROBE_ONLY` (needs an approved profile). The request is recorded as `ACCEPTED`, and the worker applies it after re-checking.
- `POST /v1/agent-runtime/disable` `{expected_version, idempotency_key}` is applied immediately: the state becomes `DISABLED` and the permission epoch increases in the same transaction.
- `POST /v1/agent-runtime/probe` `{profile_sha256, expected_version, idempotency_key}` queues the probe suite (runtime `PROBE_ONLY`, approved profile, within the probe budget).
- `GET /v1/agent-runtime/requests/{key}` resolves an unknown outcome.
- `GET /v1/agent-workflows` (cursor and limit 1–100, newest first) and `POST /v1/agent-workflows` `{template_id: "MARKET_ASSESSMENT_V1", symbols, horizon_hours, idempotency_key}` (no free text). A new workflow is `QUEUED` and expires after 10 minutes if it does not start.
- `GET /v1/agent-workflows/{id}` returns the state, role, provider, profile, cutoff, budgets and usage, the step and tool timeline, artifacts, children and provenance.
- `POST /v1/agent-workflows/{id}/cancel` `{expected_version, idempotency_key}` cascades to the child.
- `GET /v1/agent-workflows/requests/{key}` resolves an unknown outcome.
- `GET /v1/agent-artifacts/{id}` returns an artifact's canonical document and hash, labeled model-authored and untrusted.
- `GET /v1/agent-approvals`, `POST /v1/agent-approvals` `{target_kind: "RUNTIME_PROFILE", target_id, target_sha256, action, expected_version, idempotency_key}` and `GET /v1/agent-approvals/requests/{key}`.
- `GET /v1/agent-probes` lists probe runs and per-probe results.

`SystemStatus.model` becomes the enum `unconfigured | login_required | probe_only | enabled | blocked | disabled`. It reports `unconfigured` until the runtime first leaves `DISABLED`, and the web schema accepts both the old and the new shape during the rollout.

The runner's own API is internal only. It is reachable on the `agent_control` network by the agent worker, with the runner key, and never by the browser or the API.

**New error codes:** `UNKNOWN_TOOL`, `CAPABILITY_VIOLATION`, `RUNTIME_DISABLED`, `PROFILE_UNAPPROVED`, `PROFILE_MISMATCH`, `OUTPUT_REJECTED`, `OUTCOME_UNKNOWN`, `MODEL_EXPOSES_NATIVE_TOOLS` (M5-OD1: profile composition for a model that is not `code_mode_only`), plus `AGENT_VERSION_CONFLICT`, `RUNTIME_STATE_CONFLICT` and `AGENT_SCHEMA_PENDING` (the API is at 0006 during the rollout).

## M7 owner routes (ExecPlan 0026 B7)

IMPLEMENTED in B7 of [ExecPlan 0026](../plans/0026-m7-agent-driven-main-decisions.md#512-owner-api-and-pages); the isolated evidence is in its §18 and the decisions taken while building it in §17 (B7). These are private-API routes. Since B8a the browser reads `GET /v1/trade-intents`, its detail, `GET /v1/outcomes/{position_id}` and `GET /v1/policies` only through the same-origin `GET` server functions of `apps/web/src/decisions/`, behind the web's Host and CSRF middleware ([FRONTEND](FRONTEND.md#m7-decision-and-policy-pages-execplan-0026-b8a)). The owner's requests, the entry pauses and the changed routes' new fields reach the browser in B8b; until then the web only parses those shapes.

All routes below:
- require `X-Internal-Key` and `X-Owner-Session`, and a `Host` on the private allowlist;
- return `Cache-Control: private, no-store`;
- reject unknown query parameters and bodies over 8 KiB, and take strict JSON bodies;
- answer `503 DECISION_SCHEMA_PENDING` until migration `0009` is applied, except `GET /v1/policies` and `GET /v1/policies/{id}/versions`, which show the code's documents as not installed;
- answer `503 TRY_AGAIN` when a statement or lock times out or no connection is free. The database's own error text is never returned.

No route accepts an intent, a tool name, a price, a quantity, a stop or a size from the browser. A trade intent comes only from a coordinator workflow through the dispatcher, and the engine computes every price, quantity and stop. The two new writes take a key (the resume) or a profile hash, a version and a key (the decision probe).

**Idempotency.** As in M6: the same key and payload return the first record, a different payload is `409 IDEMPOTENCY_CONFLICT`, and one key names one request of one kind across every owner store of M5 to M7, the entry-pause resumes included.

**Reads**

- `GET /v1/trade-intents` (`symbol`, `action` (`ENTER`, `EXIT`, `TIGHTEN_STOP`, `CANCEL_ENTRY`), `run_id`, `cursor`, `limit` 1–100, newest first by time, then by ID): every draft of a decision with separate fields for each stage, never one inferred from another:
  - `requested`: the model's choices from the policy's sets, labeled `MODEL_AUTHORED`, `UNTRUSTED`. It never holds a price, a quantity or a stop level;
  - `review`: the intent review's workflow, state, verdict and artifact hash;
  - `submission` and `withdrawal`: what the agent submitted and, if it was withdrawn before an answer, why;
  - `answer`: the engine's event (`ACCEPTED`, `REJECTED`, `EXPIRED`, `CANCELED`) with its reason codes and the order, obligation, signal or stop update it names;
  - `permitted`: for an accepted entry, the risk gate's decision and the quantity it sized, with the binding limit, equity, entry reference and stop;
  - `filled`: the filled quantity of the orders the accepted entry or exit led to, labeled `MODELED_FILLS`;
  - `state`: one label for a list (`DRAFTED`, `NOT_SUBMITTED`, `SUBMITTED`, `WITHDRAWN`, the engine's answer, or `FILLED`).
- `GET /v1/trade-intents/{id}`: the same, with the draft's canonical text and document, the snapshot it was drafted on, its workflow, the submission's bindings (review, assessment or candidate and its approval, profile, permission epoch, context key), the engine's event detail, the orders and modeled fills, the position with the decision's terms, its stop history and the stop in force, and the position's outcome record. `404 INTENT_NOT_FOUND`.
- `GET /v1/policies`: each operating policy this build holds, then any installed one it does not, with its canonical document and hash, `INSTALLED` or `NOT_INSTALLED` (with the code's hash before the boundary), whether it is in this build and installable, the problems of a document that does not parse, the owner's latest decision on its exact hash, the consequences of approving it, the evaluation protocol it names, up to ten of its runs and the difference from its predecessor. The owner approves or revokes it through `/v1/approvals`.
- `GET /v1/policies/{id}/versions`: the versions of one policy by its ID's stem, oldest first, each with its difference from the one before. `404 POLICY_NOT_FOUND`.
- `GET /v1/entry-pauses` (`run_id`, `cursor`, `limit`; newest first by sequence): each agent's entry pause with its reason and cited records (`MODEL_AUTHORED`, `UNTRUSTED`), whether the engine opened it with effect (`ENTRIES_REFUSED`, with the entries it ended) or without (`NONE`, for a run that is not live), the owner's resume and when the engine closed the pause. `state` is `REQUESTED`, `OPEN`, `OPENED_WITHOUT_EFFECT`, `RESUME_REQUESTED` or `CLOSED`; `actions.resume` says whether a resume can be recorded; `resume_consequences` lists what one leads to (`RESUME_CONSEQUENCES` in `app/agents/decision_views.py`).
- `GET /v1/entry-pauses/requests/{key}`: the owner's resume recorded under that key, `ACCEPTED` until the engine closes the pause, then `APPLIED`. `404 REQUEST_NOT_FOUND`.
- `GET /v1/outcomes` (`run_id`, `cursor`, `limit`; newest first by time, then by ID) and `GET /v1/outcomes/{position_id}`: each closed policy position's outcome record, a function of the financial rows as stored (`COMPUTED_FROM_FINANCIAL_ROWS_AS_STORED`, `MODELED_PAPER_FILLS`, `NO_EDGE_CLAIM`), with its system outcome review; the detail adds the canonical text and document. `404 OUTCOME_NOT_FOUND`.

**Owner requests.** Each answers with the recorded request, never a completed effect.

- `POST /v1/entry-pauses/{id}/resume` `{idempotency_key}`: records the owner's resume of an agent's entry pause. Only this closes a pause; the engine closes it in its next step. The engine answers pause and resume requests in order, so a resume of a pause it has not opened yet lets that pause open first (ending the run's unfilled entries) and then closes it. One resume per pause, whatever the engine's answer to the pause was: `409 PAUSE_ALREADY_RESUMED`, also for a resume that commits concurrently. `404 PAUSE_NOT_FOUND`. Nothing here touches a position, an order or a stop; exits and protection were never paused.
- `POST /v1/agent-runtime/decision-probe` `{profile_sha256, expected_version, idempotency_key}`: requests the decision suite (CP-23 to CP-27) for the approved profile, in `PROBE_ONLY` or `ENABLED` and never while latched (`409 RUNTIME_STATE_CONFLICT`, `CAPABILITY_LATCHED`, `AGENT_VERSION_CONFLICT`, `PROBE_RUN_IN_PROGRESS`; `404 PROFILE_NOT_FOUND`, `409 PROFILE_UNAPPROVED`). The worker checks the operating policy (installed, current definitions, approved, its run `RUNNING`) when it applies the request. The request is read back through `GET /v1/agent-runtime/requests/{key}`.

**Changed routes**

- `/v1/approvals`: a `REVOKE` of an installed `AGENT_DRIVEN` policy is recorded in its own transaction and answered as recorded; the engine acts on it in its next step without the epoch. The API then raises the agents' permission epoch once for that revocation (reason `POLICY_REVOKED:<approval id>`) in a second transaction, taking the epoch row's lock first and trying again up to three times on a lock or statement timeout or when no connection is free. `permission_epoch_raised` says whether the raise has happened: `true`, `false` when it was not seen to finish (sending the same request again tries it again, and raises it once; a commit whose answer was lost may already have raised it, so `false` can follow a raise), `null` for every other action. `GET /v1/approvals/requests/{key}` reports the same and raises nothing. Once recorded, a revocation is never answered with an error such as `503 TRY_AGAIN`, which would wrongly say it was not.
- `/v1/agent-approvals` accepts `APPROVE` and `REVOKE` for a `PROMOTION_V2` request (B6a's rules). `GET /v1/promotions` gains `template_id`, the states `APPROVED` and `REVOKED`, the decision actions `APPROVE` and `REVOKE`, `approval` (`REJECT_ONLY` for a V1 request, `ENTRY_BASIS` for a V2 one; M6 sent `NOT_AVAILABLE_IN_THIS_RELEASE`), the actions `approve` and `revoke`, and each action's consequence list.
- `/v1/experiments` takes `strategy_id`, an installed operating policy of this build (`422 UNKNOWN_STRATEGY`, `409 POLICY_NOT_IN_THIS_BUILD`, `422 FIXTURE_STRATEGY_REFUSED`, `409 OTHER_STRATEGY_POSITIONS_OPEN`); without it the draft is the reference's, with M4's request hash.
- `/v1/agent-workflows` accepts the owner-startable generation-3 templates: `MARKET_BRIEF_V1` (`symbols`), `PORTFOLIO_DECISION_V1` (no parameter: the server writes the universe of the policy its run trades, and the request digest names only the template) and `PROMOTION_V2` (`candidate_id`). A decision is refused before a row exists for the reasons the worker would refuse it: `POLICY_NOT_INSTALLED`, `POLICY_RUN_NOT_LIVE`, `POLICY_UNKNOWN`, `POLICY_DEFINITIONS_MISMATCH`, `POLICY_RUN_NOT_RUNNING`, `POLICY_UNAPPROVED`, `DECISION_SUITE_NOT_VERIFIED`, and `DECISION_IN_PROGRESS` while another decision is open (all `409`). A `PROMOTION_V2` start is refused as SYSTEM's would be (`404 CANDIDATE_NOT_FOUND`, `409 POLICY_NOT_INSTALLED`, the candidate's ineligibility, `PROMOTION_IN_PROGRESS`). Every start, like the decision probe and the resume, answers `503 TRY_AGAIN` when a lock or statement times out or no connection is free, and records nothing.
- `GET /v1/agent-runtime` gains `actions.decision_probe`, `budgets_v3`, `decision_verifications` and `generations` (each generation's role grants and templates, and who may start each); a probe run gains `suite` (`CAPABILITY`, `DECISION`) and the policy it ran on. Workflows and artifacts gain generation 3's purposes, creators and the `PORTFOLIO_DECISION` kind; a runtime request the `DECISION_PROBE` kind.
- `GET /v1/positions` and `GET /v1/positions/{id}` gain `stop_in_force`: the newest stop of the decision's tightenings, or the mandate's stop.
- `SystemStatus` gains `decisions`, from recorded facts only: `unconfigured` (before `0009`), `not_installed`, `unapproved`, `inactive` (no live forward run of the policy), `blocked` (the worker would refuse a decision, or the runtime is not `ENABLED` or is latched), `entry_paused`, `running`, and `unavailable` when it cannot be read. The web accepts both shapes during the rollout and is deployed before the API.
- **B8b.** `GET /v1/approvals`: each definition gains `revoke_consequences`, what revoking it does, for an operating policy (`STRATEGY` with `policy_kind` `AGENT_DRIVEN`) and a protocol that applies to agent-driven runs only; `null` for every other definition, whose page keeps the one text. `GET /v1/risk` gains `action_limits`, `null` before `0009` or without a live run (`RUNNING`, `PAUSED`, `STOPPING`) of an operating policy in that mode: the run, the policy and its hash, `window_hours` and `since`, each symbol's accepted entries against its limit and `cooldown_until` (the open time of the first decision bar a new entry passes the re-entry and cancellation cooldowns, `null` when neither applies to the latest closed bar), the entries in all, the submissions (accepted or not) and the notional the window counts (entries' commitments plus exits' fills, as `committed_notional` counts them), whose `limit` is the policy's fraction of the latest valid equity, or `null` with `unavailable_reason` `VALUATION_UNAVAILABLE`. Each is counted as the engine counts it at its step, which checks every limit again. The approvals view's `history` gives a revocation of an operating policy `permission_epoch_raised`, and while it is `false` also the `idempotency_key` and `expected_version` it was sent with, so the page can send the same request again after a reload; every other history row leaves the three `null`. On a database at `0008` the risk view's open risk takes the mandate's stop (B4's read of `decision_stop_updates` failed there; [ExecPlan 0026 §17](../plans/0026-m7-agent-driven-main-decisions.md#17-decision-log), B8b decision 9). Since B8b the browser reaches `/v1/approvals` for the policy, `/v1/agent-approvals` for a promotion, `/v1/experiments` with `strategy_id`, `GET /v1/entry-pauses` and the resume with its key read through same-origin server functions.

## M8 update 1: one switch and the agents' check (ExecPlan 0031)

[ExecPlan 0031](../plans/0031-m8-simple-app-that-runs-itself.md#9-implementation-sequence) update 1; the behavior is in [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-the-agents-check-the-usage-limit-and-one-switch-execplan-0031). The routes need migration `0009` or later, as before (`0010` is accepted beside it).

- `POST /v1/agent-runtime/enable` with target `ENABLED` no longer answers `409 CAPABILITY_UNVERIFIED`: it needs the approved profile only and is recorded `ACCEPTED`. Without a matching verification the worker applies it as `PROBE_ONLY` with reason `CHECK_PENDING`; the outcome (`GET /v1/agent-runtime/requests/{key}`) is `REQUEST_APPLIED` with `state` and `requested`.
- `GET /v1/agent-runtime` gains:
  - `actions.turn_on`: an approved profile exists and the switch is off (the on side of the switch; `actions.disable` is its off side);
  - `switched_on` (`ENABLED`, or `PROBE_ONLY` not held by the owner) and `switch_profile_sha256` (the newest approved, current profile the switch turns on);
  - `check`: the newest agents' check (`run`: `id`, `state` `QUEUED`, `RUNNING`, `PASSED`, `FAILED` or `CANCELED`, times, `policy_id`, `calls_used`, `calls_budget`, and each case's `case` `SC-01` or `SC-02`, `passed` and `problems`) and `entries` (`OPEN` or `WAITING` for the operating policy's live run, null without one);
  - `usage_limit`: null, or the block in force (`since`, `attempt`, `retry_at`, `last_refusal_at`).
  - A probe run's `suite` takes `CHECK`.
- `POST /v1/agent-runtime/probe` and `POST /v1/agent-runtime/decision-probe` stay as an on-request diagnostic (ExecPlan 0031 §4.7); the web app no longer offers them. (Both removed by [ExecPlan 0034](#cleanup-routes-nothing-calls-are-removed-execplan-0034).)
- A decision start (`/v1/agent-workflows`, `PORTFOLIO_DECISION_V1`) and the worker refuse `CHECK_PENDING` where they refused `DECISION_SUITE_NOT_VERIFIED`, and only while the run has nothing to exit.
- `SystemStatus.decisions` reads from `0009` or later.

## M8 update 2: in-force records (ExecPlan 0031)

[ExecPlan 0031](../plans/0031-m8-simple-app-that-runs-itself.md#9-implementation-sequence) update 2; the behavior is in [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-in-force-records-the-model-table-and-pauses-that-end-execplan-0031). Every field below reads on a database before `0011` too (an absent `actor` reads `OWNER`).

- **Who recorded a state.** An approval record (`/v1/approvals`, `/v1/agent-approvals`) gains `actor`, `OWNER` or `SYSTEM`; a definition's `state_by`, a policy's `approval_by`, a research envelope's `state_by`, a promotion decision's `actor` and a runtime profile's `approval_by` say the same of the latest record. A `SYSTEM` record is the app recording what the installed code ships; it never names the owner.
- **The runtime profile.** `POST /v1/agent-runtime/profiles` (the owner's compose) is removed. `POST /v1/agent-approvals` with `target_kind` `RUNTIME_PROFILE` answers `409 PROFILE_RECORDED_BY_THE_APP`. A profile view's `source` takes `SYSTEM`, and it gains `roles` (each `role`, `model`, `reasoning_effort` and `preference`, 1 being the model table's first choice); `model` and `reasoning_effort` stay for an older profile's one pair and are null on version 4. `unset` may name `MODEL_TABLE_UNRESOLVED:<role>`.
- **Kept as a recovery lever, with no page offering them:** the owner's approval routes for definitions, manifests, the research envelope, source versions and promotions, and the owner's resume of an entry pause. The pages show history only.
- `GET /v1/agent-runtime` events take `PROFILE_IN_FORCE`. Experiment events take `CAUSE_CLOSED` with actor `SYSTEM` and no request, and `RESUMED` with actor `SYSTEM`; incidents take `INTEGRITY_CLEARED`.

## M8 update 3: the run the app keeps going (ExecPlan 0031)

[ExecPlan 0031](../plans/0031-m8-simple-app-that-runs-itself.md#9-implementation-sequence) update 3; the behavior is in [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-the-main-run-the-app-keeps-going-execplan-0031). No route is added or removed; the owner's experiment routes keep their rules.

- **`GET /v1/experiments`.** Each item gains `strategy_id` (the manifest's strategy slot, null when unset) and `created_by` (`OWNER` or `SYSTEM`, the actor of its first `CREATED` event; a run before `0012` reads `OWNER`). The list gains `next_run`: `strategy_id`, the main policy in force (null when none), and `cost_scenario_id`, the newest forward run's; the page's new run starts from them.
- **`GET /v1/experiments/{id}`.** `requests` lists the app's start and stop beside the owner's, each with `actor`; `kept_by_app` is true for a run of a main policy of this build, whose start the app requests itself, and then `actions.start` is false. Pause, resume, flatten, stop and discard stay the owner's as before.
- **`GET /v1/approvals`.** A manifest gains `state_by` (who recorded its latest state) and `kept_by_app` (the app records it in force and starts the run). The owner's manifest decision stays a route; the page offers it only for a run of the reference.
- **Run requests.** A control request view (`POST /v1/experiments/{experiment_id}/{action}`, `GET /v1/experiments/{experiment_id}/requests/{key}` and the detail's `requests`) carries `actor`. Experiment events take `CREATED`, `MARKED_READY`, `DISCARDED`, `START_REQUESTED` and `STOP_REQUESTED` with actor `SYSTEM`; a `SYSTEM` stop's detail has `flatten` false and `reason` `POLICY_SUPERSEDED`, a discard's `reason` `CODE_IDENTITY_CHANGED` or `POLICY_SUPERSEDED`.
- **`GET /v1/policies`.** `AGENT_POLICY_V2` is listed, installable and in force once the update has run.

## M9 update 2: what came of each trigger (ExecPlan 0032)

[ExecPlan 0032](../plans/0032-m9-news-and-events-the-agents-trade-on.md#53-what-came-of-it-update-2) update 2; the behavior behind the counts is in [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m9-runtime-news-and-price-moves-start-investigations-execplan-0032). One read is added; no write is added or removed.

- **`GET /v1/trigger-results`** follows the rules of the [M7 owner routes](#m7-owner-routes-execplan-0026-b7): owner session, `Cache-Control: private, no-store`, no query parameter (any is `422`), `503 DECISION_SCHEMA_PENDING` before migration `0009`, `503 TRY_AGAIN` on a timeout. The browser reads it only through the same-origin `GET` server function of `apps/web/src/decisions/` ([FRONTEND](FRONTEND.md#m9-update-2-what-came-of-each-trigger-execplan-0032)).
  - `mode`: the main mode (`FORWARD_PAPER`; `OFFLINE_TEST` only in a disposable test database with the offline flag). `at`: the database's clock at the read. `labels`: `COUNTED_FROM_THE_RECORDS_AS_STORED`, `EACH_DECISION_COUNTED_ONCE_UNDER_THE_TRIGGER_IT_CONSUMED`, `MODELED_PAPER_FILLS`, `RESULTS_AFTER_FEES`, `SEGMENTS_DIFFER_IN_MARKET_CONDITIONS`, `NO_PROFITABILITY_CLAIM`.
  - `segments`: the newest six runs of an agent-driven policy in that mode that the engine started (a run with an `ACTIVATED` event), newest first; a draft is none. Each has `run_id`, `run_state`, `policy_id`, `policy_sha256`, `created_at`, `first_trigger_at` and `last_trigger_at` (null before its first trigger), and `kinds`.
  - Each of `kinds` is one `kind` (`HOURLY_BAR`, `POSITION_EVENT`, `FEED_ITEM` and `PRICE_MOVE` always; `MARKET_BRIEF`, `OWNER` and `OTHER` only when counted) with `triggers` (of which `waiting` and `canceled`), `refused` (`daily_cap`, `stale`, `superseded`, and of the drafts `review` and `engine`, `other`), `decisions` (of which `acted`, `abstentions` and `decisions_open`), `submitted` (`entries`, `exits`, `adjustments`), `positions` (`opened`, `closed`, and `realized_pnl`, the exact decimal string of the closed ones after fees) and `tokens` (`input`, `output`, `calls`, `calls_without_usage`). A decision is counted once, under the trigger it consumed; a reviewed assessment takes the kind of the investigation or brief behind it; an owner's decision counts under `OWNER`.
  - `feeds`: each source of the registry that is not a fixture, by `source_id` with its `name`, then `PRICE_MOVES` (the price-move check, `name` and `items` null), each with `items` (stored, since the feed started), `triggers` (of which `waiting` and `canceled`), `refused` (why a trigger started no investigation: `daily_cap`, the investigations' own daily cap; `stale`; `investigation_open`, one already open for the same feed and symbol, or for a price move of the same symbol; `other`), `investigations`, `acceptable` (the review found the assessment acceptable), `decisions` (started from those assessments), `acted` (of those decisions, the ones that submitted at least one intent to the engine, an entry, exit, stop tightening or cancel, whatever the engine answered) and the investigations' `tokens`. In `kinds`, `acted` counts the same way.
- **`GET /v1/agent-runtime`** gains `budgets_v4`, generation 4's code-owned budgets (`daily_by_purpose.INVESTIGATION` 16, the two templates' own budgets). A profile's bound values sit under the same key.
- **Agent workflow and trigger views** take the template `EVENT_INVESTIGATION_V2` with its child `ASSESSMENT_REVIEW_V3`, the trigger family `PRICE_MOVE` and the creator `SYSTEM` for an investigation of a price move ([DATA_CONTRACTS](DATA_CONTRACTS.md#migration-0014_m9_agents-update-2)).

## M10 update 1: the coin watchlist (ExecPlan 0033)

[ExecPlan 0033](../plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#51-update-1-the-watchlist-and-the-coin-notes) update 1; the scan and the notes behind it are in [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m10-runtime-the-coin-notes-execplan-0033) and their records in [DATA_CONTRACTS](DATA_CONTRACTS.md#m10-records-execplan-0033). One read is added; no write is added or removed.

- **`GET /v1/coins`**: owner session, `Cache-Control: private, no-store`, no query parameter (any is `422`), `503 TRY_AGAIN` on a timeout. It answers `200` in every state, read as the API identity in one repeatable-read snapshot. The browser reads it only through the same-origin `GET` server function of `apps/web/src/coins/` ([FRONTEND](FRONTEND.md#m10-update-1-the-coins-page-execplan-0033)).
  - `state`: `READY` (a successful scan exists), `NO_SCAN_YET` or `SCHEMA_PENDING` (before migration `0015`; every other field empty). `labels`: `FIGURES_COMPUTED_IN_CODE_FROM_BINANCE_DAILY_BARS`, `PAST_VALUES_NOT_A_FORECAST`, `NOTES_MODEL_AUTHORED_UNTRUSTED`, `RESEARCH_ONLY_NO_COIN_ADDED_TO_TRADING`. `schedule`: the rules' `daily_from_utc`, `retry_after_minutes` and `attempts_per_utc_day`. `notes_today` (note workflows started since 00:00 UTC plus those queued, as the cap counts them) and `notes_per_day` (generation 5's cap).
  - `scan`: the newest successful scan, `id`, `rules_sha256`, `started_at`, `completed_at`, `weight`, `requests`, `usdt_pairs` and `walked` (the pairs it recorded); null before the first. `last_attempt`: the newest attempt when it is not that scan (`id`, `started_at`, `state`, `failure`), else null; so a later failure is shown beside the earlier watchlist, never in its place.
  - `watchlist`: the scan's eight by `rank`, each `symbol`, `base_asset`, `figures` (`median_quote_volume_30d`, `quote_volume_24h`, `spread_bps`, `last_close`, `return_7d`, `return_30d`, `return_90d`, `vs_btc_7d`, `vs_btc_30d`, `vs_btc_90d`, `volatility_30d`, `atr14_fraction`, `correlation_btc_90d`, `correlation_sol_90d`, each exact decimal text or null), `note_in_progress` (a note workflow of that coin is queued or being written; once it waits for its review, the note and its review show instead) and `note`: the coin's newest note in the main mode, from any scan, or null. A note has `workflow_id`, `artifact_id`, `scan_id`, `created_at`, `label`, `summary`, `uncertainty`, `unknowns`, `worth_trading_if`, `rule_out_if` and `review` (`state` of the review workflow, `verdict` or null, `created_at`; null before the review starts). Every note field is model-authored text.
  - `left_out`: the scan's other pairs by `position` (place by 24-hour quote volume), each `symbol` and `reason` (the sixteen codes of the rules).
- **`GET /v1/agent-runtime`** gains `budgets_v5`, generation 5's code-owned budgets (`daily_by_purpose.COIN_NOTE` 3, the two templates' own budgets). A profile's bound values sit under the same key.
- **Agent workflow and artifact views** take the purpose and the artifact kind `COIN_NOTE`, the templates `COIN_NOTE_V1` and `COIN_NOTE_REVIEW_V1` and the creator `SYSTEM` for a note.

## Cleanup: routes nothing calls are removed (ExecPlan 0034)

The owner asked for a cleanup of leftovers on 2026-10-20 ([DECISIONS](../../DECISIONS.md)). These routes had no caller in the web app, the workers or the update file, and are removed; `openapi.json` and the web's generated types are regenerated from the code. The sections above keep their history.

- `POST /v1/agent-runtime/probe`, `POST /v1/agent-runtime/decision-probe` and `GET /v1/agent-probes`. The agents' check (M8 update 1) is what the app runs; probe runs still show in `GET /v1/agent-runtime` (`probe_runs`).
- `POST /v1/agent-workflows` (the owner's Start). The app starts the agents' work itself since M8; `GET /v1/agent-workflows`, `GET /v1/agent-workflows/{id}`, `GET /v1/agent-workflows/requests/{key}` and `POST /v1/agent-workflows/{id}/cancel` stay.
- `GET /v1/account/funding` and `POST /v1/account/reconcile`. The account page reads `GET /v1/account`; reconciliation itself is unchanged and still runs where the workers and the update file run it.
- The `boundary-check` action of `python -m app.execution.identity` (the M7 boundary, done on 2026-10-19).

`POST /v1/agent-approvals` and `GET /v1/agent-approvals/requests/{key}` stay although no page calls them: they are the owner's recovery lever to reject or revoke what the app recorded ([AUTONOMY_MATRIX](AUTONOMY_MATRIX.md)).

## M10 update 2: five coins (ExecPlan 0033)

[ExecPlan 0033 §5.2](../plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#52-update-2-three-more-coins-on-paper-only-with-the-owners-yes). No route is added or removed; `openapi.json` and the web's generated types are regenerated from the code.
- **Coins.** Every `symbol` enum (markets, quotes, candles, orders, fills, positions, decisions, risk) admits `BTCUSDT`, `SOLUSDT`, `ZECUSDT`, `NEARUSDT` and `XRPUSDT`, every base `asset` enum `BTC`, `SOL`, `ZEC`, `NEAR` and `XRP`, and every ledger asset (`asset`, `fee_asset`, `reserved_asset`) those and `USDT`. The lists come from `app/markets.py`; a test compares the API's with the code's. A query parameter naming any other coin is still `422`.
- **Holdings.** `GET /v1/account` lists a holding for each of the five coins, a new coin at zero until it is bought.
- **`GET /v1/agent-runtime`** gains `budgets_v6`, generation 6's code-owned budgets. Without it the response model refused its own view (`extra_forbidden`); a test reads the view with every generation's budgets.


## Five pages: routes the web no longer calls (ExecPlan 0035)

[ExecPlan 0035 §4.4](../plans/0035-a-simpler-app-that-trades-by-itself.md#44-api). No route is added, removed or changed, so `openapi.json` and the web's generated types stay as they are (`pnpm run api:check`). The web calls none of these since their pages went; they stay, unused, until [ExecPlan 0034](../plans/0034-app-cleanup.md)'s part 3:

- Research: `GET /v1/research/status`, `/v1/research/hypotheses`, `/v1/research/datasets`, `/v1/research/experiments` with `/{id}` and `/{id}/cells/{cell}`, `/v1/research/candidates` with `/{id}`, `/v1/research/shadows` and `/v1/research/requests/{key}`; `POST /v1/research/jobs/{id}/cancel` and `/v1/research/shadows/{id}/stop`.
- `GET /v1/promotions` and `GET /v1/agent-approvals`.
- Evidence and sources: `GET /v1/evidence` with `/{id}`, `GET /v1/sources` and `/v1/sources/requests/{key}`; `POST /v1/sources/{id}/refresh`.
- `GET /v1/policies`.
- `GET /v1/agent-workflows`, the list; a workflow's page still reads `GET /v1/agent-workflows/{id}`.
- The approval writes, which no page offers: `POST /v1/approvals` and `GET /v1/approvals/requests/{key}`. Like `POST /v1/agent-approvals` (above), they stay as the owner's recovery lever. `GET /v1/approvals` is still read: a new run takes its cost scenarios from it.

`GET /v1/system/status` keeps its `research` field; the web neither shows it nor counts it in Home's trading status. Once the retired bridge's last storage observation ages out, the field reads `unavailable`.

## M11 update 2, part A: the BTCUSDT perpetual's market data (ExecPlan 0039)

[ExecPlan 0039 §5.2.1](../plans/0039-bitcoin-futures-on-paper.md#521-part-a-as-built-2026-10-24). Two owner reads, each behind the owner's session, `Cache-Control: no-store`, and `422` for any query parameter not named here. `openapi.json` and the web's generated types are regenerated from the code. Every price, quantity and rate is exact decimal text as Binance sent it; every time is UTC ISO 8601. Each answer carries the `labels` `PROVIDER_VALUES_AS_RECEIVED`, `LONGER_CANDLES_CALCULATED_FROM_1M`, `DISPLAYED_LIQUIDITY_ONLY` and `NOT_EXECUTABLE`: nothing here is a fill or a mark of the spot account.
- **`GET /v1/perp/market`**: `state` `READY`, or `SCHEMA_PENDING` until migration `0019` is applied (then the status is `UNAVAILABLE` with reason `SCHEMA_PENDING` and every part null); `symbol` `BTCUSDT`; `evaluated_at`; the feed's `status` (`STARTING`, `CONNECTED`, `DEGRADED`, `UNAVAILABLE`) and `reason`, whether each stream is connected and `heartbeat_at`. A heartbeat older than 10 s makes the status `UNAVAILABLE` with reason `FEED_SILENT`, whatever the feed last wrote. Then the newest `book` (best bid and ask with their quantities, `bids` and `asks` as `[price, quantity]` pairs, event and receipt times, `age_seconds`), the newest `mark` (mark, index, current funding rate, next funding time, receipt time, age), `last_funding` (the newest settled rate and its time), the `clock` (verified, offset, uncertainty, checked) and the `instrument` (status, usable, tick, step, minimum quantity, minimum notional, checked), each null until there is one.
- **`GET /v1/perp/candles?interval=&limit=`**: `interval` `1m` (default), `5m`, `15m` or `1h`; `limit` 1 to 1,000 (default 500). The newest `limit` candles, oldest first, built from the stored 1-minute candles: `open_ms`, open, high, low, close, volume, `minutes` (the minutes stored) and `expected_minutes`, and `complete` (every minute stored and final). An interval with no stored minute has no candle. `SCHEMA_PENDING` with no candles until `0019`.

## M11 update 2, part B: the futures account (ExecPlan 0039)

[ExecPlan 0039 §5.3.1 and §5.7](../plans/0039-bitcoin-futures-on-paper.md#531-part-bs-design-2026-10-24). Every route needs the owner's session, answers `Cache-Control: no-store`, and refuses with `422` a query parameter not named here; every answer is `READY`, or `SCHEMA_PENDING` until migration `0020` is applied. Amounts are exact decimal text. `openapi.json` and the web's generated types are regenerated from the code. The engine posts every amount; these routes only read, and the one write only asks.
- **`GET /v1/futures`**: the account (wallet, margin reserved, available, contributions, equity at the mark, NAV, high-water NAV, whether an integrity hold is on, the newest valuation with its quality), the newest run (state, causes, who started it, start equity, its own high-water NAV and drawdown, stop reason), the open position, the newest mark with its age (`fresh` when at most 5 s old: the unrealized P&L shown is a display at that mark, never what the engine values), the day's limits and results, the open latches, the owner's requests not yet answered, and the policy in force with its hashes and the cost model's.
- **`GET /v1/futures/trades?cursor=&limit=`**: positions newest first (side, leverage, quantity, entry, notional, margin, first and current stop, take-profit, liquidation price, time exit, exit, realized P&L, fees, funding, net), 25 by default.
- **`GET /v1/futures/trades/{position_id}`**: one position with its fills (kind, reason, order side, price and the walked average, slippage, fee and rate, the book levels used, the quote's second or the mark), its funding payments (`PENDING` or `POSTED`) and the trader's decisions about it; `404` `TRADE_NOT_FOUND`.
- **`GET /v1/futures/decisions?cursor=&limit=`**: the trader's workflows newest first, with the trigger, the decision (action, choices, rationale, reason code, invalidation, uncertainty, the context's time, the position it saw) and the engine's answer (`FILLED`, `APPLIED`, `NOTED` or `REFUSED` with codes).
- **`GET /v1/futures/activity?after=`**: the toasts' feed. Without `after`, only the cursor (the newest ledger sequence), so a new tab shows nothing old; with it, the fills and funding payments posted after it, one item each, the newest 20 oldest first, and how many there were in all. Since [ExecPlan 0047](#execplan-0047-live-trades) the live stream sends the same answer as its `activity` event.
- **`GET /v1/futures/markers?since_ms=`**: the chart's marks: the fills since the chart's first candle (at most the newest 500) and the open position's entry, stop, take-profit and liquidation price.
- **`POST /v1/futures/requests`** `{kind, run_id, close_position, idempotency_key}`: the owner's `PAUSE`, `RESUME`, `STOP` (with `close_position` only) or `START` (no run), written as a request the engine answers in its next step; idempotent by key, a different body under the same key is `409` `IDEMPOTENCY_CONFLICT`. Refusals: `422` `UNKNOWN_REQUEST`, `RUN_REQUIRED`, `START_TAKES_NO_RUN`, `CLOSE_ONLY_WITH_STOP`; `409` `RUN_LIVE`, `NOT_FUNDED`, `RUN_NOT_LIVE`, `RUN_CHANGED`, `FUTURES_SCHEMA_PENDING`. Audited as `FUTURES_<KIND>_REQUESTED`.
- **`GET /v1/futures/requests/{key}`**: a request and its answer (`PENDING`, `APPLIED` or `REJECTED` with reasons); `404` `REQUEST_NOT_FOUND`.
- **Changed answers.** The account view's `valuation_source` adds `FUTURES_VALUATION`; the agents' runtime view adds generation 7's budgets; while futures trade, the system status's feeds and the agents' "new entries" read the perpetual and the futures run.

## No owner sign-in (ExecPlan 0042)

[ExecPlan 0042](../plans/0042-no-owner-sign-in.md), the owner's decision of 2026-10-25 ([DECISIONS](../../DECISIONS.md#2026-10-25--no-owner-sign-in-and-no-setup-execplan-0042)). `openapi.json` and the web's generated types are regenerated from the code.
- **One identity.** Every route that needed `X-Internal-Key` and `X-Owner-Session` needs `X-Internal-Key` only; without it (or with a wrong one) the answer is still `401` `{"detail": "unauthorized"}`, and `503` while the key file cannot be read. No route reads `X-Owner-Session`. The web's server functions are the only holder of the key, and the web answers only on `127.0.0.1:3000` with its Host, Origin and CSRF checks.
- **Removed** (`404`): `GET /v1/owner/status`, `POST /v1/owner/bootstrap`, `/login`, `/logout`, `GET /v1/owner/session`, `GET /v1/account/initialization/draft` and `POST /v1/account/initialization/confirm`.
- **The initial contribution is the app's.** The API funds an account nothing has funded when it starts, once: the request `SYSTEM:INITIALIZE` of exactly 10,000 virtual USDT, posted as the owner's confirmation posted it, with no owner decision; `GET /v1/account/requests/SYSTEM:INITIALIZE` reads it (the one key read outside the owner's key pattern). Nothing is posted while the reconciliation has failed or the account is paused; while the start's attempt is refused, or held for a valuation, the API tries again every minute until it posts.
- **Top-ups stay the owner's.** `POST /v1/account/topups/draft` answers `kind` `TOPUP` only. `POST /v1/account/topups/{request_id}/cancel` refuses a pending initial contribution of an account not yet funded with `409` `INITIAL_FUNDING_NOT_CANCELABLE` (nothing else could fund it); an initialization left pending beside a funded account can be canceled, a cancel sent again answers as before, and retry works as before.
- **`GET /v1/account/workspace`** answers `{account, funding}`.
- **Owner records** (`OWNER` rows of approvals, runtime requests, pause and refresh requests, workflows, profiles) carry no session: `session_id` is `NULL`, and a row written before keeps its value.
- **The agents' switch** is on while the owner has made no switch request (`switched_on` is true for the runtime in its first state then); the owner's Turn off stays final until the owner's Turn on. In the first state `actions.disable` is offered once the app has the profile in force, which `actions.turn_on` needs afterwards.
- **Before migration `0021`.** The update replaces the API first, while the schema is `0020`, whose checks want a session on every owner row: until the migration the routes that record one (`POST /v1/agent-runtime/enable` and `/disable`, `/v1/agent-workflows/{id}/cancel`, `/v1/agent-approvals`, `/v1/approvals`, `/v1/sources/{id}/refresh` and `/v1/entry-pauses/{id}/resume`) answer `503` `OWNER_SCHEMA_PENDING` (`retryable`) and record nothing. The reads, the futures controls and top-ups answer as usual.

## ExecPlan 0040: each trade's review and the coach's note

[ExecPlan 0040 §4.7](../plans/0040-trade-reviews-and-a-coach.md#47-the-pages). One new read and new fields on three, with the futures routes' access, `Cache-Control: no-store` and `422` for any query parameter not named; `openapi.json` and the web's generated types are regenerated from the code. Until migration `0022` is applied every trade's `review` is null and the coach's read is `SCHEMA_PENDING`. A closed trade whose fact sheet is not built yet is `PENDING`, and `NOT_REVIEWED` 48 hours after its close; once the sheet is stored its state is the reviewer's ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m11-generation-8-trade-reviews-and-a-coach-execplan-0040)). A review's and a note's words are the models' and are labeled so; every number is code's.
- **`GET /v1/futures/coach`**: `state` (`READY`, `SCHEMA_PENDING`), `evaluated_at`, `note_state` (`IN_FORCE`, `EXPIRED`, `NONE`), the `note` in force (ID, recorded and expiry times, lean, setup, avoid, `confidence` with `confidence_given` and `confidence_held_low`, `reviewed_trades`, and each `cited` review or scoreboard row with code's figures) or null, `last_expired_at`, `advice_use` (for `FOLLOWED`, `PARTLY`, `IGNORED` and `NO_ADVICE`, the trades' tallies over 7 days and over all: count, wins, losses, flats, average R, net P&L and `few` under 5 trades), `conclusion_at` (20) and `conclusive` (both followed and ignored have that many), `reviews` (how many closed trades are `REVIEWED`, `PENDING`, `FAILED` and `NOT_REVIEWED`, counted as the Trades list shows them), and `labels`.
- **`GET /v1/futures/trades`**: each trade gains `review`, null while it is open: its `state`, `fact_sheet_id`, the result class and R from the sheet, and once reviewed `reviewed_at`, `grid`, `decision_quality`, `tags` and `lesson`.
- **`GET /v1/futures/trades/{position_id}`**: `review` adds the review's ID, `entry_reason_held` with its line, `invalidation_seen`, each factor with its evidence (`FACT` with the value the sheet holds, `FEED_ITEM` with its title, labeled as publisher text, or `MISSING`), the sheet's `facts` (net P&L, risk, R, result, worst and best price with their R before costs, minutes held, the 1-hour trend at entry and what was `omitted`) and the label.
- **`GET /v1/futures/decisions`**: each decision gains `advice_use` and `advice_note`, null for generation 7's decisions.
- **Changed answers.** The agents' runtime view adds generation 8's budgets (`budgets_v8`).

## ExecPlan 0041 part 1: the twins and the league table

[ExecPlan 0041 §4.2 and §4.4](../plans/0041-twins-and-a-veto.md#42-the-league-table-code). Three reads, with the futures routes' access, `Cache-Control: private, no-store` and `422` for any query parameter not named; `openapi.json` and the web's generated types are regenerated from the code. Until migration `0023` is applied each answers `SCHEMA_PENDING` with nothing else. Every amount is the engine's decimal string; the twins are isolated paper accounts, labeled so.
- **`GET /v1/futures/league`**: `state`, `evaluated_at`, the `set` (its ID, hash, `in_force` (the stored row equals the code), the start equity, the gate's multiple, the filter's rate, the minimum paired days and trader closed trades, the bootstrap's block, resamples and confidence), `accounts` (the trader's newest run, then each twin's newest segment: its state, segment, start and end with the reason, its fault's code and error class, the start equity, `net_pnl` after fees and funding (the open position's unrealized P&L at its newest valuation; null while that valuation is invalid), `return_fraction`, `valued_at`, `valuation_quality`, `trades`, `closed_trades`, `position_open`, `fees`, `funding_paid`, `funding_received`, `funding_pending`, `funding_owed` (a twin's settled payments waiting for its free wallet, counted in `net_pnl`; the trader's `0`), `max_drawdown` from its own high, `time_in_market` and BTC's own `btc_change` over the same window), `comparisons` (for each twin over the window both share: `TOO_FEW` or `READY`, the window, `days_in_window`, `days_paired`, `days_left_out`, `trader_closed_trades`, and when `READY` the `mean_difference` of the paired daily log returns, the trader minus the twin, with its `lower` and `upper` bounds; the `seed` always) and `labels` (`PAPER_ONLY`, `ISOLATED_TWIN_ACCOUNTS_NOT_THE_OWNER'S_ACCOUNT`, `FIXED_RULES_NO_AGENT`, `MODELED_FILLS`, `CASH_IS_THE_ZERO_LINE`, `A_MEASUREMENT_NOTHING_IS_PROMOTED_OR_CHANGED`).
- **`GET /v1/futures/twins`**: `state`, the `set`, and each twin (`HOLD`, `TREND`, `TREND_GATED`) with its name, state (`NOT_STARTED` before its first segment), segment, latch causes, fault (`code` and `error` class only; the detail stays in the record), start and end, `last_bar_at`, `wallet_checked_at`, `position_open` and `late` (a live twin with no bar read for more than 20 minutes after a bar's close, or after its start: its step is not running).
- **`GET /v1/futures/twins/{twin}/trades`** (`cursor`, `limit` up to 100; an unknown twin is `422`): the twin's positions, newest first, with the trader's columns (side, leverage, quantity, entry, notional, margin, stop and liquidation price, the ATR multiple, the time exit, risk, close reason and price, realized P&L, fees, posted funding and the pending count, the net result, the open one's unrealized P&L at a fresh mark), the gate's and the filter's verdicts, and `label` `ISOLATED_TWIN`; `next_cursor`.


## ExecPlan 0041 part 2: the veto twin, the momentum twin and the longer call rows

[ExecPlan 0041 §4.3 to §4.5](../plans/0041-twins-and-a-veto.md#43-the-veto-agent-update-2-entry_veto_v1-evaluator-generation-12). One new read and new fields on five, with the futures routes' access, `Cache-Control: private, no-store` and `422` for any query parameter not named; `openapi.json` and the web's generated types are regenerated from the code. Every count, interval and comparison is code's; the veto's note is the model's words, labeled so; nothing in a read changes a rule, a limit or an order.
- **`GET /v1/futures/twins/vetoes`** (`cursor`, `limit` up to 100, 25 by default): the veto twin's requests, newest first, each with its `request_id`, `seq`, `bar_open_ms`, `side`, `asked_at`, `deadline_at`, the `planned` price, stop, quantity and risk, the asked `quote` (its second, bid and ask) and `funding_rate`, the agent's `answer` (`verdict`, `reason`, `note`, `confidence`, `recorded_at`, `in_time`, recorded by the deadline, and `label` `MODEL_AUTHORED_NOTE`; null without one), what the twin `applied` (`GO`, `HALVE`, `VETO`, `NO_ANSWER`, `PENDING` while the twin is live and the deadline or a fresh quote is awaited, or `TWIN_ENDED` when the twin stopped or faulted before it applied one), the `outcome` (`FILLED` or `REFUSED` with its `codes`, `VETOED` or `BAR_TOO_OLD` among them), `applied_at`, `asking_cost` (`per_unit` and `bps`: the fill price against the planned one, positive when worse for the side), the `position_id`, and the agent's call: `workflow_state` and `terminal_reason` (`YIELDED_TO_DECISION` and the like), null when none started. `next_cursor`; `labels` (`PAPER_ONLY`, `THE_VETO_TWIN_IS_AN_ISOLATED_ACCOUNT`, `THE_NOTE_IS_MODEL_AUTHORED`, `THE_PLACEBO_AND_THE_INTERVAL_ARE_COMPUTED_IN_CODE`, `A_MEASUREMENT_NOTHING_IS_PROMOTED_OR_CHANGED`). Until migration `0030` is applied it answers `SCHEMA_PENDING` with no items.
- **`GET /v1/futures/league`**: the set gains `twins` (its twins in order: three before `0030`, five from it), and the answer gains `veto` (null until `0030`): the paired daily `interval` of `TREND_VETO` minus `TREND` over the window both share (as a comparison's, with `veto_closed_trades`), the newest `placebo` (`day`, `state` `DONE` or `FAILED` with its `error`, `computed_at`, the candidates `due`, `replayed`, `waiting` and `incomplete`, the `outcome` `TOO_FEW` under the `minimum` of 60, `BEATS_THE_STREAMS` or `DOES_NOT_BEAT_THE_STREAMS`, the verdict `counts`, the veto arm's and the trend arm's total R, the `streams`, how many the veto arm `beaten` and their share, the streams' low, median and high total R, the `seed` and its `label`), `newest_placebo_failed` (the newest attempt when it failed: it is tried again 15 minutes later), the `verdicts` applied so far, `pending`, and `success`: `TOO_FEW`, `SUCCESS` (the veto arm beats 95% of the streams and the paired interval is above zero) or `THE_VETO_ADDS_NOTHING`, with `minimum_candidates` and `labels`. An account is also `TREND_VETO` or `MOMENTUM_1W`.
- **`GET /v1/futures/twins`** and **`GET /v1/futures/twins/{twin}/trades`**: the two new twins; a twin's trade gains `veto` (`GO`, `HALVE` or `NO_ANSWER` for the veto twin's entries, null for the others) and `asking_cost` (as above, null for the other twins).
- **`GET /v1/futures/scorecard`**: each window's 4-hour and 24-hour checkpoints gain `direction`, as the 1-hour one's (null now only at 15 minutes), and the answer gains `call_checks`: for each checkpoint that judges the calls, its `minutes`, `too_few_below` (30, 120 and 720 judged calls) and the bootstrap's `mean_block` (4, 16 and 96 calls). No agent reads them.
- **Changed answers.** `GET /v1/agent-models` adds the `ENTRY_VETO` agent after the coach; the agents' runtime view adds generation 12's budgets (`budgets_v12`); workflow purposes and artifact kinds add `ENTRY_VETO`.

## ExecPlan 0043 update 1: what followed each decision

[ExecPlan 0043 §4.1 to §4.4](../plans/0043-score-every-decision.md#4-design). One new read and one new field, with the futures routes' access, `Cache-Control: private, no-store` and `422` for any query parameter not named; `openapi.json` and the web's generated types are regenerated from the code. Every score is code's hindsight on modeled test trades, from `futures_decision_scores` read as the API identity in one repeatable-read snapshot; nothing in a read changes a rule, a limit or an order. Percent values are the engine's decimal strings in percent (`0.2500` is 0.25%), not fractions.
- **`GET /v1/futures/decisions`** and a trade's `decisions` (`GET /v1/futures/trades/{id}`): each item has `scores`, null for a job without a decision and until migration `0024` is applied; otherwise `headline_minutes` (60), `executed` (false when the engine refused the action: it is scored as decided; null when the engine never answered it) and one entry per checkpoint (15, 60, 240 and 1,440 minutes) with `due_at`, `state` (`SCORED`, `INCOMPLETE` with its `reason` (`MISSING_CANDLES`, `MISSING_FUNDING`, `NO_ATR`, `NO_ANSWER`, `JOB_UNFINISHED`, `SCORE_FAILED`), or `PENDING`, not stored yet), the `label` (§4.2's), and `move_percent`, `long_net_percent`, `short_net_percent` and, for a decision that saw a position, `advantage_percent` (holding against exiting at the reference).
- **`GET /v1/futures/scorecard`**: `state`, `evaluated_at` (the database's clock), the `scorer` (the definition in force's ID and hash, `DECISION_SCORING_V2` since migration `0034` ([ExecPlan 0054](../plans/0054-the-scorer-expects-the-schedule-and-a-second-usage-signal.md)), `in_force` (the stored row equals the code), `since` (the first run's start), the stored `scored` and `incomplete` counts, `newest_at`, `waiting_decisions` and `waiting_bars` (past their hour by more than ten minutes without its score) and `state`: `CURRENT`, `WAITING`, `NO_RUN` or `NOT_STORED`), `windows` (`24H`, `7D`, `ALL`, each with its `since` and, per checkpoint, the decisions' label counts and shares, the `incomplete` count, the bars' base rate (how often the long and the short test trade paid, and their average net), the missed bars (bars without a decision while the trader was expected to decide, since V2 only at the schedule's four-hour moments: their count, why, the flat waits' labels and the count in a position), the window's ATR thirds and the same counts by condition: the 1-hour trend, the ATR third, the UTC hours, the funding rate's sign, the trader's reason code and uncertainty level; a row under `too_few_below` (30) says `too_few`), `disagreements` (the last 7 days' bars where the trader or a twin entered while the other, flat, waited (a trader's entry the engine refused is not a wait): per twin the counts, entries on the right side, on the wrong side or costs only, and not scored yet; then the newest 20 bars with who entered, the side, the trader's action and each one's 1-hour label), `subjects`, `checkpoints`, `headline_minutes`, `too_few_below` and `labels` (`HINDSIGHT`, `MODELED_TEST_TRADES`, `NOTHING_IS_CHANGED_BY_THIS_SCORECARD`). A scorecard as of a time reads only the scores recorded by then. Until migration `0024` is applied it answers `SCHEMA_PENDING`, with no scorer, windows or disagreements.

## ExecPlan 0043 update 2: the agents read the decision scores

[ExecPlan 0043 §4.5](../plans/0043-score-every-decision.md#45-the-agents-update-2-generation-9). New fields on four reads, with the futures routes' access and `422` for any query parameter not named; `openapi.json` and the web's generated types are regenerated from the code. The forecast is a choice from a fixed list, its verdict and every count are code's, and a decision review's judgments, notes and lesson are a model's words, labeled so; nothing in a read changes a rule, a limit or an order.
- **`GET /v1/futures/decisions`** and a trade's `decisions`: each decision gains `expected_move` (`UP`, `DOWN`, `NO_VIEW`; null before generation 9), and its `scores` gain `call`, code's verdict on the forecast at the 1-hour checkpoint: `RIGHT` (the 1-hour close more than 0.12% beyond the reference in its direction), `WRONG` (more than 0.12% the other way), `NEITHER` (within the band), `NO_VIEW`, or null without a forecast or before its hour is scored.
- **`GET /v1/futures/scorecard`**: each window's 1-hour checkpoint gains `direction` (null at the other checkpoints): `calls` (right, wrong and neither), `right`, `wrong`, `neither`, `no_view`, `hit_rate_percent` (right of right and wrong), `too_few` (fewer than 30 judged), `interval_percent` (the hit rate's 95% stationary block bootstrap interval, mean block 4 calls, 2,000 resamples, seeded from the scoring definition's hash and the window; null while too few), `coin_flip_percent` (`50.00`), `band_percent` (`0.12`) and the same by uncertainty level (`by_uncertainty`).
- **`GET /v1/futures/coach`**: `decision_reviews`, null until migration `0025` is applied: `latest` (the newest `DECISION_REVIEW`: its ID, day, recorded time, lesson, `knowable` counts, label and its cases, each with code's `kind` (`MISS`, `WORST`), label, rank, `size_percent`, time, action, position before, `executed`, forecast and `move_1h_percent`, and the reviewer's `knowable`, `tag`, `evidence` paths and `note`) or null, and `days` (each due UTC day since the first run started, newest first, at most 7, with its `state`, `REVIEWED`, `PENDING`, `FAILED`, `NOT_REVIEWED` or `NO_CASES`, and `due_at`, 01:30 UTC the day after; a day without a case stays `PENDING` while one of its decisions has no 1-hour score stored, and is `NO_CASES` once all have or 48 hours after it fell due). A note's `cited` items gain two kinds and the field `windows`, null for every other kind: `DECISION_REVIEW` (its ID, day, number of cases and `knowable` counts) and `SCORECARD_ROW` (its key, `windows`, the row's counts as the coach read them, one per window `24H` and `7D` with `window`, `count`, `too_few`, and for the direction calls `right`, `wrong` and `hit_rate_percent`, else null, and the row's hash `row_sha256`).
- **Changed answers.** The agents' runtime view adds generation 9's budgets (`budgets_v9`); workflow purposes add `DECISION_REVIEW` and artifact kinds `DECISION_REVIEW`.

## ExecPlan 0044: a trader that commits

[ExecPlan 0044 §4](../plans/0044-a-trader-that-commits.md#4-design). No route, field or answer of the futures reads changes: a generation-10 decision is read as generation 9's, with its forecast and its verdict. The agents' runtime view adds generation 10's budgets (`budgets_v10`); `openapi.json` and the web's generated types are regenerated from the code.

## ExecPlan 0045: where the results come from

[ExecPlan 0045 §4.5 and §4.8](../plans/0045-where-the-results-come-from.md#4-design). One new read and one new field, with the futures routes' access, `Cache-Control: private, no-store` and `422` for any query parameter not named; `openapi.json` and the web's generated types are regenerated from the code. Every number is code's hindsight on trades modeled on 1-minute candles, read as the API identity in one repeatable-read snapshot; nothing in a read changes a rule, a limit or an order.
- **A trade's `costs`** (`GET /v1/futures/trades`, `GET /v1/futures/trades/{id}`, and a twin's trades, `GET /v1/futures/twins/{twin}/trades`): null for an open position; for a closed one, computed at read from its stored fills and funding (`COMPUTED_AT_READ_FROM_THE_FILLS`): `fees`, `slippage` (each fill's quantity times its distance from the best level it took; a liquidation on the mark has none), `funding` (received positive), `costs` (fees plus slippage minus funding), `share_of_risk` (costs over the risk at the stop, to four places; null for the hold twin, which has no stop) and `r_before_costs` (net R plus that share). For the trader only, from the entry's fact sheet (null without one, and for a twin): `planned_share_of_risk`, the round trip `TWIN_SET_V1`'s gate would have priced at the entry (two taker fees, two slippage scenarios and the entry's spread) over the risk per unit, and `gate_would_refuse`, true when the stop's distance was under three such round trips. No stored row changes.
- **`GET /v1/futures/checks`**: `state`, `checks_id` and `checks_sha256` (`RESULT_CHECKS_V1`), `in_force` (the stored row equals the code), `result` (the newest `DONE` day, or null), `last_attempt` (the newest row, `DONE` or `FAILED`, with its `day`, `at` and `error`), `outcomes` (the bar outcomes `stored`, `incomplete`, the newest bar's open, the oldest bar past its 24 hours without its outcomes since the first run started, and how many wait) and `labels` (`PAPER`, `MODELED_ON_1_MINUTE_CANDLES`, `HINDSIGHT`, `NOTHING_HERE_CHANGES_A_RULE`). A `result` has its `day`, `computed_at`, `elapsed_ms`, the `window` (the trader's template, when its first decision was, its positions, the entries counted, those waiting, those incomplete and those outside generation 10's grid; in fill order, an entry counts once every bar of its UTC day is stored, and one that waits holds the later ones) and:
  - `luck_floor`: `state` (`TOO_FEW` under `minimum`, 30 entries, or `READY`), `entries`, `total_r`, `streams` (1,000), and a `primary` (a fair coin's side) and `secondary` (the trader's own side) row, each with the `percentile` (the share of streams below the trader's total, ties counted half, as a fraction), its `reading` (`ABOVE_THE_LUCK_FLOOR` at 0.95 or more, `BELOW_THE_LUCK_FLOOR` at 0.05 or less, else `INSIDE_THE_LUCK_FLOOR`) and the streams' median, 5th and 95th percentile totals;
  - `exits`: `state` (`TOO_FEW_TO_PICK`, with each exit's mean difference in R against the trader's in `by_exit`, or `PICKED`), the `pick` (the exit, its mean difference over entries 1 to 30, and their count) and its `check` on the later entries (their count, `minimum` 30, the mean difference, the 95% interval's bounds to four places, and `TOO_FEW`, `BETTER_BEYOND_LUCK`, `WORSE` or `NO_DIFFERENCE_SHOWN`), `early_exits` (the applied `EXIT` and `TIGHTEN_STOP` decisions with a 24-hour score: counts, their total gain over holding in R, and the count per label) and `calibration` (for entries that ended by their own stop, target or time with nothing changed: the fact sheet's net R minus the modeled one, mean, lowest and highest);
  - `costs`: `all`, `by_stop` (2.0 and 3.0) and `by_side`, each with `trades`, the mean `share_of_risk`, the mean R before and after costs, and how many entries the gate `would_refuse` or could not price (`gate_unknown`, no spread);
  - `buy_sell`: the `bars` and UTC `days` with a taker buy share, `minimum_days` (30), the `reference_exit` (`2.0/2/4`), the thirds' `cuts`, each third's bars, mean (the long's net R minus the short's) and bars whose long paid, the base count, `difference_r` (top third minus bottom), the 95% interval's bounds to four places and `TOO_FEW`, `MORE_BUYING_BETTER_LONGS`, `MORE_BUYING_BETTER_SHORTS` or `NO_LINK_SHOWN`.

  Until migration `0027` is applied it answers `SCHEMA_PENDING`, with no result, attempt or outcomes.

## ExecPlan 0046: leaner agents

[ExecPlan 0046 §4.3](../plans/0046-leaner-agents.md#43-the-rest). No route, field or answer of the futures reads changes: a generation-11 decision is read as generation 10's, with its forecast and its verdict. The agents' runtime view adds generation 11's budgets (`budgets_v11`); `openapi.json` and the web's generated types are regenerated from the code. A new runtime profile in force (the runner's configuration hash changes) reads as every earlier one did.

## The agents' models

[DECISIONS](../../DECISIONS.md#2026-10-28--the-agents-models-on-settings). One new read, `GET /v1/agent-models`, with the agent runtime routes' access (the service key), `Cache-Control: private, no-store` and `422` for any query parameter; `503 AGENT_SCHEMA_PENDING` before the agent schema. Read as the API identity in one repeatable-read snapshot from the records the worker and the runner already write; nothing calls Codex or a model, and nothing changes a rule, a limit or an order. `openapi.json` and the web's generated types are regenerated from the code.
- `evaluated_at` and `window_since` (24 hours before). `profile`: the runtime profile the app records in force (`seq`, `created_at`, `model_table`), or null when there is none or it no longer binds the installed definitions.
- `agents`: one entry per agent the app runs now, in this order: `TRADER`, `TRADE_REVIEWER`, `DECISION_REVIEWER`, `COACH`, each by the template its scheduler starts (`template_id`, `generation`, `role`, `purpose`), with the `model`, `reasoning_effort` and `preference` the profile in force gives its role (null without one), `fallbacks` (the model table's later pairs for the role, as `model at effort`), `open_workflows` (queued or running), `first_call_at` (that template's first call, so a version younger than the window can be told apart), `last_call` and `window`. The agents' check, which runs on the trader's template, is left out of the agent's own figures.
- `last_call`: the newest call's `at`, `model`, `reasoning_effort`, `codex_version`, `status` (the outcome's, null while unanswered), `error_class`, `seconds` (the runner's spawn to exit, for a completed call) and the four token counts, each null when Codex did not report it.
- `window` and `totals` (every agent call of the window, the check included): `calls`, `completed`, `failed` (`FAILED`, `TIMEOUT`, `KILLED`, `OUTCOME_UNKNOWN`), `canceled`, `unanswered`, the sums of `input_tokens`, `cached_input_tokens`, `output_tokens` and `reasoning_output_tokens` as Codex reported them, `calls_without_usage` (answered without token counts) and `average_seconds` (completed calls). A call counts by when it was made.
- `codex`: the runner's `version` and `checked_at`, and the newest `discovery` (`at`, `codex_version`, `catalog_source`, and each `models` entry's `id`, `reasoning_efforts`, `default_effort`, `usable` for the agents' code-mode tools, and `in_use` by the profile in force), or null before the first.
- `allowance`: `blocked` with `since`, `refusals` and `retry_at` while the usage limit holds, and the newest `last_refusal_at` and `last_cleared_at`. Codex does not report the allowance left, so there is no such field.
- `labels`: `TOKENS_AS_CODEX_REPORTED_THEM`, `NO_ALLOWANCE_LEFT_REPORTED_BY_CODEX`.

## ExecPlan 0047: live trades

[ExecPlan 0047 §4.1–§4.2](../plans/0047-live-trades-and-pop-ups.md#42-the-listener-and-the-engines-stream), the owner's ask of 2026-10-30 ([DECISIONS](../../DECISIONS.md#2026-10-30--live-trades-and-pop-ups-execplan-0047)). One new read, `GET /v1/futures/live`, with the futures routes' access (the service key), `Cache-Control: private, no-store`, `X-Accel-Buffering: no`, and `422` for any query parameter and for a `Last-Event-ID` that is not a sequence (digits, at most 19, no leading zero). `openapi.json` and the web's generated types are regenerated from the code. No other route, field or answer changes, and nothing here writes.
- **An event stream** (`text/event-stream`, FastAPI's `EventSourceResponse`, a `: ping` comment after 15 s idle). The first event carries `retry: 3000`. Its events:
  - `ready`, `id` the ledger's newest sequence, data `{"state", "cursor"}`: the first event without `Last-Event-ID`, or with one that nothing followed; again when the ledger is older than the stream's cursor (a restored database).
  - `activity`, `id` the newest sequence, data `{"after", "state", "cursor", "count", "items"}`: what `GET /v1/futures/activity?after=` answers after the stream's cursor, with that cursor as `after`. The first event after a `Last-Event-ID` that entries followed.
  - `change`, no `id`, data `{"source": "owner" | "twins", "kinds": [...]}`: an owner's step with no new fill or payment (a decision answered, a stop tightened, the run's state), and a twins' step with a change.
- **Refusals.** `503` `LIVE_UNAVAILABLE` (`retryable`) while the API's listener is not listening, and `503` `LIVE_BUSY` while 8 streams are open; `401` without the key. A stream ends when its client leaves, when the listener loses its database connection (the browser resumes it), after a failed read, and within 3 s of the API's stop (the image runs uvicorn with `--timeout-graceful-shutdown 3`).
- **The announcement** (no route). After each committed step that changed more than the valuation, and once after recovery, the futures worker runs `SELECT pg_notify('asl_futures_live', '{"source":…,"kinds":[…]}')` as the execution identity in a transaction of its own; the API listens as its own identity and wakes the streams, which read the records again. The payload names kinds, never a value; a failed announcement is logged and costs at most the listener's 30 s sweep.

## ExecPlan 0048: the Cockpit's equity curve

[ExecPlan 0048 §4.2](../plans/0048-the-cockpit.md#42-the-equity-card-and-its-curve), the owner's ask of 2026-10-31 ([DECISIONS](../../DECISIONS.md#2026-10-31--the-new-design-starting-with-the-cockpit-execplan-0048)). One new read, `GET /v1/futures/valuations?window=24h|7d|all` (default `all`), with the futures routes' access (the service key), `Cache-Control: private, no-store`, and `422` for another window or any other query parameter. Read as the API identity in one repeatable-read snapshot from `futures_valuations`; nothing here writes. `openapi.json` and the web's generated types are regenerated from the code.
- `state`: `READY`, or `SCHEMA_PENDING` before the futures schema (then `since`, `base_nav` null and no points).
- `window`, `bucket_seconds` (900 for `24h`, 3,600 for `7d`, 14,400 for `all`) and `since` (the window's start, null for `all`).
- `points`: the account's `VALID` valuations valued in the window, the newest of each bucket (by `valued_at`, then `recorded_at`, then `id`), ascending, each `{time, nav, equity}` as exact decimal strings; the window's first valuation comes first when it is not already its bucket's newest.
- `base_nav`: the first point's `nav`, the curve's base (so its change is the return over the window, top-ups left out); null without points.


## ExecPlan 0048 part 2: the web's page sizes

[ExecPlan 0048 §4.12](../plans/0048-the-cockpit.md#412-reads-and-components-part-2). No route changes. The web server's reads of `GET /v1/futures/trades`, `GET /v1/futures/twins/{twin}/trades` and `GET /v1/futures/decisions` now pass the existing `limit` (1 to 100, default 25): fifty trades and a hundred decisions a page. The server functions accept only that range, so a browser cannot ask for more than the API allows.

## ExecPlan 0049: the agents' provider and its usage

[ExecPlan 0049 §5.7](../plans/0049-choose-the-agents-provider-and-see-usage.md#57-records), approved by the owner on 2026-10-31 ([DECISIONS](../../DECISIONS.md#2026-10-31--the-agents-provider-four-to-choose-from-the-two-apis-with-a-daily-cap-execplan-0049)). Every route has the agent runtime routes' access (the service key; the web server calls them same-origin, behind its Host and CSRF checks), `Cache-Control: private, no-store`, and `503 AGENT_SCHEMA_PENDING` before migration `0029_agent_providers`. A provider is `CODEX_CLI`, `CLAUDE_CLI`, `ANTHROPIC_API` or `OPENAI_API`.
- **`GET /v1/agent-providers`** (`422` for any query parameter): `version` (the runtime's, for a pick's `expected_version`), `in_use` (the provider of the profile in force; Codex's before any pick), `runtime_state`, `runtime_reason`, `runner_reachable`, `credentials_reachable` (whether the runner answered its credential states now), `pending` (the newest pick not yet settled: `provider`, `at`, `started_at`), `usage_limit` (`since`, `retry_at` while the usage limit holds), and `providers`, one card each in the order above: `kind` (`CLI` or `API`), `status` (`IN_USE`, `SWITCHING`, `READY`, `CHECK_FAILED`, `NEEDS_SIGN_IN`, `NEEDS_KEY`, `KEY_REFUSED`, `TOKEN_EXPIRED`, `KEY_UNREADABLE`, `RUNNER_UNREACHABLE`, `NEEDS_CAP`, `SPEND_CAPPED`), `in_use`, `selectable`, `credential` (`kind`, `present`, `usable`, `refused`, `expired`, `expiring`, `last4`, `saved_at`, `expires_at`; never the secret), `credential_removable`, `cli_version`, `models` (each role's model and effort from the provider's table), `usage` (`read_at`, `source`, `windows` as reported, each with `name`, `minutes`, `used_percent` or null, `resets_at`, `status`, `limit`; `failed_at` and `error` when the newest read failed), `today` (calls and token sums since 00:00 UTC), `cost` (APIs only: `today_usd`, `month_usd`, `cap_usd`, `cap_set_at`, `capped`, exact decimal strings) and `refusal` (the newest refused pick's `reason`, `at`, `errors`, `message`, `problems`, `unset`).
- **`GET /v1/agent-usage`** (`422` for any query parameter): the in-use provider's `status`, `pending`, `usage_limit`, `usage`, `today` and `cost`, and its `headline`: `PERCENT` (the highest `used_percent` it reported, with its `window` and `resets_at`), `SPEND` (the day's cost against the cap, as `percent`, `today_usd` and `cap_usd`), `STATUS` (windows without a percent) or `NONE`, with a `tone`: `blocked` when refused or capped, `warning` from 80% or a warning status, else `ok`.
- **`POST /v1/agent-providers/select`** `{provider, expected_version, idempotency_key}`: the owner's pick, `PENDING` until the agent worker settles it (`IN_FORCE` after a passed check, or `REFUSED` with its reason). Refusals: `409 AGENT_VERSION_CONFLICT`, `409 IDEMPOTENCY_CONFLICT`, `409 PROVIDER_IN_USE`, `409 PROVIDER_SWITCHING`, `409 DAILY_CAP_REQUIRED`, `409 SPEND_CAPPED`, `409 PROVIDER_<status>` when the card is not ready, `422 UNKNOWN_PROVIDER`.
- **`PUT /v1/agent-providers/{provider}/credential`** `{secret}` and **`DELETE`**: save (the engine checks the shape, forwards it once to the runner and returns only its state: `provider`, `present`, `last4`, `saved_at`, `expires_at`) or remove a key or token. Refusals: `422 CREDENTIAL_INVALID` (never echoing the key), `422 NO_CREDENTIAL_FOR_PROVIDER` (Codex keeps its sign-in), `409 PROVIDER_IN_USE` (removing the key in use), `503 RUNNER_UNREACHABLE`, `503 CREDENTIAL_NOT_SAVED`, `503 CREDENTIAL_NOT_REMOVED`. The API records `CREDENTIAL_SAVED` or `CREDENTIAL_REMOVED` as the owner, with the provider and nothing of the key.
- **`PUT /v1/agent-providers/{provider}/daily-cap`** `{cap_usd, idempotency_key}`: an API's daily cap, US dollars above 0 and at most 1,000 with two decimals; answers `provider`, `cap_usd`, `set_at`, `today_usd`, `capped`. Refusals: `422 CAP_INVALID`, `422 NO_CAP_FOR_PROVIDER`, `409 IDEMPOTENCY_CONFLICT`.
- **Changed reads.** `GET /v1/agent-runtime` adds `provider` (whose sign-in or key `auth_state` describes, a pending pick's during a switch). `GET /v1/agent-models` adds `provider` (the profile in force's); its `codex.discovery` is that provider's newest discovery, `profile.model_table` and each agent's `fallbacks` come from that provider's table.

## ExecPlan 0053: when the trader decides

[ExecPlan 0053 §4.4](../plans/0053-the-trader-every-four-hours-and-on-events.md#44-the-pages). No new route. `GET /v1/futures` adds `schedule`: the trader the scheduler starts (`trader`), `every_minutes` (240), the `events` that start a decision sooner (`TRADE_CLOSED`, `MOVE`, `RANGE_BREAK`, `FUNDING_JUMP`), `decisions_per_day` (the schedule's 32) and `decisions_today` (that trader's decisions started this UTC day; null while the schema is pending). The futures decisions read gains the five trigger kinds, and a generation-14 decision is read as generation 11's, with its forecast and its verdict. The agents' runtime view adds generation 14's budgets (`budgets_v14`); `GET /v1/agent-models` names `FUTURES_DECISION_V6` as the trader. `openapi.json` and the web's generated types are regenerated from the code.

## ExecPlan 0057: the slow trend twin

[ExecPlan 0057 §4.5](../plans/0057-a-slow-trend-twin.md#45-the-pages). No new route or query parameter; `openapi.json` and the web's generated types are regenerated from the code. Every amount is the engine's decimal string, as before.
- **`GET /v1/futures/league`** and **`GET /v1/futures/twins`**: the set in force is `TWIN_SET_V3` from migration `0038`, whose `twins` lists six (`TREND_SLOW` last); the league's accounts and comparisons and the twins' list add `TREND_SLOW` ("Slow trend"), `NOT_STARTED` until its first step. Before `0038` they answer as `0030` made them.
- **`GET /v1/futures/twins/{twin}/trades`**: `TREND_SLOW` is a twin name (an unknown twin is still `422`); its trades have no stop, risk or time exit, and a close by its rule is `SIGNAL_EXIT`, as every twin's.
- The daily candles (`perp_daily_bars`) are read by no route.

## ExecPlan 0058: the event calendar

[ExecPlan 0058 §4.5](../plans/0058-the-event-calendar.md#45-the-pages-and-the-api). No new route. `GET /v1/futures`'s `schedule` names `FUTURES_DECISION_V7` as `trader`, adds `RELEASE_OUT` to `events`, and adds `calendar` (null while the schema is pending): `calendar` (`EVENT_CALENDAR_V1`), `readable`, `before_minutes` (240), `after_minutes` (`CPI` 45, `JOBS` 30, `FED` 120), `fed_dates_until` (the Fed table's last statement), `entries_closed_until` and `closed_for` (`event`, `at`; both null while entries are open), and `next` (up to three releases ahead, each `event`, `at`, `entries_close_at`, `entries_open_at`); a calendar that cannot be read gives `readable: false` and an empty `next`. The futures decisions read gains the kind `RELEASE_OUT`, and a generation-19 decision is read as generation 14's. The agents' runtime view adds `budgets_v19`; `GET /v1/agent-models` names `FUTURES_DECISION_V7` as the trader. `openapi.json` and the web's generated types are regenerated from the code.
