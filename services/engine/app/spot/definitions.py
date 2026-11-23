"""The spot account's code-owned definitions (ExecPlan 0060 sections 4.1 and 4.3; migration 0041).

``SPOT_RULE_V1`` is the daily rule that decides the main account; ``SPOT_POLICY_V1`` what the account may hold and do,
its latches, its runs and the data a trade needs; ``SPOT_COST_V1`` how a fill and its fee are simulated, with the
provider value it uses and the date it was read. Migration 0041 freezes the three into ``execution_definitions`` with
their hashes; the worker starts only when the stored rows equal this code, and each run records the three hashes as
``SYSTEM``. A change is a new version in an update the owner installs.
"""

import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.execution.definitions import canonical_json, definition_hash
from app.execution.numbers import dec

SYMBOL = "BTCUSDT"
BASE, QUOTE = "BTC", "USDT"
RULE_ID, POLICY_ID, COST_ID = "SPOT_RULE_V1", "SPOT_POLICY_V1", "SPOT_COST_V1"
KINDS = ("SPOT_RULE", "SPOT_POLICY", "SPOT_COST")
# The trades the policy names: the rule's daily buy and sell, and the sell of everything when a run stops.
RULE_BUY, RULE_SELL, STOP_SELL = "RULE_BUY", "RULE_SELL", "STOP_SELL"
ACTIONS = (RULE_BUY, RULE_SELL, STOP_SELL)
DAY_MS = 86_400_000
FEE_SOURCE_URL = ("https://www.binance.com/en/support/faq/how-to-calculate-binance-spot-trading-fees-"
                  "e85d6e703b874674840122196b89780a")

