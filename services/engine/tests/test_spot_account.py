"""The account and its funding on the spot app (M1's account tests and ExecPlan 0042's funding at the API's start,
kept by ExecPlan 0060 on the spot harness): an isolated ``asl_m1_`` database at migration 0041, its tables emptied
before and after each test (``spot_support.reset``). Every amount is a virtual contribution; every market value is
SYNTHETIC."""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from spot_support import T0
from spot_support import spot as spot  # noqa: F401  (pytest fixture)
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import TimeoutError as PoolTimeoutError
from test_spot_api import client as client  # noqa: F401  (pytest fixture)

from app import accounting, main
from app.db import get_engine
from app.execution.numbers import nav

SHA = "a" * 64


def _confirm(kind: str, amount: str, key: str | None = None):
    draft = accounting.draft(kind, amount)
    return accounting.confirm(kind, draft["amount"], draft["version"], draft["draft_hash"], key or str(uuid4()),
                              str(uuid4()))


def _initialize():
    """The app's own initial contribution (ExecPlan 0042), as the API posts it at its start."""
    assert accounting.fund_by_itself()["status"] == "POSTED"
    [initial] = [entry for entry in accounting.workspace_snapshot()["funding"] if entry["kind"] == "INITIALIZE"]
    return initial


# ---- M1: the account, its top-ups and their limits ------------------------------------------------------------

def test_initialization_topup_and_cashflow_neutral_nav(spot):
    initial = _initialize()
    assert initial["status"] == "POSTED"
    assert initial["issued_units"] == "100.000000000000000000000000000000000000"
    assert accounting.account_snapshot()["cash"] == "10000.00000000"
    assert accounting.fund_by_itself() == {"status": "FUNDED"}
    for kind in ("INITIALIZE", "BONUS"):  # the owner drafts and confirms top-ups only
        with pytest.raises(accounting.AccountingError, match="INVALID_FUNDING_KIND"):
            accounting.draft(kind, "10000")
        with pytest.raises(accounting.AccountingError, match="INVALID_FUNDING_KIND"):
            accounting.confirm(kind, "10000", 1, "0" * 64, str(uuid4()), str(uuid4()))
    draft = accounting.draft("TOPUP", "2200.00")
    key = str(uuid4())
    result = accounting.confirm("TOPUP", draft["amount"], draft["version"], draft["draft_hash"], key, str(uuid4()))
    assert result["status"] == "POSTED"
    assert result["issued_units"] == "22.000000000000000000000000000000000000"
    assert accounting.confirm("TOPUP", draft["amount"], draft["version"], draft["draft_hash"], key,
                              str(uuid4())) == result
    with pytest.raises(accounting.AccountingError, match="IDEMPOTENCY_CONFLICT"):
        accounting.confirm("TOPUP", "1", draft["version"], accounting._hash(
            {"account_id": 1, "amount": "1.00000000", "denomination": "USDT (virtual)", "kind": "TOPUP",
             "version": draft["version"]}), key, str(uuid4()))
    snapshot = accounting.account_snapshot()
    workspace = accounting.workspace_snapshot()
    assert workspace["account"] == snapshot
    assert [entry["status"] for entry in workspace["funding"]] == ["POSTED", "POSTED"]
    assert snapshot["cash"] == "12200.00000000"
    assert snapshot["contributions"] == "12200.00000000"
    assert snapshot["nav"] == snapshot["high_water_nav"] == "100.000000000000000000000000000000000000"
    assert Decimal(snapshot["pnl"]) == 0
    # A cash-only account values at its cash; BTC is listed, held or not, and the other coins only with a balance.
    assert (snapshot["valuation_source"], snapshot["equity"]) == ("CASH_ONLY", "12200.00000000")
    assert [(holding["asset"], holding["valued"]) for holding in snapshot["holdings"]] == [("BTC", True)]
    assert accounting.reconcile()["status"] == "OK"


