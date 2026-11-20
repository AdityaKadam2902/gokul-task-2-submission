"""Comprehensive tests for Patient and PatientAnalysis domain models.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from datetime import date
from decimal import Decimal

import pytest
from app.models.enums import AiStatus, ExternalStatus, OverallStatus
from app.models.patient import Patient
from app.models.patient_analysis import PatientAnalysis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def test_patient_model_creation_and_retrieval(test_db_session: Session) -> None:
    """Test successful patient insertion, retrieval, and field persistence."""
    patient = Patient(
        full_name="Alex Benchmark",
        date_of_birth=date(1992, 5, 20),
        email="alex.benchmark@example.test",
        glucose_value=Decimal("94.500"),
        haemoglobin_value=Decimal("13.800"),
        cholesterol_value=Decimal("175.250"),
        unit_profile_code="ASSESSMENT_CONVENTIONAL_V1",
    )
    test_db_session.add(patient)
    test_db_session.commit()
    test_db_session.refresh(patient)

    assert patient.id is not None
    assert patient.full_name == "Alex Benchmark"
    assert patient.date_of_birth == date(1992, 5, 20)
    assert patient.email == "alex.benchmark@example.test"
    assert patient.glucose_value == Decimal("94.500")
    assert patient.haemoglobin_value == Decimal("13.800")
    assert patient.cholesterol_value == Decimal("175.250")
    assert patient.unit_profile_code == "ASSESSMENT_CONVENTIONAL_V1"
    assert patient.created_at is not None
    assert patient.updated_at is not None


def test_patient_decimal_precision_preservation(test_db_session: Session) -> None:
    """Verify numeric biomarker values preserve exact 3-decimal precision."""
    patient = Patient(
        full_name="Decimal Precision Test",
        date_of_birth=date(1985, 11, 10),
        email="decimal.test@example.test",
        glucose_value=Decimal("105.125"),
        haemoglobin_value=Decimal("14.375"),
        cholesterol_value=Decimal("199.875"),
    )
    test_db_session.add(patient)
    test_db_session.commit()

    retrieved = test_db_session.scalar(
        select(Patient).where(Patient.email == "decimal.test@example.test")
    )
    assert retrieved is not None
    assert isinstance(retrieved.glucose_value, Decimal)
    assert retrieved.glucose_value == Decimal("105.125")
    assert retrieved.haemoglobin_value == Decimal("14.375")
    assert retrieved.cholesterol_value == Decimal("199.875")


def test_duplicate_patient_records_permitted(test_db_session: Session) -> None:
    """Verify that multiple patients with identical email and measurements can be inserted.

    The employer specification explicitly permits confirmed duplicate record insertion.
    """
    patient1 = Patient(
        full_name="Jordan Duplicate",
        date_of_birth=date(1990, 1, 15),
        email="jordan.duplicate@example.test",
        glucose_value=Decimal("92.000"),
        haemoglobin_value=Decimal("14.000"),
        cholesterol_value=Decimal("180.000"),
    )
    patient2 = Patient(
        full_name="Jordan Duplicate",
        date_of_birth=date(1990, 1, 15),
        email="jordan.duplicate@example.test",
        glucose_value=Decimal("92.000"),
        haemoglobin_value=Decimal("14.000"),
        cholesterol_value=Decimal("180.000"),
    )
    test_db_session.add(patient1)
    test_db_session.add(patient2)
    test_db_session.commit()

    assert patient1.id != patient2.id
    duplicates = test_db_session.scalars(
        select(Patient).where(Patient.email == "jordan.duplicate@example.test")
    ).all()
    assert len(duplicates) == 2


def test_patient_analysis_creation_and_relationship(test_db_session: Session) -> None:
    """Test PatientAnalysis creation, status enums, JSON snapshot, and patient relationship."""
    patient = Patient(
        full_name="Taylor Relationship",
        date_of_birth=date(1987, 8, 22),
        email="taylor.rel@example.test",
        glucose_value=Decimal("95.000"),
        haemoglobin_value=Decimal("14.500"),
        cholesterol_value=Decimal("185.000"),
    )
    test_db_session.add(patient)
    test_db_session.commit()
    test_db_session.refresh(patient)

    input_snapshot = {
        "glucose": {"value": 95.0, "unit": "mg/dL"},
        "haemoglobin": {"value": 14.5, "unit": "g/dL"},
        "cholesterol": {"value": 185.0, "unit": "mg/dL"},
        "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
    }

    analysis = PatientAnalysis(
        patient_id=patient.id,
        run_number=1,
        input_snapshot_json=input_snapshot,
        external_provider="testwell",
        external_status=ExternalStatus.SUCCEEDED,
        external_result_json={"provider_flag": "normal"},
        ai_provider="ollama",
        ai_model="llama3.2:3b",
        ai_status=AiStatus.SUCCEEDED,
        ai_result_json={"remarks": "Biomarkers are within normal expected ranges."},
        remarks_text="Biomarkers are within normal expected ranges.",
        overall_status=OverallStatus.COMPLETED,
    )
    test_db_session.add(analysis)
    test_db_session.commit()
    test_db_session.refresh(patient)

    assert len(patient.analyses) == 1
    assert patient.analyses[0].id == analysis.id
    assert patient.analyses[0].run_number == 1
    assert patient.analyses[0].overall_status == OverallStatus.COMPLETED
    assert patient.analyses[0].input_snapshot_json == input_snapshot
    assert "full_name" not in patient.analyses[0].input_snapshot_json


def test_multiple_analyses_per_patient_and_unique_run_number(
    test_db_session: Session,
) -> None:
    """Test sequential multiple analysis runs and unique constraint on (patient_id, run_number)."""
    patient = Patient(
        full_name="Morgan Runs",
        date_of_birth=date(1994, 3, 30),
        email="morgan.runs@example.test",
        glucose_value=Decimal("88.000"),
        haemoglobin_value=Decimal("13.500"),
        cholesterol_value=Decimal("170.000"),
    )
    test_db_session.add(patient)
    test_db_session.commit()

    run1 = PatientAnalysis(
        patient_id=patient.id,
        run_number=1,
        input_snapshot_json={"glucose": 88.0},
        overall_status=OverallStatus.FAILED,
        error_code="PROVIDER_TIMEOUT",
    )
    test_db_session.add(run1)
    test_db_session.flush()

    run2 = PatientAnalysis(
        patient_id=patient.id,
        run_number=2,
        input_snapshot_json={"glucose": 88.0},
        overall_status=OverallStatus.COMPLETED,
        retry_of_id=run1.id,
    )
    test_db_session.add(run2)
    test_db_session.commit()

    test_db_session.refresh(patient)
    assert len(patient.analyses) == 2
    assert patient.analyses[0].run_number == 1
    assert patient.analyses[1].run_number == 2
    assert patient.analyses[1].retry_of_id == run1.id

    # Attempting duplicate run_number for the same patient must raise IntegrityError
    duplicate_run = PatientAnalysis(
        patient_id=patient.id,
        run_number=1,
        input_snapshot_json={"glucose": 88.0},
    )
    test_db_session.add(duplicate_run)
    with pytest.raises(IntegrityError):
        test_db_session.commit()
    test_db_session.rollback()


def test_cascade_deletion_of_patient_analyses(test_db_session: Session) -> None:
    """Verify deleting a patient cascades and deletes all associated analyses."""
    patient = Patient(
        full_name="Casey Cascade",
        date_of_birth=date(1989, 7, 12),
        email="casey.cascade@example.test",
        glucose_value=Decimal("90.000"),
        haemoglobin_value=Decimal("14.000"),
        cholesterol_value=Decimal("180.000"),
    )
    test_db_session.add(patient)
    test_db_session.commit()

    analysis = PatientAnalysis(
        patient_id=patient.id,
        run_number=1,
        input_snapshot_json={"glucose": 90.0},
        overall_status=OverallStatus.COMPLETED,
    )
    test_db_session.add(analysis)
    test_db_session.commit()
    analysis_id = analysis.id

    # Delete the patient
    test_db_session.delete(patient)
    test_db_session.commit()

    # The patient is deleted
    assert test_db_session.get(Patient, patient.id) is None
    # The associated analysis must also be deleted via cascade
    assert test_db_session.get(PatientAnalysis, analysis_id) is None
