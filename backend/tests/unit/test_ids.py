from app.core.ids import listing_id, new_id


def test_ids_are_prefixed():
    assert new_id("ses").startswith("ses_")


def test_listing_id_is_deterministic():
    assert listing_id("https://bestbuy.com/p/1") == listing_id("https://bestbuy.com/p/1")
