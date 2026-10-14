from pathlib import Path
from flask import Flask
from backend.app.config import Config
from backend.app.rag.vector_store import VectorStore
from backend.app.rag.retriever import Retriever
from backend.app.llm.provider import LLMProvider
from backend.app.routes import api_bp

def create_app(config_class=Config) -> Flask:
    base_dir = Path(__file__).resolve().parent.parent
    
    app = Flask(
        __name__,
        static_folder=str(base_dir / "static"),
        template_folder=str(base_dir / "templates")
    )
    
    app.config.from_object(config_class)
    app.config_obj = config_class

    # Initialize Vector Store
    vector_store = VectorStore(
        persist_dir=config_class.CHROMA_PERSIST_DIR,
        model_name=config_class.EMBEDDING_MODEL_NAME
    )

    # Seed knowledge base from directory if collection is currently empty
    if vector_store.count() == 0:
        vector_store.seed_from_directory(config_class.KNOWLEDGE_BASE_DIR)

    # Initialize Retriever and LLM Provider
    retriever = Retriever(
        vector_store=vector_store,
        distance_threshold=config_class.SIMILARITY_THRESHOLD
    )
    llm_provider = LLMProvider(config=config_class)

    # Attach to app instance for access in routes
    app.vector_store = vector_store
    app.retriever = retriever
    app.llm_provider = llm_provider

    # Register blueprints
    app.register_blueprint(api_bp)

    return app
