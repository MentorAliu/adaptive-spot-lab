"""``SPOT_BACKTEST_V1`` (ExecPlan 0060 section 6, R5): the rule's backtest on stored daily candles, modeled and not
filled. The pure part runs on SYNTHETIC candles; the stored part on a scratch database (``spot_support``). Every
price here is made up for the test; none is a recorded market value."""

from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

import pytest
from spot_support import CODE, T0, day_open, trend
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.spot import backtest, money
from app.spot import rule as spot_rule
from app.spot.definitions import DAY_MS, RULE

D = Decimal
FILTERS = money.Filters(step=D("0.00001"), min_qty=D("0.00001"), max_qty=D("9000"), min_notional=D("5"),
                        max_notional=None)
LAST = int(datetime(2026, 11, 1, tzinfo=UTC).timestamp() * 1000)
FIRST = LAST - 5 * DAY_MS


def days_of(rows: list[tuple[str, str, str, str]], first: int = FIRST) -> list[backtest.Day]:
    """(open, high, low, close) a day from ``first``."""
    return [backtest.Day(first + n * DAY_MS, D(o), D(h), D(lo), D(c)) for n, (o, h, lo, c) in enumerate(rows)]


def long(day_read: int, close: str, target: str = "1") -> spot_rule.Reading:
    return spot_rule.Reading("LONG", day_read, close=D(close), signal=D(1), volatility=D("0.04"), target=D(target))


def buy_all(price: str) -> money.Fill:
    return money.plan_buy(wanted=backtest.DEPTH, cash=backtest.START_CASH, asks=[(D(price), backtest.DEPTH)],
                          filters=FILTERS)


def line_days(last: int = LAST, days: int = 800, step: str = "50") -> list[backtest.Day]:
    closes = trend(last, days=days, step=step)
    return [backtest.Day(at, close, close + 100, close - 100, close) for at, close in sorted(closes.items())]


# ---- the pure part ------------------------------------------------------------------------------------------------

def test_a_days_reading_is_the_live_rules_reading_of_the_day_before():
    days = line_days(days=420)
    closes = {d.open_ms: d.close for d in days}
    earliest = days[0].open_ms
    readings = backtest.readings_of(days, earliest)
    assert sorted(readings) == [d.open_ms for d in days]
    for day in days:
        assert readings[day.open_ms] == spot_rule.target_of(closes, day.open_ms - DAY_MS)
    assert readings[days[0].open_ms].reason == "CLOSE_MISSING"
    assert readings[days[-1].open_ms].result == "LONG"


def test_the_rule_buys_at_the_close_it_reads_with_the_costs_and_holding_bitcoin_buys_once():
    days = days_of([("100", "101", "99", "100"), ("100", "102", "99", "101"), ("101", "103", "100", "102")])
    readings = {days[1].open_ms: long(days[0].open_ms, "100"), days[2].open_ms: long(days[1].open_ms, "101")}
    summary, series = backtest.run_window(days, days[1].open_ms, readings, FILTERS)
    fill = buy_all("100")
    assert series["trades"] == [[days[0].open_ms, "BUY", format(fill.price, "f"), format(fill.quantity, "f")]]
    cash = backtest.START_CASH + fill.cash_delta
    final = money.floor8(cash + fill.quantity * D("102"))
    rule = summary["rule"]
    assert (rule["final"], rule["buys"], rule["sells"], rule["fees"]) == (format(final, "f"), 1, 0, format(fill.fee, "f"))
    # The second day reads a target of 1 with all of it held: inside the buffer, nothing more is bought.
    assert summary["hold"]["final"] == rule["final"] and summary["hold"]["bought"] is True
    assert (summary["first_day"], summary["last_day"], summary["days"]) == ("2026-10-28", "2026-10-29", 2)
    assert series["days"] == [days[1].open_ms, days[2].open_ms] and series["target"] == ["1", "1"]
    assert rule["days_in_bitcoin"] == "1.00000000" and rule["stopped"] is None


def test_a_day_not_readable_trades_nothing_and_holding_bitcoin_still_buys():
    days = days_of([("100", "101", "99", "100"), ("100", "102", "99", "101"), ("101", "103", "100", "102")])
    warm = spot_rule.Reading("WARMUP", days[0].open_ms, reason="TOO_FEW_DAYS_12")
    summary, series = backtest.run_window(days, days[1].open_ms, {days[1].open_ms: warm}, FILTERS)
    assert series["trades"] == [] and summary["rule"]["final"] == "10000.00000000"
    assert summary["hold"]["bought"] is True and series["target"] == [None, None]


