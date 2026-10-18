"""No fixture text may reach a generative model.

The page-flags and Reddit checks read raw HTML and post titles. CLAUDE.md
forbids sending either to an LLM, and the scoring is deterministic by design
(D-005). Today no module imports a model client; these tests fail if that
changes, or if the Gemini key stops being config-only.
"""

import ast
from pathlib import Path

APP = Path(__file__).resolve().parents[2] / "app"

GENERATIVE_PACKAGES = (
    "anthropic",
    "openai",
    "langchain",
    "litellm",
    "vertexai",
    "google.generativeai",
    "google.genai",
    "genai",
)


def _imported_modules(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            yield node.module or ""


def _is_generative(module: str) -> bool:
    return any(
        module == package or module.startswith(f"{package}.")
        for package in GENERATIVE_PACKAGES
    )


def test_no_module_imports_a_generative_client():
    offenders = [
        f"{path.relative_to(APP).as_posix()}: {module}"
        for path in sorted(APP.rglob("*.py"))
        for module in _imported_modules(
            ast.parse(path.read_text(encoding="utf-8"))
        )
        if _is_generative(module)
    ]

    assert offenders == []


def test_the_gemini_key_is_never_read_outside_config_and_llm():
    readers = [
        path.relative_to(APP).as_posix()
        for path in sorted(APP.rglob("*.py"))
        if path.name not in {"config.py", "llm.py"}
        and (
            "gemini_api_key" in path.read_text(encoding="utf-8")
            or "GEMINI_API_KEY" in path.read_text(encoding="utf-8")
        )
    ]

    assert readers == []


def test_scoring_and_checks_do_not_import_the_llm():
    trust_root = APP / "trust"
    checks_root = APP / "checks"
    payments_root = APP / "payments"
    offenders = []
    for path in sorted([*trust_root.rglob("*.py"), *checks_root.rglob("*.py"), *payments_root.rglob("*.py")]):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for module in _imported_modules(tree):
            if module == "app.services.llm" or module.startswith("app.services.llm."):
                offenders.append(path.relative_to(APP).as_posix())
    assert offenders == []
