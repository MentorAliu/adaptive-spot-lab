"""``SPOT_RULE_V1``: the daily reading that decides the main spot account (ExecPlan 0060 section 4.1).

``MAIN_RULE_V1``'s signal, volatility and size (ExecPlan 0059), on Binance's spot daily candles, trading the
difference: the sign of the last complete UTC day's close against the closes 30, 91 and 365 days before it, their
mean ``s``, never short (``max(s, 0)``); the annualized exponentially weighted volatility ``σ`` of the daily log
returns (centre of mass 60 days, at least 300 of the last 366 days stored); the target ``f = max(s, 0) · min(1,
0.05 / σ)`` of equity, quantized toward zero to 0.001 and 0 below 0.01. A target of 0 with BTC held sells it all;
otherwise a target more than 0.03 of equity from what is held buys or sells the difference; else nothing.

Pure functions: no clock, no database. Exact Decimal under the execution context, so the live engine and the backtest
(``app.spot.backtest``) agree to the digit on the same stored closes.
"""

from collections.abc import Mapping
from dataclasses import dataclass, replace
from decimal import ROUND_DOWN, Decimal, localcontext
from functools import lru_cache
from typing import Any

from app.execution.numbers import AMOUNT, CONTEXT, ZERO
from app.spot.definitions import DAY_MS, RULE, Rule

LONG, CASH, WARMUP = "LONG", "CASH", "WARMUP"
BUY, SELL, SELL_ALL, NO_CHANGE = "BUY", "SELL", "SELL_ALL", "NO_CHANGE"


def utc_day_open(at_ms: int) -> int:
    return at_ms - at_ms % DAY_MS


def sign_of(value: Decimal) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


@dataclass(frozen=True)
class Anchor:
    lookback_days: int
    day_open_ms: int
    close: Decimal
    sign: int


@dataclass(frozen=True)
class Reading:
    """The rule for one UTC day. ``day_open_ms`` is the day read (the last complete one before the reading's day).

    ``result``: ``LONG`` (a target above 0), ``CASH`` (a target of 0) or ``WARMUP`` (not readable: the day's close
    or an anchor is missing, or too few days are stored; ``reason`` says which). ``signal`` is ``s`` before the
    floor at 0, ``volatility`` is ``σ``, ``target`` is ``f``, ``held`` the caller's fraction and ``action`` what the
    account does: ``BUY``, ``SELL``, ``SELL_ALL`` or ``NO_CHANGE``."""
    result: str
    day_open_ms: int
    reason: str | None = None
    close: Decimal | None = None
    anchors: tuple[Anchor, ...] = ()
    days_stored: int = 0
    signal: Decimal | None = None
    volatility: Decimal | None = None
    target: Decimal | None = None
    held: Decimal = ZERO
    action: str = NO_CHANGE

    def features(self, rule: Rule = RULE) -> dict[str, Any]:
        def t(value: Decimal | None) -> str | None:
            return None if value is None else format(value, "f")
        return {"rule": rule.id, "rule_sha256": rule.sha256, "result": self.result, "reason": self.reason,
                "day_open_ms": self.day_open_ms, "close": t(self.close), "days_stored": self.days_stored,
                "anchors": [{"lookback_days": a.lookback_days, "day_open_ms": a.day_open_ms, "close": t(a.close),
                             "sign": a.sign} for a in self.anchors],
                "signal": t(self.signal), "volatility": t(self.volatility), "target": t(self.target),
                "held": t(self.held), "action": self.action, "never_short": True}


def nearest_stored(closes: Mapping[int, Decimal], day_open_ms: int, tolerance_days: int) -> int | None:
    """The nearest stored day at or before ``day_open_ms``, at most ``tolerance_days`` earlier."""
    for back in range(tolerance_days + 1):
        candidate = day_open_ms - back * DAY_MS
        if candidate in closes:
            return candidate
    return None


@lru_cache(maxsize=16384)
def log_return(later: Decimal, earlier: Decimal) -> Decimal:
    """``ln(later / earlier)`` under the execution context. Memoized: the backtest reads every day of the history
    and each reading's window shares all but one return with the day before's; the digits are the same either way."""
    with localcontext(CONTEXT):
        return (later / earlier).ln()


