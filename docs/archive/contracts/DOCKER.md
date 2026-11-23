# Docker-first local deployment

## Status and target

The original specification pack was Markdown only. M0 now has verified Dockerfiles, [Compose configuration](../../../compose.yaml), tooling and tests; see [COMMANDS.md](../../COMMANDS.md), [STATUS.md](../../STATUS.md), and [INTEGRATION_EVIDENCE.md](INTEGRATION_EVIDENCE.md) for observed versions and results. Later operational and agent-service requirements in this contract remain future gates.

The logical services are `web`, `api`, the workers, `postgres`, the agent services and `source-fetcher`. M6's research services (`research-postgres`, `research-runner`, `research-bridge`, and the one-shot `research-migrate` and `research-admin`) are retired since [ExecPlan 0035](#research-services-retired-execplan-0035); [ExecPlan 0023 §5.1](../plans/0023-m6-research-investigations.md#51-services-networks-and-identities-all-new-pilot-services-untouched) records their former topology. Reviewed engine modules/image are shared where suitable, with different entrypoints, permissions and lifecycle/health. Later services are disabled until implemented. M5 adds the agent services below (§"M5 agent services"); they ship built but not started, and a disabled or absent model runtime never breaks fixed paper trading. Hosted model inference and Binance remain external network services; Docker does not run the subscribed model locally.

## The services since ExecPlan 0060 (M12)

IMPLEMENTED in [`compose.yaml`](../../../compose.yaml) by [ExecPlan 0060](../../plans/0060-spot-trading-only.md); `docker compose config` NOT RUN in the cloud (no Docker there); the update that builds and starts the services from this file completed on the owner's PC on 2026-11-12 ([ExecPlan 0060 §14](../../plans/0060-spot-trading-only.md#14-progress)). The app's services are `postgres`, the one-shot `migrate`, `api`, `web`, `market-worker` (profile `market`, `python -m app.spot_market.worker`, on `private` and `market_egress`) and `execution-worker` (profile `execution`, `python -m app.execution.worker`, on `private` only); the tool and test profiles keep `web-tools`, `engine-tools`, `engine-tests` and `browser-tests`. The secrets are `api_internal_key`, `postgres_password`, `api_db_password`, `market_worker_password` and `execution_db_password`; the networks `frontend`, `private` (internal) and `market_egress`.

Retired by ExecPlan 0060, with their code: `agent-worker`, `agent-runner`, `agent-egress`, `agent-auth`, the agents' test services and `mock-provider`, `source-fetcher` and `evaluation-worker`, with the networks `agent_control`, `agent_provider`, `model_egress` and `source_egress`. The update stops and removes their containers and networks by exact Compose labels and ids ([OPERATIONS](OPERATIONS.md#the-update-file-m8)); their volumes (the agents' sign-in and keys, the research data) and the secret files on the PC stay, read by nothing. The sections below that describe them are history.

## Build and development

Use multi-stage images, compatible pinned runtimes, locked dependencies and nonroot final processes. Keep production source/dependencies minimal. Build/test commands run in containers; host editor/Codex/Claude installation and its authoring tools are a separate choice.

Provide a bootstrap tooling image that works before application manifests exist. It supplies the verified Node/pnpm environment required to execute the owner's exact scaffold. Create in a temporary empty directory and merge into `apps/web` without overwriting Markdown. Do not require a successful app build to build the tool that creates the app.

Use a root pnpm workspace and separate Python environment lockfile. Verify TanStack Start's actual generated build/deployment output and official hosting integration [TS-02](REFERENCES.md#ts-02); do not assume a Next.js or obsolete server path. Verify current FastAPI container guidance and actual process startup [BE-01](REFERENCES.md#be-01).

Provide development, tooling and test profiles with explicit bind mounts and separate dependency caches/volumes. Test DB/data volumes must be distinct from normal paper history. Never run destructive reset/`down -v` against the user's persistent data as routine cleanup.

## Networks, storage and secrets

