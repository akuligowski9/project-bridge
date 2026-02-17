"""ProjectBridge command-line interface.

Primary user-facing entry point. The CLI contract must remain stable
across versions as it is the interface the Tauri UI will call.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from projectbridge import __version__
from projectbridge.export import create_snapshot, render_markdown, render_project_spec
from projectbridge.orchestrator import PipelineError, run_analysis
from projectbridge.progress import Progress
from projectbridge.schema import AnalysisResult


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="projectbridge",
        description="AI-powered skill-gap analysis for developers.",
    )
    parser.add_argument("--version", action="version", version=f"projectbridge {__version__}")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable verbose (DEBUG) log output.",
    )

    sub = parser.add_subparsers(dest="command")

    # -- analyze ------------------------------------------------------------
    analyze = sub.add_parser("analyze", help="Run a skill-gap analysis.")
    analyze.add_argument(
        "--job",
        metavar="FILE",
        help="Path to a plain-text job description file.",
    )
    analyze.add_argument(
        "--job-text",
        metavar="TEXT",
        help="Job description as inline text (alternative to --job).",
    )
    analyze.add_argument(
        "--github-user",
        metavar="USERNAME",
        help="GitHub username to analyze.",
    )
    analyze.add_argument(
        "--local-repos",
        nargs="+",
        metavar="DIR",
        help="Local repository directories to scan (alternative to --github-user).",
    )
    analyze.add_argument(
        "--output",
        metavar="FILE",
        help="Write JSON output to FILE instead of stdout.",
    )
    analyze.add_argument(
        "--resume",
        metavar="FILE",
        help="Path to a plain-text resume file (optional enrichment).",
    )
    analyze.add_argument(
        "--resume-text",
        metavar="TEXT",
        help="Resume as inline text (alternative to --resume).",
    )
    analyze.add_argument(
        "--no-ai",
        action="store_true",
        default=False,
        help="Use heuristic recommendations only (no AI provider).",
    )
    analyze.add_argument(
        "--provider",
        choices=["none", "openai", "anthropic", "ollama"],
        default=None,
        help="AI provider to use. Overrides config file. 'none' = heuristic only.",
    )
    analyze.add_argument(
        "--no-cache",
        action="store_true",
        default=False,
        help="Bypass cached GitHub API responses and fetch fresh data.",
    )
    analyze.add_argument(
        "--example",
        action="store_true",
        default=False,
        help="Run with bundled example data (no setup required).",
    )

    # -- export -------------------------------------------------------------
    export = sub.add_parser("export", help="Export an analysis result.")
    export.add_argument(
        "--input",
        metavar="FILE",
        help="Path to a JSON analysis result file.",
    )
    export.add_argument(
        "--output",
        metavar="FILE",
        help="Write export to FILE instead of stdout.",
    )
    export.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Export format (default: json).",
    )
    export.add_argument(
        "--example",
        action="store_true",
        default=False,
        help="Export from bundled example data.",
    )

    # -- export-project -----------------------------------------------------
    export_proj = sub.add_parser(
        "export-project",
        help="Generate a rich project spec from a recommendation.",
    )
    export_proj.add_argument(
        "--input",
        metavar="FILE",
        help="Path to a JSON analysis result file.",
    )
    export_proj.add_argument(
        "--example",
        action="store_true",
        default=False,
        help="Use bundled example data.",
    )
    export_proj.add_argument(
        "--recommendation",
        type=int,
        required=True,
        metavar="N",
        help="1-based index of the recommendation to expand.",
    )
    export_proj.add_argument(
        "--difficulty",
        required=True,
        choices=["beginner", "intermediate", "advanced"],
        help="Difficulty tier for the project spec.",
    )
    export_proj.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format (default: markdown).",
    )
    export_proj.add_argument(
        "--output",
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    export_proj.add_argument(
        "--no-ai",
        action="store_true",
        default=False,
        help="Use heuristic generation only (no AI provider).",
    )

    return parser


def _configure_logging(verbose: bool) -> None:
    """Set up root logging for the projectbridge namespace."""
    level = logging.DEBUG if verbose else logging.WARNING
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger("projectbridge")
    root.setLevel(level)
    root.addHandler(handler)


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns an exit code (0 = success)."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    _configure_logging(getattr(args, "verbose", False))

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "analyze":
        return _cmd_analyze(args)

    if args.command == "export":
        return _cmd_export(args)

    if args.command == "export-project":
        return _cmd_export_project(args)

    parser.print_help()
    return 1


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def _cmd_analyze(args: argparse.Namespace) -> int:
    if args.github_user and args.local_repos:
        print("Error: --github-user and --local-repos are mutually exclusive.", file=sys.stderr)
        return 1

    job_text: str | None = None
    if args.job and args.job_text:
        print("Error: --job and --job-text are mutually exclusive.", file=sys.stderr)
        return 1
    if args.job:
        path = Path(args.job)
        if not path.is_file():
            print(f"Error: job description file not found: {args.job}", file=sys.stderr)
            return 1
        job_text = path.read_text()
    elif args.job_text:
        job_text = args.job_text

    resume_text: str | None = None
    if args.resume and args.resume_text:
        print("Error: --resume and --resume-text are mutually exclusive.", file=sys.stderr)
        return 1
    if args.resume:
        path = Path(args.resume)
        if not path.is_file():
            print(f"Error: resume file not found: {args.resume}", file=sys.stderr)
            return 1
        resume_text = path.read_text()
    elif args.resume_text:
        resume_text = args.resume_text

    try:
        result = run_analysis(
            job_text=job_text,
            github_user=args.github_user,
            local_repos=args.local_repos,
            resume_text=resume_text,
            no_ai=args.no_ai,
            provider_name=args.provider,
            example=args.example,
            no_cache=args.no_cache,
            progress=Progress(),
        )
    except PipelineError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        logging.getLogger(__name__).debug("Unhandled exception", exc_info=True)
        print(f"Error: An unexpected error occurred: {exc}", file=sys.stderr)
        return 1

    output_json = result.model_dump_json(indent=2)

    if args.output:
        Path(args.output).write_text(output_json + "\n")
    else:
        print(output_json)

    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    if args.example:
        try:
            result = run_analysis(example=True, no_ai=True)
        except PipelineError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    elif args.input:
        path = Path(args.input)
        if not path.is_file():
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            return 1
        try:
            result = AnalysisResult.model_validate_json(path.read_text())
        except Exception as exc:
            print(f"Error: invalid analysis result: {exc}", file=sys.stderr)
            return 1
    else:
        print("Error: provide --input FILE or --example.", file=sys.stderr)
        return 1

    if args.format == "markdown":
        output_text = render_markdown(result)
    else:
        snapshot = create_snapshot(result)
        output_text = snapshot.model_dump_json(indent=2) + "\n"

    if args.output:
        Path(args.output).write_text(output_text)
    else:
        print(output_text, end="")

    return 0


def _cmd_export_project(args: argparse.Namespace) -> int:
    if args.example:
        try:
            result = run_analysis(example=True, no_ai=True)
        except PipelineError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    elif args.input:
        path = Path(args.input)
        if not path.is_file():
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            return 1
        try:
            result = AnalysisResult.model_validate_json(path.read_text())
        except Exception as exc:
            print(f"Error: invalid analysis result: {exc}", file=sys.stderr)
            return 1
    else:
        print("Error: provide --input FILE or --example.", file=sys.stderr)
        return 1

    idx = args.recommendation - 1
    if idx < 0 or idx >= len(result.recommendations):
        print(
            f"Error: recommendation index {args.recommendation} out of range "
            f"(1-{len(result.recommendations)}).",
            file=sys.stderr,
        )
        return 1

    recommendation = result.recommendations[idx]

    # Resolve AI provider.
    from projectbridge.ai.provider import get_provider
    from projectbridge.config.settings import load_config

    config = load_config()
    provider_name = "none" if args.no_ai else config.ai.provider
    try:
        provider = get_provider(provider_name)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    from projectbridge.export_project import generate_project_spec

    try:
        spec = generate_project_spec(recommendation, args.difficulty, result, provider)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        output_text = spec.model_dump_json(indent=2) + "\n"
    else:
        output_text = render_project_spec(spec)

    if args.output:
        Path(args.output).write_text(output_text)
    else:
        print(output_text, end="")

    return 0


def cli() -> None:
    """Console script entry point."""
    sys.exit(main())


if __name__ == "__main__":
    cli()
