from app.core.config import Settings


def test_settings_read_gemini_api_key_from_process_env(monkeypatch, tmp_path):
    monkeypatch.setenv("GEMINI_API_KEY", "from-env")
    settings = Settings(_env_file=tmp_path / "unused.env")
    assert settings.gemini_api_key == "from-env"


def test_settings_read_gemini_api_key_from_env_file(monkeypatch, tmp_path):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("GEMINI_API_KEY=from-file\n", encoding="utf-8")
    settings = Settings(_env_file=env_file)
    assert settings.gemini_api_key == "from-file"
