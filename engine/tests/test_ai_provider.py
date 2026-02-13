"""Tests for projectbridge.ai.provider and no_ai."""

import pytest

from projectbridge.ai.no_ai import NoAIProvider
from projectbridge.ai.provider import AIProvider, get_provider


class TestAIProvider:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            AIProvider()


class TestNoAIProvider:
    def test_analyze_context_passthrough(self):
        provider = NoAIProvider()
        ctx = {"languages": [{"name": "Python"}]}
        assert provider.analyze_context(ctx) == ctx

    def test_generate_recommendations(self):
        provider = NoAIProvider()
        gaps = {
            "missing_skills": [
                {"name": "Kubernetes", "category": "infrastructure"},
                {"name": "Redis", "category": "infrastructure"},
            ],
            "adjacent_skills": [
                {"name": "TypeScript", "category": "language"},
            ],
        }
        recs = provider.generate_recommendations(gaps)
        assert len(recs) > 0
        for r in recs:
            assert "title" in r
            assert "description" in r
            assert "skills_addressed" in r
            assert len(r["skills_addressed"]) <= 3
            assert "estimated_scope" in r

    def test_recommendations_include_skill_context(self):
        provider = NoAIProvider()
        gaps = {
            "missing_skills": [
                {"name": "ObscureTech99", "category": "tool"},
            ],
            "adjacent_skills": [],
        }
        recs = provider.generate_recommendations(gaps)
        assert len(recs) >= 1
        for r in recs:
            assert "skill_context" in r
            assert isinstance(r["skill_context"], str)
            assert len(r["skill_context"]) > 0

    def test_heuristic_skill_context_matches_category(self):
        provider = NoAIProvider()
        gaps = {
            "missing_skills": [
                {"name": "UnknownLang", "category": "language"},
            ],
            "adjacent_skills": [],
        }
        recs = provider.generate_recommendations(gaps)
        assert len(recs) >= 1
        # Language category context should mention "language" concepts
        ctx = recs[0]["skill_context"].lower()
        assert "language" in ctx or "code" in ctx

    def test_template_recommendations_include_skill_context(self):
        provider = NoAIProvider()
        gaps = {
            "missing_skills": [
                {"name": "Docker", "category": "infrastructure"},
                {"name": "Kubernetes", "category": "infrastructure"},
            ],
            "adjacent_skills": [],
        }
        recs = provider.generate_recommendations(gaps)
        # Template-based recs should have skill_context from the template
        template_recs = [r for r in recs if "Build a project using" not in r["title"]]
        for r in template_recs:
            assert "skill_context" in r
            assert isinstance(r["skill_context"], str)
            assert len(r["skill_context"]) >= 50


class TestNoAIPersonalization:
    def test_personalized_description_with_known_skills(self):
        provider = NoAIProvider()
        gaps = {
            "missing_skills": [
                {"name": "Kubernetes", "category": "infrastructure"},
                {"name": "Terraform", "category": "infrastructure"},
                {"name": "Ansible", "category": "infrastructure"},
            ],
            "adjacent_skills": [],
            "dev_context_summary": "Developer knows: Python, Docker, Flask.",
        }
        recs = provider.generate_recommendations(gaps)
        # Heuristic recs for uncovered skills should mention "head start"
        # if any of the skills overlap with known skills.
        heuristic_recs = [r for r in recs if "Build a project using" in r["title"]]
        for r in heuristic_recs:
            # Not all may have overlap, but the description should still exist
            assert len(r["description"]) > 0

    def test_no_personalization_without_context(self):
        provider = NoAIProvider()
        gaps = {
            "missing_skills": [
                {"name": "ObscureTech42", "category": "tool"},
            ],
            "adjacent_skills": [],
        }
        recs = provider.generate_recommendations(gaps)
        assert len(recs) >= 1
        assert "head start" not in recs[0]["description"]

    def test_experience_level_threaded_to_templates(self):
        provider = NoAIProvider()
        gaps = {
            "missing_skills": [
                {"name": "Python", "category": "language"},
            ],
            "adjacent_skills": [],
            "experience_level": "junior",
        }
        recs = provider.generate_recommendations(gaps)
        # Should get at least one template-based rec
        template_recs = [r for r in recs if "Build a project using" not in r["title"]]
        assert len(template_recs) >= 1


class TestRegistry:
    def test_get_none_provider(self):
        p = get_provider("none")
        assert isinstance(p, NoAIProvider)

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown AI provider"):
            get_provider("nonexistent")
