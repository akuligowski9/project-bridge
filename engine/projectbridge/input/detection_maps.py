"""Detection registry data for GitHub repository analysis.

Data-driven heuristic rules used by :mod:`projectbridge.input.github`
to identify frameworks, infrastructure tools, and dependency ecosystems
from repository file trees and manifest contents.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# File/dir presence → framework or infrastructure tool
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Dependency manifest maps — keys to look for inside manifest files
# ---------------------------------------------------------------------------

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

RUBY_GEM_MAP: dict[str, tuple[str, str]] = {
    "rails": ("Ruby on Rails", "framework"),
    "sinatra": ("Sinatra", "framework"),
    "sidekiq": ("Sidekiq", "tool"),
    "rspec": ("RSpec", "tool"),
}

GO_MODULE_MAP: dict[str, tuple[str, str]] = {
    "github.com/gin-gonic/gin": ("Gin", "framework"),
    "github.com/gorilla/mux": ("Gorilla Mux", "framework"),
    "github.com/labstack/echo": ("Echo", "framework"),
    "github.com/gofiber/fiber": ("Fiber", "framework"),
    "gorm.io/gorm": ("GORM", "tool"),
}

PHP_PACKAGE_MAP: dict[str, tuple[str, str]] = {
    "laravel/framework": ("Laravel", "framework"),
    "symfony/symfony": ("Symfony", "framework"),
    "slim/slim": ("Slim", "framework"),
}
