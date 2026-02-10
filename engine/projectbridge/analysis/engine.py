"""Core analysis layer.

Compares GitHub-derived developer context against job requirements to
produce detected_skills, adjacent_skills, and missing_skills. This layer
is deterministic — AI is restricted to later interpretation and
recommendation stages.
"""

from __future__ import annotations

from typing import Any

from projectbridge.analysis.taxonomy import TAXONOMY, get_adjacent, get_category
from projectbridge.schema import Skill, SkillCategory


def _normalize(name: str) -> str:
    """Lowercase key used for case-insensitive matching."""
    return name.strip().lower()


def _build_lookup() -> dict[str, str]:
    """Map lowercased skill names to their canonical form."""
    return {_normalize(k): k for k in TAXONOMY}


_CANONICAL = _build_lookup()


def _canonicalize(name: str) -> str:
    """Return the canonical taxonomy name, or the original if unknown."""
    return _CANONICAL.get(_normalize(name), name)


def _skill_obj(name: str) -> Skill:
    """Create a :class:`Skill` from a name, using the taxonomy category."""
    cat = get_category(name)
    if cat is None:
        cat = SkillCategory.CONCEPT
    return Skill(name=name, category=cat)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze(
    developer_context: dict[str, Any],
    job_requirements: dict[str, Any],
) -> dict[str, list[Skill]]:
    """Compare developer context against job requirements.

    Args:
        developer_context: Output of :func:`GitHubAnalyzer.analyze` —
            must contain ``languages``, ``frameworks``, and
            ``infrastructure_signals`` lists of dicts with a ``"name"`` key.
        job_requirements: Output of :func:`parse_job_description` (or
            ``JobRequirements.model_dump()``) — must contain
            ``required_technologies`` list of strings.

    Returns:
        A dict with three lists of :class:`Skill`:

        - **detected_skills** — present in both context and requirements.
        - **adjacent_skills** — related to detected skills but not yet
          demonstrated, and relevant to the job requirements.
        - **missing_skills** — required by the job but absent from the
          developer context and not adjacent to anything detected.
    """
    # -- Collect developer skills ------------------------------------------
    dev_skills: set[str] = set()
    for group in ("languages", "frameworks", "infrastructure_signals"):
        for item in developer_context.get(group, []):
            dev_skills.add(_canonicalize(item["name"]))
    # project_structures are structural signals, not skills — skip them.

    # Resume skills are secondary — they enrich but don't override.
    for skill_name in developer_context.get("resume_skills", []):
        dev_skills.add(_canonicalize(skill_name))

    # -- Collect required skills -------------------------------------------
    required: set[str] = set()
    for tech in job_requirements.get("required_technologies", []):
        required.add(_canonicalize(tech))

    # -- Detected: intersection of dev skills and requirements -------------
    detected_names = sorted(dev_skills & required)

    # -- Adjacent: skills adjacent to detected ones that are also required -
    #    but not already in the developer's skill set.
    adjacent_pool: set[str] = set()
    for skill in dev_skills:
        for adj in get_adjacent(skill):
            adj_canon = _canonicalize(adj)
            if adj_canon not in dev_skills:
                adjacent_pool.add(adj_canon)

    # Only keep adjacents that are relevant to the job requirements.
    adjacent_names = sorted(adjacent_pool & required)

    # -- Missing: required but neither detected nor adjacent ---------------
    accounted = dev_skills | adjacent_pool
    missing_names = sorted(required - accounted)

    return {
        "detected_skills": [_skill_obj(n) for n in detected_names],
        "adjacent_skills": [_skill_obj(n) for n in adjacent_names],
        "missing_skills": [_skill_obj(n) for n in missing_names],
    }
