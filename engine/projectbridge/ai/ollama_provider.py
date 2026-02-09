"""Ollama AI provider — fully local inference via the Ollama REST API.

No data leaves the machine. Requires Ollama running at localhost:11434.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

from projectbridge.ai.provider import AIProvider, register_provider

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_DEFAULT_BASE_URL = "http://localhost:11434"
_DEFAULT_MODEL = "llama3.2"


class OllamaProviderError(Exception):
    """Raised when the Ollama provider encounters an error."""


class OllamaProvider(AIProvider):
    """AI provider backed by a local Ollama instance.

    Args:
        model: Ollama model name (default: ``llama3.2``).
        base_url: Ollama server URL (default: ``http://localhost:11434``).
    """

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

    def analyze_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Enhance developer context using Ollama."""
        system_prompt = _load_prompt("analyze_context.txt")
        user_message = json.dumps(context, indent=2, default=str)

        response_text = self._chat(system_prompt, user_message)

        try:
            enriched = json.loads(response_text)
        except json.JSONDecodeError:
            enriched = {**context, "ai_summary": response_text}

        for key, value in context.items():
            if key not in enriched:
                enriched[key] = value

        return enriched

    def generate_recommendations(self, gaps: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate project recommendations using Ollama."""
        system_prompt = _load_prompt("generate_recommendations.txt")
        user_message = json.dumps(gaps, indent=2, default=str)

        response_text = self._chat(system_prompt, user_message)

        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            raise OllamaProviderError(
                "Ollama returned an invalid JSON response for recommendations."
            )

        if isinstance(parsed, dict):
            recommendations = parsed.get("recommendations", [])
        elif isinstance(parsed, list):
            recommendations = parsed
        else:
            raise OllamaProviderError(
                "Ollama returned an unexpected response format for recommendations."
            )

        return recommendations

    def _chat(self, system_prompt: str, user_message: str) -> str:
        """Send a chat request to the Ollama API.

        Raises:
            OllamaProviderError: On connection or API errors.
        """
        url = f"{self._base_url}/api/chat"
        payload = json.dumps({
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "format": "json",
        }).encode()

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
            raise OllamaProviderError(
                f"Failed to connect to Ollama: {exc}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise OllamaProviderError(
                "Ollama returned an invalid response."
            ) from exc

        return body.get("message", {}).get("content", "")


def _load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = _PROMPTS_DIR / filename
    if not path.is_file():
        raise OllamaProviderError(f"Prompt template not found: {path}")
    return path.read_text().strip()


# Auto-register when imported.
register_provider("ollama", OllamaProvider)
