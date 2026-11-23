"""ExecPlan 0060 (ExecPlan 0047's live trades, kept for spot): the announcement, the listener and the event stream,
with no database. The activity in these streams is SYNTHETIC (no account's record); the test IDs of ExecPlan 0047's
section 6 (L1 to L9) name what each checks.
"""

import asyncio
import json
import re
import threading
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import httpx
import psycopg
import pytest
import uvicorn
from fastapi.testclient import TestClient

from app import main
from app.spot import live
from app.spot import views as spot_views
from app.spot import worker as spot_worker

ENGINE = Path(__file__).resolve().parents[1]
KEY = "k" * 40


def activity(cursor: int, items: int = 0) -> dict:
    """The toasts' feed as ``spot_views.activity`` gives it: ``items`` SYNTHETIC fills ending at ``cursor``."""
    return {"state": "READY", "cursor": str(cursor), "count": items,
            "items": [{"side": "BUY", "seq": str(cursor - n)} for n in reversed(range(items))]}


def run(coroutine):
    return asyncio.run(coroutine)


async def until(check, seconds: float = 2.0) -> None:
    deadline = time.monotonic() + seconds
    while not check():
        if time.monotonic() > deadline:
            raise AssertionError("the condition did not hold in time")
        await asyncio.sleep(0.005)


async def take(stream, seconds: float = 2.0):
    return await asyncio.wait_for(anext(stream), seconds)


# ---- L1: the announcement --------------------------------------------------------------------------------------

def test_l1_only_a_change_a_page_shows_is_announced():
    assert live.changes([{"kind": "VALUATION"}, {"kind": "VALUATION"}]) == []
    assert live.changes([{"kind": "VALUATION"}, {"kind": "FILL"}, {"kind": "RULE_READING"},
                         {"kind": "FILL"}]) == ["FILL", "RULE_READING"]


class Recording:
    """A database that records what the announcement sends."""

    def __init__(self):
        self.sent = []

    @contextmanager
    def begin(self):
        yield self

    def execute(self, statement, params):
        self.sent.append((str(statement), params))


class Refusing:
    def begin(self):
        raise psycopg.OperationalError("the database is away")


def test_l1_the_announcement_names_the_source_and_kinds_and_nothing_else():
    database, reports = Recording(), []
    announce = live.Announcer(database, lambda event, **fields: reports.append(event))
    assert announce("spot", ["FILL", "RULE_READING", "FILL"]) is True
    assert database.sent == [("SELECT pg_notify(:channel, :payload)", {
        "channel": "asl_spot_live", "payload": '{"source":"spot","kinds":["FILL","RULE_READING"]}'})]
    assert announce("spot", []) is False and len(database.sent) == 1  # nothing to announce, nothing sent
    assert reports == []


def test_l1_a_failed_announcement_is_logged_and_never_raised():
    reports = []
    announce = live.Announcer(Refusing(), lambda event, **fields: reports.append((event, fields)))
    assert [announce("spot", ["FILL"]) for _ in range(61)] == [False] * 61
    assert [(event, fields["consecutive"]) for event, fields in reports] == [
        ("spot_live_announce_failed", 1), ("spot_live_announce_failed", 61)]
    announce.db = Recording()
    assert announce("spot", ["FILL"]) is True and announce.failures == 0


def test_l1_the_worker_announces_each_committed_change_after_its_step(monkeypatch):
    steps = [[{"kind": "VALUATION"}], [{"kind": "VALUATION"}, {"kind": "FILL"}], [{"kind": "OWNER_REQUEST"}]]
    order = []
    worker = spot_worker.SpotWorker(db=Refusing(), stop=threading.Event())

    class Engine:
        def __init__(self, db, owner_id, epoch):
            pass

        def start(self):
            pass

        def recover(self, at):
            order.append("recovered")
            return {"status": "OK", "failed_checks": []}

        def step(self, at=None):  # the worker passes none: the step reads the clock under its locks
            order.append("step")
            effects = steps.pop(0)
            if not steps:
                worker.stop.set()
            return effects

    monkeypatch.setattr(spot_worker, "SpotEngine", Engine)
    monkeypatch.setattr(spot_worker.store, "db_now", lambda db: datetime(2026, 11, 12, 17, tzinfo=UTC))
    monkeypatch.setattr(spot_worker.store, "release_lease", lambda *args: None)
    monkeypatch.setattr(spot_worker, "beat", lambda *args, **kwargs: None)
    monkeypatch.setattr(spot_worker, "log", lambda *args, **kwargs: None)
    monkeypatch.setattr(spot_worker, "STEP_SECONDS", 0.0)
    worker.announce = lambda source, kinds: order.append((source, list(kinds)))
    worker.run_epoch(1, SimpleNamespace(valid=lambda: True))
    assert order == ["recovered", ("spot", ["RECOVERED"]), "step", "step", ("spot", ["FILL"]), "step",
                     ("spot", ["OWNER_REQUEST"])]
    # The backtests run only while the worker holds the lease: it let go when it stopped.
    assert not worker.leased.is_set()


