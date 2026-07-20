"""Tests unitaires de la classe de base LLMProvider."""
from askmydocs.llm.base import LLMProvider


class _FakeProvider(LLMProvider):
    """Provider minimal pour tester la logique commune de generate_answer."""

    def __init__(self):
        self.received_prompt = None
        self.received_system = None

    def generate(self, prompt, system=None):
        self.received_prompt = prompt
        self.received_system = system
        return "Réponse fictive."

    @property
    def model_name(self):
        return "fake-model"

    def is_available(self):
        return True


def test_generate_answer_builds_prompt_and_wraps_response():
    """generate_answer doit construire le contexte, appeler generate, et renvoyer un RagResponse."""
    provider = _FakeProvider()
    results = [
        {"text": "Le délai est de 72 heures.", "source": "doc.pdf", "page": 5, "score": 0.9}
    ]

    response = provider.generate_answer("Quel est le délai ?", results, lang="fr")

    assert response == {"answer": "Réponse fictive.", "sources": results}
    assert "Contexte" in provider.received_prompt
    assert "[page 5]" in provider.received_prompt
    assert "Quel est le délai ?" in provider.received_prompt
    assert provider.received_system is not None


def test_generate_answer_uses_english_context_label():
    """En anglais, le libellé du contexte doit être 'Context' et non 'Contexte'."""
    provider = _FakeProvider()
    results = [{"text": "72 hours.", "source": "doc.pdf", "page": 5, "score": 0.9}]

    provider.generate_answer("What is the deadline?", results, lang="en")

    assert "Context" in provider.received_prompt
    assert "Contexte" not in provider.received_prompt
