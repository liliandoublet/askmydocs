"""Orchestration du pipeline RAG complet.

Ce module est la façade du projet : il expose deux opérations de haut niveau
(`ingest` et `ask`) qui masquent toute la tuyauterie interne (loader, splitter,
embedder, vectorstore, llm).
"""
from pathlib import Path

from askmydocs.loader import load_document
from askmydocs.splitter import split_documents
from askmydocs.vectorstore import index_chunks, search, reset_collection
from askmydocs.llm import generate_answer
from askmydocs.types import RagResponse


def ingest(file_path: str | Path, reset: bool = False) -> int:
    """Ingère un document dans la base vectorielle.

    Pipeline : load → split → index.

    Args:
        file_path: chemin vers le fichier (PDF ou DOCX).
        reset: si True, vide la base avant d'indexer (repart de zéro).

    Returns:
        Le nombre de chunks indexés.
    """
    if reset:
        reset_collection()

    pages = load_document(Path(file_path))
    chunks = split_documents(pages)
    n = index_chunks(chunks)
    return n


def ask(question: str, provider: str | None = None, lang: str = "fr") -> RagResponse:
    """Pose une question au pipeline RAG.

    Pipeline : search → generate.

    Args:
        question: la question de l'utilisateur en langage naturel.
        lang: langue de la réponse ("fr" ou "en").

    Returns:
        Un RagResponse contenant la réponse et les sources utilisées.
    """
    results = search(question)
    return generate_answer(question, results, provider=provider, lang=lang)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print('Usage: uv run python -m src.askmydocs.rag <fichier> "<question>"')
        sys.exit(1)

    file_path = sys.argv[1]
    question = sys.argv[2]

    print(f"📥 Ingestion de : {Path(file_path).name}")
    n = ingest(file_path, reset=True)
    print(f"✅ {n} chunks indexés\n")

    print(f"❓ {question}\n")
    print("🤖 Réflexion...\n")
    response = ask(question)

    print("=" * 60)
    print(response["answer"])
    print("=" * 60)
    print("\n📚 Sources :")
    for s in response["sources"]:
        print(f"  • {s['source']} — page {s['page']} (score {s['score']})")