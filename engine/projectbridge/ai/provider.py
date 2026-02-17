"""AI provider base interface and registry.

AI functionality is abstracted behind a provider interface so the engine
can operate with different backends (OpenAI, Anthropic, Ollama) or with
no AI at all (``--no-ai``).
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

_PROMPTS_DIR = Path(__file__).parent / "prompts"


class AIProviderError(Exception):
    """Base error for AI provider operations."""


class AIProvider(ABC):
    """Abstract base class for AI providers.

    Concrete providers must implement :meth:`_chat`. The shared
    :meth:`analyze_context` and :meth:`generate_recommendations` methods
    handle prompt loading, JSON parsing, and fallback logic.
    """

    # Subclasses should set this to their own error class for branded messages.
    _error_class: type[AIProviderError] = AIProviderError

    @abstractmethod
    def _chat(self, system_prompt: str, user_message: str) -> str:
        """Send a message to the AI backend and return the response text.

        Args:
            system_prompt: System-level instruction for the model.
            user_message: The user's input message.

        Returns:
            The model's response as a string.
        """

    def analyze_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Enhance or interpret a developer context using AI.

        Loads the ``analyze_context.txt`` prompt, sends the context as JSON,
        and merges the AI response back into the original context (never
        losing original fields).
        """
        system_prompt = load_prompt("analyze_context.txt")
        user_message = json.dumps(context, indent=2, default=str)

        response_text = self._chat(system_prompt, user_message)

        try:
            enriched = json.loads(response_text)
        except json.JSONDecodeError:
            # If the model returns non-JSON, preserve original context.
            enriched = {**context}

        # Ensure original fields are never lost.
        for key, value in context.items():
            if key not in enriched:
                enriched[key] = value

        return enriched

    def generate_recommendations(self, gaps: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate project recommendations from skill gaps.

        Loads the ``generate_recommendations.txt`` prompt, sends the gaps as
        JSON, and unwraps the response (handles both ``{"recommendations": [...]}``
        and raw ``[...]`` formats).
        """
        system_prompt = load_prompt("generate_recommendations.txt")
        user_message = json.dumps(gaps, indent=2, default=str)

        response_text = self._chat(system_prompt, user_message)

        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            raise self._error_class(
                f"{self.__class__.__name__} returned an invalid JSON response for recommendations."
            )

        # The prompt asks for {"recommendations": [...]}.
        if isinstance(parsed, dict):
            return parsed.get("recommendations", [])
        if isinstance(parsed, list):
            return parsed

        raise self._error_class(
            f"{self.__class__.__name__} returned an unexpected response format "
            "for recommendations."
        )


def load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    path = _PROMPTS_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text().strip()


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, type[AIProvider]] = {}


def register_provider(name: str, cls: type[AIProvider]) -> None:
    """Register an AI provider class under *name*."""
    _REGISTRY[name] = cls


def get_provider(name: str, **kwargs: Any) -> AIProvider:
    """Instantiate and return the provider registered under *name*.

    Args:
        name: Provider identifier (e.g. ``"none"``, ``"openai"``).
        **kwargs: Forwarded to the provider constructor.

    Raises:
        ValueError: If *name* is not a registered provider.
    """
    cls = _REGISTRY.get(name)
    if cls is None:
        available = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise ValueError(f"Unknown AI provider '{name}'. Available providers: {available}")
    return cls(**kwargs)
