"""Relative Markdown link check (files and GitHub-style heading anchors).

python tools/check_links.py <repository root>

Checks every ``[text](target)`` in tracked-looking Markdown files (``.cache``, ``node_modules``
and virtual environments excluded): a relative target must exist, and a ``#fragment`` must match a
heading slug in the target file (GitHub rules: lowercase, drop characters other than letters,
digits, spaces, hyphens and underscores, spaces to hyphens, ``-1``/``-2`` for repeats). External
links are not fetched. Prints one line per broken link and exits 1 if any.
"""

import re
import sys
from pathlib import Path

SKIP = {".cache", ".claude", "node_modules", ".venv", ".git", "test-results", ".output", "dist"}
# Pre-existing on main before ExecPlan 0015: absolute Windows paths in a historical run record, reported
# as warnings instead of rewriting that record.
KNOWN: set[tuple[str, int]] = set()
LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


def slug(heading: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # linked text only
    text = text.replace("`", "").lower()
    text = "".join(ch for ch in text if ch.isalnum() or ch in " -_")
    return text.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    found: set[str] = set()
    counts: dict[str, int] = {}
    fenced = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line):
            fenced = not fenced
            continue
        match = None if fenced else HEADING.match(line)
        if match:
            base = slug(match.group(2))
            count = counts.get(base, 0)
            found.add(base if count == 0 else f"{base}-{count}")
            counts[base] = count + 1
    return found


def main(root: Path) -> int:
    cache: dict[Path, set[str]] = {}
    broken = 0
    files = [path for path in root.rglob("*.md") if not SKIP.intersection(path.relative_to(root).parts)]
    for path in sorted(files):
        fenced = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if FENCE.match(line):
                fenced = not fenced
                continue
            if fenced:
                continue
            for target in LINK.findall(line):
                if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("//"):
                    continue  # external or mail link: not fetched
                file_part, _, fragment = target.partition("#")
                destination = path if not file_part else (path.parent / file_part).resolve()
                if not destination.exists():
                    location = (path.relative_to(root).as_posix(), number)
                    if location in KNOWN:
                        print(f"{location[0]}:{number}: warning, known pre-existing link {target}")
                        continue
                    print(f"{location[0]}:{number}: missing file {target}")
                    broken += 1
                    continue
                if fragment and destination.suffix == ".md":
                    known = cache.setdefault(destination, anchors(destination))
                    if fragment.lower() not in known:
                        print(f"{path.relative_to(root)}:{number}: missing anchor {target}")
                        broken += 1
    print(f"checked {len(files)} Markdown files; {broken} broken link(s)")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()))
