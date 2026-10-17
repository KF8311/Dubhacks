from app.checks.base import CheckTarget
from app.checks.ssl_cert import SSLCertCheck
from app.domain.enums import CheckId, TrustStatus


def target(domain="bestbuy.com"):
    return CheckTarget("lst_1", f"https://{domain}/p", domain, "m", 100, None)


def cert(
    issuer="DigiCert Inc",
    valid=True,
    hostname_match=True,
    days_left=210,
):
    async def inspect(domain):
        return {
            "issuer": issuer,
            "valid": valid,
            "hostname_match": hostname_match,
            "days_left": days_left,
        }

    return inspect


async def test_free_cert_is_a_warning(monkeypatch):
    monkeypatch.setattr(
        "app.checks.ssl_cert.inspect_cert", cert(issuer="Let's Encrypt")
    )

    result = await SSLCertCheck().run(target("newstore.shop"), ctx=None)

    assert result.status == TrustStatus.WARNING
    assert result.severity == 0.4


async def test_invalid_cert_fails(monkeypatch):
    monkeypatch.setattr(
        "app.checks.ssl_cert.inspect_cert",
        cert(issuer="X", valid=False, hostname_match=False),
    )

    result = await SSLCertCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.FAILED
    assert result.severity == 0.8


async def test_hostname_mismatch_fails(monkeypatch):
    monkeypatch.setattr(
        "app.checks.ssl_cert.inspect_cert", cert(hostname_match=False)
    )

    assert (await SSLCertCheck().run(target(), ctx=None)).status == TrustStatus.FAILED


async def test_a_paid_certificate_passes(monkeypatch):
    monkeypatch.setattr("app.checks.ssl_cert.inspect_cert", cert())

    result = await SSLCertCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.PASSED
    assert result.severity == 0.0


async def test_a_certificate_about_to_expire_warns(monkeypatch):
    monkeypatch.setattr("app.checks.ssl_cert.inspect_cert", cert(days_left=9))

    result = await SSLCertCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.WARNING


async def test_an_unreachable_host_is_skipped(monkeypatch):
    async def unreachable(domain):
        return None

    monkeypatch.setattr("app.checks.ssl_cert.inspect_cert", unreachable)

    result = await SSLCertCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.SKIPPED
    assert result.source == "unavailable"


async def test_evidence_names_the_issuer(monkeypatch):
    monkeypatch.setattr(
        "app.checks.ssl_cert.inspect_cert", cert(issuer="DigiCert Inc")
    )

    result = await SSLCertCheck().run(target(), ctx=None)

    assert any(item.value == "DigiCert Inc" for item in result.evidence)


def test_check_identity():
    check = SSLCertCheck()

    assert check.id == CheckId.SSL
    assert check.display_name == "SSL certificate"
    assert check.timeout_s > 0
