import re
import pytest

def js_format_markdown_sim(text: str) -> str:
    """Python simulation of backend/static/js/app.js formatMarkdown function."""
    if not text:
        return ""
    # HTML Entity escaping
    entity_map = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}
    safe = re.sub(r'[&<>"\\\']', lambda m: entity_map.get(m.group(0), m.group(0)), text)

    # Bold
    safe = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", safe)
    # Italics
    safe = re.sub(r"\*(.*?)\*", r"<em>\1</em>", safe)
    # Headers
    safe = re.sub(r"^### (.*$)", r"<h3>\1</h3>", safe, flags=re.MULTILINE)
    safe = re.sub(r"^## (.*$)", r"<h2>\1</h2>", safe, flags=re.MULTILINE)
    safe = re.sub(r"^# (.*$)", r"<h1>\1</h1>", safe, flags=re.MULTILINE)
    # Unordered lists
    safe = re.sub(r"^\s*-\s+(.*$)", r"<li>\1</li>", safe, flags=re.MULTILINE)
    safe = re.sub(r"(<li>.*?</li>(?:\s*<li>.*?</li>)*)", r"<ul>\1</ul>", safe, flags=re.DOTALL)
    # Paragraph breaks
    safe = re.sub(r"\n\n+", r"</p><p>", safe)
    safe = safe.replace("\n", "<br>")

    return f"<p>{safe}</p>"

def test_frontend_format_markdown_clean():
    """Verify that markdown responses render clean semantic HTML without broken artifacts."""
    sample_text = (
        "### 1. Symptom Acknowledgment\n"
        "Thank you for reaching out regarding **hand discomfort**.\n\n"
        "### 2. Educational Information\n"
        "- Rest the affected hand.\n"
        "- Use ergonomic support.\n\n"
        "*Disclaimer: General educational information only.*"
    )

    rendered = js_format_markdown_sim(sample_text)

    assert "<h3>1. Symptom Acknowledgment</h3>" in rendered
    assert "<strong>hand discomfort</strong>" in rendered
    assert "<li>Rest the affected hand.</li>" in rendered
    assert "<ul>" in rendered and "</ul>" in rendered
    assert "<em>Disclaimer: General educational information only.</em>" in rendered
    assert "<script>" not in rendered

def test_frontend_escapes_xss_injection():
    """Verify that dangerous script tags or HTML are neutralized."""
    malicious = "<script>alert('xss')</script> and <img src=x onerror=alert(1)>"
    rendered = js_format_markdown_sim(malicious)

    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "&lt;img" in rendered

def test_frontend_index_html_structure(client):
    """Verify that index.html loads with all required components."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert "MediBot AI" in html
    assert "chatMessages" in html
    assert "messageInput" in html
    assert "sendBtn" in html
    assert "uploadModal" in html
    assert "disclaimer-banner" in html
