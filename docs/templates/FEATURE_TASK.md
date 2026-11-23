# Scoped implementation task

Use this structure for one reviewed change. Replace placeholders with actual scope before authorizing implementation.

## Goal

Describe the user-visible or operational outcome and current milestone. State explicitly whether the task is planning-only or implementation-authorized.

## Context

List the smallest relevant repository documents, scoped AGENTS files, source paths and observed current behavior. Use official documentation links matching installed versions; do not paste the whole specification into every prompt.

## Constraints

Preserve paper-only scope, source integrity, financial authority and approved policy. For any UI work, load the official shadcn skill, inspect preset/context and reuse available primitives. For chart work also load the official Lightweight Charts skill. No unapproved dependencies, paid calls, live credentials or later-milestone expansion.

## Acceptance and verification

Define concrete behavior, failure cases, tests, exact proposed commands and observable outputs. Distinguish integration checks from mocks and performance evaluation from correctness tests. Include permissions and migration/recovery considerations where relevant.

Apply the [milestone quality gates](../ACCEPTANCE_CHECKLIST.md#quality-gates-for-every-milestone): assess all Q01–Q10 for a milestone, or the affected gates for a small scoped task. For each assessed gate state scope/applicability, acceptance condition and planned verification; attach its final result and evidence at completion. Explain exclusions and leave unrun applicable requirements open.

## Completion

Report changed files, actual commands/results, evidence, unresolved risks and checks not run. Update status/integration documentation. Stop at this task's boundary rather than automatically implementing the next milestone.

## Agent-specific contracts when applicable

Name the affected role, tool and canonical contract. State whether an operation reads data, writes an artifact, consumes a research budget, proposes a trade, or changes authority. Include exact server-derived identity/scope, permission epoch, idempotency, current-state checks, revocation/cancellation, unavailable inputs and positive-autonomy tests. Identify evidence from [ACCEPTANCE_CHECKLIST.md](../ACCEPTANCE_CHECKLIST.md) that the task will actually produce.

Do not confuse authoring-tool permissions with runtime tool grants. UI changes must represent real state rather than decorative agent conversations. Never claim a role exists because a prompt file was added.
