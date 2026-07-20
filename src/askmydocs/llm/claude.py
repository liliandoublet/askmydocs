"""Provider Anthropic Claude (cloud)."""
import os

from askmydocs.llm.base import LLMProvider, LLMGenerationError


class ClaudeProvider(LLMProvider):
    """Genere des reponses via l'API Anthropic Claude."""

    DEFAULT_MODEL = "claude-opus-4-8"
    SUPPORTED_MODELS = ["claude-opus-4-8", "claude-sonnet-5", "claude-haiku-4-5"]
    ENV_VAR = "ANTHROPIC_API_KEY"
    MAX_TOKENS = 1024

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
            import anthropic
            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    def generate(self, prompt: str, system: str | None = None) -> str:
        if not self.is_available():
            raise LLMGenerationError(
                f"Claude indisponible : variable d'environnement {self.ENV_VAR} manquante."
            )

        import anthropic

        kwargs = {}
        if system:
            kwargs["system"] = system

        try:
            response = self._get_client().messages.create(
                model=self._model,
                max_tokens=self.MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
        except anthropic.APIError as e:
            raise LLMGenerationError(
                f"Erreur lors de l'appel a Claude (modele {self._model}) : {e}"
            ) from e
        return next(block.text for block in response.content if block.type == "text")
