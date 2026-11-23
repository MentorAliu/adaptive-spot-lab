# ExecPlan 0049 — Choose the agents' provider and see their usage

**Status: APPROVED on 2026-10-31: the owner's ask at 07:49:33 UTC and the pick "Yes, all four with a daily cap" at 08:03:30 UTC ([DECISIONS](../../DECISIONS.md#2026-10-31--the-agents-provider-four-to-choose-from-the-two-apis-with-a-daily-cap-execplan-0049)); built in the cloud on 2026-10-31 (§16); not installed yet.** Written by the project thread "Choose agent provider and show usage" from `main` at `793abdd`. A part of M11 ([ExecPlan 0039](0039-bitcoin-futures-on-paper.md)). Built after the redesign (ExecPlan 0048, the thread "Build the new Claude Design redesign") has installed its Settings part, the last of its parts that touches Settings or the shell.

Labels: `OBSERVED` (seen in records, code or official pages), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`, `NOT VERIFIED`.

## 1. Goal

The owner asked on 2026-10-31 at 07:49:33 UTC: "When the new design implementation is finished, I want the app to have ability to select between codex cli, claude cli, claude api, openai api in settings somewhere to handle the agents, probably show them as cards and add some details with great ux, also somewhere in the app best for ux I want the app to show the details for example usage, session usage, 5hour usage, weekly, make sure to display them for best ux leveraging shadcn".

Observable outcome:
1. Settings has a **Provider** section after Agents: four cards, Codex CLI, Claude CLI, Claude API and OpenAI API, one marked **In use**. Each card says how it is paid, which model each agent would use, whether it is ready (signed in, key saved) and what usage it reports. Picking another ready card and confirming moves the agents to it after one test call passes; until then the one in use keeps working.
2. A **usage button** in the header on every page: a gauge icon and the in-use provider's tightest figure ("Session 42%", or "$1.80 today" for an API); a click opens the details (session, week, today's calls and tokens, the spend cap), each with its reset time and how old the reading is.
3. The Cockpit's engine room chip ("Allowance ok" today) reads the same figure.
4. Every figure is one the provider reported, or one the app calculated from what it reported, and says so. Where a provider has no such limit (the APIs have no 5-hour or weekly window) the page says that instead of showing a bar.

## 2. What the app has

`OBSERVED` in the code at `793abdd`:
- **One provider.** The runner (`services/agent-runner`) runs the Codex CLI `rust-v0.159.2` with the owner's ChatGPT login (`codex_home` volume), one `AgentStep` per call, native tools off, egress through `agent-egress` to `EGRESS_ALLOWLIST_V1` (`auth.openai.com`, `chatgpt.com`). The runtime profile (version 4, `app.agents.profile`) binds the binary, its configuration hash, the native inventory, the egress allowlist and `MODEL_TABLE_V1` (`gpt-6.1-sol`, efforts per role). The engine never holds model credentials; `FORBIDDEN_ENV` in `runner.invocation` refuses any `API_KEY` variable.
- **Claude Code was built once.** M11's update 1 (PR #116, `9668cfb`) ran the agents on Claude Code `2.1.308` with a one-year `claude setup-token` token, and update 1b put Codex back before any Claude call ([0039 §5.6](0039-bitcoin-futures-on-paper.md#56-the-agent-cli-codex-kept)). Its runner code (`stream.py`, `token_store.py`, `sign_in.py`, `fetch_claude.py`) is in Git history; `MODEL_TABLE_V2` (`claude-sonnet-5-5` at `medium`) and `EGRESS_ALLOWLIST_V2` (`api.anthropic.com`, `platform.claude.com`) are still seeded (migration `0018`) and named by no profile.
- **Usage today.** `codex exec --json` reports a call's tokens at `turn.completed` and nothing about the allowance; the app knows the limit only from a refused call (`app.agents.usage`, `quota_state`). Settings → Models (#145, `GET /v1/agent-models`) shows calls and tokens of the last 24 hours and says "Codex does not report it" for the allowance left.
- **Pace.** `OBSERVED` on the PC on 2026-10-29: the trader made 86 calls in 18.5 hours after ExecPlan 0046, about 110 agent calls a day with the check and reviews, about 14,000 input and 300 output tokens each.
- **The redesign** (thread reply of 2026-10-31 07:52 UTC): after Home come Trades, a trade, Decisions, Markets and Settings, one install each. Its Settings redraws Agents as one item list and Models as small cards per agent; section anchors stay `#agents #models #run #limits #account #health`; the Cockpit's engine room strip (`src/cockpit/engine-room.tsx`) shows "Allowance ok" from `GET /v1/agent-models`. No board covers a provider or usage; the provider cards follow the Models cards' look.
- **shadcn** (preset `b2fms61Bqi`, `base-nova`, Lucide): `Card`, `Badge`, `Field`, `Item`, `Progress`, `Input`, `AlertDialog`, `Tooltip`, `Sheet` are installed; `RadioGroup` and `Popover` are not.

