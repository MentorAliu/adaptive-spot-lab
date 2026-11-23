"""The spot engine (ExecPlan 0060 section 4.4): one fenced step every second.

Under the execution lease and the account's fencing epoch, in one transaction, in this order:

1. the owner's requests (Pause, Resume, Stop and sell, Start), each answered once;
2. the first run, by itself, once the account is funded;
3. a stopping run's sell of everything at the book (the drawdown stop's or the owner's Stop);
4. the valuation (``VALUATION_BID_V1``: cash plus the BTC at the best bid at most 5 s old), the day's reference and
   the latches;
5. the run's state;
6. ``SPOT_RULE_V1``'s daily reading and its trade: at the engine's first step at or after 00:05 UTC, and every 15
   minutes while the day is not spent.

A latch, a paused run and an integrity hold stop buying, never selling. Every trade needs a book at most 2 s old, a
clock the feed verified and an instrument usable and checked in the last hour; nothing is guessed: a trade without them
is refused with its code and tried again. Every amount comes from ``app.spot.money`` and every posting from
``app.spot.ledger``.
"""

import json
import logging
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from app import code_identity
from app.execution import store as xstore
from app.execution.lifecycle import stable_id
from app.execution.numbers import ONE, ZERO, mul, nav, sub
from app.execution.numbers import text as dtext
from app.execution.risk import daily_reference
from app.spot import ledger, money, store
from app.spot import rule as spot_rule
from app.spot.definitions import (
    COST,
    DAY_MS,
    POLICY,
    RULE,
    RULE_BUY,
    RULE_SELL,
    STOP_SELL,
    SYMBOL,
    Cost,
    Policy,
    Rule,
)
from app.spot.reconcile import NAV_CHECKS, failed_since_clear, reconcile_locked

log = logging.getLogger("asl.spot")
MODE = "FORWARD_PAPER"
# An incident that repeats while its condition lasts (a stale book, a thin book) is recorded at most this often.
INCIDENT_EVERY = timedelta(minutes=5)
# The instrument must have been checked this recently for a trade (``SPOT_POLICY_V1``'s data rule).
INSTRUMENT_MAX_AGE_MS = 3_600_000
LIVE = ("RUNNING", "PAUSED", "STOPPING")
# The readings that spend the day; the others try again 15 minutes later.
SPENT = ("NO_CHANGE", "FILLED")


def milliseconds(at: datetime) -> int:
    return int(at.timestamp() * 1000)


def hour_floor(at: datetime) -> datetime:
    return at.astimezone(UTC).replace(minute=0, second=0, microsecond=0)


def utc_midnight(at: datetime) -> datetime:
    return at.astimezone(UTC).replace(hour=0, minute=0, second=0, microsecond=0)


