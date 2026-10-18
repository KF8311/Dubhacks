from pathlib import Path

_MODULE_DIR = Path(__file__).resolve().parent


def _candidates(module_dir: Path | None = None) -> list[Path]:
    # app/core/paths.py → parents[1] is the app's root (backend/ locally,
    # the function root on Vercel), parents[2] is the repo root.
    module_dir = _MODULE_DIR if module_dir is None else module_dir
    app_root = module_dir.parents[1]
    repo_root = module_dir.parents[2]
    return [repo_root / "data", app_root / "data", Path("/data")]


def data_dir(module_dir: Path | None = None) -> Path:
    """Catalog/allowlist/fixtures live at repo `data/`, or `backend/data` on Vercel."""
    candidates = _candidates() if module_dir is None else _candidates(module_dir)
    for path in candidates:
        if (path / "catalog.json").is_file():
            return path
    return candidates[0]
