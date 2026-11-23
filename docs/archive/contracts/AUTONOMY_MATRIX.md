# Autonomy, permission and approval matrix

## Canonical authority

This document owns **who may request an action and when approval is needed**. [RISK_POLICY.md](RISK_POLICY.md) owns financial limits. **Since [ExecPlan 0060](../../plans/0060-spot-trading-only.md)'s update the [ExecPlan 0060 section](#execplan-0060-spot-trading-only-m12) at the end is in force:** the account trades Bitcoin spot by a code rule and the app has no runtime agents. The sections before it are history; [AGENT_TOOL_CONTRACTS.md](../AGENT_TOOL_CONTRACTS.md), archived, owned the agents' schemas and validation. None of these grants a model a technical bypass. A role is assigned by the orchestrator and authenticated by server state, never read from an agent's claimed identity.

The owner installs the code that defines the operating envelope: its policy, protocol, definitions, model table, research envelope and sources. Within it, eligible routine paper trading runs unattended while the PC and services are available; research is off since [ExecPlan 0035](#execplan-0035-research-off). The app records each version it runs with its hash, as `SYSTEM` and never as the owner; installing an update is the owner's consent to what it ships, not a promise of profitability ([ExecPlan 0031](../plans/0031-m8-simple-app-that-runs-itself.md), [M8 below](#m8-the-app-runs-itself-execplan-0031)). Until the M8 update that replaces an owner approval is installed, that approval stays the app's gate. An agent's favorable performance never expands authority.

## Actors

- **ANALYST:** approved-source investigation and evidence-linked market assessments.
- **RESEARCHER:** hypotheses, declarative candidates, controlled experiments and research reports.
- **EVALUATOR:** independent-context critique, experiment inspection and evidence-quality assessment. Its verdict cannot waive hard checks.
- **COORDINATOR:** main-policy trade/position intents, bounded adaptation and promotion proposals.
- **SYSTEM:** deterministic scheduler, tool gateway, policy/risk controller, experiment runner, paper broker and accounting; from M8, also the in-force records, the short check and the run's start.
- **OWNER:** authenticated human who installs updates and holds the funding and control actions: the off switch, Stop, top-ups, an `OWNER` pause and a new run after a drawdown stop. The UI approvals of M5 to M7 go with M8's updates ([below](#m8-the-app-runs-itself-execplan-0031)).

These are logical roles, not six autonomous processes or six model subscriptions.

## Action matrix

| Action | Permitted model role | Automatic condition | Needs owner approval / prohibited boundary |
|---|---|---|---|
| Read scoped market/account/experiment state | All, least-data view by task | Active job capability and valid as-of scope | Cross-account/holdout/raw-secret access prohibited |
| Search approved evidence corpus; request a registered source refresh | ANALYST, RESEARCHER | Approved source/dataset scope, fetch budget and availability | New source, paid access or unrestricted URL fetch needs review; arbitrary network tool prohibited |
| Create evidence-linked assessment or hypothesis | ANALYST, RESEARCHER | Bounded schema, provenance, no financial effect | Cannot claim a model-written assertion is verified evidence |
| Submit declarative candidate and request backtest/shadow | RESEARCHER | Preapproved research envelope, registered operators/templates and resource budget | New operators/executable code or a larger domain arrive only in an update the owner installs; never writes main portfolio |
| Critique an assessment, candidate or trade intent | EVALUATOR | Authorized artifact IDs and immutable snapshot | Cannot grant approval or fabricate test results |
| Propose main buy/hold/reduce/exit | COORDINATOR | The AGENT_DRIVEN policy in force; current state, evidence, review and risk gates pass | No per-trade owner prompt; no direct broker/ledger credentials; reduce is not built in M7 (M7-OD7) |
| Cancel own unfilled discretionary entry | COORDINATOR | Pending order ownership and atomic reservation release | Cannot cancel another policy's obligation or remove protection |
| Tighten stop or exit early | COORDINATOR | Original position mandate explicitly permits the action | Loosening stops, lengthening maximum hold or changing ownership is forbidden |
| Select approved strategy or bounded parameter choice | COORDINATOR | Frozen adaptation rule and versioned domain; affected new entries only | A new main strategy or a wider range arrives only in an update the owner installs |
| Promote a research candidate to main eligibility | COORDINATOR may request | A proposal only; M6 requires EVIDENCE_READY and records PENDING | In M6 OWNER may reject or leave pending; M7 adds approval and main eligibility, as an entry basis inside the approved policy (built in B6, [M7 below](#m7-agent-driven-decisions-approved-contract-execplan-0026)); from M8's second update a candidate that passes the code's evidence checks becomes eligible by itself ([M8](#m8-the-app-runs-itself-execplan-0031)) |
| Pause new discretionary exposure | COORDINATOR may request; SYSTEM may enforce | Valid account-scoped pause, preserves protection | Cannot silently clear other pause causes; in M7 only OWNER resumes it; from M8's second update it carries an end of at most 24 h, ends by itself, and COORDINATOR or OWNER may lift it early ([M8](#m8-the-app-runs-itself-execplan-0031)) |
| Resume latched owner/risk/integrity pause | None | Never model automatic | OWNER review plus reconciled system readiness; from M8's second update SYSTEM clears `DAILY_LOSS` at the next UTC day and `INTEGRITY` when reconciliation passes, and `DRAWDOWN` still ends the run ([M8](#m8-the-app-runs-itself-execplan-0031)) |
| Clear transient readiness block | SYSTEM only | Recovery tests and unchanged policy; no latched cause remains | Does not clear loss, owner, permission-revocation or integrity latches |
| Top up, change risk limits, approve new tools/sources | None | Never model automatic | Top-ups are OWNER-only; risk limits, tools and sources change only in an update the owner installs; the tool set has no such mutation |
| Execute accepted paper order / post a fill | No model role | SYSTEM validates and commits in fenced transaction | Model cannot supply authoritative fills, prices or balance rows |
| Modify production code, install packages/plugins, access shell/credentials | None | Never runtime automatic | Prohibited runtime capability; reviewed development is a different environment |
| Real exchange order, withdrawal or API-key upload | None | Never in this release | Prohibited capability, not an owner toggle |

## Operating envelope

The immutable `OperatingPolicyVersion` binds policy kind, main account, universe, the prompt, tool, grant and schema definitions it is valid with, the rule for data/evidence sources, strategy family and bounded domains, triggers and horizons, position-management template, review policy, risk/cost versions, action/turnover/work budgets, invalidation/fallback behavior and reporting baseline. The owner sees what an update changes and installs it; the app records the version in force with its hash ([M8](#m8-the-app-runs-itself-execplan-0031); until M8's second update, the owner approves the hash). Text such as “do your best” is not a policy. *Settled for M7 by M7-OD11 (a), [ExecPlan 0026](../plans/0026-m7-agent-driven-main-decisions.md#33-decisions-for-the-owner):* the policy binds the hashes of the generation-3 definitions and requires "a runtime profile the owner has approved for exactly these definitions" and "items of source versions approved when they were fetched". The model and its settings are bound by that runtime profile, which the owner approves separately; each submission records the profile and the source versions in force, and a change of either starts an evaluation segment.

`ResearchEnvelopeVersion` separately authorizes datasets and time partitions, approved operators and templates, parameter search domains, modes, job/storage/CPU budgets and shadow accounting rules. A new candidate **inside this research envelope** may be tested automatically without being approved for the main account. Candidate results do not alter the envelope.

Routine early exits can be preauthorized and need no additional human approval. Protective actions never depend on an evaluator or model completing. New exposure fails closed when a required reviewer, source, policy or model is unavailable.

## Expiry, revocation and escalation

Check capability/approval status at every tool dispatch and again before committing an order. Tokens, role claims, cached approvals or an earlier validation result cannot authorize a revoked action. The owner can disable the agent workflow or stop the run at once. A policy, tool or source leaves through an update; until M8's second update the owner can also revoke a policy or a tool/source approval. Pending jobs are canceled or reclassified; uncommitted trade intents are invalidated; accepted discretionary entries are canceled where possible under broker state. Reconcile fills racing with revocation and retain existing protections.

If revocation removes something needed for an existing protection, keep the approved deterministic protection module and required market observations available while obligations exist, or pause new work and require an explicit safe migration. Never delete a rule while its positions still rely on it.

An agent may create a structured escalation with requested scope, reason, evidence, exact diff and impact. It cannot act while approval is pending, spoof a human response or substitute an evaluator's agreement. Group duplicate escalations to avoid approval fatigue. Declined proposals remain in audit history.

## Checkable meaning of hard boundaries

“No authorized path around a rule” is a design invariant tested in the app. It is not a claim of immunity to all bugs or a promise that losses cannot exceed a stop. Test cross-role impersonation, split orders, parallel reservations, stale approvals, cumulative turnover, indirect tool access and conflicting reviewer output. All permission failures must leave financial state unchanged except valid independent protective actions.

## Main-domain membership is not a new approval

An owner may approve a strategy/policy with an explicit bounded parameter domain and predeclared eligibility checks. Choosing a member of that same domain can be automatic; persist the membership proof, original owner grant and all required checks. This is use of existing authority, not a model-generated approval. Adding logic, widening a range, changing the risk/exit contract or introducing a new strategy family is not a member-selection operation and requires a new owner decision, delivered as an update the owner installs.

Isolated research eligibility never implies main-domain membership. Candidate records must identify whether main eligibility comes from an exact owner approval or a validated member of an already approved domain. A free-form claim of being “similar” is insufficient.

## M5 owner runtime controls (ExecPlan 0020)

*M8 replaces the profile approval, the probes and Enable below as its updates are installed ([M8](#m8-the-app-runs-itself-execplan-0031)); until then they apply as written.* The probe routes (`/v1/agent-runtime/probe`, `/decision-probe`, `/v1/agent-probes`) are removed in ExecPlan 0034 ([API contracts](API_CONTRACTS.md#cleanup-routes-nothing-calls-are-removed-execplan-0034)).

M5 changes no model authority in the action matrix above. Model roles get only the read and assessment tools of [catalog v1](../AGENT_TOOL_CONTRACTS.md#m5-tool-catalog-v1-execplan-0020). M5 adds these owner controls over the model runtime itself:

| Action | Who | Condition | Boundary |
|---|---|---|---|
| Approve, reject or revoke an exact runtime-profile hash | OWNER in the authenticated UI | Exact hash and the agent-approval version the owner reviewed; a separate `agent_approvals` store | Never writes `owner_approvals`; a model or chat text is never an approval; a profile with an unset field cannot be approved |
| Compose a draft profile (choose the model and reasoning effort from the discovered list) | OWNER | A discovery record exists; values must come from its list | A new DRAFT only; approval is separate |
| Start the capability probe suite | OWNER | `PROBE_ONLY`, an approved profile, the probe call budget | Probes are the only model calls allowed before `ENABLED` |
| Enable the runtime | OWNER | Approved profile hash plus a VERIFIED capability record for exactly that profile, binary, config and account | The worker re-checks both before applying; the implementer never enables |
| Disable the runtime | OWNER | Always | Immediate: increments the permission epoch; in-flight work becomes `CAPABILITY_REVOKED` or `late`; protection and every non-model function continue |
| Start an assessment workflow, or cancel one | OWNER | Registered template `MARKET_ASSESSMENT_V1` with bounded parameters and no free text; cancel cascades to the child | Queued work expires after 10 minutes; cancellation never erases completed records |
| Start the runtime in `LOGIN_REQUIRED`; log in to Codex | OWNER instruction (`tools/agent-activate.ps1 -Stage Probe`, removed by ExecPlan 0034); OWNER personally (`tools/agent-login.ps1`, device code) | M5-B only | The implementer never logs in; auth lives only in the runner's `codex_home` volume |

No model role can call any of these controls. Role prompts, artifacts, tool results and chat messages confer no permission.

## M6 research and source controls (approved contract, ExecPlan 0023)

*M8 replaces the envelope, source-version and promotion approvals below as its updates are installed ([M8](#m8-the-app-runs-itself-execplan-0031)); until then they apply as written.*

**B0 reconciled the contract; B5 and B6 implemented it (below).** Search and refresh remain ANALYST/RESEARCHER grants. EVALUATOR and COORDINATOR read cited evidence through scoped `read_artifact`; they gain no search grant. Only COORDINATOR can request promotion. `draft_trade_intent`, `submit_trade_intent`, `request_entry_pause` and model-chosen `request_review` stay refused in generations 1 and 2; generation 3 of M7 grants them to COORDINATOR only ([below](#m7-agent-driven-decisions-approved-contract-execplan-0026)).

OWNER approves or revokes the exact research-envelope and source-version hashes in `agent_approvals`, separate from the pilot's `owner_approvals`. Model roles cannot approve these or any promotion. Source refresh, job cancellation and shadow stop are bounded owner requests, preserving history. Activation, the new runtime-profile approval, probes and Enable are M6-B owner actions. Implementation approval in chat grants none of them.

The envelope binds the protocol, grammar, domains, budgets and resource limits of [ExecPlan 0023 §5.5](../plans/0023-m6-research-investigations.md#55-protocol-envelope-and-holdout). A changed value needs owner approval unless that section explicitly leaves it to a B0 measurement. Disabling/revoking cancels queued work; late results are history only.

B5 IMPLEMENTED the source side of these controls. A source version's hash binds its host, path, typed filters, answer limits, budget, symbol scope, trigger cooldown and rights record, so the owner's exact-hash approval covers them; the fetcher uses a version only while that approval is current ([DATA_CONTRACTS](DATA_CONTRACTS.md#m6-b5-source-and-evidence-records-execplan-0023)). No role, tool or source text can add a source, a destination or an approval. Both seeded versions remain `PROPOSED`.

B6 IMPLEMENTED the model-role side as role grants v2, a code-owned, hashed definition that the runtime profile binds ([AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md#m6-tool-catalog-v2-execplan-0023)). They follow this matrix:

| Role | Granted in generation 2 | Not granted |
|---|---|---|
| ANALYST | market reads, `read_artifact`, `search_evidence`, `request_source_refresh`, `read_experiment` (screening results at or before its cutoff), `record_assessment` | registering, experiments, proposals, promotion |
| RESEARCHER | the same reads, search and refresh; `register_candidate`, `request_experiment` (screening only), `record_research_proposal` | `record_assessment`, promotion, any holdout or shadow result, the full test |
| EVALUATOR | market reads, `read_artifact` (the artifacts and evidence items in its review's scope), `read_experiment`, `record_review` | search, refresh, registering, experiments, promotion |
| COORDINATOR | market reads, `read_artifact`, `read_experiment`, `request_promotion` | search, refresh, registering, experiments, reviews |

- A role comes from the stored workflow row and a grant from the stored definition. A role name, a prompt or text in a source or an artifact confers nothing; each of these is tested as an attempted escalation.
- SYSTEM actions are code, not a model role: queueing the full test of a nominated candidate (the research identity only), creating the fixed review child, recording a follow-on trigger, starting a promotion workflow for an `EVIDENCE_READY` candidate, and retiring a candidate whose shadow ended without the evidence minimum.
- Routine permitted actions need no per-action owner approval: a search, a refresh of an approved source, a registration and a screening inside the approved envelope and budgets.
- A promotion request is a `PENDING` proposal. No role, route, tool or statement approves one in M6, and `MAIN_APPROVED` stays unreachable.
- Definitions v2 change the runtime-profile hash. The new profile, the research envelope, each source version and Enable remain owner actions of M6-B; B6 approved none of them outside disposable fixtures.

B7 IMPLEMENTED the owner's side of these controls as private-API routes ([API_CONTRACTS](API_CONTRACTS.md#m6-owner-routes-execplan-0023-b7)). They add no authority to any model role and none to the browser beyond what this matrix already gives the owner:

| OWNER action | Effect | Who carries it out |
|---|---|---|
| Approve, reject or revoke the research envelope or a source version, by exact hash | The record in `agent_approvals`. A revocation raises the permission epoch in the same transaction | The API identity writes the record and the epoch; nothing else changes until the research and source identities see it |
| Reject a pending promotion, by exact hash | The promotion and its candidate become `REJECTED` | The API identity records the decision; the agent worker applies it as SYSTEM. No action but `REJECT` exists for a promotion |
| Request a refresh of an approved source | One request row with actor `OWNER` | The source fetcher, under its own budget and approval checks |
| Cancel a research job; stop a shadow | One immutable request on that row. Both are final ([DECISIONS](../../DECISIONS.md#2026-10-05--m6-b7-experiment-read-codes-canceled-jobs-and-rejected-promotions)) | The research identity |
| Start an investigation, a research workflow or a promotion workflow | One `QUEUED` workflow of a registered template with its bounded parameters | The agent worker, under the runtime state, the daily budget and the template's own start checks |

The API identity holds exactly the grants migration 0008 gave it for this: SELECT on the research, source and evidence relations, INSERT on refresh requests, and UPDATE of `version` and the one request column of a job and of a shadow. It cannot move a job, a shadow, a refresh request or a promotion to another state, write a fetch, an item, a result or a mark, or record a candidate transition; a test attempts each. Approving the envelope, a source version or a new runtime profile remains an owner action of M6-B: B7 approved none of them outside disposable fixture databases.

## M7 agent-driven decisions (approved contract, ExecPlan 0026)

*M8 replaces the approvals of the policy, the protocol and `PROMOTION_V2`, the decision probes and the owner-only resume of the entry pause below as its updates are installed ([M8](#m8-the-app-runs-itself-execplan-0031)); until then they apply as written.* The owner's workflow Start is removed in ExecPlan 0034; `POST /v1/agent-approvals` stays as the recovery lever ([API contracts](API_CONTRACTS.md#cleanup-routes-nothing-calls-are-removed-execplan-0034)).

**The agents' grants are IMPLEMENTED in B5 and B6 (2026-10-11 and 2026-10-12) and tested offline only; the owner's routes are IMPLEMENTED in B7 (2026-10-16, [API_CONTRACTS](API_CONTRACTS.md#m7-owner-routes-execplan-0026-b7)) and tested on isolated databases only; the pages are B8** ([plan §18](../plans/0026-m7-agent-driven-main-decisions.md#b5--generation-3-the-decision-loop-its-triggers-and-both-probe-suites-2026-10-11)). The owner approved [ExecPlan 0026](../plans/0026-m7-agent-driven-main-decisions.md) with every recommended decision on 2026-10-09 ([DECISIONS](../../DECISIONS.md#2026-10-09--execplan-0026-approved-for-implementation-with-the-recommended-decisions)). That approval grants none of the owner actions below.

Generation 3 adds these grants; generations 1 and 2 keep theirs unchanged:

| Role | Added in generation 3 | Not granted |
|---|---|---|
| COORDINATOR | `get_snapshot` view `PORTFOLIO` of the policy's own run; `draft_trade_intent` (`ENTER`, `EXIT`, `CANCEL_ENTRY`, `TIGHTEN_STOP`); `request_review` for its own draft; `submit_trade_intent`; `request_entry_pause`; `record_decision`; `request_promotion` in `PROMOTION_V2` (B6), a request whose scope the server writes | Approving anything; resuming a pause; raising a limit; a price, quantity, stop level, fee or balance; `REDUCE` (M7-OD7) |
| EVALUATOR | `record_review` of type `INTENT_REVIEW` (with the `PORTFOLIO` view of the draft's snapshot) and `OUTCOME_REVIEW` | Drafting, submitting, pausing; the portfolio in an outcome review |
| ANALYST, RESEARCHER | Nothing new; the market brief is an ANALYST workflow of the existing grants | `request_review` and every trading tool |

- **Routine actions need no per-action owner approval.** Under the approved policy and its `RUNNING` run, an entry with an `ACCEPTABLE` review of the exact draft, an exit, a cancellation of the run's own unfilled entry, a tightening permitted by the position's terms and an entry pause are carried out by code without a prompt to the owner.
- **Assessment and candidate reviews stay fixed children** the orchestrator creates; `request_review` creates only an intent review of the coordinator's own draft.
- **The agent's entry pause** blocks new discretionary entries of the policy's run and cancels its unfilled ones. It sits beside the experiment's latched causes and is not one of them; exits and protection continue. Only the owner's resume closes it.
- **Approving a promotion** (`PROMOTION_V2`, M7-OD4 a) makes the exact candidate an entry basis inside `AGENT_POLICY_V1`: the coordinator may name it in an `ENTER`, code checks the candidate's own entry signal (its entry condition holds and its exit signal does not), and the stop and hold stay inside the policy's sets. The candidate does not trade by itself and its exit rule (its stop, hold and exit signal) is not run for the position. A basis outside the policy's sets is refused.

OWNER actions added by M7, in the authenticated UI, with approvals bound to the exact hash; none is possible before the experiment boundary installs the policy:

| OWNER action | Store | Effect |
|---|---|---|
| Approve or revoke the operating policy and `EVALUATION_PROTOCOL_V2` | `owner_approvals`, as a `DEFINITION`, through the existing approvals route | A revocation reaches the engine in its next step as `APPROVAL_REVOKED`; the API then raises the permission epoch, retried, so agent work in flight ends too |
| Approve or revoke a `PROMOTION_V2` request | `agent_approvals` | Main eligibility as an entry basis; a revocation suspends the candidate and raises the epoch |
| Resume the agent's entry pause | `decision_pause_requests` | New discretionary entries may follow again |
| Start the decision probe suite | `agent_runtime_requests` (`DECISION_PROBE`), then `agent_probe_runs` (`suite` `DECISION`) | Five probes in `PROBE_ONLY` or `ENABLED`; a probe never writes a submission or a pause. Its passing result, for the approved profile and the policy together, is what lets the scheduler start decisions. B5 built the request (`app.agents.controls.decision_probe`) and its handling; B7 the route (both removed by ExecPlan 0034) |

Disable, revocation and the run's Pause stay the owner's immediate controls over an entry; a workflow cancel acts when the agent worker ends the workflow. No model role, prompt, artifact, review verdict or chat message can approve a policy, a protocol, a profile or a promotion, raise a limit, clear a latch or resume a pause.

**Promotion approval as built (B6, 2026-10-12; tested offline only, [plan §18](../plans/0026-m7-agent-driven-main-decisions.md#b6a--promotion-approval-and-the-candidate-basis-2026-10-12)).**
- *Who asks.* Once `AGENT_POLICY_V1` is installed, SYSTEM starts one `PROMOTION_V2` for each candidate that is `EVIDENCE_READY`, or `MAIN_APPROVAL_PENDING` on a pending `PROMOTION_V1` alone, whose exit values lie in the policy's sets; before the install it starts `PROMOTION_V1` as M6 does. The coordinator records the request or abstains. The server writes its scope (`ENTRY_BASIS_UNDER_AGENT_POLICY_V1`), the policy's ID and hash and the candidate's exit values; recording it withdraws the pending `PROMOTION_V1` of the same candidate, unless the owner has already rejected that request: the rejection is applied first and no entry-basis request follows. The owner's start of `PROMOTION_V2` gets its route, and the database's owner pair, in B7.
- *Who decides.* Only the owner, through the existing `/v1/agent-approvals` record (`asl_api`), by the request's exact hash. `APPROVE` needs a pending `PROMOTION_V2`, its candidate `MAIN_APPROVAL_PENDING`, the request's scope and policy, that policy installed, and the candidate's ATR period, stop multiple and hold in the policy's sets (`CANDIDATE_OUTSIDE_POLICY` otherwise). `REVOKE` needs that approval to be the latest record and the request still `PENDING` or `APPROVED` (an approval withdrawn unapplied granted nothing), and raises the permission epoch in the same transaction. A `PROMOTION_V1` can still only be rejected. Migration `0009`'s guards repeat every rule.
- *Who applies.* SYSTEM (the agent worker) moves the request to `APPROVED` and the candidate to `MAIN_APPROVED`, citing the approval row; the candidate guard admits `MAIN_APPROVED` only that way. A revocation moves the request to `REVOKED` and the candidate to `SUSPENDED`.
- *What it gives.* A decision is shown each approved candidate, with its computed signal at the decision bar, and may name it as the basis of an `ENTER` that takes the candidate's stop multiple and hold. The entry still needs its `ACCEPTABLE` intent review and passes every limit. The submission's guard binds the candidate's current approval and stored declaration, and the engine evaluates the candidate on the decision bar itself: the entry is taken only on `ENTRY_SIGNAL`, its entry condition holding and its exit signal not (`CANDIDATE_SIGNAL_ABSENT` otherwise). A position on a candidate keeps its terms after a revocation; no new entry may name the candidate. When research suspends an approved candidate (a shadow's integrity failure), no epoch rises: the worker withdraws, at its next pass, each entry on the candidate the engine has not answered or has accepted without a fill (`UNAPPROVED`), and the engine cancels it.

## M8: the app runs itself (ExecPlan 0031)

**Approved on 2026-10-19 ([DECISIONS](../../DECISIONS.md#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031)). Update 1's rows are implemented ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-the-agents-check-the-usage-limit-and-one-switch-execplan-0031)), update 2's ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-in-force-records-the-model-table-and-pauses-that-end-execplan-0031)) and update 3's ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-the-main-run-the-app-keeps-going-execplan-0031)), with the deviations below.** Each row takes effect when its update is installed ([ExecPlan 0031 §9](../plans/0031-m8-simple-app-that-runs-itself.md#9-implementation-sequence)); until then the M5 to M7 controls above apply as written.

| Action | Who | From | Replaces |
|---|---|---|---|
| Turn the agents on and off with one switch; no update turns them off | OWNER switches; SYSTEM keeps the setting across updates | Update 1 | Enable after a verified capability run, `PROBE_ONLY`, and enabling again after a change |
| Run the short check: one call per role on a fixed case after a change of model, prompt, definitions, runner or account. New entries wait for it; exits and stops never do. It reruns by itself with growing intervals and after a usage-limit block clears, and never latches | SYSTEM | Update 1 | The capability and decision probe suites as gates, the owner's Start of each, and `CAPABILITY_LATCHED`. The suites' routes were removed by ExecPlan 0034; the short check is the only check |
| Block model work while the provider refuses for the usage limit, and resume after the reset | SYSTEM | Update 1 | A refusal that failed the probes and latched |
| Compose the runtime profile from the model table in code, and record it in force | SYSTEM | Update 2 | The owner's compose form and exact-hash profile approval |
| Record the policy, the protocol, the research envelope and the source versions that the installed code ships as in force, with their hashes | SYSTEM | Update 2 | Exact-hash approvals in `owner_approvals` and `agent_approvals` |
| Make an `EVIDENCE_READY` candidate that passes the code's evidence checks eligible as an entry basis | SYSTEM | Update 2 | Approving `PROMOTION_V2` |
| End the agent's entry pause 24 h after it opened (planned: at the end it carries, from a closed set, with the coordinator's early lift; not built in M8) | SYSTEM; OWNER may resume it earlier | Update 2 | Resume by OWNER only |
| Clear `DAILY_LOSS` at the next UTC day, and `INTEGRITY` when reconciliation passes after a fix (never one a NAV check opened); `APPROVAL_REVOKED` goes with the approvals | SYSTEM | Update 2 | Resume by OWNER |
| Start the run of the main policy in force; when an update brings a newer version and the account holds no position, stop the run without flattening and start the next run | SYSTEM | Update 3 | The experiment draft, the manifest approval and the owner's Start of each run |

**Update 2 as built, until update 3.**
- The agent's entry pause ends 24 hours after it opened, by `SYSTEM`; the end the agent picks from a closed set, and the coordinator's early lift, were planned with `AGENT_POLICY_V2` and are not built in update 3 (below): generation 3's hashed "only the owner resumes entries" stays. The owner may still resume it earlier.
- The owner's approval routes stay as a recovery lever that no page offers: a definition, manifest, envelope, source version or promotion the owner rejects or revokes stays so, since `SYSTEM` never records over the owner's latest `REJECT` or `REVOKE`, and an owner's revocation still latches `APPROVAL_REVOKED` as before. The runtime profile is the app's alone (`PROFILE_RECORDED_BY_THE_APP`).
- A candidate still becomes an entry basis through the coordinator's `PROMOTION_V2` request, which `SYSTEM` approves by its exact hash in the owner's place when it passes the checks of the B6 rules above. A request outside the policy's sets stays pending: it reaches the main portfolio only through an update that widens the sets.
- The experiment manifest is still the owner's until update 3.
- An `INTEGRITY` latch a NAV check opened is not cleared by `SYSTEM` (independent review, 2026-10-19): a passing reconciliation proves only the newest valuation right, not the high-water NAV or daily reference a wrong one may have moved. It waits for a fix an update ships, as every integrity latch did before M8.

**Update 3 as built.**
- The app keeps the main run going: it drafts, records in force and starts a run of the main policy in force, and stops a run whose policy a newer version replaced once the account holds no position, never with a flatten and never while the owner's pause, the owner's revocation, a drawdown latch or an integrity latch is open. It starts the next run only after a run it ended itself; after the owner's Stop or discard, any request the owner sent while the app's stop waited, the owner's rejection or revocation of that run's manifest, or a `DRAWDOWN` stop, nothing starts until the owner creates a run. The owner's manifest decision and Start stay for a run of the reference.
- Update 2's first two points stand: the entry pause ends after a fixed 24 hours, and the coordinator's early lift is not built, because both need generation-3 tool texts changed; M8 ships no new agent definitions. Promotions keep their V1 scope, so under `AGENT_POLICY_V2` a candidate is not an entry basis.

The owner keeps installing each update (its double-click), the agents' switch (the permission epoch), Stop, top-ups, resuming an `OWNER` pause, and a new run after a `DRAWDOWN` stop, which still ends the run. The Codex sign-in stays the owner's own. Model roles gain nothing in M8 (the early lift of their own entry pause is not built). No model role, prompt, artifact, review verdict or chat message can change the code, the model table, a limit, the policy or a source, turn the switch, or clear a latch the code does not clear. A `SYSTEM` record never names the owner.

## M9: news and price moves start investigations (ExecPlan 0032)

**Update 2 as built (2026-10-20), [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m9-runtime-news-and-price-moves-start-investigations-execplan-0032).** No permission changes. M8's table above stands as it is.

| Action | Who | From |
|---|---|---|
| Record a `PRICE_MOVE` trigger when the application measures that a mid moved at least one hourly ATR within 15 minutes (at most four a symbol a UTC day, an hour apart) | SYSTEM | Update 2 |
| Start generation 4's investigation of a new feed item (`SOURCE_TRIGGER`) or a price move (`SYSTEM`), one open per source and symbol or per symbol, within its own count of 16 a UTC day, which the owner's own investigations (M6's route) share | SYSTEM | Update 2 |
| Start a decision under the main policy in force when an investigation's review is `ACCEPTABLE` (`REVIEWED_ASSESSMENT` in `AGENT_POLICY_V2`) | SYSTEM | Update 2 |

The analyst and the evaluator gain no tool with an effect: generation 4's grants are a subset of generation 3's, and the coordinator's decision tools, limits and checks are generation 3's and `AGENT_POLICY_V2`'s unchanged. No `AGENT_POLICY_V3` was built and the main run does not move. A feed item, a price move or an assessment is data; none raises a limit, adds a symbol, turns the switch or clears a latch.


## M10: the coin watchlist and the notes (ExecPlan 0033)

**Update 1 as built (2026-10-20), [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m10-runtime-the-coin-notes-execplan-0033).** No permission changes for trading: BTC and SOL stay the only coins traded until update 2 is installed with the owner's yes of 2026-10-20 ([DECISIONS](../../DECISIONS.md#2026-10-20--m10-approved-research-and-trade)).

| Action | Who | From |
|---|---|---|
| Scan Binance's public spot listing once a UTC day and record the watchlist of 8 and what was left out, by the code-owned rules `COIN_SCAN_V1` | SYSTEM (the source fetcher) | Update 1 |
| Start one analyst note at a time on a watchlist coin, at most 3 a UTC day, each reviewed by the evaluator | SYSTEM | Update 1 |

The analyst and the evaluator gain no tool with an effect: generation 5 only reads and records the role's own note or review. A scan, a rank, a figure, a label or a note is data; none adds a coin to trading, raises a limit, starts a decision, turns the switch or clears a latch.

**Update 2 as built (2026-10-21), [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m10-runtime-generation-6-and-five-coins-execplan-0033).** Installed with the owner's "Research and trade" of 2026-10-20 and "go" of 2026-10-21 ([DECISIONS](../../DECISIONS.md#2026-10-21--m10-update-2-zec-near-and-xrp-traded-on-paper-execplan-0033)). ZEC, NEAR and XRP are traded on paper under `AGENT_POLICY_V3`, inside V2's limits for all five coins together.

| Action | Who | From |
|---|---|---|
| Record `AGENT_POLICY_V3` and generation 6 in force, and move the main run from V2 to V3 once the account holds no position, open order or exit obligation | SYSTEM (the agent and execution workers) | Update 2 |
| Brief, decide, draft, have reviewed and submit entries and exits in BTC, SOL, ZEC, NEAR and XRP under V3 | The roles of generation 6, as generation 3's under V2 | Update 2 |

Generation 6's grants and effects are a subset of generation 3's (no research or promotion tool). A coin note stays data: it is shown to the coordinator, cited if it wants, and never an entry basis. No agent can add a coin, change the list or the limits, or move a run; the code names the coins, and only an update the owner installs changes them.

## ExecPlan 0035: research off

IMPLEMENTED on 2026-10-21 ([ExecPlan 0035 §4.2](../plans/0035-a-simpler-app-that-trades-by-itself.md#42-research-off-in-the-agent-worker); [DECISIONS](../../DECISIONS.md#2026-10-21--the-owner-asks-for-fewer-pages-and-no-research-execplan-0035)). The definitions in force still name the research templates and the RESEARCHER's grants, and no generation changes; the code that starts work only narrows what they permit:

| Action | Before | Since ExecPlan 0035 |
|---|---|---|
| Queue `SCHEDULED_RESEARCH` for a newly sealed dataset; record `FOLLOW_ON` when a reviewed assessment names a research question | SYSTEM | Nobody. A reviewed assessment still records `ASSESSMENT_READY`, which trading uses |
| Start `RESEARCH_V1`, its `CANDIDATE_REVIEW_V1`, or a promotion workflow (`PROMOTION_V1`, `PROMOTION_V2`) | SYSTEM, from a trigger or an `EVIDENCE_READY` candidate | Nobody. A research trigger still queued is settled `CANCELED` with reason `RESEARCH_OFF`; a research workflow left open ends canceled with the same reason, once the worker holds the lease |
| Record a pending promotion in force | SYSTEM | Nobody. The owner's own approval or revocation of a promotion is still applied: it stays the owner's recovery lever |
| Run research jobs and shadows; hold `asl_research` on the main database | The research runner and bridge | Nobody: the update retires their containers ([DOCKER](DOCKER.md#research-services-retired-execplan-0035)). The role stays, with no container holding its password |

The research envelope stays recorded in force: the evaluation protocol's segment key reads it. No role gains anything, and no owner control changes.


## M11: the futures trader and the owner's run controls (ExecPlan 0039)

IMPLEMENTED in update 2, part B ([ExecPlan 0039 §5.3.1](../plans/0039-bitcoin-futures-on-paper.md#531-part-bs-design-2026-10-24); [DECISIONS](../../DECISIONS.md#2026-10-23--m11-approved-bitcoin-futures-on-paper-execplan-0039)); NOT RUN on the owner's PC until the update is installed. One agent, the trader, replaces the nine; the engine's checks and protection bind every action.

| Action | Who | Bound by |
|---|---|---|
| Decide to enter long or short, exit, tighten the stop, hold or abstain on the simulated BTCUSDT perpetual | The trader (`FUTURES_DECISION_V1`, COORDINATOR), started only by `SYSTEM` triggers | `FUTURES_POLICY_V1`'s finite sets; the finish's checks; the engine's answer |
| Size, price, fill, charge fees and funding, compute margin, stop, take-profit and liquidation | `SYSTEM` (the futures engine) | `FUTURES_POLICY_V1`, `FUTURES_COST_V1`, the fenced step |
| Close a position at its stop, take-profit, time exit or liquidation | `SYSTEM`, every second, whatever the agents, the run state or a pause | Fresh data only (rule 11) |
| Tighten a stop | The trader proposes; `SYSTEM` applies it only if tighter | The database refuses a looser stop |
| Start the first run, once the account is funded | `SYSTEM` | Nothing else starts a run by itself |
| Contribute the initial 10,000 virtual USDT, once, when the API starts on an account nothing has funded (ExecPlan 0042) | `SYSTEM` (the API) | The posting of the owner's confirmation; never while the reconciliation has failed or the account is paused; it cannot be canceled |
| Switch the agents on from their first state, while the owner has made no switch request (ExecPlan 0042) | `SYSTEM` (the agent worker) | The agents' check alone enables them; the owner's Turn off (offered once the app has the profile in force) is final until the owner's Turn on |
| Pause and Resume (cause `OWNER`) | The owner only | `SYSTEM` never clears `OWNER` |
| Stop, with or without closing the position at once | The owner only | A stopping run makes no entry; the position keeps its protection |
| Start trading after a Stop or a drawdown stop | The owner only ("Start trading") | A new run, with its own high-water NAV |
| Open and clear `DAILY_LOSS` (next UTC day), open and clear `INTEGRITY` (reconciliation passes), open `DRAWDOWN` (stops the run once flat) | `SYSTEM` | As M8's rules ([RISK_POLICY](RISK_POLICY.md#m11-futures_policy_v1-execplan-0039)) |
| Change leverage limits, risk, sets, limits or costs | Nobody at run time: a new policy version in an update the owner installs | The stored definitions must equal the code |

The model cannot name a price, a quantity, a leverage outside `1` or `2`, a run, a position or a policy; the server writes the binding, and the engine refuses a decision whose policy, position or account changed. Funding the account, the owner's passphrase, the off switch, an `OWNER` pause and a new run after a stop stay the owner's (rule 14).

**Since [ExecPlan 0042](../plans/0042-no-owner-sign-in.md)** (the owner's decision of 2026-10-25) there is no sign-in or passphrase, and the initial funding and the agents' first switch-on are `SYSTEM`'s, as the two rows above say. Top-ups, the off switch, an `OWNER` pause, Stop and a new run after a stop stay the owner's, in Settings without a sign-in. A model role gains nothing: no tool reaches the funding, the switch or a run request.

## ExecPlan 0040: the trade reviewer and the coach

IMPLEMENTED in part 1 ([ExecPlan 0040 §5](../plans/0040-trade-reviews-and-a-coach.md#5-authority)); NOT RUN on the owner's PC until the update is installed. No permission is added: the action matrix's rows "Critique an assessment, candidate or trade intent" (EVALUATOR; here a closed trade's record) and "Create evidence-linked assessment or hypothesis" (ANALYST) cover the two new agents, with no financial effect, and the trader's authority is unchanged.

| Action | Who | Bound by |
|---|---|---|
| Build each closed trade's fact sheet | `SYSTEM` (the agent worker's scheduler, in code) | Stored rows only; one per position; never changed after |
| Review one closed trade: grade the decision, name factors with their evidence, tag it, write a lesson | The reviewer (`TRADE_REVIEW_V1`, EVALUATOR), started only by `SYSTEM`, one at a time, after the trader | Its own fact sheet; the tag list; no tool; code places the grid |
| Write an advice note for the trader | The coach (`TRADE_COACH_V1`, ANALYST), started only by `SYSTEM` after a new review | The reviews and scoreboard it was shown; the policy's sets; no tool; code adds the counts, holds the confidence low and ends the note after four hours |
| Read the note and say how it used it | The trader (`FUTURES_DECISION_V2`, COORDINATOR) | `NO_ADVICE` exactly when none was shown; the engine never reads either |
| Turn a lesson or a note into a rule, a limit, a size or an order | Nobody: a rule changes only in an update the owner installs ([AGENTS.md](../../../AGENTS.md) rule 4) | No code path reads a review or a note into the engine |

Neither new agent can draft, submit, pause, stop, start a workflow, change a policy or hold the trader back: the slot goes to the trader first, and a decision queued while either runs cancels its call. The three agents run on one model ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md#model-roles)), so the reviewer is not independent; the scoreboard, computed by code, is the check.

## ExecPlan 0041 part 1: the twins

IMPLEMENTED in part 1 ([ExecPlan 0041 §5](../plans/0041-twins-and-a-veto.md#5-authority)); NOT RUN on the owner's PC until the update is installed. The twins are `SYSTEM`'s, by `TWIN_SET_V1`, and no agent has a role in part 1.

| Action | Who | Bound by |
|---|---|---|
| Start the twin set (three twins, segment 1) | `SYSTEM` (the futures worker's twin step, in code), once, recording the set's hash | The stored `TWIN_SET_V1` equal to the code; the engine's lease |
| Enter, exit, protect, pay funding and value each twin's isolated account | `SYSTEM` (the twin step, each second after the owner's step) | The set's rules; `FUTURES_POLICY_V1`'s sizing, cooldowns, entries and latches (no latch for the hold twin); `FUTURES_COST_V1`'s fills, fees, funding and liquidation on fresh quotes and marks |
| Latch, stop or fault a twin | `SYSTEM` (the twin step) | That twin alone; an ended segment never changes |
| Change a twin's rule or values, or start a new set | Nobody at run time: a new set is an update the owner installs | `TWIN_SET_V1` frozen in migration `0023` |
| Read the league table and turn it into a rule, a limit or a promotion | Nobody: the table changes nothing ([AGENTS.md](../../../AGENTS.md) rule 4) | No code path reads the league or a twin into the trader, the policy or the owner's account |

No twin code writes the owner's journal, reservations, `account_state`, runs, positions, fills, funding or valuations ([LEDGER](LEDGER.md#execplan-0041-the-twins-books-are-not-the-ledger)). The owner keeps everything rule 14 lists; a twin needs nothing from the owner.


## ExecPlan 0041 part 2: the veto twin, the momentum twin and the placebo

IMPLEMENTED in part 2 ([ExecPlan 0041 §5](../plans/0041-twins-and-a-veto.md#5-authority)); NOT RUN on the owner's PC until the update is installed. The twins stay `SYSTEM`'s, now by `TWIN_SET_V2`; one agent gets a role, and no permission is added: the action matrix's row "Critique an assessment, candidate or trade intent" (EVALUATOR; here one twin's held entry) covers the entry veto, with no financial effect on the owner's account.

| Action | Who | Bound by |
|---|---|---|
| Start `TWIN_SET_V2`'s new twins (`TREND_VETO`, `MOMENTUM_1W`, segment 1) and carry part 1's three in their segments | `SYSTEM` (the twin step, in code), once, recording the set's hash | The stored `TWIN_SET_V2` equal to the code; the engine's lease |
| Hold the veto twin's entry and ask about it (one request, its hash and a 120 s deadline) | `SYSTEM` (the twin step) | The rule's entry checked and sized first; one open request; one per bar |
| Start the entry veto for an open request | `SYSTEM` (the agent worker's scheduler, in code) | Once per request, at least 30 s before its deadline, while no trader decision is queued or open, at most 24 a UTC day; a decision queued meanwhile cancels it; exempt from the quiet window |
| Answer `GO`, `HALVE` or `VETO` with a reason from `VETO_REASONS_V1`, a note and a confidence | The entry veto (`ENTRY_VETO_V1`, EVALUATOR), started only by `SYSTEM` | The bound request's ID and hash; no tool; one answer row, written from its own running workflow; `NONE` exactly with `GO` |
| Apply the answer: skip, or check, size (half the risk fraction for `HALVE`) and fill; no answer by the deadline enters as the rule says (`NO_ANSWER`) | `SYSTEM` (the twin step) | Only an answer recorded by the deadline; a fresh quote and the policy's decision age; the veto twin's own account |
| Read the momentum twin's day and enter, flip or hold | `SYSTEM` (the twin step) | `TWIN_SET_V2`'s momentum rule; the whole wallet at 1x, no stop, no time exit, no latch |
| Replay the veto twin's candidates and compare the veto with the plain rule and with random answers | `SYSTEM` (the agent worker's scheduler, in code, as the agent identity), once a UTC day from 00:40 | Only while no trader decision is queued or open; seeded; written once a day, never changed |
| Start, size, exit or protect any entry, touch the owner's account, the trader, a run, a limit or a policy, or change a twin's rule | Not the entry veto, and nobody at run time: a new set is an update the owner installs | `TWIN_SET_V2` and generation 12 frozen in migration `0030`; the agent identity writes only its answer rows and the placebo's results |
| Turn the league table, the vetoes or the placebo into a rule, a limit or a promotion | Nobody ([AGENTS.md](../../../AGENTS.md) rule 4) | No code path reads them into the trader, the policy or the owner's account |

## ExecPlan 0043 update 1: the decision scores

IMPLEMENTED in update 1 ([ExecPlan 0043 §5](../plans/0043-score-every-decision.md#5-authority)); NOT RUN on the owner's PC until the update is installed. No agent reads or writes a score in update 1; update 2 shows them to the trader and a daily reviewer.

| Action | Who | Bound by |
|---|---|---|
| Score a decision, a finished bar or a twin entry at each checkpoint | `SYSTEM` (the agent worker's scheduler pass, in code, as the agent identity), oldest due first, at most 20 subjects a pass | The stored definition in force (`DECISION_SCORING_V2` since migration `0034`) equal to the code; migration `0024`'s guard (only after the checkpoint, from stored candles and rates; never changed) |
| Store a checkpoint that cannot be scored as `INCOMPLETE` | `SYSTEM` (the same pass), once it is seven days old | Never filled in or estimated ([AGENTS.md](../../../AGENTS.md) rule 11) |
| Change a label, a checkpoint or the test trades | Nobody at run time: a new definition is an update the owner installs | `DECISION_SCORING_V1` frozen in migration `0024`, `DECISION_SCORING_V2` in `0034` |
| Turn a score or the scorecard into a rule, a limit or an order | Nobody ([AGENTS.md](../../../AGENTS.md) rule 4) | No code path reads a score into the risk gate, the policy, the twins or the owner's account |

The agent identity's insert on `futures_decision_scores` is the scheduler's code path, not a tool: no template, tool or model output writes one.

## ExecPlan 0043 update 2: the agents read the scores

IMPLEMENTED in update 2 ([ExecPlan 0043 §5](../plans/0043-score-every-decision.md#5-authority)); NOT RUN on the owner's PC until the update is installed. No permission is added: the action matrix's row "Critique an assessment, candidate or trade intent" (EVALUATOR; here a day's scored decisions) covers the decision reviewer, with no financial effect, and the trader's and the coach's authority is unchanged.

| Action | Who | Bound by |
|---|---|---|
| Choose a day's cases (the three largest misses and the three worst decisions) and size them | `SYSTEM` (the agent worker's scheduler, in code) | The 1-hour scores recorded by the review's start; `DECISION_REVIEW_V1`'s rules frozen in migration `0025` |
| Review one UTC day: say whether each case was knowable then, tag it, cite paths into it, write one lesson | The decision reviewer (`DECISION_REVIEW_V1`, EVALUATOR), started only by `SYSTEM`, once a day from 01:30 UTC, one at a time, after the trader | Its own day's cases and their hash; the tag list; no tool; code adds each case's facts and the counts; one review a day |
| Say which way the next hour goes at each decision | The trader (`FUTURES_DECISION_V3`, COORDINATOR) | `UP`, `DOWN` or `NO_VIEW`; scored by code at the hour; no code that trades reads it |
| Read its scored decisions and the scorecard | The trader | Only rows recorded by its cutoff, labeled hindsight; never an order, a limit or a check |
| Cite a decision review or a scorecard row in a note | The coach (`TRADE_COACH_V2`, ANALYST) | What it was shown; code writes each cited record's counts, and a scorecard row's hash and holds the confidence low below both samples |
| Turn a forecast, a score, a lesson or a note into a rule, a limit, a size or an order | Nobody: a rule changes only in an update the owner installs ([AGENTS.md](../../../AGENTS.md) rule 4) | No code path reads them into the engine, the risk gate, the policy, the twins or the owner's account |

The decision reviewer, like generation 8's two, cannot draft, submit, pause, stop, start a workflow, change a policy or hold the trader back: the slot goes to the trader first, and a decision queued while it runs cancels its call. All four agents run on one model ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md#model-roles)), so the reviewer is not independent; the scores, computed by code, are the check.

## ExecPlan 0044: a trader that commits

IMPLEMENTED ([ExecPlan 0044 §5](../plans/0044-a-trader-that-commits.md#5-authority)); NOT RUN on the owner's PC until the update is installed. No permission is added: the trader's authority narrows, since code also refuses entries against its own forecast, at `LOW` confidence, or with a stop under 2 ATR or a time exit under 4 hours, and the coach's note stays advice.

| Action | Who | Bound by |
|---|---|---|
| Say `UP` or `DOWN` at each decision, and its confidence | The trader (`FUTURES_DECISION_V4`, COORDINATOR) | `NO_VIEW` only with `ABSTAIN`; scored by code at the hour; no code that trades reads the forecast or the confidence |
| Propose an entry | The trader | `FUTURES_POLICY_V1` as before, and only the way of its call, at `MEDIUM` or `HIGH`, with a stop of 2 or 3 ATR and a time exit of 4, 12 or 24 hours; the engine sizes, checks and fills it as before |
| Lean `SIT_OUT` in a note | The coach (`TRADE_COACH_V3`, ANALYST) | Only once ten trades are reviewed |
| Make the trader enter | Nobody: a flat `HOLD` is always accepted | The checks only refuse |

## ExecPlan 0046: leaner agents

IMPLEMENTED ([ExecPlan 0046 §5](../plans/0046-leaner-agents.md#5-authority)); NOT RUN on the owner's PC until the update is installed. No permission, tool, limit or grant changes. Generation 11's trader, `FUTURES_DECISION_V5` (COORDINATOR), holds generation 10's trader's rows above as they are: the same two reads and finish, the same four finish checks, and the database's guard holds its rows to generation 10's rules. The runner's own base instructions, which replace Codex's for every role, are model guidance like the role prompts and confer nothing; the runner's isolation is unchanged.

## ExecPlan 0050: the replay of past decisions

IMPLEMENTED ([ExecPlan 0050 §5](../plans/0050-replay-past-decisions-offline.md#5-authority)); NOT RUN on the owner's PC until the update is installed. No permission is added: the replay agent holds the trader's two reads and its finish tool for three templates of its own, and its finish writes only a replay record. The trader, its generation, `FUTURES_POLICY_V1` and code's protection are unchanged.

| Action | Who | Bound by |
|---|---|---|
| Queue the next unanswered item of `REPLAY_SET_V1` | `SYSTEM` (the agent worker's scheduler, in code) | One at a time; Codex only, with the trader's model and effort of the original call; the reviewers' gate and nobody ahead; 2 a bar, 192 a UTC day; a fresh Codex reading with every window under half used; 3 counted starts an item |
| Answer one stored context again, at the original cutoff | The replay agent (`DECISION_REPLAY_*_V1`, COORDINATOR), started only by `SYSTEM` | The trader's two reads at the original cutoff; the trader's finish rules; one `DECISION_REPLAY` artifact and one `futures_decision_replays` row, written from its own running workflow of that arm for that decision |
| Record a decision the engine answers, an order or a fill, start a workflow, or touch the owner's account, a run, a limit, a policy or a twin | Not the replay agent | The decision guard accepts only the trader's templates; the replay rows are append-only and read only by the replay and its report |
| Turn the report's verdict into a rule, a prompt or a generation | Nobody at run time ([AGENTS.md](../../../AGENTS.md) rule 4) | A variant that passes is evidence for the next trader generation's own plan, which the owner installs or not |

## ExecPlan 0052: the AI backtest

IMPLEMENTED ([ExecPlan 0052 §5](../plans/0052-backtest-the-ai-trader-on-history.md#5-authority)); NOT RUN on the owner's PC until the update is installed. No permission is added: the backtest's templates hold their live roles' reads and finish tools for four templates of their own, the probe a finish tool of its own, and every finish writes only a backtest record. The trader, its generation, `FUTURES_POLICY_V1`, the twins and code's protection are unchanged.

| Action | Who | Bound by |
|---|---|---|
| Run the simulated accounts on the shipped archive | The agent worker's child process (`python -m app.backtest_ai.process`), code only | No database, network, model client or key; the archive checked against `BACKTEST_ARCHIVE_V1` and Binance's checksums before the first step; a model's answer reaches it only once recorded |
| Write a step the child printed; end the run (`FINISHED`, or `STOPPED` with its code) | `SYSTEM` (the agent worker, in code) | The run's one row; steps in order with no gap and none while the last waits; append-only |
| Queue the next step without an answer | `SYSTEM` (the agent worker's scheduler, in code) | One at a time, the probes first; Codex only; each role's pinned pair; the reviewers' gate and nobody ahead; turns with the replay; 2 a bar, 192 a UTC day, 2,200 started in all; a fresh Codex reading with every window under half used; 3 counted starts a step |
| Answer one stored step | The backtest agents (`BACKTEST_*_V1`), started only by `SYSTEM` | The step's stored context and reads; the trader's or the veto's finish rules; one `BACKTEST_ANSWER` artifact and one `backtest_answers` row, from its own running workflow of that step, once |
| Record a decision the engine answers, an order or a fill, start a workflow, or touch the owner's account, a run, a limit, a policy or a live twin | Not the backtest agents | The decision guard accepts only the trader's templates; the backtest rows are append-only and read only by the child process and the report |
| Turn the report's verdict into a rule, a prompt or a generation | Nobody at run time ([AGENTS.md](../../../AGENTS.md) rule 4) | A `PASS` is evidence for a later plan, which the owner installs or not |

**Generation 16** ([ExecPlan 0052 §15](../plans/0052-backtest-the-ai-trader-on-history.md#15-generation-16-the-backtest-up-to-80-of-the-week-2026-11-04), the owner's pick of 2026-11-04 09:35:17 UTC): the same rows for the templates `BACKTEST_*_V2`, which continue the same run, with one bound changed: a backtest call starts while the weekly Codex window is under 80% used and every other window under half (the replay keeps half). No permission is added; the counts in the rows above cover both generations' workflows.

**Generation 17** ([ExecPlan 0055 §5](../plans/0055-backtest-claude-on-the-same-history.md#5-authority), the owner's pick of 2026-11-05 12:04:27 UTC): the same rows for the templates `BACKTEST_CLAUDE_*_V1`, which answer a second run of their own (`BACKTEST_AI_V1:TWO_MONTHS_CLAUDE`) with its own steps, answers and child process. Their calls go to the Claude API with `claude-sonnet-5-5` at `medium`, named by the templates in code, never by a model or the profile; the key stays the runner's, and no agent reads it, chooses another provider or spends outside this run. The bounds that differ: one Claude workflow at a time and none while another backtest or a replay is open; only while the agents run on Codex and the runner reports the key usable; no count a bar or a day and no Codex allowance rule; the run's counted spend at most $119 to start (it ends `STOPPED` with `SPEND_CAP_REACHED` above that, under the $120 cap) and 3,000 workflows in all; a provider failure is not a start and makes it wait. While the Claude lane can ask a step, the ChatGPT backtest and the replay wait. A Claude call's credit or limit refusal never sets the live agents' usage-limit block, and its success never lifts one. No permission is added; a paid call runs only on the owner's pick, for this run, and paid fallback stays disabled.

**Generation 18** ([ExecPlan 0056 §5](../plans/0056-backtest-the-traders-latest-design.md#5-authority), the owner's pick of 2026-11-07 15:42:46 UTC): the same rows for the templates `BACKTEST_GEN14_*_V1`, which answer a third run of their own (`BACKTEST_GEN14_V1:TWO_MONTHS_CLAUDE`): the live design's trader, trade reviewer, decision reviewer and coach on masked history, each holding only its live template's tools and checks. A finish is one backtest answer, never a decision, a review, a note, a fill or anything a live context, the scoreboard or a page's live view reads. Their call is generation 17's (the Claude API, `claude-sonnet-5-5` at `medium`, named in code); the bounds that differ from generation 17's: a start only once 0055's run has ended, only while the installed code's fingerprint of the live design equals the frozen `LIVE_DESIGN_GEN14_V1`, the run's counted spend at most $39 to start (it ends `STOPPED` with `SPEND_CAP_REACHED` above that, under the $40 cap) and 2,000 workflows in all. While it can ask a step, the ChatGPT backtest and the replay wait. No permission is added; a paid call runs only on the owner's pick, for this run, and paid fallback stays disabled.

## ExecPlan 0049: the agents' provider

IMPLEMENTED ([ExecPlan 0049 §6](../plans/0049-choose-the-agents-provider-and-see-usage.md#6-authority-and-the-rules-that-change)); NOT RUN on the owner's PC until the update is installed. No agent tool, grant, limit or template changes, and the agents' prompts are the same whatever the provider.

| Action | Who | Condition | Boundary |
|---|---|---|---|
| Pick the provider the agents run on | OWNER in Settings → Provider, after a confirmation | The provider is ready (signed in or its key saved; an API with a daily cap not yet reached); versioned and idempotent | No agent has a tool for it and a model's text cannot reach it; nothing moves the agents to another provider by itself |
| Put the picked provider in force | SYSTEM | Its profile passed the agents' check, or passed one before (`VERIFIED_BEFORE`) | A failed, impossible or 20-minute-old pick is refused with its reason and the agents stay on the provider in force |
| Save, replace or remove a provider's key or token | OWNER in Settings → Provider | The runner alone stores it; the key of the provider in use cannot be removed | Never stored by the engine or shown back; threads never read or enter one |
| Set an API's daily cap | OWNER in Settings → Provider | US dollars, above 0 and at most 1,000, two decimals | Needed before an API can be picked |
| Stop new model calls when the day's cost reaches the cap | SYSTEM (`SPEND_CAPPED`, cleared at 00:00 UTC or when the owner raises the cap) | The calculated cost of the day's calls | Like the usage limit: entries wait, exits and code's protection do not |

## ExecPlan 0053: the trader every four hours and on events

IMPLEMENTED ([ExecPlan 0053 §5](../plans/0053-the-trader-every-four-hours-and-on-events.md#5-authority)); NOT RUN on the owner's PC until the update is installed. No permission, tool, limit or grant changes. Generation 14's trader, `FUTURES_DECISION_V6` (COORDINATOR), holds generation 11's trader's rows above as they are: the same two reads and finish, the same finish checks, and the database's guard holds its rows to generation 10's rules. When it is started is code's (`SCHEDULE_V1`, hashed in its template), from stored records only; no model, prompt or page chooses it. The schedule's 32 decisions a UTC day are one more limit, below the policy's 120, which stays.

## ExecPlan 0057: the slow trend twin

IMPLEMENTED ([ExecPlan 0057 §5](../plans/0057-a-slow-trend-twin.md#5-authority)); NOT RUN on the owner's PC until the update is installed. No permission, tool, agent or grant of an agent changes; the twins stay `SYSTEM`'s, now by `TWIN_SET_V3`.

| Action | Who | Bound by |
|---|---|---|
| Start `TWIN_SET_V3`'s new twin (`TREND_SLOW`, segment 1) and carry `TWIN_SET_V2`'s five in their segments | `SYSTEM` (the twin step, in code), once, recording the set's hash | The stored `TWIN_SET_V3` equal to the code; the engine's lease |
| Read the slow trend twin's day and enter, resize (the whole position out, the target in, in one step), flip, exit to flat or hold | `SYSTEM` (the twin step) | `TWIN_SET_V3`'s slow trend rule on the stored daily candles; at most 2x; no stop, no time exit, no latch; an exit that cannot fill is tried whole again at the day's next bar; the twin's own account |
| Store the perpetual's daily candles | `SYSTEM` (the feed, as the market worker) | Final days only (a minute after their close), from the provider's public REST answer; never changed; their notes are left out of the agents' view of the feed's notes |
| Change the rule, its values or the measure, or act on the measure's verdict | Nobody at run time: a new set is an update the owner installs | `TWIN_SET_V3` frozen in migration `0038`; no code path reads the twin or its verdict into the trader, the policy or the owner's account |

## ExecPlan 0058: the event calendar

IMPLEMENTED ([ExecPlan 0058 §5](../plans/0058-the-event-calendar.md#5-authority)); NOT RUN on the owner's PC until the update is installed. No permission, tool, limit or grant changes. Generation 19's trader, `FUTURES_DECISION_V7` (COORDINATOR), holds generation 14's trader's rows above as they are: the same two reads and finish, the same finish checks and one more that only refuses an entry inside a release's window, and the database's guard holds its rows to generation 10's rules. The calendar (`EVENT_CALENDAR_V1`: the BLS calendar's CPI and jobs report as stored, the Fed's statements from a table in code), the window (`EVENT_WINDOW_V1`) and the look after a release (`SCHEDULE_V2`) are code's, hashed in its template; no model, prompt or page changes them or when the trader is called.

| Action | Who | Bound by |
|---|---|---|
| Refuse a generation-19 entry while a window is open, or while the calendar cannot be read | Code (the finish rule, against the bound context and again at the finish) | `EVENT_WINDOW_V1`: from 240 minutes before a first-rank release to 45 (CPI), 30 (jobs) or 120 (Fed) minutes after; entries only |
| Exit, tighten the stop, hold or abstain inside a window | The trader, as before | Generation 14's rules; the engine's stop, take profit, time exit and liquidation every second |
| Start one more decision once a window ends (`RELEASE_OUT`) | `SYSTEM` (the scheduler, in code) | `SCHEDULE_V2`; one at a time; the schedule's 32 and the policy's 120 a UTC day |
| Change the events, the Fed's dates, the window or the rule | Nobody at run time: an update the owner installs | `TEMPLATES_V19` frozen in migration `0039` |

## ExecPlan 0059: the slow rule trades the main account

IMPLEMENTED ([ExecPlan 0059 §5](../plans/0059-the-slow-rule-trades-the-main-account.md#5-authority)); installed on the owner's PC on 2026-11-10, in force since 17:30:01 UTC (OBSERVED). `FUTURES_POLICY_V2` names `MAIN_RULE_V1`, code, as the main account's decider: under it the [M11 rows](#m11-the-futures-trader-and-the-owners-run-controls-execplan-0039) that let the trader decide, and the reviewer's, the daily decision reviewer's and the coach's rows of [0040](#execplan-0040-the-trade-reviewer-and-the-coach) and [0043](#execplan-0043-update-2-the-agents-read-the-scores), are in force only while a policy whose decider is an agent is installed (`FUTURES_POLICY_V1`; its code is kept for a rollback). No agent gains a tool, a read or a permission; the veto agent's rows of [0041 part 2](#execplan-0041-part-2-the-veto-twin-the-momentum-twin-and-the-placebo) are unchanged.

| Action | Who | Bound by |
|---|---|---|
| Read the day (Bitcoin's daily close against its closes 30, 91 and 365 days earlier, the volatility it sizes by), set the target and enter, resize (the whole position out, the target in, in one step), exit to flat or hold | `SYSTEM` (the futures engine's rule phase, in code), at the first finished 15-minute bar of each UTC day, again at each bar while the day is not spent | `MAIN_RULE_V1` and `FUTURES_POLICY_V2`, frozen in migration `0040`; long only, at most 1x, one position; an entry or increase refused under a latch, a paused, stopping or stopped run or an integrity fault, any fill refused on a stale quote or mark or a thin book, each refusal stored with its codes; an exit or decrease still exits under a latch |
| Store each reading and its outcome | `SYSTEM` | `futures_rule_readings`, append-only; no agent reads it |
| Close the rule's position when its run is stopping (the drawdown stop, or the owner's Stop) | `SYSTEM`, every second (the protection phase) | The whole position at once as `RULE_EXIT`; the run then stops once flat; added after the money-path review (2026-11-10), as the rule's position has no exit of its own but a later reading's |
| Close the rule's position at liquidation | `SYSTEM`, every second | The rule's position has no stop, take profit or time exit (a database check allows that only for `opened_by = 'RULE'`); at 1x long its liquidation is not reached |
| End the trader's run and start the rule's | `SYSTEM`, once, at the first finished bar with the run running without a cause, the account flat and funded and its valuation valid | The run ends `NEW_POLICY` (event `POLICY_REPLACED` with both policies' hashes); the next starts under `FUTURES_POLICY_V2` with its own high-water NAV; nothing of the ledger is reset; a stopped run waits for the owner's Start, which starts under V2 |
| Decide for the main account; review its trades; write the coach's note | Nobody while `FUTURES_POLICY_V2` is in force: the agent worker asks no trader, trade reviewer, daily decision reviewer or coach; every agent decision is refused `POLICY_CHANGED`, whatever policy it names | `WorkflowGraph.trader_work`, read from the policy in code |
| End the ChatGPT backtest (0052) | `SYSTEM` (the agent worker), at the install | `TRADER_REPLACED`; nothing starts it again |
| Pause, Resume, Stop, Stop and close, top-ups, the off switch, Start after a stop | The owner only, as [M11](#m11-the-futures-trader-and-the-owners-run-controls-execplan-0039) | Stop and close is the owner's way to close the rule's position at once at the order book's price; a plain Stop closes it at once too (above) |
| Change the rule, its values, the policy or the measure, or act on the measure's verdict | Nobody at run time: a new version is an update the owner installs | The stored definitions must equal the code |

## ExecPlan 0060: spot trading only (M12)

IMPLEMENTED ([ExecPlan 0060 §5](../../plans/0060-spot-trading-only.md#5-authority)); installed on the owner's PC on 2026-11-12 ([ExecPlan 0060 §14](../../plans/0060-spot-trading-only.md#14-progress)). `SPOT_POLICY_V1` names `SPOT_RULE_V1`, code, as the account's only decider ([RISK_POLICY](RISK_POLICY.md#m12-spot_policy_v1-spot_rule_v1-and-spot_cost_v1-execplan-0060)). The actors are `SYSTEM` and the `OWNER`: ANALYST, RESEARCHER, EVALUATOR and COORDINATOR have no process, no tool and no row below; the agents' worker, runner, egress and sign-in services are removed, and every earlier section's agent rows are history.

| Action | Who | Bound by |
|---|---|---|
| Read the day and buy or sell the difference to the target, or sell everything when the target is zero | `SYSTEM` (the spot engine's step, in code), at its first step at or after 00:05 UTC once the day's final candle is stored, again every 15 minutes while the day is not spent | `SPOT_RULE_V1`, `SPOT_POLICY_V1` and `SPOT_COST_V1`, frozen in migration `0041`; long or cash; a buy refused under a latch, a paused or stopping run or an integrity hold; any trade refused on a stale or thin book, an unverified clock or an unusable instrument, each refusal stored with its codes; a sell still sells under a latch |
| Store each reading and its outcome | `SYSTEM` | `spot_rule_readings`, one row per day acted on; a day not readable or refused once a day per reason |
| Sell everything when the run is stopping (the drawdown stop or the owner's Stop and sell) | `SYSTEM`, at each step | `STOP_SELL` of the BTC that can be sold; the run stops once only USDT or unsellable dust is held |
| Start the first run | `SYSTEM`, once the account is funded | The run records the three definitions' hashes as `SYSTEM`; the account keeps its money and units, the run's high-water NAV starts with it |
| Retire the futures account | `SYSTEM`, in migration `0041` | Refused unless the futures account is flat with nothing reserved; a live futures run ends `STOPPED`, `NEW_POLICY`, with a `FUTURES_RETIRED` event; the retired tables move to the `archive` schema with every row, readable by the migration role only |
| Compute the backtest | `SYSTEM` (the execution worker, outside the money step), after the install and after each new final day | `SPOT_BACKTEST_V1` on the stored daily candles; it writes only `spot_backtests` and changes nothing in the account |
| Pause, Resume, Stop and sell, Start, top-ups | The owner only, as requests on the Settings page that the engine applies at its next step | Pause opens an `OWNER` cause (no buy; sells continue); Resume closes it; Stop and sell makes the run stopping; Start begins a new run after a stopped one, the drawdown stop's included; top-ups are NAV-neutral at a valid valuation ([LEDGER](LEDGER.md)) |
| Change the rule, its values, the policy, the cost, the backtest or the measure, or act on the measure's verdict | Nobody at run time: a new version is an update the owner installs | The stored definitions must equal the code; the measure of [0060 §4.10](../../plans/0060-spot-trading-only.md#410-the-measure-pre-registered) changes nothing by itself |
| Ask a model anything | Nobody: no model runs in the app | A model's return is a new plan the owner approves |
