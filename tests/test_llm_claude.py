"""Tests unitaires du provider Claude (mocké, aucun appel réseau réel)."""
from unittest.mock import MagicMock

import pytest

from askmydocs.llm.base import LLMGenerationError
from askmydocs.llm.claude import ClaudeProvider


def test_default_model():
    assert ClaudeProvider(api_key="fake-key").model_name == "claude-opus-4-8"


def test_supported_models_include_default():
    assert ClaudeProvider.DEFAULT_MODEL in ClaudeProvider.SUPPORTED_MODELS


def test_is_available_true_with_key():
    assert ClaudeProvider(api_key="fake-key").is_available() is True


def test_is_available_false_without_key(monkeypatch):
    """Sans clé API, is_available doit renvoyer False sans lever d'exception."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert ClaudeProvider(api_key=None).is_available() is False


def test_generate_returns_text(monkeypatch):
    """Cas nominal : le provider renvoie le texte du premier bloc de type text."""
    provider = ClaudeProvider(model="claude-haiku-4-5", api_key="fake-key")
    fake_block = MagicMock(type="text", text="Réponse générée.")
    fake_response = MagicMock(content=[fake_block])
    fake_client = MagicMock()
    fake_client.messages.create = MagicMock(return_value=fake_response)
    monkeypatch.setattr(provider, "_get_client", lambda: fake_client)

    answer = provider.generate("Question ?", system="Tu es un assistant.")

    assert answer == "Réponse générée."
    kwargs = fake_client.messages.create.call_args.kwargs
    assert kwargs["model"] == "claude-haiku-4-5"
    assert kwargs["system"] == "Tu es un assistant."
    assert kwargs["messages"] == [{"role": "user", "content": "Question ?"}]


def test_generate_without_key_raises_llm_generation_error(monkeypatch):
    """Sans clé API, generate doit lever une erreur explicite plutôt que de crasher plus loin."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    provider = ClaudeProvider(api_key=None)

    with pytest.raises(LLMGenerationError):
        provider.generate("Question ?")


def test_generate_wraps_api_error(monkeypatch):
    """Une erreur réseau ou API doit être traduite en LLMGenerationError explicite."""
    import anthropic

    provider = ClaudeProvider(api_key="fake-key")
    fake_client = MagicMock()
    fake_client.messages.create = MagicMock(
        side_effect=anthropic.APIConnectionError(request=MagicMock())
    )
    monkeypatch.setattr(provider, "_get_client", lambda: fake_client)

    with pytest.raises(LLMGenerationError):
        provider.generate("Question ?")
