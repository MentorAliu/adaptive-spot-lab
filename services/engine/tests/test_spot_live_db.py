"""ExecPlan 0060 (ExecPlan 0047's live trades, kept for spot): the live trades on a real PostgreSQL, on an isolated
``asl_m1_`` database. The listener listens as the API's role over ``live.connect``; the spot engine's announcements
arrive after their commit, a rolled-back one never does, and a listener whose connection the server ends listens
again. Every market value is SYNTHETIC (``spot_support``)."""

import asyncio
import contextlib
from collections.abc import Callable

import psycopg
from spot_support import T0
from spot_support import spot as spot  # noqa: F401  (pytest fixture)
from sqlalchemy import text

from app.spot import live
from app.spot import views as spot_views
from app.spot_market.views import plain


async def until(condition: Callable[[], bool], timeout: float = 5.0) -> None:
    async with asyncio.timeout(timeout):
        while not condition():
            await asyncio.sleep(0.02)


@contextlib.asynccontextmanager
async def listening(**options):
    listener = live.Listener(live.connect, **options)
    running = asyncio.create_task(listener.run())
    try:
        await until(lambda: listener.listening)
        yield listener
    finally:
        running.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await running


def test_an_announcement_arrives_after_its_commit_and_a_rolled_back_one_never(spot):
    async def main() -> list[psycopg.Notify]:
        connection = await live.connect()
        try:
            await connection.execute(f"LISTEN {live.CHANNEL}")
            # Another transaction's notification is delivered only if it commits.
            with spot.execution.connect() as other:
                other.execute(text("SELECT pg_notify(:channel, :payload)"),
                              {"channel": live.CHANNEL, "payload": '{"source":"spot","kinds":["ROLLED_BACK"]}'})
                other.rollback()
            live.announce(spot.execution, "spot", ["FILL", "RULE_READING", "FILL"])
            return [notify async for notify in connection.notifies(timeout=1.0)]
        finally:
            await connection.close()

    (notify,) = asyncio.run(main())
    assert notify.channel == live.CHANNEL
    assert notify.payload == '{"source":"spot","kinds":["FILL","RULE_READING"]}'
    assert live.parse(notify.payload) == ("spot", frozenset({"FILL", "RULE_READING"}))


def test_a_fill_the_engine_commits_reaches_an_open_stream_with_its_feed_entry(spot):
    spot.ready()
    spot.start()
    reports: list[tuple[str, dict]] = []
    announcer = live.Announcer(spot.execution, lambda event, **fields: reports.append((event, fields)))

    def buy() -> list[str]:
        """The worker's order (``app.spot.worker``): the step commits, then its announcement in a transaction of its
        own."""
        kinds = live.changes(spot.step(T0))
        assert announcer("spot", kinds)
        return kinds

    async def read(after: int | None) -> dict:
        return await asyncio.to_thread(spot_views.activity, after, engine=spot.api)

    async def main():
        async with listening() as listener:
            stream = live.events(listener, None, read)
            try:
                first = await anext(stream)
                kinds = await asyncio.to_thread(buy)
                second = await asyncio.wait_for(anext(stream), 5)
            finally:
                await stream.aclose()
            assert not listener.streams
            return first, kinds, second

    first, kinds, second = asyncio.run(main())
    assert (first.event, first.retry, first.data) == ("ready", live.RECONNECT_MS, {"state": "READY", "cursor": "0"})
    assert first.id == "0"
    assert {"FILL", "RULE_READING", "RUN_STARTED"} <= set(kinds) and "VALUATION" not in kinds
    [fill] = spot.fills()
    assert second.event == "activity" and second.retry is None
    assert second.data["after"] == "0" and second.id == second.data["cursor"] == str(fill["seq"])
    assert second.data["count"] == 1
    (item,) = second.data["items"]
    assert (item["id"], item["side"], item["reason"], item["quantity"]) == (
        str(fill["id"]), "BUY", fill["reason"], plain(fill["quantity"]))
    assert reports == []


def test_a_listener_the_server_cut_off_ends_its_streams_listens_again_and_hears_the_next_announcement(spot):
    def cut_off() -> int:
        with spot.admin.begin() as connection:
            return connection.execute(text(
                "SELECT count(pg_terminate_backend(pid)) FROM pg_stat_activity "
                "WHERE application_name = :name AND datname = current_database()"),
                {"name": "asl_spot_live"}).scalar_one()

    async def main():
        async with listening(retry=(0.1,)) as listener:
            before = listener.subscribe()
            assert await asyncio.to_thread(cut_off) == 1
            await until(lambda: before.closed)  # the loss ends the open streams: the browsers reconnect
            await until(lambda: listener.listening)
            after = listener.subscribe()
            await asyncio.to_thread(live.announce, spot.execution, "spot", ["BACKTEST"])
            await asyncio.wait_for(after.wake.wait(), 5)
            return after.take()

    assert asyncio.run(main()) == (True, {"BACKTEST"})
