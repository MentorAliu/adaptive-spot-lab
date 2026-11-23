"""BTCUSDT's spot feed without a database or a network (ExecPlan 0060 section 6, R6): the parsing, the longer
candles, the client and the feed. Every input is SYNTHETIC, shaped as Binance's documentation shows it
(``spot_market_support``)."""

import asyncio
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import httpx
import pytest
from spot_market_support import (
    DAY,
    FILTERS,
    MINUTE,
    FakeSpot,
    daily_row,
    depth,
    exchange_info,
    instrument_doc,
    kline,
    rest_row,
)

from app.spot_market import bars, feed, market, provider
from app.spot_market.parse import PayloadError

T0 = datetime(2026, 11, 12, 12, 0, tzinfo=UTC)
T0_MS = int(T0.timestamp() * 1000)
D = Decimal


# ---- parsing --------------------------------------------------------------------------------------------------

def test_the_instrument_combines_a_market_orders_filters_and_names_the_others():
    instrument = market.parse_instrument(exchange_info())
    assert (instrument.symbol, instrument.status, instrument.usable) == ("BTCUSDT", "TRADING", True)
    assert (instrument.tick_size, instrument.step_size, instrument.min_qty, instrument.max_qty) == (
        D("0.01"), D("0.00001"), D("0.00001"), D("80"))
    assert (instrument.min_notional, instrument.max_notional) == (D("5"), D("9000000"))
    assert instrument.not_applied == ("ICEBERG_PARTS", "MAX_NUM_ALGO_ORDERS", "MAX_NUM_ORDERS",
                                      "PERCENT_PRICE_BY_SIDE", "TRAILING_DELTA")
    assert instrument.document["symbol"] == "BTCUSDT" and len(instrument.sha256) == 64


def test_an_instrument_a_spot_account_may_not_trade_is_stored_as_unusable():
    for changes in ({"status": "BREAK"}, {"isSpotTradingAllowed": False}, {"permissionSets": [["MARGIN"]]},
                    {"permissionSets": [["SPOT"], ["TRD_GRP_002"]]}, {"permissionSets": None, "permissions": []}):
        assert market.parse_instrument(exchange_info(instrument_doc(**changes))).usable is False, changes
    legacy = instrument_doc(permissionSets=None, permissions=["SPOT", "MARGIN"])
    del legacy["permissionSets"]
    assert market.parse_instrument(exchange_info(legacy)).usable is True


def lot(step: str = "0.00001", minimum: str = "0.00001", maximum: str = "9000") -> dict:
    return {"filterType": "LOT_SIZE", "minQty": minimum, "maxQty": maximum, "stepSize": step}


def market_lot(step: str = "0", minimum: str = "0", maximum: str = "80") -> dict:
    return {"filterType": "MARKET_LOT_SIZE", "minQty": minimum, "maxQty": maximum, "stepSize": step}


def price() -> dict:
    return {"filterType": "PRICE_FILTER", "minPrice": "0.01", "maxPrice": "1000000", "tickSize": "0.01"}


def test_a_coarser_market_step_and_the_tighter_quantity_range_apply():
    coarser = market.parse_instrument(exchange_info(instrument_doc(filters=[
        price(), lot(), market_lot("0.0001", "0.0002", "50"),
        {"filterType": "MIN_NOTIONAL", "minNotional": "10", "applyToMarket": True, "avgPriceMins": 5}])))
    assert (coarser.step_size, coarser.min_qty, coarser.max_qty, coarser.min_notional, coarser.max_notional) == (
        D("0.0001"), D("0.0002"), D("50"), D("10"), None)
    finer = market.parse_instrument(exchange_info(instrument_doc(filters=[price(), lot(), market_lot("0.000001")])))
    assert finer.step_size == D("0.00001")


