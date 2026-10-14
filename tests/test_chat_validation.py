def test_chat_empty_payload(client):
    """Test rejecting empty or non-JSON payloads."""
    response = client.post("/chat", data="not json")
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_chat_empty_message(client):
    """Test rejecting empty message string."""
    response = client.post("/chat", json={"message": "   "})
    assert response.status_code == 400
    assert "Message cannot be empty" in response.get_json()["error"]

def test_chat_oversized_message(client):
    """Test rejecting message longer than 2000 characters."""
    long_msg = "A" * 2001
    response = client.post("/chat", json={"message": long_msg})
    assert response.status_code == 400
    assert "exceeds" in response.get_json()["error"]

def test_chat_valid_message(client):
    """Test valid message returns 200 with response."""
    response = client.post("/chat", json={"message": "What is the recommended daily water intake?"})
    assert response.status_code == 200
    data = response.get_json()
    assert "response" in data
    assert "is_emergency" in data
    assert data["is_emergency"] is False
    assert "provider" in data
