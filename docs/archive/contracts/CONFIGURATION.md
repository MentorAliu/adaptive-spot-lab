# Configuration and activation gates

## Layers and source of truth

Separate environment settings, owner-approved immutable operating/research policies, strategy/risk/cost/source/model/tool definitions and secrets. Use typed schemas and canonical hashes. Unknown mandatory settings are `UNSET`; zero is not an acceptable substitute. No hidden live switch. Canonical financial values live in [RISK_POLICY.md](RISK_POLICY.md), permissions in [AUTONOMY_MATRIX.md](AUTONOMY_MATRIX.md).

## Fixed scope and declared proposals

| Setting | Value/status |
|---|---|
| Product | Local single-owner paper-trading application that trades by itself; M6's research is off since [ExecPlan 0035](../plans/0035-a-simpler-app-that-trades-by-itself.md) |
| Funding | `10000.00` virtual USDT, posted once; owner-only top-ups |
| Universe | Intended BTCUSDT/SOLUSDT spot long-only, subject to symbol/status validation |
| Policy kinds | FIXED, ADAPTIVE_SELECTOR, AGENT_DRIVEN; one main policy at a time |
| Reference horizon | Finalized 1h signals, hours-to-days; 4h requires approved variant |
| Hard risk | Unchanged proposed PAPER_PILOT_V1, not a demonstrated optimum |
| Runtime | Recorded-response adapter for tests; owner-authorized Codex CLI ChatGPT login for private live inference, the default; since [ExecPlan 0049](../plans/0049-choose-the-agents-provider-and-see-usage.md) the owner may pick the Claude Code CLI (a Claude plan token), the Claude API or the OpenAI API (keys) in Settings → Provider |
| Runtime tools | Application-brokered role-scoped tool requests; no unrestricted native tools |
| Paid API fallback | Disabled / not implemented: a paid API runs only when the owner picks it, under the daily cap the owner sets (ExecPlan 0049), and nothing moves the agents to another provider by itself |
| Inference concurrency | One initial step at a time across roles; not a provider limit |
| Sources | Numerical market adapters first; external evidence disabled until registered/approved |
| Main approvals | New strategy/domain, tool/source authority and higher caps require human approval |

## Foundation and fixed-forward gates

M2 adds `ASL_MARKET_ENABLED`, default `0`. The optional worker profile must be selected separately; this flag permits public observation collection only. `ASL_MARKET_MODE` accepts only `PUBLIC` in the worker. Enabling collection after a backup, migration and provider preflight is an operator step and does not authorize valuation, signals, trades or experiments. The market worker gets its own generated secret `market_worker_password`; do not reuse the API or PostgreSQL owner credential. For disposable acceptance, `ASL_TEST_ISOLATED=1` and an `asl_m1_` test database are required to ingest `SYNTHETIC_FIXTURE` records. Do not set that flag on the owner installation.

Production exposes no alternate provider URL, test clock or relaxed queue/storage cap. Controlled provider/clock injection exists only through explicit acceptance helpers, with a disposable-database guard for synthetic persistence. Full-density and cap fixtures additionally require their dedicated empty `_retention`/`_capacity` databases and preflight at least 30 GiB free space on both the host drive and Docker volume filesystem. See [MARKET_DATA.md](MARKET_DATA.md) for fixed collection bounds.

Missing model, research or market-fee settings do not block M0, offline tests or an honest empty UI. Before a fixed forward run confirm denomination, initial contribution, policy/strategy/exit version, instrument/filter state, current valuation, data/freshness/clock rules, explicit cost/latency/liquidity scenario, local downtime and evaluation protocol.

Readiness includes schema/worker/fencing, ledger/order/reservation reconciliation, required observations and no latched pause. Model availability is required only for model-dependent work. Unknown actual fees can be represented by an explicitly approved hypothetical cost scenario with visible labeling; not silently zero.

## Agent capability preflight — M5

