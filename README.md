# ProjectBridge

**ProjectBridge** is a local-first developer tool that helps answer:

> *What should I build next to move toward the role I want?*

It analyzes your GitHub repositories, compares them against job descriptions, and recommends practical projects that help close skill gaps through real implementation.

**Runs entirely on your machine.**
No accounts. No uploads.

---

## Why This Exists

Job descriptions tell developers what technologies are required.

They rarely tell you *what to build* to demonstrate those skills.

ProjectBridge turns:

```
Job requirements
+
Your existing experience
```

into:

```
Concrete project ideas you can actually ship.
```

The goal is clarity and forward progress — not scoring or evaluation.

---

## Quickstart

### Try without setup (example data)

```bash
projectbridge analyze --example
projectbridge export --example
```

No GitHub token or AI provider required.

### Run locally with your own data

```bash
git clone https://github.com/<yourname>/project-bridge
cd project-bridge
```

Start engine:

```bash
cd engine
pip install -r requirements.txt
python cli.py
```

Start UI:

```bash
cd app
npm install
npm run dev
```

---

## What It Does

- Analyzes GitHub repositories locally
- Extracts requirements from job descriptions
- Identifies strengths and growth areas
- Recommends small, realistic projects to build next
- Generates a shareable skill-gap snapshot

---

## Local-First & Privacy

ProjectBridge is intentionally not SaaS.

- GitHub tokens never leave your machine
- Private repositories remain private
- No telemetry or analytics
- All outputs stored locally

This tool is designed to be inspectable and trustworthy.

---

## AI Transparency

AI is used only in a bounded layer of the system.

- AI providers are optional and replaceable
- Core analysis can run without AI (`--no-ai`)
- Prompts and outputs are visible and editable

This project is developed with AI assistance (ChatGPT, Claude, and others), and contributors are welcome to use AI tools as long as contributions remain understandable and maintainable.

**Transparency matters more than workflow.**

---

## Architecture (High Level)

```
Tauri Desktop App
        ↓
Local Python Engine
        ↓
Analysis Modules
        ↓
AI Provider Interface (pluggable)
        ↓
Structured JSON Output
```

The UI is a visualization layer.
The engine is the source of truth.

---

## Output Format

Analysis results are produced as structured JSON:

```json
{
  "schema_version": "1.0",
  "strengths": [],
  "gaps": [],
  "recommendations": []
}
```

See `/docs/schema/` for details.

---

## What This Is / What This Isn't

### This is

- A local developer tool
- A bridge between job requirements and portfolio projects
- An extensible analysis engine

### This is not

- A hiring score
- A resume grader
- A hosted platform

---

## Contributing

ProjectBridge is designed to be forked and extended.

Common contribution areas:

- AI provider integrations
- language/framework detection
- recommendation improvements
- export formats
- UI improvements

See [CONTRIBUTING.md](docs/CONTRIBUTING.md).

---

## Roadmap (Short-Term)

- Additional AI provider integrations
- Improved repository detection heuristics
- Better project recommendation templates

---

## License

MIT License (see [LICENSE](LICENSE) file).
