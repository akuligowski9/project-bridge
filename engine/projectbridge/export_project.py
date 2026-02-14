"""Project spec generation.

Generates a rich, exportable project specification from a single
recommendation. Supports both heuristic (NoAI) and AI-powered generation.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from projectbridge.ai.provider import AIProvider
from projectbridge.recommend.resources import get_doc_links
from projectbridge.recommend.skill_features import get_skill_features
from projectbridge.schema import (
    AnalysisResult,
    DifficultyTier,
    DocLink,
    ProjectSpec,
    Recommendation,
)

logger = logging.getLogger(__name__)

_PROMPT_FILE = Path(__file__).parent / "ai" / "prompts" / "generate_project_spec.txt"

# Target feature counts per difficulty tier.
_FEATURE_TARGETS: dict[str, int] = {
    "beginner": 3,
    "intermediate": 5,
    "advanced": 8,
}

# Generic fallback features when a skill isn't in skill_features.yaml.
_GENERIC_FEATURES: dict[str, list[str]] = {
    "beginner": [
        "Set up the project structure with proper configuration and dependencies",
        "Implement the core functionality with clean, readable code",
        "Add basic tests and documentation for the main features",
    ],
    "intermediate": [
        "Implement the core functionality with proper error handling and validation",
        "Add integration tests and automated quality checks",
        "Build a clean API or interface with documentation",
        "Add configuration management with environment-specific settings",
        "Implement structured logging and meaningful error messages",
    ],
    "advanced": [
        "Implement a production-grade architecture with proper separation of concerns",
        "Add comprehensive testing including edge cases and performance benchmarks",
        "Build monitoring, logging, and graceful error recovery",
        "Implement proper error handling with custom error types and recovery",
        "Add configuration management with validation and environment overrides",
        "Build a CI pipeline with linting, testing, and code quality checks",
        "Implement API documentation with examples and usage guides",
        "Add security hardening with input validation and access controls",
    ],
}


def generate_project_spec(
    recommendation: Recommendation,
    difficulty: str,
    analysis_result: AnalysisResult,
    provider: AIProvider,
) -> ProjectSpec:
    """Generate a rich project spec from a recommendation.

    Args:
        recommendation: The recommendation to expand.
        difficulty: One of ``"beginner"``, ``"intermediate"``, ``"advanced"``.
        analysis_result: The full analysis result for personalization context.
        provider: The AI provider (use NoAI for heuristic generation).

    Returns:
        A :class:`ProjectSpec` with description, features, career context,
        and documentation links.
    """
    difficulty_tier = DifficultyTier(difficulty)
    strengths = [s.name for s in analysis_result.strengths]

    # Doc links are always curated, never AI-generated.
    doc_links = _collect_doc_links(recommendation.skills_addressed)

    # Determine if we should use AI.
    from projectbridge.ai.no_ai import NoAIProvider

    if isinstance(provider, NoAIProvider):
        return _generate_heuristic(
            recommendation, difficulty_tier, analysis_result, strengths, doc_links
        )

    return _generate_with_ai(
        recommendation, difficulty_tier, analysis_result, strengths, doc_links, provider
    )


def _collect_doc_links(skills: list[str]) -> list[DocLink]:
    """Gather documentation links for all skills addressed."""
    links: list[DocLink] = []
    for skill in skills:
        for entry in get_doc_links(skill):
            links.append(DocLink(label=entry["label"], url=entry["url"], skill=skill))
    return links


# ---------------------------------------------------------------------------
# Heuristic (NoAI) path
# ---------------------------------------------------------------------------


def _generate_heuristic(
    rec: Recommendation,
    difficulty: DifficultyTier,
    result: AnalysisResult,
    strengths: list[str],
    doc_links: list[DocLink],
) -> ProjectSpec:
    """Build a project spec using heuristic logic (no AI calls)."""
    description = _build_heuristic_description(rec, difficulty, strengths)
    features = _collect_features(rec.skills_addressed, difficulty.value)
    why_skills_matter = rec.skill_context or ""

    # Identify which strengths are actually referenced in the description.
    desc_lower = description.lower()
    referenced = [s for s in strengths if s.lower() in desc_lower]

    return ProjectSpec(
        title=rec.title,
        difficulty=difficulty,
        description=description,
        features=features,
        skills_addressed=list(rec.skills_addressed),
        why_skills_matter=why_skills_matter,
        doc_links=doc_links,
        strengths_referenced=referenced,
    )


def _build_heuristic_description(
    rec: Recommendation,
    difficulty: DifficultyTier,
    strengths: list[str],
) -> str:
    """Build a multi-paragraph description from the recommendation.

    Paragraph count scales with difficulty:
    - Beginner: 2 paragraphs (scope + personalization)
    - Intermediate: 3 paragraphs (scope + personalization + technical approach)
    - Advanced: 4 paragraphs (scope + personalization + architecture + mastery)
    """
    skills_str = ", ".join(rec.skills_addressed)
    known_lower = {k.lower() for k in strengths}
    new_skills = [s for s in rec.skills_addressed if s.lower() not in known_lower]
    skills_lower = {s.lower() for s in rec.skills_addressed}
    known_overlap = [s for s in strengths if s.lower() in skills_lower]

    # -- P1: Scope framing (always present) --
    scope_context = {
        DifficultyTier.BEGINNER: (
            "This project is scoped for someone getting started with these technologies. "
            "Focus on understanding the fundamentals — how the pieces fit together, "
            "basic configuration, and getting a working result you can demonstrate."
        ),
        DifficultyTier.INTERMEDIATE: (
            "This project assumes foundational knowledge and pushes into real-world "
            "patterns. You'll work with production-relevant features like "
            "authentication, data relationships, and proper error handling."
        ),
        DifficultyTier.ADVANCED: (
            "This project targets experienced developers ready for production-grade "
            "challenges. Expect to work with architectural patterns, performance "
            "optimization, and operational concerns that teams face at scale."
        ),
    }
    p1 = f"{rec.description} {scope_context[difficulty]}"

    # -- P2: Personalization (always present) --
    if known_overlap and new_skills:
        p2 = (
            f"Your experience with {', '.join(known_overlap)} gives you a solid "
            f"foundation here. Focus your learning energy on "
            f"{', '.join(new_skills)} — the concepts will click faster because "
            f"you already understand the broader ecosystem."
        )
    elif new_skills:
        strength_names = ", ".join(strengths[:3]) if strengths else "your existing experience"
        p2 = (
            f"While {', '.join(new_skills)} may be new territory, your background "
            f"with {strength_names} means you already think like a developer. "
            f"Apply the same patterns — start small, iterate, and build on what works."
        )
    else:
        p2 = (
            "You already have exposure to these technologies. This project is an "
            "opportunity to deepen that knowledge and produce a polished portfolio "
            "piece that demonstrates mastery, not just familiarity."
        )

    paragraphs = [p1, p2]

    # -- P3: Technical approach (intermediate + advanced) --
    if difficulty in (DifficultyTier.INTERMEDIATE, DifficultyTier.ADVANCED):
        p3_context = {
            DifficultyTier.INTERMEDIATE: (
                f"At this level, hiring managers expect to see more than a tutorial "
                f"follow-along. Structure your {skills_str} project with clear "
                f"separation between layers — data access, business logic, and "
                f"presentation. Add input validation that handles real edge cases, "
                f"write tests that verify behavior (not just coverage), and include "
                f"a README that explains your design decisions. These details signal "
                f"that you can ship features a team can maintain."
            ),
            DifficultyTier.ADVANCED: (
                f"Engineering teams evaluating senior candidates look for evidence "
                f"of systems thinking. Your {skills_str} project should demonstrate "
                f"clear architectural boundaries, explicit trade-off decisions, and "
                f"operational awareness. Think about failure modes — what happens "
                f"when a dependency is down, when input volume spikes, or when "
                f"configuration is missing? Build in graceful degradation, structured "
                f"logging, and health checks that make the system observable."
            ),
        }
        paragraphs.append(p3_context[difficulty])

    # -- P4: Mastery / production depth (advanced only) --
    if difficulty == DifficultyTier.ADVANCED:
        p4 = (
            "The difference between a portfolio project and a production system is "
            "in the details most developers skip: database migrations that handle "
            "rollbacks, CI pipelines that catch regressions before merge, security "
            "headers and rate limiting, and documentation that helps the next "
            "developer understand not just what the code does but why it's "
            "structured that way. Completing this project at an advanced level "
            "demonstrates the kind of ownership and foresight that distinguishes "
            "senior engineers."
        )
        paragraphs.append(p4)

    return "\n\n".join(paragraphs)


def _collect_features(skills: list[str], difficulty: str) -> list[str]:
    """Collect features for all skills at the given difficulty, with fallback.

    Target feature counts: beginner=3, intermediate=5, advanced=8.
    """
    target = _FEATURE_TARGETS.get(difficulty, 3)
    features: list[str] = []
    for skill in skills:
        skill_features = get_skill_features(skill, difficulty)
        if skill_features:
            features.extend(skill_features)
        elif not features:
            # Only use generic fallback if we have nothing yet.
            features.extend(_GENERIC_FEATURES.get(difficulty, _GENERIC_FEATURES["intermediate"]))
    # Pad with generic fallback if under minimum of 3.
    if len(features) < 3:
        generic = _GENERIC_FEATURES.get(difficulty, _GENERIC_FEATURES["intermediate"])
        for f in generic:
            if f not in features:
                features.append(f)
            if len(features) >= 3:
                break
    # Cap at the target count for the tier.
    return features[:target]


# ---------------------------------------------------------------------------
# AI path
# ---------------------------------------------------------------------------


def _generate_with_ai(
    rec: Recommendation,
    difficulty: DifficultyTier,
    result: AnalysisResult,
    strengths: list[str],
    doc_links: list[DocLink],
    provider: AIProvider,
) -> ProjectSpec:
    """Build a project spec using an AI provider."""
    prompt_template = ""
    if _PROMPT_FILE.is_file():
        prompt_template = _PROMPT_FILE.read_text()

    gap_names = [g.name for g in result.gaps]
    user_message = (
        f"{prompt_template}\n\n"
        f"Recommendation:\n"
        f"  Title: {rec.title}\n"
        f"  Description: {rec.description}\n"
        f"  Skills addressed: {', '.join(rec.skills_addressed)}\n"
        f"  Skill context: {rec.skill_context or 'N/A'}\n\n"
        f"Difficulty: {difficulty.value}\n\n"
        f"Developer strengths: {', '.join(strengths) if strengths else 'None provided'}\n"
        f"Developer gaps: {', '.join(gap_names) if gap_names else 'None provided'}\n"
    )

    try:
        raw = provider.analyze_context({"prompt_override": user_message})
        ai_text = raw.get("response", "")
        ai_data: dict[str, Any] = json.loads(ai_text)
    except Exception:
        logger.warning("AI generation failed, falling back to heuristic", exc_info=True)
        return _generate_heuristic(rec, difficulty, result, strengths, doc_links)

    description = ai_data.get("description", "")
    features = ai_data.get("features", [])
    why_skills_matter = ai_data.get("why_skills_matter", rec.skill_context or "")

    # Validate minimum requirements, fall back if insufficient.
    if not description or len(features) < 3:
        logger.warning("AI response insufficient, falling back to heuristic")
        return _generate_heuristic(rec, difficulty, result, strengths, doc_links)

    desc_lower = description.lower()
    referenced = [s for s in strengths if s.lower() in desc_lower]

    return ProjectSpec(
        title=rec.title,
        difficulty=difficulty,
        description=description,
        features=features,
        skills_addressed=list(rec.skills_addressed),
        why_skills_matter=why_skills_matter,
        doc_links=doc_links,
        strengths_referenced=referenced,
    )
