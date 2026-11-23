"""BTCUSDT's spot feed (ExecPlan 0060 section 4.5; ``app.perp.feed``'s design for one stream): the book, the 1-minute
and daily candles, the provider's clock and the instrument, written for the account and the pages.

What is written, and when:
- **Book:** the newest book (ten levels a side) of each second of receipt, once that second is over, with the feed's
  state in the same transaction.
- **Candles:** each 1-minute candle as it changes, at most once a second; a candle the provider marked closed is
  final and never changed again. At the start and every five minutes (every minute while some are lacking) the feed
  asks REST for the final candles of the last 30 days it lacks, a REST row being final only when it closed before the
  provider's clock at the answer.
- **Days:** every final daily candle since 2017-08-17, a thousand a request (four the first time), then 90 seconds
  after each UTC midnight the day that midnight closed. Once none is lacking, ``daily_checked_at`` says so: the
  backtest waits for it. A day the provider answers without is not asked again while this process runs.
- **Clock:** every minute, the best of three samples of ``/api/v3/time``. It is verified when the offset is at most
  1,000 ms and the uncertainty at most 500 ms; a check older than 150 s verifies nothing. A candle whose event time
  lies more than two seconds ahead of the provider's clock as measured is dropped, and the clock is checked again at
  once.
- **Instrument:** at the start and every 30 minutes. Its answer declares the IP's weight allowance, which sets the REST
  client's IP-wide guard.
- **Retention:** books older than two days and 1-minute candles older than 30 days, every hour.

The state is ``CONNECTED`` only while the stream delivers, the clock is verified, the instrument is usable and was
checked in the last hour, and the newest book is at most five seconds old. The account decides what it may trade on
from the stored times itself (``app.spot.engine``); the state is what the pages show.

Every failure is caught, recorded in ``spot_feed_events`` and the feed's state, and retried after a wait.
"""

import asyncio
import json
import logging
import random
import time
from collections.abc import Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from functools import partial
from typing import Any
from uuid import UUID, uuid4

from app.spot_market import market, store
from app.spot_market.parse import PayloadError
from app.spot_market.provider import ProviderUnavailable, PublicBinance

logger = logging.getLogger("asl.spot_feed")
ROTATION_SECONDS = 23 * 3600  # Binance ends a connection at 24 hours.
SILENCE_SECONDS = 10  # The book arrives ten times a second; a silent connection is reconnected.
HEALTHY_RESET_SECONDS = 60
CLOCK_SECONDS = 60
CLOCK_VALID_SECONDS = 150
CLOCK_OFFSET_MAX_MS = 1000
CLOCK_UNCERTAINTY_MAX_MS = 500
FUTURE_TOLERANCE_MS = 2000
INSTRUMENT_SECONDS = 1800
INSTRUMENT_VALID_SECONDS = 3600
FRESH_SECONDS = 5
PENDING_SECONDS_MAX = 120  # While the database is unreachable, older unwritten seconds are dropped.
HISTORY_SECONDS = 300
HISTORY_LACKING_SECONDS = 60
HISTORY_DAYS = 30
HISTORY_REQUESTS = 12  # At most this many REST pages a pass (1,000 minutes each, weight 2).
DAILY_REQUESTS = 5  # Every day since 2017-08-17 in one pass (1,000 days each, weight 2).
AFTER_MIDNIGHT_SECONDS = 90
DAILY_RETRY_SECONDS = 600
RETENTION_SECONDS = 3600
RETENTION_PASSES = 20
RETRY_SECONDS = 30


def event(code: str, **fields: object) -> None:
    logger.info(json.dumps({"event": code, **fields}, separators=(",", ":"), default=str))


def failure(exc: BaseException) -> str:
    if isinstance(exc, ProviderUnavailable):
        return exc.code
    if isinstance(exc, PayloadError):
        return str(exc)[:80]
    return type(exc).__name__


def day_open(at_ms: int) -> int:
    return at_ms - at_ms % market.DAY_MS


def daily_wait_seconds(now_ms: int, *, lacking: bool) -> float:
    """How long the daily job waits after a pass: within ``AFTER_MIDNIGHT_SECONDS`` after a UTC midnight, until then
    (the day that midnight closed is final by then); otherwise ``DAILY_RETRY_SECONDS`` while days are lacking, else
    until ``AFTER_MIDNIGHT_SECONDS`` after the next UTC midnight."""
    midnight = day_open(now_ms)
    settled = (midnight - now_ms) / 1000 + AFTER_MIDNIGHT_SECONDS
    if settled > 0:
        return max(1.0, settled)
    if lacking:
        return float(DAILY_RETRY_SECONDS)
    return max(1.0, (midnight + market.DAY_MS - now_ms) / 1000 + AFTER_MIDNIGHT_SECONDS)


