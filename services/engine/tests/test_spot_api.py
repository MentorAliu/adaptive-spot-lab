"""The API's spot routes on a scratch database (ExecPlan 0060 section 6, R8): each read returns what the engine and the
feed stored, the owner's requests are recorded once and answered by the engine, and nothing of the removed API
answers. Every market row is SYNTHETIC (``spot_support``, ``spot_market_support``)."""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from spot_support import T0, day_open, trend

from app import main
from app.spot import backtest
from app.spot.definitions import COST, POLICY, RULE
from app.spot_market import bars as spot_bars
from app.spot_market import market, store
from app.spot_market.views import plain

KEY = "test-only-secret"
SECOND = timedelta(seconds=1)
MINUTE = timedelta(minutes=1)


@pytest.fixture
def client(monkeypatch, tmp_path):
    key_file = tmp_path / "api_internal_key"
    key_file.write_text(KEY, encoding="utf-8")
    monkeypatch.setenv("ASL_INTERNAL_KEY_FILE", str(key_file))
    return TestClient(main.app, base_url="http://api:8000", headers={"X-Internal-Key": KEY})


def get(client: TestClient, path: str, **params) -> dict:
    response = client.get(path, params=params)
    assert response.status_code == 200, response.text
    return response.json()


def bought(spot) -> dict:
    """A funded account, its first run and the day's buy."""
    spot.ready()
    spot.start()
    spot.step(T0)
    [fill] = spot.fills()
    return fill


def test_the_cockpit_reads_what_the_engine_stored(spot, client):
    fill = bought(spot)
    [reading] = spot.readings()
    run = spot.run()
    view = get(client, "/v1/spot")
    assert view["state"] == "READY" and view["fills"] == 1
    assert view["run"]["id"] == str(run["id"]) and view["run"]["state"] == "RUNNING"
    assert view["run"]["started_by"] == "SYSTEM" and view["run"]["code_identity"] == "c" * 64
    assert (view["run"]["rule"], view["run"]["policy"], view["run"]["cost"]) == (
        {"id": RULE.id, "sha256": RULE.sha256}, {"id": POLICY.id, "sha256": POLICY.sha256},
        {"id": COST.id, "sha256": COST.sha256})
    account = view["account"]
    assert account["btc"] == plain(fill["quantity"]) and account["cash"] == plain(fill["cash_after"])
    valuation = spot.rows("SELECT * FROM spot_valuations ORDER BY valued_at DESC, recorded_at DESC LIMIT 1")[0]
    assert valuation["purpose"] == "FILL" and account["equity"] == plain(valuation["equity"])
    assert account["valuation"] == "VALID" and account["bid"] == plain(valuation["bid"])
    share = (valuation["equity"] - valuation["cash"]) / valuation["equity"]
    assert Decimal(account["share"]) == share.quantize(Decimal("0.00000001"))
    assert Decimal(account["pnl"]) == valuation["equity"] - Decimal(10000)
    last = view["last_reading"]
    assert (last["id"], last["outcome"], last["action"], last["spent"]) == (str(reading["id"]), "FILLED", "BUY", True)
    assert last["up"] == 3 and [a["lookback_days"] for a in last["anchors"]] == [30, 91, 365]
    assert last["target"] == plain(reading["target"]) and last["fill"]["quantity"] == plain(fill["quantity"])
    assert last["day_read"] == (T0 - timedelta(days=1)).date().isoformat()
    assert view["limits"]["daily_loss"] == "0.02" and view["limits"]["drawdown"] == "0.08"
    assert view["latches"] == [] and view["today"]["retry_seconds"] == 900
    # Today (the database's day, not the engine's synthetic one) has no reading yet.
    assert view["today"]["status"] in ("WAITING", "DUE")


