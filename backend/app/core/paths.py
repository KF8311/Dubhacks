from pathlib import Path

_MODULE_DIR = Path(__file__).resolve().parent


def _candidates() -> list[Path]:
    # app/core/paths.py → parents[2] is backend/, parents[3] is the repo root.
    backend_root = _MODULE_DIR.parents[2]
    repo_root = _MODULE_DIR.parents[3]
    return [repo_root / "data", backend_root / "data", Path("/data")]


def data_dir() -> Path:
    """Catalog/allowlist/fixtures live at repo `data/`, or `backend/data` on Vercel."""
    for path in _candidates():
        if (path / "catalog.json").is_file():
            return path
    return _candidates()[0]
