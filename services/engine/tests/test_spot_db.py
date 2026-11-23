"""The spot account on a scratch database (ExecPlan 0060 section 6, R3 and R4): the postings, the step, the daily
reading and its trade, the owner's controls, the latches, the fencing and the reconciliation, with the real database
roles and SYNTHETIC market rows (``spot_support``)."""

import json
from datetime import timedelta
from decimal import Decimal, localcontext
from uuid import uuid4

import pytest
from spot_support import MIN_QTY, STEP, T0, day_open, trend
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app import accounting
from app.execution import store as xstore
from app.execution.numbers import CONTEXT, floor_to_step
from app.spot import money
from app.spot import rule as spot_rule
from app.spot import views as spot_views
from app.spot.definitions import DAY_MS, POLICY

SECOND = timedelta(seconds=1)
MINUTE = timedelta(minutes=1)


def expected_reading(closes, at):
    return spot_rule.target_of(closes, day_open(at) - DAY_MS)


def postings_balance(spot) -> bool:
    return not spot.rows("SELECT tx_id, asset FROM journal_postings GROUP BY tx_id, asset HAVING SUM(amount) <> 0")


# ---- R4: the first run and the daily reading ------------------------------------------------------------------------

def test_the_first_run_starts_by_itself_and_the_day_trades_once(spot):
    closes = spot.ready()
    spot.start()
    spot.step(T0)
    run = spot.run()
    assert run["state"] == "RUNNING" and run["started_by"] == "SYSTEM" and run["request_id"] is None
    assert run["start_equity"] == Decimal("10000") and run["code_identity"] == "c" * 64
    expected = expected_reading(closes, T0)
    assert expected.result == spot_rule.LONG and expected.signal == 1
    [reading] = spot.readings()
    assert (reading["result"], reading["action"], reading["outcome"], reading["spent"]) == ("LONG", "BUY", "FILLED",
                                                                                            True)
    # The live reading is the pure function's on the same stored closes (the plan's M3).
    assert reading["target"] == expected.target and reading["signal"] == expected.signal
    assert reading["volatility"] == expected.volatility and reading["close"] == expected.close
    assert reading["day_open_ms"] == day_open(T0) - DAY_MS and reading["held"] == 0
    [fill] = spot.fills()
    assert (fill["side"], fill["reason"]) == ("BUY", "RULE_BUY") and reading["fill_id"] == fill["id"]
    # The quantity is within one lot step of target x equity / bid.
    wanted = expected.target * Decimal(10000) / Decimal("60000.00")
    assert wanted - Decimal(STEP) < fill["quantity"] <= wanted
    assert fill["price"] == money.fill_price(money.BUY, Decimal("60000.01"), Decimal(1))
    assert fill["fee"] == money.fee_for(fill["quantity"], fill["price"], Decimal("0.001"))
    account = spot.account()
    assert account["cash"] == Decimal(10000) - fill["gross"] - fill["fee"] == fill["cash_after"]
    assert spot.btc() == fill["quantity"] == fill["quantity_after"]
    assert account["version"] == fill["account_version"]
    assert postings_balance(spot)
    assert spot.reconcile(T0 + SECOND)["status"] == "OK"
    # The day is spent: nothing more today, whatever the time.
    spot.book(T0 + 2 * SECOND)
    spot.step(T0 + 2 * SECOND)
    spot.book(T0 + 16 * MINUTE)
    spot.step(T0 + 16 * MINUTE)
    assert len(spot.readings()) == 1 and len(spot.fills()) == 1
    purposes = [row["purpose"] for row in spot.rows("SELECT purpose FROM spot_valuations ORDER BY valued_at, recorded_at")]
    assert purposes[:3] == ["START", "DAILY_REFERENCE", "FILL"]
    assert spot.scalar("SELECT count(*) FROM spot_daily_references") == 1


def test_nothing_is_read_before_five_past_midnight(spot):
    spot.ready(T0)
    spot.start()
    spot.step(T0.replace(minute=4))
    assert spot.run()["state"] == "RUNNING" and spot.readings() == []


def test_a_day_not_readable_yet_is_tried_again_every_15_minutes(spot):
    spot.fund()
    spot.instrument(T0)
    closes = trend(day_open(T0) - DAY_MS)
    last = max(closes)
    spot.daily({day: close for day, close in closes.items() if day != last})
    spot.book(T0 - SECOND / 2)
    spot.start()
    spot.step(T0)
    [reading] = spot.readings()
    assert (reading["result"], reading["reason"], reading["outcome"], reading["spent"]) == (
        "WARMUP", "CLOSE_MISSING", "NOT_READABLE", False)
    assert (reading["held"], reading["action"]) == (None, None)
    assert (reading["features"]["held"], reading["features"]["action"]) == (None, None)
    spot.book(T0 + MINUTE)
    spot.step(T0 + MINUTE)  # not tried again within 15 minutes
    spot.book(T0 + 15 * MINUTE - SECOND / 2)
    spot.step(T0 + 15 * MINUTE)  # tried again, still missing: stored once a day
    assert len(spot.readings()) == 1 and spot.fills() == []
    spot.daily({last: closes[last]})
    spot.book(T0 + 30 * MINUTE - SECOND / 2)
    spot.step(T0 + 30 * MINUTE)
    readings = spot.readings()
    assert [row["outcome"] for row in readings] == ["NOT_READABLE", "FILLED"] and len(spot.fills()) == 1


