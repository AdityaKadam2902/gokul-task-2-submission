"""Unit tests for configuration loading and validation.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
"""

from app.core.config import Settings


def test_default_settings() -> None:
    """Test default settings attributes."""
    settings = Settings()
    assert settings.app_name == "LabInsight"
    assert settings.app_port == 8000
    assert settings.api_v1_prefix == "/api/v1"
    assert "http://localhost:5173" in settings.cors_origins


def test_parse_cors_origins_string() -> None:
    """Test CORS origins parsing from comma-separated string."""
    origins = Settings.parse_cors_origins("http://example.com, http://app.local")
    assert origins == ["http://example.com", "http://app.local"]


def test_parse_cors_origins_list() -> None:
    """Test CORS origins parsing from list."""
    origins = Settings.parse_cors_origins(["http://localhost:3000", "http://localhost:8080"])
    assert origins == ["http://localhost:3000", "http://localhost:8080"]
