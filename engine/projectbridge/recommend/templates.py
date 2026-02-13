"""Recommendation template loader.

Loads pre-written project recommendations from the YAML templates file.
Templates are selected based on skill overlap with gap analysis results.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_TEMPLATES_FILE = Path(__file__).parent / "templates.yaml"

_cache: list[dict[str, Any]] | None = None


def load_templates() -> list[dict[str, Any]]:
    """Load and cache recommendation templates from the YAML file."""
    global _cache
    if _cache is not None:
        return _cache

    if not _TEMPLATES_FILE.is_file():
        _cache = []
        return _cache

    raw = yaml.safe_load(_TEMPLATES_FILE.read_text()) or []
    _cache = raw
    return _cache


_DIFFICULTY_PREFERENCE: dict[str, list[str]] = {
    "junior": ["beginner", "intermediate"],
    "mid": ["intermediate", "beginner", "advanced"],
    "senior": ["advanced", "intermediate"],
}


def select_templates(
    gap_skill_names: set[str],
    max_results: int = 5,
    experience_level: str | None = None,
) -> list[dict[str, Any]]:
    """Select templates whose skills_addressed overlap with the gap skills.

    Templates are ranked by the number of overlapping skills (descending).
    When *experience_level* is provided, a small bonus is applied to
    templates whose difficulty aligns with the developer's level.

    Args:
        gap_skill_names: Set of skill names from the gap analysis (lowercased).
        max_results: Maximum number of templates to return.
        experience_level: Optional ``"junior"``, ``"mid"``, or ``"senior"``.

    Returns:
        A list of matching template dicts, highest overlap first.
    """
    templates = load_templates()
    gap_lower = {s.lower() for s in gap_skill_names}

    preferred: list[str] = []
    if experience_level:
        preferred = _DIFFICULTY_PREFERENCE.get(experience_level, [])

    scored: list[tuple[float, dict[str, Any]]] = []
    for tpl in templates:
        tpl_skills = {s.lower() for s in tpl.get("skills_addressed", [])}
        overlap = len(tpl_skills & gap_lower)
        if overlap > 0:
            bonus = 0.0
            if preferred and tpl.get("difficulty") in preferred:
                # First preferred difficulty gets higher bonus.
                bonus = 0.5 if tpl["difficulty"] == preferred[0] else 0.25
            scored.append((overlap + bonus, tpl))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [tpl for _, tpl in scored[:max_results]]
