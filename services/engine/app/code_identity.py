"""Code identity: one SHA-256 over the runtime ``app/`` source tree, computed at process start.

Each file contributes its path relative to ``app/`` and the SHA-256 of its bytes with
CRLF normalized to LF, so a Windows checkout and a Linux build of the same source
agree. Bytecode caches are ignored. Each spot run and each backtest records the identity of the code that
made it (ExecPlan 0060).
"""

import hashlib
from functools import lru_cache
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent


def compute(root: Path = APP_ROOT) -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*")
                   if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc")
    for path in files:
        content = path.read_bytes().replace(b"\r\n", b"\n")
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(content).hexdigest().encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


@lru_cache(maxsize=1)
def current() -> str:
    """This process's identity (the tree cannot change under a running container)."""
    return compute()
