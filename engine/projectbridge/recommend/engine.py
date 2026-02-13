"""Recommendation engine.

Converts detected skill gaps into small, realistic project suggestions.
Uses an AI provider when configured, otherwise falls back to heuristics.
"""

from __future__ import annotations

from projectbridge.ai.provider import AIProvider
from projectbridge.schema import EstimatedScope, Recommendation, Skill


def generate_recommendations(
    analysis: dict[str, list[Skill]],
    provider: AIProvider,
    max_recommendations: int = 5,
    experience_level: str | None = None,
    dev_context: dict | None = None,
) -> list[Recommendation]:
    """Produce project recommendations from analysis results.

    Args:
        analysis: Dict with ``missing_skills``, ``adjacent_skills``,
            and ``detected_skills`` lists of :class:`Skill`.
        provider: The active AI provider (may be :class:`NoAIProvider`).
        max_recommendations: Cap on recommendations returned.
        experience_level: Optional ``"junior"``, ``"mid"``, or ``"senior"``.
        dev_context: Optional developer context for personalization.

    Returns:
        A list of :class:`Recommendation` conforming to the output schema.
    """
    gaps: dict = {
        "missing_skills": [s.model_dump() for s in analysis.get("missing_skills", [])],
        "adjacent_skills": [s.model_dump() for s in analysis.get("adjacent_skills", [])],
    }
    if experience_level:
        gaps["experience_level"] = experience_level
    if dev_context:
        known: list[str] = []
        for group in ("languages", "frameworks", "infrastructure_signals"):
            for item in dev_context.get(group, []):
                known.append(item["name"])
        known.extend(dev_context.get("resume_skills", []))
        top_lang = None
        langs = dev_context.get("languages", [])
        if langs:
            top_lang = max(langs, key=lambda x: x.get("percentage", 0))["name"]
        summary = f"Developer knows: {', '.join(known)}."
        if top_lang:
            summary += f" Strongest language: {top_lang}."
        gaps["dev_context_summary"] = summary

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
                skill_context=item.get("skill_context"),
            )
        )

    return recommendations
