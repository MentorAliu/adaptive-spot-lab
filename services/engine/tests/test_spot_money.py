"""The spot account's money math (ExecPlan 0060 section 6, R2): the valuation, the fee, the book walk, the slippage
and the market orders' sizes and refusals, exact Decimal. Every price, quantity and filter here is SYNTHETIC; the
expected amounts were worked out by hand from ``SPOT_COST_V1`` (0.1% taker fee, 1 bp slippage)."""

from decimal import Decimal

import pytest

from app.execution.numbers import CONTEXT
from app.spot import money
from app.spot.definitions import COST

D = Decimal
FILTERS = money.Filters(step=D("0.00001"), min_qty=D("0.00001"), max_qty=D("9000"), min_notional=D("5"),
                        max_notional=D("9000000"))
ASKS = [(D("60000.01") + D("0.01") * n, D("2")) for n in range(10)]
BIDS = [(D("60000.00") - D("0.01") * n, D("2")) for n in range(10)]


def test_the_cost_is_the_one_the_plan_names():
    assert (COST.id, COST.levels, COST.book_max_age_ms, COST.slippage_bps, COST.taker) == (
        "SPOT_COST_V1", 10, 2000, D("1"), D("0.001"))


def test_the_valuation_is_cash_plus_bitcoin_at_the_bid_floored():
    assert money.equity(D("1000"), D(0), None) == D("1000")
    assert money.equity(D("1000"), D("0.1"), None) is None
    assert money.equity(D("1000.5"), D("0.12345678"), D("60000.01")) == D("8407.90803456")  # 8407.9080345678


def test_the_fee_rounds_up_and_the_fill_price_against_the_order():
    assert money.fee_for(D("0.00001"), D("60000.01"), D("0.001")) == D("0.00060001")
    third = CONTEXT.divide(D(1), D(3))
    assert money.fill_price("BUY", third, D("1")) == D("0.33336667")
    assert money.fill_price("SELL", third, D("1")) == D("0.33330000")
    assert money.ceil8(D("0.000000001")) == D("0.00000001") and money.floor8(D("0.000000019")) == D("0.00000001")


def test_the_walk_takes_the_levels_best_first():
    levels = [(D(100), D(1)), (D(101), D(1)), (D(102), D(1))]
    assert money.walk(levels, D("2.5")) == (D("100.8"), [(D(100), D(1)), (D(101), D(1)), (D(102), D("0.5"))])
    assert money.walk(levels, D("3.5")) is None
    assert money.walk(levels, D(0)) is None


def test_a_buy_takes_what_it_wants_down_to_the_step():
    fill = money.plan_buy(wanted=D("0.1234567"), cash=D("100000"), asks=ASKS, filters=FILTERS)
    assert isinstance(fill, money.Fill)
    assert (fill.side, fill.quantity, fill.average, fill.price) == ("BUY", D("0.12345"), D("60000.01"),
                                                                     D("60006.01000100"))
    assert (fill.gross, fill.fee) == (D("7407.74193463"), D("7.40774194"))
    assert (fill.cash_delta, fill.base_delta) == (D("-7415.14967657"), D("0.12345"))


def test_a_buy_spends_at_most_the_cash_with_its_fee_and_slippage():
    fill = money.plan_buy(wanted=D("1"), cash=D("1000"), asks=ASKS, filters=FILTERS)
    assert fill.quantity == D("0.01664") and fill.gross + fill.fee == D("999.49850643")
    one_more = money.plan_buy(wanted=D("0.01665"), cash=D("100000"), asks=ASKS, filters=FILTERS)
    assert one_more.gross + one_more.fee > D("1000")  # the next step would not have been paid for


def test_a_buy_walks_the_ten_levels_and_no_further():
    fill = money.plan_buy(wanted=D("3.5"), cash=D("1000000"), asks=ASKS, filters=FILTERS)
    assert fill.levels == [(D("60000.01"), D("2")), (D("60000.02"), D("1.5"))]
    assert (fill.price, fill.gross, fill.fee) == (D("60006.01428715"), D("210021.05000503"), D("210.02105001"))
    deeper = ASKS + [(D("60000.11"), D("100"))]
    short = money.plan_buy(wanted=D("21"), cash=D("10000000"), asks=deeper, filters=FILTERS)
    assert isinstance(short, money.Refusal) and short.codes == ["DEPTH_SHORT"]
    assert short.detail == {"quantity": "21", "depth": "20"}


