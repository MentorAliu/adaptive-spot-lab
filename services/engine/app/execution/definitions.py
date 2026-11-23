"""Canonical JSON and the SHA-256 of a frozen definition (M3's rule, kept by ExecPlan 0060).

A definition is hashed over its canonical JSON (sorted keys, no spaces, ASCII), so the stored row, the migration that
froze it and the code that reads it agree byte for byte. ``app.spot.definitions`` freezes the spot rule, policy and
cost this way; the earlier definitions (M3 to M11) stay in ``execution_definitions`` with their hashes.
"""

import hashlib
import json
from typing import Any


def canonical_json(definition: dict[str, Any]) -> str:
    return json.dumps(definition, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def definition_hash(definition: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(definition).encode("ascii")).hexdigest()
