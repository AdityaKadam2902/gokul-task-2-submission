"""Health and Readiness Schemas.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


def get_utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


class HealthResponse(BaseModel):
    """Liveness probe response model."""

    status: Literal["healthy", "unhealthy"] = "healthy"
    app: str = "LabInsight"
    version: str = "0.1.0"
    timestamp: datetime = Field(default_factory=get_utc_now)


class ReadinessChecks(BaseModel):
    """Component readiness status."""

    configuration: str = "ok"
    persistence: str = "ok"


class ReadinessResponse(BaseModel):
    """Readiness probe response model."""

    status: Literal["ready", "not_ready"] = "ready"
    app: str = "LabInsight"
    version: str = "0.1.0"
    environment: str = "development"
    phase: str = "Phase 3 - Validation & CRUD REST API"
    checks: ReadinessChecks = Field(default_factory=ReadinessChecks)
    timestamp: datetime = Field(default_factory=get_utc_now)
