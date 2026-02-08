"""NoAI provider — heuristic fallback with no external API calls.

Fulfills the AIProvider interface using deterministic logic so the
engine always works with ``--no-ai``.
"""

from __future__ import annotations

from typing import Any

from projectbridge.ai.provider import AIProvider, register_provider


class NoAIProvider(AIProvider):
    """Heuristic-only provider that requires no API keys or network."""

    def analyze_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Return the context unchanged — no AI enrichment."""
        return context

    def generate_recommendations(self, gaps: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate heuristic recommendations from missing/adjacent skills."""
        recommendations: list[dict[str, Any]] = []

        missing = gaps.get("missing_skills", [])
        adjacent = gaps.get("adjacent_skills", [])

        # Group missing skills into batches of up to 3.
        skills_to_address = [
            _skill_name(s) for s in missing
        ] + [
            _skill_name(s) for s in adjacent
        ]

        batch: list[str] = []
        for skill in skills_to_address:
            batch.append(skill)
            if len(batch) >= 3:
                recommendations.append(_make_recommendation(batch))
                batch = []
        if batch:
            recommendations.append(_make_recommendation(batch))

        return recommendations


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _skill_name(skill: Any) -> str:
    """Extract the name string from a skill (dict or Pydantic model)."""
    if isinstance(skill, dict):
        return skill.get("name", str(skill))
    return getattr(skill, "name", str(skill))


def _make_recommendation(skills: list[str]) -> dict[str, Any]:
    """Build a single recommendation dict for a batch of skills."""
    if len(skills) == 1:
        title = f"Build a project using {skills[0]}"
        desc = (
            f"Create a small, focused project that demonstrates your ability "
            f"to work with {skills[0]}. Choose a realistic use case that "
            f"produces a deployable or shareable result for your portfolio."
        )
    else:
        joined = ", ".join(skills[:-1]) + f" and {skills[-1]}"
        title = f"Build a project using {joined}"
        desc = (
            f"Create a project that combines {joined}. Pick a realistic "
            f"scenario that lets you demonstrate each technology in context, "
            f"producing a deployable or shareable portfolio piece."
        )

    scope = "small" if len(skills) == 1 else "medium"

    return {
        "title": title,
        "description": desc,
        "skills_addressed": skills,
        "estimated_scope": scope,
    }


# Auto-register when imported.
register_provider("none", NoAIProvider)
