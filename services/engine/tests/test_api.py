from fastapi.testclient import TestClient

from app import main


def test_live_does_not_depend_on_database(monkeypatch):
    monkeypatch.setattr(main, "database_ready", lambda: False)
    client = TestClient(main.app, base_url="http://api:8000")
    assert client.get("/v1/health/live").json() == {"status": "alive"}
    assert client.get("/v1/health/ready").status_code == 503


def test_container_loopback_health_probe_is_allowed(monkeypatch):
    monkeypatch.setattr(main, "database_ready", lambda: True)
    client = TestClient(main.app, base_url="http://127.0.0.1:8000")
    assert client.get("/v1/health/ready").json() == {"status": "ready"}
    assert client.get("/v1/health/live", headers={"Host": "outside.example"}).status_code == 400


def test_status_requires_service_identity_and_ready_database(monkeypatch, tmp_path):
    """ExecPlan 0060: Settings' status table, from recorded facts only. No database here: the market's status, the
    spot account's states and the account are stand-ins (``test_spot_api`` reads them from a database)."""
    key_file = tmp_path / "api_internal_key"
    key_file.write_text("test-only-secret", encoding="utf-8")
    monkeypatch.setenv("ASL_INTERNAL_KEY_FILE", str(key_file))
    monkeypatch.setattr(main, "database_ready", lambda: True)
    monkeypatch.setattr(main.market_views, "system_status", lambda: "disabled")
    monkeypatch.setattr(main.spot_views, "system_states",
                        lambda: {"trading": "inactive", "execution_worker": "not_running", "backtest": "not_computed"})
    monkeypatch.setattr(main.accounting, "account_snapshot", lambda: {"initialized": False})
    client = TestClient(main.app, base_url="http://api:8000")

    assert client.get("/v1/system/status").status_code == 401
    assert client.get("/v1/system/status", headers={"X-Internal-Key": "wrong"}).status_code == 401
    response = client.get("/v1/system/status", headers={"X-Internal-Key": "test-only-secret"})
    assert response.status_code == 200
    assert response.json() == {"mode": "PAPER", "denomination": "USDT (virtual)", "account": "unfunded",
                               "market_data": "disabled", "trading": "inactive", "execution_worker": "not_running",
                               "backtest": "not_computed"}

    # A status never makes the route fail: what cannot be read shows as unavailable.
    def broken(*_args):
        raise RuntimeError("unreadable")

    monkeypatch.setattr(main.market_views, "system_status", broken)
    monkeypatch.setattr(main.spot_views, "system_states", broken)
    monkeypatch.setattr(main.accounting, "account_snapshot", lambda: {"initialized": True})
    degraded = client.get("/v1/system/status", headers={"X-Internal-Key": "test-only-secret"}).json()
    assert (degraded["account"], degraded["market_data"], degraded["trading"], degraded["execution_worker"],
            degraded["backtest"]) == ("funded", "unavailable", "unavailable", "not_running", "unavailable")


def test_every_read_requires_the_service_identity(monkeypatch, tmp_path):
    key_file = tmp_path / "service_key"
    key_file.write_text("test-only-market-service-secret", encoding="utf-8")
    monkeypatch.setenv("ASL_INTERNAL_KEY_FILE", str(key_file))
    client = TestClient(main.app, base_url="http://api:8000")
    paths = (
        "/v1/system/status",
        "/v1/account",
        "/v1/account/workspace",
        "/v1/account/requests/abcdefgh",
        "/v1/market",
        "/v1/market/candles?interval=1d&limit=10",
        "/v1/spot",
        "/v1/spot/trades",
        "/v1/spot/readings",
        "/v1/spot/activity",
        "/v1/spot/live",
        "/v1/spot/markers?since_ms=0",
        "/v1/spot/valuations?window=24h",
        "/v1/spot/backtest?window=SINCE_2019",
        "/v1/spot/definitions",
        "/v1/spot/requests/abcdefgh",
    )
    # Since ExecPlan 0042 the service key is the only identity: without it, or with another key, nothing is read.
    for path in paths:
        assert client.get(path).status_code == 401, path
        assert client.get(path, headers={"X-Internal-Key": "test-only-market-service-wrong"}).status_code == 401
        assert client.get(path, headers={"X-Owner-Session": "fake"}).status_code == 401
    for path in ("/v1/spot/requests", "/v1/account/topups/draft", "/v1/account/topups"):
        assert client.post(path, json={}).status_code == 401, path


def test_the_sign_in_and_the_owner_setup_are_gone(monkeypatch, tmp_path):
    """ExecPlan 0042: no owner sign-in and no initialization; the account funds itself at the API's start."""
    key_file = tmp_path / "service_key"
    key_file.write_text("test-only-gone-service-secret", encoding="utf-8")
    monkeypatch.setenv("ASL_INTERNAL_KEY_FILE", str(key_file))
    client = TestClient(main.app, base_url="http://api:8000",
                        headers={"X-Internal-Key": "test-only-gone-service-secret"})
    for method, path in (("GET", "/v1/owner/status"), ("POST", "/v1/owner/bootstrap"), ("POST", "/v1/owner/login"),
                         ("POST", "/v1/owner/logout"), ("GET", "/v1/owner/session"),
                         ("POST", "/v1/account/initialization/draft"), ("POST", "/v1/account/initialization/confirm")):
        assert client.request(method, path, json={}).status_code == 404, path
    assert not any(route.path.startswith("/v1/owner") for route in main.app.routes)
    assert not hasattr(main, "require_owner_session")


def test_status_does_not_mask_database_failure(monkeypatch, tmp_path):
    key_file = tmp_path / "api_internal_key"
    key_file.write_text("test-only-secret", encoding="utf-8")
    monkeypatch.setenv("ASL_INTERNAL_KEY_FILE", str(key_file))
    monkeypatch.setattr(main, "database_ready", lambda: False)
    response = TestClient(main.app, base_url="http://api:8000").get(
        "/v1/system/status", headers={"X-Internal-Key": "test-only-secret"}
    )
    assert response.status_code == 503
    assert "database_or_migration_unavailable" in response.text
