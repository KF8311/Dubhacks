from app.domain.models import Answer
from app.sessions.questions import build_search_spec


def test_budget_option_id_300_is_cents():
    spec = build_search_spec(
        "headphones",
        [Answer(question_id="q_budget", option_id="300")],
    )
    assert spec.budget_max_cents == 30000


def test_answering_use_does_not_force_the_audio_category():
    spec = build_search_spec(
        "energy drinks",
        [Answer(question_id="q_use", option_id="daily")],
    )
    assert spec.query == "energy drinks"
    assert spec.category is None


def test_gemini_budget_option_id_with_prefix_still_parses():
    spec = build_search_spec(
        "headphones",
        [Answer(question_id="q_budget", option_id="under_150")],
    )
    assert spec.budget_max_cents == 15000
    assert spec.budget_min_cents is None


def test_typed_budget_range_sets_min_and_max():
    spec = build_search_spec(
        "computers",
        [Answer(question_id="q_budget", text="1000 to 1200")],
    )
    assert spec.query == "computers"
    assert spec.budget_min_cents == 100_000
    assert spec.budget_max_cents == 120_000


def test_budget_text_on_a_nonstandard_question_id_still_parses():
    spec = build_search_spec(
        "computers",
        [Answer(question_id="price", text="1000 to 1200")],
    )
    assert spec.budget_min_cents == 100_000
    assert spec.budget_max_cents == 120_000


def test_typed_range_wins_over_a_budget_chip():
    spec = build_search_spec(
        "water bottles",
        [
            Answer(question_id="q_use", text="50-60"),
            Answer(question_id="q_budget", option_id="100"),
        ],
    )
    assert spec.budget_min_cents == 5_000
    assert spec.budget_max_cents == 6_000


def test_typed_ceiling_still_has_no_floor():
    spec = build_search_spec(
        "computers",
        [Answer(question_id="q_budget", text="under 1200")],
    )
    assert spec.budget_min_cents is None
    assert spec.budget_max_cents == 120_000