SPOT_RULE_V1: dict[str, Any] = {
    "id": RULE_ID, "kind": "SPOT_RULE", "version": 1, "status": "PROPOSED",
    "source": "ExecPlan 0060 sections 4.1 and 4.2, approved by the owner on 2026-11-12",
    "account": "THE_MAIN_SPOT_ACCOUNT", "decider": "CODE_NO_MODEL", "instrument": "BTCUSDT_SPOT_PAPER",
    "candles": "BINANCE'S_FINAL_1D_SPOT_CANDLES_STORED_BY_THE_FEED",
    "day": "THE_LAST_COMPLETE_UTC_DAY_BEFORE_THE_READING'S_DAY",
    "lookback_days": [30, 91, 365],
    "signal": "THE_MEAN_OF_THE_SIGNS_OF_THE_DAY'S_CLOSE_AGAINST_THE_CLOSE_EACH_LOOKBACK_BEFORE_IT_A_SIGN_IS_0_WHEN_EQUAL",
    "anchor": "THE_NEAREST_STORED_DAY_AT_OR_BEFORE_THE_LOOKBACK'S_DAY_WITHIN_THE_TOLERANCE_ELSE_NOT_READABLE",
    "anchor_tolerance_days": 7,
    "volatility": "THE_ANNUALIZED_EXPONENTIALLY_WEIGHTED_STANDARD_DEVIATION_OF_THE_DAILY_LOG_RETURNS_OF_THE_STORED_DAYS_"
                  "FROM_THE_DAY_365_DAYS_BEFORE_TO_THE_DAY",
    "volatility_days": 365, "volatility_centre_of_mass_days": 60,
    "volatility_recursion": "VAR_NEXT_=_(60_X_VAR_+_RETURN_SQUARED)_/_61_SEEDED_WITH_THE_FIRST_RETURN_SQUARED",
    "gap_return": "A_RETURN_ACROSS_MISSING_DAYS_COUNTS_ONCE", "annualization_days": 365, "minimum_days_stored": 300,
    "direction": "MAX(SIGNAL,_0): LONG_OR_CASH_NEVER_SHORT",
    "target": "MAX(SIGNAL,_0)_X_MIN(CAP,_VOLATILITY_TARGET_/_VOLATILITY)_QUANTIZED_TOWARD_ZERO_TO_THE_STEP",
    "volatility_target": "0.05", "fraction_cap": "1", "target_step": "0.001", "flat_band": "0.01",
    "flat": "A_TARGET_BELOW_THE_FLAT_BAND_IS_0",
    "held": "THE_BTC_HELD_AT_THE_FRESH_BEST_BID_OVER_EQUITY_TO_0.00000001_DOWN",
    "rebalance_buffer": "0.03",
    "acts": "A_TARGET_OF_0_WITH_BTC_HELD: SELL_ALL; ELSE_WHEN_THE_TARGET_IS_MORE_THAN_THE_BUFFER_FROM_HELD: BUY_OR_SELL_"
            "THE_DIFFERENCE_(TARGET_-_HELD)_X_EQUITY_AT_THE_BOOK; ELSE_NO_CHANGE",
    "quantity": "|TARGET_-_HELD|_X_EQUITY_/_THE_BEST_BID_DOWN_TO_THE_STEP; A_SELL_AT_MOST_THE_BTC_HELD",
    "read_after_ms": 300_000,
    "evaluated": "AT_THE_ENGINE'S_FIRST_STEP_AT_OR_AFTER_00:05_UTC_ONCE_THE_DAY'S_FINAL_CANDLE_IS_STORED",
    "retry_seconds": 900,
    "day_spent": "BY_A_FILL_OR_A_READING_THAT_CHANGES_NOTHING; A_DAY_NOT_READABLE_YET_OR_A_REFUSAL_TRIES_AGAIN_EVERY_"
                 "15_MINUTES",
    "held_unknown": "BTC_HELD_WITHOUT_A_FRESH_BEST_BID: REFUSED_BID_STALE_AND_TRIED_AGAIN",
    "gates": "A_LATCH_A_PAUSED_RUN_OR_AN_INTEGRITY_HOLD: NO_BUY_AND_A_SELL_STILL_SELLS; A_STALE_BOOK_A_THIN_BOOK_AN_"
             "UNVERIFIED_CLOCK_OR_AN_UNUSABLE_INSTRUMENT: NO_TRADE_REFUSED_WITH_ITS_CODE_AND_TRIED_AGAIN",
    "holding": "BTC_THAT_CAN_BE_SOLD: A_SALE_OF_ALL_OF_IT_ON_THE_BOOK_THE_VALUATION_READS_PASSES_THE_SALE'S_OWN_"
               "MINIMUM_QUANTITY_AND_NOTIONAL_CHECKS_(THE_NOTIONAL_AT_THE_FILL_PRICE); WITHOUT_THAT_BOOK_THE_MINIMUM_"
               "QUANTITY_ALONE; LESS_IS_DUST_AND_COUNTS_AS_NOTHING_HELD_FOR_SELL_ALL",
    "stopping_run": "NO_READING: A_STOPPING_RUN_SELLS_EVERYTHING_AT_ONCE",
    "exits": "THE_RULE'S_SELLS_A_STOPPING_RUN'S_SELL_OF_EVERYTHING_AT_ONCE_AND_THE_OWNER'S_STOP_AND_SELL",
    "no_stop": "NO_STOP_TAKE_PROFIT_OR_TIME_EXIT_ON_THE_HOLDING: ITS_SIZE_AND_THE_LATCHES_PROTECT_IT",
    "size_chosen_by": "THE_LARGEST_OF_40_30_20_15_10_5%_A_YEAR_WHOSE_WORST_FALL_FROM_THE_HIGH_ON_DAILY_LOWS_STAYS_AT_OR_"
                      "BELOW_4%_HALF_THE_DRAWDOWN_STOP (EXECPLAN_0059_SECTION_4.2)",
    "readings": "ONE_SPOT_RULE_READINGS_ROW_PER_DAY_ACTED_ON; A_DAY_NOT_READABLE_OR_REFUSED_ONCE_A_DAY_PER_REASON",
    "sources": ["TR-01", "TR-03", "TR-10", "TR-12", "TR-35"],
}

SPOT_COST_V1: dict[str, Any] = {
    "id": COST_ID, "kind": "SPOT_COST", "version": 1, "status": "PROPOSED",
    "source": "ExecPlan 0060 section 4.3; Binance's spot fee page read on 2026-11-12 (section 7)",
    "orders": "MARKET_ONLY",
    "book": {"levels": 10, "max_age_ms": 2000, "walk": "THE_TEN_LEVELS_OF_THE_NEWEST_STORED_BOOK",
             "buy_side": "ASKS", "sell_side": "BIDS", "depth_short": "REFUSED_DEPTH_SHORT"},
    "slippage": {"adverse_bps": "1", "label": "SCENARIO_NOT_OBSERVED", "applied": "TO_THE_WALKED_AVERAGE_PRICE"},
    "fill_price_rounding": "TO_0.00000001_AGAINST_THE_ORDER",
    "quantity_rounding": "DOWN_TO_THE_STEP",
    "gross_rounding": "A_BUY'S_UP_A_SELL'S_DOWN_TO_0.00000001",
    "taker_fee_rate": "0.001", "fee_asset": "USDT", "bnb_discount": False, "promotions": "NOT_APPLIED",
    "fee_note": "BINANCE_TAKES_THE_FEE_IN_THE_ASSET_RECEIVED; THE_SAME_VALUE_IS_CHARGED_IN_USDT_SO_BTC_STAYS_IN_WHOLE_"
                "LOT_STEPS",
    "fee_source": {"url": FEE_SOURCE_URL, "read_at": "2026-11-12", "page_updated": "2026-01-06",
                   "row": "Regular user: 0.1% trading fee; 25% off when paid in BNB"},
    "fee_rounding": "UP_TO_0.00000001",
    "filters": {"quantity": "LOT_SIZE_AND_MARKET_LOT_SIZE_(A_ZERO_MARKET_STEP_OR_MINIMUM_ADDS_NO_CONSTRAINT)",
                "notional": "NOTIONAL_MIN_AND_MAX_AT_THE_FILL_PRICE", "read": "FROM_THE_INSTRUMENT_AT_THE_TRADE"},
}

