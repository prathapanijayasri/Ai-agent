import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from app.rag.embeddings import GeminiEmbeddings

def test_embedding():
    try:
        embedder = GeminiEmbeddings()
        vector = embedder.embed_text("What are the academic regulations of VIT-AP?")
        print("Embedding generated successfully")
        print(f"Dimension: {len(vector)}")
    except Exception as e:
        print(f"Failed to generate embedding: {e}")

if __name__ == "__main__":
    test_embedding()
