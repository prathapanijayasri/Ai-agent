import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables: check backend/.env first, then root .env if present
BASE_DIR = Path(__file__).resolve().parent.parent.parent
backend_env = BASE_DIR / "backend" / ".env"
root_env = BASE_DIR / ".env"

if backend_env.exists():
    load_dotenv(backend_env)
if root_env.exists():
    load_dotenv(root_env)

# Optimize huggingface transformers to use local cache and avoid external network retries
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

class Config:
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    SECRET_KEY = os.getenv("SECRET_KEY", "medibot-ai-insecure-secret-change-in-prod")

    # Knowledge Base & Vector DB
    KNOWLEDGE_BASE_DIR = Path(os.getenv("KNOWLEDGE_BASE_DIR", str(BASE_DIR / "knowledge_base")))
    CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db")))
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.55"))  # Cosine distance cutoff (distance <= 0.55 indicates solid semantic match)

    # File Upload Security
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10")) * 1024 * 1024  # Default 10MB
    ALLOWED_EXTENSIONS = {"pdf", "txt"}
    UPLOAD_FOLDER = BASE_DIR / "backend" / "uploads"
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")

    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").lower()  # auto, openai, gemini, huggingface, offline
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    _raw_gemini_model = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    if _raw_gemini_model in ("gemini-1.5-flash", "gemini-1.0-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"):
        GEMINI_MODEL = "gemini-flash-latest"
    else:
        GEMINI_MODEL = _raw_gemini_model
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "google/flan-t5-base")
