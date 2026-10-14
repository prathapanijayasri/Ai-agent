import pytest
from backend.app.safety import check_emergency

@pytest.mark.parametrize("query", [
    "I have severe chest pain and pressure",
    "My left arm is weak and I can't breathe",
    "Someone collapsed and is unconscious",
    "My throat is closing up and I have anaphylaxis",
    "My friend took an overdose of pills",
    "I am having sudden face drooping and slurred speech"
])
def test_emergency_symptoms_flagged(query):
    """Ensure acute warning symptoms are immediately flagged as emergency."""
    is_emergency, message = check_emergency(query)
    assert is_emergency is True
    assert "EMERGENCY" in message
    assert "911" in message or "112" in message

def test_emergency_endpoint_response(client):
    """Test /chat returns immediate emergency directive without delay."""
    response = client.post("/chat", json={"message": "I feel crushing chest pain radiating to my arm"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["is_emergency"] is True
    assert "EMERGENCY WARNING" in data["response"]
    assert len(data["sources"]) == 0
