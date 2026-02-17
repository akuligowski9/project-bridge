"""Engine orchestrator.

Coordinates the full analysis pipeline and is callable from both the
CLI and a Python API.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from typing import Any

import projectbridge.ai.anthropic_provider  # noqa: F401  — register the "anthropic" provider
import projectbridge.ai.no_ai  # noqa: F401  — register the "none" provider
import projectbridge.ai.ollama_provider  # noqa: F401  — register the "ollama" provider
import projectbridge.ai.openai_provider  # noqa: F401  — register the "openai" provider
from projectbridge.ai.provider import AIProvider, get_provider
from projectbridge.analysis.engine import analyze
from projectbridge.analysis.experience import infer_experience_level
from projectbridge.analysis.interview_topics import get_interview_topics
from projectbridge.analysis.portfolio import derive_portfolio_insights
from projectbridge.config.settings import ProjectBridgeConfig, load_config
from projectbridge.input.github import GitHubAnalyzer
from projectbridge.input.job_description import (
    parse_job_description,
    validate_technical_content,
)
from projectbridge.input.resume import merge_resume_context, parse_resume
from projectbridge.input.validation import (
    ValidationError,
    validate_github_username,
    validate_job_text,
    validate_resume_text,
)
from projectbridge.progress import Progress
from projectbridge.recommend.engine import generate_recommendations
from projectbridge.schema import AnalysisResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bundled example data (used by --example / example mode)
# ---------------------------------------------------------------------------

EXAMPLE_DEV_CONTEXT: dict[str, Any] = {
    "languages": [
        {"name": "Python", "category": "language", "percentage": 45.0},
        {"name": "JavaScript", "category": "language", "percentage": 30.0},
        {"name": "HTML", "category": "language", "percentage": 15.0},
        {"name": "CSS", "category": "language", "percentage": 10.0},
    ],
    "frameworks": [
        {"name": "Flask", "category": "framework"},
        {"name": "React", "category": "framework"},
    ],
    "infrastructure_signals": [
        {"name": "Docker", "category": "infrastructure"},
        {"name": "GitHub Actions", "category": "infrastructure"},
    ],
    "project_structures": ["src_layout", "python_package", "node_project"],
}

EXAMPLE_JOB_DESCRIPTION = """\
Senior Full-Stack Engineer

We are looking for an experienced full-stack engineer to join our platform team.

Requirements:
- 4+ years of professional experience with Python and TypeScript
- Strong experience with Django or FastAPI for backend services
- Proficiency with React and modern frontend tooling
- Experience with PostgreSQL and Redis
- Comfortable with Docker, Kubernetes, and CI/CD pipelines
- Familiarity with microservices architecture and RESTful API design
- Experience with cloud platforms (AWS preferred)
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class PipelineError(Exception):
    """Raised when a pipeline stage fails."""

    def __init__(self, stage: str, detail: str) -> None:
        self.stage = stage
        super().__init__(f"[{stage}] {detail}")


def _run_local_scan(local_repos: list[str]) -> dict[str, Any]:
    """Invoke pb-scan to scan local repositories and return dev_context."""
    cmd = ["pb-scan", "--paths"] + local_repos
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise PipelineError(
            "local_scan",
            "pb-scan not found. Install it with: cargo install --path scanner/",
        )
    except subprocess.CalledProcessError as exc:
        raise PipelineError("local_scan", exc.stderr.strip() or str(exc))

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise PipelineError("local_scan", f"Invalid JSON from pb-scan: {exc}")


