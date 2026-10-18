from app.domain.models import SearchSpec
from app.search.serpapi import listings_from_payload, merchant_host


def test_maps_merchant_product_url_to_domain():
    payload = {
        "shopping_results": [
            {
                "title": "Sony WH-1000XM5",
                "product_link": "https://www.bestbuy.com/site/sony/123.p",
                "link": "https://www.google.com/shopping/product/1",
                "source": "Best Buy",
                "extracted_price": 249.00,
                "thumbnail": "https://img.example/x.jpg",
            }
        ]
    }
    listings = listings_from_payload(payload, spec=SearchSpec(query="headphones"), limit=8)
    assert len(listings) == 1
    assert listings[0].merchant_domain == "bestbuy.com"
    assert listings[0].price_cents == 24900
    assert listings[0].source == "serpapi"
    assert listings[0].id.startswith("lst_")


def test_google_shopping_link_uses_known_retailer_source():
    payload = {
        "shopping_results": [
            {
                "title": "Market Pantry 100% Apple Juice",
                "product_link": "https://www.google.com/shopping/product/1",
                "source": "Target",
                "extracted_price": 3.69,
                "product_id": "juice1",
            },
            {
                "title": "Tree Top Apple Juice",
                "product_link": "https://www.google.com/shopping/product/2",
                "source": "Walmart - Deslepinky Goods",
                "extracted_price": 14.95,
                "product_id": "juice2",
            },
        ]
    }
    listings = listings_from_payload(payload, spec=SearchSpec(query="apple juice"), limit=8)
    assert [item.merchant_domain for item in listings] == ["target.com", "walmart.com"]
    assert listings[0].title.startswith("Market Pantry")
    assert listings[0].price_cents == 369


def test_rejects_google_hosted_and_empty_domains():
    payload = {
        "shopping_results": [
            {
                "title": "google hosted",
                "product_link": "https://www.google.com/shopping/product/1",
                "link": "https://google.com/x",
                "source": "Google",
                "extracted_price": 10,
            },
            {
                "title": "no url",
                "source": "Unknown",
                "extracted_price": 10,
            },
        ]
    }
    listings = listings_from_payload(payload, spec=SearchSpec(query="x"), limit=8)
    assert listings == []


def test_merchant_host_strips_www():
    assert merchant_host("https://www.Target.com/p/1") == "target.com"
