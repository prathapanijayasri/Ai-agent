def test_health_endpoint_success(client):
    """Test that /health returns 200 and standard health data."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "healthy"
    assert "MediBot AI" in data["service"]
    assert "indexed_chunks" in data
    assert data["indexed_chunks"] > 0
    assert "llm_provider" in data
    assert "version" in data

def test_health_endpoint_does_not_leak_secrets(client):
    """Test that /health does not expose API keys, secrets, or internal server paths."""
    response = client.get("/health")
    data = response.get_json()
    raw_text = response.get_data(as_text=True)

    assert "test-admin-secret" not in raw_text
    assert "API_KEY" not in data
    assert "SECRET_KEY" not in data