def test_the_trades_readings_markers_values_and_toasts(spot, client):
    fill = bought(spot)
    spot.request("STOP")
    spot.book(T0 + 10 * SECOND)
    spot.step(T0 + 10 * SECOND)
    buy, sell = spot.fills()
    assert buy["id"] == fill["id"] and sell["reason"] == "STOP_SELL"
    first = get(client, "/v1/spot/trades", limit=1)
    assert [item["id"] for item in first["items"]] == [str(sell["id"])] and first["next_cursor"] == str(sell["seq"])
    assert first["items"][0]["stop_reason"] == "OWNER" and first["items"][0]["reading"] is None
    second = get(client, "/v1/spot/trades", limit=1, cursor=first["next_cursor"])
    [item] = second["items"]
    assert second["next_cursor"] is None and item["id"] == str(buy["id"]) and item["side"] == "BUY"
    assert (item["quantity"], item["price"], item["fee"], item["gross"]) == (
        plain(buy["quantity"]), plain(buy["price"]), plain(buy["fee"]), plain(buy["gross"]))
    assert item["reading"]["utc_date"] == T0.date().isoformat() and item["reading"]["up"] == 3
    readings = get(client, "/v1/spot/readings")
    assert [row["outcome"] for row in readings["items"]] == ["FILLED"] and readings["next_cursor"] is None
    marks = get(client, "/v1/spot/markers", since_ms=0)["fills"]
    assert [(m["side"], m["reason"]) for m in marks] == [("BUY", "RULE_BUY"), ("SELL", "STOP_SELL")]
    curve = get(client, "/v1/spot/valuations", window="all")
    valid = spot.rows("SELECT nav FROM spot_valuations WHERE quality = 'VALID' ORDER BY valued_at, recorded_at, id")
    assert curve["points"] and curve["base_nav"] == plain(valid[0]["nav"]) and curve["bucket_seconds"] == 14400
    assert get(client, "/v1/spot/valuations", window="24h")["points"] == []  # the engine's days are synthetic
    # The toasts' feed: only the cursor without ``after``; the fills after it, oldest first.
    assert get(client, "/v1/spot/activity") == {"state": "READY", "cursor": str(sell["seq"]), "count": 0, "items": []}
    feed = get(client, "/v1/spot/activity", after=0)
    assert feed["count"] == 2 and [i["id"] for i in feed["items"]] == [str(buy["id"]), str(sell["id"])]
    assert get(client, "/v1/spot/activity", after=str(buy["seq"]))["count"] == 1


def test_the_owners_requests_are_recorded_once_and_answered_by_the_engine(spot, client):
    bought(spot)
    run = str(spot.run()["id"])
    key = f"pause-{uuid4().hex[:12]}"
    body = {"kind": "PAUSE", "run_id": run, "idempotency_key": key}
    first = client.post("/v1/spot/requests", json=body)
    assert first.status_code == 200 and first.json()["status"] == "PENDING"
    assert client.post("/v1/spot/requests", json=body).json()["id"] == first.json()["id"]
    conflict = client.post("/v1/spot/requests", json={**body, "kind": "STOP"})
    assert (conflict.status_code, conflict.json()["code"]) == (409, "IDEMPOTENCY_CONFLICT")
    for payload, status, code in (
            ({"kind": "START", "idempotency_key": "start-12345678"}, 409, "RUN_LIVE"),
            ({"kind": "PAUSE", "run_id": str(uuid4()), "idempotency_key": "pause-other-1"}, 409, "RUN_CHANGED"),
            ({"kind": "START", "run_id": run, "idempotency_key": "start-with-run"}, 422, "START_TAKES_NO_RUN"),
            ({"kind": "RESUME", "idempotency_key": "resume-no-run"}, 422, "RUN_REQUIRED")):
        refused = client.post("/v1/spot/requests", json=payload)
        assert (refused.status_code, refused.json()["code"]) == (status, code)
    assert client.post("/v1/spot/requests", json={**body, "kind": "SELL_ALL"}).status_code == 422
    assert client.post("/v1/spot/requests", json={**body, "extra": 1}).status_code == 422
    assert get(client, f"/v1/spot/requests/{key}")["status"] == "PENDING"
    spot.book(T0 + 5 * SECOND)
    spot.step(T0 + 5 * SECOND)
    answered = get(client, f"/v1/spot/requests/{key}")
    assert answered["status"] == "APPLIED" and answered["answered_at"] is not None
    assert get(client, "/v1/spot")["run"]["causes"] == ["OWNER"]
    assert spot.scalar("SELECT count(*) FROM audit_events WHERE event = 'SPOT_PAUSE_REQUESTED'") == 1
    assert client.get("/v1/spot/requests/unknown-key-1").status_code == 404


