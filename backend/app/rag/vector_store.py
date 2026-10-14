import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from backend.app.rag.document_loader import load_document
from backend.app.rag.chunking import chunk_text

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_dir: Path, model_name: str = "all-MiniLM-L6-v2"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name

        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.model_name
        )

        self.collection = self.client.get_or_create_collection(
            name="medibot_knowledge",
            embedding_function=self.embedding_fn,
            metadata={"description": "MediBot AI Verified Healthcare Knowledge Base"}
        )

    def count(self) -> int:
        """Returns the total number of indexed chunks."""
        return self.collection.count()

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Adds a list of chunks into ChromaDB."""
        if not chunks:
            return 0

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Use upsert to be safe against duplicates
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        return len(chunks)

    def query(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Queries the vector collection and returns top matching chunks with distance."""
        if self.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query_text],
            n_results=min(top_k, self.count()),
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, dists):
                formatted_results.append({
                    "text": doc,
                    "metadata": meta,
                    "distance": float(dist)
                })

        return formatted_results

    def seed_from_directory(self, knowledge_base_dir: Path) -> int:
        """
        Scans directory for .txt and .pdf files and indexes them if collection is empty or files are missing.
        """
        kb_path = Path(knowledge_base_dir)
        if not kb_path.exists():
            logger.warning(f"Knowledge base directory {kb_path} does not exist.")
            return 0

        files = list(kb_path.glob("*.txt")) + list(kb_path.glob("*.pdf"))
        total_chunks_added = 0

        for file_path in files:
            try:
                pages_data = load_document(file_path)
                chunks = chunk_text(pages_data)
                added = self.add_chunks(chunks)
                total_chunks_added += added
                logger.info(f"Ingested {file_path.name}: {added} chunks.")
            except Exception as e:
                logger.error(f"Failed to ingest {file_path.name}: {e}")

        return total_chunks_added
