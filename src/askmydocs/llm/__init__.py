from askmydocs.config import LLM_PROVIDER
from askmydocs.types import SearchResult, RagResponse
from askmydocs.llm import ollama, gemini

_PROVIDERS = {"ollama": ollama, "gemini": gemini}


def generate_answer(
    question: str,
    results: list[SearchResult],
    provider: str | None = None,
    lang: str = "fr",
) -> RagResponse:
    name = provider or LLM_PROVIDER
    if name not in _PROVIDERS:
        raise ValueError(f"Provider inconnu : {name}")
    return _PROVIDERS[name].generate_answer(question, results, lang=lang)