import re
from typing import List, Dict, Any

def chunk_text(
    pages_data: List[Dict[str, Any]],
    chunk_size: int = 500,
    chunk_overlap: int = 80
) -> List[Dict[str, Any]]:
    """
    Chunks extracted pages into smaller textual units suitable for vector embeddings.
    Retains source filename and page numbers in metadata.
    """
    chunks = []
    chunk_counter = 0

    for page_item in pages_data:
        text = page_item["text"]
        source = page_item["source"]
        page = page_item.get("page", 1)

        # Split into paragraphs / logical sections
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

        current_chunk = ""
        for para in paragraphs:
            if not current_chunk:
                current_chunk = para
            elif len(current_chunk) + len(para) + 1 <= chunk_size:
                current_chunk += "\n" + para
            else:
                # Store current chunk
                chunk_counter += 1
                chunks.append({
                    "id": f"{source}_p{page}_c{chunk_counter}",
                    "text": current_chunk,
                    "metadata": {
                        "source": source,
                        "page": int(page),
                        "chunk_id": chunk_counter
                    }
                })
                # Handle overlap by taking tail of current chunk
                overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                current_chunk = (overlap_text + " " + para).strip()

        if current_chunk:
            chunk_counter += 1
            chunks.append({
                "id": f"{source}_p{page}_c{chunk_counter}",
                "text": current_chunk,
                "metadata": {
                    "source": source,
                    "page": int(page),
                    "chunk_id": chunk_counter
                }
            })

    return chunks
