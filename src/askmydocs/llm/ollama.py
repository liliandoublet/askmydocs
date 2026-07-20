"""Provider Ollama (local, RGPD)."""
import ollama

from askmydocs.config import OLLAMA_HOST
from askmydocs.llm.base import LLMProvider, LLMGenerationError


class OllamaProvider(LLMProvider):
    """Genere des reponses via un modele Ollama local."""

    DEFAULT_MODEL = "llama3.2"
    SUPPORTED_MODELS = ["llama3.2", "mistral", "mistral-nemo"]
    IS_LOCAL = True

    def __init__(self, model: str | None = None, host: str | None = None):
        self._model = model or self.DEFAULT_MODEL
        self._client = ollama.Client(host=host or OLLAMA_HOST)

    @property
    def model_name(self) -> str:
        return self._model

    def is_available(self) -> bool:
        try:
            self._client.list()
            return True
        except Exception:
            return False

    def generate(self, prompt: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat(model=self._model, messages=messages)
        except Exception as e:
            raise LLMGenerationError(
                f"Erreur lors de l'appel a Ollama (modele {self._model}) : {e}"
            ) from e
        return response.message.content
