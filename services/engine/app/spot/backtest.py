"""``SPOT_BACKTEST_V1``: the rule's backtest on the stored spot daily candles (ExecPlan 0060 section 4.6).

``BACKTEST_MODELED_NOT_FILLED``: what the live account would have done, modeled on Binance's final daily candles, not
fills. For each window, from 10,000 USDT:

- **The rule.** Each day ``D`` the live engine reads the day before (``D − 1``) just after 00:05 UTC and trades at the
  book; here the same reading (``app.spot.rule``, the live functions, on the same stored closes) trades at that day's
  close, through ``app.spot.money``'s own fill code on a one-level book at the close: the cost's slippage against the
  order, its fee in USDT, the instrument's lot step, minimum quantity and notional as stored by the feed, a buy at most
  the cash. A day whose reading is not readable trades nothing, as live.
- **The latches.** The drawdown stop: the account's high is taken at each day's high and its fall at the day's low
  (the high first, which is the worse order); once the fall reaches 8% of the high the run stops, selling everything at
  the price where the fall reached 8% (or the day's open when it opened below), as the live engine sells within the
  minute it sees it, and the window holds cash from there ("the run would have stopped here"). The daily loss limit is
  counted (the days the day's low took the account 2% below the day's opening value) and changes no trade: the live
  account's daily trade comes at 00:05 UTC, right after the day's reference and before the day's moves, and the latch
  clears at the next day's reference, before the next trade.
- **Holding Bitcoin**, beside it: one buy at the rule's first trading moment, at the same close with the same cost.

Each window reports the final value, the return, the return a year, the worst fall (from the high, at each day's low),
the fees, the buys and sells, the share of days in Bitcoin, the average and largest share held, a row per calendar
year, and the daily values for the chart. Pure functions but ``compute_and_store``: no clock, no network.
"""

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal, localcontext
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.execution.lifecycle import stable_id
from app.execution.numbers import CONTEXT, ONE, ZERO
from app.spot import money
from app.spot import rule as spot_rule
from app.spot.definitions import COST, DAY_MS, POLICY, RULE, Cost, Policy, Rule

METHOD = "SPOT_BACKTEST_V1"
LABEL = "BACKTEST_MODELED_NOT_FILLED"
START_CASH = Decimal("10000")
# The windows of section 4.6: since 2019 (the first full year after the rule's 365-day warm-up from Binance's first
# spot day, 2017-08-17), since 2023, and the last 12 months to the last stored day.
WINDOWS: tuple[tuple[str, date | None], ...] = (("SINCE_2019", date(2019, 1, 1)), ("SINCE_2023", date(2023, 1, 1)),
                                                ("LAST_12_MONTHS", None))
LAST_DAYS = 365
# The one-level book a modeled fill walks: deep enough for any quantity the account can trade.
DEPTH = Decimal(10) ** 12
RATIO = Decimal("0.00000001")


@dataclass(frozen=True)
class Day:
    open_ms: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal


def day_of(open_ms: int) -> date:
    return datetime.fromtimestamp(open_ms / 1000, tz=UTC).date()


def ms_of(day: date) -> int:
    return int(datetime(day.year, day.month, day.day, tzinfo=UTC).timestamp() * 1000)


