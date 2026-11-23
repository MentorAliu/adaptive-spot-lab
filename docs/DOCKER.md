# Docker-first local deployment

How the spot app runs in Docker on the owner's PC ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12; [ExecPlan 0061](plans/0061-clean-up-after-the-spot-switch.md)). The services, harnesses and isolation rules of M2 to M11 that went (the acceptance projects, the research cluster, the agents' runner, egress and sign-in, the source fetcher, the evaluation worker) are in the [archived copy](archive/contracts/DOCKER.md), history only. Commands are in [COMMANDS](COMMANDS.md), the update in [OPERATIONS](OPERATIONS.md#the-update-file-m8).

## The services

IMPLEMENTED in [`compose.yaml`](../compose.yaml); OBSERVED on the owner's PC since the update of 2026-11-12 ([ExecPlan 0060 §14](plans/0060-spot-trading-only.md#14-progress)). `docker compose config` is NOT RUN in the cloud (no Docker there).

| Service | Runs | Networks | Secrets |
|---|---|---|---|
| `postgres` | PostgreSQL, the volume `postgres_data` | `private` | `postgres_password` |
| `migrate` | One-shot Alembic upgrade to head; the update runs it as `python -m app.migrate <head>` (bounded retries on a lock) | `private` | `postgres_password`, `api_db_password`, `market_worker_password` |
| `api` | `uvicorn app.main:app` (`--timeout-graceful-shutdown 3`) | `private` | `api_db_password`, `api_internal_key` |
| `market-worker` | `python -m app.spot_market.worker` (profile `market`) | `private`, `market_egress` | `market_worker_password` |
| `execution-worker` | `python -m app.execution.worker` (profile `execution`), a heartbeat-file health check | `private` | `execution_db_password` |
| `web` | The TanStack Start server, published on `127.0.0.1:${WEB_PORT:-3000}` only | `frontend`, `private` | `api_internal_key` |

Tool and test profiles: `web-tools` and `engine-tools` (no network) and `engine-tests` (the engine's pytest against a database, `private` only); none runs with the app. `private` is internal; only the market worker reaches the internet, through `market_egress`. The workers use `restart: unless-stopped`, a read-only root filesystem with a temporary `/tmp`, and 1 CPU, 512 MiB and 128 PIDs; a disabled worker idles instead of exiting ([CONFIGURATION](CONFIGURATION.md)).

The services ExecPlan 0060 retired (`agent-worker`, `agent-runner`, `agent-egress`, `agent-auth`, `source-fetcher`, `evaluation-worker` and the agents' test services, with their networks) are gone from `compose.yaml`; the update of 2026-11-12 removed their containers and networks (none was left, `OBSERVED` in its record), and since ExecPlan 0061 the update file no longer handles them. Their volumes and secret files on the PC stay, read by nothing. ExecPlan 0061 also removed `browser-tests`, whose Dockerfile no commit holds: the browser suites run in the cloud ([COMMANDS](COMMANDS.md#browser-suites-cloud)).

## Build and development

Multi-stage images, pinned runtimes, locked dependencies (`uv.lock`, `pnpm-lock.yaml`) and nonroot final processes; production images hold only what they run. TanStack Start's actual build output and official hosting guidance [TS-02](REFERENCES.md#ts-02), and FastAPI's container guidance [BE-01](REFERENCES.md#be-01), are verified against the installed versions, not assumed. Test databases and data are distinct from the app's history. Never run a destructive reset or `down -v` against the owner's data.

## Networks, storage and secrets

Only the web is published, on `127.0.0.1`, explicitly bound [OPS-03](REFERENCES.md#ops-03); the API and PostgreSQL are private services, not host or LAN endpoints, and the web validates Host and Origin. The database lives in the volume `postgres_data`. Secrets are service-scoped Compose secrets [OPS-02](REFERENCES.md#ops-02), each given only to the services that need it. No privileged container, host PID namespace, host home or repository mount, or Docker socket in a runtime service; read-only root filesystems where supported, with explicit writable locations. Nonroot and read-only settings do not replace the application's authorization.

## Initialization, readiness and shutdown

The one-shot migration service is the only Alembic owner; the update runs it before it recreates the services. Compose's dependency conditions gate start-up [OPS-01](REFERENCES.md#ops-01); the code still retries and reconciles transient dependencies. Liveness means the process answers; readiness includes the schema the code was built for, and for the execution worker its lease and reconciliation. On shutdown the workers stop taking new steps, finish or roll back the current transaction and let the lease lapse; after a forced kill or a power loss the engine reconciles before it trades again. Nothing executes while the PC is asleep or off.

## Resource management

The workers' limits protect the one-second step; the backtest runs beside it in its own transactions. The market data's retention (books 2 days, minutes 30 days, daily candles kept) bounds the database's growth ([MARKET_DATA](MARKET_DATA.md)). Disk pressure and lag are shown on the Settings page's health, not hidden.

## Cleaning up disposable resources

Owner decision of 2026-10-03 ([DECISIONS](DECISIONS.md#2026-10-03--docker-test-resources-are-removed-after-each-implementation)): test runs must not build up on the Docker host. On that day the host held more than 500 volumes and about 240 GB, nearly all from finished runs. This section replaces the earlier practice of keeping every run's volumes and images. The implementer decides what matters by the lists below and does not ask for each cleanup.

**What is kept**
- The normal `adaptive-spot-lab` project: its containers, volumes, networks and current images.
- For each of its services, the rollback tag of the latest update (`:before-update`).
- The base and tool images the repository pins.
- Every run's evidence files under `.cache/`: logs, reports, manifests and snapshots. They are files, not Docker resources, and they are the proof of a result.
- Protected backups, under their own rules in [OPERATIONS](OPERATIONS.md).

**What is removed, and when**
- **A finished isolated run:** its containers, networks, volumes and images, once its evidence is recorded. A failed run may stay while its failure is being diagnosed; at most the latest run of a harness is kept that way.
- **At the end of a task,** before its pull request is opened or its completion is reported: every run the task created.
- **After a milestone deployment has been verified:** the rollback tags older than that deployment's, untagged images, and the build cache.

**How**
- **By exact name.** A cloud session removes its scratch databases, clusters, servers and files by the names it created; on the PC the Docker clean-up (`docker-cleanup.cmd`, `tools/docker-cleanup.ps1`) removes this app's own leftovers, each by exact name or id. The PC's old test harnesses and their records are history ([COMMANDS](archive/COMMANDS.md#old-test-run-cleanup--2026-10-03)).
- **One name at a time and never forced.** Docker then refuses anything a container still uses.
- **Never with a global prune of volumes or tagged images:** no `docker system prune`, no `docker volume prune`, no `docker image prune -a`, and no pattern that could match the normal project. A volume prune removes the owner's database volume in the moment its container does not exist.
- **Untagged images** with `docker image prune -f`, **the build cache** with `docker buildx prune -f`. Both leave whatever is in use.
- **Timing.** Never across the day's reference and the rule's reading (23:55 to 00:10 UTC): the update file and the Docker clean-up wait by themselves until their step fits outside that window ([ExecPlan 0061 §4.2](plans/0061-clean-up-after-the-spot-switch.md#42-the-update-file)), and a large amount is paced.
- **Rollback tags** belong to the normal project. Removing one is a step of an update the owner started, never a separate action.
- **Record** each cleanup in COMMANDS, with its counts and with what was kept.

## Verification

Build from a clean environment, start the real stack, run migrations, exercise health/auth/empty UI, run tests with the actual browser container, restart services and restore a backup into isolated storage. Verify required ports, secret/mount isolation and graceful shutdown. Report Docker commands that could not run instead of replacing them with an unverified native success claim.

Milestone delivery must also leave the **normal local app** running the accepted release under the [milestone deployment procedure](OPERATIONS.md#milestone-completion-deployment). Reusing a running container without checking its image/source identity is not a deployment. Preserve its database volume and secrets; task cleanup must not stop this normal stack.

