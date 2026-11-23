# Mandatory shadcn and chart skill workflow

## Scope and source of truth

Every task that creates, changes, reviews, or fixes frontend UI must use the **official shadcn skill**. This includes loading/error/empty states, forms, tables, navigation, accessibility, and chart containers. A root instruction saying “use shadcn” is not proof that the skill is installed or loaded.

The upstream install and project-aware workflow are documented in [UI-01](REFERENCES.md#ui-01). The upstream skill source is [UI-03](REFERENCES.md#ui-03). Do not vendor an invented substitute or copy a stale skill from a previous repository.

## Installation in the actual authoring environment

During authorized setup, run:

```sh
pnpm dlx skills add shadcn/ui
```

Select Codex, Claude Code, or both according to the actual development clients. Inspect the resulting files/symlinks, upstream origin, and client discovery. Record the installed source/revision where discoverable in [INTEGRATION_EVIDENCE.md](INTEGRATION_EVIDENCE.md). Do not claim a globally installed skill is visible inside a container or another client's environment without checking.

The coding environment must be able to execute the package manager and shadcn commands that the skill uses. Supported project arrangements are an editor attached to a development container, or a host coding client with its own Node/pnpm authoring prerequisites invoking containerized app builds/tests. The application itself must not depend on host Node or Python. Do not route Docker operations through a Docker socket mounted into the application.

Codex's documented skill discovery is described in [AI-05](REFERENCES.md#ai-05). Verify behavior for the installed client. If automatic loading does not occur, explicitly invoke/read the installed official skill using supported client controls. If unavailable, stop UI implementation and report the setup blocker; backend work may continue.

## Fixed scaffold and preservation

Execute exactly the owner-selected bootstrap command in a verified empty scaffold directory:

```sh
pnpm dlx shadcn@latest init --preset b2fms61Bqi --template start --pointer
```

The repository already contains Markdown and scoped instruction files. Do not delete those files to satisfy a scaffolder's empty-directory check. Use a temporary scaffold directory and merge the reviewed generated application into `apps/web`, preserving supplied instructions. Record the generated project tree, resolved CLI/runtime/dependency versions, and final workspace changes. The temporary target and working directory are part of the setup plan, not an excuse to change the preset.

Inspect the actual `components.json`, CSS, framework setup, package manifest, aliases, icon dependency, and component base. Do not guess whether this preset uses Base UI, Radix, or another supported base. Do not replace its typography, tokens, radius, colors, or pointer behavior with a remembered theme. Add financial semantic tokens only when necessary, preserving accessible contrast and the preset's design system.

The scaffold has **not been run while preparing this pack**. An unavailable preset or incompatible upstream change is a reported blocker, not permission to silently select another preset.

## Required sequence for every UI task

1. Read the installed official skill and `apps/web/AGENTS.md`; identify the nearest `components.json`. Obtain current project-context output through the skill's documented `shadcn info --json` workflow.
2. Search the configured registry and official docs for existing components/blocks. Inspect their current APIs for the actual component base. Use the installed CLI/skill commands rather than guessed command syntax.
3. Prefer installed primitives; add missing upstream components using the documented CLI. Review dry-run/diff output where supported before overwriting an edited component.
4. Compose application features using those primitives and approved headless libraries. Preserve accessibility, focus behavior, semantic tokens, and responsive behavior.
5. Check official integration guidance for the installed versions of Start, Query, Table, RHF/Zod, and chart code touched by the task. Record material choices and deviations.
6. Run lint/type/unit checks and applicable browser checks, including error/empty/stale states. Report what was actually loaded, reused, installed, and verified.

The shadcn MCP server can support registry discovery but is optional; it does not replace the skill [UI-04](REFERENCES.md#ui-04). Obtain owner approval before changing global client/MCP configuration. MCP/skills are development tooling, not runtime trading tools.

## Reuse boundary

**Forbidden:** hand-made Button, Dialog, Input, Select, Tooltip, Tabs, Table primitive, Sidebar, Skeleton, or equivalent when the configured shadcn registry already provides the component; importing a second UI kit; bypassing accessibility with clickable divs; mixing incompatible base-specific APIs.

**Allowed and necessary:** domain forms, portfolio cards assembled from shadcn Card, TanStack Table column definitions, query hooks, trading-specific page layouts, typed API adapters, chart lifecycle wrappers, and test helpers. These compose the design system rather than duplicate it. An unavailable primitive requires recorded registry search evidence and a reviewed design choice.

The official Data Table recipe is an integration pattern, not a prebuilt trading table [UI-06](REFERENCES.md#ui-06). Implementing application-specific columns and server pagination is expected. Do not copy framework-specific Next.js imports from any example into this Start application.

## Financial charts

For every Lightweight Charts task, also load the official **lightweight-charts** skill. The upstream documentation lists its skill installer [FE-03](REFERENCES.md#fe-03). The project uses the pnpm invocation:

```sh
pnpm dlx skills add tradingview/lightweight-charts --skill lightweight-charts
```

This is the pnpm-runner form of the documented skills command. Verify installation for the active coding client. Do not install the plugin-authoring skill unless a separately justified custom chart plugin is actually being built. Read the installed library's documentation/types, not remembered v4 examples.

Use shadcn for chart cards, controls, tooltips outside the canvas, errors and settings. Use Lightweight Charts for financial series. Its imperative adapter is allowed; recreating the underlying chart engine is not. Check attribution/NOTICE obligations and include required attribution in the product [FE-02](REFERENCES.md#fe-02).

## UI task completion evidence

Record skill source and discovery, actual preset/base, components reused/added, official integration sources, test commands/results, browser evidence, and unresolved issues. Skill use is an implementation discipline, not a guarantee that generated code is correct.
