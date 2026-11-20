"""Ollama local AI integration package.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from app.integrations.ollama.client import OllamaClient
from app.integrations.ollama.exceptions import (
    OllamaConnectionError,
    OllamaError,
    OllamaModelNotFoundError,
    OllamaResponseError,
    OllamaSafetyValidationError,
    OllamaTimeoutError,
)
from app.integrations.ollama.fallback import render_deterministic_fallback
from app.integrations.ollama.generator import OllamaRemarksGenerator
from app.integrations.ollama.schemas import AiRemarksPayload, AnalyteRemark
from app.integrations.ollama.validator import validate_ai_remarks_output

__all__ = [
    "AiRemarksPayload",
    "AnalyteRemark",
    "OllamaClient",
    "OllamaConnectionError",
    "OllamaError",
    "OllamaModelNotFoundError",
    "OllamaRemarksGenerator",
    "OllamaResponseError",
    "OllamaSafetyValidationError",
    "OllamaTimeoutError",
    "render_deterministic_fallback",
    "validate_ai_remarks_output",
]