def test_too_few_days_is_not_readable(spot):
    closes = trend(day_open(T0) - DAY_MS, days=299)
    spot.ready(T0, closes)
    spot.start()
    spot.step(T0)
    [reading] = spot.readings()
    assert reading["outcome"] == "NOT_READABLE" and reading["reason"].startswith("ANCHOR_MISSING_365")


def test_a_stale_book_or_an_unverified_clock_refuses_and_the_day_is_tried_again(spot):
    spot.fund()
    spot.instrument(T0)
    spot.daily(trend(day_open(T0) - DAY_MS))
    spot.book(T0 - 3 * SECOND)  # too old for a trade (2 s), young enough to value (5 s)
    spot.start()
    spot.step(T0)
    [reading] = spot.readings()
    assert (reading["action"], reading["outcome"], list(reading["codes"]), reading["spent"]) == (
        "BUY", "REFUSED", ["BOOK_STALE"], False)
    spot.clock(False)
    spot.book(T0 + 15 * MINUTE - SECOND / 2)
    spot.step(T0 + 15 * MINUTE)
    assert list(spot.readings()[-1]["codes"]) == ["CLOCK_UNVERIFIED"]
    spot.clock(True)
    spot.book(T0 + 30 * MINUTE - SECOND / 2)
    spot.step(T0 + 30 * MINUTE)
    assert spot.readings()[-1]["outcome"] == "FILLED" and len(spot.fills()) == 1


def test_an_unusable_or_old_instrument_refuses_the_trade(spot):
    spot.fund()
    spot.instrument(T0 - 2 * timedelta(hours=1))  # checked two hours before: too old
    spot.daily(trend(day_open(T0) - DAY_MS))
    spot.book(T0 - SECOND / 2)
    spot.start()
    spot.step(T0)
    assert list(spot.readings()[-1]["codes"]) == ["INSTRUMENT_UNAVAILABLE"]
    spot.instrument(T0 + 15 * MINUTE, usable=False)
    spot.book(T0 + 15 * MINUTE - SECOND / 2)
    spot.step(T0 + 15 * MINUTE)
    assert len(spot.readings()) == 1  # the same refusal is stored once a day
    assert spot.fills() == []


def test_a_thin_book_refuses_with_depth_short(spot):
    spot.fund()
    spot.instrument(T0)
    spot.daily(trend(day_open(T0) - DAY_MS))
    spot.book(T0 - SECOND / 2, quantity="0.001")  # ten levels of 0.001 BTC: less than the buy
    spot.start()
    spot.step(T0)
    reading = spot.readings()[-1]
    assert reading["outcome"] == "REFUSED" and list(reading["codes"]) == ["DEPTH_SHORT"]
    assert spot.fills() == []


def test_the_rule_sells_all_when_the_trend_turns(spot):
    closes = spot.ready()
    spot.start()
    spot.step(T0)
    bought = spot.btc()
    assert bought > 0
    # The next day closes far below every anchor: the target is 0, everything is sold.
    day2 = T0 + timedelta(days=1)
    spot.daily({day_open(T0): Decimal("20000")})
    spot.instrument(day2)
    spot.book(day2 - SECOND / 2)
    spot.step(day2)
    reading = spot.readings()[-1]
    expected = expected_reading({**closes, day_open(T0): Decimal("20000")}, day2)
    assert expected.result == spot_rule.CASH and reading["target"] == 0
    assert (reading["action"], reading["outcome"]) == ("SELL_ALL", "FILLED")
    sell = spot.fills()[-1]
    assert (sell["side"], sell["reason"], sell["quantity"]) == ("SELL", "RULE_SELL", bought)
    assert spot.btc() == 0 and sell["quantity_after"] == 0
    assert spot.account()["cash"] == sell["cash_after"]
    assert spot.reconcile(day2 + SECOND)["status"] == "OK"
    # The day after, still in cash: nothing changes.
    day3 = day2 + timedelta(days=1)
    spot.daily({day_open(day2): Decimal("19000")})
    spot.instrument(day3)
    spot.book(day3 - SECOND / 2)
    spot.step(day3)
    assert spot.readings()[-1]["outcome"] == "NO_CHANGE" and len(spot.fills()) == 2


