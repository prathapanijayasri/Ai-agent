import io

def test_document_upload_unauthorized(client):
    """Test rejecting upload when admin key is required but missing."""
    data = {
        "file": (io.BytesIO(b"Sample health content"), "test.txt")
    }
    response = client.post("/documents", data=data, content_type="multipart/form-data")
    assert response.status_code == 401
    assert "Unauthorized" in response.get_json()["error"]

def test_document_upload_success_with_key(client):
    """Test successful document upload and chunking with valid admin key."""
    doc_content = (
        "# First Aid for Insect Stings\n"
        "Remove the stinger gently with a flat edge. Wash the area with soap and water. "
        "Apply an ice pack wrapped in a cloth to reduce swelling."
    )
    data = {
        "file": (io.BytesIO(doc_content.encode("utf-8")), "stings_first_aid.txt")
    }
    headers = {"X-Admin-Key": "test-admin-secret"}
    response = client.post("/documents", data=data, headers=headers, content_type="multipart/form-data")

    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["filename"] == "stings_first_aid.txt"
    assert res_data["chunks_ingested"] >= 1
    assert res_data["total_indexed_chunks"] > 0

def test_document_upload_invalid_extension(client):
    """Test rejecting unsupported file types."""
    data = {
        "file": (io.BytesIO(b"Binary executable code"), "malicious.exe")
    }
    headers = {"X-Admin-Key": "test-admin-secret"}
    response = client.post("/documents", data=data, headers=headers, content_type="multipart/form-data")

    assert response.status_code == 400
    assert "Unsupported file type" in response.get_json()["error"]
