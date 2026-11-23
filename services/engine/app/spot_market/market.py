"""BTCUSDT's public spot market data: what is collected, and strict parsing of Binance's answers (ExecPlan 0060
section 4.5).

Sources (ExecPlan 0060 section 7, read 2026-11-12): the market-data-only REST host ``data-api.binance.vision`` and
stream host ``data-stream.binance.vision`` M2 used. One combined stream carries the partial book depth (the ten best
levels of each side every 100 ms: ``lastUpdateId``, ``bids``, ``asks``, without an event time) and the 1-minute
candle (``k.x``: closed). A connection is valid for 24 hours; the server pings every 20 seconds.

The account trades on the book's levels (``app.spot.money`` walks them); the rule reads Binance's final 1-day candles,
every one since the first BTCUSDT spot day, 2017-08-17. The book is not executable: its quantities are displayed
liquidity only.

Every value is exact: prices and quantities are ``Decimal`` from the provider's decimal strings, times UTC
milliseconds. Anything that does not have the documented shape is refused (``PayloadError``), never guessed.
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.execution.numbers import is_multiple
from app.spot_market.parse import (
    PayloadError,
    decode_json,
    exact_decimal,
    spot_permitted,
    utc_from_ms,
)

SYMBOL = "BTCUSDT"
REST_HOST = "data-api.binance.vision"
STREAM_HOST = "data-stream.binance.vision"
BOOK_STREAM = "btcusdt@depth10@100ms"
KLINE_STREAM = "btcusdt@kline_1m"
STREAMS = (BOOK_STREAM, KLINE_STREAM)
MINUTE_MS = 60_000
DAY_MS = 86_400_000
# Binance's first BTCUSDT spot day (2017-08-17 00:00 UTC): the daily history starts here.
FIRST_DAY_MS = 1_502_928_000_000
KLINE_ROWS_MAX = 1000
BOOK_LEVELS_MAX = 20
# A day is final a minute after its end by the provider's clock: its last trades are in.
DAY_SETTLE_MS = 60_000
# The chart's intervals built from the stored 1-minute candles; ``1d`` reads the daily candles.
INTERVALS = {"1m": 60_000, "5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000}
# The filters a market order is checked against; every other filter is kept in the document and named.
APPLIED_FILTERS = ("PRICE_FILTER", "LOT_SIZE", "MARKET_LOT_SIZE", "NOTIONAL", "MIN_NOTIONAL")

Level = tuple[Decimal, Decimal]


def canonical_hash(value: Any) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def at(ms: int) -> datetime:
    return utc_from_ms(ms)


@dataclass(frozen=True)
class Instrument:
    """BTCUSDT's entry of ``exchangeInfo`` and a market order's combined filters: the lot step (``LOT_SIZE`` with
    ``MARKET_LOT_SIZE`` where that one's step is not 0), the quantity range of both, and the notional range of
    ``NOTIONAL`` and ``MIN_NOTIONAL``, applied in full whatever their ``applyToMarket`` flags say."""
    symbol: str
    status: str
    usable: bool
    tick_size: Decimal
    step_size: Decimal
    min_qty: Decimal
    max_qty: Decimal
    min_notional: Decimal
    max_notional: Decimal | None
    not_applied: tuple[str, ...]
    sha256: str
    document: dict[str, Any]


def _value(item: dict[str, Any], key: str, *, positive: bool = False) -> Decimal:
    if key not in item:
        raise PayloadError("instrument_filter_fields")
    return exact_decimal(item[key], positive=positive)


def parse_instrument(body: bytes) -> Instrument:
    """BTCUSDT's entry of a ``GET /api/v3/exchangeInfo?symbol=BTCUSDT`` answer. A filter this account cannot read
    refuses the answer; a status other than ``TRADING`` or a symbol a spot account may not trade is stored as
    unusable."""
    data = decode_json(body)
    if not isinstance(data, dict) or not isinstance(data.get("symbols"), list):
        raise PayloadError("invalid_exchange_info")
    matches = [item for item in data["symbols"] if isinstance(item, dict) and item.get("symbol") == SYMBOL]
    if len(matches) != 1:
        raise PayloadError("instrument_missing_or_ambiguous")
    item = matches[0]
    if item.get("baseAsset") != "BTC" or item.get("quoteAsset") != "USDT":
        raise PayloadError("instrument_assets")
    if not isinstance(item.get("status"), str) or not isinstance(item.get("isSpotTradingAllowed"), bool):
        raise PayloadError("instrument_status")
    filters = item.get("filters")
    if not isinstance(filters, list) or not all(isinstance(f, dict) and isinstance(f.get("filterType"), str)
                                                for f in filters):
        raise PayloadError("instrument_filters")
    by_type = {f["filterType"]: f for f in filters}
    if len(by_type) != len(filters) or "PRICE_FILTER" not in by_type or "LOT_SIZE" not in by_type:
        raise PayloadError("instrument_required_filters")
    tick = _value(by_type["PRICE_FILTER"], "tickSize", positive=True)
    lot = by_type["LOT_SIZE"]
    step, min_qty, max_qty = (_value(lot, "stepSize", positive=True), _value(lot, "minQty"),
                              _value(lot, "maxQty", positive=True))
    market_lot = by_type.get("MARKET_LOT_SIZE")
    if market_lot is not None:
        market_step, market_min, market_max = (_value(market_lot, "stepSize"), _value(market_lot, "minQty"),
                                               _value(market_lot, "maxQty"))
        if market_max <= 0:
            raise PayloadError("instrument_market_lot_zero_max")
        if market_step > 0:
            if is_multiple(market_step, step) and not is_multiple(step, market_step):
                step = market_step
            elif not is_multiple(step, market_step):
                raise PayloadError("instrument_incommensurate_steps")
        min_qty, max_qty = max(min_qty, market_min), min(max_qty, market_max)
    if min_qty > max_qty:
        raise PayloadError("instrument_lot_range_empty")
    min_notional, max_notional = Decimal(0), None
    for kind in ("NOTIONAL", "MIN_NOTIONAL"):
        notional = by_type.get(kind)
        if notional is None:
            continue
        min_notional = max(min_notional, _value(notional, "minNotional"))
        if kind == "NOTIONAL":
            maximum = _value(notional, "maxNotional", positive=True)
            max_notional = maximum if max_notional is None else min(max_notional, maximum)
    if max_notional is not None and min_notional > max_notional:
        raise PayloadError("instrument_notional_range_empty")
    usable = item["status"] == "TRADING" and item["isSpotTradingAllowed"] and spot_permitted(item)
    return Instrument(
        symbol=SYMBOL, status=item["status"][:24], usable=usable, tick_size=tick, step_size=step, min_qty=min_qty,
        max_qty=max_qty, min_notional=min_notional, max_notional=max_notional,
        not_applied=tuple(sorted(kind for kind in by_type if kind not in APPLIED_FILTERS)),
        sha256=canonical_hash(item), document=item)


@dataclass(frozen=True)
class Quote:
    """One partial depth snapshot: the best levels of each side as (price, quantity), best first."""
    update_id: int
    bids: tuple[Level, ...]
    asks: tuple[Level, ...]

    @property
    def bid(self) -> Decimal:
        return self.bids[0][0]

    @property
    def bid_qty(self) -> Decimal:
        return self.bids[0][1]

    @property
    def ask(self) -> Decimal:
        return self.asks[0][0]

    @property
    def ask_qty(self) -> Decimal:
        return self.asks[0][1]


@dataclass(frozen=True)
class Bar:
    """A 1-minute candle. ``final`` only once the provider marked it closed, or REST returned it after its close."""
    open_ms: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    quote_volume: Decimal
    trades: int
    final: bool
    event_ms: int | None


@dataclass(frozen=True)
class DailyBar:
    """One UTC day, as the provider closed it. ``close_ms`` is the provider's close time: the day's last millisecond,
    or earlier when the exchange closed the day early (a trading halt)."""
    open_ms: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    quote_volume: Decimal
    trades: int
    final: bool
    close_ms: int

    @property
    def closed_early(self) -> bool:
        return self.close_ms < self.open_ms + DAY_MS - 1


def _timestamp(value: Any) -> int:
    utc_from_ms(value)
    return value


def _candle(open_ms: Any, close_ms: Any, values: tuple[Any, ...], quote_volume: Any, trades: Any,
            interval_ms: int, *, early_close: bool = False
            ) -> tuple[int, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, int]:
    """A candle's fields, checked. Its close is the interval's last millisecond; with ``early_close`` it may lie
    earlier inside the interval, never before its open nor after its end."""
    if type(open_ms) is not int or open_ms < 0 or open_ms % interval_ms != 0:
        raise PayloadError("candle_alignment")
    end = open_ms + interval_ms - 1
    if type(close_ms) is not int or close_ms > end or close_ms < (open_ms if early_close else end):
        raise PayloadError("candle_interval")
    utc_from_ms(close_ms)
    if type(trades) is not int or trades < 0:
        raise PayloadError("candle_trades")
    opened, high, low, closed = (exact_decimal(value, positive=True) for value in values[:4])
    if low > min(opened, closed) or high < max(opened, closed):
        raise PayloadError("candle_ohlc")
    return open_ms, opened, high, low, closed, exact_decimal(values[4]), exact_decimal(quote_volume), trades


def _levels(value: Any, descending: bool) -> tuple[Level, ...]:
    if not isinstance(value, list) or not 1 <= len(value) <= BOOK_LEVELS_MAX:
        raise PayloadError("invalid_book_levels")
    levels = []
    for level in value:
        if not isinstance(level, list) or len(level) != 2:
            raise PayloadError("invalid_book_level")
        levels.append((exact_decimal(level[0], positive=True), exact_decimal(level[1], positive=True)))
    prices = [price for price, _ in levels]
    ordered = all(a > b for a, b in zip(prices, prices[1:], strict=False)) if descending \
        else all(a < b for a, b in zip(prices, prices[1:], strict=False))
    if not ordered:
        raise PayloadError("unordered_book_levels")
    return tuple(levels)


def parse_stream(body: bytes) -> tuple[str, Quote | Bar]:
    """One message of the combined stream: ``{"stream": name, "data": event}``."""
    envelope = decode_json(body, max_bytes=262_144)
    if not isinstance(envelope, dict) or not isinstance(envelope.get("data"), dict):
        raise PayloadError("invalid_stream_envelope")
    data, stream = envelope["data"], envelope.get("stream")
    if stream == BOOK_STREAM:
        update_id = data.get("lastUpdateId")
        if type(update_id) is not int or update_id < 0:
            raise PayloadError("invalid_book")
        quote = Quote(update_id, _levels(data.get("bids"), True), _levels(data.get("asks"), False))
        if quote.bid >= quote.ask:
            raise PayloadError("crossed_quote")
        return "quote", quote
    if stream == KLINE_STREAM and data.get("e") == "kline":
        if data.get("s") != SYMBOL:
            raise PayloadError("unsupported_symbol")
        event_ms = _timestamp(data.get("E"))
        kline = data.get("k")
        if not isinstance(kline, dict) or kline.get("s") != SYMBOL or kline.get("i") != "1m" \
                or type(kline.get("x")) is not bool:
            raise PayloadError("invalid_stream_kline")
        if kline["x"] and type(kline.get("T")) is int and event_ms < kline["T"]:
            raise PayloadError("premature_final_candle")
        fields = _candle(kline.get("t"), kline.get("T"), tuple(kline.get(key) for key in ("o", "h", "l", "c", "v")),
                         kline.get("q"), kline.get("n"), MINUTE_MS)
        return "bar", Bar(*fields, kline["x"], event_ms)
    raise PayloadError("unexpected_stream")


def _rows(body: bytes) -> list[list[Any]]:
    rows = decode_json(body, max_bytes=1_048_576)
    if not isinstance(rows, list) or len(rows) > KLINE_ROWS_MAX:
        raise PayloadError("invalid_klines")
    for row in rows:
        if not isinstance(row, list) or len(row) != 12:
            raise PayloadError("invalid_kline_row")
    return rows


def _ascending(opens: list[int]) -> None:
    if any(opens[i] >= opens[i + 1] for i in range(len(opens) - 1)):
        raise PayloadError("out_of_order_klines")


def parse_rest_klines(body: bytes, server_lower_ms: int) -> list[Bar]:
    """``GET /api/v3/klines`` rows at ``1m``, ascending. A row is final only when its close lies before the lower
    bound of the provider's clock at the answer; the last, still open minute stays provisional."""
    bars = []
    for row in _rows(body):
        fields = _candle(row[0], row[6], tuple(row[1:6]), row[7], row[8], MINUTE_MS)
        bars.append(Bar(*fields, row[6] < server_lower_ms, None))
    _ascending([bar.open_ms for bar in bars])
    return bars


def parse_rest_daily_klines(body: bytes, server_lower_ms: int) -> list[DailyBar]:
    """``GET /api/v3/klines`` rows at ``1d``, ascending. A day is final only when its end lies at least a minute
    before the lower bound of the provider's clock at the answer: a stored day never changes and is read for years,
    so its last trades must be in. A day the exchange closed early is kept as the exchange records it, its close the
    last trade before the halt (BTCUSDT's 2018-02-08, `OBSERVED` on 2026-11-12, closes at 00:28:14.788 UTC); it is
    final, as every day, only a minute after the day's own end."""
    bars = []
    for row in _rows(body):
        fields = _candle(row[0], row[6], tuple(row[1:6]), row[7], row[8], DAY_MS, early_close=True)
        bars.append(DailyBar(*fields, fields[0] + DAY_MS - 1 + DAY_SETTLE_MS < server_lower_ms, row[6]))
    _ascending([bar.open_ms for bar in bars])
    return bars
