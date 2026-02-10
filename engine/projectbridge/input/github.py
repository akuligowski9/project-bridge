"""GitHub repository analyzer.

Primary input processor that extracts signals from a user's GitHub
repositories using the GitHub API. Operates on metadata and structure
rather than deep static analysis to maintain performance and privacy.
"""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

API_BASE = "https://api.github.com"

# ---------------------------------------------------------------------------
# Detection registry — data-driven heuristic rules
# ---------------------------------------------------------------------------

# Files/dirs whose presence indicates a framework or infrastructure tool.
FRAMEWORK_INDICATORS: dict[str, tuple[str, str]] = {
    # filename or dir → (name, category)
    "Dockerfile": ("Docker", "infrastructure"),
    "docker-compose.yml": ("Docker Compose", "infrastructure"),
    "docker-compose.yaml": ("Docker Compose", "infrastructure"),
    ".github/workflows": ("GitHub Actions", "infrastructure"),
    ".gitlab-ci.yml": ("GitLab CI", "infrastructure"),
    ".circleci": ("CircleCI", "infrastructure"),
    "Jenkinsfile": ("Jenkins", "infrastructure"),
    "terraform": ("Terraform", "infrastructure"),
    "kubernetes": ("Kubernetes", "infrastructure"),
    "k8s": ("Kubernetes", "infrastructure"),
    "helm": ("Helm", "infrastructure"),
    ".travis.yml": ("Travis CI", "infrastructure"),
    "netlify.toml": ("Netlify", "infrastructure"),
    "vercel.json": ("Vercel", "infrastructure"),
    "fly.toml": ("Fly.io", "infrastructure"),
    "render.yaml": ("Render", "infrastructure"),
    "nginx.conf": ("Nginx", "infrastructure"),
    "Vagrantfile": ("Vagrant", "infrastructure"),
    "ansible": ("Ansible", "infrastructure"),
    ".eslintrc.js": ("ESLint", "tool"),
    ".eslintrc.json": ("ESLint", "tool"),
    "tailwind.config.js": ("Tailwind CSS", "framework"),
    "tailwind.config.ts": ("Tailwind CSS", "framework"),
    "tsconfig.json": ("TypeScript", "language"),
    "webpack.config.js": ("Webpack", "tool"),
    "vite.config.ts": ("Vite", "tool"),
    "vite.config.js": ("Vite", "tool"),
    ".prettierrc": ("Prettier", "tool"),
    "jest.config.js": ("Jest", "tool"),
    "jest.config.ts": ("Jest", "tool"),
    "pytest.ini": ("pytest", "tool"),
    "pyproject.toml": ("Python Package", "tool"),
    "Cargo.toml": ("Rust", "language"),
    "go.mod": ("Go", "language"),
    "Gemfile": ("Ruby", "language"),
    "composer.json": ("PHP", "language"),
    "build.gradle": ("Gradle", "tool"),
    "pom.xml": ("Maven", "tool"),
}

# Keys to look for inside package.json dependencies.
NPM_FRAMEWORK_MAP: dict[str, tuple[str, str]] = {
    "react": ("React", "framework"),
    "react-native": ("React Native", "framework"),
    "next": ("Next.js", "framework"),
    "vue": ("Vue", "framework"),
    "nuxt": ("Nuxt", "framework"),
    "svelte": ("Svelte", "framework"),
    "@angular/core": ("Angular", "framework"),
    "express": ("Express", "framework"),
    "fastify": ("Fastify", "framework"),
    "gatsby": ("Gatsby", "framework"),
    "remix": ("Remix", "framework"),
    "@nestjs/core": ("NestJS", "framework"),
    "koa": ("Koa", "framework"),
    "tailwindcss": ("Tailwind CSS", "framework"),
    "prisma": ("Prisma", "tool"),
    "mongoose": ("Mongoose", "tool"),
    "sequelize": ("Sequelize", "tool"),
    "jest": ("Jest", "tool"),
    "mocha": ("Mocha", "tool"),
    "webpack": ("Webpack", "tool"),
    "vite": ("Vite", "tool"),
    "typescript": ("TypeScript", "language"),
    "three": ("Three.js", "framework"),
    "electron": ("Electron", "framework"),
    "socket.io": ("Socket.IO", "framework"),
    "graphql": ("GraphQL", "tool"),
    "@apollo/client": ("Apollo", "framework"),
    "redis": ("Redis", "tool"),
    "pg": ("PostgreSQL", "tool"),
    "mongodb": ("MongoDB", "tool"),
    "supabase": ("Supabase", "tool"),
    "firebase": ("Firebase", "tool"),
}

