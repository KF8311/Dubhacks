"""Copy repo ``data/`` into ``backend/data`` so Vercel functions can read fixtures."""

from __future__ import annotations

import shutil
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_DATA = BACKEND_ROOT.parent / "data"
BUNDLE_DATA = BACKEND_ROOT / "data"


def main() -> None:
    if not REPO_DATA.is_dir():
        raise SystemExit(f"missing catalog directory: {REPO_DATA}")
    shutil.copytree(REPO_DATA, BUNDLE_DATA, dirs_exist_ok=True)


if __name__ == "__main__":
    main()
