import pytest

from app.payments.memory import store as payment_store
from app.payments.mock_vic import reset as reset_vic
from app.sessions.events import bus
from app.sessions.store import registry


@pytest.fixture(autouse=True)
def reset_singletons():
    registry.clear()
    bus.reset()
    payment_store.clear()
    reset_vic()
    yield
    registry.clear()
    bus.reset()
    payment_store.clear()
    reset_vic()
