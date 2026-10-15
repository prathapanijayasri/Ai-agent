import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from backend.app.config import Config
from backend.app.rag.vector_store import VectorStore
from backend.app.rag.retriever import Retriever
from backend.app.safety import check_emergency
from backend.app.llm.provider import LLMProvider

@pytest.fixture(scope="module")
def knowledge_retriever():
    """Initializes vector store and retriever with the real knowledge base."""
    vs = VectorStore(Config.CHROMA_PERSIST_DIR, Config.EMBEDDING_MODEL_NAME)
    if vs.count() == 0:
        vs.seed_from_directory(Config.KNOWLEDGE_BASE_DIR, force_reindex=True)
    return Retriever(vs, distance_threshold=0.55)

def test_left_hand_pain_retrieves_hand_arm_content(knowledge_retriever):
    """
    1. Test that left-hand pain query retrieves relevant hand/arm/strain content
       and does NOT retrieve unrelated content about headaches or burns.
    """
    result = knowledge_retriever.retrieve("slight pain in my left hand", top_k=3)
    assert result["reliable"] is True
    assert len(result["sources"]) > 0

    first_source = result["sources"][0]
    assert "general_symptoms_and_causes.txt" in first_source["source"]

    context_lower = result["context_text"].lower()
    assert "hand" in context_lower or "arm" in context_lower or "wrist" in context_lower

    # CRITICAL: Verify absence of unrelated medical topics in top retrieved chunk
    top_snippet = first_source["snippet"].lower()
    assert "burns and scalds" not in top_snippet
    assert "tension headaches" not in top_snippet

def test_headache_retrieves_headache_content(knowledge_retriever):
    """
    2. Test that headache questions retrieve headache-specific guidance.
    """
    result = knowledge_retriever.retrieve("I have a throbbing headache and sensitivity to light", top_k=2)
    assert result["reliable"] is True
    assert len(result["sources"]) > 0

    context_lower = result["context_text"].lower()
    assert "headache" in context_lower or "migraine" in context_lower

def test_burn_questions_retrieve_burn_content(knowledge_retriever):
    """
    3. Test that minor burn questions retrieve first-aid burn protocols.
    """
    result = knowledge_retriever.retrieve("What first aid should I apply to a minor hot water burn?", top_k=2)
    assert result["reliable"] is True
    assert len(result["sources"]) > 0

    context_lower = result["context_text"].lower()
    assert "burn" in context_lower or "scald" in context_lower
    assert "basic_first_aid.txt" in [s["source"] for s in result["sources"]]

def test_unrelated_retrieved_chunks_rejected(knowledge_retriever):
    """
    4. Test that out-of-domain or unrelated queries are rejected.
    """
    result = knowledge_retriever.retrieve("quantum flux density matrix calculations for hadron colliders", top_k=2)
    assert result["reliable"] is False
    assert len(result["sources"]) == 0
    assert result["context_text"] == ""

def test_missing_or_incorrect_citations_detected(knowledge_retriever):
    """
    5. Test that low-confidence queries do not fabricate citations,
       and genuine queries return valid source file references and page numbers.
    """
    # Unrelated query -> No sources
    unrelated = knowledge_retriever.retrieve("obscure alien biotechnology protocol", top_k=2)
    assert unrelated["reliable"] is False
    assert len(unrelated["sources"]) == 0

    # Valid query -> Valid sources
    valid = knowledge_retriever.retrieve("How should sprains and strains be treated with RICE?", top_k=2)
    assert valid["reliable"] is True
    for src in valid["sources"]:
        assert src["source"].endswith(".txt") or src["source"].endswith(".pdf")
        assert isinstance(src["page"], int)
        assert src["page"] >= 1
        assert len(src["snippet"].strip()) > 10

def test_emergency_cardiac_left_arm_override():
    """
    6. Test emergency safety checks:
       Left arm/hand pain + cardiac red flags (chest tightness, nausea, sweating, faintness)
       MUST override RAG, and mild pain must NOT rule out emergency.
    """
    # Mild pain with chest pressure
    is_em, msg = check_emergency("I feel a slight pain in my left hand and mild chest pressure")
    assert is_em is True
    assert "CARDIAC" in msg or "EMERGENCY" in msg
    assert "112" in msg  # India emergency number

    # Left arm pain with cold sweats and nausea
    is_em, msg = check_emergency("Mild ache in my left arm with cold sweats and nausea")
    assert is_em is True
    assert "112" in msg

    # Left wrist pain alone without cardiac signs is NOT an emergency
    is_em, msg = check_emergency("I have a slight pain in my left wrist from typing")
    assert is_em is False