def text_of(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def ratio(value: Decimal) -> str:
    with localcontext(CONTEXT):
        return format(value.quantize(RATIO), "f")


def candles_hash(days: Sequence[Day]) -> str:
    rows = [[d.open_ms, text_of(d.open), text_of(d.high), text_of(d.low), text_of(d.close)] for d in days]
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def a_year(final: Decimal, start: Decimal, days: int) -> Decimal:
    """The return a year, compounded over 365 days."""
    with localcontext(CONTEXT):
        return (final / start) ** (Decimal(365) / Decimal(days)) - ONE


class Account:
    """One window's modeled account: USDT and BTC, valued at a price."""

    def __init__(self, cash: Decimal):
        self.cash, self.quantity, self.fees = cash, ZERO, ZERO
        self.buys = self.sells = self.refused = 0

    def value(self, price: Decimal) -> Decimal:
        return money.equity(self.cash, self.quantity, price)

    def apply(self, fill: money.Fill) -> None:
        with localcontext(CONTEXT):
            self.cash += fill.cash_delta
            self.quantity += fill.base_delta
            self.fees += fill.fee
        if fill.side == money.BUY:
            self.buys += 1
        else:
            self.sells += 1


def sellable(quantity: Decimal, price: Decimal, filters: money.Filters, cost: money.Cost) -> bool:
    """``SPOT_RULE_V1``'s dust rule (``money.sellable``) on the one-level book at ``price`` the backtest's sale
    walks."""
    return money.sellable(quantity, [(price, DEPTH)], filters, cost)


class Peak:
    """The worst fall from the high, at each day's low, after each day's high."""

    def __init__(self, start: Decimal):
        self.high, self.worst, self.day = start, ZERO, None

    def see(self, high: Decimal, low: Decimal, day: date) -> Decimal:
        self.high = max(self.high, high)
        with localcontext(CONTEXT):
            fall = ONE - low / self.high if self.high > 0 else ZERO
        if fall > self.worst:
            self.worst, self.day = fall, day
        return fall


def years_of(points: list[tuple[date, Decimal]], start: Decimal) -> list[dict[str, Any]]:
    """A row per calendar year: the return from the end of the year before (the window's start for the first)."""
    rows, before, year, last = [], start, None, None
    for day, value in points:
        if year is not None and day.year != year:
            with localcontext(CONTEXT):
                rows.append({"year": year, "return": ratio(last / before - ONE)})
            before = last
        year, last = day.year, value
    if year is not None:
        with localcontext(CONTEXT):
            rows.append({"year": year, "return": ratio(last / before - ONE)})
    return rows


def run_window(days: Sequence[Day], first: int, readings: dict[int, spot_rule.Reading], filters: money.Filters,
               rule: Rule = RULE, policy: Policy = POLICY, cost: Cost = COST) -> tuple[dict[str, Any], dict[str, Any]]:
    """The rule and holding Bitcoin over the stored days from ``first`` (a day's open time) to the last, each from
    ``START_CASH``; their summaries and daily series."""
    by_ms = {d.open_ms: d for d in days}
    window = [d for d in days if d.open_ms >= first]
    account, hold = Account(START_CASH), Account(START_CASH)
    peak, hold_peak = Peak(START_CASH), Peak(START_CASH)
    points: list[tuple[date, Decimal]] = []
    hold_points: list[tuple[date, Decimal]] = []
    series: dict[str, list[Any]] = {"days": [], "rule": [], "hold": [], "target": []}
    trades: list[list[Any]] = []
    stopped: dict[str, Any] | None = None
    held_sum, held_max, days_in, daily_loss_days = ZERO, ZERO, 0, 0
    hold_bought = False
    for day in window:
        read = by_ms.get(day.open_ms - DAY_MS)
        found = readings.get(day.open_ms)
        # The morning: the day's reference (the value at the last close) and the rule's trade at that close.
        reference = account.value(read.close) if read is not None else None
        if read is not None and not hold_bought:
            plan = money.plan_buy(wanted=DEPTH, cash=hold.cash, asks=[(read.close, DEPTH)], filters=filters,
                                  cost=cost)
            if isinstance(plan, money.Fill):
                hold.apply(plan)
                hold_bought = True
        if stopped is None and read is not None and found is not None and found.result != spot_rule.WARMUP:
            value = account.value(read.close)
            held = spot_rule.held_fraction(account.quantity, read.close, value)
            acted = spot_rule.act(found, held, sellable(account.quantity, read.close, filters, cost), rule)
            plan = None
            if acted.action == spot_rule.SELL_ALL:
                plan = money.plan_sell(wanted=account.quantity, held=account.quantity, bids=[(read.close, DEPTH)],
                                       filters=filters, cost=cost)
            elif acted.action in (spot_rule.BUY, spot_rule.SELL):
                wanted = money.difference_quantity(acted.target, held, value, read.close)
                if acted.action == spot_rule.BUY:
                    plan = money.plan_buy(wanted=wanted, cash=account.cash, asks=[(read.close, DEPTH)],
                                          filters=filters, cost=cost)
                else:
                    plan = money.plan_sell(wanted=wanted, held=account.quantity, bids=[(read.close, DEPTH)],
                                           filters=filters, cost=cost)
            if isinstance(plan, money.Fill):
                account.apply(plan)
                trades.append([read.open_ms, plan.side, text_of(plan.price), text_of(plan.quantity)])
            elif isinstance(plan, money.Refusal):
                account.refused += 1
        # The day: its open, its high, then its low; the drawdown stop sells at the open when the day opened below
        # the limit, else at the price where the fall from the high reached it.
        today = day_of(day.open_ms)
        with localcontext(CONTEXT):
            opened_below = account.quantity > 0 and account.value(day.open) <= peak.high * (ONE - policy.drawdown)
        fall = peak.see(account.value(day.high), account.value(day.low), today)
        hold_peak.see(hold.value(day.high), hold.value(day.low), today)
        if reference is not None and account.quantity > 0:
            with localcontext(CONTEXT):
                if account.value(day.low) <= reference * (ONE - policy.daily_loss):
                    daily_loss_days += 1
        if stopped is None and account.quantity > 0 and fall >= policy.drawdown:
            with localcontext(CONTEXT):
                limit = (peak.high * (ONE - policy.drawdown) - account.cash) / account.quantity
            price = money.floor8(day.open if opened_below else limit)
            plan = money.plan_sell(wanted=account.quantity, held=account.quantity, bids=[(price, DEPTH)],
                                   filters=filters, cost=cost)
            if isinstance(plan, money.Fill):
                account.apply(plan)
                trades.append([day.open_ms, plan.side, text_of(plan.price), text_of(plan.quantity)])
            stopped = {"day": today.isoformat(), "price": text_of(price)}
        # The close.
        value, hold_value = account.value(day.close), hold.value(day.close)
        points.append((today, value))
        hold_points.append((today, hold_value))
        with localcontext(CONTEXT):
            share = account.quantity * day.close / value if value > 0 else ZERO
        held_sum += share
        held_max = max(held_max, share)
        days_in += 1 if account.quantity > 0 else 0
        target = None if found is None or found.result == spot_rule.WARMUP else text_of(found.target)
        series["days"].append(day.open_ms)
        series["rule"].append(text_of(value))
        series["hold"].append(text_of(hold_value))
        series["target"].append(target)
    count = len(window)
    span = (day_of(window[-1].open_ms) - day_of(window[0].open_ms)).days + 1 if window else 0
    with localcontext(CONTEXT):
        average = held_sum / count if count else ZERO

    def summary(final: Decimal, worst: Peak, fees: Decimal, years: list[dict[str, Any]]) -> dict[str, Any]:
        with localcontext(CONTEXT):
            total = final / START_CASH - ONE
        return {"final": text_of(money.floor8(final)), "return": ratio(total),
                "a_year": ratio(a_year(final, START_CASH, span)) if span else None,
                "worst_fall": ratio(worst.worst), "worst_fall_day": worst.day.isoformat() if worst.day else None,
                "fees": text_of(fees), "years": years}

    rule_final = points[-1][1] if points else START_CASH
    hold_final = hold_points[-1][1] if hold_points else START_CASH
    result = {
        "first_day": day_of(window[0].open_ms).isoformat() if window else None,
        "last_day": day_of(window[-1].open_ms).isoformat() if window else None,
        "days": count, "calendar_days": span,
        "rule": {**summary(rule_final, peak, account.fees, years_of(points, START_CASH)),
                 "buys": account.buys, "sells": account.sells, "refused": account.refused,
                 "days_in_bitcoin": ratio(Decimal(days_in) / Decimal(count)) if count else None,
                 "average_held": ratio(average), "max_held": ratio(held_max),
                 "stopped": stopped, "daily_loss_days": daily_loss_days},
        "hold": {**summary(hold_final, hold_peak, hold.fees, years_of(hold_points, START_CASH)),
                 "bought": hold_bought},
    }
    return result, {**series, "trades": trades}


def readings_of(days: Sequence[Day], earliest: int, rule: Rule = RULE) -> dict[int, spot_rule.Reading]:
    """The reading that trades on each stored day from ``earliest``: it reads the day before (D − 1), with the same
    function the live engine calls on the same stored closes."""
    closes = {d.open_ms: d.close for d in days}
    return {d.open_ms: spot_rule.target_of(closes, d.open_ms - DAY_MS, rule) for d in days if d.open_ms >= earliest}


def compute(days: Sequence[Day], filters: money.Filters, rule: Rule = RULE, policy: Policy = POLICY,
            cost: Cost = COST) -> tuple[dict[str, Any], dict[str, Any]]:
    """Every window on the stored days (oldest first): the result and the daily series."""
    days = sorted(days, key=lambda d: d.open_ms)
    if not days:
        raise ValueError("no_daily_candles")
    last = days[-1].open_ms
    starts: list[tuple[str, int]] = []
    for key, first in WINDOWS:
        starts.append((key, ms_of(first) if first is not None else last - (LAST_DAYS - 1) * DAY_MS))
    readings = readings_of(days, min(start for _, start in starts), rule)
    windows, series = [], {}
    for key, start in starts:
        summary, points = run_window(days, start, readings, filters, rule, policy, cost)
        windows.append({"key": key, **summary})
        series[key] = points
    missing = (last - days[0].open_ms) // DAY_MS + 1 - len(days)
    result = {
        "method": METHOD, "label": LABEL, "start_cash": text_of(START_CASH),
        "fills": "AT_THE_CLOSE_THE_RULE_READS_WITH_THE_COST'S_SLIPPAGE_AND_FEE_ON_A_ONE_LEVEL_BOOK",
        "drawdown_stop": "SELLS_AT_THE_PRICE_THE_FALL_REACHED_THE_LIMIT_OR_THE_DAY'S_OPEN_BELOW_IT",
        "daily_loss": "COUNTED_NO_TRADE_CHANGES: THE_DAILY_TRADE_COMES_BEFORE_THE_DAY'S_MOVES",
        "instrument": {"step_size": text_of(filters.step), "min_qty": text_of(filters.min_qty),
                       "max_qty": text_of(filters.max_qty), "min_notional": text_of(filters.min_notional),
                       "max_notional": text_of(filters.max_notional)},
        "data": {"first_day": day_of(days[0].open_ms).isoformat(), "last_day": day_of(last).isoformat(),
                 "days": len(days), "missing_days": int(missing)},
        "windows": windows,
    }
    return result, series


# ---- the stored computation (the execution worker's, outside the money step) --------------------------------------

def stored_days(connection: Connection) -> list[Day]:
    rows = connection.execute(text(
        "SELECT open_ms, open, high, low, close FROM spot_daily_bars ORDER BY open_ms")).all()
    return [Day(int(row[0]), row[1], row[2], row[3], row[4]) for row in rows]


def due(connection: Connection, code_identity: str, rule: Rule = RULE, policy: Policy = POLICY,
        cost: Cost = COST) -> dict[str, Any] | None:
    """What a new computation needs, or None while none is due: the feed's daily history complete and current
    (``daily_checked_at``), an instrument stored, and no stored row yet for the newest stored day under these
    definitions and this code."""
    state = connection.execute(text(
        "SELECT s.daily_checked_at, i.step_size, i.min_qty, i.max_qty, i.min_notional, i.max_notional "
        "FROM spot_feed_state s LEFT JOIN spot_instruments i ON i.id = s.instrument_id WHERE s.id = 1")).one()
    if state[0] is None or state[1] is None:
        return None
    last = connection.execute(text("SELECT max(open_ms) FROM spot_daily_bars")).scalar_one()
    if last is None:
        return None
    stored = connection.execute(text(
        "SELECT EXISTS (SELECT 1 FROM spot_backtests WHERE rule_sha256 = :rule AND policy_sha256 = :policy "
        "AND cost_sha256 = :cost AND code_identity = :code AND last_day_ms = :last)"),
        {"rule": rule.sha256, "policy": policy.sha256, "cost": cost.sha256, "code": code_identity,
         "last": last}).scalar_one()
    if stored:
        return None
    return {"last_day_ms": int(last), "filters": money.Filters(step=state[1], min_qty=state[2], max_qty=state[3],
                                                               min_notional=state[4], max_notional=state[5])}


def store_result(connection: Connection, *, at: datetime, code_identity: str, days: Sequence[Day],
                 result: dict[str, Any], series: dict[str, Any], rule: Rule = RULE, policy: Policy = POLICY,
                 cost: Cost = COST) -> UUID | None:
    """Insert one computation (nothing when the same one is stored) and clear the older rows' daily series."""
    candles = candles_hash(days)
    identity = stable_id("spot-backtest", rule.sha256, policy.sha256, cost.sha256, code_identity,
                         days[-1].open_ms, candles)
    inserted = connection.execute(text(
        "INSERT INTO spot_backtests (id, computed_at, method, label, rule_id, rule_sha256, policy_id, policy_sha256, "
        "cost_id, cost_sha256, code_identity, first_day_ms, last_day_ms, days, candles_sha256, result, series) "
        "VALUES (:id, :at, :method, :label, :rule, :rule_sha, :policy, :policy_sha, :cost, :cost_sha, :code, :first, "
        ":last, :days, :candles, CAST(:result AS jsonb), CAST(:series AS jsonb)) ON CONFLICT DO NOTHING "
        "RETURNING id"),
        {"id": identity, "at": at, "method": METHOD, "label": LABEL, "rule": rule.id, "rule_sha": rule.sha256,
         "policy": policy.id, "policy_sha": policy.sha256, "cost": cost.id, "cost_sha": cost.sha256,
         "code": code_identity, "first": days[0].open_ms, "last": days[-1].open_ms, "days": len(days),
         "candles": candles, "result": json.dumps(result, separators=(",", ":")),
         "series": json.dumps(series, separators=(",", ":"))}).scalar_one_or_none()
    if inserted is None:
        return None
    connection.execute(text("UPDATE spot_backtests SET series = NULL WHERE id <> :id AND series IS NOT NULL"),
                       {"id": identity})
    return identity


def compute_and_store(db, code_identity: str, now, rule: Rule = RULE, policy: Policy = POLICY,
                      cost: Cost = COST) -> UUID | None:
    """One computation when one is due; returns the stored row's ID, or None when nothing was due or stored."""
    with db.connect() as connection:
        need = due(connection, code_identity, rule, policy, cost)
        if need is None:
            return None
        days = stored_days(connection)
    result, series = compute(days, need["filters"], rule, policy, cost)
    with db.begin() as connection:
        return store_result(connection, at=now(), code_identity=code_identity, days=days, result=result,
                            series=series, rule=rule, policy=policy, cost=cost)


__all__ = ["LABEL", "METHOD", "START_CASH", "WINDOWS", "Day", "compute", "compute_and_store", "due", "readings_of",
           "run_window", "store_result"]
