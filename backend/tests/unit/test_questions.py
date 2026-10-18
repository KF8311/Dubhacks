from app.domain.models import Answer
from app.sessions.questions import build_search_spec


def test_budget_option_id_300_is_cents():
    spec = build_search_spec(
        "headphones",
        [Answer(question_id="q_budget", option_id="300")],
    )
    assert spec.budget_max_cents == 30000


def test_gemini_budget_option_id_with_prefix_still_parses():
    spec = build_search_spec(
        "headphones",
        [Answer(question_id="q_budget", option_id="under_150")],
    )
    assert spec.budget_max_cents == 15000
