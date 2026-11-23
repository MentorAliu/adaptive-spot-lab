"""The private API (ExecPlan 0060: the spot app). The web server is its only caller, with the service key.

The account and its top-ups (M1, ExecPlan 0042: the initial 10,000 virtual USDT the app contributes by itself once),
the spot account's reads for the pages (``app.spot.views``) and its market's (``app.spot_market.views``), the owner's
run requests (``app.spot.requests``) and the live trades (``app.spot.live``). Nothing here posts a trade: only the
execution worker's engine does.
"""

import asyncio
import json
import logging
import os
import re
import secrets
import time
from collections.abc import AsyncIterable
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Annotated, Any, Literal
from uuid import UUID, uuid4

import anyio
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi import Path as FastApiPath
from fastapi.responses import JSONResponse
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app import accounting, code_identity
from app.db import database_ready
from app.spot import live as spot_live
from app.spot import requests as spot_requests
from app.spot import views as spot_views
from app.spot.definitions import COST, POLICY, RULE
from app.spot.requests import SpotError
from app.spot_market import views as market_views

request_log = logging.getLogger("asl.requests")
if not request_log.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    request_log.addHandler(handler)
request_log.setLevel(logging.INFO)
accounting_log = logging.getLogger("asl.accounting")
if not accounting_log.handlers:
    accounting_handler = logging.StreamHandler()
    accounting_handler.setFormatter(logging.Formatter("%(message)s"))
    accounting_log.addHandler(accounting_handler)
accounting_log.setLevel(logging.INFO)
live_log = logging.getLogger("asl.live")
if not live_log.handlers:
    live_handler = logging.StreamHandler()
    live_handler.setFormatter(logging.Formatter("%(message)s"))
    live_log.addHandler(live_handler)
live_log.setLevel(logging.INFO)
REQUEST_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")
LOG_AREAS = frozenset({"account", "spot", "market", "system"})
NOT_CACHED = ("/v1/account", "/v1/spot", "/v1/market", "/v1/system")


class LiveResponse(BaseModel):
    status: Literal["alive"] = "alive"


class ReadyResponse(BaseModel):
    status: Literal["ready"] = "ready"


class UnavailableResponse(BaseModel):
    status: Literal["not_ready"] = "not_ready"
    reason: Literal["database_or_migration_unavailable"] = "database_or_migration_unavailable"


class SystemStatus(BaseModel):
    """Settings' status table (ExecPlan 0060), from recorded facts only."""
    model_config = ConfigDict(extra="forbid")

    mode: Literal["PAPER"] = "PAPER"
    denomination: Literal["USDT (virtual)"] = "USDT (virtual)"
    account: Literal["unconfigured", "unfunded", "funded"] = "unconfigured"
    market_data: Literal["disabled", "unavailable", "degraded", "ready"] = "disabled"
    # The spot run's state; ``inactive`` before the first run, ``stopped`` after the last.
    trading: Literal["inactive", "running", "paused", "stopping", "stopped", "unavailable"] = "inactive"
    execution_worker: Literal["not_running", "running"] = "not_running"
    backtest: Literal["not_computed", "computed", "unavailable"] = "not_computed"


def require_service_key(
    x_internal_key: Annotated[str | None, Header(alias="X-Internal-Key")] = None,
) -> None:
    try:
        expected = Path(
            os.environ.get("ASL_INTERNAL_KEY_FILE", "/run/secrets/api_internal_key")
        ).read_text(encoding="utf-8").strip()
    except OSError:
        raise HTTPException(status_code=503, detail="service_identity_unavailable") from None
    if not expected or not x_internal_key or not secrets.compare_digest(x_internal_key, expected):
        raise HTTPException(status_code=401, detail="unauthorized")


# ExecPlan 0047: the listener the live streams wait on, started by the lifespan.
LIVE = spot_live.Listener(spot_live.connect)


# ExecPlan 0042: the answers of ``accounting.fund_by_itself`` that a later try can change, and how often it is tried.
FUNDING_REFUSED = frozenset({"RECONCILIATION_REQUIRED", "POLICY_PAUSED", "PENDING_VALUATION"})
FUNDING_RETRY_SECONDS = 60.0


def log_funding(funding: dict[str, Any]) -> None:
    accounting_log.log(logging.INFO if funding["status"] in ("FUNDED", "POSTED") else logging.WARNING,
                       json.dumps({"event": "initial_funding", **funding}))


