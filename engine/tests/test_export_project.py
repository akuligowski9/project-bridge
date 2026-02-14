"""Tests for project spec export feature."""

import pytest

from projectbridge.ai.no_ai import NoAIProvider
from projectbridge.export import render_project_spec
from projectbridge.export_project import generate_project_spec
from projectbridge.recommend.resources import get_doc_links
from projectbridge.recommend.skill_features import get_skill_features
from projectbridge.schema import (
    AnalysisResult,
    DifficultyTier,
    DocLink,
    EstimatedScope,
    ProjectSpec,
    Recommendation,
    Skill,
    SkillCategory,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_result() -> AnalysisResult:
    """Build a representative analysis result for testing."""
    return AnalysisResult(
        strengths=[
            Skill(name="Python", category=SkillCategory.LANGUAGE),
            Skill(name="Flask", category=SkillCategory.FRAMEWORK),
            Skill(name="Docker", category=SkillCategory.INFRASTRUCTURE),
        ],
        gaps=[
            Skill(name="Django", category=SkillCategory.FRAMEWORK),
            Skill(name="PostgreSQL", category=SkillCategory.TOOL),
            Skill(name="AWS", category=SkillCategory.INFRASTRUCTURE),
        ],
        recommendations=[
            Recommendation(
                title="Build a REST API with Django",
                description="Create a RESTful API using Django REST Framework.",
                skills_addressed=["Django", "REST API"],
                estimated_scope=EstimatedScope.MEDIUM,
                skill_context=(
                    "Django powers a huge portion of production web applications. "
                    "Teams value developers who can ship backend features."
                ),
            ),
            Recommendation(
                title="Deploy a serverless API on AWS Lambda",
                description="Build a serverless REST API using AWS Lambda and API Gateway.",
                skills_addressed=["AWS", "Serverless"],
                estimated_scope=EstimatedScope.MEDIUM,
                skill_context=("Cloud infrastructure is fundamental to modern software delivery."),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Resource loader tests
# ---------------------------------------------------------------------------


class TestGetDocLinks:
    def test_known_skill(self):
        links = get_doc_links("Python")
        assert len(links) >= 1
        assert links[0]["label"]
        assert links[0]["url"].startswith("https://")

    def test_case_insensitive(self):
        links_lower = get_doc_links("python")
        links_upper = get_doc_links("PYTHON")
        assert links_lower == links_upper

    def test_unknown_skill_returns_empty(self):
        assert get_doc_links("NonexistentSkill123") == []

    def test_django_has_link(self):
        links = get_doc_links("Django")
        assert len(links) >= 1
        assert "django" in links[0]["url"].lower()


# ---------------------------------------------------------------------------
# Skill features loader tests
# ---------------------------------------------------------------------------


class TestGetSkillFeatures:
    def test_known_skill_and_difficulty(self):
        features = get_skill_features("Django", "beginner")
        assert len(features) >= 3
        assert all(isinstance(f, str) for f in features)

    def test_case_insensitive(self):
        features_lower = get_skill_features("django", "intermediate")
        features_upper = get_skill_features("DJANGO", "intermediate")
        assert features_lower == features_upper

    def test_unknown_skill_returns_empty(self):
        assert get_skill_features("NonexistentSkill123", "beginner") == []

    def test_unknown_difficulty_returns_empty(self):
        assert get_skill_features("Django", "extreme") == []

    def test_all_difficulties_have_features(self):
        expected = {"beginner": 3, "intermediate": 5, "advanced": 8}
        for diff, count in expected.items():
            features = get_skill_features("Python", diff)
            assert len(features) >= count, (
                f"Python/{diff} should have {count}+ features, got {len(features)}"
            )


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestProjectSpecSchema:
    def test_difficulty_tier_values(self):
        assert DifficultyTier.BEGINNER.value == "beginner"
        assert DifficultyTier.INTERMEDIATE.value == "intermediate"
        assert DifficultyTier.ADVANCED.value == "advanced"

    def test_project_spec_requires_3_features(self):
        with pytest.raises(Exception):
            ProjectSpec(
                title="Test",
                difficulty=DifficultyTier.BEGINNER,
                description="A test project.",
                features=["one", "two"],  # only 2
                skills_addressed=["Python"],
                why_skills_matter="Skills matter.",
            )

    def test_project_spec_valid(self):
        spec = ProjectSpec(
            title="Test Project",
            difficulty=DifficultyTier.INTERMEDIATE,
            description="A multi-paragraph description.\n\nWith personalization.",
            features=["Feature 1", "Feature 2", "Feature 3"],
            skills_addressed=["Django", "PostgreSQL"],
            why_skills_matter="These skills matter for production teams.",
            doc_links=[
                DocLink(
                    label="Django Docs",
                    url="https://docs.djangoproject.com/",
                    skill="Django",
                ),
            ],
            strengths_referenced=["Python"],
        )
        assert spec.title == "Test Project"
        assert spec.difficulty == DifficultyTier.INTERMEDIATE
        assert len(spec.features) == 3

    def test_project_spec_roundtrip(self):
        spec = ProjectSpec(
            title="Test",
            difficulty=DifficultyTier.BEGINNER,
            description="Description.",
            features=["a", "b", "c"],
            skills_addressed=["Go"],
            why_skills_matter="Matters.",
        )
        json_str = spec.model_dump_json()
        roundtrip = ProjectSpec.model_validate_json(json_str)
        assert roundtrip == spec


# ---------------------------------------------------------------------------
# generate_project_spec tests (heuristic path)
# ---------------------------------------------------------------------------


class TestGenerateProjectSpec:
    def test_heuristic_returns_project_spec(self):
        result = _make_result()
        rec = result.recommendations[0]
        provider = NoAIProvider()
        spec = generate_project_spec(rec, "beginner", result, provider)
        assert isinstance(spec, ProjectSpec)
        assert spec.title == rec.title
        assert spec.difficulty == DifficultyTier.BEGINNER

    def test_description_is_multi_paragraph(self):
        result = _make_result()
        rec = result.recommendations[0]
        provider = NoAIProvider()
        spec = generate_project_spec(rec, "intermediate", result, provider)
        assert "\n\n" in spec.description

    def test_beginner_has_3_features(self):
        result = _make_result()
        rec = result.recommendations[0]
        provider = NoAIProvider()
        spec = generate_project_spec(rec, "beginner", result, provider)
        assert len(spec.features) == 3

    def test_intermediate_has_5_features(self):
        result = _make_result()
        rec = result.recommendations[0]
        provider = NoAIProvider()
        spec = generate_project_spec(rec, "intermediate", result, provider)
        assert len(spec.features) == 5

    def test_advanced_has_8_features(self):
        result = _make_result()
        rec = result.recommendations[0]
        provider = NoAIProvider()
        spec = generate_project_spec(rec, "advanced", result, provider)
        assert len(spec.features) == 8

    def test_doc_links_populated(self):
        result = _make_result()
        rec = result.recommendations[0]
        provider = NoAIProvider()
        spec = generate_project_spec(rec, "beginner", result, provider)
        # Django and REST API should have doc links
        assert len(spec.doc_links) >= 1
        assert any(link.skill == "Django" for link in spec.doc_links)

    def test_difficulty_affects_features(self):
        result = _make_result()
        rec = result.recommendations[0]
        provider = NoAIProvider()
        spec_beg = generate_project_spec(rec, "beginner", result, provider)
        spec_adv = generate_project_spec(rec, "advanced", result, provider)
        # Features should differ between beginner and advanced
        assert spec_beg.features != spec_adv.features

    def test_why_skills_matter_from_skill_context(self):
        result = _make_result()
        rec = result.recommendations[0]
        provider = NoAIProvider()
        spec = generate_project_spec(rec, "intermediate", result, provider)
        assert spec.why_skills_matter == rec.skill_context

    def test_skills_addressed_matches_recommendation(self):
        result = _make_result()
        rec = result.recommendations[0]
        provider = NoAIProvider()
        spec = generate_project_spec(rec, "beginner", result, provider)
        assert spec.skills_addressed == list(rec.skills_addressed)

    def test_invalid_difficulty_raises(self):
        result = _make_result()
        rec = result.recommendations[0]
        provider = NoAIProvider()
        with pytest.raises(ValueError):
            generate_project_spec(rec, "extreme", result, provider)

    def test_second_recommendation(self):
        result = _make_result()
        rec = result.recommendations[1]
        provider = NoAIProvider()
        spec = generate_project_spec(rec, "intermediate", result, provider)
        assert spec.title == "Deploy a serverless API on AWS Lambda"
        assert "AWS" in spec.skills_addressed


# ---------------------------------------------------------------------------
# render_project_spec tests
# ---------------------------------------------------------------------------


class TestRenderProjectSpec:
    def _make_spec(self) -> ProjectSpec:
        return ProjectSpec(
            title="Build a REST API with Django",
            difficulty=DifficultyTier.INTERMEDIATE,
            description="Build a Django API.\n\nPersonalized paragraph.",
            features=[
                "Implement token-based authentication",
                "Add paginated list endpoints",
                "Build model serializers with validation",
            ],
            skills_addressed=["Django", "REST API"],
            why_skills_matter="Django powers production web apps. Teams value this.",
            doc_links=[
                DocLink(
                    label="Django Documentation",
                    url="https://docs.djangoproject.com/en/stable/",
                    skill="Django",
                ),
                DocLink(
                    label="MDN HTTP Guide",
                    url="https://developer.mozilla.org/en-US/docs/Web/HTTP",
                    skill="REST API",
                ),
            ],
            strengths_referenced=["Python"],
        )

    def test_contains_title(self):
        md = render_project_spec(self._make_spec())
        assert "# Project Spec: Build a REST API with Django" in md

    def test_contains_difficulty(self):
        md = render_project_spec(self._make_spec())
        assert "**Difficulty:** Intermediate" in md

    def test_contains_skills(self):
        md = render_project_spec(self._make_spec())
        assert "**Skills:** Django, REST API" in md

    def test_contains_description(self):
        md = render_project_spec(self._make_spec())
        assert "## Project Description" in md
        assert "Build a Django API." in md
        assert "Personalized paragraph." in md

    def test_contains_features(self):
        md = render_project_spec(self._make_spec())
        assert "## Key Features" in md
        assert "1. Implement token-based authentication" in md
        assert "2. Add paginated list endpoints" in md
        assert "3. Build model serializers with validation" in md

    def test_contains_why_skills_matter(self):
        md = render_project_spec(self._make_spec())
        assert "## Why These Skills Matter" in md
        assert "Django powers production web apps" in md

    def test_contains_doc_links(self):
        md = render_project_spec(self._make_spec())
        assert "## Documentation & Resources" in md
        assert "[Django Documentation](https://docs.djangoproject.com/en/stable/)" in md
        assert "[MDN HTTP Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP)" in md

    def test_contains_footer(self):
        md = render_project_spec(self._make_spec())
        assert "Generated by ProjectBridge v" in md

    def test_no_doc_links_section_when_empty(self):
        spec = self._make_spec()
        spec.doc_links = []
        md = render_project_spec(spec)
        assert "## Documentation & Resources" not in md

    def test_no_why_section_when_empty(self):
        spec = self._make_spec()
        spec.why_skills_matter = ""
        md = render_project_spec(spec)
        assert "## Why These Skills Matter" not in md


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------


class TestCLIExportProject:
    def test_example_beginner(self):
        from projectbridge.cli import main

        exit_code = main(
            [
                "export-project",
                "--example",
                "--recommendation",
                "1",
                "--difficulty",
                "beginner",
                "--no-ai",
            ]
        )
        assert exit_code == 0

    def test_example_advanced(self):
        from projectbridge.cli import main

        exit_code = main(
            [
                "export-project",
                "--example",
                "--recommendation",
                "1",
                "--difficulty",
                "advanced",
                "--no-ai",
            ]
        )
        assert exit_code == 0

    def test_invalid_recommendation_index(self):
        from projectbridge.cli import main

        exit_code = main(
            [
                "export-project",
                "--example",
                "--recommendation",
                "999",
                "--difficulty",
                "beginner",
                "--no-ai",
            ]
        )
        assert exit_code == 1

    def test_zero_recommendation_index(self):
        from projectbridge.cli import main

        exit_code = main(
            [
                "export-project",
                "--example",
                "--recommendation",
                "0",
                "--difficulty",
                "beginner",
                "--no-ai",
            ]
        )
        assert exit_code == 1

    def test_output_to_file(self, tmp_path):
        from projectbridge.cli import main

        out_file = tmp_path / "spec.md"
        exit_code = main(
            [
                "export-project",
                "--example",
                "--recommendation",
                "1",
                "--difficulty",
                "intermediate",
                "--no-ai",
                "--output",
                str(out_file),
            ]
        )
        assert exit_code == 0
        content = out_file.read_text()
        assert "# Project Spec:" in content
        assert "## Key Features" in content

    def test_no_input_fails(self):
        from projectbridge.cli import main

        exit_code = main(
            ["export-project", "--recommendation", "1", "--difficulty", "beginner", "--no-ai"]
        )
        assert exit_code == 1