def run_analysis(
    *,
    job_text: str | None = None,
    job_url: str | None = None,
    github_user: str | None = None,
    github_token: str | None = None,
    local_repos: list[str] | None = None,
    resume_text: str | None = None,
    no_ai: bool = False,
    provider_name: str | None = None,
    example: bool = False,
    no_cache: bool = False,
    progress: Progress | None = None,
    config: ProjectBridgeConfig | None = None,
) -> AnalysisResult:
    """Execute the complete analysis pipeline.

    Args:
        job_text: Raw job description text.
        job_url: URL to a job posting page (fetches and extracts text).
        github_user: GitHub username to analyze.
        github_token: GitHub personal access token (or read from env).
        local_repos: Local directory paths to scan with pb-scan.
        resume_text: Optional plain-text resume for contextual enrichment.
        no_ai: Force the NoAI heuristic provider.
        provider_name: AI provider override (none/openai/anthropic/ollama).
        example: Use bundled example data instead of live inputs.
        no_cache: Bypass GitHub API cache.
        config: Pre-loaded config; loaded from disk if *None*.

    Returns:
        A schema-valid :class:`AnalysisResult`.
    """
    if config is None:
        config = load_config()

    if progress is None:
        progress = Progress(enabled=False)

    # -- 1. Resolve AI provider --------------------------------------------
    progress.step("Resolving AI provider...")
    try:
        final_provider = provider_name or ("none" if no_ai else config.ai.provider)
        logger.info("Resolving AI provider: %s", final_provider)
        provider_kwargs: dict[str, Any] = {}
        if final_provider == "ollama":
            provider_kwargs["model"] = config.ai.ollama_model
        provider: AIProvider = get_provider(final_provider, **provider_kwargs)
    except Exception as exc:
        raise PipelineError("ai_provider", str(exc)) from exc

    # -- 1b. Fetch job URL if provided --------------------------------------
    if job_url:
        from projectbridge.input.job_url import JobURLError, fetch_job_text

        progress.start_spinner("Fetching job posting...")
        try:
            job_text = fetch_job_text(job_url)
        except JobURLError as exc:
            progress.stop_spinner()
            raise PipelineError("job_url_fetch", str(exc)) from exc
        progress.stop_spinner()

    # -- 2. Validate & gather inputs ----------------------------------------
    if example:
        logger.info("Using bundled example data")
        dev_context = EXAMPLE_DEV_CONTEXT
        job_text = EXAMPLE_JOB_DESCRIPTION
    elif local_repos:
        try:
            job_text = validate_job_text(job_text)
            resume_text = validate_resume_text(resume_text)
        except ValidationError as exc:
            raise PipelineError("validation", str(exc)) from exc

        logger.info("Scanning local repositories: %s", local_repos)
        progress.start_spinner("Scanning local repositories...")
        try:
            dev_context = _run_local_scan(local_repos)
        except PipelineError:
            progress.stop_spinner()
            raise
        progress.stop_spinner()
    else:
        try:
            github_user = validate_github_username(github_user)
            job_text = validate_job_text(job_text)
            resume_text = validate_resume_text(resume_text)
        except ValidationError as exc:
            raise PipelineError("validation", str(exc)) from exc

        # Resolve token: explicit arg > env var > config file.
        resolved_token = github_token or os.environ.get("GITHUB_TOKEN") or config.github.token
        if not resolved_token:
            logger.warning(
                "No GitHub token found. Using unauthenticated access "
                "(rate limited to 60 requests/hour). Set GITHUB_TOKEN env var "
                "or add github.token to projectbridge.config.yaml."
            )

        logger.info("Analyzing GitHub profile: %s", github_user)
        progress.start_spinner(f"Fetching GitHub data for {github_user}...")
        try:
            cache_on = config.cache.enabled and not no_cache
            analyzer = GitHubAnalyzer(
                token=resolved_token,
                cache_enabled=cache_on,
                cache_ttl=config.cache.ttl_seconds,
            )
            dev_context = analyzer.analyze(github_user)
        except Exception as exc:
            progress.stop_spinner()
            raise PipelineError("github_analyzer", str(exc)) from exc
        progress.stop_spinner()

    # -- 3. Resume enrichment (optional) -----------------------------------
    if resume_text:
        progress.step("Processing resume...")
        try:
            resume_ctx = parse_resume(resume_text)
            dev_context = merge_resume_context(dev_context, resume_ctx)
        except Exception as exc:
            raise PipelineError("resume_parser", str(exc)) from exc

    # -- 4. Parse job description ------------------------------------------
    progress.step("Parsing job description...")
    logger.info("Parsing job description")
    try:
        job_reqs_model = parse_job_description(job_text)
        validate_technical_content(job_text, job_reqs_model)
        job_reqs = job_reqs_model.model_dump()
    except Exception as exc:
        raise PipelineError("job_parser", str(exc)) from exc

    # -- 5. AI context enrichment (optional) --------------------------------
    if final_provider != "none":
        progress.start_spinner("Running AI analysis...")
    logger.info("Running AI context enrichment")
    try:
        dev_context = provider.analyze_context(dev_context)
    except Exception as exc:
        progress.stop_spinner()
        raise PipelineError("ai_context", str(exc)) from exc
    progress.stop_spinner()

    # -- 6. Core analysis --------------------------------------------------
    progress.step("Analyzing skills...")
    logger.info("Running core analysis")
    try:
        analysis = analyze(dev_context, job_reqs)
    except Exception as exc:
        raise PipelineError("analysis", str(exc)) from exc

    # -- 6a. Experience level inference ------------------------------------
    exp_level = infer_experience_level(dev_context)
    logger.info("Inferred experience level: %s", exp_level.value)

    # -- 6b. Portfolio insights --------------------------------------------
    portfolio_insights = derive_portfolio_insights(dev_context, job_reqs, analysis)

    # -- 6c. Interview topics for gap skills --------------------------------
    gap_skills = analysis["missing_skills"] + analysis["adjacent_skills"]
    interview_topics = []
    for skill in gap_skills:
        topics = get_interview_topics(skill.name)
        if topics:
            interview_topics.append({"skill": skill.name, "topics": topics})

    # -- 7. Recommendations ------------------------------------------------
    progress.step("Generating recommendations...")
    logger.info("Generating recommendations")
    try:
        recs = generate_recommendations(
            analysis,
            provider,
            max_recommendations=config.analysis.max_recommendations,
            experience_level=exp_level.value,
            dev_context=dev_context,
        )
    except Exception as exc:
        raise PipelineError("recommendations", str(exc)) from exc

    # -- 8. Assemble result ------------------------------------------------
    logger.info("Analysis complete")
    progress.done("Analysis complete.")
    return AnalysisResult(
        strengths=analysis["detected_skills"],
        gaps=analysis["missing_skills"] + analysis["adjacent_skills"],
        recommendations=recs,
        experience_level=exp_level.value,
        portfolio_insights=portfolio_insights,
        interview_topics=interview_topics,
    )
