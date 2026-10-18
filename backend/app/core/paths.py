import tempfile
from pathlib import Path

from app.data_bundle import DATA

_MODULE_DIR = Path(__file__).resolve().parent
_EMBEDDED_TMP = Path(tempfile.gettempdir()) / "sniff-data"


def _candidates(module_dir: Path | None = None) -> list[Path]:
    # app/core/paths.py → parents[1] is the app's root (backend/ locally,
    # the function root on Vercel), parents[2] is the repo root.
    module_dir = _MODULE_DIR if module_dir is None else module_dir
    app_root = module_dir.parents[1]
    repo_root = module_dir.parents[2]
    return [repo_root / "data", app_root / "data", Path("/data")]


def data_dir(module_dir: Path | None = None) -> Path:
    """Catalog/allowlist/fixtures live at repo `data/`, or `backend/data` on Vercel.

    A function packaged without its data files falls back to the embedded copy
    in `app/data_bundle.py`, written out to a temp directory on first use.
    """
    candidates = _candidates() if module_dir is None else _candidates(module_dir)
    for path in candidates:
        if (path / "catalog.json").is_file():
            return path
    materialized = _materialize_embedded()
    return materialized if materialized is not None else candidates[0]


def _materialize_embedded() -> Path | None:
    try:
        for relative, text in DATA.items():
            target = _EMBEDDED_TMP / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.is_file() or target.read_text(encoding="utf-8") != text:
                target.write_text(text, encoding="utf-8")
    except OSError:
        return None
    return _EMBEDDED_TMP
