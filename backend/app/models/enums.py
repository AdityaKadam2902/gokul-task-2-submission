"""Domain status enumerations for analysis lifecycle.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from enum import Enum


class ExternalStatus(str, Enum):
    """Status of external provider (TestWell) call."""

    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    NO_MATCH = "NO_MATCH"
    FAILED = "FAILED"
    NOT_RUN = "NOT_RUN"


class AiStatus(str, Enum):
    """Status of local AI (Ollama llama3.2:3b) processing."""

    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FALLBACK = "FALLBACK"
    FAILED = "FAILED"
    NOT_RUN = "NOT_RUN"


class OverallStatus(str, Enum):
    """Aggregate lifecycle status of the patient analysis."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    NOT_RUN = "NOT_RUN"
