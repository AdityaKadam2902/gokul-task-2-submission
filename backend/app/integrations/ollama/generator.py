"""High-level generator orchestrating Ollama prompt generation, validation, and safe fallback.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import logging
from typing import Any

import httpx

from app.integrations.ollama.client import OllamaClient
from app.integrations.ollama.exceptions import OllamaError
from app.integrations.ollama.fallback import render_deterministic_fallback
from app.integrations.ollama.prompts import build_ollama_prompt
from app.integrations.ollama.schemas import AiRemarksPayload
from app.integrations.ollama.validator import validate_ai_remarks_output
from app.integrations.testwell.normalizer import NormalizedProviderResult

logger = logging.getLogger(__name__)


class OllamaRemarksGenerator:
    """Orchestrates local AI remarks generation from normalized TestWell observations."""

    __test__ = False

    def __init__(self, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()

    async def generate_remarks(
        self,
        normalized_result: NormalizedProviderResult,
        http_client: httpx.AsyncClient | None = None,
    ) -> tuple[str, dict[str, Any], bool, float]:
        """Generate structured clinical remarks using local Ollama model.

        Returns:
            (remarks_text, result_json, is_ai_generated, latency_ms)

        If local Ollama fails, times out, or violates clinical safety rules:
            Seamlessly produces a deterministic fallback with is_ai_generated=False.
        """
        system_instruction, user_prompt, required_caveats = build_ollama_prompt(normalized_result)
        format_schema = AiRemarksPayload.model_json_schema()

        try:
            raw_text, latency_ms = await self.client.generate_completion(
                prompt=user_prompt,
                system_instruction=system_instruction,
                format_schema=format_schema,
                http_client=http_client,
            )

            # Strict multi-layered validation
            validated_payload = validate_ai_remarks_output(
                raw_response_text=raw_text,
                normalized_provider_result=normalized_result,
                required_caveats=required_caveats,
            )

            # Format final remarks text for presentation
            remarks_lines = [
                f"[AI Remarks — {self.client.model}]",
                validated_payload.summary,
                "",
                "Biomarker Reference Observations:",
            ]
            for ar in validated_payload.analyte_remarks:
                remarks_lines.append(
                    f"- {ar.analyte.capitalize()}: {ar.summary} (flag: {ar.provider_flag})"
                )

            remarks_lines.append("")
            remarks_lines.append("Clinical Caveats:")
            for c in validated_payload.caveat_codes:
                remarks_lines.append(f"- {c}")

            remarks_lines.append(
                "- Educational reference only. Provider observations do not replace a confirmed laboratory report or physician diagnosis."
            )

            formatted_remarks = "\n".join(remarks_lines)
            return formatted_remarks, validated_payload.model_dump(), True, latency_ms

        except (OllamaError, Exception) as err:
            logger.warning(
                "Ollama generation failed or safety validation rejected output (%s). Using deterministic fallback.",
                err,
            )
            fallback_text, fallback_payload = render_deterministic_fallback(
                normalized_result=normalized_result,
                fallback_reason=str(err),
            )
            return fallback_text, fallback_payload, False, 0.0