def test_large_cumulative_contributions_remain_exact_and_reconcile(spot):
    _initialize()
    amount = "99999999999999999999.99999999"
    posted = _confirm("TOPUP", amount)
    assert posted["status"] == "POSTED"
    snapshot = accounting.account_snapshot()
    assert snapshot["cash"] == "100000000000000009999.99999999"
    assert snapshot["contributions"] == snapshot["cash"]
    assert Decimal(snapshot["pnl"]) == 0
    assert accounting.reconcile()["status"] == "OK"


def test_workspace_reads_remain_at_one_version_during_a_concurrent_post(spot):
    _initialize()
    with get_engine().connect().execution_options(isolation_level="REPEATABLE READ") as reader:
        prior_version = reader.execute(text("SELECT version FROM account_state WHERE id=1")).scalar_one()
        assert prior_version == 1
        assert _confirm("TOPUP", "25")["status"] == "POSTED"
        assert reader.execute(text("SELECT version FROM account_state WHERE id=1")).scalar_one() == prior_version
        assert reader.execute(text("SELECT count(*) FROM funding_requests")).scalar_one() == 1
    workspace = accounting.workspace_snapshot()
    assert workspace["account"]["version"] == 2
    assert len(workspace["funding"]) == 2


def test_concurrent_starts_fund_the_account_once(spot):
    """Two API processes starting together: the account's lock lets one post and the others find it funded."""
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: accounting.fund_by_itself()["status"], range(4)))
    assert sorted(results) == ["FUNDED", "FUNDED", "FUNDED", "POSTED"]
    with get_engine().connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM funding_requests")).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM journal_transactions")).scalar_one() == 1
        assert connection.execute(text(
            "SELECT sum(amount) FROM journal_postings WHERE asset='USDT'")).scalar_one() == 0
    assert accounting.account_snapshot()["cash"] == "10000.00000000"
    assert accounting.reconcile()["status"] == "OK"


def test_pending_retry_cancel_and_reconciliation(spot):
    _initialize()
    spot.raw("UPDATE account_state SET valuation_valid=false WHERE id=1")
    draft = accounting.draft("TOPUP", "50")
    request = accounting.confirm("TOPUP", draft["amount"], draft["version"], draft["draft_hash"], str(uuid4()),
                                 str(uuid4()))
    assert request["status"] == "PENDING_VALUATION"
    assert accounting.account_snapshot()["available"] == "10000.00000000"
    with pytest.raises(accounting.AccountingError, match="VALUATION_UNAVAILABLE"):
        accounting.resolve_pending(UUID(request["id"]), "RETRY", str(uuid4()))
    canceled = accounting.resolve_pending(UUID(request["id"]), "CANCEL", str(uuid4()))
    assert canceled["status"] == "CANCELED"
    with pytest.raises(accounting.AccountingError, match="REQUEST_NOT_PENDING"):
        accounting.resolve_pending(UUID(request["id"]), "RETRY", str(uuid4()))
    second = _confirm("TOPUP", "75")
    spot.raw("UPDATE account_state SET valuation_valid=true WHERE id=1")
    posted = accounting.resolve_pending(UUID(second["id"]), "RETRY", str(uuid4()))
    assert posted["status"] == "POSTED"
    assert accounting.account_snapshot()["cash"] == "10075.00000000"
    assert accounting.reconcile()["status"] == "OK"


def test_pending_retry_cancel_race_posts_at_most_once(spot):
    _initialize()
    spot.raw("UPDATE account_state SET valuation_valid=false WHERE id=1")
    pending = _confirm("TOPUP", "125")
    spot.raw("UPDATE account_state SET valuation_valid=true WHERE id=1")

    def resolve(action):
        try:
            return accounting.resolve_pending(UUID(pending["id"]), action, str(uuid4()))["status"]
        except accounting.AccountingError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(resolve, ["RETRY", "CANCEL"]))
    assert results in (["POSTED", "REQUEST_NOT_PENDING"], ["REQUEST_NOT_PENDING", "CANCELED"])
    snapshot = accounting.account_snapshot()
    assert snapshot["cash"] in ("10000.00000000", "10125.00000000")
    assert accounting.reconcile()["status"] == "OK"
    with get_engine().connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM journal_transactions")).scalar_one() in (1, 2)


