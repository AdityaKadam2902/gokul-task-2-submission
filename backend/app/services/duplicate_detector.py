"""Duplicate record detection and canonical fingerprint generation.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import hashlib
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.patient import Patient


def format_decimal_canonical(val: Decimal | float | str) -> str:
    """Format Decimal into canonical fixed 3-decimal string representation."""
    d = Decimal(str(val))
    return f"{d:.3f}"


def compute_duplicate_fingerprint(
    full_name: str,
    date_of_birth: date,
    email: str,
    glucose_value: Decimal | float | str,
    haemoglobin_value: Decimal | float | str,
    cholesterol_value: Decimal | float | str,
    unit_profile_code: str,
) -> str:
    """Compute deterministic SHA-256 fingerprint from canonical patient identity & measurement values."""
    canonical_string = "|".join(
        [
            full_name.strip().casefold(),
            date_of_birth.isoformat(),
            email.strip().lower(),
            format_decimal_canonical(glucose_value),
            format_decimal_canonical(haemoglobin_value),
            format_decimal_canonical(cholesterol_value),
            unit_profile_code.strip(),
        ]
    )
    return hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()


def find_duplicate_patient(
    db: Session,
    full_name: str,
    date_of_birth: date,
    email: str,
    glucose_value: Decimal | float | str,
    haemoglobin_value: Decimal | float | str,
    cholesterol_value: Decimal | float | str,
    unit_profile_code: str,
    exclude_patient_id: int | None = None,
) -> Patient | None:
    """Check if an exact canonical match already exists in the database.

    Excludes the specified patient_id when checking during PATCH updates.
    Returns matching Patient instance if found, or None.
    """
    target_fingerprint = compute_duplicate_fingerprint(
        full_name=full_name,
        date_of_birth=date_of_birth,
        email=email,
        glucose_value=glucose_value,
        haemoglobin_value=haemoglobin_value,
        cholesterol_value=cholesterol_value,
        unit_profile_code=unit_profile_code,
    )

    # Candidate query matching email (case-insensitive) and date_of_birth
    stmt = select(Patient).where(
        func.lower(Patient.email) == email.strip().lower(),
        Patient.date_of_birth == date_of_birth,
    )
    if exclude_patient_id is not None:
        stmt = stmt.where(Patient.id != exclude_patient_id)

    candidates = db.scalars(stmt).all()

    for candidate in candidates:
        candidate_fp = compute_duplicate_fingerprint(
            full_name=candidate.full_name,
            date_of_birth=candidate.date_of_birth,
            email=candidate.email,
            glucose_value=candidate.glucose_value,
            haemoglobin_value=candidate.haemoglobin_value,
            cholesterol_value=candidate.cholesterol_value,
            unit_profile_code=candidate.unit_profile_code,
        )
        if candidate_fp == target_fingerprint:
            return candidate

    return None
