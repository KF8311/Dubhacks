from app.core.logging import redact


def test_redact_strips_email_phone_and_card_like_strings():
    text = "shopper alex@example.com called 206-555-0100 card 4242 4242 4242 4242"
    out = redact(text)
    assert "alex@example.com" not in out
    assert "206-555-0100" not in out
    assert "4242 4242 4242 4242" not in out


def test_redact_strips_query_api_keys():
    text = "GET https://serpapi.com/search.json?engine=google_shopping&api_key=secret-value&num=9"
    out = redact(text)
    assert "secret-value" not in out
    assert "api_key=[redacted]" in out
