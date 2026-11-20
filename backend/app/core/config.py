"""Application Configuration Module.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
"""

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = "LabInsight"
    app_env: str = "development"
    app_debug: bool = True
    app_version: str = "0.1.0"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    api_v1_prefix: str = "/api/v1"

    # CORS Settings
    cors_origins: list[str] = Field(default=["http://localhost:5173", "http://127.0.0.1:5173"])

    # Database Settings (Phase 2 Baseline - SQLite)
    database_url: str = "sqlite:///./backend/data/labinsight.db"

    # External Provider Settings (Phase 4A - TestWell)
    testwell_api_url: str = "https://www.test-well.com/api/agent/interpret_results"
    testwell_timeout_seconds: float = 12.0
    testwell_max_retries: int = 2
    testwell_retry_backoff_seconds: float = 0.5
    default_unit_profile: str = "ASSESSMENT_CONVENTIONAL_V1"

    # Local AI Settings (Phase 4B - Ollama)
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_seconds: float = 45.0
    ollama_temperature: float = 0.1
    ollama_max_tokens: int = 350
    ollama_keep_alive: str = "5m"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            # Parse comma-separated string if provided via environment variable
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        return ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
