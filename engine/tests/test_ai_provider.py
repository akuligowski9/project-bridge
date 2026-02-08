"""Tests for projectbridge.ai.provider and no_ai."""

import pytest

from projectbridge.ai.provider import AIProvider, get_provider
from projectbridge.ai.no_ai import NoAIProvider


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


class TestRegistry:
    def test_get_none_provider(self):
        p = get_provider("none")
        assert isinstance(p, NoAIProvider)

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown AI provider"):
            get_provider("nonexistent")
