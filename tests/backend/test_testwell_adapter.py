"""Automated tests for TestWell adapter, client, and normalization.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from decimal import Decimal
from typing import Any

import httpx
import pytest
import respx
from app.integrations.testwell.adapter import TestWellAdapter
from app.integrations.testwell.client import TestWellClient
from app.integrations.testwell.exceptions import (
    TestWellClientError,
    TestWellConnectionError,
    TestWellRateLimitError,
    TestWellResponseError,
    TestWellServerError,
    TestWellTimeoutError,
)
from app.integrations.testwell.normalizer import (
    normalize_testwell_response,
    sanitize_https_url,
)
from app.integrations.testwell.schemas import (
    TestWellBiomarkerInput,
    TestWellInterpretRequest,
)

ENDPOINT_URL = "https://www.test-well.com/api/agent/interpret_results"


# --- Fixtures for Mocked TestWell Responses ---


@pytest.fixture
def mock_successful_raw_response() -> dict[str, Any]:
    """Realistic provider response echoing 3 recognized analytes."""
    return {
        "tool": "interpret_results",
        "result": {
            "results": [
                {
                    "input": {"marker": "glucose", "value": 90.0, "unit": "mg/dL"},
                    "found": True,
                    "marker": "Glucose",
                    "slug": "glucose",
                    "flag": "normal",
                    "range": {
                        "qualifier": "age 18+, fasting",
                        "min": 70,
                        "max": 99,
                        "unit": "mg/dL",
                        "text": "70 – 99 mg/dL",
                    },
                    "unitMismatch": False,
                    "suggests": None,
                    "retest": "Retest in 3 years if normal.",
                    "citations": [
                        {"label": "ADA Guidelines", "url": "https://diabetes.org/diagnosis"},
                    ],
                    "links": {
                        "biomarker": "https://www.test-well.com/biomarkers/glucose",
                        "interpretation": None,
                        "orderTest": "https://www.test-well.com/tests/glucose",
                    },
                },
                {
                    "input": {"marker": "hemoglobin", "value": 14.0, "unit": "g/dL"},
                    "found": True,
                    "marker": "Hemoglobin",
                    "slug": "hemoglobin",
                    "flag": "normal",
                    "range": {
                        "qualifier": "Male, age 18+",
                        "min": 13.5,
                        "max": 17.5,
                        "unit": "g/dL",
                        "text": "13.5 – 17.5 g/dL",
                    },
                    "unitMismatch": False,
                    "suggests": None,
                    "retest": None,
                    "citations": [
                        {
                            "label": "Mayo Clinic",
                            "url": "https://www.mayocliniclabs.com/test-catalog/overview/9109",
                        },
                    ],
                    "links": {
                        "biomarker": "https://www.test-well.com/biomarkers/hemoglobin",
                        "interpretation": None,
                        "orderTest": None,
                    },
                },
                {
                    "input": {"marker": "total cholesterol", "value": 180.0, "unit": "mg/dL"},
                    "found": True,
                    "marker": "Total Cholesterol",
                    "slug": "total-cholesterol",
                    "flag": "normal",
                    "range": {
                        "qualifier": "age 18+",
                        "min": 125,
                        "max": 200,
                        "unit": "mg/dL",
                        "text": "125 – 200 mg/dL",
                    },
                    "unitMismatch": False,
                    "suggests": None,
                    "retest": None,
                    "citations": [
                        {"label": "AHA Cholesterol", "url": "https://www.heart.org/cholesterol"},
                    ],
                    "links": {
                        "biomarker": "https://www.test-well.com/biomarkers/total-cholesterol",
                        "interpretation": None,
                        "orderTest": None,
                    },
                },
            ],
            "summary": {
                "total": 3,
                "matched": 3,
                "high": 0,
                "low": 0,
                "normal": 3,
                "unknown": 0,
            },
            "disclaimer": "Educational reference catalog.",
            "reviewed": {
                "catalog": "2026-09-05",
                "reviewer": "Dr. Test Reviewer, MD",
            },
        },
    }


# --- URL Sanitization Tests ---


def test_sanitize_https_url_valid() -> None:
    """Safe HTTPS URLs are preserved."""
    assert sanitize_https_url("https://example.org/study") == "https://example.org/study"
    assert sanitize_https_url("https://medlineplus.gov/test") == "https://medlineplus.gov/test"


def test_sanitize_https_url_rejects_insecure_and_malicious() -> None:
    """Insecure, executable, or malformed URLs are rejected and return None."""
    assert sanitize_https_url("http://insecure.example.com") is None
    assert sanitize_https_url("javascript:alert(1)") is None
    assert sanitize_https_url("data:text/html,<script>alert(1)</script>") is None
    assert sanitize_https_url("ftp://files.example.org") is None
    assert sanitize_https_url("") is None
    assert sanitize_https_url(None) is None
    assert sanitize_https_url("https://") is None
    assert sanitize_https_url("https://invalid with spaces.com") is None


# --- Normalization Tests ---


def test_normalization_all_markers_matched(mock_successful_raw_response: dict[str, Any]) -> None:
    """Normalized response correctly maps all 3 analytes and surfaces context caveats."""
    snapshot = {
        "glucose_value": 90.0,
        "glucose_unit": "mg/dL",
        "haemoglobin_value": 14.0,
        "haemoglobin_unit": "g/dL",
        "cholesterol_value": 180.0,
        "cholesterol_unit": "mg/dL",
    }
    normalized = normalize_testwell_response(
        raw_response=mock_successful_raw_response,
        input_snapshot=snapshot,
        latency_ms=120.5,
    )

    assert normalized.provider == "testwell"
    assert normalized.summary["matched"] == 3
    assert len(normalized.observations) == 3
    assert normalized.latency_ms == 120.5

    # Check Glucose
    glucose_obs = next(o for o in normalized.observations if o.analyte == "glucose")
    assert glucose_obs.found is True
    assert glucose_obs.flag == "normal"
    assert glucose_obs.range_text == "70 – 99 mg/dL"
    assert glucose_obs.context_status == "CONTEXT_NOT_CONFIRMED"
    assert any("fasting" in w.lower() for w in glucose_obs.warnings)

    # Check Hemoglobin
    hemo_obs = next(o for o in normalized.observations if o.analyte == "haemoglobin")
    assert hemo_obs.found is True
    assert hemo_obs.flag == "normal"
    assert hemo_obs.matched_marker == "Hemoglobin"
    assert hemo_obs.context_status == "CONTEXT_NOT_CONFIRMED"
    assert any("demographic" in w.lower() for w in hemo_obs.warnings)

    # Check Cholesterol
    chol_obs = next(o for o in normalized.observations if o.analyte == "cholesterol")
    assert chol_obs.found is True
    assert chol_obs.flag == "normal"
    assert chol_obs.matched_marker == "Total Cholesterol"


def test_normalization_unknown_marker() -> None:
    """Unrecognized marker is flagged found=False, flag=unknown without raising."""
    raw = {
        "tool": "interpret_results",
        "result": {
            "results": [
                {
                    "input": {"marker": "glucose", "value": 90.0, "unit": "mg/dL"},
                    "found": False,
                    "marker": None,
                    "flag": "unknown",
                    "range": None,
                    "unitMismatch": False,
                    "citations": [],
                }
            ],
            "summary": {"total": 1, "matched": 0, "unknown": 1},
        },
    }
    snapshot = {"glucose_value": 90.0, "glucose_unit": "mg/dL"}
    normalized = normalize_testwell_response(raw, snapshot)

    assert normalized.summary["matched"] == 0
    obs = normalized.observations[0]
    assert obs.found is False
    assert obs.flag == "unknown"
    assert any("not recognized" in w.lower() for w in obs.warnings)


def test_normalization_unit_mismatch() -> None:
    """Unit mismatch is captured as unit_mismatch=True and flag=unknown."""
    raw = {
        "tool": "interpret_results",
        "result": {
            "results": [
                {
                    "input": {"marker": "glucose", "value": 90.0, "unit": "mmol/L"},
                    "found": True,
                    "marker": "Glucose",
                    "flag": "unknown",
                    "range": None,
                    "unitMismatch": True,
                    "citations": [],
                }
            ],
            "summary": {"total": 1, "matched": 0, "unknown": 1},
        },
    }
    snapshot = {"glucose_value": 90.0, "glucose_unit": "mmol/L"}
    normalized = normalize_testwell_response(raw, snapshot)

    obs = normalized.observations[0]
    assert obs.unit_mismatch is True
    assert obs.flag == "unknown"
    assert any("unit mismatch" in w.lower() for w in obs.warnings)


# --- Client & Adapter Unit Tests (with respx) ---


@pytest.mark.asyncio
@respx.mock
async def test_adapter_interpret_biomarkers_success(
    mock_successful_raw_response: dict[str, Any],
) -> None:
    """Test successful adapter call against mocked HTTP 200."""
    respx.post(ENDPOINT_URL).respond(
        status_code=200,
        json=mock_successful_raw_response,
    )

    adapter = TestWellAdapter()
    result = await adapter.interpret_biomarkers(
        glucose_value=Decimal("90.0"),
        haemoglobin_value=Decimal("14.0"),
        cholesterol_value=Decimal("180.0"),
    )

    assert result.provider == "testwell"
    assert result.summary["matched"] == 3
    assert len(result.observations) == 3


@pytest.mark.asyncio
@respx.mock
async def test_client_timeout_error() -> None:
    """Client raises TestWellTimeoutError when provider times out."""
    respx.post(ENDPOINT_URL).mock(side_effect=httpx.ReadTimeout("Timeout"))

    client = TestWellClient(max_retries=1, backoff_seconds=0.01)
    req = TestWellInterpretRequest(
        values=[TestWellBiomarkerInput(marker="glucose", value=90.0, unit="mg/dL")]
    )

    with pytest.raises(TestWellTimeoutError) as exc_info:
        await client.interpret_results(req)

    assert exc_info.value.status_code == 504
    assert exc_info.value.error_code == "TESTWELL_TIMEOUT"


@pytest.mark.asyncio
@respx.mock
async def test_client_network_connection_error() -> None:
    """Client raises TestWellConnectionError when network connection fails."""
    respx.post(ENDPOINT_URL).mock(side_effect=httpx.ConnectError("Failed to connect"))

    client = TestWellClient(max_retries=1, backoff_seconds=0.01)
    req = TestWellInterpretRequest(
        values=[TestWellBiomarkerInput(marker="glucose", value=90.0, unit="mg/dL")]
    )

    with pytest.raises(TestWellConnectionError) as exc_info:
        await client.interpret_results(req)

    assert exc_info.value.status_code == 503
    assert exc_info.value.error_code == "TESTWELL_CONNECTION_FAILED"


@pytest.mark.asyncio
@respx.mock
async def test_client_rate_limit_429() -> None:
    """Client raises TestWellRateLimitError with Retry-After on HTTP 429."""
    respx.post(ENDPOINT_URL).respond(
        status_code=429,
        headers={"Retry-After": "30"},
        json={"error": "Rate limit exceeded"},
    )

    client = TestWellClient(max_retries=0)
    req = TestWellInterpretRequest(
        values=[TestWellBiomarkerInput(marker="glucose", value=90.0, unit="mg/dL")]
    )

    with pytest.raises(TestWellRateLimitError) as exc_info:
        await client.interpret_results(req)

    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after == 30


@pytest.mark.asyncio
@respx.mock
async def test_client_bad_request_400() -> None:
    """Client raises TestWellClientError on HTTP 400 without retrying."""
    route = respx.post(ENDPOINT_URL).respond(
        status_code=400,
        json={"error": "Invalid input"},
    )

    client = TestWellClient(max_retries=2)
    req = TestWellInterpretRequest(
        values=[TestWellBiomarkerInput(marker="glucose", value=90.0, unit="mg/dL")]
    )

    with pytest.raises(TestWellClientError) as exc_info:
        await client.interpret_results(req)

    assert exc_info.value.status_code == 502
    assert route.call_count == 1  # Did not retry 400


@pytest.mark.asyncio
@respx.mock
async def test_client_server_error_500() -> None:
    """Client raises TestWellServerError after exhausting retries on HTTP 500."""
    route = respx.post(ENDPOINT_URL).respond(
        status_code=500,
        text="Internal Server Error",
    )

    client = TestWellClient(max_retries=1, backoff_seconds=0.01)
    req = TestWellInterpretRequest(
        values=[TestWellBiomarkerInput(marker="glucose", value=90.0, unit="mg/dL")]
    )

    with pytest.raises(TestWellServerError) as exc_info:
        await client.interpret_results(req)

    assert exc_info.value.status_code == 500
    assert route.call_count == 2  # Retried once


@pytest.mark.asyncio
@respx.mock
async def test_client_malformed_json_response() -> None:
    """Client raises TestWellResponseError when provider returns unparseable schema."""
    respx.post(ENDPOINT_URL).respond(
        status_code=200,
        json={"tool": "wrong_tool", "unexpected": {}},
    )

    client = TestWellClient(max_retries=0)
    req = TestWellInterpretRequest(
        values=[TestWellBiomarkerInput(marker="glucose", value=90.0, unit="mg/dL")]
    )

    with pytest.raises(TestWellResponseError) as exc_info:
        await client.interpret_results(req)

    assert exc_info.value.status_code == 502
