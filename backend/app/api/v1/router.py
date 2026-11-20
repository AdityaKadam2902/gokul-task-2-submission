"""API v1 Central Router.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, meta, patients

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(meta.router)
api_router.include_router(patients.router)
