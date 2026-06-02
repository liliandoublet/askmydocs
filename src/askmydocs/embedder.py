"""Génération d'embeddings (texte → vecteurs) avec sentence-transformers."""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from askmydocs.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Charge le modèle d'embedding (une seule fois, mis en cache).

    Le décorateur lru_cache garantit qu'on ne recharge pas le modèle
    à chaque appel : le premier appel le télécharge/charge en mémoire,
    les suivants réutilisent l'instance.

    Returns:
        L'instance SentenceTransformer prête à l'emploi.
    """
    print(f"⏳ Chargement du modèle d'embedding '{EMBEDDING_MODEL}'...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("✅ Modèle chargé")
    return model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Transforme une liste de textes en une liste de vecteurs.

    Utilisé pour indexer les chunks d'un document (traitement par batch,
    plus rapide qu'un par un).

    Args:
        texts: liste de chaînes à encoder.

    Returns:
        Liste de vecteurs (un par texte). Liste vide si entrée vide.
    """
    if not texts:
        return []

    model = get_model()
    # convert_to_numpy=True puis .tolist() → on retourne des listes Python
    # natives (plus simple à stocker dans ChromaDB qu'un array numpy)
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Transforme une seule question en vecteur.

    Utilisé au moment de la recherche : on encode la question de
    l'utilisateur pour la comparer aux chunks indexés.

    Args:
        query: la question de l'utilisateur.

    Returns:
        Le vecteur correspondant.
    """
    return embed_texts([query])[0]


if __name__ == "__main__":
    # Petit test de cohérence : des phrases proches doivent avoir
    # des vecteurs proches (similarité cosinus élevée).
    import numpy as np

    phrases = [
        "Le chat dort sur le canapé",
        "Le félin se repose tranquillement",
        "La bourse a chuté de 3% aujourd'hui",
    ]

    print(f"\n🧪 Test sur {len(phrases)} phrases\n")
    vectors = embed_texts(phrases)

    print(f"📐 Dimension d'un vecteur : {len(vectors[0])}")

    def cosine(a: list[float], b: list[float]) -> float:
        a, b = np.array(a), np.array(b)
        return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

    print("\n--- Similarités cosinus ---")
    print(f"'chat/canapé' vs 'félin/repose'  : {cosine(vectors[0], vectors[1]):.3f}  (doit être ÉLEVÉ)")
    print(f"'chat/canapé' vs 'bourse/chute'   : {cosine(vectors[0], vectors[2]):.3f}  (doit être FAIBLE)")