class SpotEngine:
    def __init__(self, db: Engine, owner_id: UUID, epoch: int, *, rule: Rule = RULE, policy: Policy = POLICY,
                 cost: Cost = COST, identity: str | None = None):
        self.db, self.owner_id, self.epoch = db, owner_id, epoch
        self.rule, self.policy, self.cost = rule, policy, cost
        self.code_identity = identity or code_identity.current()
        self.noted: dict[str, datetime] = {}
        # The last try of a run's reading of a day, in memory: a restart tries at once, and so does a run the owner
        # starts later that day; the database says whether the day is spent.
        self.rule_tried: dict[tuple[UUID, date], datetime] = {}

    def start(self) -> None:
        """The stored definitions must be this code's (migration 0041 froze them; an update changes both)."""
        wanted = {self.rule.id: self.rule.sha256, self.policy.id: self.policy.sha256, self.cost.id: self.cost.sha256}
        with self.db.connect() as connection:
            stored = store.stored_definitions(connection, tuple(wanted))
        if stored != wanted:
            raise xstore.IntegrityFailure("spot_definitions_mismatch")

    def step(self, at: datetime | None = None) -> list[dict[str, Any]]:
        """One fenced step. Without ``at`` (the worker), the step's time is the database's clock read inside the
        transaction once the locks are held, so a book's age counts from when the step acts on it, never from before
        a wait on the account's row (the book read takes only books received by then)."""
        with self.db.begin() as connection:
            account = xstore.fence(connection, self.owner_id, self.epoch)
            if at is None:
                at = connection.execute(text("SELECT clock_timestamp()")).scalar_one()
            step = Step(self, connection, account, at)
            step.advance()
            xstore.recheck(connection, self.owner_id, self.epoch)
        # Only a committed step moves the engine's memory.
        self.noted.update(step.noted)
        if step.tried is not None:
            self.rule_tried = {step.tried[0]: step.tried[1]}
        return step.effects

    def reconcile(self, at: datetime) -> dict[str, Any]:
        """Fenced reconciliation; a pass after a fix clears the integrity latch, unless a failure since the last clear
        was one a passing run does not prove repaired (``NAV_CHECKS``)."""
        with self.db.begin() as connection:
            account = xstore.fence(connection, self.owner_id, self.epoch)
            result = reconcile_locked(connection, account)
            if result["status"] != "OK":
                xstore.incident(connection, MODE, "RECONCILIATION_FAILED", "POINT", at, None,
                                {"failed_checks": result["failed_checks"]})
            elif account["reconciliation_failed"] or account["paused"]:
                failed = failed_since_clear(connection)
                kept = sorted(set(failed) & NAV_CHECKS) or ([] if failed else ["UNRECORDED"])
                if kept:
                    result["integrity_kept"] = kept
                else:
                    result["integrity_cleared"] = self._clear_integrity(connection, account, at, failed)
            xstore.recheck(connection, self.owner_id, self.epoch)
        return result

    def _clear_integrity(self, connection: Connection, account: dict[str, Any], at: datetime,
                         failed: list[str]) -> str | None:
        connection.execute(text(
            "UPDATE account_state SET paused = false, reconciliation_failed = false WHERE id = 1"))
        detail = {"rule": "RECONCILIATION_PASSED", "reconciliation_failed": bool(account["reconciliation_failed"]),
                  "paused": bool(account["paused"]), "failed_checks": failed}
        run = store.current_run(connection)
        closed = None
        if run is not None and run["state"] in LIVE and "INTEGRITY" in run["causes"]:
            causes = [cause for cause in run["causes"] if cause != "INTEGRITY"]
            store.update_run(connection, run, causes=causes,
                             state="RUNNING" if run["state"] == "PAUSED" and not causes else run["state"])
            store.run_event(connection, run, "CAUSE_CLOSED", at, detail={"cause": "INTEGRITY", **detail})
            closed = str(run["id"])
        xstore.incident(connection, MODE, "INTEGRITY_CLEARED", "POINT", at, None, {**detail, "spot_run": closed})
        connection.execute(text(
            "INSERT INTO outbox_events (event, object_id, account_version, payload) "
            "VALUES ('INTEGRITY_CLEARED', :object, :version, CAST(:payload AS json))"),
            {"object": UUID(closed) if closed else uuid4(), "version": account["version"],
             "payload": json.dumps({**detail, "run_id": closed}, sort_keys=True)})
        log.info("integrity_cleared spot_run=%s", closed)
        return closed

    def recover(self, at: datetime) -> dict[str, Any]:
        result = self.reconcile(at)
        self.step(at)
        return result

    def record_failure(self, at: datetime, error: str, detail: str) -> None:
        with self.db.begin() as connection:
            xstore.incident(connection, MODE, "STEP_FAILED", "POINT", at, SYMBOL,
                            {"engine": "SPOT", "error": error, "detail": detail[:200], "lease_epoch": self.epoch})