@pytest.mark.parametrize(("filters", "code"), [
    ([lot()], "instrument_required_filters"),
    ([price()], "instrument_required_filters"),
    ([price(), lot(), lot()], "instrument_required_filters"),
    ([price(), lot(step="0")], "invalid_decimal"),
    ([price(), lot(), market_lot(maximum="0")], "instrument_market_lot_zero_max"),
    ([price(), lot(step="0.00002"), market_lot(step="0.00003")], "instrument_incommensurate_steps"),
    ([price(), lot(minimum="2", maximum="1")], "instrument_lot_range_empty"),
    ([price(), lot(), {"filterType": "NOTIONAL", "minNotional": "10", "maxNotional": "5"}],
     "instrument_notional_range_empty"),
    ([price(), {"filterType": "LOT_SIZE", "minQty": "0.00001", "stepSize": "0.00001"}], "instrument_filter_fields"),
])
def test_an_instrument_whose_filters_cannot_be_read_is_refused(filters, code):
    with pytest.raises(PayloadError, match=code):
        market.parse_instrument(exchange_info(instrument_doc(filters=filters)))


def test_an_instrument_answer_of_another_shape_is_refused():
    for body, code in ((b"[]", "invalid_exchange_info"), (exchange_info(instrument_doc(symbol="ETHUSDT")),
                                                          "instrument_missing_or_ambiguous"),
                       (exchange_info(instrument_doc(), instrument_doc()), "instrument_missing_or_ambiguous"),
                       (exchange_info(instrument_doc(baseAsset="ETH")), "instrument_assets"),
                       (exchange_info(instrument_doc(status=None)), "instrument_status"),
                       (exchange_info(instrument_doc(filters={"x": 1})), "instrument_filters")):
        with pytest.raises(PayloadError, match=code):
            market.parse_instrument(body)


def test_the_book_is_ten_levels_a_side_best_first_as_exact_decimals():
    kind, quote = market.parse_stream(depth(update_id=42))
    assert kind == "quote" and quote.update_id == 42
    assert (quote.bid, quote.bid_qty, quote.ask, quote.ask_qty) == (D("60000.00"), D("0.5"), D("60000.01"),
                                                                    D("0.75"))
    assert len(quote.bids) == len(quote.asks) == 10
    assert quote.bids[-1][0] == D("59999.91") and quote.asks[-1][0] == D("60000.10")


@pytest.mark.parametrize(("frame", "code"), [
    (depth(bid="60000.02"), "crossed_quote"),
    (depth(bids=[["60000.00", "1"], ["60000.01", "1"]]), "unordered_book_levels"),
    (depth(asks=[["60000.02", "1"], ["60000.01", "1"]]), "unordered_book_levels"),
    (depth(bids=[["60000.00", "0"]]), "invalid_decimal"),
    (depth(bids=[]), "invalid_book_levels"),
    (depth(bids=[["60000.00", "1", "x"]]), "invalid_book_level"),
    (depth(lastUpdateId="7"), "invalid_book"),
    (depth(bids=[[60000.0, "1"]]), "invalid_decimal"),
])
def test_a_book_of_another_shape_is_refused_whole(frame, code):
    with pytest.raises(PayloadError, match=code):
        market.parse_stream(frame)


def test_a_candle_is_final_only_when_the_provider_closed_it():
    kind, bar = market.parse_stream(kline(T0_MS, T0_MS + 30_000, False))
    assert kind == "bar" and (bar.open_ms, bar.final, bar.event_ms, bar.close) == (T0_MS, False, T0_MS + 30_000,
                                                                                   D("60010.00"))
    assert market.parse_stream(kline(T0_MS, T0_MS + MINUTE, True))[1].final
    with pytest.raises(PayloadError, match="premature_final_candle"):
        market.parse_stream(kline(T0_MS, T0_MS + 30_000, True))
    with pytest.raises(PayloadError, match="invalid_stream_kline"):
        market.parse_stream(kline(T0_MS, T0_MS + 1, False, i="5m"))
    with pytest.raises(PayloadError, match="candle_ohlc"):
        market.parse_stream(kline(T0_MS, T0_MS + 1, False, l="60011.00"))
    with pytest.raises(PayloadError, match="candle_alignment"):
        market.parse_stream(kline(T0_MS + 1, T0_MS + 2, False, T=T0_MS + MINUTE))
    with pytest.raises(PayloadError, match="unexpected_stream"):
        market.parse_stream(json.dumps({"stream": "btcusdt@bookTicker", "data": {}}).encode())
    with pytest.raises(PayloadError, match="invalid_stream_envelope"):
        market.parse_stream(b'{"stream": "btcusdt@kline_1m"}')


