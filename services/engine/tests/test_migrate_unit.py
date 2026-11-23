"""``app.migrate.bounded`` (ExecPlan 0060): an attempt that fails because of another session, a lock not granted in
time (55P03) or a deadlock PostgreSQL broke (40P01), is tried again up to the bound; any other database error, and the
last attempt's, is raised. No database: the errors are SYNTHETIC."""

import pytest
from sqlalchemy.exc import DBAPIError

from app import migrate


class Failure(Exception):
    def __init__(self, sqlstate: str | None):
        super().__init__(sqlstate)
        self.sqlstate = sqlstate


def attempts(*states: str | None):
    """An attempt that fails with each state in turn, then returns "done"; and the list of its calls."""
    calls: list[int] = []

    def attempt() -> str:
        calls.append(len(calls) + 1)
        if len(calls) <= len(states):
            raise DBAPIError("ALTER TABLE ...", {}, Failure(states[len(calls) - 1]))
        return "done"

    return attempt, calls


@pytest.fixture
def slept(monkeypatch) -> list[float]:
    found: list[float] = []
    monkeypatch.setattr(migrate.time, "sleep", found.append)
    return found


def test_a_lock_timeout_and_a_deadlock_are_tried_again(slept):
    attempt, calls = attempts("55P03", "40P01")
    assert migrate.bounded(attempt, 5) == (3, "done")
    assert calls == [1, 2, 3] and slept == [0.1, 0.2]


def test_any_other_failure_is_raised_at_once(slept):
    for state in ("23505", "42P01", None):
        attempt, calls = attempts(state)
        with pytest.raises(DBAPIError) as raised:
            migrate.bounded(attempt, 5)
        assert raised.value.orig.sqlstate == state and calls == [1]
    assert slept == []


def test_the_last_attempt_s_failure_is_raised(slept):
    attempt, calls = attempts("40P01", "55P03", "40P01")
    with pytest.raises(DBAPIError) as raised:
        migrate.bounded(attempt, 3)
    assert raised.value.orig.sqlstate == "40P01" and calls == [1, 2, 3] and slept == [0.1, 0.2]
