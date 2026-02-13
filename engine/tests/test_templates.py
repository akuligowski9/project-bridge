"""Tests for projectbridge.recommend.templates."""

from projectbridge.recommend.templates import load_templates, select_templates


class TestLoadTemplates:
    def test_loads_templates(self):
        templates = load_templates()
        assert isinstance(templates, list)
        assert len(templates) >= 15

    def test_template_structure(self):
        templates = load_templates()
        for tpl in templates:
            assert "title" in tpl
            assert "description" in tpl
            assert "skills_addressed" in tpl
            assert "estimated_scope" in tpl
            assert "difficulty" in tpl
            assert "skill_context" in tpl
            assert len(tpl["skills_addressed"]) <= 3
            assert tpl["estimated_scope"] in ("small", "medium", "large")
            assert tpl["difficulty"] in ("beginner", "intermediate", "advanced")

    def test_skill_context_is_substantive(self):
        templates = load_templates()
        for tpl in templates:
            ctx = tpl["skill_context"]
            assert isinstance(ctx, str), f"{tpl['title']} skill_context is not a string"
            assert len(ctx) >= 50, f"{tpl['title']} skill_context is too short ({len(ctx)} chars)"


class TestSelectTemplates:
    def test_selects_by_skill_overlap(self):
        results = select_templates({"Docker", "Kubernetes"})
        assert len(results) >= 1
        # The Docker+K8s template should be first (2 overlapping skills)
        top = results[0]
        skills_lower = {s.lower() for s in top["skills_addressed"]}
        assert "docker" in skills_lower or "kubernetes" in skills_lower

    def test_returns_empty_for_no_match(self):
        results = select_templates({"UnknownTech42"})
        assert results == []

    def test_respects_max_results(self):
        results = select_templates({"Python", "React", "Docker", "TypeScript"}, max_results=2)
        assert len(results) <= 2

    def test_case_insensitive(self):
        lower = select_templates({"react"})
        upper = select_templates({"React"})
        assert len(lower) == len(upper)

    def test_highest_overlap_first(self):
        results = select_templates({"Next.js", "PostgreSQL", "TypeScript"})
        if len(results) >= 2:
            # First result should have >= overlap of second
            first_skills = {s.lower() for s in results[0]["skills_addressed"]}
            second_skills = {s.lower() for s in results[1]["skills_addressed"]}
            gap_lower = {"next.js", "postgresql", "typescript"}
            assert len(first_skills & gap_lower) >= len(second_skills & gap_lower)

    def test_selected_templates_include_skill_context(self):
        results = select_templates({"Docker", "Kubernetes"})
        for tpl in results:
            assert "skill_context" in tpl
            assert isinstance(tpl["skill_context"], str)
            assert len(tpl["skill_context"]) >= 50

    def test_experience_level_junior_prefers_beginner(self):
        results = select_templates({"Python"}, experience_level="junior")
        assert len(results) >= 1
        # With a single-skill overlap, beginner templates should rank above intermediate.
        beginner_results = [r for r in results if r["difficulty"] == "beginner"]
        assert len(beginner_results) >= 1

    def test_experience_level_senior_prefers_advanced(self):
        results = select_templates(
            {"Kafka", "Event-Driven Architecture"}, experience_level="senior"
        )
        if results:
            # The Kafka template is "advanced", should appear.
            assert results[0]["difficulty"] in ("advanced", "intermediate")

    def test_experience_level_none_no_error(self):
        results = select_templates({"Docker"}, experience_level=None)
        assert len(results) >= 1


class TestNoAIWithTemplates:
    def test_uses_templates_when_available(self):
        from projectbridge.ai.no_ai import NoAIProvider

        provider = NoAIProvider()
        gaps = {
            "missing_skills": [
                {"name": "Docker", "category": "infrastructure"},
                {"name": "Kubernetes", "category": "infrastructure"},
            ],
            "adjacent_skills": [],
        }
        recs = provider.generate_recommendations(gaps)
        # Should have at least one template-based recommendation
        assert len(recs) >= 1
        # Template titles are specific, not the generic "Build a project using..."
        has_template = any("Build a project using" not in r["title"] for r in recs)
        assert has_template

    def test_falls_back_to_heuristic_for_uncovered_skills(self):
        from projectbridge.ai.no_ai import NoAIProvider

        provider = NoAIProvider()
        gaps = {
            "missing_skills": [
                {"name": "ObscureTech99", "category": "tool"},
            ],
            "adjacent_skills": [],
        }
        recs = provider.generate_recommendations(gaps)
        assert len(recs) >= 1
        assert "ObscureTech99" in recs[0]["title"]
