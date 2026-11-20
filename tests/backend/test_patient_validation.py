"""Unit tests for patient validation rules and edge cases.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from app.schemas.patient import PatientCreate, PatientUpdate
from pydantic import ValidationError


def test_valid_patient_creation_schema() -> None:
    """Test valid patient creation payload with standard date format."""
    data = PatientCreate.model_validate(
        {
            "full_name": "Jordan Alpha",
            "date_of_birth": "1990-05-15",
            "email": "jordan.alpha@example.test",
            "glucose_value": 95.5,
            "haemoglobin_value": 14.2,
            "cholesterol_value": 185.0,
        }
    )
    assert data.full_name == "Jordan Alpha"
    assert data.date_of_birth == date(1990, 5, 15)
    assert data.email == "jordan.alpha@example.test"
    assert data.glucose_value == Decimal("95.5")
    assert data.haemoglobin_value == Decimal("14.2")
    assert data.cholesterol_value == Decimal("185.0")
    assert data.allow_duplicate is False


def test_both_date_separators_slash_and_dot() -> None:
    """Accept dd/mm/yyyy and dd.mm.yyyy formats per assignment requirement."""
    # Slash separator
    p_slash = PatientCreate.model_validate(
        {
            "full_name": "Slash Date",
            "date_of_birth": "24/08/1988",
            "email": "slash@example.test",
            "glucose_value": 90.0,
            "haemoglobin_value": 13.5,
            "cholesterol_value": 175.0,
        }
    )
    assert p_slash.date_of_birth == date(1988, 8, 24)

    # Dot separator
    p_dot = PatientCreate.model_validate(
        {
            "full_name": "Dot Date",
            "date_of_birth": "24.08.1988",
            "email": "dot@example.test",
            "glucose_value": 90.0,
            "haemoglobin_value": 13.5,
            "cholesterol_value": 175.0,
        }
    )
    assert p_dot.date_of_birth == date(1988, 8, 24)


def test_impossible_calendar_date_rejected() -> None:
    """Reject non-existent calendar dates (e.g. February 31)."""
    with pytest.raises(ValidationError) as exc:
        PatientCreate.model_validate(
            {
                "full_name": "Invalid Date",
                "date_of_birth": "31/02/1990",
                "email": "invalid.date@example.test",
                "glucose_value": 90.0,
                "haemoglobin_value": 14.0,
                "cholesterol_value": 180.0,
            }
        )
    assert "Invalid date format or impossible calendar date" in str(exc.value)


def test_future_dob_rejected() -> None:
    """Reject dates of birth later than the current runtime date."""
    future_date = (datetime.now(UTC).date() + timedelta(days=2)).strftime("%d/%m/%Y")
    with pytest.raises(ValidationError) as exc:
        PatientCreate.model_validate(
            {
                "full_name": "Future Date",
                "date_of_birth": future_date,
                "email": "future.date@example.test",
                "glucose_value": 90.0,
                "haemoglobin_value": 14.0,
                "cholesterol_value": 180.0,
            }
        )
    assert "Date of birth cannot be later than the current date" in str(exc.value)


def test_malformed_email_syntax_rejected() -> None:
    """Reject malformed email addresses."""
    invalid_emails = [
        "not-an-email",
        "missing@domain",
        "@missing-user.com",
        "user@.com",
        "user @example.com",
    ]
    for email in invalid_emails:
        with pytest.raises(ValidationError):
            PatientCreate.model_validate(
                {
                    "full_name": "Bad Email",
                    "date_of_birth": "15/05/1990",
                    "email": email,
                    "glucose_value": 90.0,
                    "haemoglobin_value": 14.0,
                    "cholesterol_value": 180.0,
                }
            )


def test_empty_or_whitespace_name_rejected() -> None:
    """Reject empty or whitespace-only full name."""
    with pytest.raises(ValidationError):
        PatientCreate.model_validate(
            {
                "full_name": "   ",
                "date_of_birth": "15/05/1990",
                "email": "valid@example.test",
                "glucose_value": 90.0,
                "haemoglobin_value": 14.0,
                "cholesterol_value": 180.0,
            }
        )


def test_negative_numeric_biomarkers_rejected() -> None:
    """Reject negative measurement values."""
    with pytest.raises(ValidationError) as exc:
        PatientCreate.model_validate(
            {
                "full_name": "Negative Glucose",
                "date_of_birth": "15/05/1990",
                "email": "valid@example.test",
                "glucose_value": -5.0,
                "haemoglobin_value": 14.0,
                "cholesterol_value": 180.0,
            }
        )
    assert "cannot be negative" in str(exc.value)


def test_non_numeric_and_nan_biomarkers_rejected() -> None:
    """Reject non-numeric strings, booleans, and NaN for biomarkers."""
    # Boolean rejected
    with pytest.raises(ValidationError):
        PatientCreate.model_validate(
            {
                "full_name": "Boolean Value",
                "date_of_birth": "15/05/1990",
                "email": "valid@example.test",
                "glucose_value": True,
                "haemoglobin_value": 14.0,
                "cholesterol_value": 180.0,
            }
        )

    # NaN rejected
    with pytest.raises(ValidationError):
        PatientCreate.model_validate(
            {
                "full_name": "NaN Value",
                "date_of_birth": "15/05/1990",
                "email": "valid@example.test",
                "glucose_value": "NaN",
                "haemoglobin_value": 14.0,
                "cholesterol_value": 180.0,
            }
        )


def test_patient_update_schema_partial_fields() -> None:
    """Verify PatientUpdate permits partial fields while validating provided ones."""
    # Valid partial email update
    update = PatientUpdate.model_validate({"email": "gokul@infocare.com"})
    assert update.email == "gokul@infocare.com"
    assert update.full_name is None
    assert update.glucose_value is None

    # Invalid DOB in update rejected
    with pytest.raises(ValidationError):
        PatientUpdate.model_validate({"date_of_birth": "32/01/1990"})