class Step:
    """One step's reads, decisions and writes, inside the fenced transaction."""

    def __init__(self, engine: SpotEngine, connection: Connection, account: dict[str, Any], at: datetime):
        self.e, self.c, self.account, self.at = engine, connection, account, at.astimezone(UTC)
        self.rule, self.policy, self.cost = engine.rule, engine.policy, engine.cost
        self.effects: list[dict[str, Any]] = []
        self.noted: dict[str, datetime] = {}
        self.tried: tuple[tuple[UUID, date], datetime] | None = None
        self.run = store.current_run(connection)
        self.held = store.holding(connection)
        self.book = store.book(connection, self.at)
        self.feed = store.feed(connection, self.at)
        self.filled = False
        self.valuations = 0
        self.equity: Decimal | None = None
        self.nav_value: Decimal | None = None

    def advance(self) -> None:
        self.requests()
        self.auto_start()
        self.stopping_sell()
        self.value()
        self.run_state()
        self.daily_rule()

    # ---- helpers ---------------------------------------------------------------------------------------------

    def effect(self, kind: str, **fields: Any) -> None:
        self.effects.append({"kind": kind, **fields})

    def note(self, code: str, detail: dict[str, Any]) -> None:
        """An incident, at most once per ``INCIDENT_EVERY`` while its condition lasts."""
        last = self.e.noted.get(code)
        if last is not None and self.at - last < INCIDENT_EVERY:
            return
        xstore.incident(self.c, MODE, code, "POINT", self.at, SYMBOL,
                        {**detail, "spot_run": str(self.run["id"]) if self.run else None})
        self.noted[code] = self.at
        self.effect("INCIDENT", code=code)

    @property
    def live(self) -> bool:
        return self.run is not None and self.run["state"] in LIVE

    @property
    def quantity(self) -> Decimal:
        return self.held["quantity"]

    def integrity(self) -> bool:
        return bool(self.account["reconciliation_failed"] or self.account["paused"])

    def funded_account(self) -> bool:
        return bool(self.account["initialized"]) and self.account["units"] > 0 and self.account["cash"] > 0

    def fresh(self, limit_ms: int) -> dict[str, Any] | None:
        if self.book is None or not -limit_ms <= self.book["age_ms"] <= limit_ms:
            return None
        return self.book

    def fresh_book(self) -> dict[str, Any] | None:
        """The book a trade walks: at most ``SPOT_COST_V1``'s 2 s old."""
        return self.fresh(self.cost.book_max_age_ms)

    def fresh_bid(self) -> Decimal | None:
        """The best bid a valuation uses: at most ``SPOT_POLICY_V1``'s 5 s old."""
        book = self.fresh(self.policy.bid_max_age_ms)
        return book["bid"] if book else None

    def instrument(self) -> dict[str, Any] | None:
        """The instrument, when usable and checked in the last hour."""
        instrument, age = self.feed["instrument"], self.feed["instrument_age_ms"]
        if instrument is None or not instrument["usable"] or age is None or age > INSTRUMENT_MAX_AGE_MS:
            return None
        return instrument

    def trade_codes(self) -> list[str]:
        """What a trade lacks: a fresh book, a verified clock, a usable instrument."""
        codes = []
        if self.fresh_book() is None:
            codes.append("BOOK_STALE")
        if not self.feed["clock_verified"]:
            codes.append("CLOCK_UNVERIFIED")
        if self.instrument() is None:
            codes.append("INSTRUMENT_UNAVAILABLE")
        return codes

    def sellable(self) -> bool:
        """BTC held that can be sold (``SPOT_RULE_V1``'s dust rule, ``money.sellable``): a sale of all of it on the
        book the valuation reads (at most 5 s old) passes the sale's own size and notional checks, so a stopping run
        never waits on a sale its own checks refuse. Without a usable instrument any BTC held counts as sellable, so
        nothing stops or values as dust on unknown filters; without that book only the size is checked."""
        quantity = self.quantity
        if quantity <= 0:
            return False
        instrument = self.instrument()
        if instrument is None:
            return True
        book = self.fresh(self.policy.bid_max_age_ms)
        return money.sellable(quantity, book["bids"] if book else [], store.filters(instrument), self.cost)

    def compute(self) -> tuple[Decimal | None, str | None]:
        """The account's equity now (``VALUATION_BID_V1``), or None with the reason."""
        if not self.account["valuation_valid"]:
            return None, "VALUATION_OVERRIDE_INVALID"
        if self.quantity <= 0:
            return self.account["cash"], None
        bid = self.fresh_bid()
        if bid is None:
            return None, "BID_STALE"
        return money.equity(self.account["cash"], self.quantity, bid), None

    def open_cause(self, cause: str, *, actor: str = "SYSTEM", request_id: UUID | None = None,
                   detail: dict[str, Any] | None = None) -> None:
        run = self.run
        store.update_run(self.c, run, causes=sorted({*run["causes"], cause}),
                         state="PAUSED" if run["state"] == "RUNNING" else run["state"])
        store.run_event(self.c, run, "CAUSE_OPENED", self.at, actor=actor, request_id=request_id,
                        detail={"cause": cause, **(detail or {})})
        self.effect("RUN_CAUSE_OPENED", cause=cause, state=run["state"])

    def close_cause(self, cause: str, *, actor: str = "SYSTEM", request_id: UUID | None = None,
                    detail: dict[str, Any] | None = None) -> None:
        run = self.run
        causes = [value for value in run["causes"] if value != cause]
        store.update_run(self.c, run, causes=causes,
                         state="RUNNING" if run["state"] == "PAUSED" and not causes else run["state"])
        store.run_event(self.c, run, "CAUSE_CLOSED", self.at, actor=actor, request_id=request_id,
                        detail={"cause": cause, **(detail or {})})
        self.effect("RUN_CAUSE_CLOSED", cause=cause, state=run["state"])

    def persist(self, purpose: str, equity: Decimal | None, reason: str | None) -> UUID:
        """Store a valuation at ``equity`` (None: invalid, with ``reason``); a valid one moves the account's NAV and
        raises the account's and the live run's high-water NAV."""
        nav_value = nav(equity, self.account["units"]) if equity is not None else None
        self.valuations += 1
        identity = stable_id("spot-valuation", self.at.isoformat(), purpose, self.valuations)
        bid = self.fresh(self.policy.bid_max_age_ms)
        store.insert_valuation(self.c, identity=identity, run_id=self.run["id"] if self.run else None, at=self.at,
                               purpose=purpose, account=self.account, quantity=self.quantity, bid=bid,
                               equity=equity, nav=nav_value, quality="VALID" if equity is not None else "INVALID",
                               reason=reason)
        if nav_value is not None:
            store.update_nav(self.c, self.account, nav_value)
            if self.live and nav_value > self.run["high_water_nav"]:
                store.update_run(self.c, self.run, high_water_nav=nav_value)
        self.effect("VALUATION", purpose=purpose, quality="VALID" if equity is not None else "INVALID",
                    nav=dtext(nav_value))
        return identity

    def fill(self, plan: money.Fill, reason: str, book: dict[str, Any], instrument: dict[str, Any],
             key: Any) -> UUID:
        identity = stable_id("spot-fill", self.run["id"], reason, key)
        ledger.post_fill(self.c, self.account, self.held, plan, identity=identity, run_id=self.run["id"],
                         reason=reason, book=book, instrument_id=instrument["id"], fee_rate=self.cost.taker,
                         slippage_bps=self.cost.slippage_bps, at=self.at)
        self.filled = True
        self.effect("FILL", reason=reason, side=plan.side, fill=str(identity), price=dtext(plan.price),
                    quantity=dtext(plan.quantity), fee=dtext(plan.fee))
        return identity

    # ---- 1 and 2: the owner's requests and the first run ------------------------------------------------------

    def requests(self) -> None:
        for request in store.pending_requests(self.c):
            status, reasons = self.apply_request(request)
            store.answer_request(self.c, request, status, reasons, self.at)
            self.effect("OWNER_REQUEST", request=str(request["id"]), request_kind=request["kind"], status=status,
                        reasons=reasons)

    def apply_request(self, request: dict[str, Any]) -> tuple[str, list[str]]:
        kind = request["kind"]
        if kind == "START":
            return self.start_run("OWNER", request["id"])
        run = self.run
        if not self.live:
            return "REJECTED", ["RUN_NOT_LIVE"]
        if run["id"] != request["run_id"]:
            return "REJECTED", ["RUN_CHANGED"]
        if kind == "PAUSE":
            if run["state"] == "STOPPING":
                return "REJECTED", ["RUN_STOPPING"]
            if "OWNER" in run["causes"]:
                return "REJECTED", ["ALREADY_PAUSED"]
            self.open_cause("OWNER", actor="OWNER", request_id=request["id"])
            return "APPLIED", []
        if kind == "RESUME":
            if "OWNER" not in run["causes"]:
                return "REJECTED", ["NOT_PAUSED_BY_OWNER"]
            self.close_cause("OWNER", actor="OWNER", request_id=request["id"])
            return "APPLIED", []
        # STOP: no buy any more; the BTC held is sold at once, and the run stops once only USDT or dust is held.
        if run["state"] != "STOPPING":
            store.update_run(self.c, run, state="STOPPING", stop_reason=run["stop_reason"] or "OWNER")
        store.run_event(self.c, run, "STOP_REQUESTED", self.at, actor="OWNER", request_id=request["id"],
                        detail={"sell": True})
        self.effect("RUN_STOPPING", reason="OWNER")
        return "APPLIED", []

    def auto_start(self) -> None:
        """The first run starts by itself once the account is funded; any later one needs the owner."""
        if self.run is None and self.funded_account():
            self.start_run("SYSTEM", None)

    def start_run(self, by: str, request_id: UUID | None) -> tuple[str, list[str]]:
        if self.live:
            return "REJECTED", ["RUN_LIVE"]
        if not self.funded_account():
            return "REJECTED", ["NOT_FUNDED"]
        equity, why = self.compute()
        if equity is None or equity <= 0:
            return "REJECTED", [why or "VALUATION_UNAVAILABLE"]
        nav_value = nav(equity, self.account["units"])
        causes = ["INTEGRITY"] if self.integrity() else []
        identity = stable_id("spot-run", request_id or "first")
        self.run = store.insert_run(
            self.c, identity=identity, rule=(self.rule.id, self.rule.sha256),
            policy=(self.policy.id, self.policy.sha256), cost=(self.cost.id, self.cost.sha256),
            code_identity=self.e.code_identity, started_by=by, request_id=request_id, at=self.at, equity=equity,
            nav=nav_value, causes=causes)
        # The app records the rule, policy and costs in force (the installed code's) as SYSTEM, never the owner: the
        # owner's Start is named only as who asked, with the request.
        store.run_event(self.c, self.run, "STARTED", self.at, request_id=request_id,
                        detail={"started_by": by, "rule": self.rule.id, "rule_sha256": self.rule.sha256,
                                "policy": self.policy.id, "policy_sha256": self.policy.sha256,
                                "cost": self.cost.id, "cost_sha256": self.cost.sha256,
                                "code_identity": self.e.code_identity, "equity": dtext(equity),
                                "nav": dtext(nav_value), "btc": dtext(self.quantity), "causes": causes})
        self.persist("START", equity, None)
        self.effect("RUN_STARTED", by=by, run=str(identity))
        return "APPLIED", []

    # ---- 3: a stopping run sells everything ----------------------------------------------------------------------

    def stopping_sell(self) -> None:
        """A stopping run (the drawdown stop or the owner's Stop) sells all the BTC it can at once, at the book; what
        it cannot sell waits for the book, the clock or the instrument, and is retried every step."""
        if not self.live or self.run["state"] != "STOPPING" or not self.sellable():
            return
        codes = self.trade_codes()
        if codes:
            self.note("STOP_SELL_WAITS", {"codes": codes, "btc": dtext(self.quantity)})
            return
        book, instrument = self.fresh_book(), self.instrument()
        plan = money.plan_sell(wanted=self.quantity, held=self.quantity, bids=book["bids"],
                               filters=store.filters(instrument), cost=self.cost)
        if isinstance(plan, money.Refusal):
            self.note("STOP_SELL_REFUSED", {"codes": plan.codes, "detail": plan.detail, "btc": dtext(self.quantity)})
            return
        self.fill(plan, STOP_SELL, book, instrument, self.at.isoformat())

    # ---- 4: valuation, the day's reference and the latches ---------------------------------------------------

    def value(self) -> None:
        equity, reason = self.compute()
        self.equity = equity
        account = self.account
        if not account["initialized"] or account["units"] <= 0:
            return
        nav_value = nav(equity, account["units"]) if equity is not None else None
        self.nav_value = nav_value
        holding = self.sellable()
        day = utc_midnight(self.at)
        reference = store.reference(self.c, day.date())
        need_reference = reference is None and nav_value is not None and (self.live or self.quantity > 0)
        latches: list[str] = []
        if nav_value is not None and self.live:
            open_causes = {latch["cause"] for latch in store.unresolved_latches(self.c, self.run["id"])}
            if (reference is not None and "DAILY_LOSS" not in open_causes
                    and nav_value <= mul(reference["nav"], sub(ONE, self.policy.daily_loss))):
                latches.append("DAILY_LOSS")
            if ("DRAWDOWN" not in open_causes
                    and nav_value <= mul(self.run["high_water_nav"], sub(ONE, self.policy.drawdown))):
                latches.append("DRAWDOWN")
        high = account["high_water_nav"]
        new_high = nav_value is not None and (high is None or nav_value > high
                                              or (self.live and nav_value > self.run["high_water_nav"]))
        last = store.last_valuation_at(self.c)
        periodic = holding and (last is None or self.at - last >= timedelta(seconds=self.policy.valuation_seconds))
        # A top-up since the newest valuation (the API posts it; a fill is valued in its own step): valued at once, so
        # the account's equity never shows the contribution as a loss until the next periodic valuation.
        changed = store.last_valuation_version(self.c) != account["version"]
        purpose = ("LATCH" if latches else "DAILY_REFERENCE" if need_reference else "FILL" if self.filled
                   else "ACCOUNT_CHANGE" if changed else "HIGH_WATER" if new_high else "PERIODIC" if periodic
                   else "HOURLY" if not store.hourly_valued(self.c, hour_floor(self.at)) else None)
        if purpose is None:
            return
        identity = self.persist(purpose, equity, reason)
        if nav_value is None:
            return
        if need_reference:
            prior = store.prior_navs(self.c, day - timedelta(hours=24), day)
            choice = daily_reference(nav_value, self.at, prior, self.policy)
            store.insert_reference(self.c, day=day.date(), valuation_id=identity, nav=choice.nav,
                                   quality=choice.quality, lateness_ms=choice.lateness_ms,
                                   basis={"first_nav": dtext(nav_value), "first_at": self.at.isoformat(),
                                          "prior_count": len(prior)})
            self.effect("DAILY_REFERENCE", nav=dtext(choice.nav), quality=choice.quality)
            reference = {"nav": choice.nav}
            self.clear_daily_loss(day, identity, nav_value)
        for cause in latches:
            trigger = {"nav": dtext(nav_value), "reference": dtext(reference["nav"]) if reference else None,
                       "high_water": dtext(self.run["high_water_nav"]),
                       "threshold": dtext(self.policy.daily_loss if cause == "DAILY_LOSS" else self.policy.drawdown)}
            latch = store.insert_latch(self.c, run_id=self.run["id"], cause=cause, at=self.at,
                                       valuation_id=identity, trigger=trigger)
            xstore.incident(self.c, MODE, f"RISK_LATCH_{cause}", "POINT", self.at, SYMBOL,
                            {**trigger, "spot_run": str(self.run["id"])})
            self.open_cause(cause, detail={"latch_id": str(latch), **trigger})
            if cause == "DRAWDOWN" and self.run["state"] != "STOPPING":
                # The drawdown stop ends the run: no buy, and the BTC held is sold at once (the next step's sell).
                store.update_run(self.c, self.run, state="STOPPING", stop_reason="DRAWDOWN")
                self.effect("RUN_STOPPING", reason="DRAWDOWN")

    def clear_daily_loss(self, day: datetime, valuation_id: UUID, nav_value: Decimal) -> None:
        """A daily-loss latch of an earlier UTC day clears when the new day's reference is taken."""
        if not self.live:
            return
        latches = [latch for latch in store.unresolved_latches(self.c, self.run["id"])
                   if latch["cause"] == "DAILY_LOSS" and latch["latched_at"] < day]
        if not latches:
            return
        resolution = {"rule": "NEXT_UTC_DAY", "utc_date": day.date().isoformat(), "nav": dtext(nav_value),
                      "valuation_id": str(valuation_id)}
        for latch in latches:
            store.resolve_latch(self.c, latch["id"], self.at, resolution)
        if "DAILY_LOSS" in self.run["causes"]:
            self.close_cause("DAILY_LOSS", detail=resolution)

    # ---- 5: the run's state ------------------------------------------------------------------------------------

    def run_state(self) -> None:
        if not self.live:
            return
        run = self.run
        if self.integrity() and "INTEGRITY" not in run["causes"]:
            self.open_cause("INTEGRITY", detail={"reconciliation_failed": bool(self.account["reconciliation_failed"]),
                                                 "paused": bool(self.account["paused"])})
        if run["state"] == "STOPPING" and not self.sellable():
            reason = run["stop_reason"] or "OWNER"
            store.update_run(self.c, run, state="STOPPED", stopped_at=self.at, stop_reason=reason)
            for latch in store.unresolved_latches(self.c, run["id"]):
                store.resolve_latch(self.c, latch["id"], self.at, {"rule": "RUN_STOPPED", "stop_reason": reason})
            store.run_event(self.c, run, "STOPPED", self.at,
                            detail={"stop_reason": reason, "dust": dtext(self.quantity)})
            if self.account["initialized"] and self.account["units"] > 0:
                equity, why = self.compute()
                self.persist("STOP", equity, why)
            self.effect("RUN_STOPPED", reason=reason)

    # ---- 6: the rule's daily reading and its trade -------------------------------------------------------------

    def daily_rule(self) -> None:
        """At the first step at or after 00:05 UTC, then every 15 minutes until the day is spent: the reading of the
        last complete day and its trade. A fill or a reading that changes nothing spends the day; a day not readable
        yet and a refusal try again. A stopping run reads nothing (it sells everything)."""
        if not self.live or self.run["state"] == "STOPPING":
            return
        day = utc_midnight(self.at)
        today, day_ms = day.date(), milliseconds(day)
        if milliseconds(self.at) < day_ms + self.rule.read_after_ms:
            return
        run = self.run
        last = self.e.rule_tried.get((run["id"], today))
        if last is not None and (self.at - last).total_seconds() < self.rule.retry_seconds:
            return
        self.tried = ((run["id"], today), self.at)
        readings = store.rule_readings(self.c, run["id"], today)
        if any(row["spent"] for row in readings):
            return
        read_day = day_ms - DAY_MS
        closes = store.daily_closes(self.c, read_day - self.rule.span_days * DAY_MS, read_day)
        found = spot_rule.target_of(closes, read_day, self.rule)
        common = {"id": stable_id("spot-rule-reading", run["id"], today.isoformat(), self.at.isoformat()),
                  "run_id": run["id"], "utc_date": today, "day_open_ms": read_day, "readings": readings}
        if found.result == spot_rule.WARMUP:
            self.reading(common, replace(found, action=spot_rule.NO_CHANGE), "NOT_READABLE", [])
            return
        quantity, equity, bid = self.quantity, self.equity, self.fresh_bid()
        if equity is None or equity <= 0 or (quantity > 0 and bid is None):
            # The account cannot be valued (BTC held without a fresh best bid, or the valuation override): no action
            # is computed, and the day is tried again.
            self.reading(common, found, "REFUSED",
                         ["BID_STALE" if quantity > 0 and bid is None else "VALUATION_UNAVAILABLE"], held_known=False)
            return
        held = spot_rule.held_fraction(quantity, bid, equity)
        found = spot_rule.act(found, held, self.sellable(), self.rule)
        if found.action == spot_rule.NO_CHANGE:
            self.reading(common, found, "NO_CHANGE", [])
            return
        buying = found.action == spot_rule.BUY
        codes = self.trade_codes()
        if buying and run["state"] != "RUNNING":
            codes.append("RUN_NOT_RUNNING")
        if buying and self.integrity():
            codes.append("INTEGRITY")
        if codes:
            self.reading(common, found, "REFUSED", codes)
            return
        book, instrument = self.fresh_book(), self.instrument()
        rules = store.filters(instrument)
        if found.action == spot_rule.SELL_ALL:
            wanted = quantity
        else:
            wanted = money.difference_quantity(found.target, held, equity, bid)
        if buying:
            plan = money.plan_buy(wanted=wanted, cash=self.account["cash"], asks=book["asks"], filters=rules,
                                  cost=self.cost)
        else:
            plan = money.plan_sell(wanted=wanted, held=quantity, bids=book["bids"], filters=rules, cost=self.cost)
        detail = {"equity": dtext(equity), "bid": dtext(bid), "wanted": dtext(wanted),
                  "book_second": book["second_at"].isoformat(), "instrument_id": instrument["id"]}
        if isinstance(plan, money.Refusal):
            self.reading(common, found, "REFUSED", plan.codes, {**detail, "refusal": plan.detail})
            return
        fill_id = self.fill(plan, RULE_BUY if buying else RULE_SELL, book, instrument, common["id"])
        self.reading(common, found, "FILLED", [], detail, fill_id=fill_id)
        if self.account["initialized"] and self.account["units"] > 0:
            # The fill's own valuation (the valuation phase ran before it), so the account shows it at once.
            equity_after, why = self.compute()
            self.persist("FILL", equity_after, why)

    def reading(self, common: dict[str, Any], found: spot_rule.Reading, outcome: str, codes: list[str],
                detail: dict[str, Any] | None = None, *, fill_id: UUID | None = None, held_known: bool = True) -> None:
        """Store the day's reading; one that tries again later is stored once a day per outcome, reason and codes."""
        if outcome in ("NOT_READABLE", "REFUSED") and any(
                row["outcome"] == outcome and list(row["codes"]) == codes and row["reason"] == found.reason
                for row in common["readings"]):
            return
        readable = found.result != spot_rule.WARMUP
        features = found.features(self.rule)
        if not (readable and held_known):
            # As the row's own columns: nothing was held against a reading that could not be made or valued.
            features = {**features, "held": None, "action": None}
        store.insert_reading(self.c, {
            "id": common["id"], "run_id": common["run_id"], "utc_date": common["utc_date"],
            "day_open_ms": common["day_open_ms"], "at": self.at, "rule_id": self.rule.id,
            "rule_sha256": self.rule.sha256, "result": found.result, "reason": found.reason, "close": found.close,
            "signal": found.signal, "volatility": found.volatility, "target": found.target,
            "held": found.held if readable and held_known else None,
            "action": found.action if readable and held_known else None, "outcome": outcome, "codes": codes,
            "spent": outcome in SPENT, "fill_id": fill_id, "features": features, "detail": detail or {}})
        self.effect("RULE_READING", result=found.result, action=found.action if held_known else None,
                    outcome=outcome, codes=codes)


__all__ = ["INCIDENT_EVERY", "LIVE", "MODE", "SpotEngine", "Step", "ZERO"]
