"""Integration tests for patient analysis endpoints.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from typing import Any
from unittest.mock import AsyncMock

from app.integrations.testwell.adapter import TestWellAdapter
from app.integrations.testwell.normalizer import (
    NormalizedObservation,
    NormalizedProviderResult,
)
from app.services.analysis_service import AnalysisService
from fastapi.testclient import TestClient


def test_trigger_and_get_analysis_lifecycle(api_client: TestClient) -> None:
    """Test full analysis endpoint lifecycle: create patient, trigger analysis, get detail, list history."""
    # 1. Create patient
    create_payload = {
        "full_name": "Robin Clinical",
        "date_of_birth": "22/10/1984",
        "email": "robin.clinical@example.test",
        "glucose_value": 91.0,
        "haemoglobin_value": 14.3,
        "cholesterol_value": 178.0,
    }
    create_res = api_client.post("/api/v1/patients", json=create_payload)
    assert create_res.status_code == 201
    patient = create_res.json()
    patient_id = patient["id"]
    initial_analysis_id = patient["latest_analysis"]["id"]

    # 2. Get initial analysis detail
    detail_res = api_client.get(f"/api/v1/patients/{patient_id}/analyses/{initial_analysis_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == initial_analysis_id
    assert detail["run_number"] == 1
    assert detail["overall_status"] == "PENDING"
    assert detail["external_status"] == "PENDING"
    assert detail["ai_status"] == "NOT_RUN"
    assert detail["input_snapshot_json"]["glucose"]["value"] == 91.0

    # 3. List analyses for patient
    list_res = api_client.get(f"/api/v1/patients/{patient_id}/analyses")
    assert list_res.status_code == 200
    runs = list_res.json()
    assert len(runs) == 1
    assert runs[0]["id"] == initial_analysis_id

    # 4. Mock adapter and generator for background execution
    mock_result = NormalizedProviderResult(
        provider="testwell",
        observations=[
            NormalizedObservation(
                analyte="glucose",
                query_marker="glucose",
                matched_marker="Glucose",
                value=91.0,
                unit="mg/dL",
                found=True,
                flag="normal",
            )
        ],
        summary={"total": 1, "matched": 1, "normal": 1},
    )

    mock_adapter = TestWellAdapter()
    mock_adapter.interpret_biomarkers = AsyncMock(return_value=mock_result)  # type: ignore[method-assign]

    mock_generator = AsyncMock()
    mock_generator.generate_remarks = AsyncMock(
        return_value=(
            "AI remarks summary...",
            {"summary": "AI remarks summary...", "generation_label": "AI_GENERATED"},
            True,
            100.0,
        )
    )
    mock_generator.client = AsyncMock()
    mock_generator.client.model = "llama3.2:3b"

    # Temporarily patch default execution to inject mock adapter & mock generator
    original_execute = AnalysisService.execute_analysis_run

    async def patched_execute(
        analysis_id: str,
        adapter: Any = None,
        generator: Any = None,
        session_factory: Any = None,
        **kwargs: Any,
    ) -> Any:
        return await original_execute(
            analysis_id=analysis_id,
            adapter=mock_adapter,
            generator=mock_generator,
            session_factory=session_factory or kwargs.get("session_factory"),
        )

    AnalysisService.execute_analysis_run = staticmethod(patched_execute)  # type: ignore[method-assign]

    try:
        # First trigger: reuses unstarted initial pending analysis (run_number = 1)
        trigger_res = api_client.post(f"/api/v1/patients/{patient_id}/analyses")
        assert trigger_res.status_code == 202
        trigger_data = trigger_res.json()
        assert trigger_data["run_number"] == 1
        assert trigger_data["id"] == initial_analysis_id

        # 5. Fetch updated analysis detail for run 1 after background execution
        run_1_res = api_client.get(f"/api/v1/patients/{patient_id}/analyses/{initial_analysis_id}")
        assert run_1_res.status_code == 200
        run_1_detail = run_1_res.json()
        assert run_1_detail["run_number"] == 1
        assert run_1_detail["external_status"] == "SUCCEEDED"
        assert run_1_detail["ai_status"] == "SUCCEEDED"
        assert run_1_detail["overall_status"] == "COMPLETED"
        assert run_1_detail["external_result_json"] is not None

        # 6. Retry trigger: now that run 1 is COMPLETED, creates run_number = 2
        retry_res = api_client.post(f"/api/v1/patients/{patient_id}/analyses")
        assert retry_res.status_code == 202
        retry_data = retry_res.json()
        assert retry_data["run_number"] == 2
        assert retry_data["id"] != initial_analysis_id
        run_2_id = retry_data["id"]

        run_2_res = api_client.get(f"/api/v1/patients/{patient_id}/analyses/{run_2_id}")
        assert run_2_res.status_code == 200
        run_2_detail = run_2_res.json()
        assert run_2_detail["run_number"] == 2
        assert run_2_detail["retry_of_id"] == initial_analysis_id

        # 7. List history shows both runs ordered newest-first
        history_res = api_client.get(f"/api/v1/patients/{patient_id}/analyses")
        assert history_res.status_code == 200
        history = history_res.json()
        assert len(history) == 2
        assert history[0]["run_number"] == 2
        assert history[1]["run_number"] == 1
    finally:
        AnalysisService.execute_analysis_run = staticmethod(original_execute)  # type: ignore[method-assign]


def test_trigger_analysis_patient_not_found(api_client: TestClient) -> None:
    """Triggering analysis on non-existent patient returns HTTP 404."""
    response = api_client.post("/api/v1/patients/999999/analyses")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "NOT_FOUND"
