"""Engine orchestrator.

Coordinates the full analysis pipeline and is callable from both the
CLI and a Python API.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import projectbridge.ai.anthropic_provider  # noqa: F401  — register the "anthropic" provider
import projectbridge.ai.no_ai  # noqa: F401  — register the "none" provider
import projectbridge.ai.ollama_provider  # noqa: F401  — register the "ollama" provider
import projectbridge.ai.openai_provider  # noqa: F401  — register the "openai" provider
from projectbridge.ai.provider import AIProvider, get_provider
from projectbridge.analysis.engine import analyze
from projectbridge.config.settings import ProjectBridgeConfig, load_config
from projectbridge.input.github import GitHubAnalyzer
from projectbridge.input.job_description import parse_job_description
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


def run_analysis(
    *,
    job_text: str | None = None,
    github_user: str | None = None,
    github_token: str | None = None,
    resume_text: str | None = None,
    no_ai: bool = False,
    example: bool = False,
    no_cache: bool = False,
    progress: Progress | None = None,
    config: ProjectBridgeConfig | None = None,
) -> AnalysisResult:
    """Execute the complete analysis pipeline.

    Args:
        job_text: Raw job description text.
        github_user: GitHub username to analyze.
        github_token: GitHub personal access token (or read from env).
        resume_text: Optional plain-text resume for contextual enrichment.
        no_ai: Force the NoAI heuristic provider.
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
        provider_name = "none" if no_ai else config.ai.provider
        logger.info("Resolving AI provider: %s", provider_name)
        provider_kwargs: dict[str, Any] = {}
        if provider_name == "ollama":
            provider_kwargs["model"] = config.ai.ollama_model
        provider: AIProvider = get_provider(provider_name, **provider_kwargs)
    except Exception as exc:
        raise PipelineError("ai_provider", str(exc)) from exc

    # -- 2. Validate & gather inputs ----------------------------------------
    if example:
        logger.info("Using bundled example data")
        dev_context = EXAMPLE_DEV_CONTEXT
        job_text = EXAMPLE_JOB_DESCRIPTION
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
        job_reqs = parse_job_description(job_text).model_dump()
    except Exception as exc:
        raise PipelineError("job_parser", str(exc)) from exc

    # -- 5. AI context enrichment (optional) --------------------------------
    if provider_name != "none":
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

    # -- 7. Recommendations ------------------------------------------------
    progress.step("Generating recommendations...")
    logger.info("Generating recommendations")
    try:
        recs = generate_recommendations(
            analysis,
            provider,
            max_recommendations=config.analysis.max_recommendations,
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
    )
