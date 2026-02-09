"""Tests for projectbridge.input.validation."""

import pytest

from projectbridge.input.validation import (
    ValidationError,
    validate_github_username,
    validate_job_text,
    validate_resume_text,
)


class TestValidateGitHubUsername:
    def test_valid_username(self):
        assert validate_github_username("octocat") == "octocat"

    def test_strips_whitespace(self):
        assert validate_github_username("  octocat  ") == "octocat"

    def test_single_char(self):
        assert validate_github_username("a") == "a"

    def test_alphanumeric_with_hyphens(self):
        assert validate_github_username("my-user-1") == "my-user-1"

    def test_none_raises(self):
        with pytest.raises(ValidationError, match="github_user") as exc_info:
            validate_github_username(None)
        assert exc_info.value.field == "github_user"

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="required"):
            validate_github_username("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError, match="required"):
            validate_github_username("   ")

    def test_too_long_raises(self):
        with pytest.raises(ValidationError, match="at most 39"):
            validate_github_username("a" * 40)

    def test_starts_with_hyphen_raises(self):
        with pytest.raises(ValidationError, match="cannot start or end"):
            validate_github_username("-octocat")

    def test_ends_with_hyphen_raises(self):
        with pytest.raises(ValidationError, match="cannot start or end"):
            validate_github_username("octocat-")

    def test_consecutive_hyphens_allowed(self):
        assert validate_github_username("octo--cat") == "octo--cat"

    def test_spaces_in_name_raises(self):
        with pytest.raises(ValidationError, match="alphanumeric"):
            validate_github_username("octo cat")


class TestValidateJobText:
    def test_valid_text(self):
        text = "Looking for a Python developer with Django experience."
        assert validate_job_text(text) == text

    def test_strips_whitespace(self):
        text = "  Looking for a Python developer.  "
        assert validate_job_text(text) == text.strip()

    def test_none_raises(self):
        with pytest.raises(ValidationError, match="job_text") as exc_info:
            validate_job_text(None)
        assert exc_info.value.field == "job_text"

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="required"):
            validate_job_text("")

    def test_too_short_raises(self):
        with pytest.raises(ValidationError, match="too short"):
            validate_job_text("Python dev")


class TestValidateResumeText:
    def test_valid_text(self):
        text = "5 years of experience with Python, Django, and PostgreSQL."
        assert validate_resume_text(text) == text

    def test_none_returns_none(self):
        assert validate_resume_text(None) is None

    def test_empty_returns_none(self):
        assert validate_resume_text("") is None

    def test_whitespace_returns_none(self):
        assert validate_resume_text("   ") is None

    def test_too_short_raises(self):
        with pytest.raises(ValidationError, match="too short"):
            validate_resume_text("short")

    def test_strips_whitespace(self):
        text = "  5 years of experience with Python and Django.  "
        assert validate_resume_text(text) == text.strip()


class TestValidationErrorAttributes:
    def test_field_and_constraint(self):
        err = ValidationError("my_field", "must be positive")
        assert err.field == "my_field"
        assert err.constraint == "must be positive"
        assert str(err) == "my_field: must be positive"