def test_distinct_topups_from_same_draft_do_not_both_post(spot):
    _initialize()
    draft = accounting.draft("TOPUP", "25")

    def submit(_):
        try:
            return accounting.confirm("TOPUP", draft["amount"], draft["version"], draft["draft_hash"], str(uuid4()),
                                      str(uuid4()))["status"]
        except accounting.AccountingError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(submit, range(2)))
    assert sorted(results) == ["ACCOUNT_VERSION_CONFLICT", "POSTED"]
    assert accounting.account_snapshot()["cash"] == "10025.00000000"
    assert accounting.reconcile()["status"] == "OK"


def test_api_lock_wait_is_bounded_and_failed_confirmation_can_retry(spot):
    _initialize()
    draft = accounting.draft("TOPUP", "25")
    key = str(uuid4())
    with spot.admin.connect() as blocker:
        with blocker.begin():
            blocker.execute(text("SELECT id FROM account_state WHERE id=1 FOR UPDATE"))
            started = time.monotonic()
            with ThreadPoolExecutor(max_workers=1) as pool:
                attempt = pool.submit(accounting.confirm, "TOPUP", draft["amount"], draft["version"],
                                      draft["draft_hash"], key, str(uuid4()))
                with pytest.raises(DBAPIError) as failure:
                    attempt.result(timeout=4)
            assert getattr(failure.value.orig, "sqlstate", None) == "55P03"
            assert time.monotonic() - started < 3
        # Releasing the competing lock cannot retrospectively commit the failed attempt.
    assert accounting.funding_by_key(key) is None
    assert accounting.confirm("TOPUP", draft["amount"], draft["version"], draft["draft_hash"], key,
                              str(uuid4()))["status"] == "POSTED"
    assert accounting.account_snapshot()["cash"] == "10025.00000000"
    assert accounting.reconcile()["status"] == "OK"


def test_api_pool_wait_is_bounded_and_connections_recover(spot):
    engine = get_engine()
    with ExitStack() as held:
        for _ in range(10):
            held.enter_context(engine.connect())
        started = time.monotonic()
        with pytest.raises(PoolTimeoutError):
            with engine.connect():
                pass
        assert time.monotonic() - started < 3.5
    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1


def test_topup_preserves_high_water_and_cannot_clear_pause(spot):
    _initialize()
    spot.raw("UPDATE account_state SET high_water_nav=105, paused=true WHERE id=1")
    with pytest.raises(accounting.AccountingError, match="POLICY_PAUSED"):
        _confirm("TOPUP", "200")
    assert accounting.account_snapshot()["paused"]
    assert accounting.account_snapshot()["cash"] == "10000.00000000"
    spot.raw("UPDATE account_state SET paused=false WHERE id=1")
    assert _confirm("TOPUP", "200")["status"] == "POSTED"
    snapshot = accounting.account_snapshot()
    assert snapshot["high_water_nav"] == "105.000000000000000000000000000000000000"
    assert Decimal(snapshot["pnl"]) == 0


