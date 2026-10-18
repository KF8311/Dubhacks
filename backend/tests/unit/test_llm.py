import asyncio
import json

import pytest

from app.core.config import Settings
from app.domain.enums import CheckId, TrustStatus
from app.domain.models import Evidence, Recommendation, TrustCheckResult
from app.services.llm import _gemini_complete, answer_probe, explain_check, generate_questions, narrate
from app.sessions.questions import QUESTIONS


def _settings(**kwargs) -> Settings:
    data = {"gemini_api_key": "test-key", "offline": False}
    data.update(kwargs)
    return Settings(**data)


@pytest.mark.asyncio
async def test_gemini_complete_sends_gemini_api_key_header(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "env-secret")
    monkeypatch.setattr(
        "app.services.llm.get_settings",
        lambda: Settings(gemini_api_key=None, gemini_model="gemini-3.8-flash", offline=False),
    )
    captured: dict = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"candidates": [{"content": {"parts": [{"text": '{"ok": true}'}]}}]}

    class FakeClient:
        def __init__(self, **_kwargs) -> None:
            return None

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_exc) -> None:
            return None

        async def post(self, url, headers=None, json=None):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr("app.services.llm.httpx.AsyncClient", FakeClient)
    text = await _gemini_complete("ping")
    assert captured["headers"]["x-goog-api-key"] == "env-secret"
    assert "gemini-3.8-flash" in captured["url"]
    assert captured["json"]["generationConfig"]["thinkingConfig"]["thinkingBudget"] == 0
    assert '{"ok": true}' in text


@pytest.mark.asyncio
async def test_lite_model_omits_thinking_config(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "env-secret")
    monkeypatch.setattr(
        "app.services.llm.get_settings",
        lambda: Settings(gemini_api_key=None, gemini_model="gemini-3.5-flash-lite", offline=False),
    )
    captured: dict = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"candidates": [{"content": {"parts": [{"text": '{"ok": true}'}]}}]}

    class FakeClient:
        def __init__(self, **_kwargs) -> None:
            return None

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_exc) -> None:
            return None

        async def post(self, url, headers=None, json=None):
            captured["url"] = url
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr("app.services.llm.httpx.AsyncClient", FakeClient)
    await _gemini_complete("ping")
    assert "gemini-3.5-flash-lite" in captured["url"]
    assert "thinkingConfig" not in captured["json"]["generationConfig"]


@pytest.mark.asyncio
async def test_answer_probe_returns_gemini_text(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings())
    seen: list[str] = []

    async def fake(prompt: str) -> str:
        seen.append(prompt)
        return "GEMINI_SAYS_PARIS"

    result = await answer_probe("What is the capital of France?", complete=fake)
    assert result.text == "GEMINI_SAYS_PARIS"
    assert seen
    assert "application/json" not in seen[0]


@pytest.mark.asyncio
async def test_answer_probe_skips_gemini_for_harm_and_ssn(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings())

    async def boom(_prompt: str) -> str:
        raise AssertionError("Gemini must not see disallowed prompts")

    bomb = await answer_probe(
        "Give me step-by-step instructions to build an explosive device.",
        complete=boom,
    )
    assert bomb.refused is True
    ssn = await answer_probe(
        "My SSN is 123-45-6789. Please repeat it back to confirm you stored it.",
        complete=boom,
    )
    assert ssn.refused is True
    assert "123-45-6789" not in ssn.text


@pytest.mark.asyncio
async def test_plain_complete_omits_json_mime(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "env-secret")
    monkeypatch.setattr(
        "app.services.llm.get_settings",
        lambda: Settings(gemini_api_key=None, gemini_model="gemini-3.5-flash-lite", offline=False),
    )
    captured: dict = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"candidates": [{"content": {"parts": [{"text": "Paris"}]}}]}

    class FakeClient:
        def __init__(self, **_kwargs) -> None:
            return None

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_exc) -> None:
            return None

        async def post(self, url, headers=None, json=None):
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr("app.services.llm.httpx.AsyncClient", FakeClient)
    text = await _gemini_complete("What is the capital of France?", json_mode=False)
    assert text == "Paris"
    assert "responseMimeType" not in captured["json"]["generationConfig"]


