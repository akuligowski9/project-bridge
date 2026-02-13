# Contributing to ProjectBridge

Thank you for your interest in contributing.

ProjectBridge is intentionally designed to be simple, local-first, and extensible. Contributions should prioritize clarity and maintainability over complexity.

---

## Philosophy

- Prefer simple solutions over clever ones.
- Avoid adding features that increase scope unnecessarily.
- Keep AI usage transparent and bounded.
- Favor composability and inspectability.

---

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+ (for the Tauri app)
- Rust toolchain (for the Tauri app)

### Quick Start

```bash
# Clone the repo
git clone https://github.com/akuligowski9/project-bridge.git
cd project-bridge

# Install the engine with dev dependencies
make install

# Set up pre-commit hooks
pre-commit install

# Verify everything works
make check
```

### Manual Setup (without Make)

```bash
pip install -e ./engine[dev]
pre-commit install
ruff check engine/
pytest engine/tests/ -v
```

### AI Provider (Optional)

To test with AI-enhanced recommendations, set up Ollama (free, local). See the **[AI Setup Guide](AI_SETUP.md)**.

### Tauri App

```bash
cd app
npm install
npm run dev
```

---

## Common Tasks

| Command        | What it does                         |
| -------------- | ------------------------------------ |
| `make install` | Install engine with dev dependencies |
| `make test`    | Run all tests                        |
| `make lint`    | Run linter + format check            |
| `make format`  | Auto-format and auto-fix lint issues |
| `make check`   | Lint + test (what CI runs)           |
| `make docs`    | Serve the documentation site locally |

Always run `make check` before submitting a PR.

---

## Common Contribution Areas

### AI Providers

AI providers live in `engine/projectbridge/ai/` and implement the `AIProvider` abstract base class. To add a new provider:

1. **Copy an existing provider** (e.g., `ollama_provider.py` for a local provider, `openai_provider.py` for a cloud API).

2. **Implement the interface:**

```python
from projectbridge.ai.provider import AIProvider, register_provider

class MyProvider(AIProvider):
    def analyze_context(self, context: dict) -> dict:
        # Enhance the developer context using your AI backend.
        # Return the enriched context dict.
        ...

    def generate_recommendations(self, gaps: dict) -> list[dict]:
        # Generate project recommendations from skill gaps.
        # Return a list of dicts with: title, description,
        # skills_addressed, estimated_scope.
        ...

register_provider("my-provider", MyProvider)
```

3. **Import your module** in `engine/projectbridge/ai/__init__.py` so it auto-registers.

4. **Add tests** in `engine/tests/` — see existing provider tests for patterns (mock API responses, test registry integration).

5. **Add optional dependencies** (if any) to `engine/pyproject.toml` under `[project.optional-dependencies]`.

### Analysis Detectors

Language or framework detection lives in `engine/projectbridge/analysis/`. Keep detectors small and focused.

### Recommendations

Project generation logic lives in `engine/projectbridge/recommend/`. Recommendations should remain realistic and scoped for completion.

---

## Pull Request Guidelines

Please ensure:

- `make check` passes
- Code is readable without AI context
- Changes are documented if behavior changes
- CLI behavior remains stable
- Output schema changes increment `schema_version`
- Tests are added for new functionality

Small, focused PRs are preferred.

---

## AI-Assisted Contributions

AI-assisted contributions are welcome.

Please review and understand generated code before submitting.
Maintainers may request clarification if behavior is unclear.
