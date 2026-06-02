"""Génération de réponses avec Gemini, à partir du contexte récupéré."""
from functools import lru_cache

from google import genai

from askmydocs.config import GEMINI_API_KEY, LLM_MODEL
from askmydocs.types import SearchResult


SYSTEM_PROMPT = """Tu es un assistant qui répond à des questions sur des documents.

Méthode :
- Appuie-toi sur le contexte fourni ci-dessous pour répondre.
- Tu peux synthétiser, reformuler et relier les informations de plusieurs extraits.
- Si plusieurs extraits sont partiellement pertinents, fais de ton mieux pour en \
tirer une réponse utile, même partielle.
- Indique seulement si VRAIMENT aucun extrait n'a de rapport avec la question : \
"Je ne trouve pas cette information dans le document."
- Cite tes sources avec le numéro de page entre crochets, ex: [page 12].
- Réponds en français, de manière claire et structurée."""


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    """Crée le client Gemini (une seule fois, mis en cache)."""
    if not GEMINI_API_KEY:
        raise ValueError("❌ GEMINI_API_KEY manquante. Vérifie ton .env")
    return genai.Client(api_key=GEMINI_API_KEY)


def build_context(results: list[SearchResult]) -> str:
    """Met en forme les chunks récupérés en un bloc de contexte lisible.

    Chaque chunk est numéroté et annoté de sa source/page, pour que le
    modèle puisse citer correctement.

    Args:
        results: les chunks retrouvés par la recherche vectorielle.

    Returns:
        Une chaîne formatée prête à insérer dans le prompt.
    """
    blocks = []
    for i, r in enumerate(results, start=1):
        blocks.append(
            f"[Extrait {i} — source: {r['source']}, page {r['page']}]\n"
            f"{r['text']}"
        )
    return "\n\n".join(blocks)


def generate_answer(question: str, results: list[SearchResult]) -> str:
    """Génère une réponse à partir d'une question et des chunks récupérés.

    Args:
        question: la question de l'utilisateur.
        results: les chunks pertinents issus du vectorstore.

    Returns:
        La réponse rédigée par Gemini.
    """
    # Cas où la recherche n'a rien trouvé
    if not results:
        return "Je ne trouve pas cette information dans le document."

    context = build_context(results)

    # On assemble le prompt complet : consignes + contexte + question
    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"=== CONTEXTE ===\n{context}\n\n"
        f"=== QUESTION ===\n{question}"
    )

    client = get_client()
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=full_prompt,
    )

    return response.text


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from askmydocs.loader import load_document
    from askmydocs.splitter import split_documents
    from askmydocs.vectorstore import reset_collection, index_chunks, search

    if len(sys.argv) < 3:
        print("Usage: uv run python -m src.askmydocs.llm <fichier> \"<question>\"")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    question = sys.argv[2]

    # Pipeline complet : load → split → index → search → generate
    print("🧹 Réinitialisation de la collection...")
    reset_collection()

    print(f"📄 Chargement & indexation de : {file_path.name}")
    pages = load_document(file_path)
    chunks = split_documents(pages)
    index_chunks(chunks)
    print(f"✅ {len(chunks)} chunks indexés\n")

    print(f"🔎 Recherche des passages pertinents...")
    results = search(question)
    print(f"✅ {len(results)} extraits récupérés\n")

    print(f"❓ Question : {question}\n")
    print("🤖 Génération de la réponse avec Gemini...\n")
    answer = generate_answer(question, results)

    print("=" * 60)
    print(answer)
    print("=" * 60)
    print("\n📚 Sources utilisées :")
    for r in results:
        print(f"  • {r['source']} (page {r['page']}, score {r['score']})")