def test_emergency_stroke_guidance():
    """
    7. Test emergency safety checks for stroke symptoms (FAST).
    """
    is_em, msg = check_emergency("Sudden weakness in my left arm and slurred speech")
    assert is_em is True
    assert "STROKE" in msg or "EMERGENCY" in msg
    assert "F.A.S.T." in msg or "FAST" in msg
    assert "112" in msg

def test_normal_symptom_follow_up_questions():
    """
    8. Test that ordinary symptom questions ask relevant follow-up questions
       (1 or 2 concise questions) and include warning signs.
    """
    cfg = Config()
    cfg.LLM_PROVIDER = "offline"
    provider = LLMProvider(cfg)

    res = provider.generate_response(
        question="I have a slight pain in my left hand from typing",
        context="Hand, Wrist, and Arm Pain: Repetitive strain from typing. Take breaks and use ergonomic setups.",
        reliable=True,
        sources=[{"source": "general_symptoms_and_causes.txt", "page": 1, "snippet": "Take breaks from typing."}]
    )

    text = res["text"]
    assert "Symptom Acknowledgment" in text
    assert "Follow-Up Questions" in text
    assert "When to Seek Professional Medical Care" in text
    assert "Disclaimer" in text

def test_mocked_gemini_provider_integration():
    """
    9. Deterministic test for Gemini LLM provider using mocked client response.
    """
    cfg = Config()
    cfg.LLM_PROVIDER = "gemini"
    cfg.GEMINI_API_KEY = "mocked-valid-key-for-testing"

    provider = LLMProvider(cfg)

    mock_gemini_text = (
        "### 1. Symptom Acknowledgment\n"
        "I understand you are experiencing discomfort in your hand.\n\n"
        "### 2. Educational Information\n"
        "Rest and ergonomic adjustments can help alleviate repetitive strain.\n\n"
        "### 3. Follow-Up Questions\n"
        "1. Where exactly is the pain located?\n"
        "2. Did it begin after prolonged typing?\n\n"
        "### 4. Warning Signs\n"
        "Seek medical care if numbness or severe pain persists.\n\n"
        "### 5. Citations\n"
        "Verified from general_symptoms_and_causes.txt\n\n"
        "### 6. Disclaimer\n"
        "Educational information only."
    )

    mock_response = MagicMock()
    mock_response.text = mock_gemini_text

    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        res = provider.generate_response(
            question="What helps hand strain?",
            context="Ergonomics and rest help hand strain.",
            reliable=True,
            sources=[{"source": "general_symptoms_and_causes.txt", "page": 1, "snippet": "Ergonomics and rest help."}]
        )

        assert res["provider"] == provider.get_provider_name()
        assert res["error"] is None
        assert "Symptom Acknowledgment" in res["text"]
        assert "Follow-Up Questions" in res["text"]

@pytest.mark.skipif(not Config.GEMINI_API_KEY, reason="Real GEMINI_API_KEY not configured in backend/.env")
def test_real_gemini_api_call():
    """
    10. Real Gemini API Integration Test:
        Clearly distinguishes live API integration from mocked tests.
        Verifies that the configured GEMINI_API_KEY can communicate with Google's API.
    """
    from google import genai
    import time

    client = genai.Client(api_key=Config.GEMINI_API_KEY)
    response = None
    last_err = None

    for model_name in [Config.GEMINI_MODEL, "gemini-3.5-flash", "gemini-flash-latest"]:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents="Respond with the exact phrase: REAL_GEMINI_INTEGRATION_VERIFIED"
                )
                if response and response.text:
                    break
            except Exception as e:
                last_err = e
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    time.sleep(1.0)
                    continue
                break
        if response and response.text:
            break

    if response is None or not response.text:
        raise last_err

    assert response is not None
    assert response.text is not None
    assert "REAL_GEMINI_INTEGRATION_VERIFIED" in response.text

