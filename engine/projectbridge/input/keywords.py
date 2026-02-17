"""Shared keyword dictionaries and matcher.

Used by both the job description parser and the resume parser to
extract technologies, domains, and architectural patterns from text.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Technology keywords — languages, frameworks, databases, tools
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

# ---------------------------------------------------------------------------
# Domain keywords — experience areas
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Architecture keywords — patterns and practices
# ---------------------------------------------------------------------------

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
# Shared matcher
# ---------------------------------------------------------------------------


def match_keywords(text: str, keywords: dict[str, str]) -> list[str]:
    """Match keywords in *text*, returning deduplicated canonical names.

    Keywords are sorted by length descending so longer phrases match first
    (e.g. "spring boot" before "spring"). Word-boundary matching avoids
    false positives (e.g. "go" inside "google").
    """
    found: dict[str, None] = {}  # preserve insertion order, deduplicate
    lower = text.lower()
    for pattern, canonical in sorted(keywords.items(), key=lambda kv: len(kv[0]), reverse=True):
        if re.search(rf"\b{re.escape(pattern)}\b", lower):
            if canonical not in found:
                found[canonical] = None
    return list(found)
