"""Point d'entree unique pour instancier un provider LLM."""
from askmydocs.llm.base import LLMProvider
from askmydocs.llm.ollama import OllamaProvider
from askmydocs.llm.gemini import GeminiProvider
from askmydocs.llm.claude import ClaudeProvider
from askmydocs.llm.openai import OpenAIProvider
from askmydocs.llm.deepseek import DeepSeekProvider

PROVIDER_REGISTRY: dict[str, type[LLMProvider]] = {
    "ollama": OllamaProvider,
    "gemini": GeminiProvider,
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "deepseek": DeepSeekProvider,
}


def get_provider(name: str, model: str | None = None) -> LLMProvider:
    """Instancie le provider `name`, avec le modele `model` si precise."""
    if name not in PROVIDER_REGISTRY:
        raise ValueError(f"Provider inconnu : {name}")
    return PROVIDER_REGISTRY[name](model=model)
