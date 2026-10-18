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


def test_immersive_store_link_becomes_a_listing():
    from app.search.serpapi import listing_from_immersive

    listing = listing_from_immersive(
        {
            "product_results": {
                "title": "Puma Fast-R",
                "stores": [
                    {
                        "name": "Google",
                        "link": "https://www.google.com/shopping/product/1",
                        "extracted_price": 10,
                    },
                    {
                        "name": "PUMA",
                        "link": "https://us.puma.com/pd/fast-r",
                        "extracted_price": 199.99,
                    },
                ],
            }
        },
        fallback_title="shoe",
        image_url="https://img.example/a.jpg",
    )
    assert listing is not None
    assert listing.merchant_domain == "us.puma.com"
    assert listing.merchant_name == "PUMA"
    assert listing.price_cents == 19999
    assert listing.title == "Puma Fast-R"
    assert listing.source == "serpapi"


def test_google_only_results_follow_the_immersive_store(monkeypatch):
    import asyncio

    import httpx

    from app.search.serpapi import SerpAPIProvider

    calls: list[str] = []

    class FakeResponse:
        def __init__(self, payload: dict) -> None:
            self.payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return self.payload

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            del args, kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args) -> None:
            return None

        async def get(self, url, params=None, timeout=None):
            del timeout
            if params is not None:
                calls.append("shopping")
                return FakeResponse(
                    {
                        "shopping_results": [
                            {
                                "title": "Puma Fast-R",
                                "product_link": "https://www.google.com/shopping/product/1",
                                "extracted_price": 199.99,
                                "thumbnail": "https://img.example/a.jpg",
                                "serpapi_immersive_product_api": (
                                    "https://serpapi.com/search.json?engine=google_immersive_product"
                                    "&page_token=abc%2Bdef"
                                ),
                            }
                        ]
                    }
                )
            calls.append(url)
            assert "page_token=abc%2Bdef" in url
            assert "api_key=test-key" in url
            return FakeResponse(
                {
                    "product_results": {
                        "title": "Puma Fast-R",
                        "stores": [
                            {
                                "name": "PUMA",
                                "link": "https://us.puma.com/pd/fast-r",
                                "extracted_price": 199.99,
                            }
                        ],
                    }
                }
            )

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
    listings = asyncio.run(
        SerpAPIProvider(api_key="test-key").search(SearchSpec(query="running shoes"))
    )
    assert calls[0] == "shopping"
    assert len(listings) == 1
    assert listings[0].merchant_domain == "us.puma.com"


def test_source_hostname_is_used_when_product_link_is_google():
    payload = {
        "shopping_results": [
            {
                "title": "Purple cotton tee",
                "product_link": "https://www.google.com/shopping/product/9",
                "source": "oldnavy.gap.com",
                "extracted_price": 12.0,
                "product_id": "tee1",
            },
            {
                "title": "ASOS purple t-shirt",
                "product_link": "https://www.google.com/shopping/product/10",
                "source": "ASOS",
                "extracted_price": 18.0,
                "product_id": "tee2",
            },
        ]
    }
    listings = listings_from_payload(payload, spec=SearchSpec(query="purple t shirt"), limit=8)
    assert [item.merchant_domain for item in listings] == ["oldnavy.gap.com", "asos.com"]


def test_search_sends_price_bounds_to_serpapi(monkeypatch):
    import asyncio

    import httpx

    from app.search.serpapi import SerpAPIProvider

    captured: dict = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "shopping_results": [
                    {
                        "title": "ThinkPad",
                        "product_link": "https://www.bestbuy.com/site/thinkpad/1.p",
                        "source": "Best Buy",
                        "extracted_price": 1099.00,
                    }
                ]
            }

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            del args, kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args) -> None:
            return None

        async def get(self, url, params=None, timeout=None):
            del url, timeout
            captured.update(params or {})
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
    asyncio.run(
        SerpAPIProvider(api_key="test-key").search(
            SearchSpec(query="computers", budget_min_cents=100_000, budget_max_cents=120_000)
        )
    )
    assert captured["min_price"] == 1000
    assert captured["max_price"] == 1200
    assert captured["q"] == "computers $1000-1200"