# Keys to look for inside requirements.txt lines.
PYTHON_FRAMEWORK_MAP: dict[str, tuple[str, str]] = {
    "django": ("Django", "framework"),
    "flask": ("Flask", "framework"),
    "fastapi": ("FastAPI", "framework"),
    "tornado": ("Tornado", "framework"),
    "celery": ("Celery", "tool"),
    "sqlalchemy": ("SQLAlchemy", "tool"),
    "pandas": ("pandas", "framework"),
    "numpy": ("NumPy", "framework"),
    "scipy": ("SciPy", "framework"),
    "scikit-learn": ("scikit-learn", "framework"),
    "tensorflow": ("TensorFlow", "framework"),
    "torch": ("PyTorch", "framework"),
    "pytest": ("pytest", "tool"),
    "pydantic": ("Pydantic", "tool"),
    "requests": ("Requests", "tool"),
    "boto3": ("AWS SDK", "tool"),
    "redis": ("Redis", "tool"),
    "psycopg2": ("PostgreSQL", "tool"),
}

# Cargo.toml [dependencies] keys.
RUST_CRATE_MAP: dict[str, tuple[str, str]] = {
    "actix-web": ("Actix Web", "framework"),
    "axum": ("Axum", "framework"),
    "rocket": ("Rocket", "framework"),
    "tokio": ("Tokio", "tool"),
    "serde": ("Serde", "tool"),
    "diesel": ("Diesel", "tool"),
    "sqlx": ("SQLx", "tool"),
    "leptos": ("Leptos", "framework"),
    "yew": ("Yew", "framework"),
    "tauri": ("Tauri", "framework"),
    "wasm-bindgen": ("WebAssembly", "tool"),
}

# Gemfile dependency keys.
RUBY_GEM_MAP: dict[str, tuple[str, str]] = {
    "rails": ("Ruby on Rails", "framework"),
    "sinatra": ("Sinatra", "framework"),
    "sidekiq": ("Sidekiq", "tool"),
    "rspec": ("RSpec", "tool"),
}

# go.mod module paths (prefix match).
GO_MODULE_MAP: dict[str, tuple[str, str]] = {
    "github.com/gin-gonic/gin": ("Gin", "framework"),
    "github.com/gorilla/mux": ("Gorilla Mux", "framework"),
    "github.com/labstack/echo": ("Echo", "framework"),
    "github.com/gofiber/fiber": ("Fiber", "framework"),
    "gorm.io/gorm": ("GORM", "tool"),
}

# composer.json dependency keys.
PHP_PACKAGE_MAP: dict[str, tuple[str, str]] = {
    "laravel/framework": ("Laravel", "framework"),
    "symfony/symfony": ("Symfony", "framework"),
    "slim/slim": ("Slim", "framework"),
}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class GitHubAnalyzerError(Exception):
    """Base exception for the GitHub analyzer."""


class GitHubAuthError(GitHubAnalyzerError):
    """Raised when the GitHub token is invalid or missing required scopes."""


class GitHubUserNotFoundError(GitHubAnalyzerError):
    """Raised when the requested GitHub user does not exist."""


class GitHubRateLimitError(GitHubAnalyzerError):
    """Raised when the GitHub API rate limit has been exceeded."""


class GitHubAPIError(GitHubAnalyzerError):
    """Raised for unexpected GitHub API errors."""


# ---------------------------------------------------------------------------
# API client
# ---------------------------------------------------------------------------


