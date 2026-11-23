"""SYNTHETIC stand-ins for Binance's public spot answers (ExecPlan 0060 section 4.5), shaped as its spot API
documentation shows them (read 2026-11-12: exchangeInfo, klines, the partial book depth and kline streams). Every
price, quantity and filter value here is made up for the tests; none is a recorded market value.
"""

import asyncio
import json
from decimal import Decimal

from app.spot_market import market

MINUTE = market.MINUTE_MS
DAY = market.DAY_MS

FILTERS = [
    {"filterType": "PRICE_FILTER", "minPrice": "0.01000000", "maxPrice": "1000000.00000000", "tickSize": "0.01000000"},
    {"filterType": "LOT_SIZE", "minQty": "0.00001000", "maxQty": "9000.00000000", "stepSize": "0.00001000"},
    {"filterType": "ICEBERG_PARTS", "limit": 10},
    {"filterType": "MARKET_LOT_SIZE", "minQty": "0.00000000", "maxQty": "80.00000000", "stepSize": "0.00000000"},
    {"filterType": "TRAILING_DELTA", "minTrailingAboveDelta": 10, "maxTrailingAboveDelta": 2000,
     "minTrailingBelowDelta": 10, "maxTrailingBelowDelta": 2000},
    {"filterType": "PERCENT_PRICE_BY_SIDE", "bidMultiplierUp": "5", "bidMultiplierDown": "0.2",
     "askMultiplierUp": "5", "askMultiplierDown": "0.2", "avgPriceMins": 5},
    {"filterType": "NOTIONAL", "minNotional": "5.00000000", "applyMinToMarket": True,
     "maxNotional": "9000000.00000000", "applyMaxToMarket": False, "avgPriceMins": 5},
    {"filterType": "MAX_NUM_ORDERS", "maxNumOrders": 200},
    {"filterType": "MAX_NUM_ALGO_ORDERS", "maxNumAlgoOrders": 5},
]


def instrument_doc(**changes) -> dict:
    entry = {"symbol": "BTCUSDT", "status": "TRADING", "baseAsset": "BTC", "baseAssetPrecision": 8,
             "quoteAsset": "USDT", "quotePrecision": 8, "quoteAssetPrecision": 8, "baseCommissionPrecision": 8,
             "quoteCommissionPrecision": 8, "orderTypes": ["LIMIT", "LIMIT_MAKER", "MARKET"],
             "icebergAllowed": True, "ocoAllowed": True, "quoteOrderQtyMarketAllowed": True,
             "isSpotTradingAllowed": True, "isMarginTradingAllowed": True, "filters": FILTERS, "permissions": [],
             "permissionSets": [["SPOT", "MARGIN", "TRD_GRP_004"]]}
    entry.update(changes)
    return entry


def exchange_info(*entries: dict) -> bytes:
    limits = [{"rateLimitType": "REQUEST_WEIGHT", "interval": "MINUTE", "intervalNum": 1, "limit": 6000},
              {"rateLimitType": "ORDERS", "interval": "SECOND", "intervalNum": 10, "limit": 100},
              {"rateLimitType": "RAW_REQUESTS", "interval": "MINUTE", "intervalNum": 5, "limit": 61000}]
    return json.dumps({"timezone": "UTC", "serverTime": 1, "rateLimits": limits, "exchangeFilters": [],
                       "symbols": list(entries) or [instrument_doc()]}).encode()


def depth(bid: str = "60000.00", ask: str = "60000.01", update_id: int = 7, levels: int = 10, **changes) -> bytes:
    bids = [[format(Decimal(bid) - Decimal("0.01") * n, "f"), "0.50000000"] for n in range(levels)]
    asks = [[format(Decimal(ask) + Decimal("0.01") * n, "f"), "0.75000000"] for n in range(levels)]
    data = {"lastUpdateId": update_id, "bids": bids, "asks": asks}
    data.update(changes)
    return json.dumps({"stream": "btcusdt@depth10@100ms", "data": data}).encode()


