"""Google Gemini AI provider — uses the Gemini API for context analysis and recommendations.

Prompts are loaded from editable template files in the ``prompts/`` directory
(shared with other providers).
"""

from __future__ import annotations

import os
from typing import Any

from projectbridge.ai.provider import AIProvider, AIProviderError, register_provider


class GeminiProviderError(AIProviderError):
    """Raised when the Gemini provider encounters an error."""


class GeminiProvider(AIProvider):
    """AI provider backed by the Google Gemini API.

    Args:
        api_key: Google API key. If *None*, reads from the
            ``GOOGLE_API_KEY`` environment variable.
        model: Model identifier to use (default: ``gemini-2.0-flash``).
    """

    _error_class = GeminiProviderError

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.0-flash",
    ) -> None:
        self._api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self._api_key:
            raise GeminiProviderError(
                "Google API key not found. Set the GOOGLE_API_KEY environment "
                "variable or pass api_key to the provider."
            )
        self._model = model
        self._client = self._create_client()

    def _create_client(self) -> Any:
        """Create and return a Gemini client instance."""
        try:
            from google import genai
        except ImportError:
            raise GeminiProviderError(
                "The 'google-genai' package is required for the Gemini provider. "
                "Install it with: pip install google-genai"
            )
        return genai.Client(api_key=self._api_key)

    def _chat(self, system_prompt: str, user_message: str) -> str:
        """Send a generate_content request and return the response text."""
        try:
            from google.genai import errors, types
        except ImportError:
            raise GeminiProviderError("The 'google-genai' package is not installed.")

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=4096,
                    temperature=0.7,
                ),
            )
            return response.text or ""
        except errors.APIError as exc:
            if exc.code == 401:
                raise GeminiProviderError(
                    "Invalid Google API key. Check your GOOGLE_API_KEY."
                ) from exc
            if exc.code == 429:
                raise GeminiProviderError(
                    "Gemini API rate limit exceeded. Please wait and try again."
                ) from exc
            raise GeminiProviderError(f"Gemini API error: {exc}") from exc
        except Exception as exc:
            raise GeminiProviderError(f"Gemini API error: {exc}") from exc


# Auto-register when imported.
register_provider("gemini", GeminiProvider)
