"""LabInsight FastAPI Application Entry Point.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import logging
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException, DuplicateRecordException

# Configure structured application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger("labinsight")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown events."""
    settings = get_settings()
    logger.info(
        "LabInsight application starting up",
        extra={
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
        },
    )
    yield
    logger.info("LabInsight application shutting down")


def create_application() -> FastAPI:
    """Factory creating and configuring the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=f"{settings.app_name} API",
        version=settings.app_version,
        description=(
            "Educational health prediction and biomarker interpretation application. "
            "Gokul Infocare - Task 2 (Candidate 267)."
        ),
        debug=settings.app_debug,
        lifespan=lifespan,
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 1. Domain Application Exception Handler
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        error_payload: dict[str, Any] = {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "request_id": str(uuid.uuid4()),
        }
        if isinstance(exc, DuplicateRecordException):
            error_payload["existing_patient_id"] = exc.existing_patient_id

        return JSONResponse(
            status_code=exc.status_code,
            content={"error": error_payload},
        )

    # 2. Pydantic Request Validation Error Handler
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        formatted_details = []
        for err in exc.errors():
            loc = err.get("loc", [])
            # Strip body prefix if present
            field_name = str(loc[-1]) if loc else "body"
            formatted_details.append(
                {
                    "field": field_name,
                    "code": str(err.get("type", "VALIDATION_ERROR")).upper(),
                    "message": err.get("msg", "Invalid value."),
                }
            )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "One or more input fields are invalid.",
                    "details": formatted_details,
                    "request_id": str(uuid.uuid4()),
                }
            },
        )

    # 3. Starlette HTTP Exception Handler
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code_map = {
            400: "BAD_REQUEST",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            500: "INTERNAL_SERVER_ERROR",
            503: "SERVICE_UNAVAILABLE",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": code_map.get(exc.status_code, "HTTP_ERROR"),
                    "message": str(exc.detail),
                    "details": [],
                    "request_id": str(uuid.uuid4()),
                }
            },
        )

    # 4. Global Unhandled Exception Handler (Never leaks SQL/stacktraces)
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server exception: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred. Please try again later.",
                    "details": [],
                    "request_id": str(uuid.uuid4()),
                }
            },
        )

    # Include API routers
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", tags=["root"], summary="Root service discovery")
    def root() -> dict[str, str]:
        """Root endpoint returning service identity and health links."""
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "status": "online",
            "health_url": f"{settings.api_v1_prefix}/health",
            "readiness_url": f"{settings.api_v1_prefix}/ready",
            "patients_url": f"{settings.api_v1_prefix}/patients",
            "docs_url": "/docs",
        }

    return app


app = create_application()
