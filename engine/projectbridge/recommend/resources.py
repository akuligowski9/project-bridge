"""Documentation resource link loader.

Loads curated official documentation links from resources.yaml.
Used by the project spec export to provide clickable learning resources.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_RESOURCES_FILE = Path(__file__).parent / "resources.yaml"

_cache: dict[str, list[dict[str, str]]] | None = None
_cache_lower: dict[str, str] | None = None


def _load() -> dict[str, list[dict[str, str]]]:
    """Load and cache resources from the YAML file."""
    global _cache, _cache_lower
    if _cache is not None:
        return _cache

    if not _RESOURCES_FILE.is_file():
        _cache = {}
        _cache_lower = {}
        return _cache

    raw: dict[str, Any] = yaml.safe_load(_RESOURCES_FILE.read_text()) or {}
    _cache = {k: v for k, v in raw.items() if isinstance(v, list)}
    _cache_lower = {k.lower(): k for k in _cache}
    return _cache


def get_doc_links(skill_name: str) -> list[dict[str, str]]:
    """Return documentation links for a skill (case-insensitive).

    Args:
        skill_name: Skill name to look up.

    Returns:
        A list of ``{"label": ..., "url": ...}`` dicts, or an empty list
        if the skill is not found.
    """
    data = _load()
    global _cache_lower
    assert _cache_lower is not None
    canonical = _cache_lower.get(skill_name.lower())
    if canonical is None:
        return []
    return data.get(canonical, [])
