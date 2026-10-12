from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from ..core.database import Base

class DocumentChunkDB(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String, unique=True, index=True, nullable=False)
    document_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, index=True, nullable=False)
    source = Column(String, nullable=False)
    page = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(3072)) # Gemini embeddings produce 3072 dimensions
