from askmydocs.config import LLM_PROVIDER
from askmydocs.types import SearchResult, RagResponse
from askmydocs.llm.factory import get_provider, PROVIDER_REGISTRY

__all__ = ["generate_answer", "get_provider", "PROVIDER_REGISTRY"]


def generate_answer(
    question: str,
    results: list[SearchResult],
    provider: str | None = None,
    model: str | None = None,
    lang: str = "fr",
) -> RagResponse:
    name = provider or LLM_PROVIDER
    return get_provider(name, model).generate_answer(question, results, lang=lang)