@pytest.mark.parametrize("statement", [
    "INSERT INTO spot_fills (id) VALUES (gen_random_uuid())",
    "UPDATE account_holdings SET quantity = quantity + 1 WHERE asset = 'BTC'",
    "UPDATE account_state SET fencing_epoch = fencing_epoch + 1 WHERE id = 1",
    "UPDATE spot_runs SET state = 'STOPPED'",
    "UPDATE spot_owner_requests SET status = 'APPLIED'",
    "INSERT INTO spot_valuations (id) VALUES (gen_random_uuid())",
    "UPDATE execution_lease SET epoch = epoch + 1 WHERE id = 1",
], ids=["fill", "holding", "fencing", "run", "answer", "valuation", "lease"])
def test_the_api_identity_cannot_trade_answer_or_take_the_execution_authority(spot, statement):
    """Only the fenced execution worker posts a trade, values the account, answers a request or holds the lease
    (ExecPlan 0060 section 4.4; M3 replaced M1's unrouted reservation stubs)."""
    _initialize()
    with pytest.raises(DBAPIError, match="permission denied"):
        with get_engine().begin() as connection:
            connection.execute(text(statement))
    assert not hasattr(accounting, "reserve_quote") and not hasattr(accounting, "release_quote")
    assert accounting.reconcile()["status"] == "OK"


def test_unbalanced_journal_rolls_back_and_projection_mismatch_latches(spot):
    _initialize()
    with pytest.raises(DBAPIError):
        with get_engine().begin() as connection:
            request_id = uuid4()
            tx_id = uuid4()
            connection.execute(text(
                "INSERT INTO funding_requests(id,kind,amount,idempotency_key,request_hash,draft_hash,expected_version,"
                "status) VALUES (:id,'TOPUP',1,:key,:hash,:hash,1,'PENDING_VALUATION')"),
                {"id": request_id, "key": str(uuid4()), "hash": "a" * 64})
            connection.execute(text(
                "INSERT INTO journal_transactions(id,funding_request_id,account_version) VALUES (:id,:request,2)"),
                {"id": tx_id, "request": request_id})
            connection.execute(text(
                "INSERT INTO journal_postings(tx_id,asset,book_account,amount) VALUES (:tx,'USDT','OWNER_CASH',1)"),
                {"tx": tx_id})
    with get_engine().connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM journal_transactions")).scalar_one() == 1
    spot.raw("UPDATE account_state SET cash=cash+1 WHERE id=1")
    assert accounting.reconcile()["status"] == "DISCREPANCY"
    assert accounting.account_snapshot()["reconciliation_failed"]
    with pytest.raises(accounting.AccountingError, match="RECONCILIATION_REQUIRED"):
        _confirm("TOPUP", "1")


def test_private_api_requires_the_service_key(spot, caplog):
    """ExecPlan 0042: the service key is the only identity; the owner's sign-in and initialization are gone."""
    key = Path("/run/secrets/api_internal_key").read_text().strip()
    client = TestClient(main.app, base_url="http://api:8000")
    with caplog.at_level(logging.INFO, logger="asl.requests"):
        denied = client.get("/v1/account", headers={"X-Request-ID": "m1-access-check"})
    assert denied.status_code == 401
    assert denied.headers["X-Correlation-ID"] == "m1-access-check"
    assert '"correlation_id":"m1-access-check"' in caplog.text
    assert key not in caplog.text
    assert client.post("/v1/account/topups/draft", content=b"x" * 8193).status_code == 413
    assert client.get("/v1/account", headers={"X-Internal-Key": "x" * len(key)}).status_code == 401
    assert client.get("/v1/account", headers={"X-Owner-Session": "x" * 43}).status_code == 401
    headers = {"X-Internal-Key": key}
    assert client.get("/v1/account", headers=headers).status_code == 200
    workspace_response = client.get("/v1/account/workspace", headers=headers)
    assert workspace_response.status_code == 200
    assert workspace_response.json()["account"]["id"] == 1
    for path in ("/v1/owner/bootstrap", "/v1/owner/login", "/v1/account/initialization/draft",
                 "/v1/account/initialization/confirm"):
        assert client.post(path, headers=headers, json={}).status_code == 404, path


# ---- ExecPlan 0042: the app funds the account itself, once -----------------------------------------------------

