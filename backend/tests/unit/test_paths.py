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


def test_data_dir_materializes_the_embedded_bundle_when_no_files_exist(
    tmp_path, monkeypatch
):
    """A function that ships without data files still has to serve the catalog."""
    monkeypatch.setattr("app.core.paths._candidates", lambda: [tmp_path / "nope"])
    monkeypatch.setattr("app.core.paths._EMBEDDED_TMP", tmp_path / "embedded")

    resolved = data_dir()

    assert (resolved / "catalog.json").is_file()
    assert (resolved / "allowlist.json").is_file()


def test_embedded_bundle_matches_the_repo_data():
    """Editing data/ without rerunning bundle_data.py would ship stale fixtures."""
    from app.data_bundle import DATA

    repo_data = Path(__file__).resolve().parents[3] / "data"
    on_disk = {
        path.relative_to(repo_data).as_posix(): path.read_text(encoding="utf-8")
        for path in repo_data.rglob("*")
        if path.is_file()
    }
    assert DATA == on_disk
