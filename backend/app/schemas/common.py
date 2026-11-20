"""Common API schemas and standard error envelopes.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import uuid

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    """Field-specific or contextual error detail."""

    model_config = ConfigDict(extra="ignore")

    field: str | None = None
    code: str
    message: str
    existing_patient_id: int | None = None


class ErrorBody(BaseModel):
    """Payload contained inside the standard error envelope."""

    model_config = ConfigDict(extra="ignore")

    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)
    existing_patient_id: int | None = None
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class ErrorEnvelope(BaseModel):
    """Standard top-level API error envelope following API_SPECIFICATION.md."""

    error: ErrorBody
