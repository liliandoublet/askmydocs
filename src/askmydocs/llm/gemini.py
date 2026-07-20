"""Provider Google Gemini (cloud)."""
import os

from askmydocs.llm.base import LLMProvider, LLMGenerationError


class GeminiProvider(LLMProvider):
    """Genere des reponses via l'API Google Gemini."""

    DEFAULT_MODEL = "gemini-2.5-flash"
    SUPPORTED_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]
    ENV_VAR = "GEMINI_API_KEY"

    def __init__(self, model: str | None = None, api_key: str | None = None):
        self._model = model or self.DEFAULT_MODEL
        self._api_key = api_key or os.getenv(self.ENV_VAR)
        self._client = None

    @property
    def model_name(self) -> str:
        return self._model

    def is_available(self) -> bool:
        return bool(self._api_key)

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def generate(self, prompt: str, system: str | None = None) -> str:
        if not self.is_available():
            raise LLMGenerationError(
                f"Gemini indisponible : variable d'environnement {self.ENV_VAR} manquante."
            )

        from google.genai import errors, types

        try:
            response = self._get_client().models.generate_content(
                model=self._model,
                config=types.GenerateContentConfig(system_instruction=system),
                contents=prompt,
            )
        except errors.APIError as e:
            raise LLMGenerationError(
                f"Erreur lors de l'appel a Gemini (modele {self._model}) : {e}"
            ) from e
        except Exception as e:
            raise LLMGenerationError(
                f"Erreur reseau lors de l'appel a Gemini (modele {self._model}) : {e}"
            ) from e
        return response.text
