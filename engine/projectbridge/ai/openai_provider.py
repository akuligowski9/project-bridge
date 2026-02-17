"""OpenAI AI provider — uses the OpenAI API for context analysis and recommendations.

Prompts are loaded from editable template files in the ``prompts/`` directory.
"""

from __future__ import annotations

import os
from typing import Any

from projectbridge.ai.provider import AIProvider, AIProviderError, register_provider


class OpenAIProviderError(AIProviderError):
    """Raised when the OpenAI provider encounters an error."""


class OpenAIProvider(AIProvider):
    """AI provider backed by the OpenAI API.

    Args:
        api_key: OpenAI API key. If *None*, reads from the
            ``OPENAI_API_KEY`` environment variable.
        model: Model identifier to use (default: ``gpt-4o``).
    """

    _error_class = OpenAIProviderError

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

    def _chat(self, system_prompt: str, user_message: str) -> str:
        """Send a chat completion request and return the response text."""
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


# Auto-register when imported.
register_provider("openai", OpenAIProvider)
