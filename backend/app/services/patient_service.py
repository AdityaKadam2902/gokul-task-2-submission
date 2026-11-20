"""Patient business logic service handling CRUD, validation, and analysis run lifecycle.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import math
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateRecordException, ResourceNotFoundException
from app.models.enums import AiStatus, ExternalStatus, OverallStatus
from app.models.patient import Patient
from app.models.patient_analysis import PatientAnalysis
from app.schemas.patient import PatientCreate, PatientUpdate
from app.services.duplicate_detector import find_duplicate_patient


def build_anonymous_input_snapshot(
    glucose_value: Decimal | float,
    haemoglobin_value: Decimal | float,
    cholesterol_value: Decimal | float,
    unit_profile_code: str,
) -> dict[str, Any]:
    """Construct anonymous biomarker measurement snapshot.

    Strict Privacy Rule: Never include patient names, emails, or DOB in analysis snapshots.
    """
    return {
        "glucose": {"value": float(glucose_value), "unit": "mg/dL"},
        "haemoglobin": {"value": float(haemoglobin_value), "unit": "g/dL"},
        "cholesterol": {"value": float(cholesterol_value), "unit": "mg/dL"},
        "unit_profile_code": unit_profile_code,
    }


def get_latest_analysis(patient: Patient) -> PatientAnalysis | None:
    """Return the most recent analysis run for a patient, if any."""
    if not patient.analyses:
        return None
    return max(patient.analyses, key=lambda a: a.run_number)


class PatientService:
    """Service orchestrating patient record persistence and analysis run lifecycle."""

    @staticmethod
    def create_patient(db: Session, data: PatientCreate) -> tuple[Patient, PatientAnalysis]:
        """Validate, check duplicates, persist patient record, and initialize analysis run.

        Raises DuplicateRecordException (HTTP 409) if duplicate is detected and allow_duplicate=False.
        """
        # 1. Duplicate check
        existing_duplicate = find_duplicate_patient(
            db=db,
            full_name=data.full_name,
            date_of_birth=data.date_of_birth,
            email=data.email,
            glucose_value=data.glucose_value,
            haemoglobin_value=data.haemoglobin_value,
            cholesterol_value=data.cholesterol_value,
            unit_profile_code=data.unit_profile_code,
        )

        if existing_duplicate is not None and not data.allow_duplicate:
            raise DuplicateRecordException(existing_patient_id=existing_duplicate.id)

        # 2. Persist patient entity
        patient = Patient(
            full_name=data.full_name,
            date_of_birth=data.date_of_birth,
            email=data.email,
            glucose_value=data.glucose_value,
            haemoglobin_value=data.haemoglobin_value,
            cholesterol_value=data.cholesterol_value,
            unit_profile_code=data.unit_profile_code,
        )
        db.add(patient)
        db.flush()  # Populates patient.id

        # 3. Create initial pending analysis record (truthful initial state)
        snapshot = build_anonymous_input_snapshot(
            glucose_value=data.glucose_value,
            haemoglobin_value=data.haemoglobin_value,
            cholesterol_value=data.cholesterol_value,
            unit_profile_code=data.unit_profile_code,
        )

        analysis = PatientAnalysis(
            patient_id=patient.id,
            run_number=1,
            input_snapshot_json=snapshot,
            external_provider="testwell",
            external_status=ExternalStatus.PENDING,
            ai_provider="ollama",
            ai_model="llama3.2:3b",
            ai_status=AiStatus.NOT_RUN,
            overall_status=OverallStatus.PENDING,
        )
        db.add(analysis)
        db.commit()
        db.refresh(patient)
        db.refresh(analysis)

        return patient, analysis

    @staticmethod
    def get_patient_by_id(db: Session, patient_id: int) -> Patient:
        """Retrieve patient by ID; raises ResourceNotFoundException if missing."""
        patient = db.get(Patient, patient_id)
        if patient is None:
            raise ResourceNotFoundException("Patient", patient_id)
        return patient

    @staticmethod
    def list_patients(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> tuple[list[Patient], int, int]:
        """Retrieve paginated patient records with stable ordering (created_at DESC, id DESC)."""
        page = max(1, page)
        page_size = max(1, min(100, page_size))

        stmt = select(Patient)

        if search:
            clean_search = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Patient.full_name.ilike(clean_search),
                    Patient.email.ilike(clean_search),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        # Pagination & stable sort
        offset = (page - 1) * page_size
        items = db.scalars(
            stmt.order_by(Patient.created_at.desc(), Patient.id.desc())
            .offset(offset)
            .limit(page_size)
        ).all()

        return list(items), total, total_pages

    @staticmethod
    def update_patient(
        db: Session,
        patient_id: int,
        data: PatientUpdate,
    ) -> tuple[Patient, PatientAnalysis | None]:
        """Update patient fields with whole-record revalidation and duplicate detection.

        Name/email-only updates do not invalidate analysis or create new analysis runs.
        Clinical input updates (DOB or measurements) create a fresh PENDING analysis run.
        """
        patient = PatientService.get_patient_by_id(db, patient_id)

        # Resolve merged effective values
        eff_name = data.full_name if data.full_name is not None else patient.full_name
        eff_dob = data.date_of_birth if data.date_of_birth is not None else patient.date_of_birth
        eff_email = data.email if data.email is not None else patient.email
        eff_glucose = (
            data.glucose_value if data.glucose_value is not None else patient.glucose_value
        )
        eff_haemoglobin = (
            data.haemoglobin_value
            if data.haemoglobin_value is not None
            else patient.haemoglobin_value
        )
        eff_cholesterol = (
            data.cholesterol_value
            if data.cholesterol_value is not None
            else patient.cholesterol_value
        )
        eff_unit_profile = (
            data.unit_profile_code
            if data.unit_profile_code is not None
            else patient.unit_profile_code
        )

        # Duplicate check against other patients
        existing_duplicate = find_duplicate_patient(
            db=db,
            full_name=eff_name,
            date_of_birth=eff_dob,
            email=eff_email,
            glucose_value=eff_glucose,
            haemoglobin_value=eff_haemoglobin,
            cholesterol_value=eff_cholesterol,
            unit_profile_code=eff_unit_profile,
            exclude_patient_id=patient_id,
        )

        if existing_duplicate is not None and not data.allow_duplicate:
            raise DuplicateRecordException(existing_patient_id=existing_duplicate.id)

        # Check if clinical inputs changed
        clinical_changed = any(
            [
                data.date_of_birth is not None and data.date_of_birth != patient.date_of_birth,
                data.glucose_value is not None and data.glucose_value != patient.glucose_value,
                data.haemoglobin_value is not None
                and data.haemoglobin_value != patient.haemoglobin_value,
                data.cholesterol_value is not None
                and data.cholesterol_value != patient.cholesterol_value,
                data.unit_profile_code is not None
                and data.unit_profile_code != patient.unit_profile_code,
            ]
        )

        # Apply updates
        if data.full_name is not None:
            patient.full_name = data.full_name
        if data.date_of_birth is not None:
            patient.date_of_birth = data.date_of_birth
        if data.email is not None:
            patient.email = data.email
        if data.glucose_value is not None:
            patient.glucose_value = data.glucose_value
        if data.haemoglobin_value is not None:
            patient.haemoglobin_value = data.haemoglobin_value
        if data.cholesterol_value is not None:
            patient.cholesterol_value = data.cholesterol_value
        if data.unit_profile_code is not None:
            patient.unit_profile_code = data.unit_profile_code

        new_analysis = None
        if clinical_changed:
            # Create a fresh PENDING analysis run preserving previous runs in history
            highest_run = max([a.run_number for a in patient.analyses], default=0)
            snapshot = build_anonymous_input_snapshot(
                glucose_value=eff_glucose,
                haemoglobin_value=eff_haemoglobin,
                cholesterol_value=eff_cholesterol,
                unit_profile_code=eff_unit_profile,
            )
            new_analysis = PatientAnalysis(
                patient_id=patient.id,
                run_number=highest_run + 1,
                input_snapshot_json=snapshot,
                external_provider="testwell",
                external_status=ExternalStatus.PENDING,
                ai_provider="ollama",
                ai_model="llama3.2:3b",
                ai_status=AiStatus.NOT_RUN,
                overall_status=OverallStatus.PENDING,
            )
            db.add(new_analysis)

        db.commit()
        db.refresh(patient)
        if new_analysis is not None:
            db.refresh(new_analysis)

        return patient, (new_analysis or get_latest_analysis(patient))

    @staticmethod
    def delete_patient(db: Session, patient_id: int) -> None:
        """Delete patient record and cascade its entire analysis history."""
        patient = PatientService.get_patient_by_id(db, patient_id)
        db.delete(patient)
        db.commit()

    @staticmethod
    def list_analyses_for_patient(db: Session, patient_id: int) -> list[PatientAnalysis]:
        """Return all analysis runs for a patient ordered newest-first."""
        # Ensure patient exists
        PatientService.get_patient_by_id(db, patient_id)
        stmt = (
            select(PatientAnalysis)
            .where(PatientAnalysis.patient_id == patient_id)
            .order_by(PatientAnalysis.run_number.desc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_analysis_by_id(db: Session, patient_id: int, analysis_id: str) -> PatientAnalysis:
        """Return specific analysis run for a patient."""
        # Ensure patient exists
        PatientService.get_patient_by_id(db, patient_id)
        stmt = select(PatientAnalysis).where(
            PatientAnalysis.patient_id == patient_id,
            PatientAnalysis.id == analysis_id,
        )
        analysis = db.scalar(stmt)
        if analysis is None:
            raise ResourceNotFoundException("PatientAnalysis", analysis_id)
        return analysis
