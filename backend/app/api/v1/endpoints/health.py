"""Health and readiness endpoint handlers.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from fastapi import APIRouter, Depends, Response, status

from app.core.config import Settings, get_settings
from app.db.session import check_db_connectivity
from app.schemas.health import HealthResponse, ReadinessChecks, ReadinessResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Process liveness check",
    description="Returns 200 OK if the backend process is running and accepting HTTP requests.",
)
def get_health(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """Check application liveness."""
    return HealthResponse(
        status="healthy",
        app=settings.app_name,
        version=settings.app_version,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Application and database are ready to accept traffic."},
        503: {"description": "Database or core dependency is not ready / unavailable."},
    },
    summary="Application readiness check",
    description=(
        "Performs a live connectivity probe against the database. "
        "Returns 200 OK when the database is reachable, or 503 Service "
        "Unavailable when unreachable."
    ),
)
def get_readiness(
    response: Response,
    settings: Settings = Depends(get_settings),
) -> ReadinessResponse:
    """Check application readiness including real database reachability."""
    db_ok, _ = check_db_connectivity()

    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="not_ready",
            app=settings.app_name,
            version=settings.app_version,
            environment=settings.app_env,
            phase="Phase 5 - Professional Frontend Implementation",
            checks=ReadinessChecks(
                configuration="ok",
                persistence="error: database connectivity check failed",
            ),
        )

    return ReadinessResponse(
        status="ready",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        phase="Phase 5 - Professional Frontend Implementation",
        checks=ReadinessChecks(
            configuration="ok",
            persistence="ok",
        ),
    )
