"""Resume context processor.

Optional input processor that extracts skills, experience domains, and
years of experience from plain-text resume content. Resume data is
treated as contextual enrichment only — it may influence interpretation
but must not override GitHub-derived signals.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field

from projectbridge.input.job_description import DOMAIN_KEYWORDS, TECHNOLOGY_KEYWORDS


class ResumeContext(BaseModel):
    """Normalized context extracted from resume text."""

    skills: list[str] = Field(
        description="Technologies and tools mentioned in the resume.",
    )
    experience_domains: list[str] = Field(
        description="Domains of experience (e.g. 'backend', 'cloud').",
    )
    years_of_experience: int | None = Field(
        default=None,
        description="Total years of experience, if detectable.",
    )


class ResumeParseError(Exception):
    """Raised when the resume text cannot be parsed."""


def parse_resume(text: str) -> ResumeContext:
    """Parse plain-text resume content into structured context.

    Args:
        text: Raw resume text in any common format.

    Returns:
        A :class:`ResumeContext` with extracted skills, domains,
        and years of experience.

    Raises:
        ResumeParseError: If *text* is empty or whitespace-only.
    """
    if not text or not text.strip():
        raise ResumeParseError("Resume text is empty. Provide non-empty resume content.")

    skills = _match_keywords(text, TECHNOLOGY_KEYWORDS)
    domains = _match_keywords(text, DOMAIN_KEYWORDS)
    years = _extract_years(text)

    return ResumeContext(
        skills=skills,
        experience_domains=domains,
        years_of_experience=years,
    )


def merge_resume_context(
    dev_context: dict[str, Any],
    resume: ResumeContext,
) -> dict[str, Any]:
    """Merge resume-derived data into the developer context.

    Resume skills are added as a secondary signal under
    ``resume_skills``. They do **not** replace or override
    GitHub-derived ``languages``, ``frameworks``, or
    ``infrastructure_signals``.

    Args:
        dev_context: Primary developer context from the GitHub analyzer.
        resume: Parsed resume context.

    Returns:
        The enriched developer context dict.
    """
    enriched = dict(dev_context)
    enriched["resume_skills"] = resume.skills
    enriched["resume_domains"] = resume.experience_domains
    enriched["resume_years"] = resume.years_of_experience
    return enriched


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _match_keywords(text: str, keywords: dict[str, str]) -> list[str]:
    """Match keywords in *text*, returning deduplicated canonical names."""
    found: dict[str, None] = {}
    lower = text.lower()
    for pattern, canonical in sorted(keywords.items(), key=lambda kv: len(kv[0]), reverse=True):
        if re.search(rf"\b{re.escape(pattern)}\b", lower):
            if canonical not in found:
                found[canonical] = None
    return list(found)


_YEARS_PATTERN = re.compile(
    r"(\d{1,2})\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+)?experience",
    re.IGNORECASE,
)


def _extract_years(text: str) -> int | None:
    """Extract years of experience from resume text."""
    matches = _YEARS_PATTERN.findall(text)
    if matches:
        # Return the largest number found (likely the total).
        return max(int(m) for m in matches)
    return None
