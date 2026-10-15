import re
from typing import List, Dict, Any

def _split_into_sentences(text: str) -> List[str]:
    """Splits text into complete sentences without chopping words."""
    sentence_end = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_end.split(text.strip())
    return [s.strip() for s in sentences if s.strip()]

def chunk_text(
    pages_data: List[Dict[str, Any]],
    chunk_size: int = 1200,
    chunk_overlap: int = 150
) -> List[Dict[str, Any]]:
    """
    Chunks extracted document pages into coherent semantic units suitable for vector embeddings.
    Keeps medical topics together by respecting section boundaries (markdown headers) and paragraphs.
    Avoids mid-word truncation during overlap.
    """
    chunks = []
    chunk_counter = 0

    for page_item in pages_data:
        raw_text = page_item["text"]
        source = page_item["source"]
        page = page_item.get("page", 1)

        # Extract document-level title/header if present at top
        doc_header = ""
        header_match = re.search(r"^(#[^#\n]+(?:\n[^\n#]+)*)", raw_text.strip())
        if header_match:
            doc_header = header_match.group(1).strip()

        # Check if text has markdown sections (## )
        section_pattern = re.compile(r"(?=^##\s+)", re.MULTILINE)
        sections = section_pattern.split(raw_text)

        # If sections exist (more than 1 piece), process by section
        if len(sections) > 1:
            for sec in sections:
                sec_text = sec.strip()
                if not sec_text:
                    continue

                # If this is the preamble before first ##, only chunk if substantial
                if not sec_text.startswith("##"):
                    if len(sec_text) < 50:
                        continue

                # Extract section title if present
                sec_title_match = re.match(r"^##\s+([^\n]+)", sec_text)
                sec_title = sec_title_match.group(1).strip() if sec_title_match else ""

                # Context prefix to preserve semantic topic for embeddings
                prefix = ""
                if doc_header and not sec_text.startswith("# "):
                    first_header_line = doc_header.split("\n")[0].replace("#", "").strip()
                    prefix = f"[{first_header_line}]\n"

                full_sec_text = (prefix + sec_text).strip()

                if len(full_sec_text) <= chunk_size:
                    chunk_counter += 1
                    chunks.append({
                        "id": f"{source}_p{page}_c{chunk_counter}",
                        "text": full_sec_text,
                        "metadata": {
                            "source": source,
                            "page": int(page),
                            "chunk_id": chunk_counter,
                            "section": sec_title or source
                        }
                    })
                else:
                    # Section is larger than chunk_size, split by paragraphs
                    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", sec_text) if p.strip()]
                    current_chunk = prefix + (f"## {sec_title}\n" if sec_title and not paragraphs[0].startswith(f"## {sec_title}") else "")
                    
                    for para in paragraphs:
                        if len(current_chunk) + len(para) + 1 <= chunk_size:
                            current_chunk = (current_chunk + "\n\n" + para).strip()
                        else:
                            if current_chunk.strip():
                                chunk_counter += 1
                                chunks.append({
                                    "id": f"{source}_p{page}_c{chunk_counter}",
                                    "text": current_chunk.strip(),
                                    "metadata": {
                                        "source": source,
                                        "page": int(page),
                                        "chunk_id": chunk_counter,
                                        "section": sec_title or source
                                    }
                                })
                            # Create overlap using last sentence(s)
                            sentences = _split_into_sentences(current_chunk)
                            overlap = ""
                            if sentences:
                                overlap = sentences[-1]
                                if len(overlap) > chunk_overlap:
                                    overlap = ""
                            current_chunk = (prefix + (overlap + "\n" if overlap else "") + para).strip()

                    if current_chunk.strip():
                        chunk_counter += 1
                        chunks.append({
                            "id": f"{source}_p{page}_c{chunk_counter}",
                            "text": current_chunk.strip(),
                            "metadata": {
                                "source": source,
                                "page": int(page),
                                "chunk_id": chunk_counter,
                                "section": sec_title or source
                            }
                        })
        else:
            # Non-markdown or unstructured text: split cleanly by paragraphs and sentences
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw_text) if p.strip()]
            current_chunk = ""

            for para in paragraphs:
                if not current_chunk:
                    current_chunk = para
                elif len(current_chunk) + len(para) + 1 <= chunk_size:
                    current_chunk += "\n\n" + para
                else:
                    chunk_counter += 1
                    chunks.append({
                        "id": f"{source}_p{page}_c{chunk_counter}",
                        "text": current_chunk.strip(),
                        "metadata": {
                            "source": source,
                            "page": int(page),
                            "chunk_id": chunk_counter,
                            "section": source
                        }
                    })
                    # Use last complete sentence for overlap instead of blind character slicing
                    sentences = _split_into_sentences(current_chunk)
                    overlap = sentences[-1] if sentences and len(sentences[-1]) <= chunk_overlap else ""
                    current_chunk = (overlap + "\n\n" + para).strip()

            if current_chunk.strip():
                chunk_counter += 1
                chunks.append({
                    "id": f"{source}_p{page}_c{chunk_counter}",
                    "text": current_chunk.strip(),
                    "metadata": {
                        "source": source,
                        "page": int(page),
                        "chunk_id": chunk_counter,
                        "section": source
                    }
                })

    return chunks
