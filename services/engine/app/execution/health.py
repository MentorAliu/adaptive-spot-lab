"""Container healthcheck: the worker wrote a heartbeat within the last 15 seconds."""

import json
import sys
import time

from app.execution.worker import HEARTBEAT


def main() -> int:
    try:
        beat = json.loads(HEARTBEAT.read_text())
    except (OSError, ValueError):
        return 1
    return 0 if time.time() - float(beat.get("at", 0)) <= 15 else 1


if __name__ == "__main__":
    sys.exit(main())