class GitHubClient:
    """Low-level GitHub REST API client with rate-limit tracking."""

    def __init__(
        self,
        token: str | None = None,
        timeout: int = 30,
        cache_enabled: bool = True,
        cache_ttl: int = 3600,
    ) -> None:
        self.token = token
        self.timeout = timeout
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.rate_limit_remaining: int | None = None
        self.rate_limit_reset: int | None = None

    @property
    def authenticated(self) -> bool:
        return self.token is not None and self.token != ""

    # -- internal -----------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if self.authenticated:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _update_rate_limit(self, resp: requests.Response) -> None:
        remaining = resp.headers.get("X-RateLimit-Remaining")
        reset = resp.headers.get("X-RateLimit-Reset")
        if remaining is not None:
            self.rate_limit_remaining = int(remaining)
        if reset is not None:
            self.rate_limit_reset = int(reset)

    def _request(self, path: str) -> Any:
        from projectbridge.input import cache as _cache

        # Check cache first.
        if self.cache_enabled:
            cached = _cache.get(path, ttl=self.cache_ttl)
            if cached is not None:
                logger.debug("Cache hit: %s", path)
                return cached

        url = f"{API_BASE}{path}"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
        except requests.ConnectionError:
            raise GitHubAPIError("Cannot reach the GitHub API. Check your internet connection.")
        except requests.Timeout:
            raise GitHubAPIError(f"GitHub API request timed out after {self.timeout}s.")

        self._update_rate_limit(resp)

        if resp.status_code == 401:
            raise GitHubAuthError(
                "GitHub token is invalid or expired. "
                "Set a valid token via the GITHUB_TOKEN environment variable."
            )
        if resp.status_code == 403 and self.rate_limit_remaining == 0:
            raise GitHubRateLimitError(
                "GitHub API rate limit exceeded. "
                f"Limit resets at unix timestamp {self.rate_limit_reset}."
            )
        if resp.status_code == 403:
            raise GitHubAuthError("GitHub token lacks required permissions.")
        if resp.status_code == 404:
            raise GitHubUserNotFoundError(f"GitHub resource not found: {path}")
        if not resp.ok:
            raise GitHubAPIError(f"GitHub API error {resp.status_code}: {resp.text[:200]}")

        body = resp.json()

        # Store in cache.
        if self.cache_enabled:
            _cache.put(path, body)

        return body

    # -- public API ---------------------------------------------------------

    def get_user_repos(self, username: str) -> list[dict]:
        """Fetch public repositories for *username* (paginated)."""
        repos: list[dict] = []
        page = 1
        while True:
            batch = self._request(f"/users/{username}/repos?per_page=100&sort=pushed&page={page}")
            if not batch:
                break
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return repos

    def get_repo_languages(self, owner: str, repo: str) -> dict[str, int]:
        """Return ``{language: bytes}`` for a repository."""
        return self._request(f"/repos/{owner}/{repo}/languages")

    def get_repo_contents(self, owner: str, repo: str, path: str = "") -> list[dict]:
        """Return the top-level file/directory listing for a repo path."""
        try:
            result = self._request(f"/repos/{owner}/{repo}/contents/{path}")
        except GitHubUserNotFoundError:
            # Empty repo or path not found — not fatal.
            return []
        if isinstance(result, list):
            return result
        return [result]

    def get_rate_limit(self) -> dict[str, int | None]:
        return {
            "remaining": self.rate_limit_remaining,
            "reset": self.rate_limit_reset,
        }


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------