class SpotFeed:
    def __init__(self, engine, client: PublicBinance | None = None, *, stop: asyncio.Event | None = None,
                 clock: Callable[[], datetime] = lambda: datetime.now(UTC),
                 monotonic: Callable[[], float] = time.monotonic) -> None:
        self.engine = engine
        self.client = client if client is not None else PublicBinance()
        self.stop = stop if stop is not None else asyncio.Event()
        self.clock = clock
        self.monotonic = monotonic
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="spot-db")
        self.connection_id: UUID = uuid4()
        self.connected = False
        # Received and not yet written: the newest book of each second of receipt (UTC epoch seconds), and the
        # newest state of each candle that changed.
        self.quotes: dict[int, tuple[market.Quote, datetime]] = {}
        self.bars: dict[int, tuple[market.Bar, datetime]] = {}
        self.last: dict[str, datetime | None] = {"quote": None, "bar": None}
        self.clock_offset_ms: float | None = None
        self.clock_uncertainty_ms: float | None = None
        self.clock_checked: float | None = None
        self.clock_verified = False
        self.recheck = asyncio.Event()
        self.measured = asyncio.Event()  # set once the provider's clock has been measured
        self.instrument_usable = False
        self.instrument_checked: float | None = None
        # Minutes and days REST answered without, after they closed; not asked again while this process runs.
        self.absent: set[int] = set()
        self.absent_days: set[int] = set()
        self.frames_refused = 0

    async def db(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        return await asyncio.get_running_loop().run_in_executor(
            self.executor, partial(fn, self.engine, *args, **kwargs))

    async def note(self, code: str, **detail: Any) -> None:
        event(code, **detail)
        try:
            await self.db(store.record_event, code, self.clock(), detail)
        except Exception as exc:  # a lost incident record must not end the feed
            event("spot_event_unrecorded", code=code, reason=type(exc).__name__)

    async def pause(self, seconds: float) -> bool:
        """Wait, ending at once when the feed stops; True when it stops."""
        try:
            await asyncio.wait_for(self.stop.wait(), timeout=max(0.0, seconds))
            return True
        except TimeoutError:
            return False

    # ---- state ------------------------------------------------------------------------------------------------

    def provider_lower_ms(self) -> int | None:
        """The earliest the provider's clock can read now, or None while it is unmeasured."""
        if self.clock_offset_ms is None or self.clock_uncertainty_ms is None:
            return None
        return int(self.clock().timestamp() * 1000 + self.clock_offset_ms - self.clock_uncertainty_ms)

    def clock_valid(self) -> bool:
        return self.clock_verified and self.clock_checked is not None \
            and self.monotonic() - self.clock_checked <= CLOCK_VALID_SECONDS

    def status(self) -> tuple[str, str | None]:
        if not self.connected:
            return "UNAVAILABLE", "STREAM_DISCONNECTED"
        if not self.clock_valid():
            return "UNAVAILABLE", "CLOCK_UNVERIFIED"
        if not self.instrument_usable or self.instrument_checked is None \
                or self.monotonic() - self.instrument_checked > INSTRUMENT_VALID_SECONDS:
            return "UNAVAILABLE", "INSTRUMENT_UNVERIFIED"
        seen = self.last["quote"]
        if seen is None or (self.clock() - seen).total_seconds() > FRESH_SECONDS:
            return "DEGRADED", "QUOTE_STALE"
        return "CONNECTED", None

    def state(self) -> dict[str, Any]:
        status, reason = self.status()
        return {"status": status, "reason": reason, "stream_connected": self.connected,
                "last_quote_at": self.last["quote"], "last_bar_at": self.last["bar"],
                "clock_verified": self.clock_valid(), "heartbeat_at": self.clock()}

    # ---- the stream -------------------------------------------------------------------------------------------

    def take(self, raw: bytes, received: datetime) -> str | None:
        """One frame, kept as the newest of its kind and second; returns its kind, or None when refused."""
        try:
            kind, item = market.parse_stream(raw)
        except PayloadError as exc:
            self.frames_refused += 1
            if self.frames_refused <= 5 or self.frames_refused % 1000 == 0:
                event("spot_frame_refused", reason=str(exc)[:80], count=self.frames_refused)
            return None
        if kind == "bar" and self.clock_offset_ms is not None and self.clock_uncertainty_ms is not None \
                and item.event_ms - self.clock_offset_ms - self.clock_uncertainty_ms \
                > received.timestamp() * 1000 + FUTURE_TOLERANCE_MS:
            # An event time ahead of the provider's clock as measured: the clock is not what was measured.
            self.frames_refused += 1
            self.clock_verified = False
            self.recheck.set()
            event("spot_frame_ahead", ahead_ms=round(item.event_ms - self.clock_offset_ms
                                                     - received.timestamp() * 1000))
            return None
        if kind == "quote":
            self.quotes[int(received.timestamp())] = (item, received)
        else:
            held = self.bars.get(item.open_ms)
            if held is not None and held[0].final and not item.final:
                return kind
            self.bars[item.open_ms] = (item, received)
        self.last[kind] = received
        return kind

    async def stream(self) -> None:
        attempts = 0
        while not self.stop.is_set():
            opened_at: float | None = None
            try:
                connector = await self.client.connect_stream()
                async with connector as websocket:
                    opened_at = self.monotonic()
                    self.connected = True
                    await self.note("STREAM_CONNECTED", streams=list(market.STREAMS))
                    while self.monotonic() - opened_at < ROTATION_SECONDS:
                        async with asyncio.timeout(SILENCE_SECONDS):
                            raw = await websocket.recv()
                        self.take(raw.encode() if isinstance(raw, str) else raw, self.clock())
                self.connected = False
                attempts = 0
                await self.note("STREAM_ROTATED")
            except asyncio.CancelledError:
                self.connected = False
                raise
            except Exception as exc:  # a lost connection is retried; it never ends the worker
                self.connected = False
                if opened_at is not None and self.monotonic() - opened_at >= HEALTHY_RESET_SECONDS:
                    attempts = 0
                attempts += 1
                wait = max(exc.retry_after if isinstance(exc, ProviderUnavailable) else 0,
                           min(60, 2 ** min(attempts, 6) + random.random()))
                await self.note("STREAM_LOST", reason=failure(exc), attempt=attempts, retry_seconds=round(wait, 1))
                if await self.pause(wait):
                    return

    # ---- the writer -------------------------------------------------------------------------------------------

    def trim(self) -> None:
        for second in sorted(self.quotes)[:-PENDING_SECONDS_MAX]:
            del self.quotes[second]

    async def write(self) -> None:
        """Write every second that is over, every changed candle and the state; keep what fails for the next."""
        current = int(self.clock().timestamp())
        seconds = sorted(second for second in self.quotes if second < current)
        bars = list(self.bars.items())
        try:
            await self.db(store.write_second, quotes=[self.quotes[second] for second in seconds],
                          bars=[pair for _, pair in bars], connection_id=self.connection_id, state=self.state())
        except Exception as exc:  # the next second tries again with what is pending then
            event("spot_write_failed", reason=type(exc).__name__)
            self.trim()
            return
        for second in seconds:
            self.quotes.pop(second, None)
        for open_ms, pair in bars:
            if self.bars.get(open_ms) is pair:
                del self.bars[open_ms]

    async def writer(self) -> None:
        while not self.stop.is_set():
            # Just after the next second starts, so the second before it is over.
            if await self.pause(1.05 - self.clock().microsecond / 1_000_000):
                return
            await self.write()

    # ---- REST: clock, instrument, history, days, retention ----------------------------------------------------

    async def check_clock(self) -> None:
        try:
            _server, offset, uncertainty = await self.client.best_clock()
        except (ProviderUnavailable, PayloadError) as exc:
            if not self.clock_valid():
                self.clock_verified = False
            await self.note("CLOCK_CHECK_FAILED", reason=failure(exc))
            return
        verified = abs(offset) <= CLOCK_OFFSET_MAX_MS and uncertainty <= CLOCK_UNCERTAINTY_MAX_MS
        if verified != self.clock_verified or self.clock_checked is None:
            await self.note("CLOCK_VERIFIED" if verified else "CLOCK_UNVERIFIED", offset_ms=round(offset, 1),
                            uncertainty_ms=round(uncertainty, 1))
        self.clock_offset_ms, self.clock_uncertainty_ms = offset, uncertainty
        self.clock_verified, self.clock_checked = verified, self.monotonic()
        self.measured.set()
        await self.db(store.update_state, {"clock_verified": verified, "clock_offset_ms": round(offset, 3),
                                           "clock_uncertainty_ms": round(uncertainty, 3),
                                           "clock_checked_at": self.clock()})

    async def check_instrument(self) -> None:
        try:
            instrument = market.parse_instrument(await self.client.instrument())
        except (ProviderUnavailable, PayloadError) as exc:
            if self.instrument_checked is None \
                    or self.monotonic() - self.instrument_checked > INSTRUMENT_VALID_SECONDS:
                self.instrument_usable = False
            await self.note("INSTRUMENT_CHECK_FAILED", reason=failure(exc))
            return
        identity = await self.db(store.record_instrument, instrument, self.clock())
        if instrument.usable != self.instrument_usable or self.instrument_checked is None:
            await self.note("INSTRUMENT_CHECKED", instrument_id=identity, usable=instrument.usable,
                            status=instrument.status, step_size=store.decimal_text(instrument.step_size),
                            min_qty=store.decimal_text(instrument.min_qty),
                            min_notional=store.decimal_text(instrument.min_notional),
                            not_applied=list(instrument.not_applied))
        self.instrument_usable, self.instrument_checked = instrument.usable, self.monotonic()

    async def references(self) -> None:
        instrument_at: float | None = None
        while not self.stop.is_set():
            self.recheck.clear()
            await self.check_clock()
            if instrument_at is None or self.monotonic() - instrument_at >= INSTRUMENT_SECONDS:
                await self.check_instrument()
                instrument_at = self.monotonic()
            try:
                await asyncio.wait_for(self.recheck.wait(), timeout=CLOCK_SECONDS)
            except TimeoutError:
                pass

    async def fill_history(self) -> tuple[int, bool]:
        """Ask REST for the final 1-minute candles of the last 30 days the store lacks: the candles stored, and whether
        some are still lacking after the pass."""
        lower = self.provider_lower_ms()
        if lower is None:
            return 0, True
        end = (lower // market.MINUTE_MS) * market.MINUTE_MS  # the minute still open is not asked for
        start = end - HISTORY_DAYS * market.DAY_MS
        self.absent = {minute for minute in self.absent if minute >= start}
        missing = [minute for minute in await self.db(store.missing_minutes, start, end) if minute not in self.absent]
        stored = 0
        for _ in range(HISTORY_REQUESTS):
            if not missing:
                break
            first = missing[0]
            last = min(first + (market.KLINE_ROWS_MAX - 1) * market.MINUTE_MS, end - market.MINUTE_MS)
            rows = (last - first) // market.MINUTE_MS + 1
            raw = await self.client.klines("1m", first, last + market.MINUTE_MS - 1, rows)
            lower = self.provider_lower_ms()
            if lower is None:
                break
            bars = [bar for bar in market.parse_rest_klines(raw, lower) if bar.final]
            if bars:
                await self.db(store.write_history, bars, self.clock(), self.clock())
            stored += len(bars)
            returned = {bar.open_ms for bar in bars}
            self.absent.update(minute for minute in missing
                               if first <= minute <= last and minute not in returned
                               and minute + market.MINUTE_MS - 1 < lower)
            missing = [minute for minute in missing if minute > last]
        return stored, bool(missing)

    async def history(self) -> None:
        await self.measured.wait()  # finality is judged by the provider's clock
        while not self.stop.is_set():
            wait = HISTORY_SECONDS
            try:
                stored, lacking = await self.fill_history()
                if stored:
                    await self.note("HISTORY_STORED", candles=stored)
                if lacking:
                    wait = HISTORY_LACKING_SECONDS
            except (ProviderUnavailable, PayloadError) as exc:
                await self.note("HISTORY_FAILED", reason=failure(exc))
                wait = RETRY_SECONDS
            if await self.pause(wait):
                return

    async def fill_daily(self) -> tuple[int, bool]:
        """Ask REST for the final days since 2017-08-17 the store lacks, from the first one lacking, a thousand a
        request: the days stored, and whether some are still lacking after the pass. A closed day the provider
        answered without is not asked again while this process runs; one not final yet waits for the next pass. A day
        the exchange closed early is stored as it records it and noted once, ``DAILY_CLOSED_EARLY``."""
        lower = self.provider_lower_ms()
        if lower is None:
            return 0, True
        start, end = market.FIRST_DAY_MS, day_open(lower)  # the day still running is not asked for
        have = await self.db(store.stored_days, start, end)
        lacking = [day for day in range(start, end, market.DAY_MS) if day not in have and day not in self.absent_days]
        wanted = set(lacking)
        pending: list[int] = []
        stored = 0
        for _ in range(DAILY_REQUESTS):
            if not lacking:
                break
            first = lacking[0]
            last = min(first + (market.KLINE_ROWS_MAX - 1) * market.DAY_MS, end - market.DAY_MS)
            raw = await self.client.klines("1d", first, last + market.DAY_MS - 1,
                                           (last - first) // market.DAY_MS + 1)
            lower = self.provider_lower_ms()
            if lower is None:
                return stored, True
            days = [day for day in market.parse_rest_daily_klines(raw, lower) if day.final and start <= day.open_ms < end]
            if days:
                stored += await self.db(store.write_daily, days, self.clock())
            for day in days:
                if day.closed_early and day.open_ms in wanted:  # stored now, kept as the exchange records it
                    await self.note("DAILY_CLOSED_EARLY", day=market.at(day.open_ms).date().isoformat(),
                                    closed_at=market.at(day.close_ms).isoformat(), trades=day.trades)
            returned = {day.open_ms for day in days}
            for day in lacking:
                if first <= day <= last and day not in returned:
                    if day + market.DAY_MS - 1 + market.DAY_SETTLE_MS < lower:
                        self.absent_days.add(day)
                    else:
                        pending.append(day)
            lacking = [day for day in lacking if day > last]
        return stored, bool(lacking or pending)

    async def daily(self) -> None:
        """Once the provider's clock is measured: at the start, then 90 s after each UTC midnight, and every ten
        minutes while a day is lacking. A pass that finds none lacking marks the history complete."""
        await self.measured.wait()  # finality is judged by the provider's clock
        while not self.stop.is_set():
            wait = float(RETRY_SECONDS)
            try:
                stored, lacking = await self.fill_daily()
                if stored:
                    await self.note("DAILY_STORED", days=stored)
                if not lacking:
                    await self.db(store.update_state, {"daily_checked_at": self.clock()})
                if self.absent_days and stored:
                    await self.note("DAILY_ABSENT", days=len(self.absent_days),
                                    first=market.at(min(self.absent_days)).date().isoformat())
                wait = daily_wait_seconds(int(self.clock().timestamp() * 1000), lacking=lacking)
            except (ProviderUnavailable, PayloadError) as exc:
                await self.note("DAILY_FAILED", reason=failure(exc))
            if await self.pause(wait):
                return

    async def retention(self) -> None:
        while not self.stop.is_set():
            removed = 0
            for _ in range(RETENTION_PASSES):
                count = await self.db(store.prune)
                removed += count
                if count < store.RETENTION_BATCH:
                    break
            if removed:
                event("spot_retention", removed=removed)
            if await self.pause(RETENTION_SECONDS):
                return

    # ---- the whole feed ---------------------------------------------------------------------------------------

    async def guarded(self, name: str, job: Callable[[], Awaitable[None]]) -> None:
        """Run one part of the feed; an unexpected failure is recorded and the part starts again after a wait."""
        while not self.stop.is_set():
            try:
                await job()
                return
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                if isinstance(exc, ProviderUnavailable) and exc.code == "worker_stopping":
                    return
                await self.note("TASK_FAILED", task=name, reason=failure(exc))
                if await self.pause(RETRY_SECONDS):
                    return

    async def schema_ready(self) -> bool:
        while not self.stop.is_set():
            try:
                if await self.db(store.schema_ready):
                    return True
                event("spot_schema_pending")
            except Exception as exc:
                event("spot_schema_unreadable", reason=type(exc).__name__)
            if await self.pause(RETRY_SECONDS):
                return False
        return False

    async def run(self) -> None:
        self.client.bind(stop=self.stop, report=self.rest_report)
        tasks: list[asyncio.Task] = []
        ready = False
        try:
            ready = await self.schema_ready()
            if not ready:
                return
            await self.note("FEED_STARTED", connection=str(self.connection_id))
            jobs = {"references": self.references, "stream": self.stream, "writer": self.writer,
                    "history": self.history, "daily": self.daily, "retention": self.retention}
            tasks = [asyncio.create_task(self.guarded(name, job), name=f"spot-{name}") for name, job in jobs.items()]
            await self.stop.wait()
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            if ready:
                try:
                    await self.db(store.update_state, {"status": "UNAVAILABLE", "reason": "FEED_STOPPED",
                                                       "stream_connected": False})
                except Exception:
                    pass
            await self.client.close()
            self.executor.shutdown(wait=True)

    async def rest_report(self, report: dict) -> None:
        if report.get("kind") in ("allowance", "backoff", "wait"):
            await self.note("REST_" + str(report["kind"]).upper(),
                            **{key: value for key, value in report.items() if key != "kind"})
