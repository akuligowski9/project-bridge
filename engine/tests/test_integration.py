"""Integration tests — exercise the full pipeline."""

from projectbridge.cli import main
from projectbridge.orchestrator import run_analysis
from projectbridge.schema import AnalysisResult


class TestFullPipeline:
    def test_example_mode_python_api(self):
        result = run_analysis(example=True, no_ai=True)
        assert isinstance(result, AnalysisResult)
        assert result.schema_version == "1.2"
        assert len(result.strengths) > 0
        assert len(result.gaps) > 0
        assert len(result.recommendations) > 0
        for r in result.recommendations:
            assert len(r.skills_addressed) <= 3

    def test_example_mode_has_skill_context(self):
        result = run_analysis(example=True, no_ai=True)
        # At least one recommendation should have skill_context
        has_context = any(r.skill_context is not None for r in result.recommendations)
        assert has_context

    def test_example_mode_has_experience_level(self):
        result = run_analysis(example=True, no_ai=True)
        assert result.experience_level in ("junior", "mid", "senior")

    def test_example_mode_has_portfolio_insights(self):
        result = run_analysis(example=True, no_ai=True)
        assert isinstance(result.portfolio_insights, list)

    def test_example_mode_has_interview_topics(self):
        result = run_analysis(example=True, no_ai=True)
        assert isinstance(result.interview_topics, list)
        # The example has gap skills like TypeScript, Django, etc. — should have topics.
        assert len(result.interview_topics) > 0
        for entry in result.interview_topics:
            assert entry.skill
            assert len(entry.topics) >= 2

    def test_example_mode_cli(self):
        exit_code = main(["analyze", "--example"])
        assert exit_code == 0

    def test_example_mode_no_ai_cli(self):
        exit_code = main(["analyze", "--example", "--no-ai"])
        assert exit_code == 0

    def test_export_example_cli(self):
        exit_code = main(["export", "--example"])
        assert exit_code == 0

    def test_missing_args_fails(self):
        exit_code = main(["analyze"])
        assert exit_code == 1

    def test_no_command_fails(self):
        exit_code = main([])
        assert exit_code == 1

    def test_export_missing_input_fails(self):
        exit_code = main(["export"])
        assert exit_code == 1

    def test_verbose_flag(self):
        exit_code = main(["--verbose", "analyze", "--example"])
        assert exit_code == 0

    def test_verbose_short_flag(self):
        exit_code = main(["-v", "analyze", "--example", "--no-ai"])
        assert exit_code == 0

    def test_job_text_inline(self):
        job = (
            "We need a Python developer with experience in Django, "
            "REST APIs, Docker, and PostgreSQL."
        )
        exit_code = main(
            [
                "analyze",
                "--github-user",
                "octocat",
                "--job-text",
                job,
                "--no-ai",
            ]
        )
        assert exit_code == 0

    def test_job_and_job_text_exclusive(self):
        exit_code = main(
            [
                "analyze",
                "--job",
                "some.txt",
                "--job-text",
                "inline text here enough chars",
            ]
        )
        assert exit_code == 1

    def test_export_markdown_cli(self):
        exit_code = main(["export", "--example", "--format", "markdown"])
        assert exit_code == 0
