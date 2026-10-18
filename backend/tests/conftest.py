import pytest

from app.core.config import Settings
from app.payments.memory import store as payment_store
from app.payments.mock_vic import reset as reset_vic
from app.services.repository import InMemoryRepository
from app.sessions.events import bus
from app.sessions.store import registry


@pytest.fixture(autouse=True)
def disable_live_gemini(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(
        "app.services.llm.get_settings",
        lambda: Settings(gemini_api_key=None, offline=False),
    )


@pytest.fixture(autouse=True)
def reset_singletons():
    registry.clear()
    bus.reset()
    payment_store.clear()
    reset_vic()
    InMemoryRepository.shared().clear()
    yield
    registry.clear()
    bus.reset()
    payment_store.clear()
    reset_vic()
    InMemoryRepository.shared().clear()
