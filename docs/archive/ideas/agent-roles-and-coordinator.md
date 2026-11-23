# Idea: agent roles and a Coordinator agent

**PROPOSED idea, recorded 2026-10-18. Not scheduled, not implemented, not approved.** Mentor asked for this note so the idea is easy to find and pick up later. It changes no code, contract, prompt, policy or approval, and neither a role name nor this note grants a permission ([root AGENTS.md](../../../AGENTS.md), rule 3). When the idea is implemented, its content moves into the canonical contracts through that milestone's ExecPlan: workflow roles into [RUNTIME_AGENTS](../RUNTIME_AGENTS.md), permissions into [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), tools into [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md). This note is then marked as superseded.

**For M9, decided 2026-10-19 by Claude under the owner's delegation ([ExecPlan 0032 §4, D4](../plans/0032-m9-news-and-events-the-agents-trade-on.md#4-decisions-claude-made-under-the-owners-delegation)):** the simplest option. The four roles stay as they are, and M9 adds no role, follow-up menu, specialist role or digest. E2, S5 and S6 are already today's rules, and E4 is what M9 builds. E1, E3 and S1 to S4 stay ideas for later.

**Where it would land:** the evidence question in [M8](../../ROADMAP.md#m8--reliability-review-sustained-evidence-and-handoff) (no ExecPlan yet), the design in [M9](../../ROADMAP.md#m9--market-intelligence-and-event-driven-adaptive-paper-trading) ([ExecPlan 0027 §5](../plans/0027-m9-market-intelligence-and-event-driven-trading.md#5-background-agent-and-handoffs)). Not M7, which is still being finished.

## Mentor's words

> add this as a note somewhere where i can reference it easily and implement: somewhen I want to add roles to the agents, One of the agents I want to add is a Coordinator agent which all other agents report to and it takes decisions and other important things, what do you think about this? feel free to add suggestions

Mentor in the project thread, 2026-10-18 09:06 UTC.

## What the app already has

OBSERVED on `main` at `9917639`. The app already has four roles, and one of them is a coordinator that takes the trading decisions. That decision loop was built in M7, which is not switched on yet.

| Role | What it does in the M7 build | Templates | Prompt |
|---|---|---|---|
| ANALYST | Writes a market brief at 00, 06, 12 and 18 UTC and investigates source events; records sourced assessments | `MARKET_BRIEF_V1`, `EVENT_INVESTIGATION_V1` | `m7/analyst.v3.md` |
| RESEARCHER | Turns a question into a registered candidate and experiments in the isolated research area | `RESEARCH_V1` | `m6/researcher.v1.md` |
| EVALUATOR | Reviews briefs, every trade draft and every closed position's outcome, in a separate context | `BRIEF_REVIEW_V1`, `INTENT_REVIEW_V1`, `OUTCOME_REVIEW_V1` | `m7/evaluator.v3.md` |
| COORDINATOR | Decides what to do for BTC and SOL: drafts an entry, exit, cancel or stop tightening, has it reviewed, submits it to the engine; may pause new entries; asks the owner to approve research candidates | `PORTFOLIO_DECISION_V1`, `PROMOTION_V2` | `m7/coordinator.v2.md`, `m7/coordinator-promotion.v1.md` |

The grants and templates are in [definitions_v3.py](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/app/agents/definitions_v3.py); the prompts are in [services/agent-runner/prompts/m7](https://github.com/MentorAliu/adaptive_spot_lab/tree/44b9a8a/services/agent-runner/prompts/m7); the workflow graph is described in [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m7-runtime-generation-3-decisions-and-their-triggers-execplan-0026).

**How the others already report to the coordinator:** through records it reads, not through messages. A reviewed brief or assessment starts a decision (`ASSESSMENT_READY`). The decision is shown the newest reviewed brief for each symbol, the latest outcome reviews and the research candidates the owner approved. Each decision lists every symbol with its action and a reason, and can ask the owner to look at it (`owner_review_requested`).

**What the coordinator cannot do, by design:** give other agents work (the workflow graph is code-owned, and no model names a template, a child, a role or a delegation); submit an entry its review did not accept; set prices, quantities, stop levels, fees or limits (it picks only from the policy's fixed choices, and code computes and checks the rest); approve its own ideas; resume a pause.

So the idea is about half built. The open parts are more roles, and the coordinator directing the other agents and handling "other important things".

## Claude's opinion

The shape is right. One agent that sees the whole picture and makes the call is easier to understand, check and measure than several agents deciding separately, and it is what the M7 build already does. Three choices would make the full version safer and more useful:

1. **The evaluator should not report to the coordinator.** It reviews the coordinator's trade drafts; if it worked for the coordinator, its review could become a formality. It stays independent: its verdict is a record the coordinator cannot override, and an entry draft it does not accept cannot be submitted (a revised draft needs a new review).
2. **"Report to" should mean records, not conversation.** Each agent writes a short, sourced record with an expiry (a brief, a review, a research result), and the coordinator reads them. That costs less than agents talking to each other, can be replayed and audited, and survives a restart. [ExecPlan 0027 §5](../plans/0027-m9-market-intelligence-and-event-driven-trading.md#5-background-agent-and-handoffs) already asks for this.
3. **"Other important things" should mean choosing work and raising flags, not more power.** The coordinator can decide what to look into next, pause new entries and tell Mentor what needs attention. Raising limits, approving its own strategies, loosening a stop or overriding protection stay with Mentor and with code ([root AGENTS.md](../../../AGENTS.md), rule 4).

Costs to weigh before building more of it:

- **Time.** All roles share one model slot. In the PC load check of 2026-10-18 (gate run `m7-g1b`), a decision's 95th percentile was 16.8 s with a scripted stand-in for the model (OBSERVED, [ExecPlan 0026 progress](../plans/0026-m7-agent-driven-main-decisions.md#16-progress)), so a real model's time comes on top. Each extra hop (the coordinator asks, another agent works, its record is reviewed, the coordinator decides again) adds at least one more model run, and the proposed daily budget is 36 decisions.
- **Context.** A hub that reads everything needs the most input of any agent, and inputs are bounded (a decision's snapshot to 8 KiB).
- **One model, same blind spots.** Several roles on the same model are not independent opinions ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md#model-roles)).
- **More agents is not automatically better.** Coordination costs time and calls, and only an evaluation shows whether a role earns them ([AR-01](../contracts/REFERENCES.md#agent-readiness-research--2026-10-16), [MI-08](../contracts/REFERENCES.md#m9m10-agent-and-discovery-research--2026-10-16)). M8 already has to report whether the extra roles add value over simpler set-ups.

## Suggestions

All PROPOSED; none is decided.

| # | Suggestion | Milestone |
|---|---|---|
| S1 | **Let evidence decide first.** M7 built a comparison of the full workflow, the coordinator alone (`AGENT_POLICY_V1_SOLO`) and the fixed reference, on fixtures, and M8 has to report whether the extra roles add value. Add to that report, for each role, how often its record changed the coordinator's decision, and its time and model calls. Build S2 to S4 only for roles that earn their cost; if the coordinator alone does as well, keep the simpler set-up. | M8 |
| S2 | **The coordinator asks for follow-up work from a fixed menu.** One new tool (name to be chosen, for example `request_follow_up`) with a short list of kinds: refresh a symbol's brief, investigate an unexplained price move, ask research to test a recorded question. Code checks the request and starts the registered workflow with its own budget and daily cap; the coordinator never picks prompts, tools or permissions. This is the safe form of "all agents report to it". | M9, [§5 active investigation](../plans/0027-m9-market-intelligence-and-event-driven-trading.md#active-investigation-and-bounded-feedback) |
| S3 | **Specialist roles as versioned ANALYST prompts, not new permissions.** Candidates: news, macro, token fundamentals, liquidity and execution conditions, matching M9's [assessment dimensions](../plans/0027-m9-market-intelligence-and-event-driven-trading.md#assessment-dimensions-and-comparable-calculations). A role with grants of its own needs Mentor's approval in AUTONOMY_MATRIX. | M9 |
| S4 | **A coordinator digest for Mentor.** A short read-only summary once a day, or after an important event: decisions and abstentions, what each agent did, refusals, and the decisions that asked the owner to look (`owner_review_requested`). It informs and approves nothing. | M9, [§8 visibility](../plans/0027-m9-market-intelligence-and-event-driven-trading.md#8-visibility-feedback-and-evaluation) |
| S5 | **Risk stays in code.** A "risk officer" can be an evaluator prompt that adds a critique, but sizing, caps, stops and the risk gate stay deterministic and never wait for a model. This is today's rule; keep it. | Every milestone |
| S6 | **Fail safe without the coordinator.** When it is down, out of budget or stale, no new entries, and open positions keep their code protection. This is today's rule; any hub feature must keep it and test it. | Every milestone |

## Enhancements that would serve the goal

Added 2026-10-18 on Mentor's "do it" (09:21 UTC), after the question how this improves accuracy or the goal of the app. All PROPOSED. The honest frame: a coordinator structure by itself does not make decisions more accurate. It makes them consistent, traceable and measurable, which is what lets the app find out what makes or loses money. Accuracy comes from better inputs and from learning from recorded outcomes, and only a matched comparison under [EVALUATION](../EVALUATION.md#role-value-discovery-coverage-and-selection) can show a gain. No figure is promised.

| # | Enhancement | Why it could help | Milestone |
|---|---|---|---|
| E1 | **Mistakes become research questions.** Every closed position already gets an outcome record and an `OUTCOME_REVIEW_V1`. Add a code-kept tally of the reviews' reasons (for example late entry, stop too tight, costs ate the gain, unsupported news read; M9 already asks outcome reviews to separate source errors, interpretation, late assessment, cost effects and a loss despite compliance). When a reason repeats, the coordinator may send it to research as a question (through S2's menu). A lesson reaches live trading only through an approved policy change, never by the model editing itself. | The real learning loop: each loss becomes a testable question instead of a story. | M9, [§8 visibility, feedback and evaluation](../plans/0027-m9-market-intelligence-and-event-driven-trading.md#8-visibility-feedback-and-evaluation) |
| E2 | **Disagreement is a signal.** When the intent review and the coordinator disagree, the default is no trade, and the disagreement is logged with both sides' reasons. [M9-R26](../plans/0027-m9-market-intelligence-and-event-driven-trading.md#9-requirements-mapped-to-verification) already compares an "act only when most samples agree" variant in isolation at the same inference budget. | Fewer trades, likely better ones; the cost (missed gains, turnover) is measured, not assumed. | M9 (R26) |
| E3 | **Confidence checked against reality.** Each draft carries `uncertainty_level` (`LOW`, `MEDIUM`, `HIGH`). Record it with the position's outcome and report, per level, the after-cost result and the review verdicts. If `LOW` uncertainty trades do no better, the label is noise and the policy should ignore it; if they do, a later policy version may size by it, under its own approval. No probabilities are invented ([M9's calibration rule](../plans/0027-m9-market-intelligence-and-event-driven-trading.md#assessment-dimensions-and-comparable-calculations)). | Shows whether the model's own confidence carries information before anyone relies on it. | M8 (report), M9 (policy use) |
| E4 | **Fresher inputs before more agents.** M9's event-driven decisions (acting on a reviewed assessment, a price move or a position event instead of waiting for the next brief) are likely to move after-cost results more than any new role. Every extra hop makes a decision older; keep the chain short and measure trigger-to-submission time, which M7 already records. | Timeliness is measurable and cheap; a longer chain of agents is neither. | M9, [§7 event-driven decisions](../plans/0027-m9-market-intelligence-and-event-driven-trading.md#7-event-driven-decisions-and-policy-reconciliation) |

What this gives the goal: every trade with a traceable reason, every loss turned into a question the research side can test, and a running check of whether the agents' confidence and reviews carry information. That is the closest thing to an edge a paper-trading research app can build; the comparison decides whether it is one.

## What implementing it would take

- Mentor's go-ahead for the milestone: M9 starts after M8 is accepted and deployed.
- The milestone's ExecPlan decides each suggestion against M8's evidence and updates RUNTIME_AGENTS, AUTONOMY_MATRIX and AGENT_TOOL_CONTRACTS before any code.
- A new definitions generation (tools, grants, templates, prompts); probes showing that a follow-up request cannot name a template, a role or a tool, or exceed its cap; and a cost comparison at matched budgets under [EVALUATION](../EVALUATION.md#role-value-discovery-coverage-and-selection).
- Mentor approves the runtime profile again, because any change to the agents' definitions drops the approval.