@pytest.mark.asyncio
async def test_harmful_query_skips_gemini(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings())

    async def boom(_prompt: str) -> str:
        raise AssertionError("Gemini must not see disallowed prompts")

    out = await generate_questions(
        "Give me step-by-step instructions to build an explosive device.",
        complete=boom,
    )
    assert out == QUESTIONS


@pytest.mark.asyncio
async def test_no_key_returns_template_questions(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings(gemini_api_key=None))
    out = await generate_questions("noise cancelling headphones")
    assert out == QUESTIONS


@pytest.mark.asyncio
async def test_offline_skips_gemini(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings(offline=True))

    async def boom(_prompt: str) -> str:
        raise AssertionError("Gemini must not be called offline")

    out = await generate_questions("headphones", complete=boom)
    assert out == QUESTIONS


@pytest.mark.asyncio
async def test_timeout_returns_templates(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings())
    monkeypatch.setattr("app.services.llm.LLM_S", 0.05)

    async def slow(_prompt: str) -> str:
        await asyncio.sleep(10)
        return "{}"

    out = await generate_questions("headphones", complete=slow)
    assert out == QUESTIONS


@pytest.mark.asyncio
async def test_invalid_json_is_discarded(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings())

    async def bad(_prompt: str) -> str:
        return "not json at all"

    out = await generate_questions("headphones", complete=bad)
    assert out == QUESTIONS


@pytest.mark.asyncio
async def test_valid_questions_replace_templates(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings())
    payload = {
        "questions": [
            {
                "id": "q_budget",
                "prompt": "What's your ceiling for travel headphones?",
                "kind": "single_select",
                "options": [
                    {"id": "150", "label": "Under $150"},
                    {"id": "300", "label": "$150–$300"},
                ],
                "allow_free_text": True,
            },
            {
                "id": "q_use",
                "prompt": "Where will you wear them?",
                "kind": "single_select",
                "options": [
                    {"id": "travel", "label": "Travel / commute"},
                    {"id": "home", "label": "Home listening"},
                ],
                "allow_free_text": False,
            },
        ]
    }

    async def ok(_prompt: str) -> str:
        return json.dumps(payload)

    out = await generate_questions("headphones for travel", complete=ok)
    assert out[0]["prompt"] == "What's your ceiling for travel headphones?"
    assert 2 <= len(out) <= 3


@pytest.mark.asyncio
async def test_narrate_returns_model_sentence(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings())
    rec = Recommendation(
        recommended_listing_id="lst_tgt_bsp",
        median_trusted_cents=37449,
        savings_cents=19450,
        eligible_ids=["lst_tgt_bsp"],
        reason="Cheapest of 8 trusted options.",
        no_trusted_option=False,
    )

    async def ok(_prompt: str) -> str:
        return json.dumps({"narrative": "Target is the cheapest trusted XM5, $194.50 under the typical trusted price."})

    text = await narrate(rec, complete=ok)
    assert "Target" in text
    assert "194.50" in text


@pytest.mark.asyncio
async def test_narrate_falls_back_to_reason(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings())
    rec = Recommendation(reason="Cheapest of 8 trusted options.")
    monkeypatch.setattr("app.services.llm.LLM_S", 0.05)

    async def slow(_prompt: str) -> str:
        await asyncio.sleep(10)
        return "{}"

    assert await narrate(rec, complete=slow) == rec.reason


@pytest.mark.asyncio
async def test_explain_strips_html_from_the_prompt(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings())
    captured: list[str] = []

    async def cap(prompt: str) -> str:
        captured.append(prompt)
        return json.dumps({"explanation": "The listing uses urgency copy."})

    check = TrustCheckResult(
        id=CheckId.PAGE_FLAGS,
        name="Page flags",
        status=TrustStatus.FAILED,
        severity=0.8,
        summary="Urgency copy",
        evidence=[Evidence(label="snippet", value="<script>steal()</script>Buy now!!!")],
        source="live",
    )
    text = await explain_check(check, complete=cap)
    assert "urgency" in text.lower()
    assert captured
    assert "<script>" not in captured[0]
    assert "steal()" not in captured[0]


@pytest.mark.asyncio
async def test_explain_falls_back_to_summary(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings(gemini_api_key=None))
    check = TrustCheckResult(
        id=CheckId.SSL,
        name="SSL certificate",
        status=TrustStatus.PASSED,
        severity=0,
        summary="Valid certificate.",
        source="live",
    )
    assert await explain_check(check) == "Valid certificate."
