from __future__ import annotations

from app.domain.models import Answer, SearchSpec

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


async def generate_questions(query: str) -> list[dict]:
    """Templates only for now. LLM path is Task 5 optional and must not block create."""
    del query
    return list(QUESTIONS)


def build_search_spec(query: str, answers: list[Answer]) -> SearchSpec:
    by_id = {item.question_id: item for item in answers}
    budget_option = (by_id.get("q_budget") or Answer(question_id="q_budget")).option_id
    budget_max_cents = None
    if budget_option and budget_option.isdigit():
        budget_max_cents = int(budget_option) * 100
    use = (by_id.get("q_use") or Answer(question_id="q_use")).option_id
    category = "audio" if use else None
    return SearchSpec(query=query, budget_max_cents=budget_max_cents, category=category)