def test_the_market_and_its_candles(spot, client):
    spot.ready()
    now = datetime.now(UTC)
    now_ms = int(now.timestamp() * 1000) // market.MINUTE_MS * market.MINUTE_MS
    received = now
    minutes = [market.Bar(now_ms - n * market.MINUTE_MS, Decimal("60000"), Decimal("60050"), Decimal("59950"),
                          Decimal("60010"), Decimal("2"), Decimal("120000"), 5, n > 0, None) for n in (6, 1, 0)]
    store.write_history(spot.market, minutes, received, received)
    today = now_ms - now_ms % market.DAY_MS
    view = get(client, "/v1/market")
    assert view["state"] == "READY" and view["book"]["bid"] == "60000" and len(view["book"]["bids"]) == 10
    assert view["instrument"]["step_size"] == "0.00001" and view["instrument"]["usable"] is True
    stored = spot.rows("SELECT count(*) AS n, min(open_ms) AS first, max(open_ms) AS last FROM spot_daily_bars")[0]
    assert view["daily"]["days"] == stored["n"]
    assert view["daily"]["first_day"] == datetime.fromtimestamp(stored["first"] / 1000, tz=UTC).date().isoformat()
    # The harness's feed state is ten days old: the feed is taken to be down.
    assert (view["status"], view["reason"]) == ("UNAVAILABLE", "FEED_SILENT")
    daily = get(client, "/v1/market/candles", interval="1d", limit=3)["candles"]
    today_bars = [bar for bar in minutes if bar.open_ms >= today]
    assert daily[-1]["open_ms"] == today and daily[-1]["complete"] is False
    assert daily[-1]["minutes"] == len(today_bars) and daily[-1]["expected_minutes"] == 1440
    assert all(candle["complete"] and candle["minutes"] == 1440 for candle in daily[:-1])
    newest = [row["open_ms"] for row in spot.rows(
        "SELECT open_ms FROM spot_daily_bars WHERE open_ms < :today ORDER BY open_ms DESC LIMIT 2", today=today)]
    assert [c["open_ms"] for c in daily[:-1]] == sorted(newest) and len(newest) == 2
    five = get(client, "/v1/market/candles", interval="5m", limit=3)["candles"]
    built = spot_bars.aggregate(minutes, 300_000)[-3:]
    assert [(c["open_ms"], c["minutes"], c["complete"]) for c in five] == [
        (c.open_ms, c.minutes, c.complete) for c in built]
    assert client.get("/v1/market/candles", params={"interval": "2h"}).status_code == 422
    assert client.get("/v1/market/candles", params={"limit": 1001}).status_code == 422


