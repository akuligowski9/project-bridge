"""Skill taxonomy and adjacency map.

Data-driven mapping of skills to categories and adjacency relationships.
Adding a new skill requires only data changes — no code changes needed.
"""

from __future__ import annotations

from projectbridge.schema import SkillCategory

# ---------------------------------------------------------------------------
# Taxonomy: skill_name → (category, [adjacent_skill_names])
#
# Adjacency represents natural growth paths — skills that are related
# to what a developer already knows and would be logical next steps.
# ---------------------------------------------------------------------------

TAXONOMY: dict[str, tuple[SkillCategory, list[str]]] = {
    # --- Languages ---------------------------------------------------------
    "Python": (
        SkillCategory.LANGUAGE,
        [
            "Django",
            "Flask",
            "FastAPI",
            "pytest",
            "Celery",
            "NumPy",
            "Pandas",
        ],
    ),
    "JavaScript": (
        SkillCategory.LANGUAGE,
        [
            "TypeScript",
            "React",
            "Vue",
            "Angular",
            "Node.js",
            "Express",
        ],
    ),
    "TypeScript": (
        SkillCategory.LANGUAGE,
        [
            "JavaScript",
            "React",
            "Angular",
            "Node.js",
            "Next.js",
        ],
    ),
    "Java": (
        SkillCategory.LANGUAGE,
        [
            "Spring",
            "Spring Boot",
            "Kotlin",
            "Maven",
            "Gradle",
        ],
    ),
    "C#": (
        SkillCategory.LANGUAGE,
        [
            ".NET",
            "ASP.NET",
            "Azure",
        ],
    ),
    "C++": (
        SkillCategory.LANGUAGE,
        [
            "Rust",
            "CMake",
        ],
    ),
    "Go": (
        SkillCategory.LANGUAGE,
        [
            "Docker",
            "Kubernetes",
            "gRPC",
            "Protobuf",
        ],
    ),
    "Rust": (
        SkillCategory.LANGUAGE,
        [
            "C++",
            "WebAssembly",
        ],
    ),
    "Ruby": (
        SkillCategory.LANGUAGE,
        [
            "Ruby on Rails",
            "RSpec",
        ],
    ),
    "PHP": (
        SkillCategory.LANGUAGE,
        [
            "Laravel",
            "WordPress",
        ],
    ),
    "Swift": (
        SkillCategory.LANGUAGE,
        [
            "iOS",
            "Xcode",
        ],
    ),
    "Kotlin": (
        SkillCategory.LANGUAGE,
        [
            "Java",
            "Android",
            "Spring Boot",
        ],
    ),
    "Scala": (
        SkillCategory.LANGUAGE,
        [
            "Java",
            "Apache Spark",
            "Kafka",
        ],
    ),
    "R": (
        SkillCategory.LANGUAGE,
        [
            "Python",
            "NumPy",
            "Pandas",
        ],
    ),
    "SQL": (
        SkillCategory.LANGUAGE,
        [
            "PostgreSQL",
            "MySQL",
            "SQLite",
        ],
    ),
    "HTML": (
        SkillCategory.LANGUAGE,
        [
            "CSS",
            "JavaScript",
            "React",
        ],
    ),
    "CSS": (
        SkillCategory.LANGUAGE,
        [
            "HTML",
            "Sass",
            "Tailwind CSS",
        ],
    ),
    # --- Frontend Frameworks -----------------------------------------------
    "React": (
        SkillCategory.FRAMEWORK,
        [
            "Next.js",
            "Redux",
            "TypeScript",
            "React Native",
            "Vite",
        ],
    ),
    "Vue": (
        SkillCategory.FRAMEWORK,
        [
            "Nuxt",
            "Vuex",
            "TypeScript",
            "Vite",
        ],
    ),
    "Angular": (
        SkillCategory.FRAMEWORK,
        [
            "TypeScript",
            "RxJS",
            "NgRx",
        ],
    ),
    "Next.js": (
        SkillCategory.FRAMEWORK,
        [
            "React",
            "TypeScript",
            "Vercel",
        ],
    ),
    "Nuxt": (
        SkillCategory.FRAMEWORK,
        [
            "Vue",
            "TypeScript",
        ],
    ),
    "Svelte": (
        SkillCategory.FRAMEWORK,
        [
            "TypeScript",
            "Vite",
        ],
    ),
    # --- Backend Frameworks ------------------------------------------------
    "Django": (
        SkillCategory.FRAMEWORK,
        [
            "Python",
            "PostgreSQL",
            "Celery",
            "Django REST Framework",
        ],
    ),
    "Flask": (
        SkillCategory.FRAMEWORK,
        [
            "Python",
            "SQLAlchemy",
            "Celery",
        ],
    ),
    "FastAPI": (
        SkillCategory.FRAMEWORK,
        [
            "Python",
            "Pydantic",
            "SQLAlchemy",
        ],
    ),
    "Express": (
        SkillCategory.FRAMEWORK,
        [
            "Node.js",
            "JavaScript",
            "TypeScript",
            "MongoDB",
        ],
    ),
    "Spring": (
        SkillCategory.FRAMEWORK,
        [
            "Java",
            "Spring Boot",
            "Maven",
        ],
    ),
    "Spring Boot": (
        SkillCategory.FRAMEWORK,
        [
            "Java",
            "Spring",
            "Kotlin",
            "Maven",
            "Gradle",
        ],
    ),
    "Ruby on Rails": (
        SkillCategory.FRAMEWORK,
        [
            "Ruby",
            "PostgreSQL",
            "Redis",
        ],
    ),
    ".NET": (
        SkillCategory.FRAMEWORK,
        [
            "C#",
            "ASP.NET",
            "Azure",
        ],
    ),
    "ASP.NET": (
        SkillCategory.FRAMEWORK,
        [
            "C#",
            ".NET",
            "Azure",
        ],
    ),
    "Laravel": (
        SkillCategory.FRAMEWORK,
        [
            "PHP",
            "MySQL",
        ],
    ),
    "Node.js": (
        SkillCategory.FRAMEWORK,
        [
            "JavaScript",
            "TypeScript",
            "Express",
            "Fastify",
        ],
    ),
    "Fastify": (
        SkillCategory.FRAMEWORK,
        [
            "Node.js",
            "TypeScript",
        ],
    ),
    # --- Databases ---------------------------------------------------------
    "PostgreSQL": (
        SkillCategory.INFRASTRUCTURE,
        [
            "SQL",
            "Redis",
            "Django",
        ],
    ),
    "MySQL": (
        SkillCategory.INFRASTRUCTURE,
        [
            "SQL",
            "PHP",
            "Laravel",
        ],
    ),
    "MongoDB": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Node.js",
            "Express",
            "Mongoose",
        ],
    ),
    "Redis": (
        SkillCategory.INFRASTRUCTURE,
        [
            "PostgreSQL",
            "Celery",
            "Caching",
        ],
    ),
    "SQLite": (
        SkillCategory.INFRASTRUCTURE,
        [
            "SQL",
            "Python",
        ],
    ),
    "Elasticsearch": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Kibana",
            "Logstash",
        ],
    ),
    # --- Infrastructure & DevOps -------------------------------------------
    "Docker": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Kubernetes",
            "Docker Compose",
            "CI/CD",
        ],
    ),
    "Docker Compose": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Docker",
            "Kubernetes",
        ],
    ),
    "Kubernetes": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Docker",
            "Helm",
            "Terraform",
            "AWS",
        ],
    ),
    "Terraform": (
        SkillCategory.INFRASTRUCTURE,
        [
            "AWS",
            "GCP",
            "Azure",
            "Kubernetes",
        ],
    ),
    "AWS": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Terraform",
            "Docker",
            "Kubernetes",
            "Lambda",
        ],
    ),
    "GCP": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Terraform",
            "Docker",
            "Kubernetes",
        ],
    ),
    "Azure": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Terraform",
            ".NET",
            "C#",
        ],
    ),
    "GitHub Actions": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Docker",
            "CI/CD",
            "Git",
        ],
    ),
    "GitLab CI": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Docker",
            "CI/CD",
            "Git",
        ],
    ),
    "Jenkins": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Docker",
            "CI/CD",
            "Groovy",
        ],
    ),
    "Ansible": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Terraform",
            "Linux",
            "Docker",
        ],
    ),
    "Nginx": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Linux",
            "Docker",
            "Load Balancing",
        ],
    ),
    "Linux": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Docker",
            "Bash",
            "Nginx",
        ],
    ),
    "Helm": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Kubernetes",
            "Docker",
        ],
    ),
    # --- Messaging & Streaming ---------------------------------------------
    "Kafka": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Event-Driven Architecture",
            "Microservices",
            "Java",
        ],
    ),
    "RabbitMQ": (
        SkillCategory.INFRASTRUCTURE,
        [
            "Microservices",
            "Celery",
            "Event-Driven Architecture",
        ],
    ),
    # --- Tools -------------------------------------------------------------
    "Git": (
        SkillCategory.TOOL,
        [
            "GitHub Actions",
            "GitLab CI",
        ],
    ),
    "Webpack": (
        SkillCategory.TOOL,
        [
            "JavaScript",
            "React",
            "Vite",
        ],
    ),
    "Vite": (
        SkillCategory.TOOL,
        [
            "React",
            "Vue",
            "Svelte",
        ],
    ),
    "Jest": (
        SkillCategory.TOOL,
        [
            "JavaScript",
            "React",
            "TypeScript",
        ],
    ),
    "pytest": (
        SkillCategory.TOOL,
        [
            "Python",
            "Django",
            "Flask",
        ],
    ),
    "Selenium": (
        SkillCategory.TOOL,
        [
            "Testing",
            "Python",
            "JavaScript",
        ],
    ),
    "Redux": (
        SkillCategory.TOOL,
        [
            "React",
            "TypeScript",
        ],
    ),
    "GraphQL": (
        SkillCategory.TOOL,
        [
            "React",
            "Apollo",
            "Node.js",
        ],
    ),
    "REST API": (
        SkillCategory.TOOL,
        [
            "Express",
            "Django",
            "FastAPI",
        ],
    ),
    "Celery": (
        SkillCategory.TOOL,
        [
            "Python",
            "Redis",
            "RabbitMQ",
        ],
    ),
    "Sass": (
        SkillCategory.TOOL,
        [
            "CSS",
            "Tailwind CSS",
        ],
    ),
    "Tailwind CSS": (
        SkillCategory.TOOL,
        [
            "CSS",
            "React",
            "Vue",
        ],
    ),
    "NumPy": (
        SkillCategory.TOOL,
        [
            "Python",
            "Pandas",
            "SciPy",
        ],
    ),
    "Pandas": (
        SkillCategory.TOOL,
        [
            "Python",
            "NumPy",
            "SQL",
        ],
    ),
}


def get_category(skill_name: str) -> SkillCategory | None:
    """Return the category for a known skill, or ``None``."""
    entry = TAXONOMY.get(skill_name)
    return entry[0] if entry else None


def get_adjacent(skill_name: str) -> list[str]:
    """Return adjacent skills for *skill_name*, or ``[]``."""
    entry = TAXONOMY.get(skill_name)
    return list(entry[1]) if entry else []


def is_known(skill_name: str) -> bool:
    """Return whether *skill_name* is in the taxonomy."""
    return skill_name in TAXONOMY
