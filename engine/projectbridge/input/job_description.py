"""Job description parser.

Extracts structured requirements from raw job description text:
required technologies, implied experience domains, and architectural
expectations. Handles bullet-list, prose-paragraph, and mixed formats.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Output model
# ---------------------------------------------------------------------------


class JobRequirements(BaseModel):
    """Normalized requirements extracted from a job description.

    Consumed by the analysis layer for gap detection.
    """

    required_technologies: list[str] = Field(
        description="Technologies, languages, and frameworks explicitly required.",
    )
    experience_domains: list[str] = Field(
        description="Implied domains of experience (e.g. 'frontend', 'cloud').",
    )
    architectural_expectations: list[str] = Field(
        description="Architectural patterns or practices expected (e.g. 'microservices', 'CI/CD').",  # noqa: E501
    )


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class JobDescriptionError(Exception):
    """Base exception for the job description parser."""


class EmptyJobDescriptionError(JobDescriptionError):
    """Raised when the job description is empty or whitespace-only."""


class NonTechnicalJobError(JobDescriptionError):
    """Raised when the job description does not appear to be for a technical role."""


# ---------------------------------------------------------------------------
# Technical role indicators — used for non-technical JD rejection
# ---------------------------------------------------------------------------

_TECHNICAL_ROLE_INDICATORS: set[str] = {
    "software",
    "developer",
    "engineer",
    "engineering",
    "devops",
    "data scientist",
    "data engineer",
    "architect",
    "sre",
    "site reliability",
    "backend",
    "frontend",
    "front-end",
    "back-end",
    "full-stack",
    "fullstack",
    "full stack",
    "machine learning",
    "cloud",
    "security engineer",
    "dba",
    "database administrator",
    "technical lead",
    "tech lead",
    "platform",
    "infrastructure",
    "programmer",
    "qa engineer",
    "test engineer",
    "embedded",
    "firmware",
}


# ---------------------------------------------------------------------------
# Known terms — used for keyword matching
# ---------------------------------------------------------------------------

TECHNOLOGY_KEYWORDS: dict[str, str] = {
    # Languages
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "c#": "C#",
    "c\\+\\+": "C++",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "scala": "Scala",
    "r": "R",
    "sql": "SQL",
    # Frontend
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "angular": "Angular",
    "vue": "Vue",
    "vuejs": "Vue",
    "vue.js": "Vue",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "nuxt": "Nuxt",
    "svelte": "Svelte",
    "html": "HTML",
    "css": "CSS",
    "sass": "Sass",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    # Backend
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "express": "Express",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",
    ".net": ".NET",
    "asp.net": "ASP.NET",
    # Data
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "kafka": "Kafka",
    "graphql": "GraphQL",
    "rest api": "REST API",
    "restful": "REST API",
    # Infrastructure
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "linux": "Linux",
    "nginx": "Nginx",
    # Tools
    "git": "Git",
    "webpack": "Webpack",
    "vite": "Vite",
    "jest": "Jest",
    "pytest": "pytest",
    "selenium": "Selenium",
    "redux": "Redux",
    "rabbitmq": "RabbitMQ",
}

DOMAIN_KEYWORDS: dict[str, str] = {
    "frontend": "frontend",
    "front-end": "frontend",
    "front end": "frontend",
    "backend": "backend",
    "back-end": "backend",
    "back end": "backend",
    "full-stack": "full-stack",
    "full stack": "full-stack",
    "fullstack": "full-stack",
    "devops": "devops",
    "dev ops": "devops",
    "cloud": "cloud",
    "cloud computing": "cloud",
    "machine learning": "machine learning",
    "ml": "machine learning",
    "data engineering": "data engineering",
    "data pipeline": "data engineering",
    "mobile": "mobile",
    "mobile development": "mobile",
    "security": "security",
    "cybersecurity": "security",
    "api development": "API development",
    "api design": "API development",
    "database": "database",
    "data modeling": "database",
    "testing": "testing",
    "qa": "testing",
    "quality assurance": "testing",
    "distributed systems": "distributed systems",
    "embedded": "embedded systems",
    "embedded systems": "embedded systems",
    "web development": "web development",
    "e-commerce": "e-commerce",
    "ecommerce": "e-commerce",
    "fintech": "fintech",
    "healthcare": "healthcare",
}

ARCHITECTURE_KEYWORDS: dict[str, str] = {
    "microservice": "microservices",
    "microservices": "microservices",
    "monolith": "monolith",
    "serverless": "serverless",
    "event-driven": "event-driven",
    "event driven": "event-driven",
    "ci/cd": "CI/CD",
    "ci cd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous deployment": "CI/CD",
    "test-driven": "TDD",
    "tdd": "TDD",
    "agile": "Agile",
    "scrum": "Scrum",
    "kanban": "Kanban",
    "rest": "REST",
    "restful": "REST",
    "graphql": "GraphQL",
    "soa": "SOA",
    "service-oriented": "SOA",
    "mvp": "MVP",
    "mvc": "MVC",
    "mvvm": "MVVM",
    "single page application": "SPA",
    "spa": "SPA",
    "ssr": "SSR",
    "server-side rendering": "SSR",
    "containerization": "containerization",
    "infrastructure as code": "infrastructure as code",
    "iac": "infrastructure as code",
    "observability": "observability",
    "monitoring": "observability",
    "load balancing": "load balancing",
    "caching": "caching",
    "message queue": "message queues",
    "message queues": "message queues",
    "api gateway": "API gateway",
}


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def _match_keywords(text: str, keywords: dict[str, str]) -> list[str]:
    """Match keywords in *text*, returning deduplicated canonical names."""
    found: dict[str, None] = {}  # preserve insertion order, deduplicate
    lower = text.lower()
    # Sort by length descending so longer phrases match first (e.g. "spring boot" before "spring").
    for pattern, canonical in sorted(keywords.items(), key=lambda kv: len(kv[0]), reverse=True):
        # Word-boundary match to avoid false positives (e.g. "go" inside "google").
        if re.search(rf"\b{re.escape(pattern)}\b", lower):
            if canonical not in found:
                found[canonical] = None
    return list(found)


def parse_job_description(text: str) -> JobRequirements:
    """Parse a plain-text job description into structured requirements.

    Args:
        text: Raw job description text in any common format
            (bullet lists, paragraphs, or mixed).

    Returns:
        A :class:`JobRequirements` with extracted technologies, domains,
        and architectural expectations.

    Raises:
        EmptyJobDescriptionError: If *text* is empty or whitespace-only.
    """
    if not text or not text.strip():
        raise EmptyJobDescriptionError(
            "Job description is empty. Provide a non-empty job description."
        )

    return JobRequirements(
        required_technologies=_match_keywords(text, TECHNOLOGY_KEYWORDS),
        experience_domains=_match_keywords(text, DOMAIN_KEYWORDS),
        architectural_expectations=_match_keywords(text, ARCHITECTURE_KEYWORDS),
    )


def validate_technical_content(text: str, job_reqs: JobRequirements) -> None:
    """Validate that a job description is for a technical role.

    Args:
        text: Raw job description text.
        job_reqs: Already-parsed :class:`JobRequirements`.

    Raises:
        NonTechnicalJobError: If no technical signals are detected.
    """
    if job_reqs.required_technologies:
        return

    lower = text.lower()
    for indicator in _TECHNICAL_ROLE_INDICATORS:
        if indicator in lower:
            return

    raise NonTechnicalJobError(
        "No technical skills detected in this job description. "
        "ProjectBridge analyzes technical roles — software engineers, "
        "architects, data scientists, DevOps engineers, and similar positions."
    )