def test_the_backtest_reads_the_newest_computation_by_window(spot, client):
    assert get(client, "/v1/spot/backtest")["state"] == "NOT_COMPUTED"
    last = day_open(datetime(2026, 11, 1, tzinfo=UTC))
    closes = trend(last, days=1036)
    days = [backtest.Day(at, close, close + 100, close - 100, close) for at, close in sorted(closes.items())]
    filters = backtest.money.Filters(step=Decimal("0.00001"), min_qty=Decimal("0.00001"), max_qty=Decimal("9000"),
                                     min_notional=Decimal("5"), max_notional=Decimal("9000000"))
    result, series = backtest.compute(days, filters)
    with spot.execution.begin() as connection:
        stored = backtest.store_result(connection, at=datetime.now(UTC), code_identity="c" * 64, days=days,
                                       result=result, series=series)
    view = get(client, "/v1/spot/backtest")
    assert view["state"] == "READY" and view["window"] == "SINCE_2019"
    computed = view["computed"]
    assert computed["id"] == str(stored) and computed["label"] == "BACKTEST_MODELED_NOT_FILLED"
    assert [w["key"] for w in computed["windows"]] == ["SINCE_2019", "SINCE_2023", "LAST_12_MONTHS"]
    assert computed["data"] == result["data"] and computed["rule"]["sha256"] == RULE.sha256
    since = computed["windows"][0]
    assert since["rule"]["final"] == result["windows"][0]["rule"]["final"]
    assert since["rule"]["years"][0]["return"] == result["windows"][0]["rule"]["years"][0]["return"]
    assert len(view["series"]["days"]) == since["days"] == len(view["series"]["rule"])
    assert len(view["series"]["trades"]) == since["rule"]["buys"] + since["rule"]["sells"]
    year = get(client, "/v1/spot/backtest", window="LAST_12_MONTHS")
    assert len(year["series"]["days"]) == 365 and year["series"]["days"][-1] == last
    assert date.fromisoformat(year["computed"]["windows"][2]["first_day"]) == date(2025, 11, 2)
    assert client.get("/v1/spot/backtest", params={"window": "SINCE_2017"}).status_code == 422


def test_the_status_the_definitions_and_the_removed_routes(spot, client):
    bought(spot)
    status = get(client, "/v1/system/status")
    assert status == {"mode": "PAPER", "denomination": "USDT (virtual)", "account": "funded",
                      "market_data": "unavailable", "trading": "running", "execution_worker": status["execution_worker"],
                      "backtest": "not_computed"}
    definitions = get(client, "/v1/spot/definitions")
    assert definitions["rule"] == {"id": "SPOT_RULE_V1", "sha256": RULE.sha256}
    assert definitions["rule_document"]["lookback_days"] == [30, 91, 365] and len(definitions["code_identity"]) == 64
    for path in ("/v1/futures", "/v1/futures/trades", "/v1/perp/market", "/v1/agent-runtime", "/v1/orders",
                 "/v1/positions", "/v1/experiments", "/v1/coins", "/v1/sources", "/v1/research/jobs",
                 "/v1/markets/health", "/v1/trade-intents", "/v1/approvals", "/v1/risk"):
        assert client.get(path).status_code == 404, path
    assert client.get("/v1/spot", params={"x": "1"}).status_code == 422
    assert TestClient(main.app, base_url="http://api:8000").get("/v1/spot").status_code == 401
    assert client.get("/v1/spot").headers["Cache-Control"] == "private, no-store"


def test_reads_wait_for_the_schema(monkeypatch, client):
    """Before migration 0041 every read reports the schema as pending (no database needed)."""
    from app.spot import views as spot_views
    from app.spot_market import views as market_views

    for module in (spot_views, market_views):
        monkeypatch.setattr(module, "ready", lambda: False)
    monkeypatch.setattr("app.spot.requests.ready", lambda: False)
    assert get(client, "/v1/spot")["state"] == "SCHEMA_PENDING"
    assert get(client, "/v1/spot/trades")["items"] == []
    assert get(client, "/v1/spot/backtest")["state"] == "SCHEMA_PENDING"
    assert get(client, "/v1/market")["state"] == "SCHEMA_PENDING"
    assert get(client, "/v1/market/candles")["candles"] == []
    refused = client.post("/v1/spot/requests", json={"kind": "START", "idempotency_key": "start-12345678"})
    assert (refused.status_code, refused.json()["code"]) == (409, "SPOT_SCHEMA_PENDING")
