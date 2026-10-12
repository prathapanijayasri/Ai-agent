import re
from typing import List
from .models import DocumentMetadata, DocumentChunk

class TextChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, text: str, metadata: DocumentMetadata) -> List[DocumentChunk]:
        """
        Splits text into overlapping chunks, preserving metadata.
        """
        words = re.findall(r'\S+|\n', text)
        chunks = []
        
        # Simple word-based chunking
        # Approx 1 token = 1.3 words. We'll chunk by characters for safety.
        # But for exactness, a character chunker is standard.
        
        start = 0
        chunk_idx = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Adjust to nearest space to avoid cutting words
            if end < len(text):
                last_space = chunk_text.rfind(' ')
                if last_space != -1:
                    end = start + last_space
                    chunk_text = text[start:end]
            
            chunk_id = f"{metadata.document_id}_chunk_{chunk_idx}"
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                content=chunk_text.strip(),
                metadata=metadata
            ))
            
            start = end - self.overlap
            chunk_idx += 1
            
        return chunks
