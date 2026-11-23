"""Candles of 5, 15, 60 and 240 minutes built from the stored 1-minute candles (ExecPlan 0060 section 4.5;
``app.perp.bars`` until then).

Binance's own longer candles are not collected: each longer candle is calculated here from the 1-minute ones of its
interval, so every intraday chart interval rests on the same stored record. A longer candle is ``complete`` only when
every minute of its interval is stored and final; one with a missing minute says how many it has.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

from app.spot_market import market


@dataclass(frozen=True)
class Candle:
    open_ms: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    minutes: int
    expected: int
    complete: bool


def aggregate(bars: Iterable[market.Bar], interval_ms: int) -> list[Candle]:
    """Group ascending 1-minute candles into candles of ``interval_ms``, ascending."""
    if interval_ms not in market.INTERVALS.values():
        raise ValueError("unsupported_interval")
    expected = interval_ms // market.MINUTE_MS
    candles: list[Candle] = []
    group: list[market.Bar] = []

    def close_group() -> None:
        if not group:
            return
        candles.append(Candle(
            open_ms=group[0].open_ms - group[0].open_ms % interval_ms, open=group[0].open,
            high=max(bar.high for bar in group), low=min(bar.low for bar in group), close=group[-1].close,
            volume=sum((bar.volume for bar in group), Decimal(0)), minutes=len(group), expected=expected,
            complete=len(group) == expected and all(bar.final for bar in group)))
        group.clear()

    previous: int | None = None
    for bar in bars:
        if previous is not None and bar.open_ms <= previous:
            raise ValueError("unordered_candles")
        previous = bar.open_ms
        if group and bar.open_ms - bar.open_ms % interval_ms != group[0].open_ms - group[0].open_ms % interval_ms:
            close_group()
        group.append(bar)
    close_group()
    return candles
