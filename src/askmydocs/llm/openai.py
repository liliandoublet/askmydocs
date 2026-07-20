"""Provider OpenAI (cloud)."""
from askmydocs.llm.openai_compatible import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    """Genere des reponses via l'API OpenAI."""

    ENV_VAR = "OPENAI_API_KEY"
    DEFAULT_MODEL = "gpt-4o-mini"
    SUPPORTED_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4.1"]
    BASE_URL = None
