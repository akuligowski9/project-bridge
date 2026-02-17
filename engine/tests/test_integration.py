"""Integration tests — exercise the full pipeline."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from projectbridge.cli import main
from projectbridge.orchestrator import PipelineError, run_analysis
from projectbridge.schema import AnalysisResult

JOB_URL_HTML = """\
<html><head><title>Senior Engineer</title></head>
<body>
<nav>Site Nav</nav>
<main>
<h1>Senior Full-Stack Engineer</h1>
<p>We are looking for an experienced engineer with 4+ years of Python and TypeScript.
Strong experience with Django or FastAPI. Proficiency with React. Experience with
PostgreSQL, Redis, Docker, Kubernetes, and CI/CD pipelines.</p>
</main>
<footer>Copyright</footer>
</body></html>
"""

JOB_URL_EXTRACTED = (
    "We are looking for an experienced engineer with 4+ years of Python and TypeScript. "
    "Strong experience with Django or FastAPI. Proficiency with React. Experience with "
    "PostgreSQL, Redis, Docker, Kubernetes, and CI/CD pipelines."
)


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

    def test_job_url_flag_exclusive_with_job_text(self):
        exit_code = main(
            [
                "analyze",
                "--job-text",
                "inline text here enough chars",
                "--job-url",
                "https://example.com/jobs/123",
            ]
        )
        assert exit_code == 1

    def test_job_url_flag_exclusive_with_job_file(self):
        exit_code = main(
            [
                "analyze",
                "--job",
                "some.txt",
                "--job-url",
                "https://example.com/jobs/123",
            ]
        )
        assert exit_code == 1

    @patch("projectbridge.input.job_url.trafilatura.extract", return_value=JOB_URL_EXTRACTED)
    @patch("projectbridge.input.job_url.requests.get")
    def test_job_url_full_pipeline(self, mock_get, _mock_extract):
        """A valid job URL produces a complete analysis result."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = JOB_URL_HTML
        mock_get.return_value = mock_resp

        result = run_analysis(
            job_url="https://boards.greenhouse.io/example/jobs/123",
            github_user="octocat",
            no_ai=True,
        )
        assert isinstance(result, AnalysisResult)
        assert result.schema_version == "1.2"
        assert len(result.gaps) > 0
        assert len(result.recommendations) > 0

    @patch("projectbridge.input.job_url.trafilatura.extract", return_value=JOB_URL_EXTRACTED)
    @patch("projectbridge.input.job_url.requests.get")
    def test_job_url_cli_succeeds(self, mock_get, _mock_extract):
        """--job-url flag runs the full CLI pipeline successfully."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = JOB_URL_HTML
        mock_get.return_value = mock_resp

        exit_code = main(
            [
                "analyze",
                "--job-url",
                "https://boards.greenhouse.io/example/jobs/123",
                "--github-user",
                "octocat",
                "--no-ai",
            ]
        )
        assert exit_code == 0

    @patch("projectbridge.input.job_url.trafilatura.extract", return_value=None)
    @patch("projectbridge.input.job_url.requests.get")
    def test_job_url_extraction_failure_cli(self, mock_get, _mock_extract):
        """When extraction returns nothing, CLI exits with error."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html></html>"
        mock_get.return_value = mock_resp

        exit_code = main(
            [
                "analyze",
                "--job-url",
                "https://example.com/not-a-job",
                "--github-user",
                "octocat",
                "--no-ai",
            ]
        )
        assert exit_code == 1

    @patch("projectbridge.input.job_url.requests.get")
    def test_job_url_403_cli(self, mock_get):
        """A 403 response exits with error suggesting manual paste."""
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_get.return_value = mock_resp

        exit_code = main(
            [
                "analyze",
                "--job-url",
                "https://linkedin.com/jobs/view/123",
                "--github-user",
                "octocat",
                "--no-ai",
            ]
        )
        assert exit_code == 1


class TestLocalScanErrors:
    @patch("projectbridge.orchestrator.subprocess.run", side_effect=FileNotFoundError)
    def test_pb_scan_not_found(self, _mock_run):
        with pytest.raises(PipelineError, match="local_scan") as exc_info:
            run_analysis(
                local_repos=["/some/path"],
                job_text="We need a Python engineer with Django, Docker, REST APIs.",
                no_ai=True,
            )
        assert "pb-scan not found" in str(exc_info.value)

    @patch("projectbridge.orchestrator.subprocess.run")
    def test_pb_scan_nonzero_exit(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "pb-scan", stderr="scan failed")
        with pytest.raises(PipelineError, match="local_scan"):
            run_analysis(
                local_repos=["/some/path"],
                job_text="We need a Python engineer with Django, Docker, REST APIs.",
                no_ai=True,
            )

    @patch("projectbridge.orchestrator.subprocess.run")
    def test_pb_scan_invalid_json(self, mock_run):
        mock_run.return_value = MagicMock(stdout="not json", stderr="")
        with pytest.raises(PipelineError, match="local_scan") as exc_info:
            run_analysis(
                local_repos=["/some/path"],
                job_text="We need a Python engineer with Django, Docker, REST APIs.",
                no_ai=True,
            )
        assert "Invalid JSON" in str(exc_info.value)
