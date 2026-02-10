"""Shared test fixtures for ProjectBridge engine tests."""

from __future__ import annotations

import base64
import json
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Sample developer context (mirrors orchestrator.EXAMPLE_DEV_CONTEXT)
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_dev_context() -> dict[str, Any]:
    return {
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


# ---------------------------------------------------------------------------
# Sample job descriptions
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_job_text() -> str:
    return """\
Senior Full-Stack Engineer

Requirements:
- 4+ years with Python and TypeScript
- Experience with Django or FastAPI
- Proficiency with React
- Experience with PostgreSQL and Redis
- Docker, Kubernetes, and CI/CD pipelines
- Microservices architecture and RESTful API design
- AWS experience preferred
"""


@pytest.fixture()
def sample_job_text_prose() -> str:
    return """\
We are looking for a backend engineer with deep experience in Java and
Spring Boot. The ideal candidate has worked with cloud infrastructure on
GCP, is comfortable with Docker, and has built event-driven systems.
Experience with Kafka and MongoDB is a plus.
"""


# ---------------------------------------------------------------------------
# Sample resume text
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_resume_text() -> str:
    return """\
Jane Smith — Software Engineer

8+ years of professional experience in backend and cloud development.

Skills: Python, Java, PostgreSQL, Redis, Docker, Kubernetes, AWS
Experience with Django, FastAPI, and microservices architecture.
Previously worked in fintech and healthcare domains.
"""


# ---------------------------------------------------------------------------
# Mock GitHub API responses
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_github_repos() -> list[dict[str, Any]]:
    return [
        {
            "name": "my-app",
            "owner": {"login": "testuser"},
            "fork": False,
        },
        {
            "name": "forked-lib",
            "owner": {"login": "testuser"},
            "fork": True,
        },
    ]


@pytest.fixture()
def mock_github_languages() -> dict[str, int]:
    return {"Python": 5000, "JavaScript": 3000}


@pytest.fixture()
def mock_github_contents() -> list[dict[str, Any]]:
    return [
        {"name": "src", "path": "src", "type": "dir"},
        {"name": "Dockerfile", "path": "Dockerfile", "type": "file"},
        {"name": "package.json", "path": "package.json", "type": "file"},
        {"name": "requirements.txt", "path": "requirements.txt", "type": "file"},
    ]


@pytest.fixture()
def mock_package_json() -> dict[str, str]:
    content = base64.b64encode(
        json.dumps({"dependencies": {"react": "^18.0.0", "express": "^4.0.0"}}).encode()
    ).decode()
    return {"content": content}


@pytest.fixture()
def mock_requirements_txt() -> dict[str, str]:
    content = base64.b64encode(b"django==4.2\ncelery==5.3\n").decode()
    return {"content": content}


@pytest.fixture()
def mock_github_response(
    mock_github_repos,
    mock_github_languages,
    mock_github_contents,
    mock_package_json,
    mock_requirements_txt,
):
    """Return a side_effect function that simulates the GitHub API."""

    def side_effect(path: str):
        if "/repos?per_page" in path:
            return mock_github_repos
        if "/languages" in path:
            return mock_github_languages
        if "/contents/package.json" in path:
            return mock_package_json
        if "/contents/requirements.txt" in path:
            return mock_requirements_txt
        if "/contents/" in path:
            return mock_github_contents
        return mock_github_contents

    return side_effect