def test_the_drawdown_stop_sells_where_the_fall_reached_eight_percent_and_holds_cash_after():
    days = days_of([("100", "101", "99", "100"), ("100", "100", "99", "100"), ("100", "100", "91", "95"),
                    ("95", "120", "95", "120")])
    readings = {d.open_ms: long(d.open_ms - DAY_MS, "100") for d in days[1:]}
    summary, series = backtest.run_window(days, days[1].open_ms, readings, FILTERS)
    fill = buy_all("100")
    cash = backtest.START_CASH + fill.cash_delta
    limit = money.floor8((backtest.START_CASH * D("0.92") - cash) / fill.quantity)
    sale = money.plan_sell(wanted=fill.quantity, held=fill.quantity, bids=[(limit, backtest.DEPTH)], filters=FILTERS)
    assert summary["rule"]["stopped"] == {"day": "2026-10-29", "price": format(limit, "f")}
    assert [t[1] for t in series["trades"]] == ["BUY", "SELL"]
    assert series["trades"][1] == [days[2].open_ms, "SELL", format(sale.price, "f"), format(fill.quantity, "f")]
    final = cash + sale.cash_delta
    assert summary["rule"]["final"] == format(final, "f") and summary["rule"]["buys"] == 1
    # The day after rises 26%; the stopped run holds cash.
    assert series["rule"][-1] == series["rule"][-2] == format(final, "f")
    assert D(summary["hold"]["final"]) > D(summary["rule"]["final"])


def test_a_day_that_opens_below_the_limit_sells_at_its_open():
    days = days_of([("100", "101", "99", "100"), ("100", "100", "99", "100"), ("90", "90", "85", "88")])
    readings = {d.open_ms: long(d.open_ms - DAY_MS, "100") for d in days[1:]}
    summary, series = backtest.run_window(days, days[1].open_ms, readings, FILTERS)
    assert summary["rule"]["stopped"] == {"day": "2026-10-29", "price": "90.00000000"}
    sale = money.plan_sell(wanted=buy_all("100").quantity, held=buy_all("100").quantity, bids=[(D("90"), backtest.DEPTH)],
                           filters=FILTERS)
    assert series["trades"][1][2] == format(sale.price, "f")


def test_the_daily_loss_limit_is_counted_and_changes_no_trade():
    days = days_of([("100", "101", "99", "100"), ("100", "100", "99", "100"), ("100", "100", "97.5", "99"),
                    ("99", "100", "98.5", "99")])
    readings = {d.open_ms: long(d.open_ms - DAY_MS, "100") for d in days[1:]}
    summary, series = backtest.run_window(days, days[1].open_ms, readings, FILTERS)
    assert summary["rule"]["daily_loss_days"] == 1 and summary["rule"]["stopped"] is None
    assert [t[1] for t in series["trades"]] == ["BUY"]


def test_the_rule_sells_all_when_its_target_falls_to_zero():
    days = days_of([("100", "101", "99", "100"), ("100", "102", "99", "101"), ("101", "103", "100", "102")])
    readings = {days[1].open_ms: long(days[0].open_ms, "100"),
                days[2].open_ms: replace(long(days[1].open_ms, "101"), result="CASH", target=D(0), signal=D(-1))}
    summary, series = backtest.run_window(days, days[1].open_ms, readings, FILTERS)
    assert [t[1] for t in series["trades"]] == ["BUY", "SELL"] and summary["rule"]["sells"] == 1
    assert series["trades"][1][0] == days[1].open_ms
    assert summary["rule"]["days_in_bitcoin"] == "0.50000000"


def test_every_window_on_a_long_history_with_a_row_a_year():
    days = line_days()
    result, series = backtest.compute(list(reversed(days)), FILTERS)
    assert (result["method"], result["label"], result["start_cash"]) == ("SPOT_BACKTEST_V1",
                                                                         "BACKTEST_MODELED_NOT_FILLED", "10000")
    assert result["data"] == {"first_day": backtest.day_of(days[0].open_ms).isoformat(), "last_day": "2026-11-01",
                              "days": 800, "missing_days": 0}
    assert [w["key"] for w in result["windows"]] == ["SINCE_2019", "SINCE_2023", "LAST_12_MONTHS"]
    since, _, last = result["windows"]
    assert since["first_day"] == backtest.day_of(days[0].open_ms).isoformat() and since["days"] == 800
    assert (last["first_day"], last["last_day"], last["days"]) == ("2025-11-02", "2026-11-01", 365)
    assert since["rule"]["buys"] >= 1 and since["hold"]["bought"] is True
    assert [row["year"] for row in since["rule"]["years"]] == [2024, 2025, 2026]
    assert set(series) == {"SINCE_2019", "SINCE_2023", "LAST_12_MONTHS"}
    assert len(series["LAST_12_MONTHS"]["days"]) == len(series["LAST_12_MONTHS"]["rule"]) == 365
    assert result["instrument"]["step_size"] == "0.00001" and result["instrument"]["max_notional"] is None


