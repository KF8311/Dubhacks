from pathlib import Path

from app.core.paths import data_dir


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
