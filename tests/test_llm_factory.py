"""Tests unitaires de la factory de providers LLM."""
import pytest

from askmydocs.llm.claude import ClaudeProvider
from askmydocs.llm.deepseek import DeepSeekProvider
from askmydocs.llm.factory import PROVIDER_REGISTRY, get_provider
from askmydocs.llm.gemini import GeminiProvider
from askmydocs.llm.ollama import OllamaProvider
from askmydocs.llm.openai import OpenAIProvider


@pytest.mark.parametrize(
    "name, expected_cls",
    [
        ("ollama", OllamaProvider),
        ("gemini", GeminiProvider),
        ("claude", ClaudeProvider),
        ("openai", OpenAIProvider),
        ("deepseek", DeepSeekProvider),
    ],
)
def test_get_provider_returns_correct_class(name, expected_cls):
    assert isinstance(get_provider(name), expected_cls)


def test_get_provider_passes_model():
    provider = get_provider("claude", model="claude-haiku-4-5")
    assert provider.model_name == "claude-haiku-4-5"


def test_get_provider_uses_default_model_when_none():
    provider = get_provider("ollama")
    assert provider.model_name == OllamaProvider.DEFAULT_MODEL


def test_get_provider_unknown_raises_value_error():
    with pytest.raises(ValueError, match="Provider inconnu"):
        get_provider("does-not-exist")


def test_registry_contains_all_expected_providers():
    assert set(PROVIDER_REGISTRY.keys()) == {"ollama", "gemini", "claude", "openai", "deepseek"}
