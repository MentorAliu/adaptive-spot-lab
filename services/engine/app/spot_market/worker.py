"""The market worker (ExecPlan 0060 section 4.5): BTCUSDT's spot feed (``app.spot_market.feed``) as the
``asl_market_worker`` identity, on the private database network and the market egress network only.

Off unless ``ASL_MARKET_ENABLED=1``; only the public provider is permitted. The feed retries its own faults, so its end
without a stop is a fault this process exits on, and the supervisor restarts it.
"""

import asyncio
import json
import logging
import os
import signal

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("asl.market_worker")


def event(code: str, **fields: object) -> None:
    logger.info(json.dumps({"event": code, **fields}, separators=(",", ":"), default=str))


async def run(stop: asyncio.Event) -> None:
    from app.db import get_engine
    from app.spot_market.feed import SpotFeed

    await SpotFeed(get_engine(), stop=stop).run()
    if not stop.is_set():
        event("market_worker_fatal", reason="SPOT_FEED_ENDED")
        raise RuntimeError("spot_feed_ended")


def main() -> None:
    if os.environ.get("ASL_MARKET_ENABLED", "0") != "1":
        event("market_collection_disabled")
        return
    if os.environ.get("ASL_MARKET_MODE", "PUBLIC") != "PUBLIC":
        raise RuntimeError("Only the public provider is permitted in this worker")
    os.environ["ASL_DB_ROLE"] = "market_worker"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    stop = asyncio.Event()
    for signame in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(signame, stop.set)
        except NotImplementedError:
            pass
    try:
        event("market_worker_started", feed="SPOT_BTCUSDT")
        loop.run_until_complete(run(stop))
    finally:
        loop.close()


if __name__ == "__main__":
    main()