@pytest.mark.parametrize(("wanted", "cash", "filters", "code"), [
    (D("0.000009"), D("100000"), FILTERS, "SIZE_BELOW_MINIMUM"),
    (D("1"), D("0.5"), FILTERS, "SIZE_BELOW_MINIMUM"),
    (D("0.00005"), D("100000"), FILTERS, "NOTIONAL_BELOW_MINIMUM"),
    (D("0.01"), D("100000"), money.Filters(D("0.00001"), D("0.00001"), D("9000"), D("5"), D("100")),
     "NOTIONAL_ABOVE_MAXIMUM"),
])
def test_a_buy_the_instrument_does_not_allow_is_refused(wanted, cash, filters, code):
    refusal = money.plan_buy(wanted=wanted, cash=cash, asks=ASKS, filters=filters)
    assert isinstance(refusal, money.Refusal) and refusal.codes == [code]


def test_a_buy_is_capped_by_the_instruments_maximum_and_refused_without_a_book():
    capped = money.plan_buy(wanted=D("5"), cash=D("10000000"), asks=ASKS,
                            filters=money.Filters(D("0.00001"), D("0.00001"), D("1.5"), D("5"), None))
    assert capped.quantity == D("1.5")
    assert money.plan_buy(wanted=D("1"), cash=D("1000"), asks=[], filters=FILTERS).codes == ["BOOK_UNAVAILABLE"]


def test_a_sell_is_capped_by_the_bitcoin_held_and_receives_its_gross_less_the_fee():
    fill = money.plan_sell(wanted=D("1"), held=D("0.5"), bids=BIDS, filters=FILTERS)
    assert (fill.side, fill.quantity, fill.price, fill.gross, fill.fee) == (
        "SELL", D("0.5"), D("59994.00000000"), D("29997.00000000"), D("29.99700000"))
    assert (fill.cash_delta, fill.base_delta) == (D("29967.00300000"), D("-0.5"))
    walked = money.plan_sell(wanted=D("2.5"), held=D("3"), bids=BIDS, filters=FILTERS)
    assert walked.levels == [(D("60000.00"), D("2")), (D("59999.99"), D("0.5"))]
    assert (walked.price, walked.gross, walked.fee) == (D("59993.99800020"), D("149984.99500050"),
                                                        D("149.98499501"))


def test_a_sell_of_dust_or_without_a_book_is_refused():
    dust = money.plan_sell(wanted=D("0.000009"), held=D("0.000009"), bids=BIDS, filters=FILTERS)
    assert isinstance(dust, money.Refusal) and dust.codes == ["SIZE_BELOW_MINIMUM"]
    assert money.plan_sell(wanted=D("1"), held=D("1"), bids=[], filters=FILTERS).codes == ["BOOK_UNAVAILABLE"]


@pytest.mark.parametrize(("bid", "sold"), [(D("100005"), False), (D("100010"), False), (D("100011"), True)])
def test_dust_is_what_a_sale_of_all_of_it_refuses_for_its_size_or_notional(bid, sold):
    # The money-path review's band (2026-11-12): 0.00005 BTC at a best bid of 100,005 is 5.00025 USDT, above the
    # minimum notional of 5, but the sale's notional is at the fill price, 1 bp lower (4.99975...), and is refused.
    # The dust rule and the sale agree, so a stopping run never waits on a sale its own checks refuse.
    held, bids = D("0.00005"), [(bid, D("1"))]
    plan = money.plan_sell(wanted=held, held=held, bids=bids, filters=FILTERS)
    assert money.sellable(held, bids, FILTERS) is sold
    assert isinstance(plan, money.Fill) is sold
    if not sold:
        assert plan.codes == ["NOTIONAL_BELOW_MINIMUM"]


def test_dust_without_a_book_is_its_size_and_a_thin_book_is_not_dust():
    assert money.sellable(D("0.00005"), [], FILTERS)  # no price: not dust on an unknown notional
    assert not money.sellable(D("0.000009"), [], FILTERS)  # below the lot step and the minimum quantity
    assert not money.sellable(D(0), BIDS, FILTERS)
    thin = money.plan_sell(wanted=D("100"), held=D("100"), bids=BIDS[:1], filters=FILTERS)
    assert isinstance(thin, money.Refusal) and thin.codes == ["DEPTH_SHORT"]
    assert money.sellable(D("100"), BIDS[:1], FILTERS)  # the sale waits for the book


def test_the_rule_trades_the_difference_at_equity_over_the_bid():
    assert money.difference_quantity(D("0.5"), D("0.2"), D("10000"), D("60000")) == D("0.05")
    assert money.difference_quantity(D("0.2"), D("0.5"), D("10000"), D("60000")) == D("0.05")
