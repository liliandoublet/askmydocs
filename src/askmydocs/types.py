"""Types partagés du projet AskMyDocs.

Centraliser les structures de données ici permet :
- d'avoir une seule source de vérité sur le format des données qui circulent
- d'obtenir l'auto-complétion VS Code sur les dicts
- de détecter les typos sur les noms de clés
"""
from typing import TypedDict


class Page(TypedDict):
    """Une page (ou section) extraite d'un document brut.

    Produite par le module `loader`.
    """
    text: str         # Contenu textuel de la page
    source: str       # Nom du fichier d'origine (ex: "rapport.pdf")
    page: int         # Numéro de page (1-indexé)


class Chunk(TypedDict):
    """Un morceau de texte prêt à être indexé dans la vector DB.

    Produit par le module `splitter` à partir d'une `Page`.
    """
    text: str         # Le texte du chunk
    source: str       # Hérité de la page d'origine
    page: int         # Hérité de la page d'origine
    chunk_id: int     # Identifiant unique du chunk (utilisé par ChromaDB)

class SearchResult(TypedDict):
    """Un chunk retrouvé lors d'une recherche, avec son score de similarité.

    Produit par le module `vectorstore` lors d'une requête.
    """
    text: str         # Le texte du chunk retrouvé
    source: str       # Fichier d'origine
    page: int         # Page d'origine
    score: float      # Similarité cosinus (1.0 = identique, 0 = sans rapport)

class RagResponse(TypedDict):
    """Réponse complète du pipeline RAG : le texte généré + ses sources.

    Produite par le module `rag`, consommée par l'interface (Streamlit).
    """
    answer: str                      # La réponse rédigée par le LLM
    sources: list[SearchResult]      # Les chunks utilisés pour répondre