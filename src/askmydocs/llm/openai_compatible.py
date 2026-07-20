"""Base commune aux providers utilisant une API compatible OpenAI (OpenAI, DeepSeek, ...)."""
import os

from askmydocs.llm.base import LLMProvider, LLMGenerationError


class OpenAICompatibleProvider(LLMProvider):
    """Genere des reponses via une API compatible avec le SDK `openai`.

    Sous-classer et definir ENV_VAR, DEFAULT_MODEL, SUPPORTED_MODELS et,
    si necessaire, BASE_URL (None = API OpenAI officielle).
    """

    ENV_VAR: str
    DEFAULT_MODEL: str
    SUPPORTED_MODELS: list[str]
    BASE_URL: str | None = None

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
            from openai import OpenAI
            self._client = OpenAI(api_key=self._api_key, base_url=self.BASE_URL)
        return self._client

    def generate(self, prompt: str, system: str | None = None) -> str:
        if not self.is_available():
            raise LLMGenerationError(
                f"{type(self).__name__} indisponible : variable d'environnement "
                f"{self.ENV_VAR} manquante."
            )

        import openai as openai_sdk

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._get_client().chat.completions.create(
                model=self._model,
                messages=messages,
            )
        except openai_sdk.APIError as e:
            raise LLMGenerationError(
                f"Erreur lors de l'appel a {type(self).__name__} (modele {self._model}) : {e}"
            ) from e
        return response.choices[0].message.content
