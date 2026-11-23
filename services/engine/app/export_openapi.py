import json
import sys
from pathlib import Path

from app.main import app


def main() -> None:
    check = "--check" in sys.argv[1:]
    paths = [argument for argument in sys.argv[1:] if argument != "--check"]
    target = Path(paths[0]) if paths else Path(__file__).resolve().parents[1] / "openapi.json"
    rendered = json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"
    if check:
        if target.read_text(encoding="utf-8") != rendered:
            raise SystemExit("FastAPI OpenAPI schema is out of date")
        print("FastAPI OpenAPI schema matches")
    else:
        target.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
