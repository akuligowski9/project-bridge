"""Tests for projectbridge.export."""

from projectbridge import __version__
from projectbridge.export import Snapshot, create_snapshot, render_markdown
from projectbridge.schema import (
    AnalysisResult,
    EstimatedScope,
    Recommendation,
    Skill,
    SkillCategory,
)


class TestCreateSnapshot:
    def test_snapshot_has_metadata(self):
        result = AnalysisResult(strengths=[], gaps=[], recommendations=[])
        snap = create_snapshot(result)
        assert snap.exported_at
        assert snap.engine_version == __version__
        assert snap.schema_version == "1.1"
        assert snap.analysis == result

    def test_snapshot_roundtrip(self):
        result = AnalysisResult(strengths=[], gaps=[], recommendations=[])
        snap = create_snapshot(result)
        json_str = snap.model_dump_json()
        roundtrip = Snapshot.model_validate_json(json_str)
        assert roundtrip.engine_version == snap.engine_version
        assert roundtrip.schema_version == snap.schema_version
        assert roundtrip.analysis == snap.analysis


class TestRenderMarkdown:
    def _make_result(self) -> AnalysisResult:
        return AnalysisResult(
            strengths=[
                Skill(name="Python", category=SkillCategory.LANGUAGE),
                Skill(name="Django", category=SkillCategory.FRAMEWORK),
            ],
            gaps=[
                Skill(name="Docker", category=SkillCategory.INFRASTRUCTURE),
            ],
            recommendations=[
                Recommendation(
                    title="Containerize a Django App",
                    description="Build a Docker setup for a Django project.",
                    skills_addressed=["Docker", "Django"],
                    estimated_scope=EstimatedScope.SMALL,
                    skill_context="Containerization is how modern teams ship software reliably.",
                ),
            ],
        )

    def test_contains_header(self):
        md = render_markdown(self._make_result())
        assert "# ProjectBridge Analysis" in md

    def test_contains_strengths_section(self):
        md = render_markdown(self._make_result())
        assert "## Strengths" in md
        assert "- Python (language)" in md
        assert "- Django (framework)" in md

    def test_contains_gaps_section(self):
        md = render_markdown(self._make_result())
        assert "## Skill Gaps" in md
        assert "- Docker (infrastructure)" in md

    def test_contains_recommendations(self):
        md = render_markdown(self._make_result())
        assert "### Containerize a Django App" in md
        assert "Docker, Django" in md
        assert "small" in md

    def test_contains_skill_context_blockquote(self):
        md = render_markdown(self._make_result())
        assert "> Containerization is how modern teams ship software reliably." in md

    def test_no_blockquote_when_skill_context_is_none(self):
        result = AnalysisResult(
            strengths=[],
            gaps=[],
            recommendations=[
                Recommendation(
                    title="Test Rec",
                    description="A project.",
                    skills_addressed=["Go"],
                    estimated_scope=EstimatedScope.SMALL,
                ),
            ],
        )
        md = render_markdown(result)
        assert "### Test Rec" in md
        # No blockquote should appear
        assert "> " not in md

    def test_empty_result(self):
        result = AnalysisResult(strengths=[], gaps=[], recommendations=[])
        md = render_markdown(result)
        assert "_None detected._" in md
        assert "_No recommendations generated._" in md

    def test_contains_footer(self):
        md = render_markdown(self._make_result())
        assert f"ProjectBridge v{__version__}" in md