def test_a_rest_candle_is_final_only_when_it_closed_before_the_providers_clock():
    rows = [rest_row(T0_MS), rest_row(T0_MS + MINUTE)]
    parsed = market.parse_rest_klines(json.dumps(rows).encode(), T0_MS + MINUTE + 1)
    assert [(bar.open_ms, bar.final) for bar in parsed] == [(T0_MS, True), (T0_MS + MINUTE, False)]
    with pytest.raises(PayloadError, match="out_of_order_klines"):
        market.parse_rest_klines(json.dumps(list(reversed(rows))).encode(), T0_MS)
    with pytest.raises(PayloadError, match="invalid_kline_row"):
        market.parse_rest_klines(json.dumps([rest_row(T0_MS)[:11]]).encode(), T0_MS)
    with pytest.raises(PayloadError, match="candle_interval"):
        market.parse_rest_klines(json.dumps([rest_row(T0_MS, interval=DAY)]).encode(), T0_MS)


def test_a_day_is_final_a_minute_after_its_close_by_the_providers_clock():
    day = T0_MS - T0_MS % DAY - DAY
    body = json.dumps([daily_row(day - DAY), daily_row(day)]).encode()
    closed = day + DAY - 1
    assert [d.final for d in market.parse_rest_daily_klines(body, closed + 60_000)] == [True, False]
    assert [d.final for d in market.parse_rest_daily_klines(body, closed + 60_001)] == [True, True]
    with pytest.raises(PayloadError, match="candle_alignment"):
        market.parse_rest_daily_klines(json.dumps([rest_row(T0_MS + MINUTE)]).encode(), T0_MS)
    assert market.FIRST_DAY_MS == int(datetime(2017, 8, 17, tzinfo=UTC).timestamp() * 1000)


# Binance's BTCUSDT days 2018-02-07 to 2018-02-09 as data-api.binance.vision answered them, OBSERVED on 2026-11-12 on the
# owner's PC: trading halted early on 2018-02-08 and the exchange closed that day at 00:28:14.788 UTC. In the whole
# history (3,374 days to 2026-11-11, none missing) it is the only day whose close is not the day's last millisecond.
THE_DAY_BEFORE = [1517961600000, "7655.02000000", "8476.00000000", "7150.01000000", "7599.00000000", "60778.46049700",
                  1518047999999, "477935038.81177692", 514893, "30084.83626600", "237137973.45313893", "0"]
HALTED_DAY = [1518048000000, "7599.00000000", "7844.00000000", "7572.09000000", "7784.02000000", "1521.53731800",
              1518049694788, "11770168.04386595", 12417, "844.25881300", "6532638.63751892", "0"]
THE_DAY_AFTER = [1518134400000, "7789.90000000", "8738.00000000", "7789.90000000", "8683.92000000", "20482.91082500",
                 1518220799999, "173348469.81187892", 273091, "10404.04079200", "88117562.12096504", "0"]


def closing_at(row: list, close_ms: int) -> list:
    return row[:6] + [close_ms] + row[7:]