async def keep_funding(status: str, interval: float = FUNDING_RETRY_SECONDS) -> None:
    """The initial contribution refused at the start is tried again every ``interval`` seconds until it is posted:
    an engine clears a reconciliation latch once a later reconciliation passes, and the owner can end a pause, while
    the API keeps running."""
    while status in FUNDING_REFUSED:
        await asyncio.sleep(interval)
        try:
            funding = await asyncio.to_thread(accounting.fund_by_itself)
        except Exception as error:  # noqa: BLE001  the database may be away for a moment; the next try reads it again
            accounting_log.warning(json.dumps({"event": "initial_funding_failed", "error": type(error).__name__}))
            continue
        if funding["status"] != status:
            log_funding(funding)
        status = funding["status"]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Compare projections to immutable sources after every process restart.
    # A mismatch latches the account pause and remains visible to the owner.
    accounting.reconcile()
    # The account's initial contribution, by the app itself once (ExecPlan 0042: no owner setup).
    funding = accounting.fund_by_itself()
    if funding["status"] != "FUNDED":
        log_funding(funding)
    retry = asyncio.create_task(keep_funding(funding["status"]))
    # ExecPlan 0047: the one LISTEN connection that wakes the browsers' live streams.
    listening = asyncio.create_task(LIVE.run())
    try:
        yield
    finally:
        retry.cancel()
        listening.cancel()
        with suppress(asyncio.CancelledError):
            await retry
        with suppress(asyncio.CancelledError):
            await listening


app = FastAPI(
    title="Adaptive Spot Lab private API",
    version="0.0.1",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["api", "localhost", "127.0.0.1"])


@app.middleware("http")
async def record_request(request: Request, call_next):
    supplied = request.headers.get("X-Request-ID", "")
    correlation_id = supplied if REQUEST_ID.fullmatch(supplied) else str(uuid4())
    request.state.correlation_id = correlation_id
    started = time.perf_counter()
    response_status = 500
    try:
        response = await call_next(request)
        response_status = response.status_code
        response.headers["X-Correlation-ID"] = correlation_id
        return response
    finally:
        if not request.url.path.startswith("/v1/health/"):
            # Log the service area, never request bodies, credentials or path parameters.
            parts = request.url.path.split("/")
            area = parts[2] if len(parts) > 2 and parts[2] in LOG_AREAS else "other"
            request_log.info(json.dumps({
                "event": "http_request", "area": area, "method": request.method,
                "status": response_status, "correlation_id": correlation_id,
                "duration_ms": round((time.perf_counter() - started) * 1000, 1),
            }, separators=(",", ":")))


def _too_large() -> JSONResponse:
    return JSONResponse(status_code=413, content={"code": "REQUEST_TOO_LARGE", "message": "Request is too large",
                                                  "correlation_id": str(uuid4()), "retryable": False})


@app.middleware("http")
async def bound_request_body(request: Request, call_next):
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        length = request.headers.get("content-length")
        if length and (not length.isdigit() or int(length) > 8192):
            return _too_large()
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 8192:
                return _too_large()
        request._body = bytes(body)
    return await call_next(request)


@app.middleware("http")
async def reads_are_not_cached(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(NOT_CACHED):
        response.headers["Cache-Control"] = "private, no-store"
    return response


def strict_query(*allowed: str):
    """Reject unknown query parameters instead of silently ignoring them."""
    def check(request: Request) -> None:
        unknown = set(request.query_params.keys()) - set(allowed)
        if unknown:
            raise HTTPException(status_code=422, detail="unknown_query_parameter")
    return Depends(check)


@app.exception_handler(accounting.AccountingError)
@app.exception_handler(SpotError)
async def domain_error(request: Request, exc: accounting.AccountingError | SpotError):
    return JSONResponse(
        status_code=exc.status,
        content={"code": exc.code, "message": exc.code.replace("_", " ").lower(),
                 "correlation_id": request.state.correlation_id, "retryable": exc.status >= 500},
    )


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---- the health and the status --------------------------------------------------------------------------------------

@app.get("/v1/health/live", response_model=LiveResponse, tags=["health"])
def live() -> LiveResponse:
    return LiveResponse()


@app.get(
    "/v1/health/ready",
    response_model=ReadyResponse,
    responses={503: {"model": UnavailableResponse}},
    tags=["health"],
)
def ready() -> ReadyResponse:
    if not database_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=UnavailableResponse().model_dump(),
        )
    return ReadyResponse()


