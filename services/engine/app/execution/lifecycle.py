"""Deterministic identities (PAPER_EXECUTION.md): the same events give the same row IDs (M3's rule, kept by
ExecPlan 0060 for the spot account's records)."""

import hashlib
from uuid import NAMESPACE_URL, UUID, uuid5

_NAMESPACE = uuid5(NAMESPACE_URL, "https://adaptive-spot-lab.local/m3/execution")
_NAMESPACE_BYTES = _NAMESPACE.bytes
# The RFC 4122 variant and version 5 bits, as ``UUID(bytes=..., version=5)`` sets them.
_V5_CLEAR = ~((0xC000 << 48) | (0xF000 << 64))
_V5_SET = (0x8000 << 48) | (5 << 76)


def stable_id(kind: str, *parts: object) -> UUID:
    """Deterministic UUIDv5 so the same events produce byte-comparable rows."""
    name = kind + ":" + "|".join(str(part) for part in parts)
    digest = hashlib.sha1(_NAMESPACE_BYTES + name.encode("utf-8")).digest()
    return UUID(int=(int.from_bytes(digest[:16]) & _V5_CLEAR) | _V5_SET)
