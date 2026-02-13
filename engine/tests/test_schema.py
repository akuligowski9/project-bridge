"""Tests for projectbridge.schema."""

import pytest
from pydantic import ValidationError

from projectbridge.schema import (
    AnalysisResult,
    EstimatedScope,
    Recommendation,
    Skill,
    SkillCategory,
)


class TestSkill:
    def test_create(self):
        s = Skill(name="Python", category=SkillCategory.LANGUAGE)
        assert s.name == "Python"
        assert s.category == SkillCategory.LANGUAGE

    def test_missing_category_raises(self):
        with pytest.raises(ValidationError):
            Skill.model_validate({"name": "Python"})


class TestRecommendation:
    def test_max_three_skills(self):
        r = Recommendation(
            title="Test",
            description="Desc",
            skills_addressed=["A", "B", "C"],
            estimated_scope=EstimatedScope.SMALL,
        )
        assert len(r.skills_addressed) == 3

    def test_over_three_skills_raises(self):
        with pytest.raises(ValidationError):
            Recommendation(
                title="Test",
                description="Desc",
                skills_addressed=["A", "B", "C", "D"],
                estimated_scope=EstimatedScope.SMALL,
            )

    def test_skill_context_optional(self):
        r = Recommendation(
            title="Test",
            description="Desc",
            skills_addressed=["A"],
            estimated_scope=EstimatedScope.SMALL,
        )
        assert r.skill_context is None

    def test_skill_context_set(self):
        r = Recommendation(
            title="Test",
            description="Desc",
            skills_addressed=["A"],
            estimated_scope=EstimatedScope.SMALL,
            skill_context="Teams value this skill because it unlocks career growth.",
        )
        assert r.skill_context == "Teams value this skill because it unlocks career growth."


class TestAnalysisResult:
    def test_schema_version_default(self):
        r = AnalysisResult(strengths=[], gaps=[], recommendations=[])
        assert r.schema_version == "1.1"

    def test_schema_version_accepts_1_0(self):
        r = AnalysisResult(schema_version="1.0", strengths=[], gaps=[], recommendations=[])
        assert r.schema_version == "1.0"

    def test_schema_version_accepts_1_1(self):
        r = AnalysisResult(schema_version="1.1", strengths=[], gaps=[], recommendations=[])
        assert r.schema_version == "1.1"

    def test_missing_field_raises(self):
        with pytest.raises(ValidationError):
            AnalysisResult.model_validate({"schema_version": "1.1", "strengths": [], "gaps": []})

    def test_roundtrip(self):
        r = AnalysisResult(
            strengths=[Skill(name="Python", category=SkillCategory.LANGUAGE)],
            gaps=[Skill(name="Docker", category=SkillCategory.INFRASTRUCTURE)],
            recommendations=[
                Recommendation(
                    title="Build something",
                    description="A project.",
                    skills_addressed=["Docker"],
                    estimated_scope=EstimatedScope.SMALL,
                    skill_context="Containerization is essential for modern teams.",
                )
            ],
        )
        json_str = r.model_dump_json()
        roundtrip = AnalysisResult.model_validate_json(json_str)
        assert roundtrip == r
