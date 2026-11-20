"""Response normalization and validation for TestWell health interpretation.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field

from app.integrations.testwell.schemas import TestWellRawResponse


def sanitize_https_url(url: str | None) -> str | None:
    """Validate and sanitize external URLs.

    Only permits safe HTTPS URLs. Rejects HTTP, javascript, data, or malformed URIs.
    """
    if not url or not isinstance(url, str):
        return None
    url_stripped = url.strip()
    try:
        parsed = urlsplit(url_stripped)
        if parsed.scheme.lower() != "https":
            return None
        if not parsed.netloc or " " in parsed.netloc:
            return None
        return url_stripped
    except Exception:
        return None


class ProviderCitation(BaseModel):
    """Physician-reviewed medical reference citation from provider."""

    model_config = ConfigDict(extra="ignore")

    label: str
    url: str | None = None


class NormalizedObservation(BaseModel):
    """Normalized clinical observation for a single laboratory biomarker."""

    model_config = ConfigDict(extra="ignore")

    analyte: str = Field(
        ..., description="Internal analyte key (glucose, haemoglobin, cholesterol)"
    )
    query_marker: str = Field(..., description="Marker name submitted to provider query")
    matched_marker: str | None = Field(
        default=None, description="Marker name reported back by provider"
    )
    value: float = Field(..., description="Analyte numeric measurement value")
    unit: str = Field(..., description="Analyte measurement unit")
    found: bool = Field(default=False, description="Whether provider recognized this biomarker")
    flag: str = Field(default="unknown", description="Provider flag: low, normal, high, or unknown")
    range_text: str | None = Field(default=None, description="Formatted reference interval string")
    range_min: float | None = Field(default=None, description="Lower bound of reference interval")
    range_max: float | None = Field(default=None, description="Upper bound of reference interval")
    range_unit: str | None = Field(default=None, description="Unit of reference interval")
    range_qualifier: str | None = Field(
        default=None, description="Demographic/physiological qualifier (e.g. fasting)"
    )
    unit_mismatch: bool = Field(
        default=False, description="Whether submitted unit mismatched provider baseline"
    )
    context_status: str = Field(
        default="CONFIRMED", description="CONFIRMED or CONTEXT_NOT_CONFIRMED"
    )
    suggests: str | None = Field(default=None, description="Educational guidance from provider")
    retest: str | None = Field(default=None, description="Retest guidance from provider")
    citations: list[ProviderCitation] = Field(default_factory=list)
    links: dict[str, str | None] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class NormalizedProviderResult(BaseModel):
    """Normalized, strongly-typed representation of TestWell interpretation payload."""

    model_config = ConfigDict(extra="ignore")

    provider: str = "testwell"
    endpoint: str = "https://www.test-well.com/api/agent/interpret_results"
    api_version: str = "1.2.0"
    catalog_review_date: str | None = None
    reviewer: str | None = None
    disclaimer: str = (
        "Educational assessment prototype only. Provider ranges and explanations are "
        "informational and depend on the assumptions and context shown. This application "
        "does not diagnose, provide medical advice or replace the laboratory report or a qualified clinician."
    )
    observations: list[NormalizedObservation] = Field(default_factory=list)
    summary: dict[str, int] = Field(
        default_factory=lambda: {
            "total": 0,
            "matched": 0,
            "high": 0,
            "low": 0,
            "normal": 0,
            "unknown": 0,
        }
    )
    global_caveats: list[str] = Field(default_factory=list)
    retrieved_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    latency_ms: float | None = None


# Marker query aliases mapping internal analyte names to TestWell catalog markers
MARKER_QUERY_MAP: dict[str, str] = {
    "glucose": "glucose",
    "haemoglobin": "hemoglobin",
    "hemoglobin": "hemoglobin",
    "cholesterol": "total cholesterol",
    "total_cholesterol": "total cholesterol",
}


def normalize_testwell_response(
    raw_response: dict[str, Any] | TestWellRawResponse,
    input_snapshot: dict[str, Any],
    latency_ms: float | None = None,
) -> NormalizedProviderResult:
    """Normalize and validate raw TestWell response against domain snapshot."""
    if isinstance(raw_response, dict):
        validated_raw = TestWellRawResponse.model_validate(raw_response)
    else:
        validated_raw = raw_response

    result_data = validated_raw.result

    # Map raw result items by normalized input marker name (lowercased)
    raw_by_marker: dict[str, Any] = {}
    for item in result_data.results:
        raw_marker = item.input.marker.lower().strip()
        raw_by_marker[raw_marker] = item

    observations: list[NormalizedObservation] = []
    global_caveats: list[str] = [
        "UNIT_ASSUMPTION: mg/dL, g/dL, mg/dL are assessment demonstration assumptions, not confirmed clinical lab units.",
        "EDUCATIONAL_REFERENCE: Provider ranges and explanations are educational reference material; not clinical diagnosis or medical advice.",
    ]

    # Process expected analytes from snapshot
    analytes_info = [
        (
            "glucose",
            input_snapshot.get("glucose_value"),
            input_snapshot.get("glucose_unit", "mg/dL"),
        ),
        (
            "haemoglobin",
            input_snapshot.get("haemoglobin_value"),
            input_snapshot.get("haemoglobin_unit", "g/dL"),
        ),
        (
            "cholesterol",
            input_snapshot.get("cholesterol_value"),
            input_snapshot.get("cholesterol_unit", "mg/dL"),
        ),
    ]

    matched_count = 0
    high_count = 0
    low_count = 0
    normal_count = 0
    unknown_count = 0

    for analyte, value_val, unit_val in analytes_info:
        if value_val is None:
            continue

        numeric_val = float(value_val)
        unit_str = str(unit_val)
        query_marker = MARKER_QUERY_MAP.get(analyte, analyte)

        # Look up item in provider response
        raw_item = raw_by_marker.get(query_marker.lower()) or raw_by_marker.get(analyte.lower())

        if raw_item is None:
            # Marker was completely missing from provider response
            observations.append(
                NormalizedObservation(
                    analyte=analyte,
                    query_marker=query_marker,
                    matched_marker=None,
                    value=numeric_val,
                    unit=unit_str,
                    found=False,
                    flag="unknown",
                    warnings=[f"Provider response omitted interpretation for {analyte}."],
                )
            )
            unknown_count += 1
            continue

        # Extract provider fields
        found = bool(raw_item.found)
        flag = str(raw_item.flag).lower() if raw_item.flag else "unknown"
        if flag not in ("low", "normal", "high", "unknown"):
            flag = "unknown"

        unit_mismatch = bool(raw_item.unitMismatch)
        if unit_mismatch:
            flag = "unknown"

        range_obj = raw_item.range
        range_text = range_obj.text if range_obj else None
        range_min = float(range_obj.min) if range_obj and range_obj.min is not None else None
        range_max = float(range_obj.max) if range_obj and range_obj.max is not None else None
        range_unit = range_obj.unit if range_obj else None
        range_qualifier = range_obj.qualifier if range_obj else None

        # Determine context limitations
        context_status = "CONFIRMED"
        obs_warnings: list[str] = []

        if not found:
            obs_warnings.append(
                f"Biomarker '{analyte}' not recognized in provider reference catalog."
            )
        elif unit_mismatch:
            obs_warnings.append(
                f"Provider reported unit mismatch for {analyte} (input: {unit_str}). Result cannot be interpreted."
            )
        else:
            # Check for unconfirmed assumptions in returned qualifier
            if range_qualifier:
                qual_lower = range_qualifier.lower()
                if "fasting" in qual_lower:
                    context_status = "CONTEXT_NOT_CONFIRMED"
                    obs_warnings.append(
                        "Provider reference interval assumes fasting state, which was not confirmed for this patient."
                    )
                if "male" in qual_lower or "female" in qual_lower:
                    context_status = "CONTEXT_NOT_CONFIRMED"
                    obs_warnings.append(
                        f"Provider reference interval assumes demographic context ('{range_qualifier}'), which was not confirmed."
                    )
                if "age" in qual_lower and context_status == "CONFIRMED":
                    context_status = "CONTEXT_NOT_CONFIRMED"
                    obs_warnings.append("Provider reference interval assumes adult baseline.")

        # Sanitize citations
        safe_citations: list[ProviderCitation] = []
        for cit in raw_item.citations:
            safe_url = sanitize_https_url(cit.url)
            safe_citations.append(ProviderCitation(label=cit.label, url=safe_url))

        # Sanitize links
        safe_links: dict[str, str | None] = {}
        if raw_item.links:
            safe_links["biomarker"] = sanitize_https_url(raw_item.links.biomarker)
            safe_links["interpretation"] = sanitize_https_url(raw_item.links.interpretation)
            safe_links["orderTest"] = sanitize_https_url(raw_item.links.orderTest)

        if found and not unit_mismatch:
            matched_count += 1
            if flag == "high":
                high_count += 1
            elif flag == "low":
                low_count += 1
            elif flag == "normal":
                normal_count += 1
            else:
                unknown_count += 1
        else:
            unknown_count += 1

        observations.append(
            NormalizedObservation(
                analyte=analyte,
                query_marker=query_marker,
                matched_marker=raw_item.marker,
                value=numeric_val,
                unit=unit_str,
                found=found,
                flag=flag,
                range_text=range_text,
                range_min=range_min,
                range_max=range_max,
                range_unit=range_unit,
                range_qualifier=range_qualifier,
                unit_mismatch=unit_mismatch,
                context_status=context_status,
                suggests=raw_item.suggests,
                retest=raw_item.retest,
                citations=safe_citations,
                links=safe_links,
                warnings=obs_warnings,
            )
        )

    # Review metadata
    catalog_date = result_data.reviewed.catalog if result_data.reviewed else None
    reviewer_name = result_data.reviewed.reviewer if result_data.reviewed else None
    disclaimer_text = result_data.disclaimer or NormalizedProviderResult().disclaimer

    return NormalizedProviderResult(
        provider="testwell",
        endpoint="https://www.test-well.com/api/agent/interpret_results",
        api_version="1.2.0",
        catalog_review_date=catalog_date,
        reviewer=reviewer_name,
        disclaimer=disclaimer_text,
        observations=observations,
        summary={
            "total": len(observations),
            "matched": matched_count,
            "high": high_count,
            "low": low_count,
            "normal": normal_count,
            "unknown": unknown_count,
        },
        global_caveats=global_caveats,
        retrieved_at=datetime.now(UTC).isoformat(),
        latency_ms=latency_ms,
    )
