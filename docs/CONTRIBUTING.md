# Contributing to ProjectBridge

Thank you for your interest in contributing.

ProjectBridge is intentionally designed to be simple, local-first, and extensible. Contributions should prioritize clarity and maintainability over complexity.

---

## Code of Conduct

Be kind, respectful, and constructive. We're building something useful together — treat fellow contributors the way you'd want to be treated. Harassment, dismissive behavior, and unconstructive criticism have no place here.

---

## New to Contributing?

If this is your first open source contribution, welcome! Here's how to get started:

1. **Find an issue** — Look for issues labeled [`good first issue`](https://github.com/akuligowski9/project-bridge/labels/good%20first%20issue) for beginner-friendly tasks.
2. **Fork the repo** — Click "Fork" on GitHub, then clone your fork locally.
3. **Create a branch** — See [Branch Naming](#branch-naming) below.
4. **Make your changes** — Follow the setup instructions and run `make check` before submitting.
5. **Open a PR** — Push your branch and open a pull request against `main`.

If you're new to Git and GitHub, [GitHub's guide](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) is a great place to start.

---

## Issue Etiquette

- **Comment before you start** — If you'd like to work on an issue, leave a comment so others know it's being tackled. This avoids duplicate effort.
- **Ask questions in the issue thread** — If you're stuck or unsure about the approach, ask! We're happy to help.
- **Don't go silent** — If you claimed an issue but can't finish it, that's totally fine. Just leave a comment so someone else can pick it up.

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

2. **Implement the interface** — you only need to implement `_chat`; the base class handles prompt loading, JSON parsing, and fallback logic via `analyze_context` and `generate_recommendations`:

```python
from projectbridge.ai.provider import AIProvider, AIProviderError, register_provider

class MyProviderError(AIProviderError):
    """Raised when MyProvider encounters an error."""

class MyProvider(AIProvider):
    _error_class = MyProviderError

    def __init__(self, api_key=None, model="default-model"):
        # Set up your client here.
        ...

    def _chat(self, system_prompt: str, user_message: str) -> str:
        # Send the prompt to your AI backend and return the response text.
        ...

register_provider("my-provider", MyProvider)
```

3. **Import your module** in `engine/projectbridge/orchestrator.py` so it auto-registers.

4. **Add tests** in `engine/tests/` — see existing provider tests for patterns (mock API responses, test registry integration).

5. **Add optional dependencies** (if any) to `engine/pyproject.toml` under `[project.optional-dependencies]`.

### Analysis Detectors

Language or framework detection lives in `engine/projectbridge/analysis/`. Keep detectors small and focused.

### Recommendations

Project generation logic lives in `engine/projectbridge/recommend/`. Recommendations should remain realistic and scoped for completion.

---

## Branch Naming

Use a descriptive branch name with a prefix:

- `feature/add-gemini-provider`
- `fix/empty-response-handling`
- `docs/update-contributing`

Keep it short, lowercase, and hyphen-separated.

---

## Commit Messages

- Use the imperative mood: "Add provider" not "Added provider"
- Keep the first line under 72 characters
- Add a blank line before any extended description

```
Add connection error handling to Gemini provider

Catches ConnectionError separately from generic exceptions and
provides a user-friendly network error message.
```

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