@app.get(
    "/v1/system/status",
    response_model=SystemStatus,
    dependencies=[Depends(require_service_key)],
    tags=["system"],
)
def system_status() -> SystemStatus:
    if not database_ready():
        raise HTTPException(status_code=503, detail="database_or_migration_unavailable")
    try:
        market_status = market_views.system_status()
    except Exception:  # a status never makes this route fail
        market_status = "unavailable"
    try:
        states = spot_views.system_states()
    except Exception:
        states = {"trading": "unavailable", "execution_worker": "not_running", "backtest": "unavailable"}
    snapshot = accounting.account_snapshot()
    return SystemStatus(account="funded" if snapshot["initialized"] else "unfunded", market_data=market_status,
                        **states)


# ---- the account (M1; ExecPlan 0042) -------------------------------------------------------------------------------

class DraftInput(StrictBody):
    amount: str = Field(min_length=1, max_length=32)


class FundingDraft(StrictBody):
    account_id: Literal[1]
    amount: str
    denomination: Literal["USDT (virtual)"]
    kind: Literal["TOPUP"]  # the owner drafts top-ups only; the initial contribution is the app's (ExecPlan 0042)
    version: int
    draft_hash: str
    valuation_status: Literal["VALID", "UNAVAILABLE"]


class ConfirmFunding(StrictBody):
    amount: str = Field(min_length=1, max_length=32)
    expected_version: int = Field(ge=0)
    draft_hash: str = Field(min_length=64, max_length=64)
    idempotency_key: str = Field(min_length=8, max_length=80)


class FundingView(StrictBody):
    id: str
    kind: Literal["INITIALIZE", "TOPUP"]
    amount: str
    status: Literal["PENDING_VALUATION", "POSTED", "CANCELED"]
    idempotency_key: str
    expected_version: int
    preflow_nav: str | None
    issued_units: str | None
    unit_residual: str | None
    journal_tx_id: str | None
    created_at: str
    completed_at: str | None


class HoldingView(StrictBody):
    # BTC, and M3 to M10's dust of the coins they traded (ExecPlan 0060: kept with its postings, not valued).
    asset: str
    quantity: str
    reserved: str
    available: str
    valued: bool


class AccountView(StrictBody):
    id: Literal[1]
    denomination: Literal["USDT (virtual)"]
    initialized: bool
    version: int
    cash: str
    reserved: str
    available: str
    contributions: str
    equity: str | None
    valuation_status: Literal["VALID", "UNAVAILABLE"]
    valuation_source: Literal["CASH_ONLY", "PERSISTED_VALUATION", "UNAVAILABLE"]
    valued_at: str | None
    units: str
    nav: str | None
    high_water_nav: str | None
    pnl: str | None
    paused: bool
    reconciliation_failed: bool
    holdings: list[HoldingView]


class AccountWorkspace(StrictBody):
    account: AccountView
    funding: list[FundingView]


@app.get("/v1/account", response_model=AccountView, tags=["account"])
def account(_service: None = Depends(require_service_key)) -> AccountView:
    return AccountView(**accounting.account_snapshot())


@app.get("/v1/account/workspace", response_model=AccountWorkspace, tags=["account"])
def account_workspace(_service: None = Depends(require_service_key)) -> AccountWorkspace:
    return AccountWorkspace(**accounting.workspace_snapshot())


@app.get("/v1/account/requests/{key}", response_model=FundingView, tags=["account"])
def funding_by_key(key: str, _service: None = Depends(require_service_key)) -> FundingView:
    result = accounting.funding_by_key(key)
    if result is None:
        raise accounting.AccountingError("REQUEST_NOT_FOUND", 404)
    return FundingView(**result)


@app.post("/v1/account/topups/draft", response_model=FundingDraft, tags=["account"])
def topup_draft(body: DraftInput, _service: None = Depends(require_service_key)) -> FundingDraft:
    return FundingDraft(**accounting.draft("TOPUP", body.amount))


