"""Bounded migration retry. A lock failure rolls back the whole attempt: a lock not granted within the migration's
``lock_timeout`` (55P03), or a deadlock PostgreSQL broke by ending the migration's transaction (40P01). Migration
0041 (ExecPlan 0060) moves tables a running service may still be reading; the update stops the writers first, and a
reader the deadlock check picks costs the migration one attempt.

This operator path grants no login or activation; the update runs it as ``python -m app.migrate`` (``app.research.migrate``
until ExecPlan 0060 removed the research package).
"""

import argparse
import time
from collections.abc import Callable
from typing import Any

from alembic.config import Config
from sqlalchemy.exc import DBAPIError

from alembic import command

# What another session can make an attempt fail with: lock_not_available and deadlock_detected.
RETRIED = frozenset({"55P03", "40P01"})


def bounded(attempt: Callable[[], Any], attempts: int) -> tuple[int, Any]:
    """How many attempts it took, and what the last one returned."""
    for number in range(attempts):
        try:
            return number + 1, attempt()
        except DBAPIError as error:
            if getattr(error.orig, "sqlstate", None) not in RETRIED or number + 1 == attempts:
                raise
            time.sleep(0.1 * (number + 1))
    raise RuntimeError("migration_attempts_exhausted")


def run(target: str = "head", *, attempts: int = 5) -> int:
    return bounded(lambda: command.upgrade(Config("alembic.ini"), target), attempts)[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default="head")
    args = parser.parse_args()
    count = run(args.target)
    print(f"VERIFIED: migration completed in {count} bounded attempt(s).", flush=True)
