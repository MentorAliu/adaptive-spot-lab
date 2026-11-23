"""The fixed, unauthenticated transport to Binance's market-data-only spot hosts (M2's client; ExecPlan 0060
section 4.5). ``app.market_data.provider`` until ExecPlan 0060, with the perpetual's hosts removed.

Every request goes to one fixed host resolved to public addresses only, without a redirect, a private parameter or a
credential, with a bounded answer, under the worker's own weight ceiling, the IP-wide guard and any provider
back-off. Weights are Binance's documented ones for the spot REST API (read 2026-11-12, ExecPlan 0060 section 7):
``time`` 1, ``exchangeInfo`` 20, ``klines`` 2.
"""

import asyncio
import ipaddress
import random
import socket
import time
from collections import deque
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode

import httpx
from websockets.asyncio.client import connect

from app.spot_market import market
from app.spot_market.parse import PayloadError, declared_request_weight, decode_json

REST_HOST = market.REST_HOST
STREAM_HOST = market.STREAM_HOST
# The only hosts a client may resolve.
HOSTS = (REST_HOST, STREAM_HOST)
# websockets bounds close() itself and aborts the transport at this deadline.
# The worker never wraps close() in a shorter cancelling timeout.
STREAM_CLOSE_TIMEOUT = 2
# The worker's own ceiling: the weight of its own requests in any 60 seconds.
OWN_CEILING = 120
# The provider reports the weight used by the whole IP, which other clients may
# share. That value is held under this share of the provider's declared
# allowance, not under the worker's own ceiling.
IP_GUARD_DIVISOR = 2
# One attempt per clock sample: an answer slower than a second cannot pass the
# clock rule, and the worker rechecks soon after a failed check.
CLOCK_SAMPLE_DEADLINE = 3.0
# A reservation that waited at least this long is reported to the worker.
WAIT_REPORT_SECONDS = 1.0


class ProviderUnavailable(RuntimeError):
    def __init__(self, code: str, retry_after: float = 0):
        super().__init__(code)
        self.code = code
        self.retry_after = retry_after


