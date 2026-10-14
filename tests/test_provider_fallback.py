from backend.app.config import Config
from backend.app.llm.provider import LLMProvider

def test_offline_provider_fallback_with_context():
    """Ensure offline provider returns factual synthesis from retrieved sources."""
    cfg = Config()
    cfg.LLM_PROVIDER = "offline"
    cfg.OPENAI_API_KEY = ""
    cfg.GEMINI_API_KEY = ""

    provider = LLMProvider(cfg)
    sources = [{"source": "test_guide.txt", "page": 1, "snippet": "Drink 2 to 3 liters of water."}]
    res = provider.generate_response(
        question="What is the water intake?",
        context="Drink 2 to 3 liters of water.",
        reliable=True,
        sources=sources
    )

    assert "Educational Summary" in res["text"]
    assert "test_guide.txt" in res["text"]
    assert "Disclaimer" in res["text"]
    assert "Offline" in res["provider"]

def test_offline_provider_honest_uncertainty():
    """Ensure provider clearly states lack of knowledge when reliable context is missing."""
    cfg = Config()
    cfg.LLM_PROVIDER = "offline"

    provider = LLMProvider(cfg)
    res = provider.generate_response(
        question="Obscure unknown medical question",
        context="",
        reliable=False,
        sources=[]
    )

    assert "do not have verified medical documentation" in res["text"]
    assert "Disclaimer" in res["text"]