Record actual Codex CLI/model availability, output schema support, native-tool inventory and effective isolated config, account auth/refresh behavior, argv/stdin/JSONL parsing, process kill/size/time limits, provider connectivity policy and no paid fallback. Verify application broker identity/role dispatch with recorded responses before using live inference. No successful auth or isolation is assumed by this pack.

Set per-step/workflow deadline, max model steps/tool calls/delegation depth, max input/output bytes, retry policy, concurrent/daily job budget, retention and observed usage semantics. Values are bounded operating choices, not model-provider guarantees. Exhaustion produces an honest blocked/abstained state.

## Research envelope — M6

Require exact source/dataset permissions and as-of partitions; allowed declarative operators/templates; parameter/feature/rule complexity bounds; trial/search/concurrency/CPU/memory/wall-clock/storage budgets; permitted backtest/shadow modes; cost/protocol versions; candidate deduplication; evaluator access; and owner approval. Final-holdout access is separate from development data. Unset fields block autonomous research, not account visibility.

The owner approved the engineering defaults of [ExecPlan 0023 §5.5](../plans/0023-m6-research-investigations.md#55-protocol-envelope-and-holdout), including only the adjustments that §5.5/§5.10 leave to B0 resource/replay measurements. The exact envelope hash still requires the owner's M6-B UI approval; it binds protocol, grammar, domains, budgets and resource limits. Bar-history research is excluded. Shadows are labeled deferred replay, with engine mode HISTORICAL_RESEARCH, until boundary work adds a live engine.

B0's completed research-limit native sample and inferred dataset/store sizing are recorded in that canonical section. Preserve the unchanged job wall-clock and protocol sample minimums; measured capacity is not permission to omit insufficiency labels or an assertion that future candidate jobs will pass their performance gate. Host physical free space and virtual data-filesystem free space are distinct observations.

**Bridge and store settings (B4).** `research-bridge` reads `ASL_DB_HOST` and `ASL_DB_NAME` for the main database, `ASL_RESEARCH_DB_HOST` for the research cluster and `ASL_RESEARCH_DB_NAME` for the first store's name; later versions are that name with `_v2`, `_v3` and so on. Its secrets are `research_db_password` and `research_bridge_db_password`, both under `ASL_RESEARCH_SECRET_DIR`. `asl_bridge` exists in the research cluster only and is NOLOGIN until the activation step that B9 rehearses. The rotation threshold (28 days or 12,271,335,131 bytes) is derived in code from the envelope's store and shadow values and is not a separate setting. The staging batch (500 rows), settle lag (60 s), gap threshold (60 s) and pass cadence are code constants: engineering defaults, not owner-approved financial or envelope values.

`ASL_RESEARCH_ENABLED` and `ASL_SOURCES_ENABLED` default to `0`; `asl_research` and `asl_source` stay NOLOGIN at inert deployment. Research/source activation and all runtime-profile approvals/probes/Enable are owner-only M6-B. Definitions v2 invalidate the old profile match before any model call. The isolated harness pins every activation flag, never inherits the owner's `.env`, and has no public endpoint or real model call.

External source activation requires schema, rights/retention, exact host and typed GET-path validation, no redirects or environment proxy, global resolved addresses, source/receipt timing, freshness/revision and rate limits. A new URL in agent output is not a new source permission.

**Source-version values (B5, PROPOSED engineering defaults).** The two seeded release feeds bind these values in their hash; none is claimed optimal, and none has been measured against a real answer. The owner approves or replaces them by exact hash in M6-B.

| Field | `RELEASES_BITCOIN_V1` and `RELEASES_AGAVE_V1` |
|---|---|
| Answer | `application/json`, at most 2,097,152 bytes, one 20 s deadline; extract at most 16,384 bytes |
| Typed filters | `per_page` 1–100, `page` 1–10; a poll asks for `per_page=10`, `page=1` |
| Budget | 6 requests an hour per version, against the publisher's 60 an hour per address; poll every 3,600 s; an equal on-demand refresh at most once per 600 s |
| Back-off | 300 s after a failure; 3,600 s after a limit that states no reset; a stated reset is honored, capped at one day |
| Trigger | `SOURCE_REVISION`, cooldown 21,600 s per source and symbol |
| Scope | BTCUSDT for Bitcoin Core, SOLUSDT for Agave |

Code-owned bounds that a source version cannot exceed: 2 MiB, a 30 s deadline, a 16 KiB extract, an own budget of half the declared allowance, a wait deadline of six hours for a queued request, and 180 s before a request left running is failed as lost. The fetcher starts nothing between HH:58 and HH:07 UTC. `ASL_SOURCE_EGRESS_INTERNAL` (default `false`) makes the fetcher's egress network internal.

## Main agent-driven operating policy — M7

Require approved agent-policy ID/hash; the prompt, schema, tool, grant, template and budget definition hashes it is valid with; the rules for the model and the sources (the model itself is bound by the separately approved runtime profile, M7-OD11 a); admissible evidence predicates; reviewed action domain; allowed horizon and deterministic protection template; intent validity/deviation bounds; code-derived sizing policy; review requirements; trigger dedupe/cooldown/priority; discretionary turnover/order/re-entry limits; model/tool workload budget; fallback and suspension rules; evaluation/benchmark settings; and owner approval.

The pilot requires an acceptable exact-hash evaluator review before new discretionary exposure. Existing-position protective actions are model independent; early voluntary reduction/exit/stop tightening follows the original approved mandate. No changing the mandate by editing a new intent.

For ADAPTIVE_SELECTOR also freeze score/formula, input windows, uncertainty/sample method, tie-break, switching cost/tenure, eligible versions and checkpoint. For AGENT_DRIVEN do not impose an irrelevant deterministic selector as a hidden prerequisite, but require the fully specified operating envelope and baselines. New decision-policy/model/prompt versions need approval and evaluation segmentation; daily decisions inside an unchanged policy do not. *M7, approved contract, PROPOSED implementation:* a changed prompt or other bound definition is a new policy version and therefore a new experiment; a new runtime profile needs its own approval and starts a segment under `EVALUATION_PROTOCOL_V2`. The values of `AGENT_POLICY_V1` are [ExecPlan 0026 §5.2 and §5.7](../plans/0026-m7-agent-driven-main-decisions.md#52-agent_policy_v1-values-proposed-engineering-defaults-no-measurement-stands-behind-them), built in as code (M7-OD3); they are PROPOSED values without a measurement behind them.

## Operational settings and changes

Measure local Docker CPU/RAM/storage and declare limits in M0/appropriate milestones; research-worker limits must protect the execution loop. Select ports, health/polling intervals, job and dataset retention, backups and source fetching limits based on actual environment observations. Secrets stay outside Git/images/prompts, with no exchange keys.

The UI presents a version diff and material authority consequences before owner approval. Budget/config changes never rewrite an old experiment. Revocation increments permission epochs, cancels invalid work and preserves open-position protections. Top-ups change contributed capital only; they do not reset action counters, risk latches or high-water NAV.

Activation must validate complete schemas and report every unset mandatory field with its owning document/milestone. Do not ask the owner to repeat answered choices; propose a labeled operating configuration for approval when actual measurements are available.

## M3 execution settings

- `ASL_EXECUTION_ENABLED` (default `0`) only lets the optional `execution-worker` process run; enabling it never trades by itself because the main activation is structurally blocked in M3 (`RISK_POLICY_UNAPPROVED`, `STRATEGY_UNAPPROVED`, `COST_SCENARIO_UNSET`, `NO_STARTED_RUN`, `EXECUTION_IDENTITY_DISABLED`).
- `ASL_EXECUTION_ACTIVATION` accepts `MAIN` (default, blocked), `FIXTURE` (refused unless `ASL_TEST_ISOLATED=1` and an `asl_m1_` database) or `REPLAY` (refused unless `ASL_REPLAY_ISOLATED=1` and an `asl_m1_replay_` database). `ASL_EXECUTION_COST_SCENARIO` must name a complete scenario for FIXTURE (fixture-only) or REPLAY (any hashed scenario); there is no default and `UNSET` blocks every order and fill.
- Definitions are seeded by migration 0005 as hashed, immutable rows with status `PROPOSED`: `PAPER_PILOT_V1`, `TREND_REFERENCE_V1`, `PAPER_COST_V1`, `COST_SCENARIO_HYPOTHETICAL_H1`, `COST_SCENARIO_HYPOTHETICAL_H2_STRESS` (unsourced round sensitivity values, not Binance's schedule or the owner's fee), `VALUATION_BID_V1` and `FILTER_POLICY_V1`. Startup refuses to run if a stored hash differs from the code's canonical definition. `FIXTURE_ONLY` definitions can be inserted only in `asl_m1_` databases.
- New secret `execution_db_password` (created only if missing by `tools/setup-local.ps1`); the `asl_execution` role is created **NOLOGIN**. `python -m app.execution.identity enable` grants LOGIN only in isolated projects; enabling it on the owner database is an M4 activation step.

## M4 settings (ExecPlan 0015)

- `ASL_EVALUATION_ENABLED` (default `0`) lets the optional `evaluation-worker` process run; a disabled worker idles with a heartbeat. Its identity `asl_evaluation` uses the new secret `evaluation_db_password` (created only if missing by `tools/setup-local.ps1`) and is created **NOLOGIN**.
- MAIN activation refuses `ASL_EXECUTION_COST_SCENARIO`; the running experiment's approved manifest names the cost scenario. A disabled execution worker idles instead of exiting.
- Both workers use `restart: unless-stopped`. The one-shot `pilot-admin` service that ran `app.execution.identity` for the M4 activation step was removed by ExecPlan 0034.
- Seeds `EVALUATION_PROTOCOL_V1` and `BASELINE_SET_V1` are `PROPOSED`; startup refuses to run if a stored hash differs from the code's canonical definition. The UI lists every `UNSET` manifest field with its owning document, and any `UNSET` field blocks READY.

## M5 settings (ExecPlan 0020)

- **Flags and secrets.**
  - `ASL_AGENTS_ENABLED` (default `0`) only lets the optional `agent-worker` process run. A disabled worker idles with a heartbeat.
  - Enabling the flag never starts model work. The runtime still needs the owner's M5-B steps.
  - The new secrets `agent_db_password` and `agent_runner_key` are created only if missing by `tools/setup-local.ps1`. `asl_agent` is created NOLOGIN.
  - No API key, provider token or alternate provider URL exists in production configuration. The mock provider, fake CLI and recorded provider exist only in isolated test images and `asl_m1_` databases. Since ExecPlan 0049 a provider key or token exists only in the runner's `agent_keys` volume, entered by the owner in Settings → Provider ([SECURITY](SECURITY.md#the-agents-provider-keys-execplan-0049)).
- **Runtime profile.** The approved exact-hash profile, not an environment setting, holds:
  - the model and reasoning effort, chosen from the discovered list, where the model must be `tool_mode: code_mode_only` in the authenticated catalog (M5-OD1; see [RUNTIME_AGENTS](../RUNTIME_AGENTS.md)); any other model is refused with `MODEL_EXPOSES_NATIVE_TOOLS`;
  - the binary digest, config hash and native-inventory hash;
  - the account-id hash and the egress allowlist;
  - the AgentStep schema, prompt, catalog and grant hashes;
  - the budgets and the provider data scope.

  Anything unset blocks approval. A change to the binary, configuration, account or inventory (including a newer discovery that reports a different catalog) returns the runtime to `PROBE_ONLY`.
- **Isolated test stacks only.** `ASL_MODEL_EGRESS_INTERNAL=true` makes `model_egress` an internal network. The M5 harness pins it in every per-run env file, so no isolated stack has an Internet route. It defaults to `false`, and the normal installation does not set it.
- **Budgets and bounds** (PROPOSED; bounded operating choices, not provider guarantees):
  - step deadline 120 s and workflow deadline 20 minutes;
  - 8 model steps and 6 tool calls per workflow;
  - handoff depth 1;
  - prompt 64 KiB, final object 16 KiB, JSONL 2 MiB, stderr 256 KiB;
  - 12 parent workflows per UTC day;
  - a probe budget of 40 live calls;
  - queue expiry 10 minutes;
  - one inference slot;
  - the HH:59:30–HH:06:00 UTC quiet window.
- **Retry.** `REJECTED_OUTPUT` gets one retry that consumes budget. An HTTP timeout never causes a second call for the same call key: the worker polls until the deadline plus a grace period, then records `OUTCOME_UNKNOWN`. A new attempt consumes retry budget.
- **Usage semantics.** Usage is the `turn.completed` token counts, as observed. Remaining quota and reset times are shown only when a verified interface reports them; otherwise "unknown".
- **Error classes.** `QUOTA_BLOCKED` is assigned only for provider error payloads classified from real observed payloads (the usage-limit text since M8 update 1, observed on the owner's PC on 2026-10-19: [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-the-agents-check-the-usage-limit-and-one-switch-execplan-0031)). Anything unknown maps to `PROVIDER_UNAVAILABLE` and fails closed. `AUTH_REQUIRED` covers a missing or refused login.
- **Retention.** Provider-call summaries are kept for 90 days (PROPOSED). Artifacts, hashes and decisions are kept permanently. New workflows are refused under the measured disk-pressure threshold.
- **Schema support.** The output schema is a strict-compatible projection whose hash is pinned in the profile. Every output is fully re-validated in the engine, because Codex's strict-mode enforcement is not documented.

## M6 B6 settings (ExecPlan 0023)

B6 adds **no environment variable, secret, service, network or volume**. The generation-2 workflows run in the existing `agent-worker` under the M5 flags; `ASL_RESEARCH_ENABLED` and `ASL_SOURCES_ENABLED` still default to `0`, and nothing was enabled.

- **Budgets v2** (`BUDGETS_V2`, status PROPOSED; bounded operating choices, bound by the runtime-profile hash, not provider guarantees and not measured against a real model):
  - step deadline 120 s; running deadline 20 minutes for a parent and 10 minutes for a child; wait deadline 6 h, counted apart from running time;
  - a parent has 12 model steps, 10 tool calls and at most 3 experiments; a child has its own 4 steps and 3 tool calls;
  - handoff depth 1; prompt 64 KiB, final object 16 KiB, JSONL 2 MiB, stderr 256 KiB; a tool result envelope at most four times 16 KiB and never above 60,000 characters, and small enough for the next prompt to show it beside the role prompt, the schema (about 19 KiB) and the job context;
  - 24 parent workflows per UTC day;
  - a probe budget of 60 live calls for the 20 probes (this batch's proposal; M5 used 40 for 14);
  - a queued owner request expires after 10 minutes, a workflow queued by the scheduler or the orchestrator after 6 h, and a trigger is refused as stale after 6 h;
  - one retry for `REJECTED_OUTPUT`; one inference slot; the HH:59:30–HH:06:00 UTC quiet window.
- **Generation 1 keeps budgets v1** (above). The daily count covers parents of both generations; each workflow is held to its own generation's cap.
- **Runtime profile.** Version 2 binds the definition hashes of both generations and `budgets_v2`. Anything unset still blocks approval. The profile approved in M5 does not match: the worker rejects a Probe or Enable that names it and removes it from the runtime state (`LOGIN_REQUIRED`, reason `PROFILE_DEFINITIONS_CHANGED`). The owner composes and approves a new one in M6-B.
- **Code-owned constants** (not profile values; a change is a code change with its tests):
  - the scheduler looks at triggers every 15 s;
  - (in `TEMPLATES_V2`, so bound by the profile hash) a source-triggered investigation has a 24 h horizon and the trigger's symbol, with one open investigation per source and symbol;
  - a refresh completion carries at most 5 items with excerpts of 600 characters and at most 20 item IDs;
  - a storage observation older than 2 h 10 min is treated as unknown, and the bridge publishes one per store and UTC hour;
  - a screening reservation estimates 58 s of replay per recorded day and cost scenario. This is INFERRED from B0's native-replay measurement; the runner enforces the job's own bound whatever the estimate says, and B9 measures candidate jobs;
  - the full test of a nominated candidate is queued once, with one retry after a failed or expired first evaluation.
- **Prompts.** `services/agent-runner/prompts/m6/` is copied into the engine image beside `prompts/m5/`. The runner image and its configuration are unchanged.

## M9 update 1 settings (ExecPlan 0032)

No environment variable, secret, service, network or volume is added. The feeds run in the existing `source-fetcher` under its existing `ASL_SOURCES_ENABLED` flag, on its existing `source_egress` network. Each feed's settings are values of its source document (`app/sources/feeds.py`), so a change is a new version in an update, with its tests:

| Feed | Polls | Hourly budget | Cap per address | Back-off after a failure | Starts work | Between investigations, per coin |
|---|---|---|---|---|---|---|
| `CALENDAR_BLS_V1` | 6 h | 1 | 2 | 30 min | never | n/a |
| `NUMBERS_BLS_V1` | 15 min | 4 | 8 | 15 min | each new item, both coins | 4 h |
| `PRESS_FED_MONETARY_V1` | 15 min | 4 | 8 | 15 min | each new item, both coins | 4 h |
| `PRESS_ECB_V1` | 15 min | 4 | 8 | 15 min | each new item, both coins | 12 h |

These are Claude's engineering choices under the owner's delegation, not publisher limits: none of the three publishers states one ([INTEGRATION_EVIDENCE](INTEGRATION_EVIDENCE.md#m9-update-1-the-free-feeds--2026-10-19)). A limit without a stated wait backs off one hour. Every answer is capped at 1 MiB and 20 s. The investigations they start share generation 2's 24 workflows a UTC day with research, and one open investigation per source and coin, as before; update 2 gives news its own count ([0032 §5.2](../plans/0032-m9-news-and-events-the-agents-trade-on.md#52-the-agents-and-agent_policy_v3-update-2)).

## M10 update 1 settings (ExecPlan 0033)

No environment variable, secret, service, network or volume is added. The daily coin scan runs in the existing `source-fetcher` under its existing `ASL_SOURCES_ENABLED` flag, identity and `source_egress` network; the coin notes run in the existing `agent-worker` under the M5 flags. The scan's settings are values of its rules (`COIN_SCAN_V1`, `app/coins/rules.py`) and the notes' of generation 5 (`NOTE_RULE` and `BUDGETS_V5`, `app/agents/definitions_v5.py`), so a change is a new version in an update, with its tests. All are Claude's engineering choices under the owner's delegation, not measurements:

| Setting | Value |
|---|---|
| Scan start, retry, attempts | from 00:20 UTC; an hour after a failed attempt; at most 4 a UTC day |
| The scan's own request weight | 100 a minute (the market worker keeps its 120) |
| Candidates, spread, daily bars | the 30 USDT pairs with the most 24-hour volume after the name lists; at most 20 bps; 91 finalized days |
| Pegged and look-alike checks | every close within 0.97 to 1.03; daily returns correlated 0.98 or more with BTC's or SOL's |
| Watchlist | the best 8 by median daily volume over 30 days |
| Notes | one open at a time, at most 3 a UTC day; a coin's note renewed after 7 days, retried after 24 hours; a scan used for 36 hours |
| A note's budget | 8 model steps, 6 tool calls, 20 minutes; its review 4 steps, 3 calls, 10 minutes |

## ExecPlan 0049 settings

- **Secret.** `agent_credentials_key` (a random value, created only if missing by `tools/setup-local.ps1`, which `tools/update.ps1` now runs when a secret file is missing) lets the API service reach the runner's credential routes; the agent worker does not hold it.
- **Volume.** `agent_keys`, mounted by the runner alone at `/agent-keys` (`ASL_RUNNER_AGENT_KEYS`).
- **Code-owned definitions**, seeded by migration `0029_agent_providers` with their hashes: `EGRESS_ALLOWLIST_V3` (one gateway port per provider), `MODEL_TABLE_V3` (Claude API), `MODEL_TABLE_V4` (OpenAI API), `API_PRICES_V1` (US dollars per million tokens, observed on 2026-10-31), and profile version 5, which names its provider. A price or a model changes only with an update.
- **Owner settings in the database**, not in the environment: the provider pick (`agent_provider_requests`) and each API's daily cap (`agent_spend_caps`, no default: an API cannot be picked without one; the form starts at $10).

## ExecPlan 0052 settings

- **No new setting, secret, volume, host or owner step.** The backtest's run, window, mask, archive, pace and call total are code-owned and hashed in generation 15's definitions (`TEMPLATES_V15`'s `BACKTEST_AI_V1` and `BACKTEST_ARCHIVE_V1`, `BUDGETS_V15`), seeded by migration `0032_ai_backtest`; they change only with an update. Since [§15](../plans/0052-backtest-the-ai-trader-on-history.md#15-generation-16-the-backtest-up-to-80-of-the-week-2026-11-04) the allowance rule (the weekly window under 80%, every other under half) is generation 16's (`TEMPLATES_V16`, `BUDGETS_V16`, migration `0035_backtest_allowance`), also code-owned, with no setting.
- **Compose.** The `agent-worker`'s memory limit rises from 256 MiB to 512 MiB ([DOCKER](DOCKER.md)) for the backtest's child process (78 MB at most, `OBSERVED` in the cloud); its CPU limit and PIDs are unchanged.
- **The archive** ships in the engine image (`services/engine/app/backtest_ai/archive/`, about 8.4 MB, Binance's files byte for byte with their `.CHECKSUM`s); nothing is downloaded.

## ExecPlan 0055 settings

- **No new setting, secret, volume, host or owner step.** The Claude run, its call (the adapter `ANTHROPIC_API`, `claude-sonnet-5-5` at `medium`), its cap of $120 (starting while the counted spend is at most $119), its 3,000 workflows and its back-off are code-owned and hashed in generation 17's definitions (`TEMPLATES_V17`, `BUDGETS_V17`), seeded by migration `0036_claude_backtest`; they change only with an update.
- **The key** is the Claude API key the owner saved on the Claude API card in Settings → Provider on 2026-11-03 ([ExecPlan 0049](../plans/0049-choose-the-agents-provider-and-see-usage.md)). Only the runner holds it; the run reads only its status (present, readable, refused, expired). Removing the key on that card holds the run at once (`NEEDS_KEY`), and a new key lets it go on. The Claude API's daily cap (`agent_spend_caps`) governs only the provider in force, so it is not this run's and none is needed; the card's day spend shows every call on the key, this run's included.
- **The host** is `api.anthropic.com` through the egress gateway's `ANTHROPIC_API` port, as since ExecPlan 0049.
- **Compose** is unchanged. The second child process (about 78 MB at most, as the first, `OBSERVED` in 0052) runs inside the agent worker's 512 MiB; NOT RUN in the cloud (no Docker): the install's check reads the worker's memory.

## ExecPlan 0056 settings

- **No new setting, secret, volume, host or owner step.** The third run, its call (the adapter `ANTHROPIC_API`, `claude-sonnet-5-5` at `medium`), its cap of $40 (starting while the counted spend is at most $39), its 2,000 workflows, its back-off and the live design's fingerprint it is tied to are code-owned and hashed in generation 18's definitions (`TEMPLATES_V18`, `BUDGETS_V18`), seeded by migration `0037_latest_backtest`; they change only with an update.
- **The key** is the same Claude API key as ExecPlan 0055's, saved on the Claude API card in Settings → Provider; removing it holds the run at once (`NEEDS_KEY`). The run starts only after 0055's has ended, so the two never spend at the same time.
- **Compose** is unchanged. The third child process runs inside the agent worker's 512 MiB beside the ChatGPT run's (Claude's 0055 child has ended); NOT RUN in the cloud (no Docker): the install's check reads the worker's memory.