@app.post("/v1/account/topups", response_model=FundingView, tags=["account"])
def topup(body: ConfirmFunding, request: Request, _service: None = Depends(require_service_key)) -> FundingView:
    return FundingView(**accounting.confirm("TOPUP", body.amount, body.expected_version, body.draft_hash,
                                            body.idempotency_key, request.state.correlation_id))


@app.post("/v1/account/topups/{request_id}/retry", response_model=FundingView, tags=["account"])
def retry_topup(request_id: UUID, request: Request, _service: None = Depends(require_service_key)) -> FundingView:
    return FundingView(**accounting.resolve_pending(request_id, "RETRY", request.state.correlation_id))


@app.post("/v1/account/topups/{request_id}/cancel", response_model=FundingView, tags=["account"])
def cancel_topup(request_id: UUID, request: Request, _service: None = Depends(require_service_key)) -> FundingView:
    return FundingView(**accounting.resolve_pending(request_id, "CANCEL", request.state.correlation_id))


# ---- the spot market (ExecPlan 0060 section 4.5) ------------------------------------------------------------------

FeedStatus = Literal["STARTING", "CONNECTED", "DEGRADED", "UNAVAILABLE"]
CandleInterval = Literal["1m", "5m", "15m", "1h", "4h", "1d"]


class MarketBook(StrictBody):
    bid: str
    bid_quantity: str
    ask: str
    ask_quantity: str
    bids: list[list[str]]
    asks: list[list[str]]
    second_at: str
    received_at: str
    age_seconds: float


class MarketClock(StrictBody):
    verified: bool
    offset_ms: str | None
    uncertainty_ms: str | None
    checked_at: str | None


class MarketInstrument(StrictBody):
    status: str
    usable: bool
    tick_size: str
    step_size: str
    min_quantity: str
    max_quantity: str
    min_notional: str
    max_notional: str | None
    checked_at: str | None


class MarketDaily(StrictBody):
    days: int
    first_day: str | None
    last_day: str | None
    checked_at: str | None


class MarketView(StrictBody):
    state: Literal["READY", "SCHEMA_PENDING"]
    symbol: Literal["BTCUSDT"]
    evaluated_at: str | None
    status: FeedStatus
    reason: str | None
    stream_connected: bool
    heartbeat_at: str | None
    book: MarketBook | None
    last_candle_at: str | None
    clock: MarketClock | None
    instrument: MarketInstrument | None
    daily: MarketDaily | None
    history_checked_at: str | None
    labels: list[str]


class Candle(StrictBody):
    open_ms: int
    open: str
    high: str
    low: str
    close: str
    volume: str
    minutes: int
    expected_minutes: int
    complete: bool


class Candles(StrictBody):
    state: Literal["READY", "SCHEMA_PENDING"]
    symbol: Literal["BTCUSDT"]
    interval: CandleInterval
    evaluated_at: str | None
    candles: list[Candle]
    labels: list[str]


@app.get("/v1/market", response_model=MarketView, tags=["market"], dependencies=[strict_query()])
def market(_service: None = Depends(require_service_key)) -> MarketView:
    return MarketView(**market_views.market_view())


@app.get("/v1/market/candles", response_model=Candles, tags=["market"],
         dependencies=[strict_query("interval", "limit")])
def market_candles(
    interval: CandleInterval = "1d",
    limit: Annotated[int, Query(ge=1, le=market_views.CANDLES_MAX)] = 365,
    _service: None = Depends(require_service_key),
) -> Candles:
    return Candles(**market_views.candles(interval, limit))


# ---- the spot account (ExecPlan 0060 sections 4.4, 4.6 and 4.9) ---------------------------------------------------

RunState = Literal["RUNNING", "PAUSED", "STOPPING", "STOPPED"]
Cause = Literal["OWNER", "DAILY_LOSS", "DRAWDOWN", "INTEGRITY"]
Side = Literal["BUY", "SELL"]
FillReason = Literal["RULE_BUY", "RULE_SELL", "STOP_SELL"]
RequestKind = Literal["PAUSE", "RESUME", "STOP", "START"]
Cursor = Annotated[str | None, Query(pattern=r"^[1-9][0-9]{0,18}$")]
PageLimit = Annotated[int, Query(ge=1, le=spot_views.PAGE_MAX)]
RequestKey = Annotated[str, FastApiPath(pattern=r"^[A-Za-z0-9_-]{8,64}$")]


