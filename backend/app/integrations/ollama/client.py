"""HTTP client for local Ollama daemon.

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
from app.integrations.ollama.exceptions import (
    OllamaConnectionError,
    OllamaError,
    OllamaModelNotFoundError,
    OllamaResponseError,
    OllamaTimeoutError,
)
from app.integrations.ollama.schemas import (
    OllamaGenerateRequest,
    OllamaGenerateResponse,
)

logger = logging.getLogger(__name__)

# Bounded concurrency semaphore: prevents parallel CPU inference spikes on local workstation
_inference_semaphore: asyncio.Semaphore | None = None


def get_inference_semaphore() -> asyncio.Semaphore:
    """Retrieve or lazily initialize the inference concurrency semaphore."""
    global _inference_semaphore
    if _inference_semaphore is None:
        _inference_semaphore = asyncio.Semaphore(1)
    return _inference_semaphore


class OllamaClient:
    """Asynchronous client for communicating with local Ollama service."""

    __test__ = False

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        keep_alive: str | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout_seconds = timeout_seconds or settings.ollama_timeout_seconds
        self.temperature = temperature if temperature is not None else settings.ollama_temperature
        self.max_tokens = max_tokens or settings.ollama_max_tokens
        self.keep_alive = keep_alive or settings.ollama_keep_alive

    async def generate_completion(
        self,
        prompt: str,
        system_instruction: str | None = None,
        format_schema: dict[str, Any] | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> tuple[str, float]:
        """Dispatch inference request to Ollama with JSON Schema structured format.

        Returns:
            (raw_response_text, latency_ms)
        Raises:
            OllamaConnectionError, OllamaTimeoutError, OllamaModelNotFoundError, OllamaError
        """
        request_body = OllamaGenerateRequest(
            model=self.model,
            prompt=prompt,
            system=system_instruction,
            format=format_schema,
            stream=False,
            options={
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
            keep_alive=self.keep_alive,
        )

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        url = f"{self.base_url}/api/generate"
        logger.info("Dispatching local inference to Ollama: model=%s at %s", self.model, url)

        # Acquire inference semaphore to enforce bounded CPU concurrency
        async with get_inference_semaphore():
            start_time = time.perf_counter()
            try:
                if http_client is not None:
                    response = await http_client.post(
                        url,
                        json=request_body.model_dump(exclude_none=True),
                        headers=headers,
                        timeout=self.timeout_seconds,
                    )
                else:
                    async with httpx.AsyncClient(timeout=self.timeout_seconds) as session:
                        response = await session.post(
                            url,
                            json=request_body.model_dump(exclude_none=True),
                            headers=headers,
                        )

                latency_ms = (time.perf_counter() - start_time) * 1000.0

                if response.status_code == 200:
                    try:
                        resp_data = response.json()
                        validated = OllamaGenerateResponse.model_validate(resp_data)
                        return validated.response, latency_ms
                    except Exception as err:
                        raise OllamaResponseError(
                            f"Failed to parse Ollama response JSON: {err}"
                        ) from err

                if response.status_code == 404:
                    raise OllamaModelNotFoundError(self.model)

                raise OllamaError(
                    f"Ollama daemon returned HTTP {response.status_code}: {response.text[:200]}",
                    status_code=response.status_code,
                )

            except (
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.PoolTimeout,
            ) as timeout_err:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.warning("Ollama inference timed out after %.1f ms", latency_ms)
                raise OllamaTimeoutError("Local AI model inference timed out.") from timeout_err

            except (httpx.ConnectError, httpx.NetworkError) as conn_err:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.warning(
                    "Failed to connect to Ollama daemon at %s: %s", self.base_url, conn_err
                )
                raise OllamaConnectionError(
                    f"Failed to connect to local Ollama daemon at {self.base_url}."
                ) from conn_err

            except OllamaError:
                raise

            except Exception as err:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.error("Unhandled error invoking Ollama API: %s", err)
                raise OllamaError(
                    f"Unexpected error communicating with local Ollama: {err}"
                ) from err