M2 adds an optional `market-worker` service on the private database network and a dedicated `market_egress` network. It is absent from default `docker compose up` unless the `market` profile is selected, and its collection switch defaults off. Only this service and the explicit public-smoke tool join `market_egress`; API/PostgreSQL remain private and web remains loopback-only. The worker has only `market_worker_password`, a read-only root filesystem, temporary `/tmp`, 1 CPU, 512 MiB memory and 128 PID limits. It has no Docker socket, host home/repository mount, exchange credential or API/account secret. A separate migration service retains sole Alembic ownership.

The M2 acceptance wrapper creates fresh per-run secrets, ports, subnets, database names, Compose projects and volumes under ignored `.cache/m2/<run-id>`. Normal tests and browser fixtures have no public egress; only explicitly invoked `PublicSmoke` or bounded `PublicWorkerStart` verification contacts the public provider. Its `Stop` phase stops only the manifest's projects and retains volumes/evidence. [ExecPlan 0003](../plans/0003-market-data-charts.md) records actual test and cleanup outcomes.

Completion phases separate worker faults, recovery memory, browser races/accessibility, full-density storage, pinned exhaustion, predecessor migration and market-egress interruption. Storage/cap fixtures have separate disposable volumes; accelerated COPY preserves production record shapes but is labeled synthetic storage evidence, not ingestion throughput. The real-time worker performance helper uses the actual WebSocket/parser/queue/store path under 1 CPU/512 MiB/128 PIDs. `Snapshot` records source hashes, image IDs and Docker hardware without secret contents. `PublicWorkerNetworkInterrupt` verifies manifest ownership before disconnecting only the market worker from its egress network and restores that connection in `finally`.