def test_a_missing_day_is_counted_and_a_history_without_days_is_refused():
    days = line_days(days=420)
    del days[200]
    result, _ = backtest.compute(days, FILTERS)
    assert result["data"]["missing_days"] == 1 and result["data"]["days"] == 419
    with pytest.raises(ValueError, match="no_daily_candles"):
        backtest.compute([], FILTERS)


def test_a_year_is_its_return_from_the_end_of_the_year_before():
    points = [(date(2024, 12, 30), D("11000")), (date(2024, 12, 31), D("12000")), (date(2025, 1, 1), D("6000")),
              (date(2025, 6, 1), D("18000"))]
    assert backtest.years_of(points, D("10000")) == [{"year": 2024, "return": "0.20000000"},
                                                     {"year": 2025, "return": "0.50000000"}]
    assert backtest.a_year(D("12100"), D("10000"), 730).quantize(D("0.0001")) == D("0.1000")


# ---- the stored part (a scratch database) -------------------------------------------------------------------------

def due_state(spot, at=T0) -> None:
    spot.instrument(at)
    with spot.market.begin() as connection:
        connection.execute(text("UPDATE spot_feed_state SET daily_checked_at = :at WHERE id = 1"), {"at": at})


def test_the_backtest_is_stored_once_per_new_final_day_and_only_the_newest_keeps_its_series(spot):
    spot.daily(trend(day_open(T0) - DAY_MS))
    spot.instrument(T0)
    assert backtest.compute_and_store(spot.execution, CODE, lambda: T0) is None  # history not complete yet
    due_state(spot)
    first = backtest.compute_and_store(spot.execution, CODE, lambda: T0)
    assert isinstance(first, UUID)
    assert backtest.compute_and_store(spot.execution, CODE, lambda: T0) is None  # stored for this day
    row = spot.rows("SELECT method, label, rule_id, rule_sha256, code_identity, days, last_day_ms, result, "
                    "series IS NOT NULL AS has_series FROM spot_backtests")[0]
    assert (row["method"], row["label"], row["rule_id"], row["rule_sha256"]) == (
        "SPOT_BACKTEST_V1", "BACKTEST_MODELED_NOT_FILLED", "SPOT_RULE_V1", RULE.sha256)
    assert (row["code_identity"], row["days"], row["last_day_ms"], row["has_series"]) == (
        CODE, 400, day_open(T0) - DAY_MS, True)
    assert [w["key"] for w in row["result"]["windows"]] == ["SINCE_2019", "SINCE_2023", "LAST_12_MONTHS"]
    spot.daily({day_open(T0): D("60000")})
    second = backtest.compute_and_store(spot.execution, CODE, lambda: T0)
    assert isinstance(second, UUID) and second != first
    assert spot.rows("SELECT id, series IS NOT NULL AS has_series FROM spot_backtests ORDER BY seq") == [
        {"id": first, "has_series": False}, {"id": second, "has_series": True}]
    # A new installed code computes again on the same days.
    assert isinstance(backtest.compute_and_store(spot.execution, "d" * 64, lambda: T0), UUID)


def test_a_stored_backtest_keeps_its_result_and_only_clears_its_series(spot):
    spot.daily(trend(day_open(T0) - DAY_MS))
    due_state(spot)
    backtest.compute_and_store(spot.execution, CODE, lambda: T0)
    for engine, sql, refusal in (
            (spot.execution, "UPDATE spot_backtests SET series = '{}'", "only clears its series"),
            (spot.execution, "UPDATE spot_backtests SET series = NULL, days = 1", "permission denied"),
            (spot.admin, "UPDATE spot_backtests SET days = 1", "only clears its series"),
            (spot.execution, "DELETE FROM spot_backtests", "permission denied"),
            (spot.api, "UPDATE spot_backtests SET series = NULL", "permission denied")):
        with pytest.raises(DBAPIError, match=refusal):
            with engine.begin() as connection:
                connection.execute(text(sql))
    with spot.execution.begin() as connection:
        connection.execute(text("UPDATE spot_backtests SET series = NULL"))
    assert spot.scalar("SELECT count(*) FROM spot_backtests WHERE series IS NULL AND result ? 'windows'") == 1


def test_the_backtests_reading_for_a_day_is_the_one_the_live_engine_stored(spot):
    closes = spot.ready()
    spot.start()
    spot.step(T0)
    live = spot.rows("SELECT day_open_ms, close, signal, volatility, target, outcome FROM spot_rule_readings")
    assert [row["outcome"] for row in live] == ["FILLED"]
    spot.daily({day_open(T0): closes[day_open(T0) - DAY_MS]})
    with spot.api.connect() as connection:
        days = backtest.stored_days(connection)
    modeled = backtest.readings_of(days, day_open(T0))[day_open(T0)]
    assert (modeled.day_open_ms, modeled.close, modeled.signal, modeled.volatility, modeled.target) == (
        live[0]["day_open_ms"], live[0]["close"], live[0]["signal"], live[0]["volatility"], live[0]["target"])
