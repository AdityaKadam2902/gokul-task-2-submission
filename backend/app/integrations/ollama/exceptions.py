"""Ollama integration exception classes.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from typing import Any

from app.core.exceptions import AppException


class OllamaError(AppException):
    """Base exception for all Ollama local AI integration failures."""

    __test__ = False

    def __init__(
        self,
        message: str,
        code: str = "OLLAMA_INTEGRATION_ERROR",
        status_code: int = 502,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)
        self.error_code = code
        self.error_summary = message


class OllamaConnectionError(OllamaError):
    """Failed to connect to local Ollama daemon on loopback."""

    def __init__(
        self, message: str = "Failed to connect to local Ollama AI daemon at 127.0.0.1:11434."
    ) -> None:
        super().__init__(
            message=message,
            code="OLLAMA_CONNECTION_FAILED",
            status_code=503,
        )


class OllamaTimeoutError(OllamaError):
    """Inference request to Ollama timed out."""

    def __init__(self, message: str = "Local AI model inference timed out.") -> None:
        super().__init__(
            message=message,
            code="OLLAMA_TIMEOUT",
            status_code=504,
        )


class OllamaModelNotFoundError(OllamaError):
    """Configured model (llama3.2:3b) is not installed in local Ollama service."""

    def __init__(self, model_name: str = "llama3.2:3b") -> None:
        super().__init__(
            message=f"Configured model '{model_name}' is not installed in local Ollama service.",
            code="OLLAMA_MODEL_NOT_FOUND",
            status_code=502,
        )
        self.model_name = model_name


class OllamaResponseError(OllamaError):
    """Model output was not valid JSON or failed structured output parsing."""

    def __init__(
        self, message: str = "Local AI output was malformed or failed schema parsing."
    ) -> None:
        super().__init__(
            message=message,
            code="OLLAMA_INVALID_RESPONSE",
            status_code=502,
        )


class OllamaSafetyValidationError(OllamaError):
    """Model output violated clinical safety rules, altered provider flags, or invented content."""

    def __init__(self, message: str, violations: list[str] | None = None) -> None:
        details = [
            {"rule": "CLINICAL_SAFETY_VALIDATION", "violation": v} for v in (violations or [])
        ]
        super().__init__(
            message=message,
            code="OLLAMA_SAFETY_VALIDATION_FAILED",
            status_code=502,
            details=details,
        )
        self.violations = violations or []
