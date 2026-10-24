
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint_returns_success():
    response = client.get("/health")
    assert response.status_code == 200


def test_ask_endpoint_returns_total_revenue():
    response = client.post(
        "/ask",
        json={"question": "What is the total revenue?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "answer" in data
    assert data["question_type"] == "total_revenue"


def test_ask_endpoint_returns_region_result():
    response = client.post(
        "/ask",
        json={"question": "Which region generated the highest revenue?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["question_type"] == "top_region"


def test_ask_endpoint_rejects_empty_question():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_ask_endpoint_rejects_missing_question():
    response = client.post("/ask", json={})
    assert response.status_code == 422


def test_ask_endpoint_rejects_missing_request_body():
    response = client.post("/ask")
    assert response.status_code == 422


def test_ask_endpoint_rejects_non_string_question():
    response = client.post("/ask", json={"question": 123})
    assert response.status_code == 422
