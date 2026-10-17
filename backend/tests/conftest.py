import pytest

from app.sessions.events import bus
from app.sessions.store import registry


@pytest.fixture(autouse=True)
def reset_singletons():
    registry.clear()
    bus.reset()
    yield
    registry.clear()
    bus.reset()
