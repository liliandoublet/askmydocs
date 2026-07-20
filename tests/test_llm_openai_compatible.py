"""Tests unitaires des providers OpenAI et DeepSeek (mockés, aucun appel réseau réel).

Les deux providers partagent la même implémentation (OpenAICompatibleProvider),
donc les mêmes cas sont vérifiés pour chacun via paramétrage.
"""
from unittest.mock import MagicMock

import pytest

from askmydocs.llm.base import LLMGenerationError
from askmydocs.llm.deepseek import DeepSeekProvider
from askmydocs.llm.openai import OpenAIProvider

# (classe, variable d'environnement, modèle par défaut, base_url attendue)
PROVIDERS = [
    (OpenAIProvider, "OPENAI_API_KEY", "gpt-4o-mini", None),
    (DeepSeekProvider, "DEEPSEEK_API_KEY", "deepseek-chat", "https://api.deepseek.com"),
]


@pytest.mark.parametrize("cls, env_var, default_model, base_url", PROVIDERS)
def test_default_model_and_base_url(cls, env_var, default_model, base_url):
    provider = cls(api_key="fake-key")
    assert provider.model_name == default_model
    assert provider.ENV_VAR == env_var
    assert provider.BASE_URL == base_url


@pytest.mark.parametrize("cls, env_var, default_model, base_url", PROVIDERS)
def test_is_available_true_with_key(cls, env_var, default_model, base_url):
    assert cls(api_key="fake-key").is_available() is True


@pytest.mark.parametrize("cls, env_var, default_model, base_url", PROVIDERS)
def test_is_available_false_without_key(cls, env_var, default_model, base_url, monkeypatch):
    """Sans clé API, is_available doit renvoyer False sans lever d'exception."""
    monkeypatch.delenv(env_var, raising=False)
    assert cls(api_key=None).is_available() is False


@pytest.mark.parametrize("cls, env_var, default_model, base_url", PROVIDERS)
def test_generate_returns_message_content(cls, env_var, default_model, base_url, monkeypatch):
    """Cas nominal : le provider renvoie le contenu du message assistant."""
    provider = cls(api_key="fake-key")
    fake_message = MagicMock(content="Réponse générée.")
    fake_choice = MagicMock(message=fake_message)
    fake_response = MagicMock(choices=[fake_choice])
    fake_client = MagicMock()
    fake_client.chat.completions.create = MagicMock(return_value=fake_response)
    monkeypatch.setattr(provider, "_get_client", lambda: fake_client)

    answer = provider.generate("Question ?", system="Tu es un assistant.")

    assert answer == "Réponse générée."
    kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == default_model
    assert kwargs["messages"][0] == {"role": "system", "content": "Tu es un assistant."}
    assert kwargs["messages"][1] == {"role": "user", "content": "Question ?"}


@pytest.mark.parametrize("cls, env_var, default_model, base_url", PROVIDERS)
def test_generate_without_key_raises_llm_generation_error(cls, env_var, default_model, base_url, monkeypatch):
    """Sans clé API, generate doit lever une erreur explicite plutôt que de crasher plus loin."""
    monkeypatch.delenv(env_var, raising=False)
    provider = cls(api_key=None)

    with pytest.raises(LLMGenerationError):
        provider.generate("Question ?")


@pytest.mark.parametrize("cls, env_var, default_model, base_url", PROVIDERS)
def test_generate_wraps_api_error(cls, env_var, default_model, base_url, monkeypatch):
    """Une erreur réseau ou API doit être traduite en LLMGenerationError explicite."""
    import openai

    provider = cls(api_key="fake-key")
    fake_client = MagicMock()
    fake_client.chat.completions.create = MagicMock(
        side_effect=openai.APIConnectionError(request=MagicMock())
    )
    monkeypatch.setattr(provider, "_get_client", lambda: fake_client)

    with pytest.raises(LLMGenerationError):
        provider.generate("Question ?")
