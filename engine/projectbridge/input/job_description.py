"""Job description parser.

Extracts structured requirements from raw job description text:
required technologies, implied experience domains, and architectural
expectations. Handles bullet-list, prose-paragraph, and mixed formats.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from projectbridge.input.keywords import (
    ARCHITECTURE_KEYWORDS,
    DOMAIN_KEYWORDS,
    TECHNOLOGY_KEYWORDS,
    match_keywords,
)

# ---------------------------------------------------------------------------
# Output model
# ---------------------------------------------------------------------------


class JobRequirements(BaseModel):
    """Normalized requirements extracted from a job description.

    Consumed by the analysis layer for gap detection.
    """

    required_technologies: list[str] = Field(
        description="Technologies, languages, and frameworks explicitly required.",
    )
    experience_domains: list[str] = Field(
        description="Implied domains of experience (e.g. 'frontend', 'cloud').",
    )
    architectural_expectations: list[str] = Field(
        description="Architectural patterns or practices expected (e.g. 'microservices', 'CI/CD').",  # noqa: E501
    )


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class JobDescriptionError(Exception):
    """Base exception for the job description parser."""


class EmptyJobDescriptionError(JobDescriptionError):
    """Raised when the job description is empty or whitespace-only."""


class NonTechnicalJobError(JobDescriptionError):
    """Raised when the job description does not appear to be for a technical role."""


# ---------------------------------------------------------------------------
# Technical role indicators — used for non-technical JD rejection
# ---------------------------------------------------------------------------

_TECHNICAL_ROLE_INDICATORS: set[str] = {
    "software",
    "developer",
    "engineer",
    "engineering",
    "devops",
    "data scientist",
    "data engineer",
    "architect",
    "sre",
    "site reliability",
    "backend",
    "frontend",
    "front-end",
    "back-end",
    "full-stack",
    "fullstack",
    "full stack",
    "machine learning",
    "cloud",
    "security engineer",
    "dba",
    "database administrator",
    "technical lead",
    "tech lead",
    "platform",
    "infrastructure",
    "programmer",
    "qa engineer",
    "test engineer",
    "embedded",
    "firmware",
}


def parse_job_description(text: str) -> JobRequirements:
    """Parse a plain-text job description into structured requirements.

    Args:
        text: Raw job description text in any common format
            (bullet lists, paragraphs, or mixed).

    Returns:
        A :class:`JobRequirements` with extracted technologies, domains,
        and architectural expectations.

    Raises:
        EmptyJobDescriptionError: If *text* is empty or whitespace-only.
    """
    if not text or not text.strip():
        raise EmptyJobDescriptionError(
            "Job description is empty. Provide a non-empty job description."
        )

    return JobRequirements(
        required_technologies=match_keywords(text, TECHNOLOGY_KEYWORDS),
        experience_domains=match_keywords(text, DOMAIN_KEYWORDS),
        architectural_expectations=match_keywords(text, ARCHITECTURE_KEYWORDS),
    )


def validate_technical_content(text: str, job_reqs: JobRequirements) -> None:
    """Validate that a job description is for a technical role.

    Args:
        text: Raw job description text.
        job_reqs: Already-parsed :class:`JobRequirements`.

    Raises:
        NonTechnicalJobError: If no technical signals are detected.
    """
    if job_reqs.required_technologies:
        return

    lower = text.lower()
    for indicator in _TECHNICAL_ROLE_INDICATORS:
        if indicator in lower:
            return

    raise NonTechnicalJobError(
        "No technical skills detected in this job description. "
        "ProjectBridge analyzes technical roles — software engineers, "
        "architects, data scientists, DevOps engineers, and similar positions."
    )
