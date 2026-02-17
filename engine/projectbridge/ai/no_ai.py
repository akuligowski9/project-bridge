"""NoAI provider — heuristic fallback with no external API calls.

Fulfills the AIProvider interface using deterministic logic so the
engine always works with ``--no-ai``.
"""

from __future__ import annotations

from typing import Any

from projectbridge.ai.provider import AIProvider, register_provider
from projectbridge.recommend.templates import select_templates

# Generic mentor-tone context for heuristic-generated recommendations,
# keyed by SkillCategory value.
_CATEGORY_CONTEXT: dict[str, str] = {
    "language": (
        "Programming languages are the foundation of everything you build. "
        "Teams value developers who write clean, idiomatic code and understand "
        "the ecosystem — tooling, packaging, and community conventions — not "
        "just syntax."
    ),
    "framework": (
        "Frameworks encode the best practices of thousands of engineering teams. "
        "Knowing a framework well means you can ship features faster, follow "
        "established patterns, and contribute meaningfully from day one on a new team."
    ),
    "infrastructure": (
        "Infrastructure skills bridge the gap between writing code and running "
        "it in production. Engineering organizations value developers who "
        "understand deployment, scaling, and operational concerns alongside "
        "application logic."
    ),
    "tool": (
        "Developer tools and databases are the building blocks of real systems. "
        "Understanding how to choose, configure, and integrate the right tools "
        "makes you effective across projects and teams."
    ),
    "concept": (
        "Software engineering concepts — like design patterns, testing "
        "strategies, and architectural principles — transfer across every "
        "language and framework. Mastering them makes you adaptable and "
        "valuable in any engineering organization."
    ),
}


class NoAIProvider(AIProvider):
    """Heuristic-only provider that requires no API keys or network."""

    def _chat(self, system_prompt: str, user_message: str) -> str:
        """Not used — NoAI provider uses heuristic logic instead."""
        return ""

    def analyze_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Return the context unchanged — no AI enrichment."""
        return context

    def generate_recommendations(self, gaps: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate recommendations: templates first, heuristic fallback for the rest."""
        missing = gaps.get("missing_skills", [])
        adjacent = gaps.get("adjacent_skills", [])
        experience_level = gaps.get("experience_level")

        all_skills = [(_skill_name(s), _skill_category(s)) for s in missing] + [
            (_skill_name(s), _skill_category(s)) for s in adjacent
        ]
        skill_name_set = {name for name, _ in all_skills}

        # Build known skills from dev_context_summary for personalization.
        known_skills: set[str] | None = None
        summary = gaps.get("dev_context_summary", "")
        if summary and summary.startswith("Developer knows: "):
            prefix = "Developer knows: "
            chunk = summary[len(prefix) :].split(".")[0]
            known_skills = {s.strip() for s in chunk.split(",") if s.strip()}

        # 1. Try template-based recommendations first.
        matched_templates = select_templates(skill_name_set, experience_level=experience_level)
        recommendations: list[dict[str, Any]] = list(matched_templates)

        # 2. Find skills not covered by any template.
        covered: set[str] = set()
        for tpl in matched_templates:
            covered.update(s.lower() for s in tpl.get("skills_addressed", []))

        uncovered = [(name, cat) for name, cat in all_skills if name.lower() not in covered]

        # 3. Generate heuristic recommendations for uncovered skills.
        batch: list[str] = []
        batch_categories: list[str] = []
        for name, cat in uncovered:
            batch.append(name)
            batch_categories.append(cat)
            if len(batch) >= 3:
                recommendations.append(
                    _make_recommendation(
                        batch, _pick_category(batch_categories), known_skills=known_skills
                    )
                )
                batch = []
                batch_categories = []
        if batch:
            recommendations.append(
                _make_recommendation(
                    batch, _pick_category(batch_categories), known_skills=known_skills
                )
            )

        return recommendations


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _skill_name(skill: Any) -> str:
    """Extract the name string from a skill (dict or Pydantic model)."""
    if isinstance(skill, dict):
        return skill.get("name", str(skill))
    return getattr(skill, "name", str(skill))


def _skill_category(skill: Any) -> str:
    """Extract the category string from a skill (dict or Pydantic model)."""
    if isinstance(skill, dict):
        return skill.get("category", "concept")
    cat = getattr(skill, "category", "concept")
    # Handle enum values
    return getattr(cat, "value", str(cat)) if cat else "concept"


def _pick_category(categories: list[str]) -> str:
    """Pick the most common category from a batch, defaulting to 'concept'."""
    if not categories:
        return "concept"
    from collections import Counter

    return Counter(categories).most_common(1)[0][0]


def _make_recommendation(
    skills: list[str],
    category: str = "concept",
    known_skills: set[str] | None = None,
) -> dict[str, Any]:
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

    # Personalization: mention what the developer already knows.
    if known_skills:
        skill_lower = {s.lower() for s in skills}
        known_lower = {k.lower(): k for k in known_skills}
        overlap = [known_lower[s] for s in skill_lower if s in known_lower]
        new = [s for s in skills if s.lower() not in known_lower]
        if overlap and new:
            desc += (
                f" Your experience with {', '.join(overlap)} gives you a "
                f"head start — focus on {', '.join(new)} specifically."
            )

    scope = "small" if len(skills) == 1 else "medium"

    return {
        "title": title,
        "description": desc,
        "skills_addressed": skills,
        "estimated_scope": scope,
        "skill_context": _CATEGORY_CONTEXT.get(category, _CATEGORY_CONTEXT["concept"]),
    }


# Auto-register when imported.
register_provider("none", NoAIProvider)
