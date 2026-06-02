"""Stockage et recherche vectorielle avec ChromaDB."""
from functools import lru_cache

import chromadb
from chromadb.api.models.Collection import Collection

from askmydocs.config import CHROMA_DIR, COLLECTION_NAME, TOP_K
from askmydocs.embedder import embed_texts, embed_query
from askmydocs.types import Chunk, SearchResult


@lru_cache(maxsize=1)
def get_collection() -> Collection:
    """Récupère (ou crée) la collection ChromaDB persistante.

    On configure l'espace de distance en 'cosine' : c'est la métrique
    adaptée aux embeddings sémantiques (mesure l'angle entre vecteurs,
    pas leur longueur).

    Returns:
        La collection ChromaDB prête à l'emploi.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def index_chunks(chunks: list[Chunk]) -> int:
    """Indexe une liste de chunks dans ChromaDB.

    Pour chaque chunk : calcule son embedding et le stocke avec son texte
    et ses métadonnées (source, page). L'ID combine source + chunk_id pour
    rester unique même avec plusieurs documents.

    Args:
        chunks: les chunks à indexer (issus du splitter).

    Returns:
        Le nombre de chunks indexés.
    """
    if not chunks:
        return 0

    collection = get_collection()

    # On calcule tous les embeddings d'un coup (batch = plus rapide)
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    # ID unique par chunk : "fichier.pdf_0", "fichier.pdf_1", ...
    ids = [f"{c['source']}_{c['chunk_id']}" for c in chunks]

    metadatas = [
        {"source": c["source"], "page": c["page"], "chunk_id": c["chunk_id"]}
        for c in chunks
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    return len(chunks)


def search(query: str, top_k: int = TOP_K) -> list[SearchResult]:
    """Recherche les chunks les plus pertinents pour une question.

    Args:
        query: la question de l'utilisateur (en langage naturel).
        top_k: nombre de chunks à retourner.

    Returns:
        Liste de SearchResult triés du plus pertinent au moins pertinent.
    """
    collection = get_collection()

    # Si la base est vide, pas la peine de chercher
    if collection.count() == 0:
        return []

    query_vector = embed_query(query)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
    )

    # ChromaDB renvoie des listes de listes (une par requête).
    # On n'a qu'une requête, donc on prend l'indice [0].
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    search_results: list[SearchResult] = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        search_results.append(SearchResult(
            text=doc,
            source=meta["source"],
            page=meta["page"],
            # distance cosinus → similarité : 1 - distance
            score=round(1 - dist, 3),
        ))

    return search_results


def reset_collection() -> None:
    """Vide complètement la collection (utile pour ré-indexer à zéro)."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass  # La collection n'existait pas, rien à faire
    # On vide le cache pour forcer la recréation au prochain appel
    get_collection.cache_clear()


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from askmydocs.loader import load_document
    from askmydocs.splitter import split_documents

    if len(sys.argv) < 2:
        print("Usage: uv run python -m src.askmydocs.vectorstore <fichier> [question]")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    question = sys.argv[2] if len(sys.argv) > 2 else None

    # On repart d'une base propre pour ce test
    print("🧹 Réinitialisation de la collection...")
    reset_collection()

    # Pipeline complet : load → split → index
    print(f"📄 Chargement de : {file_path.name}")
    pages = load_document(file_path)
    chunks = split_documents(pages)
    print(f"✂️  {len(chunks)} chunks à indexer")

    print("🔢 Indexation (calcul des embeddings)...")
    n = index_chunks(chunks)
    print(f"✅ {n} chunks indexés dans ChromaDB\n")

    # Recherche de démonstration
    if question is None:
        # Pas de question fournie → on prend les premiers mots du doc
        question = " ".join(chunks[0]["text"].split()[:5])
        print(f"ℹ️  Aucune question fournie, test avec : « {question} »\n")

    print(f"🔎 Recherche : « {question} »\n")
    results = search(question)

    if not results:
        print("❌ Aucun résultat")
    else:
        for i, r in enumerate(results, start=1):
            print(f"--- Résultat {i} (score: {r['score']}) ---")
            print(f"📄 {r['source']} | page {r['page']}")
            print(f"📝 {r['text'][:200]}...")
            print()