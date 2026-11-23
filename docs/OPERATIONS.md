# Operations, scheduling and recovery

How the spot app runs, updates and recovers on the owner's PC ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12; [ExecPlan 0061](plans/0061-clean-up-after-the-spot-switch.md)). The operations of M2 to M11 (M2's market recovery and incident codes, the experiments' states, the agents' workflows, the futures' clean start) are in the [archived copy](archive/contracts/OPERATIONS.md), history only.

## Local operating reality

The execution worker must run for the account to be valued, protected and traded. Closing the browser does not stop it; stopping Docker, the PC's sleep, a power loss or a lost internet connection does. The app offers no unattended cloud availability, and nothing executes while the PC is off: the next step afterwards starts from the stored state, never from a replay of the missed time.

The authoritative schedule is the execution worker's step and the database's records, never a browser timer, a request handler or a model.

## Cadence

| What | When |
|---|---|
| The market feed | The book each second, the 1-minute candle as it changes, a REST catch-up at the start and every five minutes, each new final day 90 s after UTC midnight, the clock every minute, the instrument hourly ([MARKET_DATA](MARKET_DATA.md)) |
| The engine's step | Every second, under the execution lease ([ARCHITECTURE](ARCHITECTURE.md#exact-authority-sequence)) |
| Valuations | Every 60 s while Bitcoin is held, hourly otherwise, and at each fill, top-up, latch, stop and new high |
| The day's reference | The first valid valuation after UTC midnight: `TIMELY` within five minutes, else `LATE_CONSERVATIVE` |
| The rule's reading | Once a UTC day, at the first step at or after 00:05 UTC once the day's final candle is stored, again every 15 minutes while the day is not spent |
| Reconciliation | Every five minutes, and at the worker's and the API's start |
| The backtest | After the install, and after each new final day, beside the step |

A missed reading is recorded as late or refused with its reason, never backdated. Each schedule is idempotent: a restarted worker does not read a day twice or post a fill twice.

## Run state

A run is `RUNNING`, `PAUSED` (with one or more causes among `OWNER`, `DAILY_LOSS`, `DRAWDOWN` and `INTEGRITY`), `STOPPING` or `STOPPED`. Each cause is cleared on its own: the owner's Resume clears `OWNER`, a new UTC day `DAILY_LOSS`, a passing reconciliation `INTEGRITY`; `DRAWDOWN` stops the run. A paused run never buys and still sells; a stopping run sells everything it can at the book, then stops. Stop and sell is the owner's way to stop at once; after a stop, only the owner's Start begins a new run ([AUTONOMY_MATRIX](AUTONOMY_MATRIX.md#execplan-0060-spot-trading-only-m12)).

## Recovery sequence

- **The feed.** The market worker reconnects by itself and catches up the final candles it lacks through REST; the books of the missing seconds are not invented, and the engine refuses a trade until a fresh book, a verified clock and a checked instrument are there again. A stale book shows on the Cockpit and in Settings' health.
- **The engine.** On start the worker takes the lease with a new epoch, reconciles the account and resumes from the stored run, latches and readings. A failed step rolls back whole, is recorded, and the worker backs off and recovers from the database; it never retries the same step blindly. An unknown outcome of an owner request is read back by its key.
- **The API.** At its start it reconciles the account and contributes the starting 10,000 USDT if the account has none. A mismatch sets the integrity hold (`reconciliation_failed` and `paused`); start-up never rewrites a projection.
- **A restore.** The pages notice a ledger older than their cursor and start again; the engine reconciles before it trades.

No historical replay is ever posted into the forward ledger to conceal downtime.

## Milestone completion deployment

