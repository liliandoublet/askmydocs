"""Découpage du texte en chunks pour l'indexation."""
from langchain_text_splitters import RecursiveCharacterTextSplitter

from askmydocs.config import CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_SIZE
from askmydocs.types import Page, Chunk


def split_documents(
    pages: list[Page],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    min_chunk_size: int = MIN_CHUNK_SIZE,
) -> list[Chunk]:
    """Découpe les pages d'un document en chunks plus petits.

    Utilise `RecursiveCharacterTextSplitter` qui essaie de couper aux
    endroits naturels (paragraphes, phrases) pour préserver la cohérence
    sémantique des chunks.

    Args:
        pages: liste de Pages issues du loader.
        chunk_size: taille cible d'un chunk (en caractères).
        chunk_overlap: nombre de caractères partagés entre chunks consécutifs.

    Returns:
        Liste de Chunks. Liste vide si `pages` est vide.

    Raises:
        ValueError: si chunk_overlap >= chunk_size (config invalide).
    """
    # Garde-fou sur la config
    if chunk_overlap >= chunk_size:
        raise ValueError(
            f"chunk_overlap ({chunk_overlap}) doit être < "
            f"chunk_size ({chunk_size})"
        )

    # Pas de pages → pas de chunks (cas géré explicitement)
    if not pages:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # Ordre des séparateurs : du plus structuré au moins structuré
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    all_chunks: list[Chunk] = []
    chunk_id = 0

    for page in pages:
        chunks_text = splitter.split_text(page["text"])

        for chunk_text in chunks_text:
            if len(chunk_text.strip()) < min_chunk_size:
                continue
            all_chunks.append(Chunk(
                text=chunk_text,
                source=page["source"],
                page=page["page"],
                chunk_id=chunk_id,
            ))
            chunk_id += 1

    return all_chunks


def _print_stats(chunks: list[Chunk]) -> None:
    """Affiche des statistiques utiles sur un set de chunks (mode debug)."""
    if not chunks:
        print("⚠️  Aucun chunk généré (document vide ?)")
        return

    sizes = [len(c["text"]) for c in chunks]
    print(f"📏 Taille moyenne : {sum(sizes) // len(sizes)} caractères")
    print(f"📏 Min / Max      : {min(sizes)} / {max(sizes)} caractères")

    print("\n--- APERÇU CHUNK 0 ---")
    print(f"Source : {chunks[0]['source']} | Page : {chunks[0]['page']}")
    print(f"Texte  : {chunks[0]['text'][:200]}...")

    if len(chunks) > 5:
        mid = len(chunks) // 2
        print(f"\n--- APERÇU CHUNK {mid} (milieu) ---")
        print(f"Source : {chunks[mid]['source']} | Page : {chunks[mid]['page']}")
        print(f"Texte  : {chunks[mid]['text'][:200]}...")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from askmydocs.loader import load_document

    if len(sys.argv) < 2:
        print("Usage: uv run python -m src.askmydocs.splitter <chemin_fichier>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    print(f"📄 Chargement de : {file_path.name}")
    pages = load_document(file_path)
    print(f"✅ {len(pages)} page(s) extraites")

    print(f"\n✂️  Découpage en chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    chunks = split_documents(pages)
    print(f"✅ {len(chunks)} chunks créés\n")

    _print_stats(chunks)