"""Tests unitaires du provider Ollama (mocké, aucun appel réseau réel)."""
from unittest.mock import MagicMock

import pytest

from askmydocs.llm.base import LLMGenerationError
from askmydocs.llm.ollama import OllamaProvider


def _provider() -> OllamaProvider:
    return OllamaProvider(model="mistral", host="http://fake-host:11434")


def test_default_model_is_llama32():
    assert OllamaProvider().model_name == "llama3.2"


def test_custom_model_is_used():
    assert _provider().model_name == "mistral"


def test_supported_models_include_required_models():
    assert set(OllamaProvider.SUPPORTED_MODELS) >= {"llama3.2", "mistral", "mistral-nemo"}


def test_is_local():
    assert OllamaProvider.IS_LOCAL is True


def test_generate_returns_message_content():
    """Cas nominal : le provider renvoie le texte du message assistant."""
    provider = _provider()
    fake_response = MagicMock()
    fake_response.message.content = "Réponse générée."
    provider._client.chat = MagicMock(return_value=fake_response)

    answer = provider.generate("Question ?", system="Tu es un assistant.")

    assert answer == "Réponse générée."
    kwargs = provider._client.chat.call_args.kwargs
    assert kwargs["model"] == "mistral"
    assert kwargs["messages"][0] == {"role": "system", "content": "Tu es un assistant."}
    assert kwargs["messages"][1] == {"role": "user", "content": "Question ?"}


def test_generate_without_system_prompt():
    provider = _provider()
    fake_response = MagicMock()
    fake_response.message.content = "Réponse générée."
    provider._client.chat = MagicMock(return_value=fake_response)

    provider.generate("Question ?")

    kwargs = provider._client.chat.call_args.kwargs
    assert kwargs["messages"] == [{"role": "user", "content": "Question ?"}]


def test_is_available_true_when_service_reachable():
    provider = _provider()
    provider._client.list = MagicMock(return_value={"models": []})
    assert provider.is_available() is True


def test_is_available_false_when_service_unreachable():
    """Le service Ollama n'est pas joignable : is_available doit renvoyer False, pas crasher."""
    provider = _provider()
    provider._client.list = MagicMock(side_effect=ConnectionError("service down"))
    assert provider.is_available() is False


def test_generate_wraps_network_error():
    """Une erreur réseau lors de l'appel doit être traduite en LLMGenerationError explicite."""
    provider = _provider()
    provider._client.chat = MagicMock(side_effect=ConnectionError("boom"))

    with pytest.raises(LLMGenerationError):
        provider.generate("Question ?")
