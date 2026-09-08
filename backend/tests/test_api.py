"""
Integration tests for FastAPI REST API endpoints.
"""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Test health check returns 200 OK and expected schema."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database_connected"] is True
    assert "total_medicines" in data


def test_medicines_crud(client: TestClient):
    """Test creating and listing medicines."""
    # List initially
    response = client.get("/api/v1/medicines")
    assert response.status_code == 200
    initial_count = len(response.json())

    # Create new medicine
    new_med = {
        "id": "amoxicillin",
        "generic_name": "Amoxicillin",
        "brand_names": "Amoxil, Moxatag",
        "drug_class": "Penicillin Antibacterial",
        "description": "Used to treat various bacterial infections."
    }
    create_resp = client.post("/api/v1/medicines", json=new_med)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["id"] == "amoxicillin"

    # Get single medicine
    get_resp = client.get("/api/v1/medicines/amoxicillin")
    assert get_resp.status_code == 200
    assert get_resp.json()["generic_name"] == "Amoxicillin"

    # List again to verify count incremented
    list_resp = client.get("/api/v1/medicines")
    assert len(list_resp.json()) == initial_count + 1


def test_emergency_query_chat(client: TestClient):
    """Test that submitting an overdose question to /chat/query triggers emergency protocol."""
    payload = {
        "question": "Help, I swallowed a whole bottle of pills, overdose emergency!"
    }
    response = client.post("/api/v1/chat/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["safety_metadata"]["emergency_detected"] is True
    assert data["safety_metadata"]["classification"] == "EMERGENCY"
    assert "CRITICAL MEDICAL ALERT" in data["answer"]
    assert len(data["citations"]) == 0
