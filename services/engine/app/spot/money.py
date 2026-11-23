"""The spot account's money math, exact Decimal and nothing else (ExecPlan 0060 sections 4.3 and 4.4).

Pure functions: no clock, no database. Every rounding is named and goes against the account: a fill price rounds
against the order, a buy's gross and every fee round up, a sell's gross rounds down, a quantity rounds down to the
instrument's step, and the valuation (``VALUATION_BID_V1``) floors cash plus the BTC at the best bid to 0.00000001.
The engine, the backtest and the tests call these and nothing else for amounts.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal, localcontext

from app.execution.numbers import AMOUNT, BPS, CONTEXT, ONE, ZERO, floor_to_step
from app.spot.definitions import COST, Cost

Level = tuple[Decimal, Decimal]  # (price, quantity), best first
BUY, SELL = "BUY", "SELL"


def ceil8(value: Decimal) -> Decimal:
    with localcontext(CONTEXT):
        return value.quantize(AMOUNT, rounding=ROUND_CEILING)


def floor8(value: Decimal) -> Decimal:
    with localcontext(CONTEXT):
        return value.quantize(AMOUNT, rounding=ROUND_FLOOR)


def equity(cash: Decimal, quantity: Decimal, bid: Decimal | None) -> Decimal | None:
    """``VALUATION_BID_V1``: cash plus the BTC held at the best bid, floored to 0.00000001; cash alone when nothing
    is held; None when BTC is held and no bid is given."""
    if quantity <= 0:
        return cash
    if bid is None:
        return None
    with localcontext(CONTEXT):
        return floor8(cash + quantity * bid)


def fee_for(quantity: Decimal, price: Decimal, rate: Decimal) -> Decimal:
    """The taker fee on the fill's notional, in USDT, rounded up."""
    with localcontext(CONTEXT):
        return ceil8(quantity * price * rate)


def walk(levels: Sequence[Level], quantity: Decimal) -> tuple[Decimal, list[Level]] | None:
    """The average price of taking ``quantity`` from the levels, best first, and the part of each level taken;
    None when the levels hold less."""
    left, notional, used = quantity, ZERO, []
    with localcontext(CONTEXT):
        for price, size in levels:
            if left <= 0:
                break
            take = min(size, left)
            if take > 0:
                used.append((price, take))
                notional += price * take
                left -= take
        if left > 0 or quantity <= 0:
            return None
        return notional / quantity, used


def fill_price(side: str, average: Decimal, slippage_bps: Decimal) -> Decimal:
    """The walked average with the slippage scenario against the order, rounded against it."""
    with localcontext(CONTEXT):
        if side == BUY:
            return ceil8(average * (ONE + slippage_bps / BPS))
        return floor8(average * (ONE - slippage_bps / BPS))


def difference_quantity(target: Decimal, held: Decimal, equity_value: Decimal, bid: Decimal) -> Decimal:
    """The BTC the rule's trade moves: ``|target - held| · equity / bid``, exact (the order rounds it down to the
    step)."""
    with localcontext(CONTEXT):
        return abs(target - held) * equity_value / bid


@dataclass(frozen=True)
class Filters:
    """The instrument's rules for a market order, as the feed stored them (``app.spot_market.market``)."""
    step: Decimal
    min_qty: Decimal
    max_qty: Decimal
    min_notional: Decimal
    max_notional: Decimal | None


@dataclass(frozen=True)
class Refusal:
    codes: list[str]
    detail: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Fill:
    """One market order's simulated fill. ``cash_delta`` and ``base_delta`` are what the account's USDT and BTC
    change by: a buy pays its gross and fee and receives the quantity; a sell receives its gross less the fee and
    gives the quantity."""
    side: str
    quantity: Decimal
    price: Decimal
    average: Decimal
    levels: list[Level]
    gross: Decimal
    fee: Decimal

    @property
    def cash_delta(self) -> Decimal:
        return -(self.gross + self.fee) if self.side == BUY else self.gross - self.fee

    @property
    def base_delta(self) -> Decimal:
        return self.quantity if self.side == BUY else -self.quantity


def _text(value: Decimal) -> str:
    return format(value, "f")


