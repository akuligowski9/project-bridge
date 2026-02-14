"""Skill feature loader for project spec generation.

Loads per-skill, per-difficulty feature suggestions from skill_features.yaml.
Used by the project spec export to populate the Key Features section.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_FEATURES_FILE = Path(__file__).parent / "skill_features.yaml"

_cache: dict[str, dict[str, list[str]]] | None = None
_cache_lower: dict[str, str] | None = None


def _load() -> dict[str, dict[str, list[str]]]:
    """Load and cache features from the YAML file."""
    global _cache, _cache_lower
    if _cache is not None:
        return _cache

    if not _FEATURES_FILE.is_file():
        _cache = {}
        _cache_lower = {}
        return _cache

    raw: dict[str, Any] = yaml.safe_load(_FEATURES_FILE.read_text()) or {}
    _cache = {}
    for skill, tiers in raw.items():
        if isinstance(tiers, dict):
            _cache[skill] = {k: v for k, v in tiers.items() if isinstance(v, list)}
    _cache_lower = {k.lower(): k for k in _cache}
    return _cache


def get_skill_features(skill_name: str, difficulty: str) -> list[str]:
    """Return feature suggestions for a skill at a given difficulty.

    Args:
        skill_name: Skill name to look up (case-insensitive).
        difficulty: One of ``"beginner"``, ``"intermediate"``, or ``"advanced"``.

    Returns:
        A list of feature description strings, or an empty list if the
        skill or difficulty tier is not found.
    """
    data = _load()
    global _cache_lower
    assert _cache_lower is not None
    canonical = _cache_lower.get(skill_name.lower())
    if canonical is None:
        return []
    tiers = data.get(canonical, {})
    return list(tiers.get(difficulty, []))
