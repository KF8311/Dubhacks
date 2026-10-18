"""Run the whole demo path with no server, no database, and no network.

Usage (from repo root):
  backend\\.venv\\Scripts\\python.exe scripts\\replay_offline.py

Exit code 0 means the replay still matches the numbers the demo script quotes.
Exit code 1 means the demo drifted -- fix it before you present.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

os.environ["OFFLINE"] = "1"
os.environ["DEMO_MODE"] = "1"

from app.demo.replay import ReplayReport, replay  # noqa: E402

QUERY = "noise cancelling headphones"

# What the demo script says on stage. If the replay disagrees, the script is wrong.
EXPECTED = {
    "listings": 9,
    "trusted": 8,
    "caution": 0,
    "danger": 1,
    "danger_ids": ["lst_vln_xm5"],
    "picked_id": "lst_tgt_bsp",
    "median_cents": 37449,
    "savings_cents": 19450,
}


def format_report(report: ReplayReport) -> str:
    median = f"${report.median_cents / 100:.2f}" if report.median_cents else "n/a"
    savings = f"${report.savings_cents / 100:.2f}" if report.savings_cents else "n/a"
    lines = [
        f"query          {QUERY}",
        f"stage          {report.stage}",
        f"listings       {report.listings}",
        f"trusted        {report.trusted}",
        f"caution        {report.caution}",
        f"danger         {report.danger}  ({', '.join(report.danger_ids) or 'none'})",
        f"best pick      {report.picked_id}",
        f"median trusted {median}",
        f"savings        {savings}",
        "events         "
        + ", ".join(f"{name}={count}" for name, count in report.events.items()),
    ]
    return "\n".join(lines)


def drift(report: ReplayReport) -> list[str]:
    actual = {
        "listings": report.listings,
        "trusted": report.trusted,
        "caution": report.caution,
        "danger": report.danger,
        "danger_ids": report.danger_ids,
        "picked_id": report.picked_id,
        "median_cents": report.median_cents,
        "savings_cents": report.savings_cents,
    }
    return [
        f"{key}: expected {EXPECTED[key]!r}, got {actual[key]!r}"
        for key in EXPECTED
        if actual[key] != EXPECTED[key]
    ]


async def run() -> int:
    report = await replay(QUERY)
    print(format_report(report))

    problems = drift(report)
    if problems:
        print("\nDRIFT: the replay no longer matches the demo script:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("\nOK: offline replay matches the live demo numbers.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