class DefinitionRef(StrictBody):
    id: str
    sha256: str


class SpotAccount(StrictBody):
    initialized: bool
    version: int
    cash: str
    btc: str
    btc_value: str | None
    equity: str | None
    share: str | None
    bid: str | None
    valued_at: str | None
    valuation: Literal["VALID", "UNAVAILABLE"]
    units: str
    nav: str | None
    contributions: str
    pnl: str | None
    paused: bool
    reconciliation_failed: bool


class SinceStart(StrictBody):
    """The run against holding Bitcoin, paired by day (ExecPlan 0061): its first and newest timely daily references
    against Bitcoin's daily closes at the same midnights."""
    from_at: str
    from_price: str
    at: str
    price: str
    account: str
    bitcoin: str


class SpotRun(StrictBody):
    id: str
    seq: str
    state: RunState
    causes: list[Cause]
    started_at: str
    started_by: Literal["SYSTEM", "OWNER"]
    start_equity: str
    start_nav: str
    high_water_nav: str
    stopped_at: str | None
    stop_reason: Literal["OWNER", "DRAWDOWN"] | None
    version: int
    code_identity: str
    rule: DefinitionRef
    policy: DefinitionRef
    cost: DefinitionRef
    since_start: SinceStart | None


class SpotLatch(StrictBody):
    cause: Literal["DAILY_LOSS", "DRAWDOWN"]
    latched_at: str


class SpotLimits(StrictBody):
    daily_loss: str
    drawdown: str
    today_change: str | None
    fall_from_high: str | None


class SpotToday(StrictBody):
    utc_date: str
    status: Literal["WAITING", "DUE", "RETRYING", "SPENT", "NONE"]
    next_reading_at: str | None
    retry_seconds: int


class SpotAnchor(StrictBody):
    lookback_days: int
    day: str
    close: str | None
    sign: int


class ReadingFill(StrictBody):
    id: str
    side: Side
    quantity: str
    price: str
    fee: str
    gross: str


class SpotReading(StrictBody):
    id: str
    seq: str
    run_id: str
    utc_date: str
    day_read: str
    at: str
    result: Literal["LONG", "CASH", "WARMUP"]
    reason: str | None
    close: str | None
    signal: str | None
    volatility: str | None
    target: str | None
    held: str | None
    action: Literal["BUY", "SELL", "SELL_ALL", "NO_CHANGE"] | None
    outcome: Literal["NOT_READABLE", "NO_CHANGE", "FILLED", "REFUSED"]
    codes: list[str]
    spent: bool
    anchors: list[SpotAnchor]
    up: int
    fill: ReadingFill | None


class SpotOverview(StrictBody):
    state: Literal["READY", "SCHEMA_PENDING"]
    evaluated_at: str | None
    account: SpotAccount | None
    run: SpotRun | None
    latches: list[SpotLatch]
    limits: SpotLimits | None
    today: SpotToday | None
    last_reading: SpotReading | None
    fills: int


class TradeReading(StrictBody):
    utc_date: str
    target: str | None
    held: str | None
    up: int
    anchors: int


class SpotTrade(StrictBody):
    id: str
    seq: str
    run_id: str
    run_seq: str
    reason: FillReason
    side: Side
    quantity: str
    price: str
    average_price: str
    slippage_bps: str
    gross: str
    fee: str
    fee_rate: str
    cash_after: str
    quantity_after: str
    filled_at: str
    book_second: str
    stop_reason: Literal["OWNER", "DRAWDOWN"] | None
    reading: TradeReading | None


class SpotTradePage(StrictBody):
    state: Literal["READY", "SCHEMA_PENDING"]
    items: list[SpotTrade]
    next_cursor: str | None


class SpotReadingPage(StrictBody):
    state: Literal["READY", "SCHEMA_PENDING"]
    items: list[SpotReading]
    next_cursor: str | None


class SpotActivity(StrictBody):
    state: Literal["READY", "SCHEMA_PENDING"]
    cursor: str
    count: int
    items: list[SpotTrade]


class SpotMarker(StrictBody):
    id: str
    reason: FillReason
    side: Side
    quantity: str
    price: str
    filled_at: str


class SpotMarkers(StrictBody):
    state: Literal["READY", "SCHEMA_PENDING"]
    fills: list[SpotMarker]


