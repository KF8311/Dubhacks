from app.search.catalog import catalog_covers, load_catalog
from app.trust.allowlist import load_allowlist


def test_catalog_has_hero_and_villain():
    listings = load_catalog()
    assert len(listings) >= 9
    domains = {listing.merchant_domain for listing in listings}
    assert "bestbuy.com" in domains
    assert any(domain.endswith(".shop") for domain in domains)


def test_catalog_only_covers_audio_queries():
    assert catalog_covers("noise cancelling headphones")
    assert catalog_covers("Sony WH-1000XM5")
    assert not catalog_covers("computers")
    assert not catalog_covers("water bottles")
    assert not catalog_covers("purple t shirt")


def test_allowlist_matches_subdomains_only_on_boundary():
    allowlist = load_allowlist()
    assert allowlist.matches("bestbuy.com")
    assert allowlist.matches("www.bestbuy.com")
    assert not allowlist.matches("bestbuy.com.evil.shop")