def kline(open_ms: int, event_ms: int, final: bool, close: str = "60010.00", **changes) -> bytes:
    k = {"t": open_ms, "T": open_ms + MINUTE - 1, "s": "BTCUSDT", "i": "1m", "f": 100, "L": 200, "o": "60000.00",
         "c": close, "h": max("60020.00", close, key=Decimal), "l": "59990.00", "v": "12.50000000", "n": 40,
         "x": final, "q": "750000.00000000", "V": "6.00000000", "Q": "360000.00000000", "B": "0"}
    k.update(changes)
    return json.dumps({"stream": "btcusdt@kline_1m",
                       "data": {"e": "kline", "E": event_ms, "s": "BTCUSDT", "k": k}}).encode()


def rest_row(open_ms: int, close: str = "60010.00", interval: int = MINUTE) -> list:
    return [open_ms, "60000.00", max("60020.00", close, key=Decimal), "59990.00", close, "12.50000000",
            open_ms + interval - 1, "750000.00000000", 40, "6.00000000", "360000.00000000", "0"]


def daily_close(open_ms: int) -> str:
    """A made-up close for a day: a slow line with a weekly swing, so the rule has something to read."""
    n = (open_ms - market.FIRST_DAY_MS) // DAY
    return format(Decimal(4000) + Decimal(20) * n + Decimal(150) * (n % 7), "f")


def daily_row(open_ms: int, close_ms: int | None = None) -> list:
    """A SYNTHETIC day in Binance's format; ``close_ms`` earlier than the day's end for a day closed early."""
    close = daily_close(open_ms)
    return [open_ms, close, format(Decimal(close) + 100, "f"), format(Decimal(close) - 100, "f"), close,
            "1000.00000000", open_ms + DAY - 1 if close_ms is None else close_ms, "60000000.00000000", 5000,
            "500.00000000", "30000000.00000000", "0"]


class FakeSocket:
    """A connection that answers ``recv`` from a frame source, as ``websockets`` does."""

    def __init__(self, frames):
        self.frames = frames

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def recv(self):
        frame = await self.frames()
        if isinstance(frame, BaseException):
            raise frame
        return frame


class FakeSpot:
    """Stands in for ``app.spot_market.provider.PublicBinance``: the same methods, no network."""

    def __init__(self, *, now_ms, frames=None, offset_ms: float = 0.0, uncertainty_ms: float = 5.0):
        self.now_ms = now_ms
        self.frames = frames
        self.offset_ms, self.uncertainty_ms = offset_ms, uncertainty_ms
        self.calls: list[tuple] = []
        self.missing: set[int] = set()
        self.missing_days: set[int] = set()
        self.closed_early: dict[int, int] = {}  # a day's open: the close time the provider gives it
        self.info = exchange_info()
        self.closed = False
        self.bound = None

    def bind(self, *, stop, report):
        self.bound = (stop, report)

    async def close(self):
        self.closed = True

    async def best_clock(self, samples: int = 3):
        self.calls.append(("clock",))
        return int(self.now_ms() + self.offset_ms), self.offset_ms, self.uncertainty_ms

    async def instrument(self):
        self.calls.append(("instrument",))
        return self.info

    async def klines(self, interval, start_ms, end_ms, limit):
        """The candles opening in the request whose open has passed, the running one included (it parses as not
        final), those the provider lacks left out."""
        self.calls.append(("klines", interval, start_ms, end_ms, limit))
        now = self.now_ms() + self.offset_ms
        if interval == "1d":
            rows = [daily_row(at, self.closed_early.get(at)) for at in range(start_ms, end_ms + 1, DAY)
                    if at <= now and at not in self.missing_days][:limit]
        else:
            rows = [rest_row(at) for at in range(start_ms, end_ms + 1, MINUTE)
                    if at <= now and at not in self.missing][:limit]
        return json.dumps(rows).encode()

    async def connect_stream(self):
        self.calls.append(("connect",))
        source = self.frames
        if source is None:
            async def silent():
                await asyncio.sleep(3600)
            return FakeSocket(silent)
        return FakeSocket(source)
