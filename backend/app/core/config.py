from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    demo_mode: bool = True
    demo_pacing: bool = False
    offline: bool = False
    allowed_origins: str = "http://localhost:5173,http://localhost:5174"
    mongodb_uri: str | None = None
    mongodb_db: str = "sniff"
    gemini_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GEMINI_API_KEY", "gemini_api_key"),
    )
    gemini_model: str = "gemini-3.5-flash-lite"
    serpapi_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SERPAPI_KEY", "serpapi_key"),
    )
    # Google Shopping is geolocated: the same query prices and stocks
    # differently in Seattle than in a default (often East Coast) market.
    serpapi_location: str = "Seattle, Washington, United States"
    serpapi_gl: str = "us"
    serpapi_hl: str = "en"
    google_safe_browsing_key: str | None = None
    receipt_signing_secret: str = "dev-only-change-me"
    version: str = "0.9.0"
    max_listings: int = 9
    investigation_budget_s: float = 14.0
    check_concurrency: int = 8

    @field_validator(
        "mongodb_uri",
        "gemini_api_key",
        "serpapi_key",
        "google_safe_browsing_key",
        mode="before",
    )
    @classmethod
    def empty_str_to_none(cls, value: object) -> object:
        if value == "":
            return None
        return value

    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
