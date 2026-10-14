from typing import List, Dict, Any, Tuple
from backend.app.rag.vector_store import VectorStore

class Retriever:
    def __init__(self, vector_store: VectorStore, distance_threshold: float = 1.35):
        self.vector_store = vector_store
        self.distance_threshold = distance_threshold

    def retrieve(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieves top relevant chunks for a question.
        Returns:
            {
                "reliable": bool,
                "sources": List[Dict], # [{ "source": "...", "page": 1, "snippet": "..." }]
                "context_text": str
            }
        """
        raw_results = self.vector_store.query(query, top_k=top_k)

        if not raw_results:
            return {
                "reliable": False,
                "sources": [],
                "context_text": ""
            }

        # Filter and rank by distance threshold
        reliable_results = [r for r in raw_results if r["distance"] <= self.distance_threshold]

        # If none met the threshold, fallback to unreliable
        if not reliable_results:
            return {
                "reliable": False,
                "sources": [],
                "context_text": ""
            }

        sources = []
        context_snippets = []

        for item in reliable_results:
            meta = item.get("metadata", {})
            source_name = meta.get("source", "Unknown Document")
            page_num = meta.get("page", 1)
            text_snippet = item.get("text", "").strip()

            sources.append({
                "source": source_name,
                "page": page_num,
                "snippet": text_snippet[:200] + ("..." if len(text_snippet) > 200 else "")
            })

            context_snippets.append(
                f"[Source: {source_name}, Page: {page_num}]\n{text_snippet}"
            )

        context_text = "\n\n---\n\n".join(context_snippets)

        return {
            "reliable": True,
            "sources": sources,
            "context_text": context_text
        }
