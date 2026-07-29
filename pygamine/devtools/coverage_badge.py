"""Turns coverage.json (from `coverage json`) into a shields.io endpoint
badge JSON file, committed to a host project's repo so its README's badge
stays current without any external service/account.

Installed as the `pygamine-coverage-badge` console script (see
pyproject.toml's [project.scripts]) so every host project's CI can run
`uv run pygamine-coverage-badge` instead of keeping its own copy of this
script -- it was previously duplicated byte-for-byte across five sibling
projects. Run after the test suite, from the host project's repo root:

    uv run --group dev pytest tests/ --cov --cov-report=json -q
    uv run pygamine-coverage-badge
"""

from __future__ import annotations

import json
from pathlib import Path


def badge_color(percent: float) -> str:
    if percent < 50:
        return "red"
    if percent < 80:
        return "yellow"
    return "brightgreen"


def main() -> None:
    totals = json.loads(Path("coverage.json").read_text(encoding="utf-8"))["totals"]
    percent = round(totals["percent_covered"])

    badge = {
        "schemaVersion": 1,
        "label": "coverage",
        "message": f"{percent}%",
        "color": badge_color(percent),
    }

    out = Path(".github/badges/coverage.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(badge, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}: {badge}")


if __name__ == "__main__":
    main()
