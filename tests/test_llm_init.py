"""Tests unitaires du point d'entrée askmydocs.llm.generate_answer."""
from unittest.mock import MagicMock

from askmydocs.llm import generate_answer
from askmydocs.llm.factory import PROVIDER_REGISTRY


def test_generate_answer_dispatches_to_requested_provider(monkeypatch):
    """generate_answer doit instancier le provider demandé via la factory et lui déléguer."""
    fake_provider = MagicMock()
    fake_provider.generate_answer.return_value = {"answer": "ok", "sources": []}
    fake_cls = MagicMock(return_value=fake_provider)
    monkeypatch.setitem(PROVIDER_REGISTRY, "ollama", fake_cls)

    response = generate_answer("Question ?", [], provider="ollama", model="llama3.2", lang="fr")

    assert response == {"answer": "ok", "sources": []}
    fake_cls.assert_called_once_with(model="llama3.2")
    fake_provider.generate_answer.assert_called_once_with("Question ?", [], lang="fr")


def test_generate_answer_falls_back_to_llm_provider_env_default(monkeypatch):
    """Sans provider explicite, le provider par défaut (LLM_PROVIDER) doit être utilisé."""
    fake_provider = MagicMock()
    fake_provider.generate_answer.return_value = {"answer": "ok", "sources": []}
    fake_cls = MagicMock(return_value=fake_provider)
    monkeypatch.setitem(PROVIDER_REGISTRY, "ollama", fake_cls)
    monkeypatch.setattr("askmydocs.llm.LLM_PROVIDER", "ollama")

    generate_answer("Question ?", [], lang="en")

    fake_cls.assert_called_once_with(model=None)
