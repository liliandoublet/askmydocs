from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# --- Chemins du projet ---
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
CHROMA_DIR = DATA_DIR / "chroma_db"

# --- API ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Modèles ---
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL = "gemini-2.5-flash"          # Gratuit jusqu'à ~1500 req/jour

# --- Paramètres RAG ---
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 6
MIN_CHUNK_SIZE = 50

# --- ChromaDB ---
COLLECTION_NAME = "askmydocs"


def check_config() -> None:
    """Vérifie que la config est OK au démarrage."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "❌ GEMINI_API_KEY manquante. Vérifie ton fichier .env"
        )
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    print("✅ Config OK")


if __name__ == "__main__":
    check_config()
    print(f"📁 Project root : {PROJECT_ROOT}")
    print(f"📁 Uploads dir  : {UPLOADS_DIR}")
    print(f"📁 ChromaDB dir : {CHROMA_DIR}")
    print(f"🤖 Modèle embed : {EMBEDDING_MODEL}")
    print(f"🤖 Modèle LLM   : {LLM_MODEL}")