def test_l1_a_refused_announcement_does_not_stop_the_worker(monkeypatch):
    worker = spot_worker.SpotWorker(db=Refusing(), stop=threading.Event())
    monkeypatch.setattr(spot_worker, "log", lambda *args, **kwargs: None)
    assert worker.announce("spot", ["FILL"]) is False and worker.announce.failures == 1


@pytest.mark.parametrize("payload", [
    "not json", "[]", '{"source":"spot"}', '{"source":"owner","kinds":["FILL"]}',
    '{"source":"futures","kinds":["FILL"]}', '{"source":"spot","kinds":"FILL"}', '{"source":"spot","kinds":["fill"]}',
    '{"source":"spot","kinds":["FILL"],"amount":"1"}', '{"source":"spot","kinds":["' + "A" * 1000 + '"]}'])
def test_l1_anything_else_on_the_channel_is_ignored(payload):
    assert live.parse(payload) is None


def test_l1_a_notification_is_parsed_to_its_source_and_kinds():
    assert live.parse('{"source":"spot","kinds":["FILL","RUN_STARTED"]}') == (
        "spot", frozenset({"FILL", "RUN_STARTED"}))


# ---- L2: the listener ------------------------------------------------------------------------------------------

def test_l2_no_stream_starts_while_the_listener_is_down_or_full():
    listener = live.Listener(connect=None, limit=2)
    with pytest.raises(live.Unavailable) as refused:
        listener.subscribe()
    assert refused.value.code == "LIVE_UNAVAILABLE"
    listener.listening = True
    first, _ = listener.subscribe(), listener.subscribe()
    with pytest.raises(live.Unavailable) as full:
        listener.subscribe()
    assert full.value.code == "LIVE_BUSY"
    listener.unsubscribe(first)
    listener.subscribe()


class Connection:
    """A ``LISTEN`` connection whose waits are scripted: each entry of ``waits`` is one wait on ``notifies`` (its
    payloads, then the wait's timeout), and ``None`` is the server lost."""

    def __init__(self, waits):
        self.waits, self.queries, self.closed = list(waits), [], False
        self.go, self.waited = asyncio.Event(), asyncio.Event()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        self.closed = True

    async def execute(self, query):
        self.queries.append(query)

    async def notifies(self, timeout=None):
        await self.go.wait()
        wait = self.waits.pop(0) if self.waits else None
        if wait is None:
            raise psycopg.OperationalError("server closed the connection unexpectedly")
        for payload in wait:
            yield SimpleNamespace(payload=payload)
        self.waited.set()
        await asyncio.sleep(0.01)


def test_l2_the_listener_wakes_the_streams_and_ends_them_when_it_is_lost():
    async def check():
        gate = asyncio.Event()
        first = Connection([['{"source":"spot","kinds":["FILL"]}', "noise"], []])
        second = Connection([[]] * 1000)
        second.go.set()
        connections = [first, second]
        connected = []

        async def connect():
            if len(connected) == 1:
                await gate.wait()
            connection = connections.pop(0)
            connected.append(connection)
            return connection

        listener = live.Listener(connect, sweep=0.01, retry=(0.01,))
        task = asyncio.create_task(listener.run())
        await until(lambda: listener.listening)
        stream = listener.subscribe()
        assert stream.take() == (False, set())
        # The first wait's notification (the noise beside it ignored): the stream reads the feed again.
        first.go.set()
        await until(lambda: first.waited.is_set())
        assert stream.take() == (True, {"FILL"})
        # Its sweep: the connection is checked, and the stream reads again.
        await until(lambda: stream.wake.is_set())
        assert stream.take() == (True, set())
        # The server lost: the listener stops listening and ends the open streams; nothing starts until it is back.
        await until(lambda: not listener.listening)
        assert stream.closed and listener.streams == set() and first.closed
        assert first.queries[:2] == ["LISTEN asl_spot_live", "SELECT 1"]
        with pytest.raises(live.Unavailable):
            listener.subscribe()
        gate.set()
        await until(lambda: listener.listening)
        again = listener.subscribe()
        await until(lambda: again.wake.is_set())
        assert again.take()[0] is True  # every sweep reads again
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert not listener.listening and again.closed

    run(check())


