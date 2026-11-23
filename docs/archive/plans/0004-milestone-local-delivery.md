# ExecPlan 0004 — milestone deployment rule and M2 local catch-up

## Goal and owner authority

The owner requested that after each M-numbered milestone completion, the app run its latest changes. Persist that rule in root authoring instructions and canonical delivery/operations contracts. Apply it now to the completed M2 code so the normal local app exposes owner setup/sign-in. This is an M2 operational follow-up, not M3.

The [dated decision](../../DECISIONS.md#2026-09-28--completed-milestones-must-run-locally) supplies standing authorization for routine local updates. The previous no-owner-deployment boundary is superseded only for software deployment. Keep collection, trading, model/agent/research and paid services disabled; preserve owner approval/funding requirements and safety latches.

## Observed starting state

- Repository clean on `main`, commit `bb0fb0298ca56cedf191e3db2c494039a9d18d3f`; origin `https://github.com/MentorAliu/adaptive_spot_lab.git`.
- M2 application acceptance is complete; owner-reported Narrator N01–N09 passed. [ExecPlan 0003](0003-market-data-charts.md) retains the source/image identities, commands and limitations.
- Normal project `adaptive-spot-lab` runs healthy `web`, `api`, `postgres`, URL `http://127.0.0.1:4317/`. Its page identifies M0; database `asl` is at `0001_foundation`, with only `alembic_version` and `system_metadata` tables.
- Persistent volume `adaptive-spot-lab_postgres_data`; PostgreSQL image `postgres:17.11-alpine3.24`, image ID `sha256:b0f9560a2de083e2cc7382e75f808c7381a32852a7ec49117deedb300e552b24`.
- The normal owner setup key is absent. Generate required missing secrets without replacing existing ones; never put values in evidence or Git.

## Implementation and deployment sequence

1. Add the root rule, dated owner decision, canonical deployment procedure, planning/Q09 links and current-state record. Reconcile the old M2 activation wording while preserving historical acceptance evidence.
2. Record normal container/image/network/volume identities and metadata fingerprints. Create a protected local backup and verify an isolated restore before changing the normal schema.
3. Build the existing accepted M2 application with frozen Docker dependencies; no application code/dependency changes are planned. Create only missing local secrets and validate resolved Compose configuration.
4. Stop affected M0 web/API writes, retain PostgreSQL/volume, migrate forward to `0004_m2_completion`, start the new API/web, and leave the market profile disabled.
5. Verify readiness, schema, preserved metadata, zero owner/funding/journal activity, reconciliation, actual runtime source/image identity and normal owner setup UI. Do not create the owner account or fund it.
6. Stop only the disposable restore helper; retain its volume, the backup and run evidence. Record outcomes, commit/push reviewed changes to `origin/main` without force and verify the remote and clean local state.

## Applicable quality gates and evidence

| Gate | Applicability / verification | Result |
|---|---|---|
| Q01/Q02/Q05/Q06/Q07 | Application source unchanged; retain M2 acceptance. Check the actual normal browser/setup surface and deployment failure visibility. Do not rerun unrelated hour-long workloads for documentation/deployment-only changes. | VERIFIED for this deployment: 146 source files, 29 runtime API/migration files and 64 compiled web files matched; normal sign-in browser smoke passed. Prior M2 acceptance remains scoped to its recorded evidence. |
| Q03 | Preserve foundation metadata, apply approved forward migrations, verify uninitialized/zero financial state and reconciliation. | VERIFIED: metadata fingerprints preserved; initial post-migration financial state was empty/uninitialized; reconciliation passed again after concurrent normal-app activity. |
| Q04 | Protect the backup, preserve existing secrets, keep loopback-only web/private API/DB, no test flags or privileged/socket mounts. Do not display setup credentials. | VERIFIED: original secret hashes unchanged; only missing secrets created; deployment inspection preserved isolation. |
| Q08 | Verify health/readiness and honest disabled collection/unconfigured owner state. | VERIFIED: readiness and reconciliation passed; both feeds DISABLED, no market worker; initial owner setup required, later normal sign-in observed. |
| Q09 | Record backup checksum and real isolated restore, migrate the actual normal database, verify running release and recovery artifacts. | VERIFIED: backup restored with matching fingerprints; forward migration and startup exited 0; three normal services left healthy; recovery volume/dump retained. |
| Q10 | Diff/link checks; no contradictory deployment authority; record exact commands/results and residual limits. | VERIFIED: 174 relative file links resolve; `git diff --check` passed; deployment authority and historical acceptance wording were reconciled. Git publication is recorded separately in the delivery receipt. |

## Failure and recovery

Do not delete/downgrade owner data or run test fixtures on it. Before migration, the old M0 images/database are the intact running fallback. After migration, old M0/M1 images are not assumed schema-compatible: prefer the verified M2 images with collection disabled and repair forward. Retain the pre-upgrade dump and isolated verified restoration; never overwrite the only normal database as a routine retry. If an upgrade cannot be made healthy, report deployment blocked rather than claiming the new rule is satisfied.

## Living run record

**DEPLOYMENT VERIFIED, 2026-09-28 04:31 UTC.** Evidence is retained under ignored, access-restricted `.cache/deployments/m2-local-20260928a/`. [COMMANDS.md](../COMMANDS.md#verified-m2-normal-deployment--2026-09-28) records the operations. Earlier M2 acceptance documents remain historical and unchanged by this follow-up. Application source is unchanged from `bb0fb0298ca56cedf191e3db2c494039a9d18d3f`; this follow-up changes authoring/delivery documentation only.

### Backup, migration and runtime identity

- Protected PostgreSQL custom dump: `m2-local-20260928a.dump`, 2,555 bytes, SHA-256 `d4973a3296377befa132ef5f7fd5c30f97c2303c7541873939e8dcaf389a62a3`. Real restore completed at 04:21 UTC in `asl-m2-delivery-20260928a-restore`, network `none`, with matching schema/table/metadata fingerprints. The backup predates subsequent normal-app account activity and must not overwrite that newer state.
- Frozen Compose builds for `migrate api web` passed. Only the three missing local secrets were created; the original PostgreSQL/internal-service secrets retained their hashes. No secret values were placed in evidence or Git.
- Normal web/API were stopped, PostgreSQL and `adaptive-spot-lab_postgres_data` preserved, and migrations `0001→0002→0003→0004_m2_completion` applied forward. `up -d --wait --wait-timeout 120 api web` exited 0. No market/test profile was started.
- Running web image: `sha256:6ea3f051483313374dcfe6fe1fea3f4a178886b1dfc3200508ecbb12c78ff581`; API: `sha256:2676daf6f11642cbd9de8ad0ae1c5c621d57e467e0c55093bf1de59f32242dee`; migration image: `sha256:f554937283ada7de75a895e70ee9e00c2cc379d658a93076b5a5c5f533ac74cd`. PostgreSQL retained its starting image and volume.
- All 146 files in `m2-completion-0927f/source-images-20260927T215706208.json` match. All 29 Python/migration/configuration files read from the normal API match the checkout. All 64 compiled web files match the accepted Narrator image `sha256:8c96dac8575ddb8b2e73f9ce37957ce3326afa7ec1b0c72106d465794863d44e` exactly. Different image export identities do not imply a changed application payload.

### Observed normal behavior and retained controls

The immediate post-migration check found no owner/session/funding/journal/reservation/market observations and an uninitialized zero account. Foundation metadata fingerprints were unchanged; readiness and reconciliation passed; owner setup was required. During subsequent read-only browser checks, concurrent normal-app activity created an owner and initialized the virtual account. The authoring agent did not submit setup, sign-in or funding requests. That newer state was preserved, its financial details remain in protected local evidence, and a final reconciliation returned `OK`.

The actual browser at `http://127.0.0.1:4317/` showed the labeled owner passphrase field and Sign in button, PAPER/virtual-denomination context, and Account/Markets/System navigation. The first observation reported an expired session; refresh showed the normal sign-in page. Visual and accessibility-tree inspection confirmed it; no credentials were entered. The official shadcn skill was loaded and the pinned Docker CLI discovery confirmed TanStack Start, Base UI/base-nova and preset `b2fms61Bqi`; no UI components changed. This was a deployment smoke check, not a new Narrator or full browser-suite claim.

Web remains bound only to `127.0.0.1:4317`; API/DB have no published ports. Normal services have no test flag or privileged/Docker-socket/source mounts. Web/API remain read-only with scoped secrets. Both market feeds remain `DISABLED`, with no observations or worker collection. The normal stack was left healthy/running at 04:31 UTC. Only the labeled disposable restore container was stopped/removed; its volume `asl-m2-delivery-20260928a-restore-data`, backup, prior M2 evidence volumes and logs remain.

### Failed attempts and limits

The first backup-helper launch failed because its newly protected folder initially omitted the actual Windows owner's SID. The owner was granted access to this task-owned folder, broad inherited access stayed removed, and the subsequent backup/restore passed; `backup-attempt-1.json` retains the failure. The first shadcn discovery attempt used `--network none` and failed its official registry lookup; the same pinned image succeeded with bounded command execution on `bridge`, without installing dependencies. Both outputs are retained. Neither failed attempt is counted as a pass.

No application source, dependency or migration was edited. The prior full M2 tests/performance/Narrator evidence was not rerun because runtime payloads were proven unchanged. M3, public collection activation, trading and agent/model workflows remain outside this follow-up. Documentation checks and Git remote/clean-state verification are retained in the same run directory's delivery receipts.