async def resolve_public_ip(host: str) -> str:
    """Resolve a fixed host and return the checked address used by the socket."""
    if host not in HOSTS:
        raise ProviderUnavailable("destination_not_allowed")
    try:
        addresses = await asyncio.to_thread(socket.getaddrinfo, host, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ProviderUnavailable("provider_dns_unavailable") from exc
    if not addresses or any(not ipaddress.ip_address(entry[4][0]).is_global for entry in addresses):
        raise ProviderUnavailable("provider_dns_not_public")
    # Prefer IPv4 on Docker hosts without an IPv6 route. The connection uses
    # this literal address while TLS SNI and Host retain the fixed provider name.
    return next((entry[4][0] for entry in addresses if entry[0] == socket.AF_INET), addresses[0][4][0])


class WeightBudget:
    """Request-weight accounting for the REST transport.

    The worker's own requests stay under its own ceiling. The IP-wide value the
    provider reports stays under a guard derived from the provider's declared
    allowance; until an allowance has been read the guard is the own ceiling.
    A provider back-off blocks every reservation until it has passed."""

    def __init__(self, maximum: int = OWN_CEILING):
        self.maximum = maximum
        self.allowance: int | None = None
        # Set by the worker: waits end when it stops, and waits, back-offs and
        # the declared allowance are reported to it.
        self.stop: asyncio.Event | None = None
        self.report: Callable[[dict], Awaitable[None]] | None = None
        self.monotonic = time.monotonic
        self._events: deque[tuple[float, int]] = deque()
        self._lock = asyncio.Lock()
        self._remote_used = 0
        self._remote_observed_at = 0.0
        self._remote_highest = 0
        self._blocked_until = 0.0

    @property
    def ceiling(self) -> int:
        return self.maximum if self.allowance is None else min(self.maximum, self.allowance)

    @property
    def guard(self) -> int:
        if self.allowance is None:
            return self.ceiling
        return max(self.ceiling, self.allowance // IP_GUARD_DIVISOR)

    def declare(self, allowance: int | None) -> bool:
        """Adopt the provider's declared one-minute allowance; say whether it changed.
        An answer that does not declare one leaves the last known value."""
        if allowance is None or allowance == self.allowance:
            return False
        self.allowance = allowance
        return True

    def block(self, seconds: float) -> None:
        """Hold every reservation for a provider back-off."""
        self._blocked_until = max(self._blocked_until, self.monotonic() + seconds)

    def observe_used(self, header: str | None) -> None:
        # Never waits: a reservation may be sleeping.
        if header is None or not header.isascii() or not header.isdecimal():
            return
        self._remote_used = int(header)
        self._remote_observed_at = self.monotonic()
        self._remote_highest = max(self._remote_highest, self._remote_used)

    def snapshot(self) -> dict[str, int | None]:
        """Own use now and the highest IP-wide value since the previous snapshot."""
        now = self.monotonic()
        highest, self._remote_highest = self._remote_highest, 0
        return {"own_used": sum(weight for at, weight in self._events if at > now - 60),
                "ip_used_max": highest, "ceiling": self.ceiling, "guard": self.guard,
                "allowance": self.allowance}

    async def tell(self, report: dict) -> None:
        if self.report is not None:
            await self.report(report)

    async def _pause(self, seconds: float) -> None:
        if self.stop is None:
            await asyncio.sleep(seconds)
            return
        if not self.stop.is_set():
            try:
                await asyncio.wait_for(self.stop.wait(), timeout=seconds)
            except TimeoutError:
                return
        raise ProviderUnavailable("worker_stopping")

    async def reserve(self, weight: int, path: str = "") -> float:
        """Wait until the request fits, charge it and return the seconds waited."""
        began = self.monotonic()
        waits: dict[str, float] = {}
        seen: dict = {}
        async with self._lock:
            while True:
                now = self.monotonic()
                while self._events and self._events[0][0] <= now - 60:
                    self._events.popleft()
                own = sum(w for _, w in self._events)
                remote = self._remote_used if now - self._remote_observed_at < 60 else 0
                if now < self._blocked_until:
                    reason, wait = "provider_backoff", self._blocked_until - now
                elif own + weight > self.ceiling and self._events:
                    # A request heavier than the ceiling itself still goes
                    # alone in an empty minute; the provider's own 429 is the limit.
                    reason, wait = "own_ceiling", 60 - (now - self._events[0][0])
                elif remote and remote + weight > self.guard:
                    # Only an observed IP-wide value holds a request back; it stops
                    # counting a minute after it was read.
                    reason, wait = "ip_guard", 60 - (now - self._remote_observed_at)
                else:
                    self._events.append((now, weight))
                    break
                # Look again at least once a second: a back-off or an
                # observation may have changed meanwhile.
                pause = min(1.0, max(0.1, wait))
                paused = self.monotonic()
                await self._pause(pause)
                waits[reason] = waits.get(reason, 0.0) + (self.monotonic() - paused)
                seen.setdefault(reason, {"own_used": own, "ip_used": remote})
        waited = self.monotonic() - began
        if waits and waited >= WAIT_REPORT_SECONDS:
            # The reason the request waited longest for, with what was seen when that wait began.
            reason = max(waits, key=waits.get)
            await self.tell({"kind": "wait", "path": path, "weight": weight, "waited_ms": round(waited * 1000, 1),
                             "reason": reason, **seen[reason], "ceiling": self.ceiling, "guard": self.guard})
        return waited


def retry_seconds(value: str | None) -> float:
    if not value:
        return 0
    try:
        return min(3600.0, max(0.0, float(value)))
    except ValueError:
        try:
            deadline = parsedate_to_datetime(value).astimezone(UTC)
            return min(3600.0, max(0.0, (deadline - datetime.now(UTC)).total_seconds()))
        except (TypeError, ValueError):
            return 0


class ExchangeTrace:
    """Moments of one HTTP exchange, as HTTPX's trace extension reports them.

    The measured exchange runs from writing the request on an open connection to
    the complete answer; connection set-up comes before it. When the transport
    reports neither moment, the whole transport call is measured instead, which
    is wider and still contains the moment the provider read its clock."""

    SENT = "http11.send_request_headers.started"
    DONE = "http11.receive_response_body.complete"
    CONNECT = "connection.connect_tcp.started"

    def __init__(self) -> None:
        self.began = time.monotonic()
        self.began_wall_ms = time.time() * 1000
        self.connect: float | None = None
        self.sent: float | None = None
        self.sent_wall_ms: float | None = None
        self.done: float | None = None

    async def __call__(self, name: str, _info: dict) -> None:
        now = time.monotonic()
        if name == self.SENT and self.sent is None:
            self.sent, self.sent_wall_ms = now, time.time() * 1000
        elif name == self.DONE:
            self.done = now
        elif name == self.CONNECT and self.connect is None:
            self.connect = now

    def finish(self) -> dict[str, float | bool | None]:
        if self.sent is not None and self.done is not None and self.done >= self.sent:
            return {"sent_wall_ms": self.sent_wall_ms, "exchange_ms": (self.done - self.sent) * 1000,
                    "connect_ms": (self.sent - self.connect) * 1000 if self.connect is not None else 0.0,
                    "traced": True}
        return {"sent_wall_ms": self.began_wall_ms, "exchange_ms": (time.monotonic() - self.began) * 1000,
                "connect_ms": None, "traced": False}


class PublicBinance:
    # The only paths this client sends.
    PATHS = ("/api/v3/time", "/api/v3/exchangeInfo", "/api/v3/klines")
    HOST = REST_HOST
    TIME_PATH = "/api/v3/time"
    USER_AGENT = "adaptive-spot-lab-market/3"
    MAX_BODY = 2_097_152

    def __init__(self, own_ceiling: int = OWN_CEILING) -> None:
        self.budget = WeightBudget(own_ceiling)
        self.semaphore = asyncio.Semaphore(2)
        # The last clock check: the time of the sample that was used and the
        # parts of every sample.
        self.last_clock: dict | None = None
        self.last_sample: dict | None = None
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(5.0, connect=5.0, read=5.0),
            limits=httpx.Limits(max_connections=2, max_keepalive_connections=2),
            trust_env=False,
            follow_redirects=False,
            headers={"User-Agent": self.USER_AGENT, "Accept-Encoding": "identity"},
        )

    def bind(self, *, stop: asyncio.Event, report: Callable[[dict], Awaitable[None]]) -> None:
        """Let budget waits end when the worker stops, and report to the worker."""
        self.budget.stop = stop
        self.budget.report = report

    async def close(self) -> None:
        await self.client.aclose()

    async def get(self, path: str, parameters: dict[str, str | int], weight: int, *,
                  attempts: int = 5, deadline: float = 15.0, timing: dict | None = None) -> bytes:
        if path not in self.PATHS:
            raise ProviderUnavailable("provider_path_not_allowed")
        if any(key.lower() in {"signature", "timestamp", "apikey"} for key in parameters):
            raise ProviderUnavailable("private_request_forbidden")
        async with self.semaphore:
            for attempt in range(attempts):
                waited = await self.budget.reserve(weight, path)
                limited: tuple[int, float] | None = None
                try:
                    resolving = time.monotonic()
                    ip = await resolve_public_ip(self.HOST)
                    dns_ms = (time.monotonic() - resolving) * 1000
                    literal = f"[{ip}]" if ":" in ip else ip
                    trace = ExchangeTrace()
                    request = self.client.build_request(
                        "GET", f"https://{literal}{path}", params=parameters,
                        headers={"Host": self.HOST},
                        extensions={"sni_hostname": self.HOST, "trace": trace},
                    )
                    async with asyncio.timeout(deadline):
                        response = await self.client.send(request, stream=True)
                        try:
                            self.budget.observe_used(response.headers.get("X-MBX-USED-WEIGHT-1M"))
                            if response.status_code in (429, 418):
                                wait = max(retry_seconds(response.headers.get("Retry-After")), 1)
                                # No caller may send before the provider's deadline.
                                self.budget.block(wait)
                                limited = (response.status_code, wait)
                                raise ProviderUnavailable("provider_rate_limited", wait)
                            if response.is_redirect:
                                raise ProviderUnavailable("provider_redirect_rejected")
                            if response.status_code != 200:
                                raise ProviderUnavailable("provider_http_error")
                            chunks = []
                            size = 0
                            async for chunk in response.aiter_bytes():
                                size += len(chunk)
                                if size > self.MAX_BODY:
                                    raise ProviderUnavailable("provider_payload_too_large")
                                chunks.append(chunk)
                            body = b"".join(chunks)
                        finally:
                            await response.aclose()
                    if timing is not None:
                        timing.update(trace.finish(), wait_ms=waited * 1000, dns_ms=dns_ms)
                    return body
                except ProviderUnavailable:
                    if limited is not None:
                        await self.budget.tell({"kind": "backoff", "path": path, "status": limited[0],
                                                "retry_after_s": limited[1]})
                    raise
                except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                    if attempt == attempts - 1:
                        raise ProviderUnavailable("provider_rest_unavailable") from exc
                    await asyncio.sleep(min(60, 2**attempt + random.random()))
                    continue
        raise ProviderUnavailable("provider_rest_unavailable")

    async def clock(self) -> tuple[int, float, float]:
        """One clock sample: (server time, offset, uncertainty) in milliseconds.

        The uncertainty is half the time from writing the request to the complete
        answer. The budget wait, the DNS lookup and connection set-up come before
        that interval and say nothing about the clock."""
        timing: dict = {}
        raw = await self.get(self.TIME_PATH, {}, 1, attempts=1, deadline=CLOCK_SAMPLE_DEADLINE, timing=timing)
        data = decode_json(raw)
        if not isinstance(data, dict) or type(data.get("serverTime")) is not int:
            raise PayloadError("invalid_server_time")
        middle_ms = timing["sent_wall_ms"] + timing["exchange_ms"] / 2
        self.last_sample = {
            "at": datetime.fromtimestamp(middle_ms / 1000, UTC),
            "wait_ms": round(timing["wait_ms"], 1), "dns_ms": round(timing["dns_ms"], 1),
            "connect_ms": None if timing["connect_ms"] is None else round(timing["connect_ms"], 1),
            "exchange_ms": round(timing["exchange_ms"], 1), "traced": timing["traced"],
        }
        return data["serverTime"], data["serverTime"] - middle_ms, timing["exchange_ms"] / 2

    async def best_clock(self, samples: int = 3) -> tuple[int, float, float]:
        """Use the least uncertain of bounded independent provider clock samples.

        A sample whose request fails is dropped; the check needs one sample. A
        provider back-off ends the check."""
        if not 1 <= samples <= 5:
            raise ValueError("invalid_clock_sample_count")
        readings: list[tuple[tuple[int, float, float], dict]] = []
        parts: list[dict] = []
        failure: Exception | None = None
        for _ in range(samples):
            try:
                reading = await self.clock()
            except ProviderUnavailable as exc:
                if exc.code == "worker_stopping":
                    raise
                failure = exc
                parts.append({"failure": exc.code})
                if exc.code == "provider_rate_limited":
                    break
                continue
            except PayloadError as exc:
                failure = exc
                parts.append({"failure": str(exc)[:80]})
                continue
            readings.append((reading, self.last_sample))
            parts.append({key: value for key, value in self.last_sample.items() if key != "at"})
        self.last_clock = {"sampled_at": None, "samples": parts}
        if not readings:
            raise failure if failure is not None else ProviderUnavailable("provider_rest_unavailable")
        best, sample = min(readings, key=lambda item: item[0][2])
        self.last_clock["sampled_at"] = sample["at"]
        return best

    async def instrument(self) -> bytes:
        """``GET /api/v3/exchangeInfo?symbol=BTCUSDT``, weight 20. Its answer declares the IP's one-minute allowance,
        which sets the IP-wide guard."""
        raw = await self.get("/api/v3/exchangeInfo", {"symbol": market.SYMBOL}, 20, deadline=20.0)
        await self.adopt_allowance(raw)
        return raw

    async def adopt_allowance(self, raw: bytes) -> None:
        """Adopt the one-minute allowance an exchangeInfo answer declares, and report a change."""
        allowance = declared_request_weight(raw)
        if self.budget.declare(allowance):
            await self.budget.tell({"kind": "allowance", "allowance": allowance,
                                    "ceiling": self.budget.ceiling, "guard": self.budget.guard})

    async def klines(self, interval: str, start_ms: int, end_ms: int, limit: int) -> bytes:
        """``GET /api/v3/klines`` for BTCUSDT at ``1m`` or ``1d``: at most 1,000 rows, weight 2."""
        if interval not in ("1m", "1d") or not 1 <= limit <= market.KLINE_ROWS_MAX or start_ms < 0 \
                or end_ms <= start_ms:
            raise ValueError("invalid_kline_request")
        return await self.get("/api/v3/klines", {"symbol": market.SYMBOL, "interval": interval,
                                                 "startTime": start_ms, "endTime": end_ms, "limit": limit}, 2)

    async def connect_stream(self):
        """The one combined stream: the book's ten best levels every 100 ms and the 1-minute candle."""
        ip = await resolve_public_ip(STREAM_HOST)
        url = f"wss://{STREAM_HOST}:443/stream?" + urlencode({"streams": "/".join(market.STREAMS)})
        return connect(url, open_timeout=10, close_timeout=STREAM_CLOSE_TIMEOUT, max_size=262_144, max_queue=64,
                       ping_interval=20, ping_timeout=60, proxy=None, host=ip, port=443)
