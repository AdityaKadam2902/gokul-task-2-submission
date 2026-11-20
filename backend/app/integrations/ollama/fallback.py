"""Deterministic fallback remarks renderer for when local AI generation fails or is unavailable.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from typing import Any

from app.integrations.testwell.normalizer import NormalizedProviderResult


def render_deterministic_fallback(
    normalized_result: NormalizedProviderResult,
    fallback_reason: str,
) -> tuple[str, dict[str, Any]]:
    """Generate a deterministic, rule-based summary strictly using validated TestWell facts.

    CRITICAL ARCHITECTURAL RULES:
    1. Built exclusively from validated provider observations.
    2. Clearly indicates that AI text generation was unavailable.
    3. Never claims to be AI-generated (generation_label = 'DETERMINISTIC_FALLBACK').
    4. Does not invent reference intervals or clinical diagnoses.

    Returns:
        (fallback_remarks_text, fallback_payload_dict)
    """
    lines: list[str] = [
        "[AI Remarks Unavailable — Provider Information Shown]",
        "TestWell educational reference observations:",
    ]

    for obs in normalized_result.observations:
        marker_name = obs.matched_marker or obs.analyte.capitalize()
        range_str = obs.range_text or "No reference range provided"

        qual_note = ""
        if obs.context_status != "CONFIRMED":
            if obs.range_qualifier:
                qual_note = (
                    f" (Context limitation: '{obs.range_qualifier}' not confirmed for patient)"
                )
            else:
                qual_note = " (Context limitation: demographic baseline not confirmed)"

        lines.append(
            f"- {marker_name}: {obs.value} {obs.unit} (flag: {obs.flag}, reference range: {range_str}{qual_note})"
        )

    lines.append("")
    lines.append("Clinical Caveats:")
    for caveat in normalized_result.global_caveats:
        lines.append(f"- {caveat}")

    lines.append(
        "- Educational reference only. Provider flags do not constitute a clinical diagnosis or medical advice."
    )

    fallback_text = "\n".join(lines)

    fallback_payload: dict[str, Any] = {
        "summary": "AI remarks unavailable; deterministic provider reference observations shown.",
        "generation_label": "DETERMINISTIC_FALLBACK",
        "fallback_reason": fallback_reason,
        "provider": normalized_result.provider,
        "observations_count": len(normalized_result.observations),
        "caveat_codes": [
            "UNIT_ASSUMPTION",
            "FASTING_STATUS_NOT_CONFIRMED"
            if any(
                "fasting" in (o.range_qualifier or "").lower()
                for o in normalized_result.observations
            )
            else None,
            "DEMOGRAPHIC_CONTEXT_NOT_CONFIRMED"
            if any(
                "male" in (o.range_qualifier or "").lower() for o in normalized_result.observations
            )
            else None,
        ],
    }
    # Filter out None caveat codes
    fallback_payload["caveat_codes"] = [
        c for c in fallback_payload["caveat_codes"] if c is not None
    ]

    return fallback_text, fallback_payload
