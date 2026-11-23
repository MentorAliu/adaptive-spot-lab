# Start with Codex or Claude Code

**Pack 2.0.0 — complete revised specification, not executable application code.**

## 1. Choose the correct entry path

For an empty repository, extract the ZIP contents directly into its root, preserving paths. `AGENTS.md`, `CLAUDE.md`, and this file belong at the repository root. No `docker compose up` application exists yet.

For an existing original pack, edited documentation or implementation, read [MIGRATION.md](MIGRATION.md) first. Preserve the current Git history, implementation status, lockfiles and measured evidence. Do not rerun the scaffolder over an existing app or claim old tests passed new requirements. Keep one active specification set, not original and revised instruction folders side by side.

Use your coding client's normal login, planning controls and existing security settings. The development client and the future application's Codex runtime are separate environments; never give runtime agents the development home directory or repository mount.

## 2. Paste this initial planning prompt

```text
Work in planning mode only. Do not modify repository files, install packages,
scaffold, run migrations, initialize credentials, start experiments, or make
paid/API model calls.

Read AGENTS.md, docs/STATUS.md, docs/DECISIONS.md, docs/PROJECT.md,
docs/ARCHITECTURE.md, docs/ROADMAP.md and docs/plans/0001-foundation.md.
Then read docs/AUTONOMY_MATRIX.md, docs/AGENT_TOOL_CONTRACTS.md and
relevant parts of docs/RUNTIME_AGENTS.md and docs/RESEARCH_WORKFLOWS.md
to understand future trust boundaries, not to implement them in M0.
For M0 read docs/SHADCN_WORKFLOW.md, docs/LIBRARIES.md, docs/FRONTEND.md,
docs/DOCKER.md, docs/COMMANDS.md, docs/PLANS.md and scoped AGENTS.md files
for paths you propose to touch. Use docs/README.md to locate other contracts.
Verify material integrations through the current official sources in
docs/REFERENCES.md, matching the installed or proposed versions.

Inspect the actual repository/environment. If code or edited documentation
already exists, apply MIGRATION.md's reconciliation path and preserve measured
progress rather than resetting it. Do not overwrite existing work or rescale
completed milestones by name alone.

Audit for contradictions and genuine foundation blockers. Preserve local Docker,
BTC/SOL spot paper-only scope, virtual 10,000 USDT plus top-ups, the exact Start
shadcn preset, mandatory official UI/chart skills, and the specified libraries.
Do not reopen answered owner decisions. Risk values are untested paper-pilot
proposals, not proven optima. No exchange credentials, live adapter, hidden live
switch, paid API fallback or unapproved native agent tools may be added.

The target includes role-scoped application tools, approved-source research,
registered experiments and agent trade/position intents. It is not selector-only.
Native Codex shell/browser/file tools are not the default runtime transport.
Authority remains in the permission/risk/broker services, with approvals for
new main strategies and expanded domains but not each routine permitted trade.

For an empty/unimplemented repository, plan M0 only in implementation detail.
For an existing implementation, identify the actual next bounded migration or
milestone task and explain why. Cover the remaining roadmap only briefly.
Preserve documentation while scaffolding. Establish official shadcn skill
installation and discovery in the actual coding environment; each UI task must
use it. Plan the Lightweight Charts skill for chart tasks. Verify SSR/Query
ownership, Table/RHF/Zod integration, lint support, Docker paths and test setup.

Return observed repository/environment state, proposed files, source/version
evidence, unresolved compatibility checks, trust boundaries, requirement-to-test
mapping, concrete verification commands and the reviewed plan. Distinguish facts
from proposals and checks not run. Stop before implementation.
```

Official development workflow references are [AI-03](../../REFERENCES.md#ai-03), [AI-04](../contracts/REFERENCES.md#ai-04), [AI-08](../../REFERENCES.md#ai-08) and [AI-09](../../REFERENCES.md#ai-09). Prompt instructions do not replace permissions, code controls or tests.

## 3. After review, authorize only the selected bounded task

For an empty repository's foundation:

```text
Implement the reviewed M0 foundation plan only. Preserve the specification,
existing files and security boundaries. Use the official shadcn skill before
UI work, research official integration guidance, preserve the exact preset,
and verify containerized build/test behavior. Finish code, tests, review and
verification for M0; update STATUS and INTEGRATION_EVIDENCE with actual results.
Do not fund an account, log in the runtime model, activate trading, add live
exchange access, or begin M1 automatically. Report exact commands/results,
unrun checks and remaining limitations.
```

For an existing implementation, replace M0 with the exact reviewed migration/task ID; do not authorize a whole roadmap through a vague “finish everything” prompt.

## 4. Exact frontend bootstrap and skills

During authorized setup, in the verified empty scaffold target:

```sh
pnpm dlx shadcn@latest init --preset b2fms61Bqi --template start --pointer
```

Preserve supplied documentation; use a temporary scaffold and reviewed merge into `apps/web` when needed. This preset has not been executed by this pack. Do not infer its typography, tokens, icons, base components or dependency versions.

Install and verify the official shadcn skill for the coding clients you actually use:

```sh
pnpm dlx skills add shadcn/ui
```

For financial-chart work, also install and load the official chart skill:

```sh
pnpm dlx skills add tradingview/lightweight-charts --skill lightweight-charts
```

Follow [docs/SHADCN_WORKFLOW.md](../../SHADCN_WORKFLOW.md) for source, discovery, container paths, component reuse and attribution. These skills are authoring tools, not runtime trading-agent tools. Do not fabricate replacement skills.

## 5. Activation is separate from implementation

A first fixed forward pilot requires approved denomination, risk/reference strategy, explicit cost assumptions and healthy/reconciled services at M4. Main agent-driven operation additionally requires the approved operating policy and M7 capability/security gates. Runtime subscription authentication and provider access are verified only with your explicit setup authorization.

Daily use should not ask permission for every allowed trade. New main strategy domains, higher risk, paid services and future live integration still require separate authority. The endpoint is measured capability under controls—not promised income or a “5/5” certification.
