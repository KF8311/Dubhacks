from app.checks.base import CheckTarget
from app.checks.domain_age import DomainAgeCheck
from app.domain.enums import CheckId, TrustStatus


def target(domain="newstore.shop"):
    return CheckTarget("lst_1", f"https://{domain}/p", domain, "m", 100, None)


def rdap(age_days, registrar="Namecheap", source_of_truth="rdap"):
    async def fake(domain):
        return {
            "age_days": age_days,
            "registrar": registrar,
            "source_of_truth": source_of_truth,
        }

    return fake


async def test_young_domain_fails(monkeypatch):
    monkeypatch.setattr("app.checks.domain_age.fetch_rdap", rdap(12))

    result = await DomainAgeCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.FAILED
    assert result.severity >= 0.9
    assert "12 days" in result.summary


async def test_old_domain_passes(monkeypatch):
    monkeypatch.setattr(
        "app.checks.domain_age.fetch_rdap", rdap(2000, "MarkMonitor")
    )

    result = await DomainAgeCheck().run(target("bestbuy.com"), ctx=None)

    assert result.status == TrustStatus.PASSED
    assert result.severity == 0.0


async def test_domain_between_one_and_three_months_warns(monkeypatch):
    monkeypatch.setattr("app.checks.domain_age.fetch_rdap", rdap(45))

    result = await DomainAgeCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.WARNING
    assert result.severity == 0.6


async def test_thirty_day_boundary_is_a_warning(monkeypatch):
    monkeypatch.setattr("app.checks.domain_age.fetch_rdap", rdap(30))

    assert (await DomainAgeCheck().run(target(), ctx=None)).status == TrustStatus.WARNING


async def test_whois_is_used_when_rdap_misses(monkeypatch):
    async def no_rdap(domain):
        return None

    async def whois(domain):
        return {"age_days": 3000, "registrar": "MarkMonitor", "source_of_truth": "whois"}

    monkeypatch.setattr("app.checks.domain_age.fetch_rdap", no_rdap)
    monkeypatch.setattr("app.checks.domain_age.fetch_whois", whois)

    result = await DomainAgeCheck().run(target("bestbuy.com"), ctx=None)

    assert result.status == TrustStatus.PASSED
    assert any(item.value == "whois" for item in result.evidence)


async def test_no_answer_from_either_source_is_skipped(monkeypatch):
    async def nothing(domain):
        return None

    monkeypatch.setattr("app.checks.domain_age.fetch_rdap", nothing)
    monkeypatch.setattr("app.checks.domain_age.fetch_whois", nothing)

    result = await DomainAgeCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.SKIPPED
    assert result.source == "unavailable"


async def test_villain_fixture_needs_no_network():
    """The demo's headline failure must be deterministic, network or not."""

    result = await DomainAgeCheck().run(
        target("premium-audio-deals.shop"), ctx=None
    )

    assert result.status == TrustStatus.FAILED
    assert result.source == "fixture"


async def test_evidence_names_age_registrar_and_source(monkeypatch):
    monkeypatch.setattr("app.checks.domain_age.fetch_rdap", rdap(1200, "MarkMonitor"))

    result = await DomainAgeCheck().run(target("bestbuy.com"), ctx=None)

    labels = {item.label for item in result.evidence}
    assert {"Age", "Registrar", "Source"} <= labels


def test_check_identity():
    check = DomainAgeCheck()

    assert check.id == CheckId.DOMAIN_AGE
    assert check.display_name == "Domain age"
    assert check.timeout_s > 0
