"""Interface commune aux providers LLM."""
from abc import ABC, abstractmethod

from askmydocs.types import SearchResult, RagResponse
from askmydocs.llm.prompt import get_system_prompt, build_context


class LLMError(Exception):
    """Erreur de base pour tout ce qui touche a la generation LLM."""


class LLMGenerationError(LLMError):
    """Levee quand un provider echoue a generer une reponse (reseau ou API)."""


class LLMProvider(ABC):
    """Interface commune a tous les providers LLM (local ou cloud)."""

    #: True si le provider tourne en local (aucune donnee ne quitte la machine).
    IS_LOCAL: bool = False

    @abstractmethod
    def generate(self, prompt: str, system: str | None = None) -> str:
        """Genere une reponse texte a partir d'un prompt (et d'un system prompt optionnel)."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Nom du modele utilise par ce provider."""

    @abstractmethod
    def is_available(self) -> bool:
        """Indique si le provider est utilisable (service joignable, cle API presente, etc.)."""

    def generate_answer(
        self,
        question: str,
        results: list[SearchResult],
        lang: str = "fr",
    ) -> RagResponse:
        """Construit le prompt RAG (contexte + question) et genere la reponse."""
        context = build_context(results)
        system = get_system_prompt(lang)
        ctx_label = "Contexte" if lang == "fr" else "Context"
        prompt = f"{ctx_label} :\n{context}\n\nQuestion : {question}"
        answer = self.generate(prompt, system=system)
        return {"answer": answer, "sources": results}
