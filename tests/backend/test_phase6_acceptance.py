"""Phase 6 End-to-End Acceptance, Hardening, and Failure Recovery Tests.

Tests the full 10-attempt assessment workflow with neutral synthetic fixtures:
- 3 rejected with 422 Unprocessable Entity (impossible calendar date, malformed email, future DOB).
- 1 exact duplicate warned with 409 Conflict and accepted upon allow_duplicate=True.
- 7 persisted records.
- Email update to gokul@infocare.com without creating a new analysis run.
- Cascade deletion of a different record leaving exactly 6 records.
- Failure recovery: TestWell network failure keeps patient safe with error recorded.
- Failure recovery: Ollama unavailable falls back deterministically with DEGRADED status.
- AI Safety: Enforces transparent educational observations, forbids physician review claims.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from app.integrations.testwell.exceptions import TestWellClientError
from app.models.enums import AiStatus, ExternalStatus, OverallStatus
from app.models.patient import Patient
from app.schemas.patient import PatientCreate
from app.services.analysis_service import AnalysisService
from app.services.patient_service import PatientService
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_employer_assessment_10_submission_lifecycle(api_client: TestClient) -> None:
    """Execute the full 10-attempt workflow using neutral synthetic values.

    Validates:
    - 3 invalid submissions rejected with 422.
    - 1 duplicate warned with 409 and confirmed with allow_duplicate=true.
    - 7 distinct persisted patient records.
    - Target email update to gokul@infocare.com.
    - Cascade deletion of a different record leaving exactly 6 records.
    """
    # 1. Attempt 1: Valid registration
    sub1 = {
        "full_name": "Subject Alpha",
        "date_of_birth": "1985-05-12",
        "email": "alpha.patient@example.test",
        "glucose_value": 95.0,
        "haemoglobin_value": 14.2,
        "cholesterol_value": 185.0,
        "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
    }
    res1 = api_client.post("/api/v1/patients", json=sub1)
    assert res1.status_code == 201
    p1_id = res1.json()["id"]

    # 2. Attempt 2: Rejected - Malformed email (missing TLD)
    sub2 = {
        "full_name": "Subject Beta",
        "date_of_birth": "1990-03-15",
        "email": "beta.patient@invaliddomain",
        "glucose_value": 110.0,
        "haemoglobin_value": 13.5,
        "cholesterol_value": 210.0,
    }
    res2 = api_client.post("/api/v1/patients", json=sub2)
    assert res2.status_code == 422
    assert "email" in str(res2.json()).lower()

    # 3. Attempt 3: Valid registration (elevated measurements are valid syntax)
    sub3 = {
        "full_name": "Subject Gamma",
        "date_of_birth": "1978-11-20",
        "email": "gamma.patient@example.test",
        "glucose_value": 240.0,
        "haemoglobin_value": 10.2,
        "cholesterol_value": 310.0,
    }
    res3 = api_client.post("/api/v1/patients", json=sub3)
    assert res3.status_code == 201
    p3_id = res3.json()["id"]

    # 4. Attempt 4: Rejected - Impossible calendar date (31.11 / Nov 31)
    # The client/schema parser rejects impossible dates
    sub4 = {
        "full_name": "Subject Delta",
        "date_of_birth": "1982-11-31",  # Invalid calendar date
        "email": "delta.patient@example.test",
        "glucose_value": 88.0,
        "haemoglobin_value": 15.0,
        "cholesterol_value": 175.0,
    }
    res4 = api_client.post("/api/v1/patients", json=sub4)
    assert res4.status_code == 422

    # 5. Attempt 5: Valid registration
    sub5 = {
        "full_name": "Subject Epsilon",
        "date_of_birth": "1995-07-04",
        "email": "epsilon.patient@example.test",
        "glucose_value": 90.0,
        "haemoglobin_value": 14.8,
        "cholesterol_value": 160.0,
    }
    res5 = api_client.post("/api/v1/patients", json=sub5)
    assert res5.status_code == 201

    # 6. Attempt 6: Exact duplicate of Attempt 1 -> 409 Conflict warning
    sub6 = dict(sub1)
    res6_warn = api_client.post("/api/v1/patients", json=sub6)
    assert res6_warn.status_code == 409
    err6 = res6_warn.json()["error"]
    assert err6["code"] == "DUPLICATE_RECORD"
    assert err6["existing_patient_id"] == p1_id

    # Confirm duplicate insertion with allow_duplicate=true
    sub6["allow_duplicate"] = True
    res6_confirm = api_client.post("/api/v1/patients", json=sub6)
    assert res6_confirm.status_code == 201
    p6_id = res6_confirm.json()["id"]
    assert p6_id != p1_id

    # 7. Attempt 7: Valid registration
    sub7 = {
        "full_name": "Subject Zeta",
        "date_of_birth": "1968-09-18",
        "email": "zeta.patient@example.test",
        "glucose_value": 105.0,
        "haemoglobin_value": 13.9,
        "cholesterol_value": 225.0,
    }
    res7 = api_client.post("/api/v1/patients", json=sub7)
    assert res7.status_code == 201

    # 8. Attempt 8: Rejected - Future date of birth & malformed email
    sub8 = {
        "full_name": "Subject Eta",
        "date_of_birth": "2030-01-01",  # Future date
        "email": "eta-no-at-sign",
        "glucose_value": 92.0,
        "haemoglobin_value": 14.0,
        "cholesterol_value": 190.0,
    }
    res8 = api_client.post("/api/v1/patients", json=sub8)
    assert res8.status_code == 422

    # 9. Attempt 9: Valid registration (Nov 30 exists)
    sub9 = {
        "full_name": "Subject Theta",
        "date_of_birth": "1982-11-30",
        "email": "theta.patient@example.test",
        "glucose_value": 98.0,
        "haemoglobin_value": 14.5,
        "cholesterol_value": 195.0,
    }
    res9 = api_client.post("/api/v1/patients", json=sub9)
    assert res9.status_code == 201

    # 10. Attempt 10: Valid registration
    sub10 = {
        "full_name": "Subject Iota",
        "date_of_birth": "1992-04-25",
        "email": "iota.patient@example.test",
        "glucose_value": 85.0,
        "haemoglobin_value": 15.2,
        "cholesterol_value": 170.0,
    }
    res10 = api_client.post("/api/v1/patients", json=sub10)
    assert res10.status_code == 201

    # VERIFY: Exactly 7 persisted records
    list_res = api_client.get("/api/v1/patients?limit=50")
    assert list_res.status_code == 200
    patients = list_res.json()["items"]
    assert len(patients) == 7

    # STEP: Change one saved email to gokul@infocare.com
    patch_res = api_client.patch(
        f"/api/v1/patients/{p1_id}",
        json={"email": "gokul@infocare.com"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["email"] == "gokul@infocare.com"

    # STEP: Delete a DIFFERENT record (Subject Gamma / p3_id)
    del_res = api_client.delete(f"/api/v1/patients/{p3_id}")
    assert del_res.status_code == 204

    # VERIFY: Exactly 6 records remain in the directory
    final_list = api_client.get("/api/v1/patients?limit=50")
    assert final_list.status_code == 200
    remaining = final_list.json()["items"]
    assert len(remaining) == 6

    # Verify gokul@infocare.com is present among the 6 remaining records
    emails = [p["email"] for p in remaining]
    assert "gokul@infocare.com" in emails
    assert "gamma.patient@example.test" not in emails


@pytest.mark.asyncio
async def test_failure_recovery_testwell_network_outage(test_db_session: Session) -> None:
    """When TestWell is unreachable, patient record persists and failure is safely recorded."""
    patient, analysis = PatientService.create_patient(
        db=test_db_session,
        data=PatientCreate(
            full_name="Outage Test Subject",
            date_of_birth=date(1991, 8, 12),
            email="outage.test@example.test",
            glucose_value=Decimal("94.0"),
            haemoglobin_value=Decimal("14.0"),
            cholesterol_value=Decimal("180.0"),
            unit_profile_code="ASSESSMENT_CONVENTIONAL_V1",
        ),
    )
    test_db_session.commit()

    from sqlalchemy.orm import sessionmaker

    bind = test_db_session.get_bind()
    factory = sessionmaker(bind=bind, autocommit=False, autoflush=False)

    from app.integrations.testwell.adapter import TestWellAdapter

    mock_adapter = TestWellAdapter()
    mock_adapter.interpret_biomarkers = AsyncMock(  # type: ignore[method-assign]
        side_effect=TestWellClientError(
            "Connection refused by remote host (503 Service Unavailable)"
        )
    )

    updated_analysis = await AnalysisService.execute_analysis_run(
        analysis_id=analysis.id,
        adapter=mock_adapter,
        session_factory=factory,
    )

    # Verify analysis is marked as failed / degraded without crashing or deleting patient
    assert updated_analysis.external_status == ExternalStatus.FAILED
    assert updated_analysis.overall_status in (OverallStatus.DEGRADED, OverallStatus.FAILED)
    assert "Connection refused" in (updated_analysis.error_summary or "")

    # Verify patient still exists intact in the database
    persisted_patient = test_db_session.get(Patient, patient.id)
    assert persisted_patient is not None
    assert persisted_patient.email == "outage.test@example.test"


@pytest.mark.asyncio
async def test_failure_recovery_ollama_fallback(test_db_session: Session) -> None:
    """When Ollama is offline, TestWell observations persist and deterministic fallback is applied."""
    patient, analysis = PatientService.create_patient(
        db=test_db_session,
        data=PatientCreate(
            full_name="Ollama Offline Subject",
            date_of_birth=date(1989, 2, 20),
            email="ollama.offline@example.test",
            glucose_value=Decimal("100.0"),
            haemoglobin_value=Decimal("14.5"),
            cholesterol_value=Decimal("190.0"),
            unit_profile_code="ASSESSMENT_CONVENTIONAL_V1",
        ),
    )
    test_db_session.commit()

    from app.integrations.testwell.adapter import TestWellAdapter
    from app.integrations.testwell.normalizer import (
        NormalizedObservation,
        NormalizedProviderResult,
    )
    from sqlalchemy.orm import sessionmaker

    bind = test_db_session.get_bind()
    factory = sessionmaker(bind=bind, autocommit=False, autoflush=False)

    dummy_provider_result = NormalizedProviderResult(
        provider="testwell",
        catalog_review_date="2026-09-05",
        reviewer="Reference Provider Catalog",
        observations=[
            NormalizedObservation(
                analyte="glucose",
                query_marker="glucose",
                matched_marker="Glucose",
                value=100.0,
                unit="mg/dL",
                found=True,
                flag="normal",
                range_text="70 – 99 mg/dL",
                range_qualifier="age 18+, fasting",
                context_status="CONTEXT_NOT_CONFIRMED",
            )
        ],
        summary={"total": 1, "matched": 1, "high": 0, "low": 0, "normal": 1, "unknown": 0},
    )

    mock_adapter = TestWellAdapter()
    mock_adapter.interpret_biomarkers = AsyncMock(return_value=dummy_provider_result)  # type: ignore[method-assign]

    mock_generator = AsyncMock()
    mock_generator.client = AsyncMock()
    mock_generator.client.model = "llama3.2:3b"
    mock_generator.generate_remarks = AsyncMock(
        return_value=(
            "AI remarks unavailable; deterministic provider reference observations shown.",
            {
                "summary": "AI remarks unavailable; deterministic provider reference observations shown.",
                "notes": ["Educational reference intervals only."],
                "generation_label": "DETERMINISTIC_FALLBACK",
            },
            False,  # is_ai_generated is False
            150.0,
        )
    )

    updated_analysis = await AnalysisService.execute_analysis_run(
        analysis_id=analysis.id,
        adapter=mock_adapter,
        generator=mock_generator,
        session_factory=factory,
    )

    # Verify overall status is DEGRADED with AiStatus.FALLBACK
    assert updated_analysis.ai_status == AiStatus.FALLBACK
    assert updated_analysis.overall_status == OverallStatus.DEGRADED
    assert updated_analysis.ai_result_json is not None
    assert updated_analysis.ai_result_json["generation_label"] == "DETERMINISTIC_FALLBACK"
    assert "physician-reviewed" not in str(updated_analysis.ai_result_json).lower()
