"""HTTP client for TestWell external health interpretation API.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import asyncio
import logging
import time
from typing import Any

import httpx

from app.core.config import get_settings
from app.integrations.testwell.exceptions import (
    TestWellClientError,
    TestWellConnectionError,
    TestWellError,
    TestWellRateLimitError,
    TestWellResponseError,
    TestWellServerError,
    TestWellTimeoutError,
)
from app.integrations.testwell.schemas import TestWellInterpretRequest, TestWellRawResponse

logger = logging.getLogger(__name__)


class TestWellClient:
    """Asynchronous HTTP client for interacting with TestWell API."""

    __test__ = False

    def __init__(
        self,
        endpoint_url: str | None = None,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        backoff_seconds: float | None = None,
    ) -> None:
        settings = get_settings()
        self.endpoint_url = endpoint_url or settings.testwell_api_url
        self.timeout_seconds = timeout_seconds or settings.testwell_timeout_seconds
        self.max_retries = max_retries if max_retries is not None else settings.testwell_max_retries
        self.backoff_seconds = (
            backoff_seconds
            if backoff_seconds is not None
            else settings.testwell_retry_backoff_seconds
        )

    async def interpret_results(
        self,
        request: TestWellInterpretRequest,
        client: httpx.AsyncClient | None = None,
    ) -> tuple[TestWellRawResponse, float]:
        """Send biomarker interpretation request to TestWell with bounded transient retries.

        Returns tuple of (validated TestWellRawResponse, latency_ms).
        Raises appropriate TestWellError subclass on failure.
        """
        payload = request.model_dump()
        attempt = 0
        last_error: Exception | None = None
        latency_ms = 0.0

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "LabInsight-Health-Platform/0.1.0",
        }

        # Safe diagnostic log: analyte counts only, NO patient identities or measurements
        marker_names = [item["marker"] for item in payload.get("values", [])]
        logger.info(
            "Dispatching TestWell interpretation request: markers=%s, count=%d",
            marker_names,
            len(marker_names),
        )

        while attempt <= self.max_retries:
            attempt += 1
            start_time = time.perf_counter()

            try:
                # Use provided client or create an ephemeral async client
                if client is not None:
                    response = await client.post(
                        self.endpoint_url,
                        json=payload,
                        headers=headers,
                        timeout=self.timeout_seconds,
                    )
                else:
                    async with httpx.AsyncClient(timeout=self.timeout_seconds) as session:
                        response = await session.post(
                            self.endpoint_url,
                            json=payload,
                            headers=headers,
                        )

                latency_ms = (time.perf_counter() - start_time) * 1000.0

                # 1. Handle HTTP 200 OK
                if response.status_code == 200:
                    try:
                        raw_data: Any = response.json()
                        validated = TestWellRawResponse.model_validate(raw_data)
                        return validated, latency_ms
                    except Exception as parse_err:
                        logger.error("TestWell returned malformed JSON or schema: %s", parse_err)
                        raise TestWellResponseError(
                            "External health API returned an unparseable response schema."
                        ) from parse_err

                # 2. Handle Rate Limit (HTTP 429) - do not immediately hammer
                if response.status_code == 429:
                    retry_header = response.headers.get("Retry-After")
                    retry_after = (
                        int(retry_header) if retry_header and retry_header.isdigit() else None
                    )
                    logger.warning(
                        "TestWell rate limit encountered (429). Retry-After: %s", retry_after
                    )
                    raise TestWellRateLimitError(retry_after=retry_after)

                # 3. Handle Client Error (HTTP 400) - non-retryable
                if 400 <= response.status_code < 500:
                    logger.error(
                        "TestWell client error: HTTP %d - %s",
                        response.status_code,
                        response.text[:200],
                    )
                    raise TestWellClientError(
                        f"External health API rejected input values (HTTP {response.status_code})."
                    )

                # 4. Handle Server Error (HTTP 5xx) - transient candidate
                if response.status_code >= 500:
                    logger.warning(
                        "TestWell server error HTTP %d (attempt %d/%d)",
                        response.status_code,
                        attempt,
                        self.max_retries + 1,
                    )
                    last_error = TestWellServerError(
                        f"External health API server error (HTTP {response.status_code}).",
                        status_code=response.status_code,
                    )

            except (
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.PoolTimeout,
            ) as timeout_err:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.warning(
                    "TestWell timeout error (attempt %d/%d): %s",
                    attempt,
                    self.max_retries + 1,
                    timeout_err,
                )
                last_error = TestWellTimeoutError("External health API request timed out.")

            except (httpx.ConnectError, httpx.NetworkError, httpx.ProtocolError) as net_err:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.warning(
                    "TestWell network connection error (attempt %d/%d): %s",
                    attempt,
                    self.max_retries + 1,
                    net_err,
                )
                last_error = TestWellConnectionError(
                    "Failed to establish network connection to external health API."
                )

            except TestWellError:
                # Direct domain exception; do not catch and retry non-transient
                raise

            except Exception as unhandled_err:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.error("Unexpected error during TestWell HTTP dispatch: %s", unhandled_err)
                last_error = TestWellError(
                    f"Unexpected external API dispatch error: {unhandled_err}"
                )

            # If more retries remain, back off before retry
            if attempt <= self.max_retries:
                sleep_duration = self.backoff_seconds * (2 ** (attempt - 1))
                await asyncio.sleep(sleep_duration)

        # Exhausted retries
        if last_error is not None:
            raise last_error
        raise TestWellError("Failed to communicate with external health API after retries.")
