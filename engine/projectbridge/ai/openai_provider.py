"""OpenAI AI provider — uses the OpenAI API for context analysis and recommendations.

Prompts are loaded from editable template files in the ``prompts/`` directory.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from projectbridge.ai.provider import AIProvider, register_provider

_PROMPTS_DIR = Path(__file__).parent / "prompts"


class OpenAIProviderError(Exception):
    """Raised when the OpenAI provider encounters an error."""


class OpenAIProvider(AIProvider):
    """AI provider backed by the OpenAI API.

    Args:
        api_key: OpenAI API key. If *None*, reads from the
            ``OPENAI_API_KEY`` environment variable.
        model: Model identifier to use (default: ``gpt-4o``).
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o",
    ) -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self._api_key:
            raise OpenAIProviderError(
                "OpenAI API key not found. Set the OPENAI_API_KEY environment "
                "variable or pass api_key to the provider."
            )
        self._model = model
        self._client = self._create_client()

    def _create_client(self) -> Any:
        """Create and return an OpenAI client instance."""
        try:
            from openai import OpenAI
        except ImportError:
            raise OpenAIProviderError(
                "The 'openai' package is required for the OpenAI provider. "
                "Install it with: pip install openai"
            )
        return OpenAI(api_key=self._api_key)

    def analyze_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Enhance developer context using OpenAI."""
        system_prompt = _load_prompt("analyze_context.txt")
        user_message = json.dumps(context, indent=2, default=str)

        response_text = self._chat(system_prompt, user_message)

        try:
            enriched = json.loads(response_text)
        except json.JSONDecodeError:
            # If the model returns non-JSON, preserve original context
            # and add the raw response as a note.
            enriched = {**context}

        # Ensure original fields are never lost.
        for key, value in context.items():
            if key not in enriched:
                enriched[key] = value

        return enriched

    def generate_recommendations(self, gaps: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate project recommendations using OpenAI."""
        system_prompt = _load_prompt("generate_recommendations.txt")
        user_message = json.dumps(gaps, indent=2, default=str)

        response_text = self._chat(system_prompt, user_message)

        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            raise OpenAIProviderError(
                "OpenAI returned an invalid JSON response for recommendations."
            )

        # The prompt asks for {"recommendations": [...]}.
        if isinstance(parsed, dict):
            recommendations = parsed.get("recommendations", [])
        elif isinstance(parsed, list):
            recommendations = parsed
        else:
            raise OpenAIProviderError(
                "OpenAI returned an unexpected response format for recommendations."
            )

        return recommendations

    def _chat(self, system_prompt: str, user_message: str) -> str:
        """Send a chat completion request and return the response text.

        Raises:
            OpenAIProviderError: On API or authentication errors.
        """
        try:
            from openai import APIConnectionError, AuthenticationError, RateLimitError
        except ImportError:
            raise OpenAIProviderError("The 'openai' package is not installed.")

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or ""
        except AuthenticationError as exc:
            raise OpenAIProviderError(
                "Invalid OpenAI API key. Check your OPENAI_API_KEY."
            ) from exc
        except RateLimitError as exc:
            raise OpenAIProviderError(
                "OpenAI API rate limit exceeded. Please wait and try again."
            ) from exc
        except APIConnectionError as exc:
            raise OpenAIProviderError(
                "Could not connect to the OpenAI API. Check your network connection."
            ) from exc
        except Exception as exc:
            raise OpenAIProviderError(f"OpenAI API error: {exc}") from exc


def _load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = _PROMPTS_DIR / filename
    if not path.is_file():
        raise OpenAIProviderError(f"Prompt template not found: {path}")
    return path.read_text().strip()


# Auto-register when imported.
register_provider("openai", OpenAIProvider)
