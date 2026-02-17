"""Ollama AI provider — fully local inference via the Ollama REST API.

No data leaves the machine. Requires Ollama running at localhost:11434.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from projectbridge.ai.provider import AIProvider, AIProviderError, register_provider

_DEFAULT_BASE_URL = "http://localhost:11434"
_DEFAULT_MODEL = "llama3.2"


class OllamaProviderError(AIProviderError):
    """Raised when the Ollama provider encounters an error."""


class OllamaProvider(AIProvider):
    """AI provider backed by a local Ollama instance.

    Args:
        model: Ollama model name (default: ``llama3.2``).
        base_url: Ollama server URL (default: ``http://localhost:11434``).
    """

    _error_class = OllamaProviderError

    def __init__(
        self,
        model: str = _DEFAULT_MODEL,
        base_url: str = _DEFAULT_BASE_URL,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._check_server()

    def _check_server(self) -> None:
        """Verify that Ollama is reachable."""
        try:
            req = urllib.request.Request(self._base_url, method="GET")
            with urllib.request.urlopen(req, timeout=5):
                pass
        except (urllib.error.URLError, OSError) as exc:
            raise OllamaProviderError(
                f"Cannot reach Ollama at {self._base_url}. "
                "Make sure Ollama is running (https://ollama.com)."
            ) from exc

    def _chat(self, system_prompt: str, user_message: str) -> str:
        """Send a chat request to the Ollama API."""
        url = f"{self._base_url}/api/chat"
        payload = json.dumps(
            {
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
                "format": "json",
            }
        ).encode()

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read())
        except urllib.error.URLError as exc:
            raise OllamaProviderError(f"Failed to connect to Ollama: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise OllamaProviderError("Ollama returned an invalid response.") from exc

        return body.get("message", {}).get("content", "")


# Auto-register when imported.
register_provider("ollama", OllamaProvider)