class ValuationPoint(StrictBody):
    time: str
    nav: str
    equity: str


class SpotValuations(StrictBody):
    state: Literal["READY", "SCHEMA_PENDING"]
    window: Literal["24h", "7d", "all"]
    bucket_seconds: int
    since: str | None
    base_nav: str | None
    points: list[ValuationPoint]


class BacktestYear(StrictBody):
    year: int
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    return_: str = Field(alias="return")


class BacktestStop(StrictBody):
    day: str
    price: str


class BacktestSide(StrictBody):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    final: str
    return_: str = Field(alias="return")
    a_year: str | None
    worst_fall: str
    worst_fall_day: str | None
    fees: str
    years: list[BacktestYear]


class BacktestRule(BacktestSide):
    buys: int
    sells: int
    refused: int
    days_in_bitcoin: str | None
    average_held: str
    max_held: str
    stopped: BacktestStop | None
    daily_loss_days: int


class BacktestHold(BacktestSide):
    bought: bool


class BacktestWindow(StrictBody):
    key: Literal["SINCE_2019", "SINCE_2023", "LAST_12_MONTHS"]
    first_day: str | None
    last_day: str | None
    days: int
    calendar_days: int
    rule: BacktestRule
    hold: BacktestHold


class BacktestData(StrictBody):
    first_day: str
    last_day: str
    days: int
    missing_days: int


class BacktestInstrument(StrictBody):
    step_size: str
    min_qty: str
    max_qty: str
    min_notional: str
    max_notional: str | None


class BacktestComputed(StrictBody):
    id: str
    seq: str
    computed_at: str
    method: Literal["SPOT_BACKTEST_V1"]
    label: Literal["BACKTEST_MODELED_NOT_FILLED"]
    rule: DefinitionRef
    policy: DefinitionRef
    cost: DefinitionRef
    code_identity: str
    candles_sha256: str
    start_cash: str
    data: BacktestData
    instrument: BacktestInstrument
    windows: list[BacktestWindow]


class BacktestTrade(StrictBody):
    day_ms: int
    side: Side
    price: str
    quantity: str


class BacktestSeries(StrictBody):
    days: list[int]
    rule: list[str]
    hold: list[str]
    target: list[str | None]
    trades: list[BacktestTrade]


BacktestWindowKey = Literal["SINCE_2019", "SINCE_2023", "LAST_12_MONTHS"]


class SpotBacktest(StrictBody):
    state: Literal["READY", "NOT_COMPUTED", "SCHEMA_PENDING"]
    window: BacktestWindowKey
    computed: BacktestComputed | None
    series: BacktestSeries | None


class SpotRequestBody(StrictBody):
    kind: RequestKind
    run_id: UUID | None = None
    idempotency_key: str = Field(pattern=r"^[A-Za-z0-9_-]{8,64}$")


class SpotRequestView(StrictBody):
    id: str
    kind: RequestKind
    run_id: str | None
    idempotency_key: str
    status: Literal["PENDING", "APPLIED", "REJECTED"]
    reasons: list[str]
    created_at: str
    answered_at: str | None


class SpotDefinitions(StrictBody):
    """The code's definitions in force, with the running app's code identity (Settings' "Version")."""
    rule: DefinitionRef
    policy: DefinitionRef
    cost: DefinitionRef
    code_identity: str
    rule_document: dict[str, Any]
    policy_document: dict[str, Any]
    cost_document: dict[str, Any]


@app.get("/v1/spot", response_model=SpotOverview, tags=["spot"], dependencies=[strict_query()])
def spot_overview(_service: None = Depends(require_service_key)) -> SpotOverview:
    return SpotOverview(**spot_views.overview())


@app.get("/v1/spot/trades", response_model=SpotTradePage, tags=["spot"],
         dependencies=[strict_query("cursor", "limit")])
def spot_trades(cursor: Cursor = None, limit: PageLimit = 25,
                _service: None = Depends(require_service_key)) -> SpotTradePage:
    return SpotTradePage(**spot_views.trades(int(cursor) if cursor else None, limit))


@app.get("/v1/spot/readings", response_model=SpotReadingPage, tags=["spot"],
         dependencies=[strict_query("cursor", "limit")])
