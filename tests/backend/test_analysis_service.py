"""Integration and persistence tests for AnalysisService and TestWell execution.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from app.core.exceptions import AppException
from app.integrations.testwell.adapter import TestWellAdapter
from app.integrations.testwell.exceptions import TestWellConnectionError
from app.integrations.testwell.normalizer import (
    NormalizedObservation,
    NormalizedProviderResult,
    ProviderCitation,
)
from app.models.enums import AiStatus, ExternalStatus, OverallStatus
from app.models.patient import Patient
from app.models.patient_analysis import PatientAnalysis
from app.services.analysis_service import AnalysisService
from app.services.patient_service import PatientService
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def sample_patient_with_analysis(test_db_session: Session) -> tuple[Patient, PatientAnalysis]:
    """Create a sample patient and initial pending analysis run."""
    patient = Patient(
        full_name="Morgan Integrity",
        date_of_birth=date(1985, 6, 15),
        email="morgan.integrity@example.test",
        glucose_value=Decimal("94.0"),
        haemoglobin_value=Decimal("14.5"),
        cholesterol_value=Decimal("175.0"),
        unit_profile_code="ASSESSMENT_CONVENTIONAL_V1",
    )
    test_db_session.add(patient)
    test_db_session.flush()

    analysis = PatientAnalysis(
        patient_id=patient.id,
        run_number=1,
        input_snapshot_json={
            "glucose_value": 94.0,
            "glucose_unit": "mg/dL",
            "haemoglobin_value": 14.5,
            "haemoglobin_unit": "g/dL",
            "cholesterol_value": 175.0,
            "cholesterol_unit": "mg/dL",
            "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
        },
        external_provider="testwell",
        external_status=ExternalStatus.PENDING,
        ai_provider="ollama",
        ai_model="llama3.2:3b",
        ai_status=AiStatus.NOT_RUN,
        overall_status=OverallStatus.PENDING,
    )
    test_db_session.add(analysis)
    test_db_session.commit()
    test_db_session.refresh(patient)
    test_db_session.refresh(analysis)
    return patient, analysis


@pytest.mark.asyncio
async def test_execute_analysis_success(
    test_db_session: Session,
    sample_patient_with_analysis: tuple[Patient, PatientAnalysis],
) -> None:
    """Test successful TestWell analysis execution marks status and stores provenance."""
    patient, analysis = sample_patient_with_analysis
    bind = test_db_session.get_bind()
    factory = sessionmaker(bind=bind, autocommit=False, autoflush=False)

    # Mock adapter returning 3 matched observations
    mock_result = NormalizedProviderResult(
        provider="testwell",
        catalog_review_date="2026-09-05",
        reviewer="Dr. Reviewer",
        observations=[
            NormalizedObservation(
                analyte="glucose",
                query_marker="glucose",
                matched_marker="Glucose",
                value=94.0,
                unit="mg/dL",
                found=True,
                flag="normal",
                range_text="70 – 99 mg/dL",
                range_qualifier="age 18+, fasting",
                context_status="CONTEXT_NOT_CONFIRMED",
                citations=[ProviderCitation(label="ADA", url="https://diabetes.org")],
            ),
            NormalizedObservation(
                analyte="haemoglobin",
                query_marker="hemoglobin",
                matched_marker="Hemoglobin",
                value=14.5,
                unit="g/dL",
                found=True,
                flag="normal",
                range_text="13.5 – 17.5 g/dL",
                range_qualifier="Male, age 18+",
                context_status="CONTEXT_NOT_CONFIRMED",
            ),
            NormalizedObservation(
                analyte="cholesterol",
                query_marker="total cholesterol",
                matched_marker="Total Cholesterol",
                value=175.0,
                unit="mg/dL",
                found=True,
                flag="normal",
                range_text="125 – 200 mg/dL",
                range_qualifier="age 18+",
                context_status="CONTEXT_NOT_CONFIRMED",
            ),
        ],
        summary={"total": 3, "matched": 3, "high": 0, "low": 0, "normal": 3, "unknown": 0},
        latency_ms=150.0,
    )

    mock_adapter = TestWellAdapter()
    mock_adapter.interpret_biomarkers = AsyncMock(return_value=mock_result)  # type: ignore[method-assign]

    mock_generator = AsyncMock()
    mock_generator.generate_remarks = AsyncMock(
        return_value=(
            "Laboratory findings are consistent with expected reference intervals.",
            {"summary": "Laboratory findings are consistent.", "generation_label": "AI_GENERATED"},
            True,
            150.0,
        )
    )
    mock_generator.client = AsyncMock()
    mock_generator.client.model = "llama3.2:3b"

    updated = await AnalysisService.execute_analysis_run(
        analysis_id=analysis.id,
        adapter=mock_adapter,
        generator=mock_generator,
        session_factory=factory,
    )

    assert updated.external_status == ExternalStatus.SUCCEEDED
    assert updated.overall_status == OverallStatus.COMPLETED
    assert updated.ai_status == AiStatus.SUCCEEDED
    assert updated.remarks_text is not None
    assert "consistent" in updated.remarks_text
    assert updated.external_result_json is not None
    assert updated.external_result_json["summary"]["matched"] == 3
    assert updated.completed_at is not None
    assert updated.started_at is not None
    assert updated.error_code is None


@pytest.mark.asyncio
async def test_execute_analysis_provider_failure(
    test_db_session: Session,
    sample_patient_with_analysis: tuple[Patient, PatientAnalysis],
) -> None:
    """Test provider connection failure persists FAILED status with error metadata."""
    patient, analysis = sample_patient_with_analysis
    bind = test_db_session.get_bind()
    factory = sessionmaker(bind=bind, autocommit=False, autoflush=False)

    mock_adapter = TestWellAdapter()
    mock_adapter.interpret_biomarkers = AsyncMock(  # type: ignore[method-assign]
        side_effect=TestWellConnectionError("Failed to connect to TestWell.")
    )

    updated = await AnalysisService.execute_analysis_run(
        analysis_id=analysis.id,
        adapter=mock_adapter,
        session_factory=factory,
    )

    assert updated.external_status == ExternalStatus.FAILED
    assert updated.overall_status == OverallStatus.FAILED
    assert updated.ai_status == AiStatus.NOT_RUN
    assert updated.error_code == "TESTWELL_CONNECTION_FAILED"
    assert "Failed to connect" in str(updated.error_summary)
    assert updated.completed_at is not None


@pytest.mark.asyncio
async def test_execute_analysis_partial_match_degraded(
    test_db_session: Session,
    sample_patient_with_analysis: tuple[Patient, PatientAnalysis],
) -> None:
    """Test partial match marks overall_status as DEGRADED."""
    patient, analysis = sample_patient_with_analysis
    bind = test_db_session.get_bind()
    factory = sessionmaker(bind=bind, autocommit=False, autoflush=False)

    mock_result = NormalizedProviderResult(
        provider="testwell",
        observations=[
            NormalizedObservation(
                analyte="glucose",
                query_marker="glucose",
                matched_marker="Glucose",
                value=94.0,
                unit="mg/dL",
                found=True,
                flag="normal",
            ),
            NormalizedObservation(
                analyte="haemoglobin",
                query_marker="hemoglobin",
                matched_marker=None,
                value=14.5,
                unit="g/dL",
                found=False,
                flag="unknown",
            ),
        ],
        summary={"total": 2, "matched": 1, "unknown": 1},
    )

    mock_adapter = TestWellAdapter()
    mock_adapter.interpret_biomarkers = AsyncMock(return_value=mock_result)  # type: ignore[method-assign]

    mock_generator = AsyncMock()
    mock_generator.generate_remarks = AsyncMock(
        return_value=(
            "Partial observation findings.",
            {"summary": "Partial observation findings.", "generation_label": "AI_GENERATED"},
            True,
            120.0,
        )
    )
    mock_generator.client = AsyncMock()
    mock_generator.client.model = "llama3.2:3b"

    updated = await AnalysisService.execute_analysis_run(
        analysis_id=analysis.id,
        adapter=mock_adapter,
        generator=mock_generator,
        session_factory=factory,
    )

    assert updated.external_status == ExternalStatus.SUCCEEDED
    assert updated.overall_status == OverallStatus.DEGRADED
    assert updated.error_code == "PARTIAL_PROVIDER_MATCH"


@pytest.mark.asyncio
async def test_execute_analysis_ollama_fallback_marks_degraded(
    test_db_session: Session,
    sample_patient_with_analysis: tuple[Patient, PatientAnalysis],
) -> None:
    """When Ollama fails, analysis completes in DEGRADED status with AI_FALLBACK_APPLIED."""
    patient, analysis = sample_patient_with_analysis
    bind = test_db_session.get_bind()
    factory = sessionmaker(bind=bind, autocommit=False, autoflush=False)

    mock_result = NormalizedProviderResult(
        provider="testwell",
        observations=[
            NormalizedObservation(
                analyte="glucose",
                query_marker="glucose",
                matched_marker="Glucose",
                value=94.0,
                unit="mg/dL",
                found=True,
                flag="normal",
            )
        ],
        summary={"total": 1, "matched": 1, "normal": 1},
    )

    mock_adapter = TestWellAdapter()
    mock_adapter.interpret_biomarkers = AsyncMock(return_value=mock_result)  # type: ignore[method-assign]

    # Generator returns deterministic fallback (is_ai_generated=False)
    mock_generator = AsyncMock()
    mock_generator.generate_remarks = AsyncMock(
        return_value=(
            "Deterministic fallback remarks.",
            {"summary": "Fallback text", "generation_label": "DETERMINISTIC_FALLBACK"},
            False,
            20.0,
        )
    )
    mock_generator.client = AsyncMock()
    mock_generator.client.model = "llama3.2:3b"

    updated = await AnalysisService.execute_analysis_run(
        analysis_id=analysis.id,
        adapter=mock_adapter,
        generator=mock_generator,
        session_factory=factory,
    )

    assert updated.external_status == ExternalStatus.SUCCEEDED
    assert updated.overall_status == OverallStatus.DEGRADED
    assert updated.ai_status == AiStatus.FALLBACK
    assert updated.error_code == "AI_FALLBACK_APPLIED"
    assert updated.remarks_text == "Deterministic fallback remarks."
    assert updated.ai_result_json is not None
    assert updated.ai_result_json["generation_label"] == "DETERMINISTIC_FALLBACK"


def test_create_retry_analysis_lineage_and_preservation(
    test_db_session: Session,
    sample_patient_with_analysis: tuple[Patient, PatientAnalysis],
) -> None:
    """Creating a retry appends run_number 2, points retry_of_id to run 1, and preserves run 1."""
    patient, analysis_run_1 = sample_patient_with_analysis

    # Mark run 1 as failed/terminal so retry is permitted
    analysis_run_1.external_status = ExternalStatus.FAILED
    analysis_run_1.overall_status = OverallStatus.FAILED
    test_db_session.commit()

    run_2 = AnalysisService.create_retry_analysis(test_db_session, patient.id)

    assert run_2.run_number == 2
    assert run_2.retry_of_id == analysis_run_1.id
    assert run_2.overall_status == OverallStatus.PENDING
    assert run_2.external_status == ExternalStatus.PENDING

    # Verify both records exist in DB
    all_runs = test_db_session.scalars(
        select(PatientAnalysis).where(PatientAnalysis.patient_id == patient.id)
    ).all()
    assert len(all_runs) == 2


def test_retry_guard_prevents_concurrent_runs(
    test_db_session: Session,
    sample_patient_with_analysis: tuple[Patient, PatientAnalysis],
) -> None:
    """When an analysis is actively running, attempting a retry raises HTTP 409 conflict."""
    patient, analysis = sample_patient_with_analysis
    # Mark analysis as actively started
    from app.models.base import get_utc_now

    analysis.started_at = get_utc_now()
    test_db_session.commit()

    with pytest.raises(AppException) as exc_info:
        AnalysisService.create_retry_analysis(test_db_session, patient.id)

    assert exc_info.value.status_code == 409
    assert exc_info.value.code == "ANALYSIS_IN_PROGRESS"


def test_cascade_delete_removes_all_analysis_records(
    test_db_session: Session,
    sample_patient_with_analysis: tuple[Patient, PatientAnalysis],
) -> None:
    """Deleting patient cascades and deletes all related analysis history rows."""
    patient, analysis = sample_patient_with_analysis
    patient_id = patient.id
    analysis_id = analysis.id

    PatientService.delete_patient(test_db_session, patient_id)

    assert test_db_session.scalar(select(Patient).where(Patient.id == patient_id)) is None
    assert (
        test_db_session.scalar(select(PatientAnalysis).where(PatientAnalysis.id == analysis_id))
        is None
    )
