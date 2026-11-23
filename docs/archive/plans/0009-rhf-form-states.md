# ExecPlan 0009 — React Hook Form submission states

## Goal and starting facts

Use the installed React Hook Form (RHF) for validation, submission pending state, and submission errors in every production RHF form: owner setup, owner sign-in, and virtual top-up review. Before this change, those forms duplicated submission state in React `busy`/`message` variables. The funding confirmation dialog is a separate, authoritative action after draft review.

## Scope and boundaries

- Change `owner-access.tsx`, `account-home.tsx`, and the related Zod messages and tests. No API, database, schema, package, trading, collector, or account authority change.
- Use `formState.isSubmitting` for the three requests and `setError("root.server", …)` for safe, visible form failures. Clear a stale server error when the user edits an input. Preserve field errors through Zod resolver and shadcn `FieldError`.
- Retain independent state for funding initialization, confirmation, unknown-outcome reconciliation, pending request action, and sign-out. A successful top-up draft opens review; only an authoritative `POSTED` confirmation resets the amount.
- Never infer a posted contribution from an RHF submission flag or a successful draft response. Keep account balances and funding history server-owned.

## Source and project evidence

- OBSERVED 2026-09-28: installed `react-hook-form` 7.89.0, `@hookform/resolvers` 5.9.1, Zod 4.6.5, shadcn 4.21.0, Base UI 1.8.0. Docker `shadcn info --json` confirmed TanStack Start, `base-nova`, preset `b2fms61Bqi`, and installed `Field`, `Alert`, `Button`, `Input`, and `Spinner`. No primitive or dependency was added.
- [Official RHF `formState`](https://react-hook-form.com/docs/useform/formstate) defines `isSubmitting` for an active submit; `isLoading` applies to asynchronous default values. [Official `setError`](https://react-hook-form.com/docs/useform/seterror) documents `root` for server/global errors that clear on a subsequent submit. [Official `handleSubmit`](https://react-hook-form.com/docs/useform/handlesubmit) leaves async error handling to the caller.
- [Official shadcn RHF guide](https://ui.shadcn.com/docs/forms/react-hook-form) composes `Controller`, `Field`, `FieldError`, `data-invalid`, and `aria-invalid`. The existing source already follows that pattern for field validation.

## Implementation and checks

1. IMPLEMENTED: replace form-specific `busy` and `message` state with RHF `isSubmitting` and root server errors; provide readable Zod/auth messages.
2. IMPLEMENTED: keep other account actions independently busy and disable conflicting actions while draft review is submitting.
3. VERIFIED: Docker lint, typecheck, 21 unit tests, targeted formatting, and production build passed. Tests cover invalid fields, delayed submission, server failure/edit, duplicate review and draft versus posting behavior. The existing isolated funding browser case passed.
4. VERIFIED: a protected normal database backup preceded a web-only recreate. The normal app and signed-in account browser were healthy. No forward migration was needed. Owner data was not used for test funding.

Affected gates: Q01 requires no client-side balance authority or premature reset; Q02 requires accessible field and global errors plus pending buttons; Q05 requires frozen Docker checks/build; Q10 requires protected backup and verified normal web update. If checks fail, repair before deployment. The previous schema-compatible web image is the application rollback; do not restore an old database over live collection. Record exact results and unresolved limits below.

## Completion evidence

Docker `shadcn info --json` confirmed the fixed preset, Base UI and installed components. `docker compose --profile tools build web-tools --quiet` passed. After correction of an unnecessary optional chain, explicit test cleanup and formatting, Docker `pnpm --filter web lint`, `typecheck`, `test:unit` (21 passed), targeted Prettier check and `build` all exited 0. The production build retained the prior nonfatal dependency `"use client"` directive warnings. `git diff --check` passed with Windows line-ending notices.

The disposable `asl-rhf-0928a` Compose project used task-specific secrets, database `asl_m1_browser_rhf_0928a`, port 4334 and separate networks. `browser-tests pnpm --filter web test:e2e e2e/funding.spec.ts` passed 1 Chromium case in 3.6 seconds, covering setup, invalid amount, initialization, top-up, sign-out and expired-session recovery. Those contributions belong only to the disposable database. Its containers and networks were stopped afterward without deleting the test volume.

Before normal rollout, `pg_dump -Fc` and `docker cp` passed. The protected dump at `.cache/deployments/rhf-forms-20260928a/rhf-forms-20260928a.dump` is 6,228,707 bytes with SHA-256 `c6680d3cff28f273a2b540568a95644e3490a8a759f123c2ab2d43320859a131`. Docker `build web --quiet` and `up -d --no-deps --wait --wait-timeout 120 web` passed. The web service is healthy on image `sha256:497e20bb23b2839b783bae280af74b08cf9f8d46947b02a160e66725c9606d80`; previous web image `sha256:7df510e657d195ccb14254c33ac0e9729f2214c4648d09b9fc0efa86682e5602` remains a schema-compatible fallback. API, PostgreSQL and worker container IDs stayed unchanged. Schema remained `0004_m2_completion`; `/` and `/system` returned HTTP 200. The signed-in in-app browser displayed the normal Account balances and virtual top-up form after rollout; no owner funding action was performed there. The current application source was built into both isolated and normal web images before documentation-only edits.

Q01 passed for the unchanged server authority and tested draft/posting boundary. Q02 passed automated field/error and browser flow checks; manual Narrator was not rerun for this scoped form-state change. Q05 passed Docker checks/build. Q10 passed backup and normal running-state checks. Full M1 financial backend and M2 acceptance suites were not rerun because neither backend nor market logic changed. Remaining work is later approved milestones, not form-state implementation.