def funding(spot) -> dict:
    (row,) = spot.rows("SELECT * FROM funding_requests")
    return row


def test_the_account_funds_itself_once_with_the_owner_confirmations_journal_and_no_owner_decision(spot):
    assert accounting.fund_by_itself()["status"] == "POSTED"
    request = funding(spot)
    assert (request["kind"], request["amount"], request["idempotency_key"], request["status"],
            request["expected_version"]) == ("INITIALIZE", Decimal("10000"), "SYSTEM:INITIALIZE", "POSTED", 0)
    # The hashes the owner's draft and confirmation computed for the same contribution.
    payload = {"account_id": 1, "amount": "10000.00000000", "denomination": "USDT (virtual)", "kind": "INITIALIZE",
               "version": 0}
    assert request["draft_hash"] == accounting._hash(payload)
    assert request["request_hash"] == accounting._hash({**payload, "draft_hash": request["draft_hash"]})
    assert (request["preflow_equity"], request["preflow_nav"], request["issued_units"], request["unit_residual"]) == (
        0, 100, 100, 0)
    postings = spot.rows(
        "SELECT p.book_account, p.asset, p.amount, t.account_version FROM journal_postings p "
        "JOIN journal_transactions t ON t.id = p.tx_id WHERE t.funding_request_id = :id AND t.id = :tx "
        "ORDER BY p.book_account", id=request["id"], tx=request["journal_tx_id"])
    assert postings == [
        {"book_account": "OWNER_CASH", "asset": "USDT", "amount": Decimal("10000"), "account_version": 1},
        {"book_account": "VIRTUAL_CAPITAL", "asset": "USDT", "amount": Decimal("-10000"), "account_version": 1}]
    assert spot.scalar("SELECT count(*) FROM journal_transactions") == 1
    account = spot.account()
    assert (account["version"], account["initialized"], account["cash"], account["reserved"],
            account["contributions"], account["units"], account["nav"], account["high_water_nav"]) == (
        1, True, Decimal("10000"), 0, Decimal("10000"), 100, 100, 100)
    assert spot.scalar("SELECT count(*) FROM owner_decisions") == 0
    events = spot.rows("SELECT event, correlation_id FROM audit_events WHERE object_id = :id", id=request["id"])
    assert sorted((row["event"], row["correlation_id"]) for row in events) == [
        ("FUNDING_PENDING", "SYSTEM_INITIAL_FUNDING"), ("FUNDING_POSTED", "SYSTEM_INITIAL_FUNDING")]
    outbox = spot.rows("SELECT event, account_version, payload FROM outbox_events WHERE object_id = :id "
                       "ORDER BY id", id=request["id"])
    assert [(row["event"], row["account_version"], row["payload"]) for row in outbox] == [
        ("FUNDING_PENDING", 0, {"request_id": str(request["id"]), "status": "FUNDING_PENDING", "by": "SYSTEM"}),
        ("FUNDING_POSTED", 1, {"request_id": str(request["id"]), "status": "FUNDING_POSTED",
                               "valuation": "CASH_ONLY"})]
    # Each later start finds it funded and writes nothing.
    assert accounting.fund_by_itself() == {"status": "FUNDED"}
    assert spot.scalar("SELECT count(*) FROM funding_requests") == 1
    assert spot.scalar("SELECT count(*) FROM outbox_events") == 2
    assert accounting.reconcile()["status"] == "OK"
    # Posted, it is no longer pending, as any posted request.
    with pytest.raises(accounting.AccountingError, match="REQUEST_NOT_PENDING"):
        accounting.resolve_pending(request["id"], "CANCEL", "no-owner-test")


