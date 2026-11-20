"""TestWell provider exception classes.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from typing import Any

from app.core.exceptions import AppException


class TestWellError(AppException):
    """Base exception for all TestWell integration failures."""

    __test__ = False

    def __init__(
        self,
        message: str,
        code: str = "TESTWELL_INTEGRATION_ERROR",
        status_code: int = 502,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)
        self.error_code = code
        self.error_summary = message


class TestWellConnectionError(TestWellError):
    """Network connection, DNS, or TLS handshake failure."""

    def __init__(self, message: str = "Failed to connect to external health API service.") -> None:
        super().__init__(
            message=message,
            code="TESTWELL_CONNECTION_FAILED",
            status_code=503,
        )


class TestWellTimeoutError(TestWellError):
    """Request timeout connecting to or reading from TestWell."""

    def __init__(self, message: str = "External health API request timed out.") -> None:
        super().__init__(
            message=message,
            code="TESTWELL_TIMEOUT",
            status_code=504,
        )


class TestWellRateLimitError(TestWellError):
    """Provider returned HTTP 429 rate limiting."""

    def __init__(
        self,
        message: str = "External health API rate limit exceeded. Please retry shortly.",
        retry_after: int | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="TESTWELL_RATE_LIMITED",
            status_code=429,
        )
        self.retry_after = retry_after


class TestWellResponseError(TestWellError):
    """Provider returned invalid JSON or response schema did not match contract."""

    def __init__(
        self,
        message: str = "External health API returned an unparseable or unexpected response.",
    ) -> None:
        super().__init__(
            message=message,
            code="TESTWELL_INVALID_RESPONSE",
            status_code=502,
        )


class TestWellClientError(TestWellError):
    """Provider returned HTTP 400 Bad Request."""

    def __init__(self, message: str = "External health API rejected the input parameters.") -> None:
        super().__init__(
            message=message,
            code="TESTWELL_BAD_REQUEST",
            status_code=502,
        )


class TestWellServerError(TestWellError):
    """Provider returned HTTP 5xx Server Error."""

    def __init__(
        self,
        message: str = "External health API encountered an internal server error.",
        status_code: int = 502,
    ) -> None:
        super().__init__(
            message=message,
            code="TESTWELL_SERVER_ERROR",
            status_code=status_code,
        )
