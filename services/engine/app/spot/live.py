"""Live trades (ExecPlan 0047, kept for spot by ExecPlan 0060): the execution worker announces each committed change on a
PostgreSQL channel, the API's listener wakes the browsers' event streams, and each stream reads the toasts' feed (the
spot fills) again.

A notification names the change's source and kinds, never a value: every number a page shows still comes from the
engine's reads. PostgreSQL delivers a notification only when its transaction commits, and fails a transaction at
commit when the notification queue is full, so the worker announces in a transaction of its own after the step's: a
lost announcement costs at most the listener's sweep, and an announcement can never fail a trade.
"""

import asyncio
import json
import logging
import re
from collections.abc import AsyncIterator, Awaitable, Callable, Iterable
from typing import Any

import psycopg
from fastapi.sse import ServerSentEvent
from sqlalchemy import text
from sqlalchemy.engine import Engine

CHANNEL = "asl_spot_live"
SOURCES = frozenset({"spot"})
# A valuation changes nothing the stream tells: the Cockpit reads the book every 2 s.
QUIET = frozenset({"VALUATION"})
# The effects that post the ledger: the toasts' feed has new entries.
LEDGER = frozenset({"FILL"})
KIND = re.compile(r"^[A-Z][A-Z_]{0,39}$")
PAYLOAD_MAX = 1000
LOG_EVERY = 60
# Without a notification the streams read again every 30 s, which shows a lost announcement.
SWEEP_SECONDS = 30.0
PING_TIMEOUT_SECONDS = 5.0
RETRY_SECONDS = (1.0, 2.0, 4.0, 8.0, 16.0, 30.0)
STREAMS_MAX = 8
# The browser's wait before it reconnects a stream that ended (the event stream's `retry` field).
RECONNECT_MS = 3000

# The API sets this logger up with the request log's format (`app.main`).
log = logging.getLogger("asl.live")


def changes(effects: Iterable[dict[str, Any]]) -> list[str]:
    """The kinds of a step's effects that a page shows, sorted; none when the step only valued the account."""
    return sorted({effect["kind"] for effect in effects} - QUIET)


def announce(db: Engine, source: str, kinds: Iterable[str]) -> None:
    """Notify the listeners that ``source`` committed a change of these kinds; raises what the database raises."""
    payload = json.dumps({"source": source, "kinds": sorted(set(kinds))}, separators=(",", ":"))
    with db.begin() as connection:
        connection.execute(text("SELECT pg_notify(:channel, :payload)"), {"channel": CHANNEL, "payload": payload})


class Announcer:
    """The worker's announcements, after each step's commit: a failure is logged (the first, then every 60th in a
    row) and never raised, so it neither stops nor delays the next step."""

    def __init__(self, db: Engine, report: Callable[..., None]):
        self.db, self.report = db, report
        self.failures = 0

    def __call__(self, source: str, kinds: Iterable[str]) -> bool:
        kinds = sorted(set(kinds))
        if not kinds:
            return False
        try:
            announce(self.db, source, kinds)
        except Exception as exc:  # the change is committed; the listener's sweep shows it
            self.failures += 1
            if self.failures % LOG_EVERY == 1:
                self.report("spot_live_announce_failed", source=source, error=type(exc).__name__,
                            consecutive=self.failures)
            return False
        self.failures = 0
        return True


def parse(payload: str) -> tuple[str, frozenset[str]] | None:
    """A notification's source and kinds, or None for anything else on the channel."""
    if len(payload) > PAYLOAD_MAX:
        return None
    try:
        value = json.loads(payload)
    except ValueError:
        return None
    if not isinstance(value, dict) or set(value) != {"source", "kinds"} or value["source"] not in SOURCES:
        return None
    kinds = value["kinds"]
    if not isinstance(kinds, list) or not all(isinstance(kind, str) and KIND.fullmatch(kind) for kind in kinds):
        return None
    return value["source"], frozenset(kinds)


async def connect() -> psycopg.AsyncConnection:
    """The listener's connection as the process's database identity (the API's), in autocommit so that it never
    holds a transaction, with TCP keepalives so that a silent loss shows."""
    from app.db import database_url

    url = database_url()
    return await psycopg.AsyncConnection.connect(
        host=url.host, port=url.port, dbname=url.database, user=url.username, password=url.password,
        autocommit=True, connect_timeout=3, keepalives=1, keepalives_idle=30, keepalives_interval=10,
        keepalives_count=3, application_name="asl_spot_live")


class Unavailable(Exception):
    """The listener cannot take a stream: ``LIVE_UNAVAILABLE`` (not listening) or ``LIVE_BUSY`` (full)."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class Subscription:
    """One stream's wake-ups: the kinds announced since it last looked, and whether to read the feed again."""

    def __init__(self) -> None:
        self.wake = asyncio.Event()
        self.kinds: set[str] = set()
        self.read = False
        self.closed = False

    def push(self, source: str | None, kinds: Iterable[str]) -> None:
        self.read = True
        if source is not None:
            self.kinds.update(kinds)
        self.wake.set()

    def close(self) -> None:
        self.closed = True
        self.wake.set()

    def take(self) -> tuple[bool, set[str]]:
        """Whether to read the feed, and the kinds announced since the last take."""
        self.wake.clear()
        taken = (self.read, self.kinds)
        self.kinds = set()
        self.read = False
        return taken


