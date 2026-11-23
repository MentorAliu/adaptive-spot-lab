"""The execution worker's spot account (ExecPlan 0060 section 4.4).

One fenced authority: the worker takes the execution lease, renews it every 2 s on its own connection
(``app.execution.worker.LeaseKeeper``) and stops issuing work once its last renewal is more than 7 s old. Under it, a
step every second (``SpotEngine.step``) and a reconciliation every 5 minutes. A failed step rolled back entirely; it is
recorded and not retried as it was: the worker backs off, lets the lease lapse and recovers from the database.

After each committed step that changed something a page shows, the worker announces it (``app.spot.live``) in a
transaction of its own; a failed announcement is logged and lost.

Beside the steps, while it holds the lease, a thread computes the rule's backtest (``app.spot.backtest``) once the
feed's daily history is complete and again after each new final day: about two seconds of work a day, in transactions
of its own, never inside a step. Its failure is logged and tried again a minute later.
"""

import threading
import time
from datetime import datetime
from uuid import uuid4

from sqlalchemy.engine import Engine

from app import code_identity
from app.execution import store
from app.execution.worker import MAX_BACKOFF_SECONDS, RECONCILE_SECONDS, LeaseKeeper, beat, log
from app.spot import backtest, live
from app.spot.engine import SpotEngine

STEP_SECONDS = 1.0
BACKTEST_EVERY_SECONDS = 60.0
BACKTEST_LOG_EVERY = 60


class Backtests(threading.Thread):
    """The backtest's computations, while the worker holds the lease."""

    def __init__(self, db: Engine, stop: threading.Event, leased: threading.Event, announce: live.Announcer):
        super().__init__(daemon=True, name="spot-backtests")
        self.db, self.stop, self.leased, self.announce = db, stop, leased, announce
        self.failures = 0

    def run(self) -> None:
        while not self.stop.is_set():
            if self.leased.is_set():
                self.once()
                self.stop.wait(BACKTEST_EVERY_SECONDS)
            else:
                self.stop.wait(5.0)

    def once(self) -> None:
        began = time.monotonic()
        try:
            stored = backtest.compute_and_store(self.db, code_identity.current(), lambda: store.db_now(self.db))
        except Exception as exc:  # tried again a minute later; the steps go on
            self.failures += 1
            if self.failures % BACKTEST_LOG_EVERY == 1:
                log("spot_backtest_failed", error=type(exc).__name__, detail=str(exc)[:200],
                    consecutive=self.failures)
            return
        self.failures = 0
        if stored is not None:
            log("spot_backtest_stored", backtest=str(stored), duration_ms=round((time.monotonic() - began) * 1000))
            self.announce("spot", ["BACKTEST"])


class SpotWorker:
    def __init__(self, db: Engine, stop: threading.Event):
        self.db, self.stop = db, stop
        self.owner_id = uuid4()
        self.failures = 0
        self.engine: SpotEngine | None = None
        self.announce = live.Announcer(db, log)
        self.leased = threading.Event()
        self.backtests = Backtests(db, stop, self.leased, self.announce)

    def now(self) -> datetime:
        return store.db_now(self.db)

    def serve(self) -> None:
        log("spot_worker_started")
        self.backtests.start()
        while not self.stop.is_set():
            try:
                epoch = store.acquire_lease(self.owner_id, self.db)
            except Exception as exc:
                log("lease_acquire_failed", error=type(exc).__name__)
                epoch = None
            if epoch is None:
                beat("STANDBY", engine="SPOT")
                self.stop.wait(1.0)
                continue
            keeper = LeaseKeeper(self.db, self.owner_id, epoch)
            keeper.start()
            log("execution_lease_acquired", epoch=epoch, engine="SPOT")
            try:
                self.run_epoch(epoch, keeper)
                self.failures = 0
            except store.LostAuthority as exc:
                log("execution_authority_lost", epoch=epoch, reason=str(exc))
            except Exception as exc:  # the step rolled back entirely
                self.failures += 1
                log("spot_step_failed", epoch=epoch, error=type(exc).__name__, detail=str(exc)[:200],
                    consecutive=self.failures)
                try:
                    if self.engine is not None:
                        self.engine.record_failure(self.now(), type(exc).__name__, str(exc))
                except Exception as record_exc:
                    log("execution_incident_unrecorded", error=type(record_exc).__name__)
                self.stop.wait(min(MAX_BACKOFF_SECONDS, 2.0 ** self.failures))
            finally:
                self.leased.clear()
                keeper.stopped.set()
        beat("STOPPED", engine="SPOT")

    def run_epoch(self, epoch: int, keeper: LeaseKeeper) -> None:
        self.engine = None
        engine = SpotEngine(self.db, self.owner_id, epoch)
        engine.start()
        self.engine = engine
        result = engine.recover(self.now())
        log("spot_recovered", epoch=epoch, reconciliation=result["status"], failed_checks=result["failed_checks"])
        self.announce("spot", ["RECOVERED"])
        self.leased.set()
        reconciled_at = time.monotonic()
        while not self.stop.is_set():
            if not keeper.valid():
                raise store.LostAuthority("lease_renewal_stale")
            if time.monotonic() - reconciled_at >= RECONCILE_SECONDS:
                result = engine.reconcile(self.now())
                reconciled_at = time.monotonic()
                if result["status"] != "OK":
                    log("execution_reconciliation_failed", epoch=epoch, failed_checks=result["failed_checks"])
            began = time.monotonic()
            effects = engine.step()
            changed = live.changes(effects)
            if changed:
                log("spot_step", epoch=epoch, effects=effects,
                    duration_ms=round((time.monotonic() - began) * 1000, 1))
                self.announce("spot", changed)
            beat("ACTIVE", engine="SPOT", epoch=epoch)
            self.stop.wait(max(0.0, STEP_SECONDS - (time.monotonic() - began)))
        self.leased.clear()
        if keeper.valid():
            store.release_lease(self.owner_id, epoch, self.db)
            log("execution_lease_released", epoch=epoch, engine="SPOT")
