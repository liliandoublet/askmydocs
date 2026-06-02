"""Métriques d'évaluation pour le pipeline RAG."""
from askmydocs.types import SearchResult


def retrieval_hit_rate(
    results: list[SearchResult],
    relevant_pages: list[int],
) -> float:
    """1.0 si au moins une page récupérée est pertinente, 0.0 sinon."""
    if not results:
        return 0.0
    retrieved_pages = {r["page"] for r in results}
    return 1.0 if retrieved_pages & set(relevant_pages) else 0.0


def retrieval_precision(
    results: list[SearchResult],
    relevant_pages: list[int],
) -> float:
    """Proportion des chunks récupérés qui sont sur une page pertinente."""
    if not results:
        return 0.0
    relevant_set = set(relevant_pages)
    hits = sum(1 for r in results if r["page"] in relevant_set)
    return hits / len(results)


def answer_keyword_recall(answer: str, keywords: list[str]) -> float:
    """Proportion des mots-clés attendus présents dans la réponse générée."""
    if not keywords:
        return 0.0
    answer_lower = answer.lower()
    found = sum(1 for kw in keywords if kw.lower() in answer_lower)
    return found / len(keywords)


def is_refusal(answer: str) -> bool:
    """Détecte si le LLM a refusé de répondre."""
    refusal_markers = [
        "je ne trouve pas",
        "pas cette information",
        "aucune information",
    ]
    answer_lower = answer.lower()
    return any(marker in answer_lower for marker in refusal_markers)