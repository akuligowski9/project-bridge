"""Anthropic Claude AI provider — uses the Anthropic API for context analysis and recommendations.

Prompts are loaded from editable template files in the ``prompts/`` directory
(shared with other providers).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from projectbridge.ai.provider import AIProvider, register_provider

_PROMPTS_DIR = Path(__file__).parent / "prompts"


class AnthropicProviderError(Exception):
    """Raised when the Anthropic provider encounters an error."""


class AnthropicProvider(AIProvider):
    """AI provider backed by the Anthropic Claude API.

    Args:
        api_key: Anthropic API key. If *None*, reads from the
            ``ANTHROPIC_API_KEY`` environment variable.
        model: Model identifier to use (default: ``claude-sonnet-4-5-20250929``).
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-5-20250929",
    ) -> None:
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self._api_key:
            raise AnthropicProviderError(
                "Anthropic API key not found. Set the ANTHROPIC_API_KEY environment "
                "variable or pass api_key to the provider."
            )
        self._model = model
        self._client = self._create_client()

    def _create_client(self) -> Any:
        """Create and return an Anthropic client instance."""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise AnthropicProviderError(
                "The 'anthropic' package is required for the Anthropic provider. "
                "Install it with: pip install anthropic"
            )
        return Anthropic(api_key=self._api_key)

    def analyze_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Enhance developer context using Claude."""
        system_prompt = _load_prompt("analyze_context.txt")
        user_message = json.dumps(context, indent=2, default=str)

        response_text = self._chat(system_prompt, user_message)

        try:
            enriched = json.loads(response_text)
        except json.JSONDecodeError:
            enriched = {**context, "ai_summary": response_text}

        # Ensure original fields are never lost.
        for key, value in context.items():
            if key not in enriched:
                enriched[key] = value

        return enriched

    def generate_recommendations(self, gaps: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate project recommendations using Claude."""
        system_prompt = _load_prompt("generate_recommendations.txt")
        user_message = json.dumps(gaps, indent=2, default=str)

        response_text = self._chat(system_prompt, user_message)

        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            raise AnthropicProviderError(
                "Anthropic returned an invalid JSON response for recommendations."
            )

        # The prompt asks for {"recommendations": [...]}.
        if isinstance(parsed, dict):
            recommendations = parsed.get("recommendations", [])
        elif isinstance(parsed, list):
            recommendations = parsed
        else:
            raise AnthropicProviderError(
                "Anthropic returned an unexpected response format for recommendations."
            )

        return recommendations

    def _chat(self, system_prompt: str, user_message: str) -> str:
        """Send a message to the Anthropic API and return the response text.

        Raises:
            AnthropicProviderError: On API or authentication errors.
        """
        try:
            from anthropic import (
                AuthenticationError,
                APIConnectionError,
                RateLimitError,
            )
        except ImportError:
            raise AnthropicProviderError("The 'anthropic' package is not installed.")

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message},
                ],
            )
            # Anthropic returns a list of content blocks; extract the first text block.
            for block in response.content:
                if block.type == "text":
                    return block.text
            return ""
        except AuthenticationError as exc:
            raise AnthropicProviderError(
                "Invalid Anthropic API key. Check your ANTHROPIC_API_KEY."
            ) from exc
        except RateLimitError as exc:
            raise AnthropicProviderError(
                "Anthropic API rate limit exceeded. Please wait and try again."
            ) from exc
        except APIConnectionError as exc:
            raise AnthropicProviderError(
                "Could not connect to the Anthropic API. Check your network connection."
            ) from exc
        except Exception as exc:
            raise AnthropicProviderError(
                f"Anthropic API error: {exc}"
            ) from exc


def _load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = _PROMPTS_DIR / filename
    if not path.is_file():
        raise AnthropicProviderError(f"Prompt template not found: {path}")
    return path.read_text().strip()


# Auto-register when imported.
register_provider("anthropic", AnthropicProvider)
