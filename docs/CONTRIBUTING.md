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

### Engine

```bash
cd engine
pip install -r requirements.txt
python cli.py --example
```

### UI

```bash
cd app
npm install
npm run dev
```

---

## Common Contribution Areas

### AI Providers

AI integrations live in:

```
engine/projectbridge/ai/
```

Implement the base interface:

```python
class AIProvider:
    def analyze_skills(self, context: dict) -> dict:
        pass

    def generate_projects(self, gaps: dict) -> list:
        pass
```

### Analysis Detectors

Language or framework detection lives in:

```
engine/projectbridge/analysis/
```

Keep detectors small and focused.

### Recommendations

Project generation logic lives in:

```
engine/projectbridge/recommend/
```

Recommendations should remain realistic and scoped for completion.

---

## Pull Request Guidelines

Please ensure:

- Code is readable without AI context
- Changes are documented if behavior changes
- CLI behavior remains stable
- Output schema changes increment `schema_version`

Small, focused PRs are preferred.

---

## AI-Assisted Contributions

AI-assisted contributions are welcome.

Please review and understand generated code before submitting.
Maintainers may request clarification if behavior is unclear.
