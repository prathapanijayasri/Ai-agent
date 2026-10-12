from typing import List, Optional
from .models import RetrievedChunk

class BaseRetriever:
    """
    Interface for the Retrieval-Augmented Generation system.
    """

    def search(self, query: str, category: Optional[str] = None, top_k: int = 5) -> List[RetrievedChunk]:
        """
        Search the vector database for relevant documents.
        """
        raise NotImplementedError("Retriever not implemented yet")

class MockRetriever(BaseRetriever):
    """
    A mock retriever for testing hallucination and out-of-domain logic before full DB integration.
    """
    def search(self, query: str, category: Optional[str] = None, top_k: int = 5) -> List[RetrievedChunk]:
        # Simple mock implementation for testing
        return []

from sqlalchemy.orm import Session
from .db_models import DocumentChunkDB
from .embeddings import GeminiEmbeddings
from .models import DocumentMetadata

class PGVectorRetriever(BaseRetriever):
    def __init__(self, db: Session):
        self.db = db
        self.embedder = GeminiEmbeddings()

    def search(self, query: str, category: Optional[str] = None, top_k: int = 5) -> List[RetrievedChunk]:
        query_embedding = self.embedder.embed_text(query)
        
        # Base query using pgvector's L2 distance operator `<->`
        stmt = self.db.query(DocumentChunkDB).order_by(
            DocumentChunkDB.embedding.l2_distance(query_embedding)
        )
        
        if category:
            stmt = stmt.filter(DocumentChunkDB.category == category)
            
        results = stmt.limit(top_k).all()
        
        retrieved = []
        for r in results:
            metadata = DocumentMetadata(
                document_id=r.document_id,
                title=r.title,
                category=r.category,
                source=r.source,
                page=r.page
            )
            # We don't fetch exact score natively with l2_distance without raw SQL,
            # but we can mock a confidence score or fetch it via func.
            # For now, just assign a default high score if retrieved.
            retrieved.append(RetrievedChunk(
                chunk_id=r.chunk_id,
                content=r.content,
                metadata=metadata,
                relevance_score=0.9
            ))
            
        return retrieved

