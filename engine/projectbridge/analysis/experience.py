"""Experience level inference.

Estimates a developer's experience level from their context data
to calibrate recommendation difficulty.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class ExperienceLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"


def infer_experience_level(dev_context: dict[str, Any]) -> ExperienceLevel:
    """Infer an experience level from a developer context dict.

    Heuristic based on:
    - Count of unique skills across languages, frameworks, infrastructure
    - Resume years of experience if present

    Args:
        dev_context: Developer context from GitHub analyzer / resume merge.

    Returns:
        An :class:`ExperienceLevel` value.
    """
    skill_count = 0
    for group in ("languages", "frameworks", "infrastructure_signals"):
        skill_count += len(dev_context.get(group, []))
    skill_count += len(dev_context.get("resume_skills", []))

    years = dev_context.get("resume_years")

    # Years take precedence when available.
    if years is not None:
        if years >= 7:
            return ExperienceLevel.SENIOR
        if years < 2:
            return ExperienceLevel.JUNIOR

    # Skill count heuristic.
    if skill_count > 12:
        return ExperienceLevel.SENIOR
    if skill_count < 5:
        return ExperienceLevel.JUNIOR

    return ExperienceLevel.MID