def test_l2_a_refused_connection_is_retried():
    async def check():
        attempts = []

        async def connect():
            attempts.append(time.monotonic())
            raise psycopg.OperationalError("connection refused")

        listener = live.Listener(connect, retry=(0.01, 0.02))
        task = asyncio.create_task(listener.run())
        await until(lambda: len(attempts) >= 3)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert not listener.listening

    run(check())


# ---- L3: the stream's events -----------------------------------------------------------------------------------

def reader(*answers):
    answers, asked = list(answers), []

    async def read(after):
        asked.append(after)
        answer = answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    read.asked = asked
    return read


def listening(limit: int = 8) -> live.Listener:
    listener = live.Listener(connect=None, limit=limit)
    listener.listening = True
    return listener


def test_l3_a_new_stream_starts_at_the_newest_entry_and_shows_nothing_old():
    async def check():
        listener, read = listening(), reader(activity(41))
        stream = live.events(listener, None, read)
        ready = await take(stream)
        assert (ready.event, ready.id, ready.retry, ready.data) == (
            "ready", "41", 3000, {"state": "READY", "cursor": "41"})
        assert read.asked == [None] and len(listener.streams) == 1
        await stream.aclose()
        assert listener.streams == set()

    run(check())


def test_l3_a_resumed_stream_starts_with_what_it_missed():
    async def check():
        missed = live.events(listening(), 40, reader(activity(43, items=3)))
        first = await take(missed)
        assert (first.event, first.id, first.retry, first.data["after"], first.data["count"]) == (
            "activity", "43", 3000, "40", 3)
        assert [item["seq"] for item in first.data["items"]] == ["41", "42", "43"]
        nothing = live.events(listening(), 43, reader(activity(43)))
        assert (await take(nothing)).event == "ready"

    run(check())


def test_l3_each_wake_tells_what_changed_once():
    async def check():
        listener = listening()
        # Every wake reads the feed again (a change of any kind may come with a fill), so a wake that found no new
        # fill tells its kinds as a change.
        read = reader(activity(41), activity(42, items=1), activity(42), activity(42), activity(42), activity(30))
        stream = live.events(listener, None, read)
        assert (await take(stream)).id == "41"
        # A fill: its activity, with the cursor it follows; no change event as well.
        listener.publish("spot", {"FILL", "RULE_READING"})
        fill = await take(stream)
        assert (fill.event, fill.id, fill.data["after"], fill.retry) == ("activity", "42", "41", None)
        # A request answered with no fill: a change.
        listener.publish("spot", {"OWNER_REQUEST"})
        answered = await take(stream)
        assert (answered.event, answered.id, answered.data) == (
            "change", None, {"source": "spot", "kinds": ["OWNER_REQUEST"]})
        # A sweep with nothing new tells nothing: the next event is the backtest's.
        pending = asyncio.ensure_future(take(stream))
        listener.publish(None)
        await until(lambda: len(read.asked) == 4)
        assert not pending.done()
        listener.publish("spot", {"BACKTEST"})
        backtest = await pending
        assert (backtest.event, backtest.data) == ("change", {"source": "spot", "kinds": ["BACKTEST"]})
        assert read.asked == [None, 41, 42, 42, 42]
        # A ledger older than the stream (a restore): start again from it.
        listener.publish(None)
        restored = await take(stream)
        assert (restored.event, restored.id) == ("ready", "30")
        # The listener lost: the stream ends.
        listener.end_streams()
        with pytest.raises(StopAsyncIteration):
            await take(stream)

    run(check())


def test_l3_a_failed_read_ends_the_stream_and_frees_its_place():
    async def check():
        listener = listening(limit=1)
        stream = live.events(listener, None, reader(activity(41), psycopg.OperationalError("statement timeout")))
        await take(stream)
        listener.publish(None)
        with pytest.raises(StopAsyncIteration):
            await take(stream)
        assert listener.streams == set()
        listener.subscribe()
        # A stream started while the listener is full ends at once.
        with pytest.raises(StopAsyncIteration):
            await take(live.events(listener, None, reader(activity(41))))

    run(check())


# ---- L3: the route ---------------------------------------------------------------------------------------------

@pytest.fixture
def key(tmp_path, monkeypatch):
    path = tmp_path / "api_internal_key"
    path.write_text(KEY)
    monkeypatch.setenv("ASL_INTERNAL_KEY_FILE", str(path))
    return KEY


