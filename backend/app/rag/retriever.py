import re
from typing import List, Dict, Any, Set, Tuple
from backend.app.rag.vector_store import VectorStore

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
    "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just",
    "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only",
    "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she",
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which",
    "while", "who", "whom", "why", "with", "would", "you", "your", "yours", "yourself",
    "yourselves", "slight", "mild", "severe", "lot", "much", "having", "feeling", "please"
}

def extract_keywords(text: str) -> Set[str]:
    """Extracts non-stopword content words from text."""
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return {w for w in words if w not in STOPWORDS}

def make_clean_snippet(text: str, query_keywords: Set[str], max_len: int = 250) -> str:
    """Extracts coherent, complete sentence snippets without truncation artifacts."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    matching = [s.strip() for s in sentences if s.strip() and any(kw in s.lower() for kw in query_keywords)]

    if matching:
        chosen = " ".join(matching[:2])
    elif sentences:
        chosen = " ".join([s.strip() for s in sentences[:2] if s.strip()])
    else:
        chosen = text.strip()

    if len(chosen) <= max_len:
        return chosen
    cut = chosen[:max_len].rsplit(" ", 1)[0]
    return cut.rstrip(".,;") + "..."

class Retriever:
    def __init__(self, vector_store: VectorStore, distance_threshold: float = 0.55):
        self.vector_store = vector_store
        self.distance_threshold = distance_threshold

    def retrieve(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieves top relevant chunks using semantic similarity combined with lexical keyword verification.
        Applies a configurable relevance threshold so unrelated or low-confidence chunks are never presented
        as verified supporting evidence.
        """
        query_clean = query.strip()
        if not query_clean:
            return {"reliable": False, "sources": [], "context_text": ""}

        query_keywords = extract_keywords(query_clean)

        # Retrieve a slightly larger pool for hybrid ranking
        fetch_k = max(top_k * 3, 6)
        raw_results = self.vector_store.query(query_clean, top_k=fetch_k)

        if not raw_results:
            return {"reliable": False, "sources": [], "context_text": ""}

        scored_candidates = []
        for item in raw_results:
            dist = float(item.get("distance", 1.0))
            text = item.get("text", "")
            meta = item.get("metadata", {})
            section = meta.get("section", "").lower()
            text_lower = text.lower()

            # Cosine semantic similarity score in [0.0, 1.0]
            semantic_score = max(0.0, 1.0 - dist)

            # Keyword lexical match score
            if query_keywords:
                matches = sum(1 for kw in query_keywords if kw in text_lower or kw in section)
                lexical_score = matches / len(query_keywords)
            else:
                lexical_score = 0.5

            # Hybrid score prioritizing semantic match with keyword reinforcement
            hybrid_score = 0.65 * semantic_score + 0.35 * lexical_score

            # Relevance Gate:
            # 1. Cosine distance must satisfy distance_threshold
            # 2. If query specifies distinct anatomical/symptom terms, reject chunks that completely fail lexical match
            is_relevant = True
            if dist > self.distance_threshold:
                is_relevant = False
            elif query_keywords and lexical_score == 0 and dist > 0.48:
                # Borderline distance with zero keyword overlap is considered off-topic
                is_relevant = False

            if is_relevant:
                scored_candidates.append({
                    "item": item,
                    "hybrid_score": hybrid_score,
                    "semantic_score": semantic_score,
                    "lexical_score": lexical_score,
                    "distance": dist
                })

        # Rank by hybrid score descending
        scored_candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)

        if not scored_candidates:
            return {
                "reliable": False,
                "sources": [],
                "context_text": ""
            }

        # Select top_k reliable items
        top_candidates = scored_candidates[:top_k]

        sources = []
        context_snippets = []

        for cand in top_candidates:
            item = cand["item"]
            meta = item.get("metadata", {})
            source_name = meta.get("source", "Unknown Document")
            page_num = meta.get("page", 1)
            text_snippet = item.get("text", "").strip()

            snippet = make_clean_snippet(text_snippet, query_keywords, max_len=260)

            sources.append({
                "source": source_name,
                "page": int(page_num),
                "snippet": snippet
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