class GitHubAnalyzer:
    """Extracts developer context signals from GitHub repositories."""

    def __init__(
        self,
        token: str | None = None,
        timeout: int = 30,
        cache_enabled: bool = True,
        cache_ttl: int = 3600,
    ) -> None:
        self.client = GitHubClient(
            token=token,
            timeout=timeout,
            cache_enabled=cache_enabled,
            cache_ttl=cache_ttl,
        )

    def analyze(self, username: str) -> dict[str, Any]:
        """Analyze all public repos for *username*.

        Returns a context dict with keys:
            languages, frameworks, project_structures,
            infrastructure_signals, rate_limit.
        """
        repos = self.client.get_user_repos(username)

        languages: dict[str, int] = {}
        frameworks: dict[str, str] = {}  # name → category
        infra: dict[str, str] = {}  # name → category
        structures: set[str] = set()

        for repo in repos:
            if repo.get("fork"):
                continue

            owner = repo["owner"]["login"]
            name = repo["name"]

            # --- languages ---
            repo_langs = self.client.get_repo_languages(owner, name)
            for lang, byte_count in repo_langs.items():
                languages[lang] = languages.get(lang, 0) + byte_count

            # --- file tree signals ---
            contents = self.client.get_repo_contents(owner, name)
            content_names = {item["name"] for item in contents}
            content_paths = {item["path"] for item in contents}

            self._detect_file_indicators(content_names, content_paths, frameworks, infra)
            self._detect_npm_frameworks(owner, name, content_names, frameworks)
            self._detect_python_frameworks(owner, name, content_names, frameworks)
            self._detect_rust_crates(owner, name, content_names, frameworks)
            self._detect_ruby_gems(owner, name, content_names, frameworks)
            self._detect_go_modules(owner, name, content_names, frameworks)
            self._detect_php_packages(owner, name, content_names, frameworks)
            self._detect_structures(content_names, structures)

        return {
            "languages": self._build_language_list(languages),
            "frameworks": [{"name": n, "category": c} for n, c in sorted(frameworks.items())],
            "project_structures": sorted(structures),
            "infrastructure_signals": [
                {"name": n, "category": c} for n, c in sorted(infra.items())
            ],
            "rate_limit": {
                "remaining": self.client.rate_limit_remaining,
                "reset": self.client.rate_limit_reset,
                "authenticated": self.client.authenticated,
            },
        }

    # -- private helpers ----------------------------------------------------

    @staticmethod
    def _build_language_list(lang_bytes: dict[str, int]) -> list[dict]:
        total = sum(lang_bytes.values()) or 1
        return sorted(
            [
                {
                    "name": lang,
                    "category": "language",
                    "percentage": round(byte_count / total * 100, 1),
                }
                for lang, byte_count in lang_bytes.items()
            ],
            key=lambda d: d["percentage"],
            reverse=True,
        )

    @staticmethod
    def _detect_file_indicators(
        names: set[str],
        paths: set[str],
        frameworks: dict[str, str],
        infra: dict[str, str],
    ) -> None:
        for indicator, (name, category) in FRAMEWORK_INDICATORS.items():
            if indicator in names or indicator in paths:
                bucket = infra if category == "infrastructure" else frameworks
                bucket[name] = category

    def _detect_npm_frameworks(
        self,
        owner: str,
        repo: str,
        names: set[str],
        frameworks: dict[str, str],
    ) -> None:
        if "package.json" not in names:
            return
        try:
            pkg = self.client._request(f"/repos/{owner}/{repo}/contents/package.json")
        except GitHubAnalyzerError:
            return
        self._match_json_deps(pkg, frameworks, NPM_FRAMEWORK_MAP)

    def _detect_python_frameworks(
        self,
        owner: str,
        repo: str,
        names: set[str],
        frameworks: dict[str, str],
    ) -> None:
        if "requirements.txt" not in names:
            return
        try:
            import base64

            file_info = self.client._request(f"/repos/{owner}/{repo}/contents/requirements.txt")
            content = base64.b64decode(file_info.get("content", "")).decode()
        except (GitHubAnalyzerError, Exception):
            return

        lower_lines = content.lower()
        for key, (name, category) in PYTHON_FRAMEWORK_MAP.items():
            if key in lower_lines:
                frameworks[name] = category

    @staticmethod
    def _match_json_deps(
        file_info: dict,
        frameworks: dict[str, str],
        mapping: dict[str, tuple[str, str]],
        dep_keys: tuple[str, ...] = ("dependencies", "devDependencies"),
    ) -> None:
        import base64
        import json

        try:
            content = base64.b64decode(file_info.get("content", "")).decode()
            pkg = json.loads(content)
        except Exception:
            return
        all_deps: set[str] = set()
        for key in dep_keys:
            all_deps.update(pkg.get(key, {}).keys())
        for dep_name, (fw_name, category) in mapping.items():
            if dep_name in all_deps:
                frameworks[fw_name] = category

    def _detect_rust_crates(
        self,
        owner: str,
        repo: str,
        names: set[str],
        frameworks: dict[str, str],
    ) -> None:
        if "Cargo.toml" not in names:
            return
        content = self._fetch_file_text(owner, repo, "Cargo.toml")
        if content is None:
            return
        lower = content.lower()
        for key, (name, category) in RUST_CRATE_MAP.items():
            if key in lower:
                frameworks[name] = category

    def _detect_ruby_gems(
        self,
        owner: str,
        repo: str,
        names: set[str],
        frameworks: dict[str, str],
    ) -> None:
        if "Gemfile" not in names:
            return
        content = self._fetch_file_text(owner, repo, "Gemfile")
        if content is None:
            return
        lower = content.lower()
        for key, (name, category) in RUBY_GEM_MAP.items():
            if key in lower:
                frameworks[name] = category

    def _detect_go_modules(
        self,
        owner: str,
        repo: str,
        names: set[str],
        frameworks: dict[str, str],
    ) -> None:
        if "go.mod" not in names:
            return
        content = self._fetch_file_text(owner, repo, "go.mod")
        if content is None:
            return
        for key, (name, category) in GO_MODULE_MAP.items():
            if key in content:
                frameworks[name] = category

    def _detect_php_packages(
        self,
        owner: str,
        repo: str,
        names: set[str],
        frameworks: dict[str, str],
    ) -> None:
        if "composer.json" not in names:
            return
        try:
            file_info = self.client._request(f"/repos/{owner}/{repo}/contents/composer.json")
        except GitHubAnalyzerError:
            return
        self._match_json_deps(
            file_info, frameworks, PHP_PACKAGE_MAP, dep_keys=("require", "require-dev")
        )

    def _fetch_file_text(self, owner: str, repo: str, path: str) -> str | None:
        """Fetch and decode a text file from a repo. Returns None on failure."""
        import base64

        try:
            file_info = self.client._request(f"/repos/{owner}/{repo}/contents/{path}")
            return base64.b64decode(file_info.get("content", "")).decode()
        except Exception:
            return None

    @staticmethod
    def _detect_structures(names: set[str], structures: set[str]) -> None:
        if "src" in names:
            structures.add("src_layout")
        if "packages" in names or "libs" in names:
            structures.add("monorepo")
        if "setup.py" in names or "pyproject.toml" in names:
            structures.add("python_package")
        if "package.json" in names:
            structures.add("node_project")
        if "Makefile" in names:
            structures.add("makefile")
