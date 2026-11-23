# Migration to the agent-driven specification

## What this package is

Pack **2.0.0** is a complete replacement specification derived from the original **1.0.0** archive. It is not an independent second design, an application-code patch, or permission to discard your implementation. All original relative file paths are retained; **no original files are renamed or removed** in this revision. New files add role/tool/research authority, runtime prompt templates, migration and acceptance records.

[CHANGELOG.md](CHANGELOG.md) lists actual added, modified and byte-unchanged files. [MANIFEST.md](MANIFEST.md) records packaged file hashes and original archive provenance. The version number belongs to this documentation pack, not a verified running app release.

## Empty repository

Extract the full ZIP contents directly into the repository root, preserving directories. The archive deliberately contains `AGENTS.md` at its root, not an extra project directory. Open the repository and follow [START_HERE.md](START_HERE.md). Do not call `/init` over the supplied instructions. No app can run until the implementation milestones exist.

## Repository containing only the unchanged original pack

Preserve a baseline copy or Git commit of the original documentation. Extract the revised ZIP outside the repository first and inspect its files/change log. Replace matching documentation paths and add the new paths, preserving directory structure. Because this release removes/renames nothing, there is no deletion list to apply.

Keep one active instruction set. Archive the old ZIP outside the working tree or in version history; do not put a second old `AGENTS.md` tree inside the repository where a coding client might load it. Review the documentation diff and follow the revised planning prompt.

## Repository with your edits or application code

1. Inspect the current worktree and preserve your work before replacement. Create a branch for the documentation migration using your normal Git workflow. Commit only reviewed, intended files; do not stage secrets or generated credentials. No destructive cleanup or reset is needed.
2. Extract the new pack to a separate temporary directory. Compare each modified file against both your current copy and the original pack, using a three-way merge where possible. Copy unchanged files only if you need them; do not replace user-owned additions absent from this archive.
3. Preserve actual `docs/STATUS.md`, completed ExecPlan history, `docs/INTEGRATION_EVIDENCE.md`, local commands, observed versions, lockfiles and test results. Merge new requirements into these records rather than overwriting them with unexecuted template status. Retain historical run manifests and approvals unchanged.
4. Review runtime prompts and scoped AGENTS/CLAUDE instructions together. Update authority, tool, adaptation and roadmap rules consistently; do not retain the old blanket selector-only behavior as an active requirement. Do not broaden native runtime tools merely because application-tool access was added.
5. Compare current code with the new contracts and [ACCEPTANCE_CHECKLIST.md](../../ACCEPTANCE_CHECKLIST.md). Write a bounded migration implementation plan for the actual gaps. Prior tests do not automatically satisfy new role/tool/revocation requirements. Do not rerun the preset or delete generated components to make the repo resemble a new scaffold.
6. Review the resulting Git diff, rerun relevant existing checks, and record which new checks remain unavailable. Apply one reviewed code milestone at a time. Keep an active forward account paused until its deployed code/config still satisfies the approved policy; new agent modes stay disabled until their gates pass.

These are manual-review instructions, not a script that has been executed against your repository. This pack has no access to your PC's files or current Git state.

## Old-to-new milestone interpretation

| Original | Revised interpretation |
|---|---|
| M0–M4 foundation through fixed pilot | Retained with explicit v2 boundary/traceability additions; preserve evidence and reconcile actual differences. |
| Old M5 no-native-tool model adapter | New M5 includes a real application-brokered multi-step tool loop, grants/revocation and positive/negative capability tests. Native tools remain restricted. |
| Old M6 approved-strategy daily selector | Split/expanded into M6 research roles/tools and M7 agent-driven main trading; the daily selector survives as a separate baseline. |
| Old M7 reliability/report | Becomes M8 with expanded agent, tool and resource failure tests. |

No old milestone is automatically marked complete under its new counterpart. The enlarged runtime is not an instruction to modify the ledger's mathematics, financial caps or selected frontend.

## Preserved choices and deliberate differences

Preserved: BTC/SOL spot paper scope, virtual 10,000 USDT/top-ups, local Docker, chosen Python/PostgreSQL engine, subscription-first Codex without paid fallback, exact TanStack Start/shadcn preset, mandatory official skills, required libraries, numeric risk proposal and owner approval for new main strategies/domains.

Expanded: agents may investigate approved sources, run preauthorized registered experiments, critique evidence, submit discretionary trade/position intents and review outcomes. Ordinary allowed actions no longer require a separate human prompt. Grants, current-state financial checks and immutable original position mandates still apply. A favorable model review is not owner approval.

Do not import the conversation's informal “5/5” label as a test result. The acceptance checklist defines observable capability; trading advantage still requires forward evidence.