def test_the_apps_contribution_is_read_by_its_key(spot, client):
    assert client.get("/v1/account/requests/SYSTEM:INITIALIZE").json()["code"] == "REQUEST_NOT_FOUND"
    assert accounting.fund_by_itself()["status"] == "POSTED"  # as the API's own identity, as at its start
    read = client.get("/v1/account/requests/SYSTEM:INITIALIZE")
    assert read.status_code == 200, read.text
    assert (read.json()["kind"], Decimal(read.json()["amount"]), read.json()["status"]) == (
        "INITIALIZE", Decimal("10000"), "POSTED")
    # Only the app's own key is read outside the owner's key pattern.
    assert client.get("/v1/account/requests/SYSTEM:TOPUP").json()["code"] == "INVALID_IDEMPOTENCY_KEY"


@pytest.mark.parametrize(("flag", "status"), [("reconciliation_failed", "RECONCILIATION_REQUIRED"),
                                              ("paused", "POLICY_PAUSED")])
def test_nothing_is_posted_while_the_reconciliation_has_failed_or_the_account_is_paused(spot, flag, status):
    spot.raw(f"UPDATE account_state SET {flag} = true WHERE id = 1")
    assert accounting.fund_by_itself() == {"status": status}
    assert spot.scalar("SELECT count(*) FROM funding_requests") == 0
    assert spot.scalar("SELECT count(*) FROM outbox_events") == 0
    assert not spot.account()["initialized"]
    spot.raw(f"UPDATE account_state SET {flag} = false WHERE id = 1")
    assert accounting.fund_by_itself()["status"] == "POSTED"


def test_a_refused_contribution_is_tried_again_while_the_api_runs_until_it_posts(spot, monkeypatch):
    """An engine clears the reconciliation latch once a later reconciliation passes, with the API still running: the
    API's next try posts the contribution (``main.keep_funding``), as the owner's confirmation sent again did."""
    spot.raw("UPDATE account_state SET reconciliation_failed = true WHERE id = 1")
    refused = accounting.fund_by_itself()
    assert refused == {"status": "RECONCILIATION_REQUIRED"}
    real, tries = accounting.fund_by_itself, []

    def fund_by_itself():
        tries.append(len(tries))
        if len(tries) == 2:
            spot.raw("UPDATE account_state SET reconciliation_failed = false WHERE id = 1")
        return real()

    monkeypatch.setattr(accounting, "fund_by_itself", fund_by_itself)
    asyncio.run(main.keep_funding(refused["status"], interval=0))
    assert len(tries) == 2 and spot.account()["initialized"]
    assert funding(spot)["status"] == "POSTED"
    # Nothing is tried for an answer no later try changes.
    tries.clear()
    for status in ("FUNDED", "POSTED", "CANCELED"):
        asyncio.run(main.keep_funding(status, interval=0))
    assert tries == []
    # A try that fails (the database away for a moment) is followed by the next one.
    answers = iter([OSError("database away"), {"status": "PENDING_VALUATION"}, {"status": "POSTED"}])

    def flaky():
        tries.append(1)
        answer = next(answers)
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(accounting, "fund_by_itself", flaky)
    asyncio.run(main.keep_funding("POLICY_PAUSED", interval=0))
    assert len(tries) == 3


def test_the_api_keeps_trying_while_it_runs_and_stops_with_it(monkeypatch):
    """The API's lifespan: a contribution refused at the start is tried again while the API runs, and nothing is
    tried once it stops. No database: the reconciliation, the contribution and the live listener are stand-ins."""
    tries = []
    monkeypatch.setattr(accounting, "reconcile", lambda: {"status": "OK"})
    monkeypatch.setattr(accounting, "fund_by_itself",
                        lambda: tries.append(1) or {"status": "RECONCILIATION_REQUIRED"})
    monkeypatch.setattr(main.keep_funding, "__defaults__", (0.01,))

    async def connect():
        raise OSError("no database here")

    monkeypatch.setattr(main.LIVE, "connect", connect)

    async def run() -> int:
        async with main.lifespan(main.app):
            await asyncio.sleep(0.1)
        stopped = len(tries)
        await asyncio.sleep(0.05)
        return stopped

    stopped = asyncio.run(run())
    assert stopped > 1 and len(tries) == stopped


