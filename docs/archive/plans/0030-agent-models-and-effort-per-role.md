# ExecPlan 0030 — A model and reasoning effort per agent role, and the usage-limit block

**Status: PROPOSED 2026-10-19, then trimmed by [ExecPlan 0031](0031-m8-simple-app-that-runs-itself.md) the same day; not implemented.** The owner picked "Cut to essentials" at 11:37:19 UTC ([DECISIONS](../../DECISIONS.md#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031)). What stays, built in M8's updates (0031 §9): the model table, the worker's composition, the usage-limit block and the token summary. What goes: the owner's approval of the profile, Allow probes, both probe suites as gates, and Enable; a short automatic check replaces them (0031 §4.7). The text below was trimmed to match in 0031's first part (2026-10-19); the model table comes with M8's second update. Written by the project thread "Agent setup and best models" from `main` at `66951e3`, on the owner's ask of 2026-10-19 08:30 UTC ([DECISIONS](../../DECISIONS.md#2026-10-19--the-owner-delegates-the-agents-model-choice-no-profile-change-during-m7s-switch-on)). Nothing here touches M7, its profile `9a7e664d9186` or its records. Planning only: no code, no command against any application.

Labels: `OBSERVED` (seen in code, records or a vendor page), `INFERRED`, `PROPOSED`, `NOT RUN`.

## 1. Goal and observable outcome

The owner does not want to choose models: "I don't want to configure agents which model to use, I want you to research and use the best model for the agent" (08:30 UTC), and, at 08:42 UTC, asked that the configuration leave the UI and happen "in the background". The app, however, binds one model and one reasoning effort for every role, chosen by the owner in a form, so the only choice it can express is a compromise. The goal is that each role runs on the setting the vendor's guidance names for its kind of work, that this table lives in code and is reviewed like the prompts, that the app composes the profile from it by itself and records it in force with its hash ([ExecPlan 0031 §4.5](0031-m8-simple-app-that-runs-itself.md#45-in-force-records-instead-of-approvals)), and that the allowance the agents use is visible.

Observable after the deployment:
1. The Agents page has no model or effort picker. When the runner is logged in and discovery has run, the app composes a profile from the code's model table (§4.1), records it in force as `SYSTEM` and shows it with its hash, the table and its consequences; the owner chooses nothing and approves nothing.
2. Each model call is made with the role's own model and effort (the provider-call row records both, as today).
3. The Agents page shows tokens used per workflow and per UTC day, from the rows the app already stores.
4. A call the provider refuses for the usage limit ends `QUOTA_BLOCKED`; the runtime shows the block and resumes when it clears; the short check met by it reruns after the block, without latching ([ExecPlan 0031 §4.7](0031-m8-simple-app-that-runs-itself.md#47-the-agents-models-the-usage-limit-and-the-short-check)).
5. Every existing test of the single-model profile has a per-role counterpart, and the probes cover every model the table names.

## 2. Current facts (OBSERVED in code at `66951e3` unless marked)

- **One setting for all roles.** `profile.compose` writes `model` and `reasoning_effort` once (`app/agents/profile.py:84`); `Runtime.model()` returns that pair with no role argument (`app/agents/orchestrator.py:92`), and `_send_step` uses it for every generation and template (`orchestrator.py:510`). The compose request takes one model and one effort (`app/main.py:1592`, `app/agents/controls.py:396-398`); the form has one field of each (`apps/web/src/agents/agents-page.tsx:578-608`).
- **The runner already takes the pair per job.** `POST /v1/jobs` carries `model` and `reasoning_effort` (`runner/server.py:195-200`) and `invocation.argv` builds `-m` and `model_reasoning_effort` from them (`runner/invocation.py:110-121`). No runner change is needed for a per-role table.
- **What the owner chose, and on what basis.** `gpt-6.1-sol` at `medium` since 2026-10-02, on the vendor's descriptions and the 120 s step deadline, "not a measurement" ([DECISIONS](../../DECISIONS.md#2026-10-02--m5-b-started-runtime-profile-gpt-61-sol-at-medium-effort-execplan-0020)). The profile approved on 2026-10-19 at 08:25 UTC (seq 2, `9a7e664d9186`) keeps it.
- **The catalog the app offers** is the online catalog discovered on 2026-10-02 ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#model-catalog-and-model-descriptions-m5-b-2026-10-02)): seven `code_mode_only` models, `gpt-6.1-sol` with default effort `low` and efforts low to ultra, `gpt-6-luna` default `medium` and efforts low to max, `gpt-6-astra` default `medium`. Discovery runs again only when the runner's binary, config or account hash changes (`app/agents/runtime.py:113-120`), so the list stays that of 2 October until then.
- **Only `code_mode_only` models can be named** (M5-OD1; `profile.py:71-73`). NativeBehavior evidence exists for `gpt-6.1-sol`, `gpt-5.6-sol` and `gpt-6-luna` sending no tools ([ExecPlan 0020 §16 item 48](0020-m5-agent-runtime.md#16-decision-log-proposed)).
- **Live latency on this setting.** 17 completed probe calls of 2026-10-02: model step 11.8 to 26.4 s, median 13.7 s, p95 18.8 s ([ExecPlan 0026 §15, B3's table, row 4](0026-m7-agent-driven-main-decisions.md#b3--the-engines-intake-the-checks-until-the-fill-the-limits-and-the-intent-stream-2026-10-11)). The step deadline is 120 s (`app/agents/definitions_v3.py:198`); a decision has 900 s of running time and the policy's intent expiries are minutes.
- **Prompts.** The M7 role prompts (`services/agent-runner/prompts/m7/`) are developer-style instructions with identity, rules, inputs and output sections, name only granted tools, and end "Keep explanations brief. Do not include hidden reasoning." The invocation hides reasoning and asks for no reasoning summary (`runner/invocation.py:56-57`). The role prompt comes first and the job context last (`app/agents/prompting.py:3-5`), which is the order the vendor's caching guidance asks for.
- **Tokens are stored, not shown.** The runner keeps `input_tokens`, `cached_input_tokens`, `cache_write_input_tokens`, `output_tokens` and `reasoning_output_tokens` in the JSONL summary (`runner/jsonl.py:17-18`); the engine stores it in `agent_provider_details.jsonl_summary` (`orchestrator.py:663`). No owner view sums them.
- **A profile change costs.** A new profile drops the approval's effect: probes again (capability run at most 70 live calls, decision suite at most 40; `definitions_v3.py:226`), Enable again, and a new evaluation segment ([ExecPlan 0026 §5.11](0026-m7-agent-driven-main-decisions.md#511-evaluation-segments-and-comparisons)).
- **The allowance is one and shared.** The profile's consequence text says the workflows run "sharing the owner's ChatGPT usage allowance" (`profile.py`, `consequences`). OBSERVED by the owner on 2026-10-19: the first M7 capability run failed on the Codex usage limit ("it was usage limit", thread "Build M7", 08:37 UTC), after the owner's own Codex use on the same account.
- **A usage-limit refusal is not recognized.** `runner/jsonl.py:98-104` keeps two candidate patterns ("you've hit your usage limit", straight and curly apostrophe) with `verified_by_observation` false, so `classify_failure` (`jsonl.py:108-118`) returns `PROVIDER_UNAVAILABLE` and names `QUOTA_BLOCKED` only as a candidate. The orchestrator ends a step `QUOTA_BLOCKED` only on that class (`orchestrator.py:729-732`); otherwise the call is a plain failure, `probes._technical` flags its outcome (`app/agents/probes.py:246`), the probe fails and the run latches `CAPABILITY_LATCHED` (`probes.py:18`, `740`). OBSERVED on the PC (reported by Build M7, 08:40 UTC): run 2's `error_candidates` were empty, so the stored text may match neither candidate pattern; it must be read before the fix is designed.

## 3. Scope and exclusions

**In scope (M8):**
- a code-owned model table (§4.1 and §4.2), versioned and hashed like a prompt;
- profile version 4 composed by the app from that table, its validation, view, consequences and approval dialog;
- the orchestrator choosing the pair by the workflow's role;
- the Agents page: the compose form removed, the table in the profile card and the approval dialog, and a token summary;
- the usage-limit block: a verified pattern from the stored observation, and a probe run that ends unverified instead of latching on it;
- tests for each, and the contracts that describe the profile.

**Not in scope:**
- M7, profile `9a7e664d9186`, and anything deployed before M8 (nothing here lands while M7's switch-on is in flight).
- A different model per template, prompt changes, budget changes, more roles, or a role's permissions.
- A model picker of any kind for the owner. A change of the table is a code change, reviewed in a pull request and probed; an owner who wants a different model asks for one in the project and the table's next version carries it.
- Any measured claim that one setting is more accurate than another; §4.4 says what M8 measures.
- A second ChatGPT account for the app, credits, or any paid API fallback (forbidden by [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#authentication-and-capacity)).

## 4. Design (PROPOSED)

### 4.1 The table, from the vendor's guidance

The recommendation per role, read from the sources in §6. It is a reading of the vendor's task descriptions, not a measurement on this workload; none exists.

| Role | Templates | Model | Effort | Why (vendor wording, §6) |
|---|---|---|---|---|
| `COORDINATOR` | `PORTFOLIO_DECISION_V1`, `PROMOTION_V2` | `gpt-6.1-sol` | `medium` | "Judgment-heavy work, such as planning a feature or comparing options" is medium; the decision has minutes, not hours, and a 120 s step deadline |
| `ANALYST` | `MARKET_BRIEF_V1`, `EVENT_INVESTIGATION_V1`, `MARKET_ASSESSMENT_V1` | `gpt-6.1-sol` | `medium` | "research" and "data analysis" sit at medium and low; a brief weighs sources, so medium |
| `EVALUATOR` | `BRIEF_REVIEW_V1`, `INTENT_REVIEW_V1`, `OUTCOME_REVIEW_V1`, the M5/M6 reviews | `gpt-6.1-sol` | `high` | "careful review" is high; its 4-step, 300 to 600 s budgets leave room for slower steps |
| `RESEARCHER` | `RESEARCH_V1` | `gpt-6.1-sol` | `medium` | "research" is medium; "deeper research" at xhigh only "when your evals show a clear benefit" |

- `gpt-6.1-sol` everywhere: the vendor's "balanced speed, cost, and intelligence" model and the named replacement for GPT-5.5 on paid plans. Not `gpt-6-astra`: five times the allowance per token, slower, and the vendor places it where "cost and latency don't matter". Not `gpt-6-luna` by default: it is described for "focused, repeated tasks with a clear goal" (extraction, classification, structured summaries); the outcome review is the only role work of that shape, and §4.4 measures it there before any default changes.
- The evaluator at `high` is the one change from today. The vendor says to "evaluate both medium and high for a given task", so §4.4 compares them before the table becomes the standing default; until then the table is what the app composes first in M8.
- An effort the discovery does not list for a model is refused at composition, as today (`EFFORT_NOT_DISCOVERED`).

### 4.2 The model table in code, and profile version 4

- **`MODEL_TABLE_V1`** is a definition document under `app/agents/` (next to the budgets), `PROPOSED` like them, with one entry per role: a list of `(model, reasoning_effort)` pairs in order of preference, the first being §4.1's. The fallbacks per role, in order: `gpt-6.1-sol` at the role's effort; `gpt-6-sol` at the same effort; `gpt-5.6-sol` at the same effort (both `code_mode_only` in the 2 October catalog, `gpt-5.6-sol` with NativeBehavior evidence). No entry names `gpt-5.5` (retired, native tools) or a model the catalog hides. The table is hashed into the agent definition hashes, so it is bound by every profile and shown as a definition on the Agents page; a changed table is a changed definition: the worker refuses to start if the stored row differs from the code's, and the app composes a new profile and records it in force, as for a prompt.
- **Resolution.** `profile.compose(observation_id, discovery)` takes no model and no effort. For each role it takes the first pair of the table whose model the discovery lists as `code_mode_only` and whose effort the discovery lists for that model (or `DEFAULT`); a role with no such pair leaves `unset` non-empty with the reason `MODEL_TABLE_UNRESOLVED:<role>`, which blocks approval and is shown. The chosen pair per role is written into the profile under `roles`, and the table's hash beside it, so the approved document says exactly what will be sent. The top-level `model` and `reasoning_effort` fields are removed. `PROFILE_VERSION` becomes 4; `current()` then refuses every version-3 profile, as version 3 refused version 2, so the app composes a version-4 profile, records it in force and runs the short check.
- **Composition in the background.** On each pass, under the orchestrator lease, the worker composes a profile when the newest discovery for the runner's identity has no profile of this version and this table yet, with `source` `SYSTEM` (today's rows carry the owner's session as source). It composes once per discovery and table; a new discovery (a changed binary, configuration or account) or a new table makes it compose again. It records the row in force as `SYSTEM`, never as the owner; nothing waits for the owner. The owner's compose route and its idempotent replay are removed; the API's `POST` for a profile is gone, and the owner view lists the composed profile as today.
- `Runtime.model(role)` returns the role's pair from the approved profile; `_send_step` passes `workflow["role"]`. A probe workflow uses its own role's pair, so a capability run exercises every model the profile names (INFERRED: the suite has workflows of all four roles).
- `consequences()` names each role's model and effort.
- The owner view (`views.py:89`) and its Zod mirror (`apps/web/src/agents/schemas.ts:91-92`) carry `roles`; the compose body and its Zod mirror go.
- **What stays the owner's:** the agents' on/off switch. Approve, Allow probes, Start probes, Start decision probes and Enable after a change go with ExecPlan 0031 ([AUTONOMY_MATRIX](../contracts/AUTONOMY_MATRIX.md#m8-the-app-runs-itself-execplan-0031)).

### 4.3 The Agents page

Shadcn workflow as in [SHADCN_WORKFLOW](../../SHADCN_WORKFLOW.md), preset unchanged. The compose form (model select, effort select, Compose button) is removed, with its 2026-10-16 pre-fill rule, which has nothing left to fill. The profile card shows the composed profile with its hash, a four-row table (role, model, effort, and which preference it is), the definitions it binds, and that the app recorded it in force; a profile with `unset` shows the unresolved role and that a code change is needed. A "Usage" card lists, per UTC day and per workflow, the token fields summed from `agent_provider_details.jsonl_summary`, by model; it shows tokens, never credits (the rate card is per plan and moves). The System page's "needs profile approval" text goes.

### 4.4 What M8 measures before the table is the standing default

Under [EVALUATION](../EVALUATION.md#role-value-discovery-coverage-and-selection): one declared factor at a time, matched everything else, at the same total inference work.
1. Evaluator `medium` against `high`, on the review templates: verdict agreement with the recorded outcome, deficiencies found, step time and tokens.
2. Outcome review on `gpt-6-luna` (its catalog default effort) against the table: the same measures.
3. Tokens per decision, per brief and per review on the table, as the allowance figure the owner reads.

The design of these comparisons is M8's plan's; this plan only says what the profile must make possible (a per-role pair) and that no default changes on a summary ([EVALUATION](../EVALUATION.md#role-value-discovery-coverage-and-selection): "Do not auto-promote a variant, change models/prompts or widen risk from an evaluation summary"). A comparison that needs a second pair for one role runs under its own approved profile in isolation; the table does not change for it.

### 4.5 The usage-limit block

- First read the stored text of the 2026-10-19 refusal (`agent_provider_details.stderr_summary` and the JSONL `error` messages) on the owner's PC, read-only; it is the observation the contract requires (`jsonl.py:98-100`). If it matches a candidate pattern, mark that pattern verified; if not, add the observed phrase as a verified pattern. The runner image is rebuilt; `config_hash` does not change (patterns are not an override).
- A call that ends `QUOTA_BLOCKED` sets the runtime's quota block as today's code already provides (`runtime.py:311`), which pauses new model work until the next successful status read; no latch.
- A short check whose call ends `QUOTA_BLOCKED` ends without a verdict and reruns by itself after the block clears; nothing latches and the owner does nothing ([ExecPlan 0031 §4.7](0031-m8-simple-app-that-runs-itself.md#47-the-agents-models-the-usage-limit-and-the-short-check)).
- The runtime card on the Agents page names the block as "usage limit reached" with the time of the last refusal; the System page likewise.

## 5. Requirements and tests (PROPOSED)

| ID | Requirement | Tests |
|---|---|---|
| R1 | A version-4 profile binds four role pairs and the table's hash; a version-3 profile authorizes nothing once this code runs | `test_m5_profile.py` counterparts: compose, `current()`, `consequences()`, diff |
| R2 | Each role's step is sent with its own pair; the provider-call row records them | orchestrator tests with a scripted provider asserting `requested_model` and `reasoning_effort` per role |
| R3 | Resolution takes the first pair the discovery offers per role; a role with none blocks approval with `MODEL_TABLE_UNRESOLVED`; a changed table is a changed definition | compose tests over discoveries with and without each model; the definitions-drift test |
| R4 | The worker composes one `SYSTEM` profile per discovery and table, records it in force as `SYSTEM`, and composes again only for a new discovery or table; the owner compose route is gone (404) | worker tests; `ApiAuth` counterpart |
| R5 | A capability run exercises every model the profile names | probe test asserting each role's pair appears in the run's calls |
| R6 | A `QUOTA_BLOCKED` call pauses new model work and never latches; the short check met by it reruns after the block | runner unit test on the verified pattern; probe test |
| R7 | The token summary equals the stored rows; the owner view and its Zod mirror carry `roles` | view test over fixture rows; `api:check` |
| R8 | Browser: no picker, the profile card's table, the unresolved state, no Approve dialog, the usage card, at 390 px | `BrowserAgents` |

## 6. Official sources and versions

Read on 2026-10-19 through a summarizing fetch (wording paraphrased unless quoted); recorded in [REFERENCES](../contracts/REFERENCES.md#model-and-effort-guidance--2026-10-19). The installed Codex is `rust-v0.159.2` (`runner/invocation.py:16`); the vendor's pages do not say which guidance depends on the client version.

- MG-01, OpenAI "Using GPT-6": GPT-6 Astra "highest intelligence"; GPT-6.1 Sol "balanced speed, cost, and intelligence"; GPT-6 Luna "fastest and most cost-effective, for focused, high-volume tasks". 6.1 Sol's efforts low, medium (default), high, xhigh, max; `minimal` not supported. Keep request-level effort unchanged to preserve caching.
- MG-02, OpenAI "Reasoning models": `medium` is the "default configuration for most workloads"; `high` for "hard reasoning, complex debugging, and deep planning, where quality matters more than latency", and "evaluate both medium and high for a given task"; `xhigh` "only use when your evals show a clear benefit".
- MG-03, OpenAI "A model guide for the GPT-6 family" (2026-10-02): low for "routine tasks, such as extracting facts or making small edits"; medium for "judgment-heavy work, such as planning a feature or comparing options"; high for "difficult debugging, deeper analysis, or careful review"; Luna for "focused, repeated tasks with a clear goal". Prices per 1M tokens as listed: Astra 10/50, 6.1 Sol 2/10, Luna 0.10/0.50 (input/output, USD).
- MG-04, ChatGPT "Model selection": "if cost and latency don't matter, default to Astra"; 6.1 Sol at extra high for "decisions from conflicting evidence"; Luna with medium for small, scoped work.
- MG-05, ChatGPT "Models": GPT-6.1 Sol in the Codex CLI rollout for Plus, Pro and Business; GPT-5.5 retired from Codex with ChatGPT sign-in on 2026-10-14, GPT-6.1 Sol its replacement on paid plans; Luna's Codex default effort "start with High".
- MG-06, OpenAI Help "Codex rate card": credits per 1M tokens (input / cached / output): Astra 250 / 25 / 1,250; 6.1 Sol 50 / 2.5 / 250; Luna 2.5 / 0.25 / 12.5; "these multipliers describe allowance usage, not speed". The Plus and Pro rates are on a page the fetch did not reach.
- MG-07, OpenAI "Prompt engineering": developer messages first, sections Identity, Instructions, Examples, Context; reasoning models "will provide better results on tasks with only high-level guidance"; keep reusable content at the start for caching.
- MG-08, ChatGPT "Non-interactive mode" and "Config basics": `codex exec --output-schema` for "a final response that conforms to a JSON Schema"; `model_reasoning_effort` "tunes reasoning effort when supported"; `--ignore-user-config` and `--ignore-rules` for controlled runs. The app does all three (`runner/invocation.py:23-24`, `110-121`).

What the sources do not give: a benchmark of any model on this application's work, a Codex usage figure per model on the Plus plan, or a latency figure per effort. None is claimed.

## 7. Data and trust-boundary changes

- `agent_runtime_profiles.profile` gains `roles` and the table's hash; `source` gains the value `SYSTEM`; the definitions table gains the `MODEL_TABLE_V1` row (an additive migration seeds it beside the prompts, as `0009` seeded the generation-3 rows). The worker's composition is recorded in force as `SYSTEM`, never as the owner (ExecPlan 0031 §4.5); the owner keeps the off switch.
- No new permission, tool, template or prompt. A role's model does not change its grants ([AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md)). The owner loses the model picker, which was never an authority: the profile approval is.
- The token summary reads stored rows as the API identity; it exposes no prompt, output or secret.
- The usage-limit text is read from a stored, redacted field; no `codex_home` read.

## 8. Proposed file edits

- `services/engine/app/agents/`: a new `model_table.py` (`MODEL_TABLE_V1`), `generations.py` (its hash among the definitions), `profile.py`, `orchestrator.py`, `worker.py` (composition), `controls.py` (the owner compose route removed), `views.py`, `probes.py`, `main.py`; one additive migration; `services/agent-runner/runner/jsonl.py`.
- `apps/web/src/agents/agents-page.tsx` (form removed, table and usage card added), `schemas.ts`, tests; the generated API client.
- Contracts: [RUNTIME_AGENTS](../RUNTIME_AGENTS.md) (profile version 4, the table, composition by the worker), [API_CONTRACTS](../../API_CONTRACTS.md) (the compose route removed), [DATA_CONTRACTS](../../DATA_CONTRACTS.md) (profile document, the definition row), [OPERATIONS](../../OPERATIONS.md) (the usage-limit block and what the owner does), [TESTING](../TESTING.md).

## 9. Implementation sequence

1. Read the stored refusal text on the PC (read-only; no approval in chat is needed since 2026-10-19); design §4.5's pattern.
2. The model table, profile version 4 and the orchestrator (R1 to R3, R5), with tests.
3. The worker's composition and the API (R4); the web (R7, R8).
4. The usage-limit block (R6).
5. Delivered with M8's second update ([ExecPlan 0031 §9](0031-m8-simple-app-that-runs-itself.md#9-implementation-sequence)): the app composes the profile, records it in force and runs the short check; the owner only double-clicks the update. A new evaluation segment starts at the first submission under the new profile.

## 10. Verification

In the cloud: web lint, typecheck, unit tests and build; Ruff; the OpenAPI drift check; the database-free pytest. In the cloud also the PostgreSQL pytest and the browser suites on a scratch PostgreSQL; on the owner's PC only the update's own checks ([ExecPlan 0031 §4.8](0031-m8-simple-app-that-runs-itself.md#48-tests-and-the-fast-lane)). Every one of them `NOT RUN` at this writing.

## 11. Failure and rollback

A version-4 profile that cannot be approved leaves the runtime waiting for a profile, as a version mismatch does today; the previous images are retagged `:pre-m8` by the deployment script. No data migration, so a rollback is the images. A pattern that misclassifies a real provider outage as the usage limit would pause work until the next status read, never trade; the pattern is verified against a stored observation first.

## 12. Q01-Q10 (affected gates)

| Gate | Applicability | Condition |
|---|---|---|
| Q01, Q02 | The profile card's table, the unresolved state and the usage card | Loading, empty, error and stale states; keyboard and labels; 390 px |
| Q03 | Resolution per role; the role-to-pair binding; one composition per discovery and table | R1 to R5 |
| Q05 | The usage-limit block | R6 |
| Q07 | All of the above | §10 |
| Q08 | The block is visible and truthful | R6, the runtime card |
| Q09 | Deployment with no owner step | §9 step 5 |
| Q10 | Vendor guidance against the pinned version; contracts updated | §6, §8 |

## 13. Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-10-19 | The table lives in code and the app composes the profile; no picker | The owner's words of 08:30 and 08:42 UTC. A versioned definition is reviewed, hashed and probed like a prompt; the owner's approval of the exact profile stays, because it is the authority, and the picker never was |
| 2026-10-19 | Fallbacks per role, in order | A catalog withdraws models (GPT-5.5 on 2026-10-14); the app then composes from the next pair instead of waiting for a code change, and the owner sees which preference it took |
| 2026-10-19 | Per role, not per template | One row per role is what the owner reads and approves; a template-level table is a later refinement if §4.4 shows a reason |
| 2026-10-19 | `gpt-6.1-sol` for every role; evaluator at `high`; no Luna by default | §4.1 and §6; the allowance is shared with the owner's own Codex use, so no role moves to a dearer model, and a cheaper one is measured before it is used |
| 2026-10-19 | Tokens, not credits, on the page | The rate card is per plan and may change; tokens are what the app observes |
| 2026-10-19 | Trimmed by ExecPlan 0031: no profile approval, no probe suites as gates, no Enable after a change | The owner picked "Cut to essentials" (11:37:19 UTC) |
| 2026-10-19 | Nothing before M8 | A profile change now would drop the approval of 08:25 UTC, cost up to 110 probe calls on the allowance that ran out today, and start a segment during M7's first live days |

## 14. Progress and completion evidence

- 2026-10-19: §4.5, the usage-limit block, is implemented in M8 update 1 ([ExecPlan 0031 §15](0031-m8-simple-app-that-runs-itself.md#15-progress); [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-the-agents-check-the-usage-limit-and-one-switch-execplan-0031)). The PC's stored outcomes were read read-only: the 50 failed calls between 08:26 and 12:06 UTC all carried the usage-limit candidate and none lacked it; the rows keep counts, not the text, so both spellings were marked verified. Differences from §4.5: the block lifts at the first completed call, which the agents' check makes (10 minutes after the first refusal, doubling up to 2 hours), not at a status read; the runner now keeps up to five of a failure's own messages so the next refusal can be read. Everything else in this plan waits for update 2.

Before that, nothing implemented. The docs-only pull request that records this plan, the decision and the sources is listed in [COMMANDS](../COMMANDS.md#agent-models-and-effort-per-role-documentation--2026-10-19).