def spot_readings(cursor: Cursor = None, limit: PageLimit = 25,
                  _service: None = Depends(require_service_key)) -> SpotReadingPage:
    return SpotReadingPage(**spot_views.readings(int(cursor) if cursor else None, limit))


@app.get("/v1/spot/activity", response_model=SpotActivity, tags=["spot"], dependencies=[strict_query("after")])
def spot_activity(after: Annotated[str | None, Query(pattern=r"^(0|[1-9][0-9]{0,18})$")] = None,
                  _service: None = Depends(require_service_key)) -> SpotActivity:
    return SpotActivity(**spot_views.activity(int(after) if after is not None else None))


def live_available() -> None:
    try:
        LIVE.available()
    except spot_live.Unavailable as exc:
        raise SpotError(exc.code, 503) from None


@app.get("/v1/spot/live", response_class=EventSourceResponse, tags=["spot"],
         dependencies=[strict_query(), Depends(require_service_key), Depends(live_available)])
async def spot_live_stream(
        last_event_id: Annotated[str | None, Header(alias="Last-Event-ID", pattern=r"^(0|[1-9][0-9]{0,18})$")] = None,
) -> AsyncIterable[ServerSentEvent]:
    """The trades as they happen (ExecPlan 0047): ``ready``, then an ``activity`` for each new fill (the toasts' feed
    after the stream's cursor, which is each event's id) and a ``change`` for the rest."""
    async def read(after: int | None) -> dict[str, Any]:
        return await anyio.to_thread.run_sync(spot_views.activity, after)

    async for event in spot_live.events(LIVE, int(last_event_id) if last_event_id is not None else None, read):
        yield event


@app.get("/v1/spot/markers", response_model=SpotMarkers, tags=["spot"], dependencies=[strict_query("since_ms")])
def spot_markers(since_ms: Annotated[int, Query(ge=0, le=4_102_444_800_000)],
                 _service: None = Depends(require_service_key)) -> SpotMarkers:
    return SpotMarkers(**spot_views.markers(since_ms))


@app.get("/v1/spot/valuations", response_model=SpotValuations, tags=["spot"], dependencies=[strict_query("window")])
def spot_valuations(window: Literal["24h", "7d", "all"] = "all",
                    _service: None = Depends(require_service_key)) -> SpotValuations:
    """The account's NAV and equity over the window, newest valuation of each bucket (ExecPlan 0048)."""
    return SpotValuations(**spot_views.valuations(window))


@app.get("/v1/spot/backtest", response_model=SpotBacktest, tags=["spot"], dependencies=[strict_query("window")])
def spot_backtest(window: BacktestWindowKey = "SINCE_2019",
                  _service: None = Depends(require_service_key)) -> SpotBacktest:
    return SpotBacktest(**spot_views.backtest(window))


@app.get("/v1/spot/definitions", response_model=SpotDefinitions, tags=["spot"], dependencies=[strict_query()])
def spot_definitions(_service: None = Depends(require_service_key)) -> SpotDefinitions:
    from app.spot.definitions import SPOT_COST_V1, SPOT_POLICY_V1, SPOT_RULE_V1

    return SpotDefinitions(
        rule=DefinitionRef(id=RULE.id, sha256=RULE.sha256), policy=DefinitionRef(id=POLICY.id, sha256=POLICY.sha256),
        cost=DefinitionRef(id=COST.id, sha256=COST.sha256), code_identity=code_identity.current(),
        rule_document=SPOT_RULE_V1, policy_document=SPOT_POLICY_V1, cost_document=SPOT_COST_V1)


@app.post("/v1/spot/requests", response_model=SpotRequestView, tags=["spot"])
def spot_request(body: SpotRequestBody, request: Request,
                 _service: None = Depends(require_service_key)) -> SpotRequestView:
    return SpotRequestView(**spot_requests.submit(kind=body.kind, run_id=body.run_id, key=body.idempotency_key,
                                                  correlation=request.state.correlation_id))


@app.get("/v1/spot/requests/{key}", response_model=SpotRequestView, tags=["spot"], dependencies=[strict_query()])
def spot_request_by_key(key: RequestKey, _service: None = Depends(require_service_key)) -> SpotRequestView:
    found = spot_requests.by_key(key)
    if found is None:
        raise SpotError("REQUEST_NOT_FOUND", 404)
    return SpotRequestView(**found)
