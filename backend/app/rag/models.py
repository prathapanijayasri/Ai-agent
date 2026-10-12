from pydantic import BaseModel, Field
from typing import Optional

class DocumentMetadata(BaseModel):
    document_id: str
    title: str
    category: str
    source: str
    page: Optional[int] = None

class DocumentChunk(BaseModel):
    chunk_id: str
    content: str
    metadata: DocumentMetadata

class RetrievedChunk(DocumentChunk):
    relevance_score: float
