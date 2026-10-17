from app.core.logging import redact


def test_redact_strips_email_phone_and_card_like_strings():
    text = "shopper alex@example.com called 206-555-0100 card 4242 4242 4242 4242"
    out = redact(text)
    assert "alex@example.com" not in out
    assert "206-555-0100" not in out
    assert "4242 4242 4242 4242" not in out