def _checked(side: str, quantity: Decimal, book: list[Level], filters: Filters, cost: Cost,
             caps: dict[str, Decimal]) -> Fill | Refusal:
    if quantity <= 0 or quantity < filters.min_qty:
        return Refusal(["SIZE_BELOW_MINIMUM"], {key: _text(value) for key, value in caps.items()}
                       | {"min_qty": _text(filters.min_qty)})
    walked = walk(book, quantity)
    if walked is None:
        return Refusal(["DEPTH_SHORT"], {"quantity": _text(quantity),
                                         "depth": _text(sum((size for _, size in book), ZERO))})
    average, used = walked
    price = fill_price(side, average, cost.slippage_bps)
    with localcontext(CONTEXT):
        notional = quantity * price
    if notional < filters.min_notional:
        return Refusal(["NOTIONAL_BELOW_MINIMUM"], {"notional": _text(ceil8(notional)),
                                                    "min_notional": _text(filters.min_notional)})
    if filters.max_notional is not None and notional > filters.max_notional:
        return Refusal(["NOTIONAL_ABOVE_MAXIMUM"], {"notional": _text(ceil8(notional)),
                                                    "max_notional": _text(filters.max_notional)})
    gross = ceil8(notional) if side == BUY else floor8(notional)
    return Fill(side, quantity, price, average, used, gross, fee_for(quantity, price, cost.taker))


def plan_buy(*, wanted: Decimal, cash: Decimal, asks: Sequence[Level], filters: Filters,
             cost: Cost = COST) -> Fill | Refusal:
    """A market buy of ``wanted`` BTC on the asks: the largest step at most ``wanted``, the instrument's maximum and
    what the cash pays for at the deepest level the order can reach with the slippage and the fee; then walked and
    checked again on the fill."""
    book = list(asks[:cost.levels])
    if not book:
        return Refusal(["BOOK_UNAVAILABLE"])
    with localcontext(CONTEXT):
        highest = book[-1][0] * (ONE + cost.slippage_bps / BPS)
        per_unit = highest * (ONE + cost.taker)
        caps = {"wanted": wanted, "cash": cash / per_unit if cash > 0 else ZERO, "max_quantity": filters.max_qty}
    quantity = floor_to_step(min(caps.values()), filters.step)
    fill = _checked(BUY, quantity, book, filters, cost, caps)
    if isinstance(fill, Fill) and fill.gross + fill.fee > cash:
        return Refusal(["CASH_SHORT"], {"gross": _text(fill.gross), "fee": _text(fill.fee), "cash": _text(cash)})
    return fill


# The refusals that make BTC dust: a sale of all of it fails the instrument's minimum quantity or notional.
DUST_CODES = frozenset({"SIZE_BELOW_MINIMUM", "NOTIONAL_BELOW_MINIMUM"})


def sellable(quantity: Decimal, bids: Sequence[Level], filters: Filters, cost: Cost = COST) -> bool:
    """``SPOT_RULE_V1``'s dust rule: BTC held that a market sell of all of it would not refuse for its size or its
    notional, by the sale's own checks (``plan_sell``: the lot step, the minimum quantity, and the minimum notional at
    the fill price, slippage included). Without bids only the size is checked: BTC is not dust on an unknown price. A
    book too thin to fill the sale does not make it dust either; the sale waits for the book."""
    if quantity <= 0:
        return False
    steps = floor_to_step(quantity, filters.step)
    if steps <= 0 or steps < filters.min_qty:
        return False
    if not bids:
        return True
    plan = plan_sell(wanted=quantity, held=quantity, bids=bids, filters=filters, cost=cost)
    return not (isinstance(plan, Refusal) and DUST_CODES & set(plan.codes))


def plan_sell(*, wanted: Decimal, held: Decimal, bids: Sequence[Level], filters: Filters,
              cost: Cost = COST) -> Fill | Refusal:
    """A market sell of ``wanted`` BTC on the bids: the largest step at most ``wanted``, the BTC held and the
    instrument's maximum; then walked and checked on the fill."""
    book = list(bids[:cost.levels])
    if not book:
        return Refusal(["BOOK_UNAVAILABLE"])
    caps = {"wanted": wanted, "held": held, "max_quantity": filters.max_qty}
    quantity = floor_to_step(min(caps.values()), filters.step)
    return _checked(SELL, quantity, book, filters, cost, caps)
