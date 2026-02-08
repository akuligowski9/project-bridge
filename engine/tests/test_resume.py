"""Tests for projectbridge.input.resume."""

import pytest

from projectbridge.input.resume import (
    ResumeContext,
    ResumeParseError,
    merge_resume_context,
    parse_resume,
)


class TestParseResume:
    def test_extracts_skills(self, sample_resume_text):
        result = parse_resume(sample_resume_text)
        assert "Python" in result.skills
        assert "Docker" in result.skills
        assert "Kubernetes" in result.skills

    def test_extracts_domains(self, sample_resume_text):
        result = parse_resume(sample_resume_text)
        assert "backend" in result.experience_domains
        assert "fintech" in result.experience_domains

    def test_extracts_years(self, sample_resume_text):
        result = parse_resume(sample_resume_text)
        assert result.years_of_experience == 8

    def test_no_years_returns_none(self):
        result = parse_resume("Skills: Python, Java, Docker")
        assert result.years_of_experience is None

    def test_empty_raises(self):
        with pytest.raises(ResumeParseError):
            parse_resume("")

    def test_whitespace_raises(self):
        with pytest.raises(ResumeParseError):
            parse_resume("   \n  ")


class TestMergeResumeContext:
    def test_adds_secondary_fields(self, sample_dev_context):
        resume = ResumeContext(
            skills=["Kubernetes", "Terraform"],
            experience_domains=["cloud"],
            years_of_experience=5,
        )
        enriched = merge_resume_context(sample_dev_context, resume)
        assert enriched["resume_skills"] == ["Kubernetes", "Terraform"]
        assert enriched["resume_domains"] == ["cloud"]
        assert enriched["resume_years"] == 5
        # Original fields unchanged
        assert enriched["languages"] == sample_dev_context["languages"]
        assert enriched["frameworks"] == sample_dev_context["frameworks"]
