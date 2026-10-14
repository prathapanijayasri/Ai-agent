import pytest
import shutil
import tempfile
from pathlib import Path

from backend.app import create_app
from backend.app.config import Config

@pytest.fixture(scope="session")
def test_env():
    """Sets up a temporary ChromaDB directory and test configuration."""
    temp_dir = tempfile.mkdtemp()
    temp_kb = tempfile.mkdtemp()

    # Create a sample test knowledge document
    sample_doc = Path(temp_kb) / "sample_health_guide.txt"
    sample_doc.write_text(
        "# Test Health Guide\nSource: Test Medical Institute\n\n"
        "Hydration: Adults should drink 2 to 3 liters of water per day. "
        "Symptoms of dehydration include dark amber urine, dry mouth, and fatigue.\n\n"
        "Minor Burns: Cool minor burns under running water for at least 10 minutes. "
        "Never apply ice or butter directly to a burn.",
        encoding="utf-8"
    )

    class TestConfig(Config):
        TESTING = True
        CHROMA_PERSIST_DIR = Path(temp_dir)
        KNOWLEDGE_BASE_DIR = Path(temp_kb)
        ADMIN_API_KEY = "test-admin-secret"
        LLM_PROVIDER = "offline"  # Offline extractive mode for deterministic testing

    app = create_app(config_class=TestConfig)

    with app.app_context():
        yield app

    # Cleanup temporary directories
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree(temp_kb, ignore_errors=True)

@pytest.fixture
def client(test_env):
    return test_env.test_client()
