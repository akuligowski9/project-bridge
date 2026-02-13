"""Portfolio gap insight generation.

Surfaces actionable insights about underrepresented areas in a
developer's portfolio relative to the target role.
"""

from __future__ import annotations

from typing import Any


def derive_portfolio_insights(
    dev_context: dict[str, Any],
    job_reqs: dict[str, Any],
    analysis: dict[str, list],
) -> list[dict[str, str]]:
    """Generate portfolio insights from the analysis context.

    Args:
        dev_context: Developer context from GitHub analyzer / resume merge.
        job_reqs: Parsed job requirements dict.
        analysis: Analysis result with ``detected_skills``, ``missing_skills``,
            ``adjacent_skills``.

    Returns:
        Up to 3 insight dicts with ``category`` and ``message`` keys.
    """
    insights: list[dict[str, str]] = []

    # -- Category balance --------------------------------------------------
    has_languages = bool(dev_context.get("languages"))
    has_frameworks = bool(dev_context.get("frameworks"))
    has_infra = bool(dev_context.get("infrastructure_signals"))

    present = [
        name
        for name, flag in [
            ("languages", has_languages),
            ("frameworks", has_frameworks),
            ("infrastructure", has_infra),
        ]
        if flag
    ]
    absent = [
        name
        for name, flag in [
            ("languages", has_languages),
            ("frameworks", has_frameworks),
            ("infrastructure", has_infra),
        ]
        if not flag
    ]

    if len(present) == 1 and absent:
        insights.append(
            {
                "category": "balance",
                "message": (
                    f"Your portfolio is heavily weighted toward {present[0]}. "
                    f"Adding projects that demonstrate {', '.join(absent)} "
                    f"will show broader capability."
                ),
            }
        )

    # -- Infrastructure gap ------------------------------------------------
    job_techs_lower = {t.lower() for t in job_reqs.get("required_technologies", [])}
    infra_keywords = {"docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ansible"}
    job_needs_infra = bool(job_techs_lower & infra_keywords)

    if job_needs_infra and not has_infra:
        insights.append(
            {
                "category": "infrastructure",
                "message": (
                    "Your portfolio doesn't demonstrate deployment or "
                    "infrastructure skills. Even a simple Docker + CI setup "
                    "on an existing project fills this gap."
                ),
            }
        )

    # -- Missing domains ---------------------------------------------------
    job_domains = set(job_reqs.get("experience_domains", []))
    dev_domains: set[str] = set()
    # resume might carry domain info
    for skill_name in dev_context.get("resume_skills", []):
        dev_domains.add(skill_name.lower())
    # infer from infra / frameworks
    for item in dev_context.get("frameworks", []):
        dev_domains.add(item["name"].lower())

    missing_domains = job_domains - dev_domains
    if missing_domains and len(insights) < 3:
        sample = ", ".join(sorted(missing_domains)[:3])
        insights.append(
            {
                "category": "domain",
                "message": (
                    f"The target role values {sample} experience. "
                    f"Consider projects in "
                    f"{'this domain' if len(missing_domains) == 1 else 'these domains'}"
                    f" even if you use familiar technologies."
                ),
            }
        )

    # -- Depth vs breadth --------------------------------------------------
    langs = dev_context.get("languages", [])
    if len(langs) >= 5 and len(insights) < 3:
        high_pct = [lang for lang in langs if lang.get("percentage", 0) >= 20]
        if len(high_pct) <= 1:
            insights.append(
                {
                    "category": "depth",
                    "message": (
                        "Consider deepening expertise in one or two areas "
                        "rather than spreading thin."
                    ),
                }
            )

    return insights[:3]
