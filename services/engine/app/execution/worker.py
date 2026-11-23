"""The execution worker: the single fenced authority over the main account (ExecPlan 0060: its spot account).

Disabled unless ``ASL_EXECUTION_ENABLED=1``: a disabled worker idles (so the ``unless-stopped`` restart policy does not
loop it) and never connects. Enabled, it runs ``app.spot.worker.SpotWorker``: it takes the 10 s execution lease, renews
it every 2 s on a separate connection (``LeaseKeeper``) and stops issuing work once its last successful renewal is
more than 7 s old. It has no network route beyond the private database network.
"""

import json
import logging
import os
import signal
import threading
import time
from pathlib import Path
from typing import Any

from sqlalchemy.engine import Engine

from app.db import get_engine
from app.execution import store

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("asl.execution_worker")
HEARTBEAT = Path(os.environ.get("ASL_EXECUTION_HEARTBEAT", "/tmp/execution-heartbeat.json"))
RECONCILE_SECONDS = 300.0
MAX_BACKOFF_SECONDS = 60.0
RENEW_SECONDS = 2.0
AUTHORITY_MAX_AGE_SECONDS = 7.0


def log(event: str, **fields: Any) -> None:
    logger.info(json.dumps({"event": event, **fields}, separators=(",", ":"), default=str))


def beat(state: str, **fields: Any) -> None:
    try:
        HEARTBEAT.write_text(json.dumps({"at": time.time(), "state": state, **fields}, default=str))
    except OSError:
        pass


class LeaseKeeper(threading.Thread):
    """Renews the lease on its own connection; records the last successful renewal."""

    def __init__(self, db: Engine, owner_id, epoch: int):
        super().__init__(daemon=True)
        self.db, self.owner_id, self.epoch = db, owner_id, epoch
        self.last_ok = time.monotonic()
        self.lost = threading.Event()
        self.stopped = threading.Event()

    def run(self) -> None:
        while not self.stopped.wait(RENEW_SECONDS):
            try:
                if store.renew_lease(self.owner_id, self.epoch, self.db):
                    self.last_ok = time.monotonic()
                else:
                    self.lost.set()
                    return
            except Exception as exc:  # database unavailable: authority ages out
                log("lease_renewal_failed", error=type(exc).__name__)
            if time.monotonic() - self.last_ok > AUTHORITY_MAX_AGE_SECONDS:
                self.lost.set()
                return

    def valid(self) -> bool:
        return not self.lost.is_set() and time.monotonic() - self.last_ok <= AUTHORITY_MAX_AGE_SECONDS


def idle_disabled(stop: threading.Event) -> None:
    """A disabled worker stays up without a database connection (restart policy unless-stopped)."""
    log("execution_worker_disabled")
    while not stop.wait(5.0):
        beat("DISABLED")  # the container healthcheck accepts heartbeats up to 15 s old
    beat("STOPPED")


def main() -> None:
    stop = threading.Event()
    for signame in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signame, lambda *_: stop.set())
    if os.environ.get("ASL_EXECUTION_ENABLED") != "1":
        beat("DISABLED")
        idle_disabled(stop)
        return
    from app.spot.worker import SpotWorker

    SpotWorker(get_engine(), stop).serve()


if __name__ == "__main__":
    main()