SPOT_POLICY_V1: dict[str, Any] = {
    "id": POLICY_ID, "kind": "SPOT_POLICY", "version": 1, "status": "PROPOSED",
    "source": "ExecPlan 0060 section 4.3, approved by the owner on 2026-11-12",
    "replaces": "FUTURES_POLICY_V2",
    "instrument": "BTCUSDT_SPOT_PAPER", "assets": [QUOTE, BASE], "direction": "LONG_OR_CASH",
    "borrowing": False, "shorting": False, "leverage": "NONE_1X_BY_CONSTRUCTION",
    "decider": RULE_ID, "decided_by": "SYSTEM_CODE_NO_MODEL",
    "actions": list(ACTIONS),
    "size": "THE_RULE'S_TARGET; A_BUY_AT_MOST_THE_FREE_USDT_AFTER_ITS_FEE_AND_SLIPPAGE; A_SELL_AT_MOST_THE_BTC_HELD",
    "daily_loss_fraction": "0.02", "drawdown_fraction": "0.08",
    "drawdown_measure": "THE_RUN'S_OWN_HIGH_WATER_NAV",
    "daily_reference": {"timezone": "UTC", "timeliness_ms": 300000,
                        "late_rule": "MAX_OF_LAST_VALID_NAV_PRIOR_24H_AND_FIRST_POST_MIDNIGHT_NAV"},
    "latch_effect": "NO_BUY; SELLS_CONTINUE; THE_DRAWDOWN_STOP_MAKES_THE_RUN_STOPPING_WHICH_SELLS_ALL_AT_ONCE_AND_STOPS_"
                    "ONCE_ONLY_USDT_IS_HELD",
    "daily_loss_clears": "AT_THE_NEXT_UTC_DAY'S_REFERENCE",
    "runs": {"states": ["RUNNING", "PAUSED", "STOPPING", "STOPPED"], "first": "STARTS_BY_ITSELF_ONCE_FUNDED",
             "later": "THE_OWNER'S_START", "owner": ["PAUSE", "RESUME", "STOP_AND_SELL", "START"],
             "stop": "THE_DRAWDOWN_STOP_OR_THE_OWNER'S_STOP: NO_BUY; THE_BTC_HELD_IS_SOLD_AT_ONCE; STOPPED_ONCE_ONLY_"
                     "USDT_OR_UNSELLABLE_DUST_IS_HELD",
             "dust": "BTC_A_SALE_OF_ALL_OF_IT_WOULD_PUT_BELOW_THE_INSTRUMENT'S_MINIMUM_QUANTITY_OR_NOTIONAL_AT_ITS_"
                     "FILL_PRICE_CANNOT_BE_SOLD"},
    "data": {"book_max_age_ms": 2000, "bid_max_age_ms": 5000, "clock": "VERIFIED_BY_THE_FEED",
             "instrument": "USABLE_AND_CHECKED_IN_THE_LAST_HOUR",
             "missing": "A_STALE_OR_MISSING_PRICE_REFUSES_THE_TRADE_WITH_ITS_CODE_AND_INVALIDATES_THE_VALUATION"},
    "valuation": "VALUATION_BID_V1", "valuation_rule": "CASH_PLUS_BTC_AT_THE_BEST_BID_FLOORED_TO_0.00000001",
    "valuation_seconds": 60, "valuation_every_seconds_while": "BTC_THAT_CAN_BE_SOLD_IS_HELD",
    "valuation_otherwise": "HOURLY_AT_EACH_FILL_EACH_DAY'S_REFERENCE_EACH_NEW_HIGH_AND_THE_FIRST_STEP_AFTER_A_TOP_UP",
    "dust": {"btc": "PART_OF_THE_HOLDING_VALUED_AT_THE_BEST_BID",
             "other_coins": "M3_TO_M10'S_SALES_LEFT_DUST_OF_SOL_ZEC_NEAR_OR_XRP_BELOW_THEIR_MINIMUM_ORDER: KEPT_IN_THE_"
                            "HOLDINGS_WITH_ITS_POSTINGS_AND_NOT_VALUED (NO_FEED; WORTH_CENTS)"},
    "top_ups": "NAV_NEUTRAL_AT_A_VALID_VALUATION",
    "rule": RULE_ID, "cost": COST_ID,
}

