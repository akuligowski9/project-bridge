"""ProjectBridge command-line interface.

Primary user-facing entry point. The CLI contract must remain stable
across versions as it is the interface the Tauri UI will call.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from projectbridge import __version__
from projectbridge.export import create_snapshot
from projectbridge.orchestrator import PipelineError, run_analysis
from projectbridge.schema import AnalysisResult


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="projectbridge",
        description="AI-powered skill-gap analysis for developers.",
    )
    parser.add_argument(
        "--version", action="version", version=f"projectbridge {__version__}"
    )
    parser.add_argument(
        "--verbose", "-v",
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
        "--github-user",
        metavar="USERNAME",
        help="GitHub username to analyze.",
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
        "--no-ai",
        action="store_true",
        default=False,
        help="Use heuristic recommendations only (no AI provider).",
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
        choices=["json"],
        default="json",
        help="Export format (default: json).",
    )
    export.add_argument(
        "--example",
        action="store_true",
        default=False,
        help="Export from bundled example data.",
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

    parser.print_help()
    return 1


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _cmd_analyze(args: argparse.Namespace) -> int:
    job_text: str | None = None
    if args.job:
        path = Path(args.job)
        if not path.is_file():
            print(f"Error: job description file not found: {args.job}", file=sys.stderr)
            return 1
        job_text = path.read_text()

    resume_text: str | None = None
    if args.resume:
        path = Path(args.resume)
        if not path.is_file():
            print(f"Error: resume file not found: {args.resume}", file=sys.stderr)
            return 1
        resume_text = path.read_text()

    try:
        result = run_analysis(
            job_text=job_text,
            github_user=args.github_user,
            resume_text=resume_text,
            no_ai=args.no_ai,
            example=args.example,
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

    snapshot = create_snapshot(result)
    output_json = snapshot.model_dump_json(indent=2)

    if args.output:
        Path(args.output).write_text(output_json + "\n")
    else:
        print(output_json)

    return 0


def cli() -> None:
    """Console script entry point."""
    sys.exit(main())


if __name__ == "__main__":
    cli()
