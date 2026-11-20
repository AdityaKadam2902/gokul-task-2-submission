"""Unit and integration tests for Ollama HTTP client.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import httpx
import pytest
import respx
from app.integrations.ollama.client import OllamaClient
from app.integrations.ollama.exceptions import (
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaResponseError,
    OllamaTimeoutError,
)


@pytest.fixture
def ollama_client() -> OllamaClient:
    return OllamaClient(
        base_url="http://127.0.0.1:11434",
        model="llama3.2:3b",
        timeout_seconds=5.0,
        temperature=0.1,
        max_tokens=350,
    )


@pytest.mark.asyncio
@respx.mock
async def test_ollama_generate_success(ollama_client: OllamaClient) -> None:
    """Test successful JSON generation from local Ollama daemon."""
    raw_response = {
        "model": "llama3.2:3b",
        "created_at": "2026-11-18T10:00:00Z",
        "response": '{"summary": "Normal laboratory values observed.", "generation_label": "AI_GENERATED"}',
        "done": True,
        "total_duration": 1500000000,
        "load_duration": 100000000,
        "prompt_eval_count": 85,
        "eval_count": 45,
    }

    respx.post("http://127.0.0.1:11434/api/generate").mock(
        return_value=httpx.Response(200, json=raw_response)
    )

    resp_text, latency_ms = await ollama_client.generate_completion(
        prompt="Synthesize observations...",
        system_instruction="Clinical assistant prompt...",
    )
    assert "Normal laboratory values observed." in resp_text
    assert latency_ms >= 0.0


@pytest.mark.asyncio
@respx.mock
async def test_ollama_connection_error(ollama_client: OllamaClient) -> None:
    """Test handling of Ollama daemon connection error (e.g. daemon stopped)."""
    respx.post("http://127.0.0.1:11434/api/generate").mock(
        side_effect=httpx.ConnectError("Failed to connect to 127.0.0.1:11434")
    )

    with pytest.raises(OllamaConnectionError) as exc_info:
        await ollama_client.generate_completion(prompt="Synthesize observations...")

    assert exc_info.value.error_code == "OLLAMA_CONNECTION_FAILED"
    assert "Failed to connect to local Ollama daemon" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_ollama_timeout_error(ollama_client: OllamaClient) -> None:
    """Test handling of Ollama inference timeout."""
    respx.post("http://127.0.0.1:11434/api/generate").mock(
        side_effect=httpx.ReadTimeout("Inference timed out after 5.0 seconds")
    )

    with pytest.raises(OllamaTimeoutError) as exc_info:
        await ollama_client.generate_completion(prompt="Synthesize observations...")

    assert exc_info.value.error_code == "OLLAMA_TIMEOUT"
    assert "timed out" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_ollama_model_not_found_404(ollama_client: OllamaClient) -> None:
    """Test handling when specified model is missing from Ollama library."""
    respx.post("http://127.0.0.1:11434/api/generate").mock(
        return_value=httpx.Response(
            404, json={"error": "model 'llama3.2:3b' not found, try pulling it first"}
        )
    )

    with pytest.raises(OllamaModelNotFoundError) as exc_info:
        await ollama_client.generate_completion(prompt="Synthesize observations...")

    assert exc_info.value.error_code == "OLLAMA_MODEL_NOT_FOUND"
    assert "llama3.2:3b" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_ollama_http_500_response_error(ollama_client: OllamaClient) -> None:
    """Test handling of Ollama server-side HTTP 500 error."""
    respx.post("http://127.0.0.1:11434/api/generate").mock(
        return_value=httpx.Response(500, text="Internal server error in llama runner")
    )

    from app.integrations.ollama.exceptions import OllamaError

    with pytest.raises(OllamaError) as exc_info:
        await ollama_client.generate_completion(prompt="Synthesize observations...")

    assert "HTTP 500" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_ollama_malformed_json_response(ollama_client: OllamaClient) -> None:
    """Test handling when Ollama returns non-JSON HTTP 200 payload."""
    respx.post("http://127.0.0.1:11434/api/generate").mock(
        return_value=httpx.Response(200, text="<html><body>Gateway Error</body></html>")
    )

    with pytest.raises(OllamaResponseError) as exc_info:
        await ollama_client.generate_completion(prompt="Synthesize observations...")

    assert "Failed to parse Ollama response JSON" in str(exc_info.value)
