import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    SECRET_KEY = os.getenv("SECRET_KEY", "medibot-ai-insecure-secret-change-in-prod")

    # Knowledge Base & Vector DB
    KNOWLEDGE_BASE_DIR = Path(os.getenv("KNOWLEDGE_BASE_DIR", str(BASE_DIR / "knowledge_base")))
    CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db")))
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "1.35"))  # L2 distance cutoff

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
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "google/flan-t5-base")