## 3. What each provider reports

| | Codex CLI | Claude CLI | Claude API | OpenAI API |
|---|---|---|---|---|
| Paid by | the owner's ChatGPT plan | the owner's Claude plan | per token, the owner's Anthropic account | per token, the owner's OpenAI account |
| Shares its limits with | the owner's own Codex use | the owner's own Claude use, these project threads included | nothing | nothing |
| Session (5 hours) | yes: used %, reset time | the window the CLI names, with status and reset time; used % when included | no such limit | no such limit |
| Week | yes: used %, reset time | as above (`seven_day`, `seven_day_sonnet`, …) | no such limit | no such limit |
| Per call | tokens | tokens | tokens, and from them a cost | tokens, and from them a cost |
| Per minute | no | no | requests and tokens left, reset time | requests and tokens left, reset time |
| Money spent so far | no (a credits balance when the plan has one) | no | no: only in Anthropic's Console | no: only in OpenAI's dashboard |

Where each comes from (`OBSERVED` in the sources of §8):
- **Codex CLI.** `codex exec` at the pin drops the rate limits: they are in the protocol's `TokenCountEvent.rate_limits`, and the exec JSONL processor never prints them. The pinned `codex app-server` answers `account/rateLimits/read` (not marked experimental) with `rateLimits.primary` and `.secondary`, each `{usedPercent, windowDurationMins, resetsAt}`, plus `credits`, `planType` and `rateLimitReachedType`; a background reader may pass `excludeResetCreditDetails: true`. The app names a window by its `windowDurationMins` (300 is "Session · 5 h", 10080 is "Week"), never by its position. `NOT VERIFIED` until the first read on the PC: the durations the owner's plan returns.
- **Claude CLI.** Claude Code `2.1.309`'s SDK types: a `rate_limit_event` carries `rate_limit_info` with `status` (`allowed`, `allowed_warning`, `rejected`), `resetsAt`, `rateLimitType` (`five_hour`, `seven_day`, `seven_day_opus`, `seven_day_sonnet`, …), an optional `utilization` and overage fields. Update 1 saw `rejected` with `five_hour` and `resetsAt` from an offline stand-in. `NOT VERIFIED`: whether the CLI sends one with every answer or only near a limit, and whether `utilization` comes below the warning level. The page shows what came and its age; with `allowed` and no percentage it says "below Claude's warning level". The result's `total_cost_usd` is "an estimate, not a billing statement" and means nothing on a plan, so it is not shown.
- **Claude API.** Response headers `anthropic-ratelimit-{requests,tokens,input-tokens,output-tokens}-{limit,remaining,reset}` (tokens rounded to the nearest thousand) and `retry-after`. Limits are per minute; the spend limit is monthly and set in the Console; no header or endpoint of an ordinary key reports spend.
- **OpenAI API.** Response headers `x-ratelimit-{limit,remaining,reset}-{requests,tokens}` (and `-project-tokens`) and `Retry-After`; per-minute and per-day limits; the monthly limit and spend live in the dashboard; no header reports money.

