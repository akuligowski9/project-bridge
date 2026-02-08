"""Tests for projectbridge.input.job_description."""

import pytest

from projectbridge.input.job_description import (
    EmptyJobDescriptionError,
    JobRequirements,
    parse_job_description,
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
