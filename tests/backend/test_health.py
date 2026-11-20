"""Unit and integration tests for health endpoints.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
"""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_endpoint() -> None:
    """Test the root service discovery endpoint returns 200 and valid links."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "LabInsight"
    assert data["status"] == "online"
    assert data["health_url"] == "/api/v1/health"
    assert data["readiness_url"] == "/api/v1/ready"


def test_health_endpoint_liveness() -> None:
    """Test GET /api/v1/health returns 200 and healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "LabInsight"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
