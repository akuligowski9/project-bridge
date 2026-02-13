"""Interview topic data and lookup.

Maps popular technologies to 2-3 common interview topics so
developers know what to study for gap skills.
"""

from __future__ import annotations

INTERVIEW_TOPICS: dict[str, list[str]] = {
    # Languages
    "Python": [
        "Decorators, generators, and context managers",
        "Memory management and the GIL",
        "Type hints and static analysis tooling",
    ],
    "JavaScript": [
        "Closures, prototypes, and the event loop",
        "Promises, async/await, and error handling",
        "Module systems (ESM vs CommonJS)",
    ],
    "TypeScript": [
        "Generic types and utility types",
        "Type narrowing and discriminated unions",
        "Declaration files and module augmentation",
    ],
    "Java": [
        "JVM memory model and garbage collection",
        "Concurrency with threads and executors",
        "Generics, type erasure, and bounded types",
    ],
    "Go": [
        "Goroutines, channels, and concurrency patterns",
        "Interfaces and composition over inheritance",
        "Error handling conventions and wrapping",
    ],
    "Rust": [
        "Ownership, borrowing, and lifetimes",
        "Pattern matching and error handling with Result/Option",
        "Trait objects vs generics",
    ],
    "C#": [
        "Async/await and the Task Parallel Library",
        "LINQ and expression trees",
        "Value types vs reference types and boxing",
    ],
    "Ruby": [
        "Blocks, procs, and lambdas",
        "Metaprogramming and method_missing",
        "Module mixins and the Ruby object model",
    ],
    "Kotlin": [
        "Null safety and smart casts",
        "Coroutines and structured concurrency",
        "Data classes and sealed classes",
    ],
    "Swift": [
        "Optionals and nil coalescing",
        "Protocol-oriented programming",
        "Memory management with ARC",
    ],
    "Scala": [
        "Pattern matching and case classes",
        "Implicits and type classes",
        "Functional programming with monads",
    ],
    # Frontend
    "React": [
        "Component lifecycle and hooks",
        "State management patterns (Context, Redux)",
        "Performance optimization and memoization",
    ],
    "Angular": [
        "Dependency injection and modules",
        "RxJS observables and operators",
        "Change detection strategies",
    ],
    "Vue": [
        "Reactivity system and computed properties",
        "Composition API vs Options API",
        "Vue Router and Vuex/Pinia state management",
    ],
    "Svelte": [
        "Reactivity declarations and stores",
        "Component lifecycle and transitions",
        "SvelteKit routing and server-side rendering",
    ],
    "Next.js": [
        "Server-side rendering vs static generation",
        "API routes and middleware",
        "Image optimization and incremental static regeneration",
    ],
    # Backend
    "Django": [
        "ORM query optimization and N+1 problems",
        "Middleware pipeline and request lifecycle",
        "Django REST Framework serializers and viewsets",
    ],
    "Flask": [
        "Application factory pattern and blueprints",
        "Request context and application context",
        "Extension ecosystem and middleware",
    ],
    "FastAPI": [
        "Dependency injection system",
        "Async endpoint patterns and background tasks",
        "Pydantic model validation and serialization",
    ],
    "Spring Boot": [
        "Dependency injection and IoC container",
        "Spring Security and filter chains",
        "JPA/Hibernate and transaction management",
    ],
    "Node.js": [
        "Event loop and non-blocking I/O",
        "Stream processing and backpressure",
        "Cluster module and worker threads",
    ],
    "Express": [
        "Middleware pattern and execution order",
        "Error handling middleware",
        "Route parameter validation and sanitization",
    ],
    # Data
    "PostgreSQL": [
        "Query optimization and EXPLAIN plans",
        "Indexing strategies (B-tree, GIN, GiST)",
        "Transaction isolation levels",
    ],
    "MySQL": [
        "InnoDB vs MyISAM storage engines",
        "Query optimization and index selection",
        "Replication and high availability",
    ],
    "MongoDB": [
        "Document modeling and schema design",
        "Aggregation pipeline stages",
        "Indexing strategies and query profiling",
    ],
    "Redis": [
        "Data structures and use cases for each type",
        "Persistence strategies (RDB vs AOF)",
        "Pub/Sub and Lua scripting",
    ],
    "Elasticsearch": [
        "Inverted index and text analysis",
        "Query DSL and relevance scoring",
        "Sharding and cluster management",
    ],
    "GraphQL": [
        "Schema design and type system",
        "N+1 query problem and DataLoader",
        "Subscriptions and real-time updates",
    ],
    "Kafka": [
        "Partitioning and consumer groups",
        "Exactly-once semantics and idempotency",
        "Schema registry and data evolution",
    ],
    # Infrastructure
    "Docker": [
        "Dockerfile optimization and multi-stage builds",
        "Container networking and volume management",
        "Docker Compose for multi-service applications",
    ],
    "Kubernetes": [
        "Pod lifecycle and deployment strategies",
        "Services, ingress, and networking",
        "Resource limits, requests, and horizontal scaling",
    ],
    "AWS": [
        "IAM policies and least-privilege access",
        "VPC networking and security groups",
        "S3, Lambda, and serverless patterns",
    ],
    "Terraform": [
        "State management and remote backends",
        "Module composition and reuse",
        "Plan/apply workflow and drift detection",
    ],
    "CI/CD": [
        "Pipeline stages and artifact management",
        "Testing strategies in CI (unit, integration, E2E)",
        "Deployment strategies (blue-green, canary, rolling)",
    ],
    "Linux": [
        "Process management and signals",
        "File permissions and systemd services",
        "Shell scripting and cron jobs",
    ],
}

# Build a case-insensitive lookup.
_LOOKUP: dict[str, list[str]] = {k.lower(): v for k, v in INTERVIEW_TOPICS.items()}


def get_interview_topics(skill_name: str) -> list[str]:
    """Return interview topics for a skill (case-insensitive).

    Args:
        skill_name: Skill name to look up.

    Returns:
        A list of 2-3 topic strings, or ``[]`` if not found.
    """
    return _LOOKUP.get(skill_name.lower(), [])
