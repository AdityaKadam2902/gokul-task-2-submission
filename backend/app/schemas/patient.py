"""Pydantic schemas for Patient CRUD requests, responses, and validation.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from email_validator import EmailNotValidError, validate_email
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    computed_field,
    field_validator,
)

from app.models.enums import OverallStatus
from app.schemas.analysis import AnalysisSummary


def parse_flexible_date(v: Any) -> date:
    """Parse calendar date supporting YYYY-MM-DD, dd/mm/yyyy, and dd.mm.yyyy formats."""
    target_date: date
    if isinstance(v, date):
        target_date = v
    elif isinstance(v, str):
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Date of birth cannot be empty.")

        parsed_date: date | None = None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y"):
            try:
                parsed_date = datetime.strptime(cleaned, fmt).date()
                break
            except ValueError:
                continue

        if parsed_date is None:
            raise ValueError(
                "Invalid date format or impossible calendar date. Expected dd/mm/yyyy or dd.mm.yyyy."
            )
        target_date = parsed_date
    else:
        raise ValueError("Invalid date value.")

    today = datetime.now(UTC).date()
    if target_date > today:
        raise ValueError("Date of birth cannot be later than the current date.")

    return target_date


def validate_email_syntax(v: Any) -> str:
    """Validate standards-compliant email syntax without DNS deliverability checks.

    Allows valid test environments and prevents arbitrary domain restrictions.
    """
    if not isinstance(v, str):
        raise ValueError("Email must be a string.")
    cleaned = v.strip().lower()
    if not cleaned:
        raise ValueError("Email is required.")
    if len(cleaned) > 254:
        raise ValueError("Email cannot exceed 254 characters.")

    try:
        validated = validate_email(cleaned, check_deliverability=False, test_environment=True)
        return str(validated.normalized)
    except EmailNotValidError as exc:
        raise ValueError(f"Invalid email address: {exc}") from None


def validate_biomarker_value(v: Any, info: ValidationInfo) -> Decimal:
    """Validate numeric biomarker measurement: must be finite, non-negative, and decimal-precise."""
    if v is None:
        raise ValueError(f"{info.field_name} is required.")
    if isinstance(v, bool):
        raise ValueError(f"{info.field_name} must be a number, not a boolean.")

    try:
        dec = Decimal(str(v).strip())
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{info.field_name} must be a valid numeric value.") from None

    if dec.is_nan() or dec.is_infinite():
        raise ValueError(f"{info.field_name} must be a finite number.")

    if dec < Decimal("0"):
        raise ValueError(f"{info.field_name} cannot be negative.")

    return dec


class PatientBase(BaseModel):
    """Shared patient attributes."""

    full_name: str = Field(..., min_length=1, max_length=120)
    date_of_birth: date
    email: str = Field(..., max_length=254)
    glucose_value: Decimal = Field(..., description="Glucose measurement in mg/dL")
    haemoglobin_value: Decimal = Field(..., description="Haemoglobin measurement in g/dL")
    cholesterol_value: Decimal = Field(..., description="Cholesterol measurement in mg/dL")
    unit_profile_code: str = Field(
        default="ASSESSMENT_CONVENTIONAL_V1",
        max_length=40,
        description="Configured measurement unit profile",
    )

    @field_validator("full_name", mode="before")
    @classmethod
    def clean_full_name(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("Full name must be a string.")
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Full name is required and cannot be whitespace-only.")
        if len(trimmed) > 120:
            raise ValueError("Full name cannot exceed 120 characters.")
        return trimmed

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def parse_dob(cls, v: Any) -> date:
        return parse_flexible_date(v)

    @field_validator("email", mode="before")
    @classmethod
    def clean_email(cls, v: Any) -> str:
        return validate_email_syntax(v)

    @field_validator("glucose_value", "haemoglobin_value", "cholesterol_value", mode="before")
    @classmethod
    def check_biomarker(cls, v: Any, info: ValidationInfo) -> Decimal:
        return validate_biomarker_value(v, info)


class PatientCreate(PatientBase):
    """Payload for creating a patient record (POST /api/v1/patients)."""

    allow_duplicate: bool = Field(
        default=False,
        description="Set to true to explicitly confirm insertion of a duplicate record",
    )


class PatientUpdate(BaseModel):
    """Payload for updating an existing patient record (PATCH /api/v1/patients/{id})."""

    full_name: str | None = None
    date_of_birth: date | None = None
    email: str | None = None
    glucose_value: Decimal | None = None
    haemoglobin_value: Decimal | None = None
    cholesterol_value: Decimal | None = None
    unit_profile_code: str | None = None
    allow_duplicate: bool = Field(
        default=False,
        description="Set to true to confirm update when resulting record matches another patient",
    )

    @field_validator("full_name", mode="before")
    @classmethod
    def clean_full_name(cls, v: Any) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Full name must be a string.")
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Full name cannot be empty or whitespace-only.")
        if len(trimmed) > 120:
            raise ValueError("Full name cannot exceed 120 characters.")
        return trimmed

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def parse_dob(cls, v: Any) -> date | None:
        if v is None:
            return None
        return parse_flexible_date(v)

    @field_validator("email", mode="before")
    @classmethod
    def clean_email(cls, v: Any) -> str | None:
        if v is None:
            return None
        return validate_email_syntax(v)

    @field_validator("glucose_value", "haemoglobin_value", "cholesterol_value", mode="before")
    @classmethod
    def check_biomarker(cls, v: Any, info: ValidationInfo) -> Decimal | None:
        if v is None:
            return None
        return validate_biomarker_value(v, info)


class PatientResponse(PatientBase):
    """Full patient record response including technical identifiers and latest analysis."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    latest_analysis: AnalysisSummary | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def current_analysis(self) -> AnalysisSummary | None:
        """Alias for latest_analysis to satisfy frontend and client expectations."""
        return self.latest_analysis


class PatientListItem(BaseModel):
    """Summarized patient item for paginated directory lists."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    date_of_birth: date
    email: str
    glucose_value: Decimal
    haemoglobin_value: Decimal
    cholesterol_value: Decimal
    unit_profile_code: str
    created_at: datetime
    updated_at: datetime
    latest_analysis_status: OverallStatus | None = None
    latest_remarks: str | None = None


class PatientListResponse(BaseModel):
    """Paginated collection of patient records."""

    items: list[PatientListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
