"""Metadata and enum discovery endpoints.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.models.enums import AiStatus, ExternalStatus, OverallStatus

router = APIRouter(prefix="/meta", tags=["metadata"])


class AnalysisStatusesResponse(BaseModel):
    """Canonical analysis lifecycle enum definitions."""

    external_status: list[str]
    ai_status: list[str]
    overall_status: list[str]


@router.get(
    "/analysis-statuses",
    response_model=AnalysisStatusesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get canonical analysis statuses",
    description="Returns canonical enum values for external_status, ai_status, and overall_status.",
)
def get_analysis_statuses() -> AnalysisStatusesResponse:
    """Return all allowed analysis lifecycle states."""
    return AnalysisStatusesResponse(
        external_status=[e.value for e in ExternalStatus],
        ai_status=[e.value for e in AiStatus],
        overall_status=[e.value for e in OverallStatus],
    )
