"""Domain exceptions and API error classes.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from typing import Any


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str,
        code: str = "APPLICATION_ERROR",
        status_code: int = 400,
        details: list[dict[str, Any]] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []


class ResourceNotFoundException(AppException):
    """Raised when a requested resource does not exist (HTTP 404)."""

    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' was not found.",
            code="NOT_FOUND",
            status_code=404,
            details=[
                {
                    "field": "id",
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"No {resource_type.lower()} exists with ID {resource_id}.",
                }
            ],
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class DuplicateRecordException(AppException):
    """Raised when an identical patient record is detected without confirmation (HTTP 409)."""

    def __init__(self, existing_patient_id: int, message: str | None = None):
        msg = (
            message
            or f"An identical patient record (ID: {existing_patient_id}) already exists. "
            "Confirm to proceed with inserting a separate duplicate record."
        )
        super().__init__(
            message=msg,
            code="DUPLICATE_RECORD",
            status_code=409,
            details=[
                {
                    "field": "record",
                    "code": "DUPLICATE_CONFIRMATION_REQUIRED",
                    "message": (
                        f"An identical record exists with ID {existing_patient_id}. "
                        "Resubmit with allow_duplicate=true to confirm insertion."
                    ),
                    "existing_patient_id": existing_patient_id,
                }
            ],
        )
        self.existing_patient_id = existing_patient_id