**Since M8 ([ExecPlan 0031 §4.4](archive/plans/0031-m8-simple-app-that-runs-itself.md)), every update is one double-click:** [the update file](#the-update-file-m8). A planning request or an explicit owner hold does not trigger an update; a finished, checked part of an approved plan does ([AGENTS](../AGENTS.md) rule 14).
1. The change is merged to `main` with its checks recorded in its plan; only then does the owner double-click `update-app.cmd`, the double-click being the owner's consent to that update.
2. The update file preserves the database and secrets, backs up, applies forward migrations, recreates the changed services and verifies the running source and images, readiness, reconciliation and the pages. It never uses `down -v`, resets the owner's state or enables anything that was off.
3. The thread then checks the install itself, read-only, on the PC: the folder at `main`, the update's record, the services and the pages. A deployment test changes nothing that is the owner's (top-ups, Pause, Stop and sell, Start).
4. If the app cannot be updated or verified, the update is reported blocked, and the part is not described as delivered.

### The update file (M8)

`update-app.cmd` in the owner's main folder (a copy of `tools/update.cmd`, ignored by Git) runs `tools/update.ps1` as GitHub's `main` holds it, with Windows PowerShell 5.1, on that folder. The owner double-clicks it; it asks nothing and the window stays open at the end. It enables no identity, sets no flag and approves nothing.
1. **The folder.** With an uncommitted change to a tracked file it stops and names the files, changing nothing. Otherwise it puts the folder on `main` and fast-forwards it to `origin/main`; a local `main` with commits GitHub lacks stops it. When the fast-forward brought a newer copy of the update file, that copy runs instead.
2. **Preflight** (read-only): Docker, the env file, postgres, api and web running and the api ready, the schema, and each running service's `ASL_*_ENABLED` flags equal to what the env file renders.
3. **Backup and rollback tags.** A protected backup of the main database with its SHA-256 (refused without room for it), and `<project>-<service>:before-update` tags on the images that run. After a run that stopped once it had set its tags, those tags are kept, since they still name the release before it. A secret file `compose.yaml` names that the folder lacks is created first, as `tools/setup-local.ps1` creates it.
4. **Build** every image of the app (never postgres; the test services are not built).
5. **Migrate** the main database to the head of the built code (`python -m app.migrate <head>`, bounded attempts). When the new api accepts the schema that is there (it asks the built code's `app.db.ACCEPTED_REVISIONS`), the api and then the web are replaced first; otherwise the two workers that write every second stop, each in its container, the migration runs, and a migration that does not apply starts them again by their ids (`docker start`; Compose's `start` refuses a service whose one-shot `migrate` dependency has no container). The api always comes before the web, whose health check reads the api ([ExecPlan 0042 §13](archive/plans/0042-no-owner-sign-in.md#13-progress)). Services a stopped run's migration left stopped count as running for the next run and are recreated.
6. **Recreate** each running service whose image or settings changed (Compose's `config --hash` against the container's `com.docker.compose.config-hash` label), with `--no-deps` and its flags unchanged; services that do not run stay stopped. A recreated execution worker with `ASL_EXECUTION_ENABLED=1` must hold its lease.
7. **Verify:** the folder still at `origin/main`, each running service on its built image, the api ready, the schema at the head, reconciliation `OK`, and the pages `/`, `/trades`, `/backtest` and `/settings` answering 200. Then a read-out that never stops the update: Bitcoin's spot feed and its daily history, the spot account, its run, the rule's newest reading, the backtest and the futures app's records kept in the archive.
8. **Record** `update.json` beside the backup (`update-failed.json` after a stop) and print the release notes of the merges since the last completed update.
9. **Tidy:** delete each branch that `main` contains through a merge (never `main`, never a branch that only points into `main`'s own history, never one with commits `main` lacks) on GitHub, with a lease on the tip it checked, and in the folder, then list local branches with unmerged work. Delete the database backups older than the newest three (never this run's, nor those of runs that stopped since the last completed one, nor the copy in `before-futures/`, which is the owner's to delete), and remove this app's images that no current service uses, by exact name, never forced ([ExecPlan 0034](archive/plans/0034-app-cleanup.md)). A failure here is reported; the update is done by then.

**The quiet time.** Before each change it waits by itself while the clock is near the day's reference and the rule's reading: a change begins at or after 00:10 UTC and must end, with its declared minutes, before 23:55 UTC ([ExecPlan 0061 §4.2](plans/0061-clean-up-after-the-spot-switch.md#42-the-update-file)); until ExecPlan 0061 it waited near every hour (HH:55 to HH:05 UTC), which served M3's hourly bars and the futures' 15-minute decisions. It keeps the PC awake while it runs. Any failed step stops the run where it is, records `FAILED`, and prints what it replaced, the schema, the backup and the record; nothing reports success after a failed step. A stopped update is fixed forward: the fix comes as a new update, and the next run continues from what is installed. Its transcript is `update-<time>.log` under the backup root (`.cache/deployments`).

**Its model test.** `tools/m8/update-model.ps1` runs the update file against a fake Docker and Git on a model of the spot app (schema `0041_spot`, the four app services, a hypothetical contract migration `0042_model` for the stop-and-restart scenarios), in a temporary clone on the owner's PC through a Remote Control session, since the cloud cannot run Windows PowerShell ([COMMANDS](COMMANDS.md)).

**What ExecPlan 0061 removed** from the update file, with its model's scenarios: the futures account's preflight before migration `0041`, the futures app's clean start of [ExecPlan 0039 §5.1](archive/plans/0039-bitcoin-futures-on-paper.md#51-a-clean-start) with its undo and `app.migrate --keep-logins`, the stop and removal of the retired services' containers and networks, and the Claude sign-in's starter. Their description is in the [archived copy](archive/contracts/OPERATIONS.md#the-update-file-m8).

### The Docker clean-up (ExecPlan 0034)

`docker-cleanup.cmd` in the owner's main folder (a copy of `tools/docker-cleanup.cmd`, ignored by Git) runs `tools/docker-cleanup.ps1` as GitHub's `main` holds it. Windows asks once for administrator rights before anything changes. It waits by itself outside the quiet time (10 minutes' room before the backup, an hour before Docker stops), backs up the database, removes this app's images that no current service uses and two leftover test volumes (by exact name, never `-f`, never a prune), trims and compacts Docker's data disk with Docker Desktop stopped (the app is down meanwhile), starts Docker again and waits for the app's containers, then deletes database dumps older than the newest three and the old PC test-run folders. `-DryRun` lists all of it and changes nothing. Other projects' Docker resources and the build cache are left alone. Details: [ExecPlan 0034 §4.1](archive/plans/0034-app-cleanup.md#41-part-1-the-docker-clean-up-file).

## Monitoring and incident record

Settings' health and the Cockpit's status show the feed (the book's age, the clock, the daily history), the execution worker (its heartbeat and lease), the database's schema, reconciliation, the run's state and causes, and the app's version, with measured values and no fake green. A refused trade, a late reading, a latch and a reconciliation failure are records with their times and reasons. Alerts live in the local UI and logs; external notifications would need an approved plan.

## Backup and restore

Each update and each Docker clean-up takes a protected `pg_dump -Fc` of the main database with its SHA-256, outside the database volume under `.cache/deployments`, and keeps the newest three (the copy in `before-futures/` is never deleted by the tools). Secrets are not in the dump. A restore goes into a **new** database (`createdb`, `pg_restore`), never over the owner's running one, and is checked by reconciliation and the account's totals before it is used. M1's rehearsal of 2026-09-27 matched source and restore on every account total ([archived copy](archive/contracts/OPERATIONS.md#backup-and-restore)). A backup that lives only on the same PC is not a full backup strategy; changing or deleting volumes needs the owner's explicit word.

## Upgrade and future hosting

Before an upgrade: a backup, the schema, library and skill changes reviewed, the checks run and the version change recorded. Hosting elsewhere would need a new deployment, authentication, TLS, monitoring and resource plan. Real Binance execution is a separately authorized project with new keys, permissions, risk and testing, not a configuration flip in this release.
