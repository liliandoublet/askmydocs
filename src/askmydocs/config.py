from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# --- Chemins du projet ---
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
CHROMA_DIR = DATA_DIR / "chroma_db"

# --- LLM ---
# Le provider par défaut et son modèle par défaut sont définis par les classes
# provider elles-mêmes (voir askmydocs.llm) ; chaque provider lit sa propre
# clé API depuis l'environnement.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# Ollama (local, RGPD)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# --- Modèles ---
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# --- Paramètres RAG ---
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 6
MIN_CHUNK_SIZE = 50

# --- ChromaDB ---
COLLECTION_NAME = "askmydocs"


def check_config() -> None:
    """Vérifie que la config est OK au démarrage."""
    from askmydocs.llm.factory import get_provider

    provider = get_provider(LLM_PROVIDER)
    if not provider.is_available():
        raise ValueError(
            f"❌ Provider '{LLM_PROVIDER}' indisponible. Vérifie ton fichier .env"
        )
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    print("✅ Config OK")


if __name__ == "__main__":
    from askmydocs.llm.factory import get_provider

    check_config()
    print(f"📁 Project root : {PROJECT_ROOT}")
    print(f"📁 Uploads dir  : {UPLOADS_DIR}")
    print(f"📁 ChromaDB dir : {CHROMA_DIR}")
    print(f"🤖 Modèle embed : {EMBEDDING_MODEL}")
    print(f"🤖 Provider LLM : {LLM_PROVIDER}")
    print(f"🤖 Modèle LLM   : {get_provider(LLM_PROVIDER).model_name}")