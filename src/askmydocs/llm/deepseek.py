"""Provider DeepSeek (cloud, API compatible OpenAI)."""
from askmydocs.llm.openai_compatible import OpenAICompatibleProvider


class DeepSeekProvider(OpenAICompatibleProvider):
    """Genere des reponses via l'API DeepSeek (compatible OpenAI)."""

    ENV_VAR = "DEEPSEEK_API_KEY"
    DEFAULT_MODEL = "deepseek-chat"
    SUPPORTED_MODELS = ["deepseek-chat", "deepseek-reasoner"]
    BASE_URL = "https://api.deepseek.com"
