"""Pydantic schemas for PatientAnalysis representations.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import AiStatus, ExternalStatus, OverallStatus


class AnalysisSummary(BaseModel):
    """Summary of an analysis run for inclusion in patient responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: int
    run_number: int
    overall_status: OverallStatus
    external_status: ExternalStatus
    ai_status: AiStatus
    external_provider: str = "testwell"
    ai_model: str | None = "llama3.2:3b"
    remarks_text: str | None = None
    error_code: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class AnalysisDetailResponse(AnalysisSummary):
    """Complete analysis record including input snapshot and provider payloads."""

    input_snapshot_json: dict[str, Any]
    external_result_json: dict[str, Any] | None = None
    ai_result_json: dict[str, Any] | None = None
    error_summary: str | None = None
    retry_of_id: str | None = None