def test_l3_the_stream_needs_the_service_key_and_a_listener(key, monkeypatch):
    client = TestClient(main.app, base_url="http://api:8000")
    assert client.get("/v1/spot/live").status_code == 401
    assert client.get("/v1/spot/live", headers={"X-Internal-Key": "x" * 40}).status_code == 401
    monkeypatch.setattr(main.LIVE, "listening", False)
    refused = client.get("/v1/spot/live", headers={"X-Internal-Key": key})
    assert (refused.status_code, refused.json()["code"], refused.json()["retryable"]) == (
        503, "LIVE_UNAVAILABLE", True)
    monkeypatch.setattr(main.LIVE, "listening", True)
    monkeypatch.setattr(main.LIVE, "limit", 0)
    busy = client.get("/v1/spot/live", headers={"X-Internal-Key": key})
    assert (busy.status_code, busy.json()["code"]) == (503, "LIVE_BUSY")
    monkeypatch.setattr(main.LIVE, "limit", 8)
    assert client.get("/v1/spot/live?after=1", headers={"X-Internal-Key": key}).status_code == 422
    for bad in ("01", "-1", "1 2", "9" * 20):
        assert client.get("/v1/spot/live", headers={"X-Internal-Key": key, "Last-Event-ID": bad}).status_code == 422


class Server(uvicorn.Server):
    """uvicorn in a thread, as the image runs the API (without its lifespan: no database here)."""

    async def startup(self, sockets=None):
        self.loop = asyncio.get_running_loop()
        await super().startup(sockets)


@contextmanager
def serving(**options):
    server = Server(uvicorn.Config(main.app, host="127.0.0.1", port=0, lifespan="off", log_level="warning",
                                   **options))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started:
        assert time.monotonic() < deadline and thread.is_alive(), "uvicorn did not start"
        time.sleep(0.01)
    port = server.servers[0].sockets[0].getsockname()[1]
    try:
        yield server, thread, f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(10)


def events_of(lines):
    """The stream's events as the browser parses them, skipping the keep-alive comments."""
    fields = {}
    for line in lines:
        if line == "":
            if fields:
                yield fields
            fields = {}
        elif not line.startswith(":"):
            name, _, value = line.partition(": ")
            fields[name] = value


def test_l3_the_stream_on_the_wire_resumes_from_its_last_id(key, monkeypatch):
    answers = {None: activity(41), 41: activity(42, items=1), 40: activity(42, items=2)}
    monkeypatch.setattr(spot_views, "activity", lambda after: answers[after])
    monkeypatch.setattr(main.LIVE, "listening", True)
    with serving() as (server, _, base), httpx.Client(base_url=base, headers={"X-Internal-Key": key},
                                                     timeout=5) as client:
        with client.stream("GET", "/v1/spot/live") as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            assert response.headers["cache-control"] == "private, no-store"
            assert response.headers["x-accel-buffering"] == "no"
            stream = events_of(response.iter_lines())
            ready = next(stream)
            assert (ready["event"], ready["id"], ready["retry"], json.loads(ready["data"])) == (
                "ready", "41", "3000", {"state": "READY", "cursor": "41"})
            server.loop.call_soon_threadsafe(main.LIVE.publish, "spot", frozenset({"FILL"}))
            fill = next(stream)
            assert (fill["event"], fill["id"], "retry" in fill) == ("activity", "42", False)
            assert json.loads(fill["data"]) == {"after": "41", **activity(42, items=1)}
        with client.stream("GET", "/v1/spot/live", headers={"Last-Event-ID": "40"}) as response:
            first = next(events_of(response.iter_lines()))
            assert (first["event"], first["id"], json.loads(first["data"])["after"]) == ("activity", "42", "40")
        deadline = time.monotonic() + 5
        while main.LIVE.streams and time.monotonic() < deadline:
            time.sleep(0.01)
        assert main.LIVE.streams == set()  # each stream left with its client


# ---- L9: the API stops while a stream is open --------------------------------------------------------------------

def test_l9_the_api_stops_within_its_grace_while_a_stream_is_open(key, monkeypatch):
    monkeypatch.setattr(spot_views, "activity", lambda after: activity(41))
    monkeypatch.setattr(main.LIVE, "listening", True)
    with serving(timeout_graceful_shutdown=1) as (server, thread, base), httpx.Client(
            base_url=base, headers={"X-Internal-Key": key}, timeout=5) as client:
        with client.stream("GET", "/v1/spot/live") as response:
            assert next(events_of(response.iter_lines()))["event"] == "ready"
            began = time.monotonic()
            server.should_exit = True
            thread.join(10)
            assert not thread.is_alive() and time.monotonic() - began < 4
    assert main.LIVE.streams == set()


def test_l9_the_image_bounds_the_api_s_shutdown():
    commands = re.findall(r"^CMD (\[.*\])$", (ENGINE / "Dockerfile").read_text(), re.MULTILINE)
    api = [json.loads(command) for command in commands if "app.main:app" in command]
    assert api == [["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log",
                    "--timeout-graceful-shutdown", "3"]]