Only the web entry point is published to `127.0.0.1` on a documented port. Docker documents how published ports bind by default; explicitly constrain the binding [OPS-03](REFERENCES.md#ops-03). API and Postgres are private services, not host/LAN endpoints. Validate Host/Origin to reduce local web attack exposure.

Use durable volumes for PostgreSQL, retained datasets/artifacts and the narrowly scoped Codex auth store. Grant services only the mounts and internal credentials they require. Static secrets can use service-scoped Compose secrets [OPS-02](REFERENCES.md#ops-02). Codex's refreshable auth cache needs a protected writable volume with correct ownership; keep it out of general artifact backups unless explicitly protected.

No privileged containers, host PID namespace, host home-directory mounts, Docker socket, or developer repo mounts in the runtime agent. Prefer read-only runtime filesystems where supported with explicit writable temp/state locations. Nonroot and read-only settings do not replace application/tool authorization.

Do not declare the entire app network `internal` and then assume market/provider internet access still works. Design isolated DB/service networks plus deliberate outbound connectivity for ingestion and model calls. Do not allow a model tool arbitrary egress merely because the client needs to reach its provider.

## Initialization, readiness and shutdown

Use a one-shot migration service with one Alembic owner. Migration completion and database health may gate startup, using documented Compose dependency conditions [OPS-01](REFERENCES.md#ops-01). Application code still retries/reconciles transient dependencies; startup ordering is not ongoing availability.

Liveness means a process can respond; readiness includes the dependencies for its role. Runtime model not configured is a capability state, not a reason to falsify overall health. Worker readiness includes current execution lease, data readiness for enabled tasks and ledger reconciliation status.

On shutdown: stop taking new jobs/entries, preserve unresolved work, complete/rollback current transactions, release/expire leases safely, and checkpoint ingestion cursors. After forced kill/power loss, reconcile before resuming. Protect existing positions while the process is running; acknowledge that nothing executes while the PC is asleep/off.

## Resource management

Measure available CPU/RAM/storage and Docker allocation during M0. Bound research concurrency and event retention to avoid starving the market/risk worker. Do not invent minimum hardware requirements or claim the user's machine was inspected. Expose backpressure, queue delay and disk pressure, and pause new work before data integrity is compromised.

## Cleaning up disposable resources

**Address ranges of test runs (OBSERVED 2026-10-08).** The networks of an M6 test run take their address
ranges from the run id. A finished run that has not been cleaned keeps its networks, and a new run whose id
gives the same range cannot create its own: Docker answers "Pool overlaps with other one on this address
space" and the run's first phase that needs a network fails. Clean finished runs by exact name before many
new ones are prepared, or compare a prepared run's `subnet` lines with `docker network inspect` of the
existing test networks first. The harness's `Clean` is refused while another phase holds the lock.

Owner decision of 2026-10-03 ([DECISIONS](../../DECISIONS.md#2026-10-03--docker-test-resources-are-removed-after-each-implementation)): test runs must not build up on the Docker host. On that day the host held more than 500 volumes and about 240 GB, nearly all from finished runs. This section replaces the earlier practice of keeping every run's volumes and images. The implementer decides what matters by the lists below and does not ask for each cleanup.

**What is kept**
- The normal `adaptive-spot-lab` project: its containers, volumes, networks and current images.
- For each of its services, the rollback tag of the latest deployment. While an experiment runs, also the images its workers are pinned to.
- The base and tool images the repository pins.
- Every run's evidence files under `.cache/`: logs, reports, manifests and snapshots. They are files, not Docker resources, and they are the proof of a result.
- Protected backups, under their own rules in [OPERATIONS](OPERATIONS.md).

**What is removed, and when**
- **A finished isolated run:** its containers, networks, volumes and images, once its evidence is recorded. A failed run may stay while its failure is being diagnosed; at most the latest run of a harness is kept that way.
- **At the end of a task,** before its pull request is opened or its completion is reported: every run the task created.
- **After a milestone deployment has been verified:** the rollback tags older than that deployment's, untagged images, and the build cache.

**How**
- **By exact name from the run's own manifest.** Each acceptance harness has a `Clean` phase that removes only the Compose projects of its run. `Stop` still removes nothing, so a stopped run can be inspected first. A harness without a `Clean` phase is cleaned by exact name, as recorded in [COMMANDS](../COMMANDS.md#old-test-run-cleanup--2026-10-03).
- **One name at a time and never forced.** Docker then refuses anything a container still uses.
- **Never with a global prune of volumes or tagged images:** no `docker system prune`, no `docker volume prune`, no `docker image prune -a`, and no pattern that could match the normal project. A volume prune removes the owner's database volume in the moment its container does not exist.
- **Untagged images** with `docker image prune -f`, **the build cache** with `docker buildx prune -f`. Both leave whatever is in use.
- **Timing.** Between HH:15 and HH:55 UTC while an experiment runs, like every heavy operation, and paced when the amount is large.
- **Rollback tags** belong to the normal project. Removing one is a step of a deployment the owner has approved, never a separate action.
- **Record** each cleanup in COMMANDS, with its counts and with what was kept.

## Verification

Build from a clean environment, start the real stack, run migrations, exercise health/auth/empty UI, run tests with the actual browser container, restart services and restore a backup into isolated storage. Verify required ports, secret/mount isolation and graceful shutdown. Report Docker commands that could not run instead of replacing them with an unverified native success claim.

Milestone delivery must also leave the **normal local app** running the accepted release under the [milestone deployment procedure](OPERATIONS.md#milestone-completion-deployment). Reusing a running container without checking its image/source identity is not a deployment. Preserve its database volume/secrets and approved activation state; task cleanup must not stop this normal stack.

## Research services retired (ExecPlan 0035)

IMPLEMENTED on 2026-10-21 ([ExecPlan 0035 §4.3](../plans/0035-a-simpler-app-that-trades-by-itself.md#43-compose-and-the-update-file)). `compose.yaml` no longer defines `research-postgres`, `research-runner`, `research-migrate`, `research-bridge` or `research-admin`, the `research_private` network or the four research secrets, and the update file no longer names the `research` and `research-admin` profiles. Compose calls the containers of a service no longer in the file orphans, warns about them on `up` and leaves them alone, so the update retires them; on the owner's PC it did on 2026-10-21, removing `research-bridge`, `research-runner`, `research-postgres` and the network and keeping the volume (OBSERVED read-only, [ExecPlan 0035 §12](../plans/0035-a-simpler-app-that-trades-by-itself.md#12-progress)).
- **The update's retirement** ([OPERATIONS](OPERATIONS.md#the-update-file-m8)), after every running service runs its built image: each container of a retired service, found by its exact Compose labels (`com.docker.compose.project` and `com.docker.compose.service`), is stopped and removed by its id with `docker container stop` and `docker container rm`, never with `-f`; then the network `<project>_research_private` is removed by its id. Before anything is removed, the network's exact name and Compose's labels on it (`com.docker.compose.project` this project, `com.docker.compose.network` `research_private`) are checked: another project's network of that name stops the update with nothing removed. A refusal stops the update with the main app installed; the next run continues. The check after the update fails while a container or the network of a retired service remains.
- **The tidy step** then removes their images (`<project>-research-runner` and the others), as it removes every image no current service uses; `research-postgres` ran the main database's own PostgreSQL image, which stays.
- **What stays on the PC:** the volume `<project>_research_postgres_data` (deleting data cannot be undone) and the secret files under `secrets/research`, unused. A later update could bring research back from Git history.

The sections below on the research services are their history.

## Agent-driven service isolation

B3 IMPLEMENTED; isolated runtime/configuration checks VERIFIED in `m6-b3b`: the inert `research` profile adds
`research-postgres` and `research-runner`; `research-admin` adds the one-shot
`research-migrate`. All join only internal `research_private`. The runner mounts
only the two research-cluster secrets, under the engine's existing secret paths,
and a read-only named research data volume for filesystem free-space measurement.
The research-only bootstrap generates temporary passwords required by the
unchanged legacy migrations, disables unused identities, and deletes those
temporary files. The runtime probe verified own-cluster connectivity, denied
connectivity to the separate catalog fixture, two secret mounts, UID 10001,
no effective capabilities and a read-only root. Only the new service blocks
were rendered with fixture substitutions; the normal project was never rendered.
It has no main credential, host repository/home mount, Docker socket or public
port. The pinned PostgreSQL image and B0 CPU/memory/PID limits are unchanged.
The runner defaults disabled; profiles, secret generation and activation remain
owner-gated B11 work. No normal Compose command is needed for B3 acceptance.

B4 IMPLEMENTED; isolated runtime/configuration checks VERIFIED on fixture
stacks: the same inert `research` profile adds `research-bridge`
(`python -m app.research.bridge`). It joins `private` and `research_private`
and nothing else, mounts exactly `research_db_password` (`asl_research` on the
main database) and `research_bridge_db_password` (`asl_bridge` on the research
cluster), and mounts no volume: the runner publishes the research filesystem's
free space in the store registry and the bridge reads it there. Both secret files live under the research secret directory; neither is
a main-database, engine or cluster-owner secret. Read-only root, no
capabilities, UID 10001, 0.5 CPU, 256 MiB, 64 PIDs, no published port. With
`ASL_RESEARCH_ENABLED` at its default `0` it opens no connection. The runner
now serves every registered store and creates or drops a store database only
on a request the bridge records in the research cluster; its own Compose block
is unchanged. `research-migrate` also brings every registered store to the
current schema. The harness renders only the four research blocks with fixture
substitutions; the normal project was never rendered. The `research-admin`
service that enables or disables the bridge's main-database identity was
built in B9 (see "M6 identity control and rollout targets" below); until the
owner's activation both identities stay NOLOGIN.

The default tool broker is trusted engine code; it does not require another exposed server. `agent-runner` returns structured requests and receives scoped results, but has no DB, source-fetch proxy or owner-control credentials. Copy only reviewed runtime role templates/schemas into its image; never mount development AGENTS/CLAUDE files, skills, hooks or the repo. M5 realizes this with a separate `agent-worker` (the broker and orchestrator) that reaches the runner over the internal `agent_control` network with a runner key, and an `agent-egress` gateway that is the runner's only route to the provider (see "M5 agent services" below).

M6's `research-runner` receives immutable staged datasets and registered candidate declarations. It joins `research_private` only and has credentials generated for the second research cluster, never the main worker connection string or a route to the main database. The bridge holds `asl_research` for bounded `research_read` views/catalog writes and no engine credential. The fetcher holds `asl_source` for source/evidence rows. Grant and network tests must prove denied main-ledger/approval writes. Artifacts are validated on ingestion; they do not become executable modules or privileged instructions.

Build the controlled M6 research/source services at inert deployment and leave them **not started**, their identities NOLOGIN and flags `0`; starting them is owner-gated M6-B. Agents cannot spawn arbitrary containers and need no Docker socket. Bound CPU/memory/PIDs, job wall time, artifact sizes and concurrency using supported controls checked against the installed runtime [OPS-04](REFERENCES.md#ops-04). Separate data/protection event handling from expensive calculations even though modules share a repository. Demonstrate that saturated research cannot starve protective processing in the supported PC configuration.

Test network reachability, grants, process identity, mount contents, unauthorized native tools and protected auth refresh. Network membership or a container name is not sufficient authorization. No new public host port is required for agent or research services. Do not assume CPU/memory values before measuring the user's PC.

## M3 execution worker and acceptance projects

The logical `worker` is now two services: `market-worker` (M2 public collection, `market` profile) and `execution-worker` (M3 paper execution authority, `execution` profile, `python -m app.execution.worker`). The execution worker uses the engine runtime image, joins only the private database network, holds only `execution_db_password`, runs read-only with tmpfs `/tmp` and 1 CPU / 512 MiB / 128 PIDs, has a heartbeat-file healthcheck and `restart: on-failure` (a disabled worker exits 0 and is not restarted). *Since M4 (ExecPlan 0015) both pilot workers use `restart: unless-stopped` and a disabled worker idles instead of exiting; see [CONFIGURATION](CONFIGURATION.md#m4-settings-execplan-0015).* On the owner installation it is built but **not started**, and its database identity stays NOLOGIN until M4. `tools/m3-acceptance.ps1` creates five isolated projects per run (`engine`, `browser`, `recovery`, `worker`, `replay`) with their own clusters, secrets, `asl_m1_*` databases, loopback ports and `10.252.x` subnets; `tools/m3-replay.ps1` runs modeled replays in its own `asl-replay-<id>` project. Neither script touches the normal `adaptive-spot-lab` project, and `Stop` never removes volumes. The shared helper `tools/lib/Acceptance.psm1` also serves `m2-acceptance.ps1` and `setup-local.ps1` and is Windows PowerShell 5.1 compatible.

## M5 agent services

[ExecPlan 0020](../plans/0020-m5-agent-runtime.md#51-services-and-networks-all-new-pilot-services-untouched) adds only new services, networks, a volume and secrets. The blocks of `postgres`, the pilot services (`market-worker`, `execution-worker`, `evaluation-worker`, `pilot-admin`), the `private` network and `postgres_data` stay unchanged; the deploy script asserts their rendered `docker compose config` hashes.

| Service | Profile | Image and entry point | Networks, volume and secrets | Hardening |
|---|---|---|---|---|
| `agent-worker` | `agents` | Engine runtime, `python -m app.agents.worker`, identity `asl_agent` | `private`, internal `agent_control`; `agent_db_password`, `agent_runner_key` | 0.5 CPU, 512 MiB (256 MiB before [ExecPlan 0052](../plans/0052-backtest-the-ai-trader-on-history.md#43-the-simulated-accounts-code-a-child-process-of-the-agent-worker): the AI backtest's child process `python -m app.backtest_ai.process` runs inside it, no database, network or key), 64 PIDs; read-only root; `unless-stopped`; heartbeat healthcheck |
| `agent-runner` | `agents` | `services/agent-runner` runtime (pinned, digest-checked Codex binary plus a standard-library job server) | internal `agent_control` and `agent_provider`; DNS override so external names do not resolve; volume `codex_home`; `agent_runner_key` | Read-only root; size-limited `noexec,nosuid,nodev` tmpfs `/tmp` and `/jobs`; `cap_drop: ALL`; `no-new-privileges`; `init`; non-root; memory and PID limits; long stop grace period; no published port |
| `agent-egress` | `agents` | `services/agent-runner` egress target (standard-library CONNECT gateway) | internal `agent_provider` plus `model_egress`, the only non-internal agent network | Read-only root; `cap_drop: ALL`; `no-new-privileges`; non-root; limits |
| `agent-auth` | `agent-auth` | Runner image, one-shot device-code login | `agent_provider` only (through the gateway); volume `codex_home` | Run only by the owner through `tools/agent-login.ps1`, which stops the runner first and restarts it afterwards |
| `agent-admin` (removed by ExecPlan 0034) | `agent-admin` | Engine runtime, migration identity, `python -m app.agents.identity` | `private`; `postgres_password`, `agent_db_password` | Only `asl_agent` enable, disable and status, plus the runtime activation request |

- **Build context.** `.dockerignore` excludes `**/AGENTS.md` and `**/CLAUDE.md`, so no authoring instruction file can reach any image; an image test also checks the runner image for them.
- **Mock services.** The mock Responses provider and the fake CLI exist only in the runner's `test` target, which isolated stacks use. The normal installation never builds or starts them.
- **Acceptance projects (M5; the script was removed by ExecPlan 0034).** `tools/m5-acceptance.ps1` created isolated `asl-m5-<run>-<kind>` projects with `asl_m1_` databases and `10.254.x` subnets. Every Compose call passes a per-run env file that sets every pilot and agent flag, and neutralizes `COMPOSE_PROFILES`, so the owner's `.env` is never inherited. Heavy phases run one stack at a time, after a memory preflight, and never between HH:55 and HH:15 UTC. `Stop` never removes volumes.
- **Test containment (after the B3 incident, plan 0020 §15).**
  - The per-run env file pins `ASL_MODEL_EGRESS_INTERNAL=true`, so `model_egress` is `internal` and no isolated container has an Internet route.
  - The test runner and gateway answer to the production names `agent-runner` and `agent-egress` and share `codex_home`. So the production-target runner services never run beside them: the harness removes them before every runner test stack and asserts that they are absent and that the network is internal.
  - RunnerIsolation always removes the production targets it started, and EgressPolicy requires exactly one address behind `agent-egress`.

## M6 source fetcher (ExecPlan 0023, B5)

B5 IMPLEMENTED the `source-fetcher` service; its block is VERIFIED by rendering only that block with fixture substitutions, and a runtime-shaped probe ran in an isolated project ([ExecPlan 0023 §18](../plans/0023-m6-research-investigations.md#18-completion-evidence)). No existing block changed.

| Service | Profile | Image and entry point | Networks and secret | Hardening |
|---|---|---|---|---|
| `source-fetcher` | `sources` | Engine runtime, `python -m app.sources.worker`, identity `asl_source` | `private` and the new `source_egress`; `source_db_password` | 0.5 CPU, 256 MiB, 64 PIDs (the envelope's values); UID 10001; read-only root; `noexec` tmpfs; `cap_drop: ALL`; `no-new-privileges`; heartbeat healthcheck; `unless-stopped`; no port, volume or dependency on `migrate` |

- **Inert by default.** `ASL_SOURCES_ENABLED` defaults to `0`: the process then idles without a database connection or a request. `asl_source` is NOLOGIN and no source version is approved. Starting the service, creating its secret and enabling the identity are owner-gated M6-B steps.
- **The daily coin scan (M10 update 1).** The same process runs the scan of [MARKET_DATA](MARKET_DATA.md#m10-the-daily-coin-scan-execplan-0033) in its own thread under the same switch, identity, network and limits; no service, network, secret or volume is added.
- **`source_egress`** is the fetcher's only route out. `ASL_SOURCE_EGRESS_INTERNAL=true` makes it internal; isolated stacks never give the fetcher an Internet route at all, because their one fixture network is internal.
- **Not added in B5.** The one-shot identity service of §5.1 (`research-admin`) and the activation scripts belong to the bridge and rehearsal batches. `python -m app.sources.identity` enables the identity only in an isolated test database.
- **Deployment note for B10.** Compose needs the file `secrets/source_db_password` to exist before the service is created. The inert deployment creates neither the file nor the service's container; the activation script creates the file first (B9, below).

## M6 identity control and rollout targets (ExecPlan 0023, B9)

B9 IMPLEMENTED one new service, changed one existing M6 block and gave three research services log limits. No block of `postgres`, a pilot service, the `private` network or `postgres_data` changed; the deploy script and the rehearsal compare their rendered configuration with the compose file of `ed9fae3`.

| Service | Profile | Image and entry point | Networks and secrets | Hardening |
|---|---|---|---|---|
| `research-admin` | `research-admin` | Engine runtime, migration identity, `python -m app.research.identity` (`status`, `enable --main`, `disable`, `replace-store --store NAME`) | `private` only; `postgres_password`, `research_db_password`, `source_db_password` | One-shot (`restart: "no"`); read-only root; tmpfs `/tmp`; `cap_drop: ALL`; `no-new-privileges`. It has no route to the research cluster and runs no candidate |

- **`research-migrate`** now also mounts `research_bridge_db_password`, so that `python -m app.research.runner --bridge-identity enable|disable|status` can set `asl_bridge` inside the research cluster. It stays on `research_private` only and holds no main-database secret.
- **Enabling is refused outside its two cases.** `app.research.identity` changes a login only with `--main` on the normal installation, or in an isolated test database, and only at schema `0008_m6_research`.
- **A secret file before its service.** Compose creates a missing secret file as an empty directory when a service that mounts it starts. `research-admin` mounts the research and source secrets, so the activation script creates the files before it runs the service and refuses a secret path that is a directory. The deactivation runs no service that mounts a secret: it changes the identities with `psql` inside the two database containers.
- **Log limits.** `research-postgres`, `research-runner` (and with it `research-migrate`, which inherits its block) and `research-bridge` now use the `json-file` driver with three files of 10 MB, like every other long-running service. They had none, and the runner writes one line a second onto the disk the pilot's database shares.
- **The deploy script's helper containers have limits of their own.** The PostgreSQL that holds the restored copy runs with 1 CPU, 1 GiB and 128 processes on an internal-only network; the containers that migrate, reconcile and downgrade that copy run with 0.5 CPU, 512 MiB and 64 processes. The script removes the helper container, its named volume and its network by name and names anything that is still there afterwards: the volume would hold a full copy of the database. A listing that fails is recorded as `NOT READ`, never as nothing left.
- **One `migrate` image per deployment.** The deploy script builds `migrate` once, for the restore rehearsal, and uses that image by its ID for the copy and for the installation; it is not among the later builds, and the run stops if the name points elsewhere before the migration.
- **The secret scan's second container.** `SecretScan` writes a plain dump of one database at a time into a directory (`asl-m6-scan`) of that database's own data volume and searches it from a one-off container of the run's engine runtime image: `--network none`, `--read-only`, `--cap-drop ALL`, `no-new-privileges`, the user that owns the data directory, 1 CPU and 512 MiB, the data volume and the pattern files mounted read-only. It mounts the volume by its name and not with `--volumes-from`, which would also hand it the database container's secret file. It carries the engine project's label, so `Stop` and `Clean` recognise one that is left. The dump is written only when twice the database's size and 2 GiB are free in the volume's file system, and its directory is removed before the next database. NOT RUN: whether the Docker VM has that room for the largest store of a run, and what the dump and the search cost beside the real pilot, only an observed run can show.
- **Image IDs are not stable across builds on this host.** OBSERVED on 2026-10-06: four builds of the same tree by the deploy script gave four image IDs. Nothing may therefore assume that a rebuilt image has the ID of an earlier build: the scripts compare a container with the image built in the same run, and the rollback images by the `:pre-m6` tags.
- **On the normal installation since 2026-10-08 (B10, OBSERVED).** The images of `source-fetcher`, `research-runner`, `research-migrate`, `research-bridge` and `research-admin` are built, and none of them has a container. The rollback tags of that deployment are `:pre-m6` on `api`, `web`, `agent-worker`, `migrate` and `agent-admin`. After its verification the fifteen older rollback tags of `api`, `web` and `migrate`, the 82 untagged images and the unused build cache were removed as the cleanup section above says. The older tags of the pilot's services were left: that deployment deployed none of them ([COMMANDS](../COMMANDS.md#m6-b10-the-inert-deployment-of-m6-a-to-the-normal-application-2026-10-08)).

**Harness targets on the product Compose file.** The rollout phases act on the product file itself, because the owner's scripts act on it and a mixed state is a state of its services. Four target kinds (`pilot`, `rehearsal`, `saturation`, `regression`) run it under their own project name `asl-m6-<run>-<kind>`, with a per-run env file that pins every flag, fresh per-run secrets, their own `10.253.x` subnets, a loopback web port and `asl_m1_` database names. The owner's `.env`, secrets and volumes are never read, and no command names the normal `adaptive-spot-lab` project. The pre-M6 images are read by image ID only. `Clean` removes these projects' containers, networks and volumes by name, and every image name that begins with the project's name; it never forces a removal, so an image another name or container still uses stays.

**Three things the rollout phases add beside the Compose services.** Each is named in the phase record. The first carries the project label, so `Stop` and `Clean` find it; the second is a database session and ends with its container at the latest; the third is removed by the script that made it.
- **A market worker stand-in.** No isolated stack runs a market worker. `docker run` starts one container named `<project>-market-worker-1`, labeled as the `market-worker` service, on the pilot's market image (by image ID) with its entry point replaced by a sleep: on the private network only, read-only, 0.25 CPU and 64 MiB, opening no connection. The owner scripts then see a container of that service and must leave it as it is.
- **A blocking session.** The rehearsal starts `psql` inside the project's own postgres container holding `ACCESS SHARE` on `agent_workflows` for at most fifteen minutes, and ends it by its application name. It blocks only the first statement of migration 0008.
- **The deploy script's restore helper.** One PostgreSQL container, one internal-only network and one named volume `asl-m6-restore-<id>-data`, all removed by name when the rehearsal of the restore ends, also when it fails. The rehearsal checks that none is left.

## ExecPlan 0049: the agents' provider keys

[ExecPlan 0049 §5.1–§5.2](../plans/0049-choose-the-agents-provider-and-see-usage.md#51-four-adapters-in-one-runner). `compose.yaml`:
- **`agent-runner`** also mounts the volume **`agent_keys`** at `/agent-keys` (the owner's keys and token, one file per provider; no other service mounts it: the isolated `agent-runner-test` mounts its own `agent_keys_test` instead, for the scratch keys of the credential tests) and holds the secret **`agent_credentials_key`** for its credential routes. Its image carries the pinned Claude Code CLI `2.1.308` again (digest-checked as in M11's update 1) beside the Codex binary.
- **`api`** joins the internal `agent_control` network and holds `agent_credentials_key`, so it can forward a key the owner saves to the runner and read the keys' states; it never mounts `agent_keys`. The agent worker does not hold this secret.
- **`agent-egress`** listens once per provider (3128 Codex, 3129 Claude CLI, 3130 Claude API, 3131 OpenAI API), each allowed only its vendor's hosts (`EGRESS_ALLOWLIST_V3`).
- **`agent-test-client`** (isolated stacks only) holds `agent_credentials_key` for the credential tests.
- **Secrets.** `tools/setup-local.ps1` creates `secrets/agent_credentials_key` only if missing; `tools/update.ps1` runs it when the env file names no other secret directory, so the update creates the new file itself. NOT RUN: the image builds and the update, which need the PC's Docker.

