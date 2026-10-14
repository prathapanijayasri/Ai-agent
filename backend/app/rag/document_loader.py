import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any

def load_document(file_path: Path) -> List[Dict[str, Any]]:
    """
    Extracts text and page metadata from supported documents (.txt, .pdf).
    Returns a list of page dicts: [{'text': str, 'source': str, 'page': int}]
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    source_name = path.name
    pages_data = []

    if extension == ".txt":
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                content = f.read()
        
        if content.strip():
            pages_data.append({
                "text": content.strip(),
                "source": source_name,
                "page": 1
            })

    elif extension == ".pdf":
        doc = fitz.open(path)
        try:
            for page_index in range(len(doc)):
                page = doc[page_index]
                text = page.get_text("text").strip()
                if text:
                    pages_data.append({
                        "text": text,
                        "source": source_name,
                        "page": page_index + 1
                    })
        finally:
            doc.close()

    else:
        raise ValueError(f"Unsupported file format '{extension}'. Only .txt and .pdf are supported.")

    return pages_data
