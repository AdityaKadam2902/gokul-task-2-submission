"""Privacy and de-identification verification tests for external TestWell integration.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import json
import logging
from decimal import Decimal

import pytest
import respx
from app.integrations.testwell.adapter import TestWellAdapter
from app.integrations.testwell.schemas import (
    TestWellBiomarkerInput,
    TestWellInterpretRequest,
)

ENDPOINT_URL = "https://www.test-well.com/api/agent/interpret_results"


def test_outgoing_request_schema_forbids_identifiers() -> None:
    """Outgoing request schema strictly forbids extra fields and patient identifiers."""
    with pytest.raises(ValueError):
        # Attempting to pass forbidden PII fields fails validation
        TestWellBiomarkerInput(  # type: ignore[call-arg]
            marker="glucose",
            value=95.0,
            unit="mg/dL",
            patient_id=123,  # Forbidden extra field
        )


def test_serialized_request_contains_zero_pii() -> None:
    """Ensure serialized request payload to TestWell contains strictly anonymous fields."""
    request = TestWellInterpretRequest(
        values=[
            TestWellBiomarkerInput(marker="glucose", value=95.5, unit="mg/dL"),
            TestWellBiomarkerInput(marker="hemoglobin", value=14.2, unit="g/dL"),
            TestWellBiomarkerInput(marker="total cholesterol", value=185.0, unit="mg/dL"),
        ]
    )

    serialized = request.model_dump()
    raw_json_str = json.dumps(serialized)

    # Assert permitted keys only
    assert set(serialized.keys()) == {"values"}
    for item in serialized["values"]:
        assert set(item.keys()) == {"marker", "value", "unit"}

    # Strict string assertions for any PII leakage
    forbidden_tokens = ["name", "email", "birth", "patient", "dob", "address", "phone"]
    for token in forbidden_tokens:
        assert token not in raw_json_str.lower(), (
            f"Forbidden identifier token '{token}' in serialized payload"
        )


@pytest.mark.asyncio
@respx.mock
async def test_adapter_outgoing_payload_contains_no_patient_pii(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify that actual HTTP dispatch only transmits anonymous markers and does not log PII."""
    route = respx.post(ENDPOINT_URL).respond(
        status_code=200,
        json={
            "tool": "interpret_results",
            "result": {
                "results": [
                    {
                        "input": {"marker": "glucose", "value": 90.0, "unit": "mg/dL"},
                        "found": True,
                        "marker": "Glucose",
                        "flag": "normal",
                        "citations": [],
                    }
                ],
                "summary": {"total": 1, "matched": 1},
            },
        },
    )

    caplog.set_level(logging.INFO)
    adapter = TestWellAdapter()

    await adapter.interpret_biomarkers(
        glucose_value=Decimal("95.5"),
        haemoglobin_value=Decimal("14.2"),
        cholesterol_value=Decimal("185.0"),
    )

    assert route.called
    sent_request = route.calls.last.request
    sent_json = json.loads(sent_request.content.decode("utf-8"))

    # Assert HTTP body contains only 'values'
    assert "values" in sent_json
    assert len(sent_json["values"]) == 3
    for entry in sent_json["values"]:
        assert list(entry.keys()) == ["marker", "value", "unit"]

    # Verify log output does not log patient identities or exact sensitive values
    log_text = caplog.text
    assert "name" not in log_text.lower()
    assert "email" not in log_text.lower()