def ewma_volatility(closes: Mapping[int, Decimal], first_open_ms: int, last_open_ms: int,
                    rule: Rule = RULE) -> tuple[Decimal | None, int]:
    """The annualized exponentially weighted standard deviation of the daily log returns of the stored days from
    ``first_open_ms`` to ``last_open_ms`` (both inclusive), and how many days are stored in that window. A return
    across missing days counts once; the variance is seeded with the first return's square; None under the minimum
    of stored days or without a return."""
    days = sorted(open_ms for open_ms in closes if first_open_ms <= open_ms <= last_open_ms)
    if len(days) < rule.minimum_days or len(days) < 2:
        return None, len(days)
    com = Decimal(rule.centre_of_mass)
    with localcontext(CONTEXT):
        variance: Decimal | None = None
        for earlier, later in zip(days, days[1:], strict=False):
            squared = log_return(closes[later], closes[earlier]) ** 2
            variance = squared if variance is None else (com * variance + squared) / (com + 1)
        return (Decimal(rule.annualization) * variance).sqrt(), len(days)


def held_fraction(quantity: Decimal, bid: Decimal | None, equity: Decimal | None) -> Decimal:
    """The BTC held at the best bid over equity, to 0.00000001 down; 0 when nothing is held."""
    if quantity <= 0:
        return ZERO
    if bid is None or equity is None or equity <= 0:
        raise ValueError("held_fraction_needs_a_valuation")
    with localcontext(CONTEXT):
        return (quantity * bid / equity).quantize(AMOUNT, rounding=ROUND_DOWN)


def target_of(closes: Mapping[int, Decimal], day_open_ms: int, rule: Rule = RULE) -> Reading:
    """The target for the day ``day_open_ms`` (the day read), without an action."""
    close = closes.get(day_open_ms)
    if close is None:
        return Reading(WARMUP, day_open_ms, reason="CLOSE_MISSING")
    anchors: list[Anchor] = []
    for lookback in rule.lookbacks:
        anchor = nearest_stored(closes, day_open_ms - lookback * DAY_MS, rule.tolerance_days)
        if anchor is None:
            return Reading(WARMUP, day_open_ms, reason=f"ANCHOR_MISSING_{lookback}", close=close,
                           anchors=tuple(anchors))
        anchors.append(Anchor(lookback, anchor, closes[anchor], sign_of(close - closes[anchor])))
    volatility, stored = ewma_volatility(closes, day_open_ms - rule.volatility_days * DAY_MS, day_open_ms, rule)
    if volatility is None:
        return Reading(WARMUP, day_open_ms, reason=f"TOO_FEW_DAYS_{stored}", close=close, anchors=tuple(anchors),
                       days_stored=stored)
    with localcontext(CONTEXT):
        signal = Decimal(sum(anchor.sign for anchor in anchors)) / Decimal(len(anchors))
        scale = rule.cap if volatility == 0 else min(rule.cap, rule.target / volatility)
        target = (max(signal, ZERO) * scale).quantize(rule.step, rounding=ROUND_DOWN)
        if target < rule.flat:
            target = ZERO
    return Reading(LONG if target > 0 else CASH, day_open_ms, close=close, anchors=tuple(anchors),
                   days_stored=stored, signal=signal, volatility=volatility, target=target)


def act(found: Reading, held: Decimal, holding: bool, rule: Rule = RULE) -> Reading:
    """The action for a readable target: ``SELL_ALL`` when the target is 0 and BTC is held, else ``BUY`` or ``SELL``
    when the target is more than the buffer from ``held``, else ``NO_CHANGE``."""
    if found.result == WARMUP:
        return replace(found, held=held, action=NO_CHANGE)
    target = found.target
    if target == 0 and holding:
        action = SELL_ALL
    elif abs(target - held) > rule.buffer:
        action = BUY if target > held else SELL
    else:
        action = NO_CHANGE
    return replace(found, held=held, action=action)


def reading(closes: Mapping[int, Decimal], today_open_ms: int, held: Decimal = ZERO, holding: bool = False,
            rule: Rule = RULE) -> Reading:
    """The rule for the UTC day opening at ``today_open_ms``: it reads the last complete day before it."""
    return act(target_of(closes, utc_day_open(today_open_ms) - DAY_MS, rule), held, holding, rule)


__all__ = ["BUY", "CASH", "LONG", "NO_CHANGE", "SELL", "SELL_ALL", "WARMUP", "Anchor", "Reading", "act",
           "ewma_volatility", "held_fraction", "log_return", "nearest_stored", "reading", "sign_of", "target_of",
           "utc_day_open"]
