"""Services package."""

from app.services.duplicate_detector import (
    compute_duplicate_fingerprint,
    find_duplicate_patient,
)
from app.services.patient_service import PatientService

__all__ = [
    "PatientService",
    "compute_duplicate_fingerprint",
    "find_duplicate_patient",
]
