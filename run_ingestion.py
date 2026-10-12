import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from app.core.database import SessionLocal, engine, Base
from app.rag.db_models import DocumentChunkDB
from app.rag.ingestion import DocumentIngestor

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def main():
    db = SessionLocal()
    try:
        kb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'knowledge_base'))
        ingestor = DocumentIngestor(db, kb_dir)
        print("Starting ingestion process...")
        ingestor.process_directory()
        print("Ingestion complete.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