class Listener:
    """The API's one ``LISTEN`` connection and the streams it wakes. ``run`` listens until cancelled: it reconnects
    after a loss (1, 2, 4 … at most 30 s), and every 30 s without a notification it checks the connection and wakes
    every stream to read again. While it is not listening, no stream starts and the open ones end."""

    def __init__(self, connect: Callable[[], Awaitable[psycopg.AsyncConnection]], *, sweep: float = SWEEP_SECONDS,
                 retry: tuple[float, ...] = RETRY_SECONDS, limit: int = STREAMS_MAX):
        self.connect, self.sweep, self.retry, self.limit = connect, sweep, retry, limit
        self.listening = False
        self.streams: set[Subscription] = set()

    def available(self) -> None:
        if not self.listening:
            raise Unavailable("LIVE_UNAVAILABLE")
        if len(self.streams) >= self.limit:
            raise Unavailable("LIVE_BUSY")

    def subscribe(self) -> Subscription:
        self.available()
        subscription = Subscription()
        self.streams.add(subscription)
        return subscription

    def unsubscribe(self, subscription: Subscription) -> None:
        self.streams.discard(subscription)

    def publish(self, source: str | None, kinds: Iterable[str] = ()) -> None:
        """Wake every stream: ``source`` None reads the feed again (a sweep or a return)."""
        kinds = frozenset(kinds)
        for subscription in self.streams:
            subscription.push(source, kinds)

    def end_streams(self) -> None:
        for subscription in list(self.streams):
            subscription.close()
        self.streams.clear()

    async def run(self) -> None:
        failures = 0
        while True:
            try:
                connection = await self.connect()
            except Exception as exc:
                failures += 1
                self._lost(failures, exc)
                await asyncio.sleep(self.retry[min(failures, len(self.retry)) - 1])
                continue
            try:
                async with connection:
                    await connection.execute(f"LISTEN {CHANNEL}")
                    self.listening = True
                    log.info(json.dumps({"event": "spot_live_listening", "after_failures": failures}, separators=(",", ":")))
                    failures = 0
                    # A stream that started before a loss and is still open reads what it may have missed.
                    self.publish(None)
                    while True:
                        async for notify in connection.notifies(timeout=self.sweep):
                            change = parse(notify.payload)
                            if change is not None:
                                self.publish(*change)
                        async with asyncio.timeout(PING_TIMEOUT_SECONDS):
                            await connection.execute("SELECT 1")
                        self.publish(None)
            except Exception as exc:
                failures += 1
                self._lost(failures, exc)
            finally:
                self.listening = False
                self.end_streams()
            await asyncio.sleep(self.retry[min(failures, len(self.retry)) - 1])

    @staticmethod
    def _lost(failures: int, exc: Exception) -> None:
        if failures == 1 or failures % LOG_EVERY == 0:
            log.warning(json.dumps({"event": "spot_live_listener_lost", "error": type(exc).__name__,
                                    "consecutive": failures}, separators=(",", ":")))


def ready_event(activity: dict[str, Any], retry: int | None = None) -> ServerSentEvent:
    return ServerSentEvent(event="ready", id=activity["cursor"], retry=retry,
                           data={"state": activity["state"], "cursor": activity["cursor"]})


def activity_event(after: int, activity: dict[str, Any], retry: int | None = None) -> ServerSentEvent:
    return ServerSentEvent(event="activity", id=activity["cursor"], retry=retry, data={"after": str(after), **activity})


def change_event(source: str, kinds: set[str]) -> ServerSentEvent:
    return ServerSentEvent(event="change", data={"source": source, "kinds": sorted(kinds)})


async def events(listener: Listener, last: int | None,
                 read: Callable[[int | None], Awaitable[dict[str, Any]]]) -> AsyncIterator[ServerSentEvent]:
    """One browser's stream: ``ready`` with the feed's newest sequence (or, after ``Last-Event-ID``, the
    ``activity`` it missed), then an ``activity`` for each new fill and a ``change`` for the rest. Each event that moves the cursor carries it as its id. A failed read ends the stream; the browser
    reconnects and resumes."""
    try:
        subscription = listener.subscribe()
    except Unavailable:
        return
    try:
        activity = await read(last)
        cursor = int(activity["cursor"])
        if last is not None and cursor > last:
            yield activity_event(last, activity, RECONNECT_MS)
        else:
            yield ready_event(activity, RECONNECT_MS)
        while True:
            await subscription.wake.wait()
            if subscription.closed:
                return
            again, kinds = subscription.take()
            told = False
            if again:
                activity = await read(cursor)
                newest = int(activity["cursor"])
                if newest > cursor:
                    yield activity_event(cursor, activity)
                    told = True
                elif newest < cursor:  # the ledger is older than the stream (a restore): start again from it
                    yield ready_event(activity)
                cursor = newest
            if kinds and not told:
                yield change_event("spot", kinds)
    except Exception as exc:  # a failed read: the browser reconnects with the last id
        log.warning(json.dumps({"event": "spot_live_stream_failed", "error": type(exc).__name__},
                               separators=(",", ":")))
    finally:
        listener.unsubscribe(subscription)
