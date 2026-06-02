"""Extraction de texte depuis des fichiers PDF et DOCX."""
from askmydocs.types import Page
from pathlib import Path
from pypdf import PdfReader
from docx import Document


def load_pdf(file_path: Path) -> list[Page]:
    """
    Extrait le texte d'un PDF, page par page.

    Args:
        file_path: chemin vers le fichier PDF

    Returns:
        Liste de dicts {text, source, page}
    """
    reader = PdfReader(str(file_path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()

        # On ignore les pages vides (souvent des pages de garde)
        if not text:
            continue

        pages.append({
            "text": text,
            "source": file_path.name,
            "page": page_number,
        })

    return pages


def load_docx(file_path: Path) -> list[Page]:
    """
    Extrait le texte d'un fichier Word (.docx).

    Note: les .docx n'ont pas de notion de page native, donc on retourne
    un seul "bloc" avec page=1.
    """
    doc = Document(str(file_path))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs)

    if not full_text:
        return []

    return [{
        "text": full_text,
        "source": file_path.name,
        "page": 1,
    }]


def load_document(file_path: Path) -> list[Page]:
    """
    Détecte le type de fichier et appelle le bon loader.

    Args:
        file_path: chemin vers le fichier

    Returns:
        Liste de dicts {text, source, page}

    Raises:
        ValueError: si le format n'est pas supporté
        FileNotFoundError: si le fichier n'existe pas
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"❌ Fichier introuvable : {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return load_pdf(file_path)
    elif suffix == ".docx":
        return load_docx(file_path)
    else:
        raise ValueError(
            f"❌ Format non supporté : {suffix}. "
            f"Formats acceptés : .pdf, .docx"
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: uv run python -m src.askmydocs.loader <chemin_fichier>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    print(f"📄 Chargement de : {file_path.name}")

    pages = load_document(file_path)

    print(f"✅ {len(pages)} page(s)/section(s) extraites\n")
    print("--- APERÇU PAGE 1 ---")
    if pages:
        preview = pages[0]["text"][:300]
        print(preview)
        print(f"\n📊 Source : {pages[0]['source']} | Page : {pages[0]['page']}")
        print(f"📏 Longueur totale page 1 : {len(pages[0]['text'])} caractères")