def test_a_day_the_exchange_closed_early_is_kept_as_it_records_it_and_final_after_the_days_end():
    body = json.dumps([THE_DAY_BEFORE, HALTED_DAY, THE_DAY_AFTER]).encode()
    days = market.parse_rest_daily_klines(body, T0_MS)
    assert [(d.open_ms, d.close, d.close_ms, d.closed_early, d.final) for d in days] == [
        (1517961600000, D("7599"), 1518047999999, False, True),
        (1518048000000, D("7784.02"), 1518049694788, True, True),
        (1518134400000, D("8683.92"), 1518220799999, False, True)]
    halted = days[1]
    assert (halted.open, halted.high, halted.low, halted.volume, halted.trades) == (
        D("7599"), D("7844"), D("7572.09"), D("1521.537318"), 12417)
    # Final a minute after the day's own end, as every day, not a minute after its early close.
    end = HALTED_DAY[0] + DAY - 1
    assert not market.parse_rest_daily_klines(json.dumps([HALTED_DAY]).encode(), end + 60_000)[0].final
    assert market.parse_rest_daily_klines(json.dumps([HALTED_DAY]).encode(), end + 60_001)[0].final
    # A close outside its day is refused; a minute's candle still closes at its end.
    for close_ms in (HALTED_DAY[0] - 1, end + 1):
        with pytest.raises(PayloadError, match="candle_interval"):
            market.parse_rest_daily_klines(json.dumps([closing_at(HALTED_DAY, close_ms)]).encode(), T0_MS)
    with pytest.raises(PayloadError, match="candle_interval"):
        market.parse_rest_klines(json.dumps([closing_at(rest_row(T0_MS), T0_MS + 30_000)]).encode(), T0_MS * 2)


def test_longer_candles_are_calculated_from_the_minutes_and_say_when_one_is_missing():
    start = T0_MS - T0_MS % 14_400_000
    minutes = [market.parse_rest_klines(json.dumps([rest_row(start + n * MINUTE)]).encode(), T0_MS * 2)[0]
               for n in range(240) if n != 7]
    built = bars.aggregate(minutes, market.INTERVALS["4h"])
    assert [(c.open_ms, c.minutes, c.expected, c.complete) for c in built] == [(start, 239, 240, False)]
    hours = bars.aggregate(minutes, market.INTERVALS["1h"])
    assert [c.complete for c in hours] == [False, True, True, True]
    with pytest.raises(ValueError, match="unsupported_interval"):
        bars.aggregate(minutes, 120_000)


# ---- the client ------------------------------------------------------------------------------------------------

def test_the_client_sends_only_its_public_paths_to_its_own_host(monkeypatch):
    sent = []

    async def get(self, path, parameters, weight, **options):
        sent.append((self.HOST, path, parameters, weight))
        return exchange_info()

    monkeypatch.setattr(provider.PublicBinance, "get", get)

    async def calls():
        spot = provider.PublicBinance()
        try:
            await spot.instrument()
            await spot.klines("1m", T0_MS, T0_MS + 5 * MINUTE - 1, 5)
            await spot.klines("1d", market.FIRST_DAY_MS, market.FIRST_DAY_MS + 1000 * DAY - 1, 1000)
            for bad in (lambda: spot.klines("1h", T0_MS, T0_MS + 1, 1), lambda: spot.klines("1m", T0_MS, T0_MS + 1,
                                                                                            1001),
                        lambda: spot.klines("1m", T0_MS, T0_MS, 1)):
                with pytest.raises(ValueError):
                    await bad()
        finally:
            await spot.close()

    asyncio.run(calls())
    assert sent == [
        ("data-api.binance.vision", "/api/v3/exchangeInfo", {"symbol": "BTCUSDT"}, 20),
        ("data-api.binance.vision", "/api/v3/klines", {"symbol": "BTCUSDT", "interval": "1m", "startTime": T0_MS,
                                                      "endTime": T0_MS + 5 * MINUTE - 1, "limit": 5}, 2),
        ("data-api.binance.vision", "/api/v3/klines", {"symbol": "BTCUSDT", "interval": "1d",
                                                      "startTime": market.FIRST_DAY_MS,
                                                      "endTime": market.FIRST_DAY_MS + 1000 * DAY - 1,
                                                      "limit": 1000}, 2)]
    assert provider.PublicBinance.PATHS == ("/api/v3/time", "/api/v3/exchangeInfo", "/api/v3/klines")


