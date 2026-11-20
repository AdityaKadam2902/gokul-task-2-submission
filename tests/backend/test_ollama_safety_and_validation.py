"""Clinical safety, validation, and deterministic fallback tests for Ollama integration.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import pytest
from app.integrations.ollama.exceptions import (
    OllamaResponseError,
    OllamaSafetyValidationError,
)
from app.integrations.ollama.fallback import render_deterministic_fallback
from app.integrations.ollama.schemas import AiRemarksPayload
from app.integrations.ollama.validator import validate_ai_remarks_output
from app.integrations.testwell.normalizer import (
    NormalizedObservation,
    NormalizedProviderResult,
    ProviderCitation,
)


@pytest.fixture
def sample_testwell_result() -> NormalizedProviderResult:
    """Fixture providing a realistic normalized TestWell provider result."""
    return NormalizedProviderResult(
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
                value=225.0,
                unit="mg/dL",
                found=True,
                flag="high",
                range_text="125 – 200 mg/dL",
                range_qualifier="age 18+",
                context_status="CONTEXT_NOT_CONFIRMED",
                citations=[ProviderCitation(label="AHA", url="https://heart.org")],
            ),
        ],
        summary={"total": 3, "matched": 3, "high": 1, "low": 0, "normal": 2, "unknown": 0},
        global_caveats=[
            "TestWell standard conventional units were assumed for this interpretation.",
            "Patient fasting status was not confirmed; fasting reference range applied for Glucose.",
        ],
        latency_ms=120.0,
    )


@pytest.fixture
def required_caveats() -> list[str]:
    return [
        "UNIT_ASSUMPTION",
        "FASTING_STATUS_NOT_CONFIRMED",
        "DEMOGRAPHIC_CONTEXT_NOT_CONFIRMED",
    ]


def test_validate_valid_ai_remarks(
    sample_testwell_result: NormalizedProviderResult,
    required_caveats: list[str],
) -> None:
    """Valid AI response preserving all provider flags and caveats passes validation."""
    valid_payload = {
        "summary": "Laboratory results indicate elevated total cholesterol alongside normal fasting glucose and haemoglobin.",
        "analyte_remarks": [
            {
                "analyte": "glucose",
                "observation_id": "obs-glucose",
                "provider_flag": "normal",
                "summary": "Fasting glucose of 94.0 mg/dL is within the reference interval of 70 – 99 mg/dL.",
            },
            {
                "analyte": "haemoglobin",
                "observation_id": "obs-haemoglobin",
                "provider_flag": "normal",
                "summary": "Haemoglobin of 14.5 g/dL aligns with the expected male adult reference interval.",
            },
            {
                "analyte": "cholesterol",
                "observation_id": "obs-cholesterol",
                "provider_flag": "high",
                "summary": "Total cholesterol of 225.0 mg/dL exceeds the provider reference interval threshold of 200 mg/dL.",
            },
        ],
        "source_observation_ids": ["obs-glucose", "obs-haemoglobin", "obs-cholesterol"],
        "caveat_codes": [
            "UNIT_ASSUMPTION",
            "FASTING_STATUS_NOT_CONFIRMED",
            "DEMOGRAPHIC_CONTEXT_NOT_CONFIRMED",
        ],
        "generation_label": "AI_GENERATED",
    }

    raw_json = AiRemarksPayload.model_validate(valid_payload).model_dump_json()
    validated = validate_ai_remarks_output(raw_json, sample_testwell_result, required_caveats)

    assert validated.summary.startswith("Laboratory results indicate")
    assert len(validated.analyte_remarks) == 3
    assert validated.generation_label == "AI_GENERATED"


def test_safety_rejects_altered_provider_flag(
    sample_testwell_result: NormalizedProviderResult,
    required_caveats: list[str],
) -> None:
    """Safety validation rejects AI output that alters a provider flag (e.g. normal -> high)."""
    tampered_payload = {
        "summary": "Glucose is severely elevated.",
        "analyte_remarks": [
            {
                "analyte": "glucose",
                "observation_id": "obs-glucose",
                "provider_flag": "high",  # Provider says 'normal'!
                "summary": "Glucose is critically high.",
            }
        ],
        "source_observation_ids": ["obs-glucose"],
        "caveat_codes": [
            "UNIT_ASSUMPTION",
            "FASTING_STATUS_NOT_CONFIRMED",
            "DEMOGRAPHIC_CONTEXT_NOT_CONFIRMED",
        ],
        "generation_label": "AI_GENERATED",
    }

    raw_json = AiRemarksPayload.model_validate(tampered_payload).model_dump_json()

    with pytest.raises(OllamaSafetyValidationError) as exc_info:
        validate_ai_remarks_output(raw_json, sample_testwell_result, required_caveats)

    assert any("altered provider flag for 'glucose'" in v for v in exc_info.value.violations)


def test_safety_rejects_missing_required_caveats(
    sample_testwell_result: NormalizedProviderResult,
    required_caveats: list[str],
) -> None:
    """Safety validation rejects AI output omitting mandatory clinical caveats."""
    payload_missing_caveats = {
        "summary": "Summary text.",
        "analyte_remarks": [
            {
                "analyte": "glucose",
                "observation_id": "obs-glucose",
                "provider_flag": "normal",
                "summary": "Observation remark.",
            }
        ],
        "source_observation_ids": ["obs-glucose"],
        "caveat_codes": ["UNIT_ASSUMPTION"],  # Missing FASTING and DEMOGRAPHIC
        "generation_label": "AI_GENERATED",
    }

    raw_json = AiRemarksPayload.model_validate(payload_missing_caveats).model_dump_json()

    with pytest.raises(OllamaSafetyValidationError) as exc_info:
        validate_ai_remarks_output(raw_json, sample_testwell_result, required_caveats)

    assert any("DEMOGRAPHIC_CONTEXT_NOT_CONFIRMED" in v for v in exc_info.value.violations)


def test_safety_rejects_unknown_analyte_name(
    sample_testwell_result: NormalizedProviderResult,
    required_caveats: list[str],
) -> None:
    """Safety validation rejects AI output inventing markers not present in provider result."""
    payload_unknown_analyte = {
        "summary": "Summary text.",
        "analyte_remarks": [
            {
                "analyte": "potassium",  # Invented!
                "observation_id": "obs-potassium",
                "provider_flag": "normal",
                "summary": "Potassium is normal.",
            }
        ],
        "source_observation_ids": ["obs-potassium"],
        "caveat_codes": [
            "UNIT_ASSUMPTION",
            "FASTING_STATUS_NOT_CONFIRMED",
            "DEMOGRAPHIC_CONTEXT_NOT_CONFIRMED",
        ],
        "generation_label": "AI_GENERATED",
    }

    raw_json = AiRemarksPayload.model_validate(payload_unknown_analyte).model_dump_json()

    with pytest.raises(OllamaSafetyValidationError) as exc_info:
        validate_ai_remarks_output(raw_json, sample_testwell_result, required_caveats)

    assert any("unknown analyte 'potassium'" in v for v in exc_info.value.violations)


def test_safety_rejects_unknown_observation_id(
    sample_testwell_result: NormalizedProviderResult,
    required_caveats: list[str],
) -> None:
    """Safety validation rejects AI output referencing forged observation IDs."""
    payload_unknown_obs_id = {
        "summary": "Summary text.",
        "analyte_remarks": [
            {
                "analyte": "glucose",
                "observation_id": "forged-id-12345",  # Forged!
                "provider_flag": "normal",
                "summary": "Normal glucose.",
            }
        ],
        "source_observation_ids": ["forged-id-12345"],
        "caveat_codes": [
            "UNIT_ASSUMPTION",
            "FASTING_STATUS_NOT_CONFIRMED",
            "DEMOGRAPHIC_CONTEXT_NOT_CONFIRMED",
        ],
        "generation_label": "AI_GENERATED",
    }

    raw_json = AiRemarksPayload.model_validate(payload_unknown_obs_id).model_dump_json()

    with pytest.raises(OllamaSafetyValidationError) as exc_info:
        validate_ai_remarks_output(raw_json, sample_testwell_result, required_caveats)

    assert any("forged-id-12345" in v for v in exc_info.value.violations)


@pytest.mark.parametrize(
    "forbidden_phrase",
    [
        "You have been diagnosed with type 2 diabetes.",
        "I prescribe metformin 500mg daily.",
        "Take insulin before bedtime.",
        "The patient is diagnosed with cardiac failure.",
        "The disease probability is 95%.",
        "Physician-reviewed laboratory observations with noted context limitations.",
        "The patient results were reviewed by a physician.",
    ],
)
def test_safety_rejects_diagnostic_or_prescriptive_claims(
    sample_testwell_result: NormalizedProviderResult,
    required_caveats: list[str],
    forbidden_phrase: str,
) -> None:
    """Safety validation rejects unauthorized medical diagnoses, prescriptions, and disease probabilities."""
    forbidden_payload = {
        "summary": forbidden_phrase,
        "analyte_remarks": [
            {
                "analyte": "glucose",
                "observation_id": "obs-glucose",
                "provider_flag": "normal",
                "summary": "Normal glucose.",
            }
        ],
        "source_observation_ids": ["obs-glucose"],
        "caveat_codes": [
            "UNIT_ASSUMPTION",
            "FASTING_STATUS_NOT_CONFIRMED",
            "DEMOGRAPHIC_CONTEXT_NOT_CONFIRMED",
        ],
        "generation_label": "AI_GENERATED",
    }

    raw_json = AiRemarksPayload.model_validate(forbidden_payload).model_dump_json()

    with pytest.raises(OllamaSafetyValidationError) as exc_info:
        validate_ai_remarks_output(raw_json, sample_testwell_result, required_caveats)

    assert any(
        "unauthorized diagnostic or prescriptive language" in v for v in exc_info.value.violations
    )


def test_safety_rejects_unparseable_json(
    sample_testwell_result: NormalizedProviderResult,
    required_caveats: list[str],
) -> None:
    """Validation rejects raw responses that are not valid JSON."""
    with pytest.raises(OllamaResponseError) as exc_info:
        validate_ai_remarks_output(
            "Here is the analysis: glucose is normal.",
            sample_testwell_result,
            required_caveats,
        )

    assert "not valid JSON" in str(exc_info.value)


def test_deterministic_fallback_rendering(sample_testwell_result: NormalizedProviderResult) -> None:
    """Deterministic fallback produces rule-based remarks accurately labelled as DETERMINISTIC_FALLBACK."""
    fallback_text, fallback_payload = render_deterministic_fallback(
        sample_testwell_result,
        fallback_reason="OLLAMA_TIMEOUT",
    )

    assert fallback_payload["generation_label"] == "DETERMINISTIC_FALLBACK"
    assert fallback_payload["fallback_reason"] == "OLLAMA_TIMEOUT"
    assert fallback_payload["observations_count"] == 3

    # Check caveat codes
    assert "UNIT_ASSUMPTION" in fallback_payload["caveat_codes"]
    assert "FASTING_STATUS_NOT_CONFIRMED" in fallback_payload["caveat_codes"]
    assert "DEMOGRAPHIC_CONTEXT_NOT_CONFIRMED" in fallback_payload["caveat_codes"]

    # Check formatted text representation
    assert "[AI Remarks Unavailable — Provider Information Shown]" in fallback_text
    assert "Glucose: 94.0 mg/dL" in fallback_text
    assert "70 – 99 mg/dL" in fallback_text
    assert "flag: normal" in fallback_text
    assert "Total Cholesterol: 225.0 mg/dL" in fallback_text
    assert "flag: high" in fallback_text
    assert "Clinical Caveats:" in fallback_text