So "session usage" and "5-hour usage" are the same window on both plans (Claude's own usage page calls the 5-hour window "Current session"); the app shows it once, as **Session · 5 h**. "Usage" is the app's own count of calls and tokens, and for the APIs the cost calculated from them.

## 4. Scope

In: the four providers behind the runner's one job protocol (§5.1); credentials entered in Settings and kept by the runner only (§5.2); the owner's pick and the switch (§5.3); reading usage (§5.4); a daily spend cap for the APIs (§5.5); the Provider section, the header's usage button and the Cockpit chip (§5.6); records (§5.7); the rule and contract changes (§6).

Out: a model picker (the owner delegated the model choice on 2026-10-19; each provider has one code-owned model table); a fallback from one provider to another (rule 10's "paid API fallback is disabled" stays: only the owner's pick changes the provider); undocumented endpoints (Claude's OAuth usage endpoint, cookies); the Admin API's cost reports (they need an admin key); a chart of usage over time; comparing the providers' decisions (a later plan, if the owner wants it).

## 5. Design (PROPOSED)

### 5.1 Four adapters in one runner

The runner keeps its job protocol (`POST /v1/jobs`: call key, prompt, output schema, model, effort, deadline) and gains a `provider` field. Each job runs through one adapter, and each adapter returns the same result (status, the final `AgentStep` JSON, usage, error class) so the engine's dispatcher, validation and records do not change:
- **`CODEX_CLI`**: today's adapter, unchanged.
- **`CLAUDE_CLI`**: update 1's adapter back from Git history, at the newest Claude Code release at build time (exact version and digest pinned, its flags and native inventory re-checked against that version as update 1 did): `claude -p --output-format stream-json --json-schema … --tools "" --strict-mcp-config --no-session-persistence --permission-mode dontAsk`, the token passed as `CLAUDE_CODE_OAUTH_TOKEN`, a job killed on any tool but `StructuredOutput` and on paid overage.
- **`ANTHROPIC_API`**: one Messages API call through the official `anthropic` Python SDK: the runner's base instructions and the role prompt as a cached system prefix, the job as the user turn, `output_config.format` with the `AgentStep` JSON schema, `output_config.effort`, no tools. Refusals (`stop_reason: "refusal"`) and `max_tokens` end the job as `REJECTED_OUTPUT`; 429 is `QUOTA_BLOCKED` with `retry-after`; 401/403 `AUTH_REQUIRED`; the SDK's retries are off (the engine owns retries).
- **`OPENAI_API`**: one Responses API call through the official `openai` Python SDK, `text.format` `json_schema` with `strict`, `reasoning.effort`, `store: false`, no tools; the same error mapping.

The API adapters have no native tools at all, which is stronger isolation than a CLI. Both SDK clients get an `httpx` client that goes through `agent-egress`, with no inherited environment. The engine already validates every answer against the schema; whether each vendor's structured outputs accept the `AgentStep` schema as is, or need a provider-specific copy with unsupported keywords removed, is checked at build (`NOT VERIFIED`), and the engine's own validation stays the authority either way.

**Models** (code-owned, no picker): Codex `MODEL_TABLE_V1` as today; Claude CLI `MODEL_TABLE_V2` (`claude-sonnet-5-5` at `medium`, the model ExecPlan 0039 named and the owner approved); Claude API `MODEL_TABLE_V3`, the same pair, so the two Claude cards differ only in how they are paid; OpenAI API `MODEL_TABLE_V4`, `gpt-6.1-sol` at each role's `MODEL_TABLE_V1` effort, the model the agents run today. Both API tables are checked against the vendor's `GET /v1/models` with the owner's key before a switch.

**Egress**: `EGRESS_ALLOWLIST_V3` lists each provider's hosts (`auth.openai.com`, `chatgpt.com`; `api.anthropic.com`, `platform.claude.com`; `api.anthropic.com`; `api.openai.com`). The gateway listens on one port per provider and each port allows only its provider's hosts; each adapter's process or client is given only its own port, so a CLI's stray connection cannot reach another vendor.

### 5.2 Credentials

The owner enters each secret once, in Settings, and the app never shows it again:
- **Codex CLI**: the existing ChatGPT login (`codex_home`); the card shows "Signed in" from `codex login status`, or how to sign in (`tools/agent-login.ps1`, as today).
- **Claude CLI**: the owner runs `claude setup-token` in their own terminal (they have Claude Code on the PC) and pastes the one-year token on the card. The card shows the date it runs out, a year after saving, and warns 14 days before.
- **Claude API** and **OpenAI API**: the owner pastes an API key from the vendor's console.
  - Since 2026-11-03 the Claude API card takes each kind of key the Claude Console issues for the Messages API: a personal key (`sk-ant-usr…`), a service account key (`sk-ant-svc…`) or a legacy workspace key (`sk-ant-api03-…`); an Admin API key (`sk-ant-admin…`) is refused. The key must be scoped to a workspace, since the runner sends no `anthropic-workspace-id` header (§16).

The form (React Hook Form, Zod: the vendor's prefix and length only) posts through the web server to the engine, which forwards it once to the runner (`PUT /v1/credentials/{provider}`, runner key) and keeps nothing but `saved_at` and the last four characters. The runner writes it atomically to a new `agent_keys` volume (mode 0700, the runner's user), mounted by the runner only. A key never reaches the database, a log, an image, a backup, a prompt or an API answer; the engine's request logging is checked to drop the body (test P4). "Remove" deletes the file. A provider in use cannot lose its credential; the owner switches first.

### 5.3 The switch

Picking a ready card opens a confirmation (`AlertDialog`): which provider, how it is paid, the models, about how much it costs a day at today's pace for an API (§5.5), and "the next decision uses it after a test call passes". The confirmation posts an owner request (`agent_provider_requests`, idempotency key, the runtime's version). The agent worker then:
1. composes a profile for that provider (version 5: the profile names the provider, its adapter's configuration hash, its model table, its egress allowlist, the CLI's version and native inventory or the API's model list) and records it as `SYSTEM`, as today;
2. runs the agents' check on it (`app.agents.check`, one call);
3. on a pass records the new profile in force; workflows already running finish on the old one. On a failure the old profile stays in force and the card shows the check's own error ("The key was refused", "Usage limit reached until 14:00").

As built (§14, corrected after the independent review): once the new profile is composed the runtime is on it in `PROBE_ONLY` until the check ends, so the agents pause for the check (at most 20 minutes) and work started on the old profile ends `PROFILE_MISMATCH`; it fails closed and the engine's stops are not held back. After a refusal the old provider comes back at once with its usage-limit block.

No decision waits for the owner; open positions keep code's protection throughout. The owner's off switch and pauses are untouched. A refusal for the usage limit or the spend cap on the provider in force blocks new entries as `quota_state` does today; the app never moves to another provider by itself.

### 5.4 Reading usage

The runner returns what each call reported; the engine stores it as a usage reading (provider, time, source, the windows or headers) and the pages read the newest per provider:
- **Codex CLI**: the runner starts the pinned `codex app-server` in a pristine copy of the login (as discovery does), sends `initialize`, then `account/rateLimits/read` with `excludeResetCreditDetails: true`, and exits. Every 10 minutes while Codex is in use, after a refused call, and when the owner opens the usage button and the reading is older than 2 minutes. The app server is given no thread, tool or turn.
- **Claude CLI**: each job's `rate_limit_event`s.
- **APIs**: each response's rate-limit headers; tokens from each answer's `usage`.

A provider not in use keeps its last reading, shown with its age.

### 5.5 Cost and the daily spend cap (APIs only)

Each API call's cost is **calculated** in code: its tokens times a code-owned price table (`API_PRICES_V1`, Decimal, per model: input, cached input, cache write, output; source and date recorded; changed only by an update). `OBSERVED` on the vendors' pricing pages on 2026-10-31: `claude-sonnet-5-5` $2.00 input and $10.00 output per million tokens, cache reads $0.20; `gpt-6.1-sol` $2.00 input, $0.10 cached input, $10.00 output. At today's pace (§2) that is roughly **$3 to $7 a day** per API before caching, depending on how many thinking or reasoning tokens each answer uses; the first day measures it.

An API card needs a **daily cap** before it can be picked (prefilled $10, the owner can change it). When the day's calculated cost reaches it, no model call starts on that provider until 00:00 UTC (`SPEND_CAPPED`, like the usage-limit block: entries wait, exits and code's protection do not); raising the cap ends it at once. The card also points to the vendor's own monthly limit as the backstop the app cannot see. As built: a call that times out or is canceled gets no usage back and its cost is not counted, so the day's total can be under what the vendor bills (found by the independent review; whether the vendors bill an aborted request is not verified).

### 5.6 The pages

Built with the official shadcn skill after the redesign's Settings part; preset `b2fms61Bqi`; the new primitives `RadioGroup` and `Popover` added with the shadcn CLI (registry lookup first; the CLI runs on the owner's PC, the cloud proxy refuses its registry). No disclaimers ([DECISIONS 2026-10-30](../../DECISIONS.md#2026-10-30--no-disclaimers-on-the-pages)).
- **Settings → Provider** (`#provider`, after `#models`): a `RadioGroup` of four choice cards (shadcn's `Field` choice-card pattern; two by two on wide screens, stacked on a phone), in the Models cards' look. Each card: a Lucide icon with a word (terminal for the CLIs, key for the APIs), the name, a `Badge` (In use, Ready, Needs sign-in, Needs key, Check failed, Switching with a `Spinner`), one line on how it is paid and what it shares, the model per agent, its usage bars (§3, each with "resets in" and the reading's age), the credential row (status, last four characters, saved date; Add, Replace, Remove), and for an API the daily cap (`Field` + `Input`) and today's and this month's calculated cost. What the provider does not report is one muted line ("No weekly limit: pay per token"). The Models cards keep showing each agent's calls and tokens.
- **Header**: a ghost icon button with a gauge icon and the in-use provider's tightest figure (the highest used percentage, or the day's cost against the cap), `aria-label` "Agent usage"; on a phone the icon and figure only. It opens a `Popover`: the provider's name and badge, a `Progress` per window with its percent, reset time and age, today's calls and tokens, and a link to Settings → Provider. When the provider reports nothing yet: "No reading yet".
- **Cockpit**: the engine room chip shows the same figure instead of "Allowance ok", with the same tone rules (warning from 80%, blocked when refused).

### 5.7 Records

One migration (the next free number at build time): `agent_provider_requests` (the owner's picks and their outcome), `agent_usage_readings` (provider, read at, source, document), `agent_spend_caps` (provider, Decimal per day, set at), a `provider` and a calculated `cost_usd` (NUMERIC, null on the plans) on each call's record, runtime events `PROVIDER_REQUESTED`, `PROVIDER_IN_FORCE`, `PROVIDER_REFUSED`, `CREDENTIAL_SAVED`, `CREDENTIAL_REMOVED`, `SPEND_CAPPED`, `SPEND_CLEARED` (no secret in any), and the definitions `MODEL_TABLE_V3`, `MODEL_TABLE_V4`, `EGRESS_ALLOWLIST_V3`, `API_PRICES_V1`, `PROFILE` version 5, seeded with their hashes as before. New reads: `GET /v1/agent-providers`, `GET /v1/agent-usage`; writes (service key, same-origin through the web server): `POST /v1/agent-providers/select`, `PUT`/`DELETE /v1/agent-providers/{provider}/credential`, `PUT /v1/agent-providers/{provider}/daily-cap`.

## 6. Authority and the rules that change

- **Rule 10** of [AGENTS.md](../../../AGENTS.md) and the row Authoring/runtime of [DECISIONS](../../DECISIONS.md) name the four providers, the Codex CLI's ChatGPT login staying the default, and keep "paid API fallback is disabled": a paid API runs only when the owner picks it and sets its cap. [ROADMAP](../../ROADMAP.md#later-and-separately-approved) moves "paid APIs" for the agents out of "Later and separately approved" on the owner's yes (§15); paid data stays there. [CONFIGURATION](../../CONFIGURATION.md)'s "Paid API fallback: disabled" stays, its "No API key … exists in production configuration" becomes "only in the runner's `agent_keys` volume, entered by the owner".
- **The owner's controls** gain the pick, the credentials and the cap; no agent has a tool for any of them, and a model's text cannot reach them ([AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md)). Rule 4 holds: the agents' tools, limits, policy, templates and prompts do not change with the provider.
- **Unchanged**: paper only; the trader, its generation and prompt, `FUTURES_POLICY_V1` and its limits, the sizing, the costs, the twins, the scores, the reviewers, the coach, code's protection; the threads never read or enter a key.

## 7. Requirements and tests

| ID | Requirement | Test |
|---|---|---|
| P1 | Each adapter returns the same result shape; a valid answer completes, a refusal, a cut answer, a 429, a 401 and a timeout map to their classes | runner, offline: fake Messages and Responses servers, update 1's offline stand-in for Claude Code, the fake Codex CLI |
| P2 | No native tool: a Claude CLI tool call other than `StructuredOutput` kills the job; the API requests carry no `tools` | runner: the pinned binary against the stand-in; request bodies recorded by the fakes |
| P3 | Each provider's gateway port allows only its own hosts | runner: each port, a connection to another provider's host refused |
| P4 | A credential is stored only in `agent_keys`, never echoed, logged or stored in the database, and survives a runner restart | runner and engine: a marker key searched in logs, database dump, API answers and image layers; restart test |
| P5 | The switch: the new profile in force only after a passed check; a failed check keeps the old; a running workflow finishes on its own profile; idempotent and versioned | engine, scratch PostgreSQL, scripted runner |
| P6 | No automatic move to another provider on a limit, a cap or an error | engine: each blocked state with three ready providers; nothing changes |
| P7 | Codex usage: windows named by duration, reset times, age; an app-server failure leaves the last reading and says so | runner: the pinned `codex app-server` against a stand-in backend; engine: readings |
| P8 | Claude CLI usage: one window per event, status without a percentage shown as "below the warning level" | runner and web unit |
| P9 | API cost: Decimal, from the price table, cache reads and writes priced apart; the cap blocks at the first call over it and clears at 00:00 UTC or when raised | engine, without a database and on scratch PostgreSQL |
| P10 | Settings: four cards, one In use, states, credential forms, the confirmation, Switching, Check failed; keyboard and screen reader | web unit and browser suite, light and dark, desktop and phone |
| P11 | Header button and Cockpit chip show the tightest figure; "No reading yet"; the APIs show cost and no session or week bar | web unit and browser suite |

## 8. Official sources

`OBSERVED` on 2026-10-31:
- Codex `rust-v0.159.2` ([`openai/codex`](https://github.com/openai/codex/tree/rust-v0.159.2)): `codex-rs/exec/src/exec_events.rs` (no rate limits in the exec JSONL), `codex-rs/protocol/src/protocol.rs` (`TokenCountEvent.rate_limits`, `RateLimitSnapshot`, `RateLimitWindow`: "Percentage (0-100) of the window that has been consumed", "Rolling window duration, in minutes", "Unix timestamp … when the window resets"), `codex-rs/app-server-protocol/src/protocol/common.rs` (`GetAccountRateLimits => "account/rateLimits/read"`) and its JSON schema (`GetAccountRateLimitsResponse`, `excludeResetCreditDetails`: "Skip the separate reset-credit detail lookup for background usage polls").
- Claude Code: `@anthropic-ai/claude-agent-sdk` 0.3.309 (bundling Claude Code 2.1.309), `sdk.d.ts`: `SDKRateLimitEvent` ("Rate limit information for claude.ai subscription users"), `SDKRateLimitInfo`, `ModelUsage`, `total_cost_usd` ("An estimate, not a billing statement"). Update 1's evidence in [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#claude-code-cli). The newest releases on npm: 2.1.309 stable, 2.1.316 latest.
- Anthropic, [Rate limits](https://platform.claude.com/docs/en/api/rate-limits): the `anthropic-ratelimit-*` headers, per-minute token buckets, monthly spend limits, no spend reported by the API; the Claude API skill's model table (cached 2026-10-06) and structured outputs (`output_config.format`).
- OpenAI, [Rate limits](https://developers.openai.com/api/docs/guides/rate-limits): the `x-ratelimit-*` headers, RPM/RPD/TPM/TPD, monthly usage limits, no header for money; [Pricing](https://developers.openai.com/api/docs/pricing): `gpt-6.1-sol` $2.00 / $0.10 / $10.00 per million.
- shadcn skill (raw GitHub `skills/shadcn/SKILL.md`, SHA-256 `93951e5e…7592`, the same as recorded before): option sets, `RadioGroup` for a single choice, `Field`/`FieldSet` for grouped radios, `Popover` for info.

To verify at build, at the versions installed then: the `anthropic` and `openai` SDKs' structured-output and client options; the Claude Code release's flags, stream and `init` inventory; the app server's `initialize` handshake.

## 9. Data and trust boundaries

New: two vendor hosts (`api.anthropic.com` already listed in V2; `api.openai.com`), two Python dependencies in the runner image (`anthropic`, MIT; `openai`, Apache-2.0; exact versions and hashes in [LIBRARIES](../../LIBRARIES.md)), the Claude Code binary back in the runner image, one volume (`agent_keys`), and secrets that cross the web server and the engine once on their way to the runner. The browser sends a secret only in the credential form's request (same-origin, Host and CSRF checks as every write); the engine forwards it without storing or logging it; only the runner reads `agent_keys`. Each provider's traffic goes through its own gateway port (§5.1); the gateway still refuses IP literals and private ranges. A model sees the same inputs whatever the provider.

## 10. Implementation sequence

1. While the redesign ships (no web file): the runner's adapters and credential store, `codex app-server` usage reads, the gateway's per-provider hosts; the engine's profile version 5, switch, readings, prices, cap, routes and migration; tests P1–P9.
2. After the redesign's Settings part is installed: the Provider section, the header button, the Cockpit chip; tests P10–P11; screenshots light and dark, desktop and phone.
3. The contracts: [RUNTIME_AGENTS](../RUNTIME_AGENTS.md), [SECURITY](../../SECURITY.md), [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), [CONFIGURATION](../../CONFIGURATION.md), [API_CONTRACTS](../../API_CONTRACTS.md), [DATA_CONTRACTS](../../DATA_CONTRACTS.md), [FRONTEND](../../FRONTEND.md), [INTEGRATION_EVIDENCE](../../INTEGRATION_EVIDENCE.md), [LIBRARIES](../../LIBRARIES.md), [DOCKER](../../DOCKER.md), [COMMANDS](../../COMMANDS.md), [STATUS](../../STATUS.md); rule 10 and ROADMAP (§6).
4. An independent review of the credential path and the switch, then one update the owner starts with a double-click, after the redesign's last install is checked. Codex stays in force; nothing calls a new provider until the owner picks it.

## 11. Verification commands

Cloud, as in [COMMANDS](../../COMMANDS.md): from `apps/web`, `pnpm typecheck`, `pnpm lint`, `pnpm check`, `pnpm api:check`, `pnpm test`, `pnpm build`; from `services/engine`, `ruff check`, `python -m app.export_openapi --check`, the suite without a database, then the new and affected database tests and the browser suites on a scratch PostgreSQL; from `services/agent-runner`, `python3 -m unittest tests.test_units` and the process tests with the fakes. `NOT RUN` in the cloud and left to the PC: the Docker image builds, the update and its checks, and the first real call of each new provider, which is the check of the owner's first switch to it.

## 12. Failure and rollback

- A new provider's check fails: the old one stays in force; the card shows why.
- The provider in force refuses (limit, cap, key revoked, sign-in expired): new entries wait, code's protection continues, the card and the header say why and when it may clear; the owner may pick another ready provider.
- `codex app-server` fails or changes its answer: the last reading stays with its age; decisions are unaffected.
- A price changes: the calculated cost is off until an update changes `API_PRICES_V1`; the vendor's own limit is the backstop.
- Rollback: the previous images; the migration only adds tables and nullable columns. Keys stay in `agent_keys` until the owner removes them.

## 13. Q01–Q10

Q01: the Provider section, the header button and the chip checked in the browser at both widths and themes (P10, P11). Q02: shadcn primitives only, labelled; keyboard reachable radio cards. Q03: no ledger or order path changes; the switch never interrupts protection (P5, P6). Q04: credentials (P4), egress (P3), same-origin writes, an independent review. Q05: §12; P5–P7. Q06: one app-server read per 10 minutes; no extra model call except the switch's check. Q07: every figure labelled reported or calculated, with its age (§3). Q08: the records of §5.7. Q09: the update and its checks on the PC; the first live call of each new provider is the owner's first switch. Q10: this plan's §16.

## 14. Decision log

The owner delegates engineering choices ("decide for me", 2026-10-19); the thread's recommended options:
- **Direct API calls for the two APIs**, through the vendors' own SDKs, not the CLIs with an API key: one structured answer per call with no native tool to disable, the rate-limit headers, exact token counts and prompt caching under the app's control.
- **One runner with four adapters**, not one container per provider: one job protocol, one place for credentials, and one gateway port per provider limits each adapter to its vendor's hosts.
- **Keys pasted in Settings** rather than a sign-in file to double-click: one place, no extra window; the runner alone keeps them. Codex keeps its existing sign-in.
- **Claude on `claude-sonnet-5-5` at medium** for both Claude cards (ExecPlan 0039's approved choice; the same price as `gpt-6.1-sol`); `claude-opus-5-5` (about twice the price) is a later update if the owner wants it.
- **Session and 5 hours shown once**, as "Session · 5 h", because both plans' session is that window.
- **A daily cap prefilled at $10** on each API, about twice the expected cost.
- **No automatic fallback** between providers.

As built (2026-10-31), also under "decide for me", each the recommended option:
- **The runner's own HTTP client for the two APIs**, not the vendors' SDKs (§5.1 named them): the runner image keeps no package manager and no third-party package, and one structured request per call (the role's schema as the strict output format, no `tools`) needs no SDK feature. The answer's tokens and rate-limit headers are read as the SDKs would expose them.
- **No server-side fallback** of any kind: a request the provider refuses is one refused call, as on Codex.
- **Claude Code `2.1.308` kept**, update 1's pinned and recorded binary, rather than a newer release without the same offline evidence.
- **A button and a confirmation per card**, not a `RadioGroup` (§5.6): it is not installed, the shadcn skill fits it to a form value, and a switch is a consequential action the owner confirms; the header's button is outlined like the bell beside it rather than ghost.
- **Codex's windows read every 10 minutes** while Codex is in force, and once after a refused call; the other providers report with each answer.
- **During a switch's check the agents pause** (corrected after the independent review, which found the first wording wrong): until the new provider's profile is composed the worker reconciles the in-force profile against its own provider's runner status and the agents go on; from then the runtime is on the new profile in `PROBE_ONLY`, only the check's calls run and work started on the old profile ends `PROFILE_MISMATCH`. The pause lasts the check, at most 20 minutes, and fails closed; the engine's stops are not held back. After a refused switch the provider in force comes back at once (`VERIFIED_BEFORE`) with its usage-limit block; the owner's pick always runs its check.
- **Coming back to the provider in force after a refused or superseded switch** puts it in force at once (`VERIFIED_BEFORE`), without another test call, and puts back its usage-limit block. The owner's own pick of a provider always runs the check, even when its profile passed one before (corrected after the independent review: the first build skipped it, so a key revoked since would only have shown at the first decision).
- **The credential routes behind their own key** (`agent_credentials_key`), held by the API service and the runner, not by the agent worker; `platform.claude.com` dropped from the Claude CLI's hosts, since its token is made on the owner's PC.
- **Dedicated tables** for the picks, the caps and the readings, and the call's provider and cost as columns, as §5.7 proposed.
- **The Claude CLI's `utilization` scale** is read as a fraction up to 1 and as a percent above it: NOT VERIFIED against a live event.
- **The words elsewhere name the provider in use** (the status notes, the agents' rows, the trader card, the Models card), with a new note place "Provider"; Codex's words stay as they were.

## 15. The owner's decision

ROADMAP kept paid APIs "later and separately approved", so the thread asked once, on a card: "Include the two pay-per-token APIs (Claude API, OpenAI API)?". `OBSERVED`: at 08:03:30 UTC the owner picked **"Yes, all four with a daily cap"** ("API keys go in Settings. Paid calls stop at a daily cap (prefilled at $10, you can change it). At today's pace, about $3-7 a day while an API is in use."), recorded in [DECISIONS](../../DECISIONS.md#2026-10-31--the-agents-provider-four-to-choose-from-the-two-apis-with-a-daily-cap-execplan-0049) and [ROADMAP](../../ROADMAP.md#later-and-separately-approved). Rule 10 and the contracts of §6 change with the update that builds it.

## 16. Progress

- 2026-10-31: the plan written; the sources of §8 read; the redesign thread asked about its parts and the Settings boards (its answer in §2).
- 2026-10-31 08:03 UTC: the owner's yes to all four providers with a daily cap (§15); the plan APPROVED.
- 2026-10-31 15:45 UTC: built in the cloud on `claude/project-thread-gtmydt` after the redesign's Settings part was installed (`5aa35ca`): the runner (four adapters, the credential store, one gateway port per provider, the Codex app server's windows), the engine (migration `0029_agent_providers`, profile version 5, the switch, the readings, the cost and the cap, the routes), the web (Settings → Provider, the header's usage button, the Cockpit's chip, the provider's name in the notes), and the contracts of §10 step 3. VERIFIED offline as [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#execplan-0049-four-providers--2026-10-31) records: runner 28 provider tests, engine provider and model tests on a scratch PostgreSQL, web types, lint, 392 unit tests and the build. NOT RUN: the Docker images, the browser suites and screenshots, the update on the PC, and any live call; the independent review of the credential path and the switch comes before the merge.
- 2026-10-31 16:30 UTC: the independent review of the credential path, the switch and the cap ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#execplan-0049-four-providers--2026-10-31)). Nothing serious on the credential path. Fixed: the owner's pick always runs its test call; a refused switch puts the old provider's usage-limit block back; a 401 on an old key never marks a key saved meanwhile; the isolated test runner has its own key volume. Corrected: the agents pause during a switch's check (§5.3, §14), and a canceled or timed-out API call's cost is not counted (§5.5). Rerun offline after the fixes: runner `tests.test_providers` 29 OK; the engine's provider, runtime, in-force, check, agent, API and schema suites on a scratch PostgreSQL; the web's agents tests, lint and types. The full engine suite on a fresh database: `6 failed, 1940 passed, 74 errors`, all of them `main`'s or the quiet window's (INTEGRATION_EVIDENCE).
- 2026-10-31 19:04 UTC: PR #157 merged on the owner's yes (card "Yes, merge when green"), after the full suite above.
- 2026-11-01 01:24 UTC: **installed** by the owner's double-click (`update-20261101T011919Z`, `COMPLETE`, source `836e6ce`, which holds #157's `26ae7f6` and the redesign's docs-only #156): backup taken, migration `0028_leaner_trader` to `0029_agent_providers` in one attempt, reconciliation OK, the five pages 200, nine services recreated (the runner with the Claude Code CLI), the agents back to `ENABLED` with `CHECK_PASSED`. The new profile (version 5, `CODEX_CLI`) came into force at 01:23:13 UTC and its check passed at 01:23:20 UTC, so the agents waited 7 seconds. Checked read-only on the PC on 2026-11-01 08:00 to 08:10 UTC (OBSERVED): all ten containers up, none restarted; no error, traceback or refusal in the logs of the agent worker, runner, gateway and API since 01:24 UTC, and every API request 200; Codex's windows read every 10 minutes (40 readings, all ok; at 07:54 UTC the 5-hour window 9% used, the weekly 32%); 31 calls on Codex since the install, every workflow `SUCCEEDED` (29 decisions, one decision review, one coach); no pick, no cap, no cost recorded (no paid API in use); Settings → Provider shows the four cards, "In use", the 5-hour and weekly windows and the daily cap. NOT RUN: the header's usage popover in the owner's browser (the API's log names no path, so its reads cannot be told apart), a switch to another provider, and any key or paid call; they come with the owner's first use.
- 2026-11-03 11:43 UTC: on the owner's first try, the Claude API card refused a personal Console key (`sk-ant-usr…`): the page, the engine and the runner took only `sk-ant-api` keys, the one prefix the plan's sources showed. The Console now issues personal and service account keys and calls the old one a legacy workspace key ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#claude-console-keys-execplan-0049--2026-11-03)). The three checks now take `sk-ant-usr`, `sk-ant-svc` and `sk-ant-apiNN` keys and still refuse an Admin API key, a Claude Code token or an OpenAI key; an engine test holds the engine's shapes equal to the runner's. Built by the project thread "Check Claude CLI support for agents".
- 2026-11-03 12:19 UTC: that fix (PR #169, `5758605`) **installed** by the owner's double-click (`update-20261103T121448Z`, `COMPLETE` 12:14:40 to 12:19:57 UTC, no migration, schema `0031_decision_replays`, reconciliation OK, the five pages 200, nine services recreated). Checked read-only on the PC at 13:01 UTC (OBSERVED): ten services up and healthy, no error, traceback or refusal in the runner, agent worker, API or web logs since 12:19:57 UTC; Settings serves the new placeholder `sk-ant-usr…` and the help text that names personal and service account keys and the workspace; the agents `ENABLED` on the Codex CLI with no new profile, ten trader decisions `SUCCEEDED` in the two hours up to 13:00 UTC; no key saved and no pick made yet. NOT RUN: a saved personal key and the switch's test call; they come with the owner's first use.
