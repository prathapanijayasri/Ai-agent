import os
import logging
from pathlib import Path
from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename

from backend.app.safety import check_emergency, validate_chat_input
from backend.app.rag.document_loader import load_document
from backend.app.rag.chunking import chunk_text

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)

def check_admin_auth(req, config) -> bool:
    """Checks admin authorization if ADMIN_API_KEY is set in environment."""
    if not config.ADMIN_API_KEY:
        return True  # If no admin key configured, allow access
    
    header_key = req.headers.get("X-Admin-Key")
    if header_key and header_key == config.ADMIN_API_KEY:
        return True
    
    auth_header = req.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split("Bearer ")[1].strip()
        if token == config.ADMIN_API_KEY:
            return True
            
    return False

@api_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@api_bp.route("/health", methods=["GET"])
def health():
    """Reports application health without exposing secrets or keys."""
    vector_store = current_app.vector_store
    llm_provider = current_app.llm_provider
    return jsonify({
        "status": "healthy",
        "service": "MediBot AI — Healthcare Information Assistant",
        "version": "1.0.0",
        "indexed_chunks": vector_store.count(),
        "llm_provider": llm_provider.get_provider_name()
    }), 200

@api_bp.route("/chat", methods=["POST"])
def chat():
    """Answers healthcare questions with safety triage and RAG retrieval."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json(silent=True) or {}
    is_valid, user_message, error_msg = validate_chat_input(data)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    # 1. Emergency Safety Triage
    is_emergency, emergency_msg = check_emergency(user_message)
    if is_emergency:
        return jsonify({
            "response": emergency_msg,
            "is_emergency": True,
            "sources": [],
            "provider": "Safety Guardrail",
            "reliable_context": True
        }), 200

    # 2. Knowledge Retrieval from ChromaDB
    retriever = current_app.retriever
    llm_provider = current_app.llm_provider

    retrieval_result = retriever.retrieve(user_message, top_k=3)
    reliable = retrieval_result["reliable"]
    sources = retrieval_result["sources"]
    context_text = retrieval_result["context_text"]

    # 3. Model Generation / Extractive Synthesis
    generated = llm_provider.generate_response(
        question=user_message,
        context=context_text,
        reliable=reliable,
        sources=sources
    )

    return jsonify({
        "response": generated["text"],
        "is_emergency": False,
        "reliable_context": reliable,
        "sources": sources,
        "provider": generated["provider"],
        "error": generated.get("error")
    }), 200

@api_bp.route("/documents", methods=["POST"])
def upload_document():
    """Uploads and ingests a permitted PDF or TXT healthcare document."""
    config = current_app.config_obj
    
    # Check Admin authentication if configured
    if not check_admin_auth(request, config):
        return jsonify({"error": "Unauthorized: Valid X-Admin-Key header required"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file field in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    if not filename:
        return jsonify({"error": "Invalid filename"}), 400

    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in config.ALLOWED_EXTENSIONS:
        return jsonify({
            "error": f"Unsupported file type '.{extension}'. Permitted types: {', '.join(config.ALLOWED_EXTENSIONS)}"
        }), 400

    upload_dir = Path(config.UPLOAD_FOLDER)
    upload_dir.mkdir(parents=True, exist_ok=True)
    save_path = upload_dir / filename

    try:
        file.save(str(save_path))

        # Check file size
        file_size = save_path.stat().st_size
        if file_size > config.MAX_CONTENT_LENGTH:
            save_path.unlink(missing_ok=True)
            return jsonify({"error": f"File exceeds maximum allowed size ({config.MAX_CONTENT_LENGTH // (1024*1024)}MB)"}), 400

        # Load and chunk document
        pages_data = load_document(save_path)
        chunks = chunk_text(pages_data)
        
        # Ingest into vector store
        vector_store = current_app.vector_store
        added_count = vector_store.add_chunks(chunks)

        return jsonify({
            "success": True,
            "filename": filename,
            "chunks_ingested": added_count,
            "total_indexed_chunks": vector_store.count()
        }), 201

    except Exception as e:
        logger.error(f"Error processing uploaded document: {e}")
        return jsonify({"error": f"Failed to ingest document: {str(e)}"}), 500