DEFINITIONS = (SPOT_RULE_V1, SPOT_POLICY_V1, SPOT_COST_V1)


@dataclass(frozen=True)
class Rule:
    id: str
    sha256: str
    lookbacks: tuple[int, ...]
    tolerance_days: int
    volatility_days: int
    centre_of_mass: int
    annualization: int
    minimum_days: int
    target: Decimal
    cap: Decimal
    step: Decimal
    flat: Decimal
    buffer: Decimal
    read_after_ms: int
    retry_seconds: int

    @property
    def span_days(self) -> int:
        """How many days before the day read its closes reach back (the volatility window or the longest lookback,
        and the anchor's tolerance)."""
        return max(self.volatility_days, *self.lookbacks) + self.tolerance_days


@dataclass(frozen=True)
class Policy:
    id: str
    sha256: str
    daily_loss: Decimal
    drawdown: Decimal
    reference_timeliness_ms: int
    valuation_seconds: int
    book_max_age_ms: int
    bid_max_age_ms: int


@dataclass(frozen=True)
class Cost:
    id: str
    sha256: str
    levels: int
    book_max_age_ms: int
    slippage_bps: Decimal
    taker: Decimal


def rule(document: dict[str, Any] = SPOT_RULE_V1) -> Rule:
    return Rule(
        id=document["id"], sha256=definition_hash(document),
        lookbacks=tuple(int(days) for days in document["lookback_days"]),
        tolerance_days=int(document["anchor_tolerance_days"]), volatility_days=int(document["volatility_days"]),
        centre_of_mass=int(document["volatility_centre_of_mass_days"]),
        annualization=int(document["annualization_days"]), minimum_days=int(document["minimum_days_stored"]),
        target=dec(document["volatility_target"]), cap=dec(document["fraction_cap"]),
        step=dec(document["target_step"]), flat=dec(document["flat_band"]), buffer=dec(document["rebalance_buffer"]),
        read_after_ms=int(document["read_after_ms"]), retry_seconds=int(document["retry_seconds"]))


def policy(document: dict[str, Any] = SPOT_POLICY_V1) -> Policy:
    return Policy(
        id=document["id"], sha256=definition_hash(document), daily_loss=dec(document["daily_loss_fraction"]),
        drawdown=dec(document["drawdown_fraction"]),
        reference_timeliness_ms=int(document["daily_reference"]["timeliness_ms"]),
        valuation_seconds=int(document["valuation_seconds"]),
        book_max_age_ms=int(document["data"]["book_max_age_ms"]),
        bid_max_age_ms=int(document["data"]["bid_max_age_ms"]))


def cost(document: dict[str, Any] = SPOT_COST_V1) -> Cost:
    return Cost(
        id=document["id"], sha256=definition_hash(document), levels=int(document["book"]["levels"]),
        book_max_age_ms=int(document["book"]["max_age_ms"]),
        slippage_bps=dec(document["slippage"]["adverse_bps"]), taker=dec(document["taker_fee_rate"]))


RULE = rule()
POLICY = policy()
COST = cost()


def seed_rows(documents: tuple[dict[str, Any], ...] = DEFINITIONS) -> list[dict[str, Any]]:
    """(id, kind, version, status, canonical JSON, SHA-256) for migration 0041 and the worker's startup check."""
    return [{"id": d["id"], "kind": d["kind"], "version": d["version"], "status": d["status"],
             "canonical": canonical_json(d), "sha256": definition_hash(d)} for d in documents]


if __name__ == "__main__":
    # Prints migration 0041's SPOT_SEED_LINES; the tests check they match this code.
    for row in seed_rows():
        print(json.dumps([row["id"], row["kind"], row["version"], row["status"], row["canonical"], row["sha256"]]))
