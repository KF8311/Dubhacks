from __future__ import annotations

import re

from pydantic import ValidationError

from app.domain.models import Answer, Question, SearchSpec
from app.search.catalog import catalog_covers

QUESTIONS: list[dict] = [
    {
        "id": "q_budget",
        "prompt": "What's your ceiling?",
        "kind": "single_select",
        "options": [
            {"id": "150", "label": "Under $150"},
            {"id": "300", "label": "$150–$300"},
            {"id": "600", "label": "$300–$600"},
        ],
        "allow_free_text": True,
    },
    {
        "id": "q_use",
        "prompt": "Where will you use them?",
        "kind": "single_select",
        "options": [
            {"id": "travel", "label": "Travel / commute"},
            {"id": "work", "label": "Work / calls"},
            {"id": "home", "label": "Home listening"},
        ],
        "allow_free_text": False,
    },
    {
        "id": "q_priority",
        "prompt": "What matters most?",
        "kind": "single_select",
        "options": [
            {"id": "anc", "label": "Noise cancelling"},
            {"id": "battery", "label": "Battery life"},
            {"id": "price", "label": "Lowest price"},
        ],
        "allow_free_text": False,
    },
]

GENERIC_QUESTIONS: list[dict] = [
    {
        "id": "q_budget",
        "prompt": "What's your ceiling?",
        "kind": "single_select",
        "options": [
            {"id": "150", "label": "Under $150"},
            {"id": "300", "label": "$150–$300"},
            {"id": "600", "label": "$300–$600"},
        ],
        "allow_free_text": True,
    },
    {
        "id": "q_use",
        "prompt": "Where will you use it?",
        "kind": "single_select",
        "options": [
            {"id": "home", "label": "Home"},
            {"id": "work", "label": "Work"},
            {"id": "travel", "label": "Travel"},
        ],
        "allow_free_text": True,
    },
    {
        "id": "q_priority",
        "prompt": "What matters most?",
        "kind": "single_select",
        "options": [
            {"id": "quality", "label": "Quality"},
            {"id": "brand", "label": "A brand I know"},
            {"id": "price", "label": "Lowest price"},
        ],
        "allow_free_text": True,
    },
]


def templates_for(query: str) -> list[dict]:
    if catalog_covers(query):
        return list(QUESTIONS)
    return list(GENERIC_QUESTIONS)


async def generate_questions(query: str) -> list[Question]:
    """Gemini when a key is present; templates on timeout, offline, or bad JSON."""
    from app.services.llm import generate_questions as llm_questions

    raw = await llm_questions(query, fallback=templates_for(query))
    try:
        return [Question.model_validate(item) for item in raw]
    except ValidationError:
        return [Question.model_validate(item) for item in templates_for(query)]


def _dollar_amounts(raw: str) -> list[int]:
    return [int(token.replace(",", "")) for token in re.findall(r"\d[\d,]*", raw)]


def _budget_bounds(raw: str | None) -> tuple[int | None, int | None]:
    """Return (min_cents, max_cents). A single number is a ceiling, not a floor."""
    if not raw:
        return None, None
    amounts = _dollar_amounts(raw)
    if not amounts:
        return None, None
    if len(amounts) == 1:
        return None, amounts[0] * 100
    return min(amounts) * 100, max(amounts) * 100


def _looks_like_budget(item: Answer) -> bool:
    key = (item.question_id or "").lower()
    raw = item.option_id or item.text
    if _budget_bounds(raw) == (None, None):
        return False
    if any(token in key for token in ("budget", "price", "ceiling", "cost")):
        return True
    if item.text and _dollar_amounts(item.text):
        return True
    return bool(item.option_id and item.option_id.isdigit())


def _typed_range(answers: list[Answer]) -> Answer | None:
    for item in answers:
        if item.text and len(_dollar_amounts(item.text)) >= 2:
            return item
    return None


def _budget_answer(answers: list[Answer]) -> Answer:
    typed = _typed_range(answers)
    if typed is not None:
        return typed
    by_id = {item.question_id: item for item in answers}
    if "q_budget" in by_id:
        return by_id["q_budget"]
    for item in answers:
        if _looks_like_budget(item):
            return item
    return Answer(question_id="q_budget")


def build_search_spec(query: str, answers: list[Answer]) -> SearchSpec:
    budget = _budget_answer(answers)
    budget_min_cents, budget_max_cents = _budget_bounds(budget.option_id or budget.text)
    return SearchSpec(
        query=query,
        budget_min_cents=budget_min_cents,
        budget_max_cents=budget_max_cents,
        category=None,
    )
