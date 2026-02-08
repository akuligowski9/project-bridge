"""Recommendation engine.

Converts detected skill gaps into small, realistic project suggestions.
Uses an AI provider when configured, otherwise falls back to heuristics.
"""

from __future__ import annotations

from typing import Any

from projectbridge.ai.provider import AIProvider
from projectbridge.schema import Recommendation, EstimatedScope, Skill


def generate_recommendations(
    analysis: dict[str, list[Skill]],
    provider: AIProvider,
    max_recommendations: int = 5,
) -> list[Recommendation]:
    """Produce project recommendations from analysis results.

    Args:
        analysis: Dict with ``missing_skills``, ``adjacent_skills``,
            and ``detected_skills`` lists of :class:`Skill`.
        provider: The active AI provider (may be :class:`NoAIProvider`).
        max_recommendations: Cap on recommendations returned.

    Returns:
        A list of :class:`Recommendation` conforming to the output schema.
    """
    gaps = {
        "missing_skills": [s.model_dump() for s in analysis.get("missing_skills", [])],
        "adjacent_skills": [s.model_dump() for s in analysis.get("adjacent_skills", [])],
    }

    raw = provider.generate_recommendations(gaps)

    recommendations: list[Recommendation] = []
    for item in raw[:max_recommendations]:
        # Enforce the max-3 skills constraint.
        skills = item.get("skills_addressed", [])[:3]
        scope_raw = item.get("estimated_scope", "medium")
        try:
            scope = EstimatedScope(scope_raw)
        except ValueError:
            scope = EstimatedScope.MEDIUM

        recommendations.append(
            Recommendation(
                title=item["title"],
                description=item["description"],
                skills_addressed=skills,
                estimated_scope=scope,
            )
        )

    return recommendations