def test_a_path_not_allowed_or_a_private_parameter_is_never_sent():
    async def attempts():
        spot = provider.PublicBinance()
        try:
            with pytest.raises(provider.ProviderUnavailable, match="provider_path_not_allowed"):
                await spot.get("/api/v3/account", {}, 1)
            for key in ("signature", "timestamp", "apiKey"):
                with pytest.raises(provider.ProviderUnavailable, match="private_request_forbidden"):
                    await spot.get("/api/v3/klines", {key: "x"}, 1)
        finally:
            await spot.close()

    asyncio.run(attempts())


def test_the_declared_allowance_sets_the_ip_wide_guard(monkeypatch):
    reports = []

    async def report(entry):
        reports.append(entry)

    async def resolved(_host):
        return "8.8.8.8"

    async def answered(request, **_kwargs):
        content = exchange_info() if request.url.path == "/api/v3/exchangeInfo" else b'{"serverTime": 1}'
        return httpx.Response(200, request=request, content=content, headers={"X-MBX-USED-WEIGHT-1M": "133"})

    async def exercise():
        spot = provider.PublicBinance()
        spot.bind(stop=asyncio.Event(), report=report)
        monkeypatch.setattr(spot.client, "send", answered)
        try:
            assert (spot.budget.allowance, spot.budget.guard) == (None, 120)
            market.parse_instrument(await spot.instrument())
            assert (spot.budget.allowance, spot.budget.ceiling, spot.budget.guard) == (6000, 120, 3000)
            await spot.instrument()  # the same allowance again is not reported again
        finally:
            await spot.close()

    monkeypatch.setattr(provider, "resolve_public_ip", resolved)
    asyncio.run(exercise())
    assert reports == [{"kind": "allowance", "allowance": 6000, "ceiling": 120, "guard": 3000}]


def test_the_stream_takes_the_book_and_the_candle_on_one_connection_to_the_checked_address(monkeypatch):
    opened = []

    async def resolve(host):
        assert host == "data-stream.binance.vision"
        return "203.0.113.9"

    monkeypatch.setattr(provider, "resolve_public_ip", resolve)
    monkeypatch.setattr(provider, "connect", lambda url, **options: opened.append((url, options)) or "socket")

    async def one():
        spot = provider.PublicBinance()
        try:
            return await spot.connect_stream()
        finally:
            await spot.close()

    assert asyncio.run(one()) == "socket"
    assert [url for url, _ in opened] == [
        "wss://data-stream.binance.vision:443/stream?streams=btcusdt%40depth10%40100ms%2Fbtcusdt%40kline_1m"]
    assert (opened[0][1]["host"], opened[0][1]["port"], opened[0][1]["proxy"]) == ("203.0.113.9", 443, None)


def test_only_the_two_market_data_hosts_are_ever_resolved():
    assert provider.HOSTS == ("data-api.binance.vision", "data-stream.binance.vision")
    for host in ("api.binance.com", "fapi.binance.com", "fstream.binance.com", "stream.binance.com"):
        with pytest.raises(provider.ProviderUnavailable, match="destination_not_allowed"):
            asyncio.run(provider.resolve_public_ip(host))


# ---- the feed --------------------------------------------------------------------------------------------------

class Clock:
    def __init__(self, at: datetime = T0):
        self.at = at
        self.mono = 1000.0

    def __call__(self) -> datetime:
        return self.at

    def monotonic(self) -> float:
        return self.mono

    def advance(self, seconds: float) -> None:
        self.at += timedelta(seconds=seconds)
        self.mono += seconds

    def ms(self) -> int:
        return int(self.at.timestamp() * 1000)


