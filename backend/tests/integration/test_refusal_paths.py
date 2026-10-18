"""Every refusal the checkout route will have to return, against real demo data.

The orchestrator runs offline, the fixture-backed checks produce real scores,
and the payability guard is asked to pay. Each test names the code the browser
will have to render.
"""

from datetime import UTC, datetime, timedelta

import pytest

from app.core.config import Settings
from app.domain.models import SearchSpec
from app.payments.mandates import create_mandate
from app.payments.payability import PayabilityCode, PayabilityError, assert_payable
from app.sessions.events import EventBus
from app.sessions.orchestrator import SessionOrchestrator
from app.sessions.store import SessionRegistry

QUERY = "noise cancelling headphones"
HERO_ID = "lst_tgt_bsp"
VILLAIN_ID = "lst_vln_xm5"


@pytest.fixture
async def session():
    """One offline investigation, the same one the demo runs."""
    store, bus = SessionRegistry(), EventBus()
    orchestrator = SessionOrchestrator(store, bus, config=Settings(offline=True))
    created = store.create("refusal-test", QUERY)
    created.search_spec = SearchSpec(query=QUERY)
    await orchestrator._run(created.id)
    return store, created.id


def listing_for(store, session_id, listing_id):
    return next(item for item in store.listings(session_id) if item.id == listing_id)


def investigation_for(store, session_id, listing_id):
    investigation = store.investigation_for(session_id, listing_id)
    assert investigation is not None
    return investigation


def test_the_real_hero_is_payable(session):
    store, session_id = session
    listing = listing_for(store, session_id, HERO_ID)
    investigation = investigation_for(store, session_id, HERO_ID)
    mandate = create_mandate(listing, max_amount_cents=listing.price_cents)

    assert_payable(investigation, listing, mandate, now=datetime.now(UTC))


def test_the_real_villain_is_refused(session):
    store, session_id = session
    listing = listing_for(store, session_id, VILLAIN_ID)
    investigation = investigation_for(store, session_id, VILLAIN_ID)
    mandate = create_mandate(listing, max_amount_cents=listing.price_cents)

    with pytest.raises(PayabilityError) as error:
        assert_payable(investigation, listing, mandate, now=datetime.now(UTC))

    assert error.value.code == PayabilityCode.MERCHANT_NOT_TRUSTED
    assert error.value.details["verdict"] == "danger"


def test_a_trusted_listing_cannot_exceed_the_cap(session):
    """The cap is checked after the verdict, so this pins the second door too."""
    store, session_id = session
    listing = listing_for(store, session_id, HERO_ID)
    investigation = investigation_for(store, session_id, HERO_ID)
    mandate = create_mandate(listing, max_amount_cents=listing.price_cents + 5000)

    expensive = listing.model_copy(update={"price_cents": listing.price_cents + 5001})

    with pytest.raises(PayabilityError) as error:
        assert_payable(investigation, expensive, mandate, now=datetime.now(UTC))

    assert error.value.code == PayabilityCode.AMOUNT_EXCEEDS_CAP


def test_a_real_investigation_goes_stale(session):
    store, session_id = session
    listing = listing_for(store, session_id, HERO_ID)
    investigation = investigation_for(store, session_id, HERO_ID)
    mandate = create_mandate(listing, max_amount_cents=listing.price_cents)

    with pytest.raises(PayabilityError) as error:
        assert_payable(
            investigation,
            listing,
            mandate,
            now=investigation.created_at + timedelta(minutes=31),
        )

    assert error.value.code == PayabilityCode.INVESTIGATION_STALE
