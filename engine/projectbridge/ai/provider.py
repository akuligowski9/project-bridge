"""AI provider base interface and registry.

AI functionality is abstracted behind a provider interface so the engine
can operate with different backends (OpenAI, Anthropic, Ollama) or with
no AI at all (``--no-ai``).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Abstract base class for AI providers.

    Concrete providers must implement :meth:`analyze_context` and
    :meth:`generate_recommendations`. AI is restricted to interpretation
    and recommendation — it must not perform repository parsing or core
    analysis logic.
    """

    @abstractmethod
    def analyze_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Enhance or interpret a developer context using AI.

        Args:
            context: Developer context produced by the analysis layer.

        Returns:
            An enriched context dict (may add or refine fields).
        """

    @abstractmethod
    def generate_recommendations(self, gaps: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate project recommendations from skill gaps.

        Args:
            gaps: Dict containing ``missing_skills`` and optionally
                ``adjacent_skills`` from the analysis layer.

        Returns:
            A list of recommendation dicts, each with ``title``,
            ``description``, ``skills_addressed``, and
            ``estimated_scope``.
        """


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
        raise ValueError(
            f"Unknown AI provider '{name}'. Available providers: {available}"
        )
    return cls(**kwargs)