def offline_feed(clock: Clock, fake: FakeSpot | None = None) -> feed.SpotFeed:
    spot = feed.SpotFeed(None, fake or FakeSpot(now_ms=clock.ms), clock=clock, monotonic=clock.monotonic)
    spot.calls, spot.answers = [], {}

    async def db(fn, *args, **kwargs):
        spot.calls.append((fn.__name__, args, kwargs))
        answer = spot.answers.get(fn.__name__)
        return answer(*args, **kwargs) if callable(answer) else answer

    spot.db = db
    return spot


def test_the_feed_keeps_the_newest_book_of_each_second_and_never_reopens_a_final_candle():
    clock = Clock()
    spot = offline_feed(clock)
    assert spot.take(depth(update_id=1), clock()) == "quote"
    clock.advance(0.5)
    spot.take(depth(update_id=2), clock())
    clock.advance(0.6)
    spot.take(depth(update_id=3), clock())
    assert {second: item.update_id for second, (item, _) in spot.quotes.items()} == {
        int(T0.timestamp()): 2, int(T0.timestamp()) + 1: 3}
    spot.take(kline(T0_MS, T0_MS + MINUTE, True), clock())
    assert spot.take(kline(T0_MS, T0_MS + 50_000, False), clock()) == "bar"
    assert spot.bars[T0_MS][0].final
    assert spot.take(b'{"stream": "x"}', clock()) is None and spot.frames_refused == 1


def test_a_candle_from_ahead_of_the_measured_clock_is_dropped_and_the_clock_checked_again():
    clock = Clock()
    spot = offline_feed(clock)
    spot.clock_offset_ms, spot.clock_uncertainty_ms, spot.clock_verified = 0.0, 5.0, True
    assert spot.take(kline(T0_MS, clock.ms() + 1_900, False), clock()) == "bar"
    assert spot.take(kline(T0_MS, clock.ms() + 2_500, False), clock()) is None
    assert not spot.clock_verified and spot.recheck.is_set() and len(spot.bars) == 1


def test_the_writer_writes_only_seconds_that_are_over_and_keeps_what_a_failed_write_held():
    clock = Clock(T0 + timedelta(milliseconds=200))
    spot = offline_feed(clock)
    spot.take(depth(update_id=1), clock())
    spot.take(kline(T0_MS, T0_MS + 100, False), clock())
    asyncio.run(spot.write())
    name, _, written = spot.calls[-1]
    assert name == "write_second" and written["quotes"] == [] and len(written["bars"]) == 1
    assert written["state"]["status"] == "UNAVAILABLE" and len(spot.quotes) == 1 and not spot.bars
    clock.advance(1)

    def broken(*_args, **_kwargs):
        raise RuntimeError("database down")

    spot.answers["write_second"] = broken
    asyncio.run(spot.write())
    assert len(spot.quotes) == 1
    spot.answers.clear()
    asyncio.run(spot.write())
    assert [item.update_id for item, _ in spot.calls[-1][2]["quotes"]] == [1] and not spot.quotes


def test_the_state_is_connected_only_with_the_stream_a_verified_clock_a_usable_instrument_and_a_fresh_book():
    clock = Clock()
    spot = offline_feed(clock)
    assert spot.status() == ("UNAVAILABLE", "STREAM_DISCONNECTED")
    spot.connected = True
    assert spot.status() == ("UNAVAILABLE", "CLOCK_UNVERIFIED")
    spot.clock_verified, spot.clock_checked = True, clock.monotonic()
    assert spot.status() == ("UNAVAILABLE", "INSTRUMENT_UNVERIFIED")
    spot.instrument_usable, spot.instrument_checked = True, clock.monotonic()
    assert spot.status() == ("DEGRADED", "QUOTE_STALE")
    spot.take(depth(), clock())
    assert spot.status() == ("CONNECTED", None) and spot.state()["clock_verified"] is True
    clock.advance(6)
    assert spot.status() == ("DEGRADED", "QUOTE_STALE")
    spot.take(depth(), clock())
    clock.advance(feed.CLOCK_VALID_SECONDS - 5)  # 151 s after the last check
    spot.take(depth(), clock())
    assert spot.status() == ("UNAVAILABLE", "CLOCK_UNVERIFIED") and spot.state()["clock_verified"] is False