# ---- R4: the owner's controls, the latches and the stops --------------------------------------------------------------

def test_a_paused_run_refuses_a_buy_until_resumed(spot):
    spot.ready()
    spot.start()
    spot.step(T0.replace(minute=4))  # the run starts before the reading
    spot.request("PAUSE")
    spot.step(T0)
    run = spot.run()
    assert run["state"] == "PAUSED" and list(run["causes"]) == ["OWNER"]
    reading = spot.readings()[-1]
    assert (reading["action"], reading["outcome"], list(reading["codes"])) == ("BUY", "REFUSED", ["RUN_NOT_RUNNING"])
    spot.request("RESUME")
    spot.book(T0 + 15 * MINUTE - SECOND / 2)
    spot.step(T0 + 15 * MINUTE)
    assert spot.run()["state"] == "RUNNING" and spot.readings()[-1]["outcome"] == "FILLED"


def test_a_paused_run_still_sells(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    spot.request("PAUSE")
    day2 = T0 + timedelta(days=1)
    spot.daily({day_open(T0): Decimal("20000")})
    spot.instrument(day2)
    spot.book(day2 - SECOND / 2)
    spot.step(day2)
    assert spot.run()["state"] == "PAUSED"
    reading = spot.readings()[-1]
    assert (reading["action"], reading["outcome"]) == ("SELL_ALL", "FILLED") and spot.btc() == 0


def test_stop_and_sell_sells_everything_and_stops_the_run(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    first = spot.run()
    spot.request("STOP")
    spot.book(T0 + 10 * SECOND)
    spot.step(T0 + 10 * SECOND)
    run = spot.run()
    assert run["id"] == first["id"] and run["state"] == "STOPPED" and run["stop_reason"] == "OWNER"
    assert [row["reason"] for row in spot.fills()] == ["RULE_BUY", "STOP_SELL"] and spot.btc() == 0
    assert "STOP_REQUESTED" in spot.events() and spot.events()[-1] == "STOPPED"
    assert spot.reconcile(T0 + 11 * SECOND)["status"] == "OK"
    # A stopped run reads and trades nothing; the owner's Start begins a new run, which reads the day for itself.
    spot.book(T0 + 20 * MINUTE)
    spot.step(T0 + 20 * MINUTE)
    assert len(spot.fills()) == 2
    request = spot.request("START")
    spot.book(T0 + 21 * MINUTE)
    spot.step(T0 + 21 * MINUTE)
    second = spot.run()
    assert second["id"] != first["id"] and second["started_by"] == "OWNER" and second["request_id"] == request
    assert second["state"] == "RUNNING" and spot.readings()[-1]["run_id"] == second["id"]
    assert spot.readings()[-1]["outcome"] == "FILLED"


def test_a_run_the_owner_starts_reads_the_day_at_once(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    spot.request("STOP")
    spot.book(T0 + 10 * SECOND)
    spot.step(T0 + 10 * SECOND)
    assert spot.run()["state"] == "STOPPED"
    spot.request("START")
    spot.book(T0 + 20 * SECOND)
    spot.step(T0 + 20 * SECOND)
    # The 15 minutes between tries are a run's own: the new run has not read the day yet, so it reads it now.
    second = spot.run()
    assert second["state"] == "RUNNING" and second["started_by"] == "OWNER"
    assert spot.readings()[-1]["run_id"] == second["id"] and spot.readings()[-1]["outcome"] == "FILLED"
    assert [row["reason"] for row in spot.fills()] == ["RULE_BUY", "STOP_SELL", "RULE_BUY"]


def test_owner_requests_are_answered_once(spot):
    spot.ready()
    spot.start()
    spot.step(T0.replace(minute=4))
    resume = spot.request("RESUME")  # not paused by the owner
    start = spot.request("START")  # a run is live
    pause = spot.request("PAUSE")
    again = spot.request("PAUSE")
    spot.step(T0.replace(minute=4, second=1))
    answers = {row["id"]: (row["status"], list(row["reasons"])) for row in spot.rows(
        "SELECT id, status, reasons FROM spot_owner_requests")}
    assert answers[resume] == ("REJECTED", ["NOT_PAUSED_BY_OWNER"])
    assert answers[start] == ("REJECTED", ["RUN_LIVE"])
    assert answers[pause] == ("APPLIED", []) and answers[again] == ("REJECTED", ["ALREADY_PAUSED"])
    # A request for a run that has ended is refused.
    spot.request("STOP")
    spot.step(T0.replace(minute=4, second=2))
    late = spot.request("RESUME")
    spot.step(T0.replace(minute=4, second=3))
    assert spot.rows("SELECT status, reasons FROM spot_owner_requests WHERE id = :id", id=late)[0] == {
        "status": "REJECTED", "reasons": ["RUN_NOT_LIVE"]}


def test_the_daily_loss_latch_pauses_and_clears_at_the_next_reference(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    held = spot.btc()
    nav = spot.account()["nav"]
    # BTC falls far enough to take the account 2% below the day's reference, not 8% below its high.
    cash = spot.account()["cash"]
    bid = ((nav * 100 * Decimal("0.97") - cash) / held).quantize(Decimal("0.01"))
    spot.book(T0 + 30 * SECOND, bid=format(bid, "f"), ask=format(bid + Decimal("0.01"), "f"))
    spot.step(T0 + 30 * SECOND)
    run = spot.run()
    assert run["state"] == "PAUSED" and list(run["causes"]) == ["DAILY_LOSS"]
    [latch] = spot.rows("SELECT * FROM spot_latches")
    assert latch["cause"] == "DAILY_LOSS" and latch["resolved_at"] is None
    # The next UTC day's reference clears it before the day's reading.
    day2 = T0 + timedelta(days=1)
    spot.daily({day_open(T0): max(trend(day_open(T0) - DAY_MS).values()) + 100})
    spot.book(day2 - SECOND / 2, bid=format(bid, "f"), ask=format(bid + Decimal("0.01"), "f"))
    spot.step(day2)
    assert spot.run()["state"] == "RUNNING"
    assert spot.rows("SELECT resolution FROM spot_latches")[0]["resolution"]["rule"] == "NEXT_UTC_DAY"


def test_the_drawdown_stop_sells_everything_and_stops(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    spot.book(T0 + 20 * SECOND, bid="18000.00", ask="18000.01")  # BTC -70%: the account about -10%
    spot.step(T0 + 20 * SECOND)
    run = spot.run()
    assert run["state"] == "STOPPING" and run["stop_reason"] == "DRAWDOWN"
    assert sorted(run["causes"]) == ["DAILY_LOSS", "DRAWDOWN"]
    spot.book(T0 + 21 * SECOND, bid="18000.00", ask="18000.01")
    spot.step(T0 + 21 * SECOND)
    run = spot.run()
    assert run["state"] == "STOPPED" and spot.btc() == 0
    assert [row["reason"] for row in spot.fills()] == ["RULE_BUY", "STOP_SELL"]
    assert all(row["resolved_at"] is not None for row in spot.rows("SELECT resolved_at FROM spot_latches"))
    assert spot.reconcile(T0 + 22 * SECOND)["status"] == "OK"
    # A drawdown-stopped account starts nothing by itself.
    spot.step(T0 + 30 * SECOND)
    assert spot.scalar("SELECT count(*) FROM spot_runs") == 1


def test_a_stopping_run_waits_for_a_fresh_book_to_sell(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    spot.request("STOP")
    spot.step(T0 + 10 * SECOND)  # the book is 10.5 s old: nothing can be sold yet
    assert spot.run()["state"] == "STOPPING" and len(spot.fills()) == 1
    assert spot.scalar("SELECT count(*) FROM execution_incidents WHERE code = 'STOP_SELL_WAITS'") == 1
    spot.book(T0 + 11 * SECOND)
    spot.step(T0 + 11 * SECOND)
    assert spot.run()["state"] == "STOPPED" and spot.btc() == 0


# ---- R4: the fencing -----------------------------------------------------------------------------------------------

def test_a_stale_epoch_cannot_step(spot):
    spot.ready()
    first = spot.start()
    spot.restart()
    with pytest.raises(xstore.LostAuthority):
        first.step(T0)
    spot.step(T0)
    assert spot.run() is not None and len(spot.fills()) == 1


def test_a_restarted_engine_does_not_trade_a_spent_day_again(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    spot.restart()
    spot.book(T0 + MINUTE)
    result = spot.engine.recover(T0 + MINUTE)
    assert result["status"] == "OK"
    spot.step(T0 + MINUTE + SECOND)
    assert len(spot.fills()) == 1 and len(spot.readings()) == 1


# ---- R3: the postings, the top-ups and the reconciliation -----------------------------------------------------------

def test_every_fill_posts_a_balanced_journal_that_reconciles(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    [fill] = spot.fills()
    rows = spot.rows(
        "SELECT p.asset, p.book_account, p.amount FROM journal_postings p JOIN journal_transactions j "
        "ON j.id = p.tx_id WHERE j.spot_fill_id = :id ORDER BY p.id", id=fill["id"])
    assert [(row["asset"], row["book_account"], row["amount"]) for row in rows] == [
        ("USDT", "OWNER_CASH", -fill["gross"]), ("USDT", "CLEARING", fill["gross"]),
        ("BTC", "CLEARING", -fill["quantity"]), ("BTC", "OWNER_ASSET", fill["quantity"]),
        ("USDT", "OWNER_CASH", -fill["fee"]), ("USDT", "EXPENSE", fill["fee"])]
    assert accounting.reconcile_with(spot.api)["status"] == "OK"  # the API's own reconciliation, as asl_api


def test_a_top_up_is_nav_neutral_while_bitcoin_is_held(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    before = spot.account()
    # The top-up values the account at the database's clock: a book received now, at the bid the engine used.
    spot.book(xstore.db_now(spot.admin))
    nav_before = before["nav"]
    funding = spot.top_up("500")
    assert funding["status"] == "POSTED"
    after = spot.account()
    assert after["contributions"] == before["contributions"] + 500 and after["cash"] == before["cash"] + 500
    assert after["high_water_nav"] == before["high_water_nav"]
    assert abs(after["nav"] - nav_before) < Decimal("0.000000001")
    assert Decimal(funding["preflow_nav"]) == nav_before
    assert spot.reconcile(T0 + SECOND)["status"] == "OK"


def test_a_top_up_while_bitcoin_is_held_never_reads_as_a_loss(spot):
    """The money-path review (2026-11-12): the account's reads showed the newest valuation, from before a top-up,
    against the contributions after it. Until the engine values the changed account (its next step, ACCOUNT_CHANGE)
    they show the cash and BTC now at that valuation's bid."""
    spot.ready()
    spot.start()
    spot.step(T0)
    assert spot.btc() > 0
    before, cockpit = accounting.account_snapshot(), spot_views.overview(spot.api)["account"]
    spot.book(xstore.db_now(spot.admin))
    assert spot.top_up("500")["status"] == "POSTED"
    account = spot.account()
    for shown in (accounting.account_snapshot(), spot_views.overview(spot.api)["account"]):
        assert Decimal(shown["equity"]) == Decimal(before["equity"]) + 500
        assert Decimal(shown["contributions"]) == Decimal(before["contributions"]) + 500
        assert Decimal(shown["pnl"]) == Decimal(before["pnl"]) == Decimal(cockpit["pnl"])
        assert abs(Decimal(shown["nav"]) - Decimal(before["nav"])) < Decimal("0.000000001")
    # The engine's next step values the changed account: the book it reads is the one received by its time.
    spot.step(T0 + SECOND)
    [newest] = spot.rows("SELECT purpose, account_version, cash, equity, quality FROM spot_valuations "
                         "ORDER BY valued_at DESC, recorded_at DESC LIMIT 1")
    assert (newest["purpose"], newest["account_version"], newest["cash"], newest["quality"]) == (
        "ACCOUNT_CHANGE", account["version"], account["cash"], "VALID")
    assert newest["equity"] == Decimal(before["equity"]) + 500
    assert accounting.account_snapshot()["equity"] == format(newest["equity"], "f")


def test_a_book_received_after_the_steps_time_is_not_used(spot):
    """The step's book is the newest received by its time, so a fill never cites a quote from after it; the worker's
    step takes its time from the database's clock once it holds its locks."""
    spot.fund()
    spot.instrument(T0)
    spot.daily(trend(day_open(T0) - DAY_MS))
    spot.book(T0 + SECOND / 2)  # received after the step's time
    spot.start()
    spot.step(T0)
    [reading] = spot.readings()
    assert reading["outcome"] == "REFUSED" and "BOOK_STALE" in list(reading["codes"]) and spot.fills() == []
    spot.renew()
    spot.engine.step()  # the database's clock: today, far from T0's book and candles
    now = xstore.db_now(spot.admin)
    stepped = spot.scalar("SELECT max(at) FROM spot_rule_readings")
    assert stepped is not None and abs((now - stepped).total_seconds()) < 60


def test_a_top_up_waits_for_a_fresh_bid_while_bitcoin_is_held(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    funding = spot.top_up("100")
    assert funding["status"] == "PENDING_VALUATION"  # the only book is not fresh by the database's clock
    spot.book(xstore.db_now(spot.admin))
    retried = accounting.resolve_pending(funding["id"], "RETRY", "test")
    assert retried["status"] == "POSTED"
    assert spot.reconcile(T0 + MINUTE)["status"] == "OK"


def test_reconciliation_after_buys_sells_a_top_up_and_a_restart(spot):
    closes = spot.ready()
    spot.start()
    spot.step(T0)
    assert spot.reconcile(T0 + SECOND)["status"] == "OK"
    day2 = T0 + timedelta(days=1)
    # Below every anchor (about 59,000, 55,000 and 41,750), by a fall small enough that the rule buys again after.
    spot.daily({day_open(T0): Decimal("41000")})
    spot.instrument(day2)
    spot.book(day2 - SECOND / 2)
    spot.step(day2)
    assert spot.btc() == 0 and len(spot.fills()) == 2
    spot.restart()
    spot.book(day2 + MINUTE)
    assert spot.engine.recover(day2 + MINUTE)["status"] == "OK"
    assert spot.top_up("250")["status"] == "POSTED"  # cash only: no bid needed
    assert spot.reconcile(day2 + 2 * MINUTE)["status"] == "OK"
    # The trend is back the day after: the rule buys again, from the larger account.
    day3 = day2 + timedelta(days=1)
    spot.daily({day_open(day2): max(closes.values()) + 1000})
    spot.instrument(day3)
    spot.book(day3 - SECOND / 2)
    spot.step(day3)
    assert [row["side"] for row in spot.fills()] == ["BUY", "SELL", "BUY"]
    assert spot.reconcile(day3 + SECOND)["status"] == "OK"
    assert accounting.reconcile()["status"] == "OK"
    assert postings_balance(spot)
    assert spot.account()["contributions"] == Decimal("10250")


def test_a_discrepancy_holds_buys_until_a_reconciliation_passes(spot):
    spot.ready()
    spot.start()
    spot.step(T0.replace(minute=4))
    spot.raw("UPDATE account_holdings SET quantity = quantity + 0.00000001 WHERE asset = 'BTC'")
    result = spot.reconcile(T0.replace(minute=4, second=30))
    assert result["status"] == "DISCREPANCY" and result["failed_checks"] == ["holding_BTC"]
    account = spot.account()
    assert account["reconciliation_failed"] and account["paused"]
    spot.raw("UPDATE account_holdings SET quantity = quantity - 0.00000001 WHERE asset = 'BTC'")
    spot.step(T0)
    run = spot.run()
    assert run["state"] == "PAUSED" and list(run["causes"]) == ["INTEGRITY"]
    reading = spot.readings()[-1]
    assert reading["outcome"] == "REFUSED" and list(reading["codes"]) == ["RUN_NOT_RUNNING", "INTEGRITY"]
    result = spot.reconcile(T0 + MINUTE)
    assert result["status"] == "OK" and result["integrity_cleared"] == str(run["id"])
    assert spot.run()["state"] == "RUNNING" and not spot.account()["paused"]
    spot.book(T0 + 15 * MINUTE - SECOND / 2)
    spot.step(T0 + 15 * MINUTE)
    assert spot.readings()[-1]["outcome"] == "FILLED"


@pytest.mark.parametrize("check", ["nav_futures_valuation", "nav_persisted_valuation", "nav_valuation"])
def test_a_nav_failure_keeps_the_latch_a_passing_reconciliation_would_clear(spot, check):
    # A futures-era failure the retired code kept (SYNTHETIC: written as it wrote them, before migration 0041's
    # switch) keeps the integrity latch as the spot account's own NAV failure does; a later clear ends it.
    spot.ready()
    spot.start()
    spot.step(T0.replace(minute=4))
    spot.raw("UPDATE account_state SET reconciliation_failed = true, paused = true WHERE id = 1")
    spot.raw("INSERT INTO outbox_events (event, object_id, account_version, payload) "
             "VALUES ('RECONCILIATION_FAILED', :object, 1, CAST(:payload AS json))",
             object=str(uuid4()), payload=json.dumps({"failed_checks": [check]}))
    result = spot.reconcile(T0.replace(minute=4, second=30))
    assert result["status"] == "OK" and result["integrity_kept"] == [check]
    assert "integrity_cleared" not in result
    account = spot.account()
    assert account["reconciliation_failed"] and account["paused"]


def test_a_tampered_fill_fails_its_checks(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    with spot.admin.begin() as connection:
        connection.execute(text("SET LOCAL session_replication_role = replica"))  # past the append-only guard
        connection.execute(text("UPDATE spot_fills SET fee = fee + 0.00000001"))
    failed = spot.reconcile(T0 + SECOND)["failed_checks"]
    assert "spot_fill_postings" in failed and "spot_fill_amounts" in failed


# ---- R3: dust ---------------------------------------------------------------------------------------------------------

def test_bitcoin_below_the_minimum_after_a_sale_is_dust(spot):
    spot.fund()
    spot.instrument(T0, step="0.000001", min_qty="0.000001")
    closes = trend(day_open(T0) - DAY_MS)
    spot.daily(closes)
    spot.book(T0 - SECOND / 2, bid="61234.56", ask="61234.57")
    spot.start()
    spot.step(T0)
    bought = spot.btc()
    assert bought != floor_to_step(bought, Decimal(STEP)), "the synthetic buy must leave a remainder below 0.00001"
    # The instrument's step grows: the remainder can no longer be sold.
    spot.instrument(T0 + SECOND)
    spot.request("STOP")
    spot.book(T0 + 2 * SECOND, bid="61234.56", ask="61234.57")
    spot.step(T0 + 2 * SECOND)
    run = spot.run()
    dust = bought - floor_to_step(bought, Decimal(STEP))
    assert run["state"] == "STOPPED" and spot.btc() == dust < Decimal(MIN_QTY)
    assert spot.rows("SELECT detail FROM spot_run_events WHERE kind = 'STOPPED'")[0]["detail"]["dust"] == format(dust, "f")
    assert spot.reconcile(T0 + 3 * SECOND)["status"] == "OK"


def test_dust_the_retired_sales_left_reconciles_and_is_not_traded(spot):
    """M3 to M10's sales left coins below their minimum order; their fills are archived by migration 0041. The
    journal keeps their postings: BTC's dust is the start of the spot holding, the other coins' is kept unvalued."""
    spot.fund()
    with spot.admin.begin() as connection:
        connection.execute(text("SET LOCAL session_replication_role = replica"))  # the archived fill row is absent
        transaction = uuid4()
        connection.execute(text(
            "INSERT INTO journal_transactions (id, fill_id, account_version) VALUES (:id, :fill, 1)"),
            {"id": transaction, "fill": uuid4()})
        for asset, book, amount in (("BTC", "OWNER_ASSET", "0.000003"), ("BTC", "CLEARING", "-0.000003"),
                                    ("SOL", "OWNER_ASSET", "0.004"), ("SOL", "CLEARING", "-0.004")):
            connection.execute(text(
                "INSERT INTO journal_postings (tx_id, asset, book_account, amount) VALUES (:tx, :asset, :book, :amount)"),
                {"tx": transaction, "asset": asset, "book": book, "amount": Decimal(amount)})
        connection.execute(text("UPDATE account_holdings SET quantity = 0.000003 WHERE asset = 'BTC'"))
        connection.execute(text("UPDATE account_holdings SET quantity = 0.004 WHERE asset = 'SOL'"))
    assert accounting.reconcile_with(spot.api)["status"] == "OK"
    spot.instrument(T0)
    spot.daily(trend(day_open(T0) - DAY_MS))
    spot.book(T0 - SECOND / 2)
    spot.start()
    spot.step(T0)
    [fill] = spot.fills()
    assert fill["quantity_after"] == fill["quantity"] + Decimal("0.000003") == spot.btc()
    assert spot.reconcile(T0 + SECOND)["status"] == "OK"
    snapshot = accounting.account_snapshot()
    assert [(row["asset"], row["valued"]) for row in snapshot["holdings"]] == [("BTC", True), ("SOL", False)]
    # Stop and sell sells the whole steps; the retired dust below a step stays with its postings.
    spot.request("STOP")
    spot.book(T0 + 2 * SECOND)
    spot.step(T0 + 2 * SECOND)
    assert spot.run()["state"] == "STOPPED" and spot.btc() == Decimal("0.000003")
    assert spot.reconcile(T0 + 3 * SECOND)["status"] == "OK"


# ---- the roles ------------------------------------------------------------------------------------------------------

def test_each_role_writes_only_its_own_records(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    with pytest.raises(DBAPIError):
        with spot.market.connect() as connection:
            connection.execute(text("SELECT cash FROM account_state"))
    with pytest.raises(DBAPIError):
        with spot.api.begin() as connection:
            connection.execute(text("UPDATE spot_runs SET state = 'STOPPED'"))
    with pytest.raises(DBAPIError):
        with spot.api.begin() as connection:
            connection.execute(text("DELETE FROM spot_fills"))
    with pytest.raises(DBAPIError):
        with spot.execution.begin() as connection:
            connection.execute(text(
                "INSERT INTO spot_owner_requests (id, kind, idempotency_key, request_hash) "
                "VALUES (:id, 'START', 'not-the-owner', :hash)"), {"id": uuid4(), "hash": "0" * 64})
    with pytest.raises(DBAPIError):
        with spot.execution.begin() as connection:
            connection.execute(text("UPDATE spot_fills SET fee = 0"))
    with pytest.raises(DBAPIError):  # an answered request is the engine's to write, never the API's
        with spot.api.begin() as connection:
            connection.execute(text(
                "INSERT INTO spot_owner_requests (id, kind, idempotency_key, request_hash, status, answered_at) "
                "VALUES (:id, 'START', 'answered-already', :hash, 'APPLIED', clock_timestamp())"),
                {"id": uuid4(), "hash": "0" * 64})
    with pytest.raises(DBAPIError):
        with spot.market.begin() as connection:
            connection.execute(text("UPDATE spot_daily_bars SET close = 1"))


def test_the_records_are_append_only_and_postings_stay_with_their_header(spot):
    """M3's immutability, kept for the spot records: not even the migration's identity changes or deletes a fill, a
    reading, a valuation or a run, and a posting is added only in the transaction of its journal header."""
    spot.ready()
    spot.start()
    spot.step(T0)
    [fill] = spot.fills()
    for statement in ("UPDATE spot_fills SET fee = fee + 1", "DELETE FROM spot_fills",
                      "UPDATE spot_rule_readings SET reason = 'CHANGED'", "DELETE FROM spot_valuations",
                      "DELETE FROM spot_run_events", "DELETE FROM spot_daily_references", "DELETE FROM spot_runs"):
        with pytest.raises(DBAPIError, match="append-only spot record"):
            spot.raw(statement)
    header = spot.scalar("SELECT id FROM journal_transactions WHERE spot_fill_id = :id", id=fill["id"])
    with pytest.raises(DBAPIError, match="postings must be written with their journal header"):
        with spot.execution.begin() as connection:
            connection.execute(text(
                "INSERT INTO journal_postings (tx_id, asset, book_account, amount) "
                "VALUES (:tx, 'USDT', 'OWNER_CASH', 1)"), {"tx": header})
    assert accounting.reconcile()["status"] == "OK"


def test_the_valuation_runs_every_minute_while_bitcoin_is_held(spot):
    spot.ready()
    spot.start()
    spot.step(T0)
    count = spot.scalar("SELECT count(*) FROM spot_valuations")
    for seconds in (30, 59, 89, 90, 91):
        spot.book(T0 + seconds * SECOND - SECOND / 2)
        spot.step(T0 + seconds * SECOND)
    # The hour's first valuation without one is its hourly one; a minute after it, a periodic one.
    purposes = [row["purpose"] for row in spot.rows(
        "SELECT purpose FROM spot_valuations ORDER BY valued_at, recorded_at OFFSET :count", count=count)]
    assert purposes == ["HOURLY", "PERIODIC"] and POLICY.valuation_seconds == 60
    # Without BTC that can be sold, only the hourly ones.
    spot.request("STOP")
    spot.book(T0 + 92 * SECOND)
    spot.step(T0 + 92 * SECOND)
    count = spot.scalar("SELECT count(*) FROM spot_valuations")
    for minutes in (3, 4, 5):
        spot.book(T0 + minutes * MINUTE)
        spot.step(T0 + minutes * MINUTE)
    assert spot.scalar("SELECT count(*) FROM spot_valuations") == count


# ---- ExecPlan 0061: the Cockpit's run against holding Bitcoin -------------------------------------------------------

def test_the_run_against_holding_bitcoin_is_paired_by_day(spot):
    """The overview's ``since_start``: between the run's first and newest timely daily references, its NAV against
    Bitcoin's daily close of the day before each; nothing until two such days, a late reference left out."""
    spot.ready()
    spot.start()
    spot.step(T0)
    assert spot.btc() > 0
    # T0's reference came ten minutes after midnight: late, so it is not a pair's end.
    assert spot.scalar("SELECT quality FROM spot_daily_references") == "LATE_CONSERVATIVE"
    assert spot_views.overview(spot.api, at=T0 + SECOND)["run"]["since_start"] is None
    first_close, second_close = Decimal("61000.00"), Decimal("63500.00")
    day2 = day_open(T0) + DAY_MS
    spot.daily({day_open(T0): first_close})
    at2 = T0.replace(minute=1) + timedelta(days=1)
    spot.book(at2 - SECOND / 2, bid="61000.00", ask="61000.01")
    spot.step(at2)
    # One timely day is not a pair.
    assert spot_views.overview(spot.api, at=at2 + SECOND)["run"]["since_start"] is None
    spot.daily({day2: second_close})
    at3 = at2 + timedelta(days=1)
    spot.book(at3 - SECOND / 2, bid="63000.00", ask="63000.01")
    spot.step(at3)
    references = spot.rows(
        "SELECT r.utc_date, r.quality, v.valued_at, v.nav FROM spot_daily_references r "
        "JOIN spot_valuations v ON v.id = r.valuation_id ORDER BY r.utc_date")
    assert [row["quality"] for row in references] == ["LATE_CONSERVATIVE", "TIMELY", "TIMELY"]
    first, last = references[1], references[2]
    since = spot_views.overview(spot.api, at=at3 + SECOND)["run"]["since_start"]
    assert since["from_at"] == spot_views.iso(first["valued_at"]) and since["at"] == spot_views.iso(last["valued_at"])
    assert (Decimal(since["from_price"]), Decimal(since["price"])) == (first_close, second_close)
    with localcontext(CONTEXT):
        assert since["account"] == spot_views.ratio(last["nav"] / first["nav"] - 1)
        assert since["bitcoin"] == spot_views.ratio(second_close / first_close - 1) == "0.04098361"
    assert Decimal(since["account"]) > 0
    # Stored rows only: the same answer hours later, without a step.
    assert spot_views.overview(spot.api, at=at3 + timedelta(hours=5))["run"]["since_start"] == since
