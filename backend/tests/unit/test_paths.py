from pathlib import Path

from app.core.paths import _candidates, data_dir


def test_data_dir_prefers_backend_copy_when_repo_root_is_missing(tmp_path, monkeypatch):
    bundled = tmp_path / "backend" / "data"
    bundled.mkdir(parents=True)
    (bundled / "catalog.json").write_text("{}", encoding="utf-8")
    missing_root = tmp_path / "missing" / "data"
    monkeypatch.setattr(
        "app.core.paths._candidates",
        lambda: [missing_root, bundled, Path("/data")],
    )
    assert data_dir() == bundled


def test_data_dir_falls_back_to_repo_layout(tmp_path, monkeypatch):
    repo = tmp_path / "data"
    repo.mkdir()
    (repo / "catalog.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr("app.core.paths._candidates", lambda: [repo])
    assert data_dir() == repo


def test_candidates_include_data_beside_the_app_package(tmp_path):
    module_dir = _make_app_module_dir(tmp_path)

    candidates = _candidates(module_dir)

    assert module_dir.parents[1] / "data" in candidates


def test_data_dir_finds_data_beside_the_app_package(tmp_path):
    module_dir = _make_app_module_dir(tmp_path)
    packaged = module_dir.parents[1] / "data"
    packaged.mkdir()
    (packaged / "catalog.json").write_text("{}", encoding="utf-8")

    assert data_dir(module_dir) == packaged


def _make_app_module_dir(root: Path) -> Path:
    """Build the layout a Vercel function ships: <root>/app/core/paths.py."""
    module_dir = root / "app" / "core"
    module_dir.mkdir(parents=True)
    (module_dir / "paths.py").write_text("", encoding="utf-8")
    return module_dir


def test_data_dir_finds_data_two_levels_up(tmp_path):
    """<root>/backend/app/core with the catalog at <root>/backend/data."""
    module_dir = _make_app_module_dir(tmp_path / "backend")
    packaged = tmp_path / "backend" / "data"
    packaged.mkdir()
    (packaged / "catalog.json").write_text("{}", encoding="utf-8")

    assert data_dir(module_dir) == packaged


def test_data_dir_finds_data_at_the_repo_root(tmp_path):
    """<root>/backend/app/core with the only catalog at <root>/data."""
    module_dir = _make_app_module_dir(tmp_path / "backend")
    repo = tmp_path / "data"
    repo.mkdir()
    (repo / "catalog.json").write_text("{}", encoding="utf-8")

    assert data_dir(module_dir) == repo


def test_candidates_walk_up_from_the_module_dir(tmp_path):
    module_dir = _make_app_module_dir(tmp_path / "backend")

    candidates = _candidates(module_dir)

    for depth in (1, 2):
        assert module_dir.parents[depth] / "data" in candidates