def test_the_clock_and_the_instrument_are_checked_and_stored():
    clock = Clock()
    fake = FakeSpot(now_ms=clock.ms, offset_ms=120.0, uncertainty_ms=40.0)
    spot = offline_feed(clock, fake)
    spot.answers["record_instrument"] = 5
    asyncio.run(spot.check_clock())
    asyncio.run(spot.check_instrument())
    assert spot.clock_verified and spot.measured.is_set() and spot.instrument_usable
    stored = [call for call in spot.calls if call[0] == "update_state"][0][1][0]
    assert stored["clock_verified"] is True and stored["clock_offset_ms"] == 120.0
    assert [call[0] for call in spot.calls if call[0] == "record_instrument"] == ["record_instrument"]
    late = FakeSpot(now_ms=clock.ms, offset_ms=1500.0)
    spot = offline_feed(clock, late)
    asyncio.run(spot.check_clock())
    assert not spot.clock_verified
    fake.info = b"{}"
    spot = offline_feed(clock, fake)
    asyncio.run(spot.check_instrument())
    assert not spot.instrument_usable and spot.calls[-1][1][0] == "INSTRUMENT_CHECK_FAILED"


def test_history_asks_only_for_the_closed_minutes_the_store_lacks_and_remembers_what_binance_has_not():
    clock = Clock()
    fake = FakeSpot(now_ms=clock.ms)
    spot = offline_feed(clock, fake)
    spot.clock_offset_ms, spot.clock_uncertainty_ms = 0.0, 0.0
    end = T0_MS
    gap = [end - 3 * MINUTE, end - 2 * MINUTE, end - MINUTE]
    spot.answers["missing_minutes"] = lambda start, stop: [m for m in gap if start <= m < stop]
    fake.missing = {end - 2 * MINUTE}
    stored, lacking = asyncio.run(spot.fill_history())
    assert (stored, lacking) == (2, False)
    assert fake.calls == [("klines", "1m", end - 3 * MINUTE, end - 1, 3)]
    assert spot.absent == {end - 2 * MINUTE}
    fake.calls.clear()
    spot.answers["missing_minutes"] = lambda start, stop: [end - 2 * MINUTE]
    assert asyncio.run(spot.fill_history()) == (0, False) and fake.calls == []


def test_every_day_since_2017_is_asked_for_in_four_requests_and_a_day_binance_lacks_is_not_asked_again():
    clock = Clock()
    fake = FakeSpot(now_ms=clock.ms)
    spot = offline_feed(clock, fake)
    spot.clock_offset_ms, spot.clock_uncertainty_ms = 0.0, 0.0
    have: set[int] = set()

    def write_daily(days, _received):
        new = [day.open_ms for day in days if day.open_ms not in have]
        have.update(new)
        return len(new)

    spot.answers["stored_days"] = lambda start, stop: {day for day in have if start <= day < stop}
    spot.answers["write_daily"] = write_daily
    fake.missing_days = {market.FIRST_DAY_MS + 10 * DAY}
    stored, lacking = asyncio.run(spot.fill_daily())
    today = T0_MS - T0_MS % DAY
    expected = (today - market.FIRST_DAY_MS) // DAY
    assert (stored, lacking) == (expected - 1, False)
    assert [call[1] for call in fake.calls] == ["1d"] * 4
    assert fake.calls[0] == ("klines", "1d", market.FIRST_DAY_MS, market.FIRST_DAY_MS + 1000 * DAY - 1, 1000)
    assert spot.absent_days == {market.FIRST_DAY_MS + 10 * DAY}
    assert max(have) == today - DAY
    fake.calls.clear()
    assert asyncio.run(spot.fill_daily()) == (0, False) and fake.calls == []


