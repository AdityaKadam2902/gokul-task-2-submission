"""Safety, schema, and clinical integrity validation for Ollama-generated remarks.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import json
import re

from pydantic import ValidationError

from app.integrations.ollama.exceptions import (
    OllamaResponseError,
    OllamaSafetyValidationError,
)
from app.integrations.ollama.schemas import AiRemarksPayload
from app.integrations.testwell.normalizer import NormalizedProviderResult

# Forbidden phrases that claim clinical diagnosis, disease certainty, or medical prescriptions
FORBIDDEN_PHRASES: list[str] = [
    "you have been diagnosed with",
    "i diagnose you with",
    "confirmed diagnosis",
    "confirmed disease",
    "prescribe",
    "prescription",
    "take insulin",
    "start medication",
    "disease probability is",
    "you are diagnosed",
    "patient is diagnosed",
    "physician-reviewed",
    "physician reviewed",
    "reviewed by a physician",
]

FORBIDDEN_REGEX: list[re.Pattern[str]] = [
    re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE) for phrase in FORBIDDEN_PHRASES
]


def validate_ai_remarks_output(
    raw_response_text: str,
    normalized_provider_result: NormalizedProviderResult,
    required_caveats: list[str],
) -> AiRemarksPayload:
    """Execute multi-layered structural, semantic, and clinical safety validation.

    Raises:
        OllamaResponseError: if JSON parsing fails or schema structure is invalid.
        OllamaSafetyValidationError: if clinical safety or integrity constraints are violated.
    """
    violations: list[str] = []

    # 1. Parse JSON
    try:
        raw_data = json.loads(raw_response_text.strip())
    except Exception as parse_err:
        raise OllamaResponseError(f"Model response was not valid JSON: {parse_err}") from parse_err

    # 2. Validate against Pydantic schema
    try:
        payload = AiRemarksPayload.model_validate(raw_data)
    except ValidationError as schema_err:
        raise OllamaResponseError(
            f"Model output failed schema validation: {schema_err}"
        ) from schema_err

    # 3. Validate generation label
    if payload.generation_label != "AI_GENERATED":
        violations.append(
            f"generation_label must be 'AI_GENERATED', got '{payload.generation_label}'"
        )

    # 4. Map expected observations
    expected_by_analyte = {
        obs.analyte.lower(): obs for obs in normalized_provider_result.observations
    }
    valid_obs_ids = {
        f"obs-{obs.analyte.lower()}" for obs in normalized_provider_result.observations
    }

    # 5. Check analyte remarks integrity
    observed_analytes: set[str] = set()
    for remark in payload.analyte_remarks:
        analyte_key = remark.analyte.lower().strip()
        observed_analytes.add(analyte_key)

        expected_obs = expected_by_analyte.get(analyte_key)
        if expected_obs is None:
            violations.append(
                f"Model referenced unknown analyte '{remark.analyte}' not in provider observations."
            )
            continue

        # Check observation ID
        if remark.observation_id not in valid_obs_ids:
            violations.append(f"Observation ID '{remark.observation_id}' is invalid or fabricated.")

        # STRICT RULE: Provider flag must NOT be modified
        if remark.provider_flag.lower().strip() != expected_obs.flag.lower().strip():
            violations.append(
                f"Model altered provider flag for '{remark.analyte}' from '{expected_obs.flag}' to '{remark.provider_flag}'."
            )

    # 6. Check source observation IDs
    for obs_id in payload.source_observation_ids:
        if obs_id not in valid_obs_ids:
            violations.append(f"source_observation_ids contains unknown reference '{obs_id}'.")

    # 7. Check caveat retention
    for req_caveat in required_caveats:
        if req_caveat not in payload.caveat_codes:
            violations.append(
                f"Required clinical caveat code '{req_caveat}' was omitted by the model."
            )

    # 8. Check for unauthorized diagnostic or prescriptive assertions
    texts_to_scan = [payload.summary] + [r.summary for r in payload.analyte_remarks]
    for text in texts_to_scan:
        for pattern in FORBIDDEN_REGEX:
            if pattern.search(text):
                violations.append(
                    f"Model produced unauthorized diagnostic or prescriptive language matching '{pattern.pattern}'."
                )

    if violations:
        raise OllamaSafetyValidationError(
            message=f"Model output violated clinical safety constraints ({len(violations)} violations).",
            violations=violations,
        )

    return payload
