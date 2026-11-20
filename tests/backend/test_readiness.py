"""Unit and integration tests for readiness endpoint.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_readiness_endpoint_success() -> None:
    """Test GET /api/v1/ready returns 200 OK when database is reachable."""
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["app"] == "LabInsight"
    assert "phase" in data
    assert "Phase" in data["phase"]
    assert data["checks"]["configuration"] == "ok"
    assert data["checks"]["persistence"] == "ok"


def test_readiness_endpoint_database_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test GET /api/v1/ready returns 503 Service Unavailable when database check fails."""
    # Mock check_db_connectivity to simulate database unavailability
    monkeypatch.setattr(
        "app.api.v1.endpoints.health.check_db_connectivity",
        lambda: (False, "Simulated database connection failure"),
    )

    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "not_ready"
    assert data["checks"]["configuration"] == "ok"
    assert "database connectivity check failed" in data["checks"]["persistence"]