def test_a_day_the_exchange_closed_early_is_stored_with_the_rest_and_noted_once():
    clock = Clock()
    fake = FakeSpot(now_ms=clock.ms)
    spot = offline_feed(clock, fake)
    spot.clock_offset_ms, spot.clock_uncertainty_ms = 0.0, 0.0
    have: set[int] = set()

    def write_daily(days, _received):
        new = [day.open_ms for day in days if day.open_ms not in have]
        have.update(new)
        return len(new)

    spot.answers["stored_days"] = lambda start, stop: {day for day in have if start <= day < stop}
    spot.answers["write_daily"] = write_daily
    halted = market.FIRST_DAY_MS + 175 * DAY  # 2018-02-08, in the first request's thousand days
    fake.closed_early = {halted: halted + 1_694_788}
    stored, lacking = asyncio.run(spot.fill_daily())
    today = T0_MS - T0_MS % DAY
    assert (stored, lacking) == ((today - market.FIRST_DAY_MS) // DAY, False)
    assert halted in have and spot.absent_days == set()
    notes = [(args[0], args[2]) for name, args, _ in spot.calls if name == "record_event"]
    assert notes == [("DAILY_CLOSED_EARLY", {"day": "2018-02-08", "closed_at": "2018-02-08T00:28:14.788000+00:00",
                                             "trades": 5000})]
    spot.calls.clear()
    assert asyncio.run(spot.fill_daily()) == (0, False)
    assert not [name for name, _, _ in spot.calls if name == "record_event"]


def test_the_day_a_midnight_closed_waits_a_minute_and_the_daily_job_waits_for_it():
    midnight = datetime(2026, 11, 12, tzinfo=UTC)
    clock = Clock(midnight + timedelta(seconds=30))
    fake = FakeSpot(now_ms=clock.ms)
    spot = offline_feed(clock, fake)
    spot.clock_offset_ms, spot.clock_uncertainty_ms = 0.0, 0.0
    have = set(range(market.FIRST_DAY_MS, int(midnight.timestamp() * 1000) - DAY, DAY))
    spot.answers["stored_days"] = lambda start, stop: {day for day in have if start <= day < stop}
    spot.answers["write_daily"] = lambda days, _received: len(days)
    assert asyncio.run(spot.fill_daily()) == (0, True)  # yesterday is not final 30 s after midnight
    assert spot.absent_days == set()
    now_ms = clock.ms()
    assert feed.daily_wait_seconds(now_ms, lacking=True) == 60.0
    assert feed.daily_wait_seconds(now_ms + 120_000, lacking=True) == feed.DAILY_RETRY_SECONDS
    assert feed.daily_wait_seconds(now_ms + 120_000, lacking=False) == (DAY - 150_000) / 1000 + 90


def test_the_feed_stops_its_parts_and_closes_its_client():
    clock = Clock()
    fake = FakeSpot(now_ms=clock.ms)
    spot = offline_feed(clock, fake)
    spot.answers["schema_ready"] = True

    async def run_and_stop():
        task = asyncio.create_task(spot.run())
        await asyncio.sleep(0.05)
        spot.stop.set()
        await asyncio.wait_for(task, 5)

    asyncio.run(run_and_stop())
    assert fake.closed and fake.bound is not None
    assert spot.calls[-1][0] == "update_state" and spot.calls[-1][1][0]["reason"] == "FEED_STOPPED"


def test_the_filters_of_the_fixture_are_the_documented_kinds():
    assert {f["filterType"] for f in FILTERS} >= {"PRICE_FILTER", "LOT_SIZE", "MARKET_LOT_SIZE", "NOTIONAL"}
