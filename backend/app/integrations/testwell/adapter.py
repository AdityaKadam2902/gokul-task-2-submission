"""High-level adapter orchestrating TestWell API communication and normalization.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from decimal import Decimal
from typing import Any

import httpx

from app.integrations.testwell.client import TestWellClient
from app.integrations.testwell.normalizer import (
    NormalizedProviderResult,
    normalize_testwell_response,
)
from app.integrations.testwell.schemas import (
    TestWellBiomarkerInput,
    TestWellInterpretRequest,
)


class TestWellAdapter:
    """High-level adapter for TestWell laboratory results interpretation."""

    __test__ = False

    def __init__(self, client: TestWellClient | None = None) -> None:
        self.client = client or TestWellClient()

    async def interpret_biomarkers(
        self,
        glucose_value: Decimal | float,
        haemoglobin_value: Decimal | float,
        cholesterol_value: Decimal | float,
        unit_profile_code: str = "ASSESSMENT_CONVENTIONAL_V1",
        http_client: httpx.AsyncClient | None = None,
    ) -> NormalizedProviderResult:
        """Execute biomarker interpretation against TestWell and return normalized domain observations.

        Strictly transmits only anonymous numeric values and units.
        Never transmits patient identifiers, dates of birth, or names.
        """
        # Build anonymous outgoing request
        request = TestWellInterpretRequest(
            values=[
                TestWellBiomarkerInput(marker="glucose", value=float(glucose_value), unit="mg/dL"),
                TestWellBiomarkerInput(
                    marker="hemoglobin", value=float(haemoglobin_value), unit="g/dL"
                ),
                TestWellBiomarkerInput(
                    marker="total cholesterol", value=float(cholesterol_value), unit="mg/dL"
                ),
            ]
        )

        # Snapshot for normalizer context comparison
        input_snapshot: dict[str, Any] = {
            "glucose_value": float(glucose_value),
            "glucose_unit": "mg/dL",
            "haemoglobin_value": float(haemoglobin_value),
            "haemoglobin_unit": "g/dL",
            "cholesterol_value": float(cholesterol_value),
            "cholesterol_unit": "mg/dL",
            "unit_profile_code": unit_profile_code,
        }

        # Dispatch request through client
        raw_response, latency_ms = await self.client.interpret_results(
            request=request,
            client=http_client,
        )

        # Normalize and validate raw response
        normalized = normalize_testwell_response(
            raw_response=raw_response,
            input_snapshot=input_snapshot,
            latency_ms=latency_ms,
        )

        return normalized
