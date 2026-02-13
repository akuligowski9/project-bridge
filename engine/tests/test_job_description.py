"""Tests for projectbridge.input.job_description."""

import pytest

from projectbridge.input.job_description import (
    EmptyJobDescriptionError,
    JobRequirements,
    NonTechnicalJobError,
    parse_job_description,
    validate_technical_content,
)


class TestParseJobDescription:
    def test_bullet_format(self, sample_job_text):
        result = parse_job_description(sample_job_text)
        assert isinstance(result, JobRequirements)
        assert "Python" in result.required_technologies
        assert "React" in result.required_technologies
        assert "Docker" in result.required_technologies

    def test_prose_format(self, sample_job_text_prose):
        result = parse_job_description(sample_job_text_prose)
        assert "Java" in result.required_technologies
        assert "Spring Boot" in result.required_technologies
        assert "Docker" in result.required_technologies

    def test_domains(self, sample_job_text):
        result = parse_job_description(sample_job_text)
        assert "full-stack" in result.experience_domains

    def test_architecture(self, sample_job_text):
        result = parse_job_description(sample_job_text)
        assert "microservices" in result.architectural_expectations
        assert "CI/CD" in result.architectural_expectations

    def test_empty_raises(self):
        with pytest.raises(EmptyJobDescriptionError):
            parse_job_description("")

    def test_whitespace_raises(self):
        with pytest.raises(EmptyJobDescriptionError):
            parse_job_description("   \n\t  ")

    def test_roundtrip(self, sample_job_text):
        result = parse_job_description(sample_job_text)
        json_str = result.model_dump_json()
        roundtrip = JobRequirements.model_validate_json(json_str)
        assert roundtrip == result


class TestValidateTechnicalContent:
    def test_passes_with_technologies(self):
        text = "We need a Python developer with Docker experience."
        reqs = parse_job_description(text)
        validate_technical_content(text, reqs)  # should not raise

    def test_passes_with_role_indicator_no_tech(self):
        text = "Looking for a software engineer to join our team."
        reqs = JobRequirements(
            required_technologies=[],
            experience_domains=[],
            architectural_expectations=[],
        )
        validate_technical_content(text, reqs)  # should not raise

    def test_raises_for_non_technical(self):
        text = (
            "Sales manager role, 5 years experience managing "
            "client relationships and closing deals."
        )
        reqs = JobRequirements(
            required_technologies=[],
            experience_domains=[],
            architectural_expectations=[],
        )
        with pytest.raises(NonTechnicalJobError, match="No technical skills detected"):
            validate_technical_content(text, reqs)

    def test_raises_for_marketing_role(self):
        text = "Marketing coordinator, manage social media campaigns and brand strategy."
        reqs = parse_job_description(text)
        with pytest.raises(NonTechnicalJobError):
            validate_technical_content(text, reqs)

    def test_passes_with_devops_indicator(self):
        text = "DevOps position, manage deployment pipelines and monitoring."
        reqs = JobRequirements(
            required_technologies=[],
            experience_domains=["devops"],
            architectural_expectations=[],
        )
        validate_technical_content(text, reqs)  # should not raise
