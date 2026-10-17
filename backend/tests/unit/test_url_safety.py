import pytest

from app.services.url_safety import validate_public_url


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/x",
        "https://localhost/x",
        "http://169.254.169.254/latest",
        "http://10.0.0.1/x",
        "http://192.168.1.5/x",
        "http://100.64.0.1/x",
        "http://[::1]/x",
        "file:///etc/passwd",
        "ftp://example.com/x",
        "http://example.com/x",
        "https://user:pass@example.com/x",
        "https://example.com:8443/x",
        "https://" + "a" * 2100 + ".com/x",
    ],
)
def test_rejects_unsafe_urls(url):
    with pytest.raises(ValueError):
        validate_public_url(url)


def test_rejects_a_domain_that_resolves_to_a_private_address(monkeypatch):
    monkeypatch.setattr(
        "app.services.url_safety._resolved_addresses",
        lambda host: ["10.1.2.3"],
    )

    with pytest.raises(ValueError):
        validate_public_url("https://looks-public.example/x")


def test_accepts_https():
    assert validate_public_url("https://bestbuy.com/p/1").startswith("https://")


def test_an_unresolvable_host_is_not_rejected(monkeypatch):
    """No DNS answer means no connection, which is a later, safer failure."""

    monkeypatch.setattr(
        "app.services.url_safety._resolved_addresses", lambda host: []
    )

    assert validate_public_url("https://bestbuy.com/p/1") == "https://bestbuy.com/p/1"
