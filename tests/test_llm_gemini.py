"""Tests unitaires du provider Gemini (mocké, aucun appel réseau réel)."""
from unittest.mock import MagicMock

import pytest

from askmydocs.llm.base import LLMGenerationError
from askmydocs.llm.gemini import GeminiProvider


def test_default_model():
    assert GeminiProvider(api_key="fake-key").model_name == "gemini-2.5-flash"


def test_is_available_true_with_key():
    assert GeminiProvider(api_key="fake-key").is_available() is True


def test_is_available_false_without_key(monkeypatch):
    """Sans clé API, is_available doit renvoyer False sans lever d'exception."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert GeminiProvider(api_key=None).is_available() is False


def test_generate_returns_text(monkeypatch):
    """Cas nominal : le provider renvoie le texte de la réponse."""
    provider = GeminiProvider(api_key="fake-key")
    fake_response = MagicMock()
    fake_response.text = "Réponse générée."
    fake_client = MagicMock()
    fake_client.models.generate_content = MagicMock(return_value=fake_response)
    monkeypatch.setattr(provider, "_get_client", lambda: fake_client)

    answer = provider.generate("Question ?", system="Tu es un assistant.")

    assert answer == "Réponse générée."
    kwargs = fake_client.models.generate_content.call_args.kwargs
    assert kwargs["model"] == "gemini-2.5-flash"
    assert kwargs["contents"] == "Question ?"


def test_generate_without_key_raises_llm_generation_error(monkeypatch):
    """Sans clé API, generate doit lever une erreur explicite plutôt que de crasher plus loin."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    provider = GeminiProvider(api_key=None)

    with pytest.raises(LLMGenerationError):
        provider.generate("Question ?")


def test_generate_wraps_api_error(monkeypatch):
    """Une erreur API doit être traduite en LLMGenerationError explicite."""
    from google.genai import errors

    provider = GeminiProvider(api_key="fake-key")
    fake_client = MagicMock()
    fake_client.models.generate_content = MagicMock(
        side_effect=errors.APIError(500, {"message": "boom"})
    )
    monkeypatch.setattr(provider, "_get_client", lambda: fake_client)

    with pytest.raises(LLMGenerationError):
        provider.generate("Question ?")