def test_a_held_valuation_keeps_the_contribution_pending_until_a_later_start(spot):
    spot.raw("UPDATE account_state SET valuation_valid = false WHERE id = 1")
    first = accounting.fund_by_itself()
    assert first["status"] == "PENDING_VALUATION"
    assert accounting.fund_by_itself() == first  # the same request, still held
    request = funding(spot)
    assert (str(request["id"]), request["status"], request["journal_tx_id"]) == (
        first["request_id"], "PENDING_VALUATION", None)
    assert not spot.account()["initialized"]
    # Canceled, nothing could fund the account any more: the owner's cancel is refused and records nothing.
    with pytest.raises(accounting.AccountingError, match="INITIAL_FUNDING_NOT_CANCELABLE"):
        accounting.resolve_pending(UUID(first["request_id"]), "CANCEL", "no-owner-test")
    assert spot.scalar("SELECT count(*) FROM owner_decisions") == 0
    spot.raw("UPDATE account_state SET valuation_valid = true WHERE id = 1")
    assert accounting.fund_by_itself() == {"status": "POSTED", "request_id": first["request_id"]}
    assert spot.scalar("SELECT count(*) FROM funding_requests") == 1
    assert [row["event"] for row in spot.rows("SELECT event FROM outbox_events ORDER BY id")] == [
        "FUNDING_PENDING", "FUNDING_POSTED"]
    assert spot.account()["cash"] == Decimal("10000")
    assert accounting.fund_by_itself() == {"status": "FUNDED"}
    assert accounting.reconcile()["status"] == "OK"


def test_an_initialization_left_pending_beside_the_posted_one_can_be_canceled(spot):
    """An app from before ExecPlan 0042 could leave a second initialization pending (two confirmations while the
    valuation was held). Once the account is funded it can never post: the owner's cancel is accepted for it, and
    a cancel sent again answers as the first did."""
    spot.raw("UPDATE account_state SET valuation_valid = false WHERE id = 1")
    ours = accounting.fund_by_itself()
    assert ours["status"] == "PENDING_VALUATION"
    payload = {"account_id": 1, "amount": "10000.00000000", "denomination": "USDT (virtual)", "kind": "INITIALIZE",
               "version": 0}
    other = uuid4()
    spot.raw("INSERT INTO funding_requests (id, kind, amount, idempotency_key, request_hash, draft_hash, "
             "expected_version, status) VALUES (:id, 'INITIALIZE', 10000, 'no-owner-old-confirmation', :hash, "
             ":draft, 0, 'PENDING_VALUATION')", id=other, hash=SHA, draft=accounting._hash(payload))
    spot.raw("UPDATE account_state SET valuation_valid = true WHERE id = 1")
    assert accounting.fund_by_itself() == {"status": "POSTED", "request_id": ours["request_id"]}  # the oldest
    canceled = accounting.resolve_pending(other, "CANCEL", "no-owner-test")
    assert canceled["status"] == "CANCELED"
    assert accounting.resolve_pending(other, "CANCEL", "no-owner-test") == canceled
    assert spot.scalar("SELECT count(*) FROM owner_decisions WHERE funding_request_id = :id", id=other) == 1
    assert spot.account()["cash"] == Decimal("10000")
    assert accounting.reconcile()["status"] == "OK"


def test_the_first_run_starts_by_itself_after_the_app_funds_the_account(spot):
    spot.start()
    spot.step(T0)
    assert spot.run() is None
    assert accounting.fund_by_itself()["status"] == "POSTED"
    spot.step(T0 + timedelta(seconds=1))
    run = spot.run()
    assert (run["state"], run["started_by"]) == ("RUNNING", "SYSTEM")
    assert run["start_nav"] == run["high_water_nav"] == nav(Decimal("10000"), Decimal(100))
