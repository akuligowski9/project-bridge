"""Centralized input validation.

Validates all data entering the engine before any processing or API calls.
Each validator raises :class:`ValidationError` with the field name and a
human-readable description of the constraint.
"""

from __future__ import annotations

import re


class ValidationError(Exception):
    """Raised when an input value fails validation.

    Attributes:
        field: The name of the invalid field.
        constraint: A human-readable description of the violated constraint.
    """

    def __init__(self, field: str, constraint: str) -> None:
        self.field = field
        self.constraint = constraint
        super().__init__(f"{field}: {constraint}")


# GitHub username rules:
# https://github.com/shinnn/github-username-regex
# - 1–39 characters
# - Alphanumeric or hyphens
# - Cannot start or end with a hyphen
# - No consecutive hyphens
_GITHUB_USER_RE = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$")

# Matches GitHub profile URLs like https://github.com/octocat or github.com/user/
_GITHUB_URL_RE = re.compile(
    r"^(?:https?://)?github\.com/([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]?)/?$",
    re.IGNORECASE,
)

# Minimum meaningful job description length (characters).
_MIN_JOB_TEXT_LENGTH = 20

# Minimum meaningful resume length (characters).
_MIN_RESUME_TEXT_LENGTH = 20


def validate_github_username(username: str | None) -> str:
    """Validate a GitHub username and return the cleaned value.

    Raises:
        ValidationError: If the username is empty, too long, or contains
            invalid characters.
    """
    if username is None or not username.strip():
        raise ValidationError("github_user", "GitHub username is required.")

    username = username.strip()

    url_match = _GITHUB_URL_RE.match(username)
    if url_match:
        username = url_match.group(1)

    if len(username) > 39:
        raise ValidationError(
            "github_user",
            f"GitHub username must be at most 39 characters (got {len(username)}).",
        )

    if not _GITHUB_USER_RE.match(username):
        raise ValidationError(
            "github_user",
            "GitHub username must contain only alphanumeric characters or hyphens, "
            "cannot start or end with a hyphen, and cannot have consecutive hyphens.",
        )

    return username


def validate_job_text(text: str | None) -> str:
    """Validate job description text and return the cleaned value.

    Raises:
        ValidationError: If the text is empty or too short to be meaningful.
    """
    if text is None or not text.strip():
        raise ValidationError("job_text", "Job description text is required.")

    text = text.strip()

    if len(text) < _MIN_JOB_TEXT_LENGTH:
        raise ValidationError(
            "job_text",
            f"Job description is too short (minimum {_MIN_JOB_TEXT_LENGTH} characters).",
        )

    return text


def validate_resume_text(text: str | None) -> str | None:
    """Validate optional resume text and return the cleaned value.

    Returns *None* if no text was provided (resume is optional).

    Raises:
        ValidationError: If text is provided but too short to be meaningful.
    """
    if text is None or not text.strip():
        return None

    text = text.strip()

    if len(text) < _MIN_RESUME_TEXT_LENGTH:
        raise ValidationError(
            "resume_text",
            f"Resume text is too short (minimum {_MIN_RESUME_TEXT_LENGTH} characters).",
        )

    return text
