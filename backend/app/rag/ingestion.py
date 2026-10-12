import os
import glob
from PyPDF2 import PdfReader
from sqlalchemy.orm import Session
from .models import DocumentMetadata
from .chunking import TextChunker
from .embeddings import GeminiEmbeddings
from .db_models import DocumentChunkDB

def extract_text_from_pdf(filepath: str) -> list[str]:
    """Returns a list of strings, each string representing a page's text."""
    reader = PdfReader(filepath)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
        else:
            pages.append("")
    return pages

class DocumentIngestor:
    def __init__(self, db: Session, knowledge_base_dir: str):
        self.db = db
        self.kb_dir = knowledge_base_dir
        self.chunker = TextChunker()
        self.embedder = GeminiEmbeddings()

    def process_directory(self):
        """Scans the knowledge base directory for PDFs and ingests them."""
        categories = os.listdir(self.kb_dir)
        for category in categories:
            cat_path = os.path.join(self.kb_dir, category)
            if not os.path.isdir(cat_path):
                continue
                
            pdf_files = glob.glob(os.path.join(cat_path, "*.pdf"))
            for pdf_file in pdf_files:
                self.ingest_pdf(pdf_file, category)

    def ingest_pdf(self, filepath: str, category: str):
        filename = os.path.basename(filepath)
        doc_id = filename.replace(".pdf", "").replace(" ", "_").lower()
        title = filename.replace(".pdf", "").replace("_", " ")

        print(f"Ingesting: {filename} into category: {category}")
        
        pages = extract_text_from_pdf(filepath)
        
        for page_num, text in enumerate(pages, start=1):
            if not text.strip():
                continue
                
            metadata = DocumentMetadata(
                document_id=doc_id,
                title=title,
                category=category,
                source=filename,
                page=page_num
            )
            
            chunks = self.chunker.chunk_document(text, metadata)
            
            # Embed chunks
            texts_to_embed = [c.content for c in chunks]
            embeddings = self.embedder.embed_documents(texts_to_embed)
            
            # Save to DB
            for chunk, embedding in zip(chunks, embeddings):
                db_chunk = DocumentChunkDB(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.metadata.document_id,
                    title=chunk.metadata.title,
                    category=chunk.metadata.category,
                    source=chunk.metadata.source,
                    page=chunk.metadata.page,
                    content=chunk.content,
                    embedding=embedding
                )
                self.db.add(db_chunk)
                
        self.db.commit()
        print(f"Successfully ingested {filename}")
