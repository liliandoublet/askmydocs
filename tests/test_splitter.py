"""Tests unitaires du module splitter."""
import pytest

from askmydocs.splitter import split_documents


def test_split_creates_multiple_chunks_from_long_text():
    """Un texte long doit produire plusieurs chunks."""
    pages = [{
        "text": "Ceci est un test. " * 200,  # ~3600 caractères
        "source": "test.pdf",
        "page": 1,
    }]
    chunks = split_documents(pages, chunk_size=500, chunk_overlap=50)

    assert len(chunks) > 1
    assert all(c["source"] == "test.pdf" for c in chunks)


def test_chunk_ids_are_unique():
    """Chaque chunk doit avoir un chunk_id unique."""
    pages = [{
        "text": "Lorem ipsum dolor sit amet. " * 100,
        "source": "test.pdf",
        "page": 1,
    }]
    chunks = split_documents(pages)

    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids))


def test_empty_pages_returns_empty_list():
    """Liste vide en entrée → liste vide en sortie, pas de crash."""
    assert split_documents([]) == []


def test_metadata_preserved_across_pages():
    """Les métadonnées source et page doivent être conservées."""
    pages = [
        {"text": "Page 1 content " * 100, "source": "doc.pdf", "page": 1},
        {"text": "Page 2 content " * 100, "source": "doc.pdf", "page": 2},
    ]
    chunks = split_documents(pages)

    pages_in_chunks = {c["page"] for c in chunks}
    assert pages_in_chunks == {1, 2}


def test_invalid_overlap_raises_error():
    """Un overlap >= chunk_size doit lever une ValueError."""
    pages = [{"text": "test", "source": "test.pdf", "page": 1}]

    with pytest.raises(ValueError, match="chunk_overlap"):
        split_documents(pages, chunk_size=100, chunk_overlap=100)


def test_chunks_have_required_keys():
    """Chaque chunk doit contenir toutes les clés attendues."""
    pages = [{"text": "test content " * 100, "source": "test.pdf", "page": 1}]
    chunks = split_documents(pages)

    required_keys = {"text", "source", "page", "chunk_id"}
    for chunk in chunks:
        assert set(chunk.keys()) == required_keys

def test_short_fragments_are_filtered():
    """Les fragments plus courts que min_chunk_size sont ignorés."""
    pages = [
        {"text": "Contenu réel et suffisamment long. " * 50, "source": "doc.pdf", "page": 1},
        {"text": "56", "source": "doc.pdf", "page": 2},   # ← numéro de page, à jeter
    ]
    chunks = split_documents(pages, min_chunk_size=50)

    # Aucun chunk ne doit être un micro-fragment
    assert all(len(c["text"].strip()) >= 50 for c in chunks)
    # La page 2 (juste "56") ne doit produire aucun chunk
    assert all(c["page"] == 1 for c in chunks)