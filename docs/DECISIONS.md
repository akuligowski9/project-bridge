# Decisions Log

This document captures architectural, design, and scope decisions for ProjectBridge.

Each entry records the context, the decision, and the reasoning — so future contributors (and future sessions) can understand *why* without guessing.

---

## Format

```markdown
### DEC-###: <Short title>

**Date:** YYYY-MM-DD
**Status:** Accepted | Superseded | Revisiting
**Context:** <What prompted this decision>
**Decision:** <What was decided>
**Reasoning:** <Why this option was chosen over alternatives>
**Alternatives Considered:** <What else was evaluated>
**Consequences:** <What this enables or constrains going forward>
```

---

## Decisions

### DEC-001: Local-first architecture

**Date:** 2026-02-08
**Status:** Accepted
**Context:** ProjectBridge needs to handle GitHub tokens and private repository data. Users must trust the tool with sensitive information.
**Decision:** All processing runs locally. No data is transmitted externally.
**Reasoning:** Local execution eliminates trust boundaries with external services, simplifies privacy guarantees, and removes the need for account infrastructure.
**Alternatives Considered:** Hosted SaaS model, hybrid (local analysis with cloud AI).
**Consequences:** No hosted features. AI providers must support local invocation or API keys managed by the user.

### DEC-002: Python engine as source of truth

**Date:** 2026-02-08
**Status:** Accepted
**Context:** The system needs a core analysis engine that can run independently of any UI.
**Decision:** The Python engine is the authoritative source of all analysis logic. The UI is a consumer only.
**Reasoning:** Python offers strong AI ecosystem support and accessibility for contributors. Separating engine from UI ensures CLI-first usability and testability.
**Alternatives Considered:** Node.js engine, Rust engine, monolithic Tauri app.
**Consequences:** UI must call the engine interface. No business logic in the frontend.

### DEC-003: Tauri for desktop UI

**Date:** 2026-02-08
**Status:** Accepted
**Context:** A desktop interface is needed for users who prefer a visual workflow over CLI.
**Decision:** Use Tauri for the desktop application shell.
**Reasoning:** Tauri is lightweight, supports local execution, and avoids shipping a full Chromium runtime (unlike Electron).
**Alternatives Considered:** Electron, web-only UI, no UI.
**Consequences:** Frontend is built with standard web technologies. Distribution is desktop-native.

### DEC-004: AI provider isolation

**Date:** 2026-02-08
**Status:** Accepted
**Context:** AI capabilities are valuable but the landscape of providers and models changes rapidly.
**Decision:** AI functionality is abstracted behind a pluggable provider interface. The system must function with `--no-ai`.
**Reasoning:** Isolation prevents vendor lock-in, enables experimentation, and ensures core analysis remains deterministic.
**Alternatives Considered:** Hard-coding a single provider, making AI required.
**Consequences:** All AI usage must go through the provider interface. Core analysis cannot depend on AI output.

### DEC-005: PB prefix for backlog items

**Date:** 2026-02-08
**Status:** Accepted
**Context:** A project identifier prefix is needed for backlog items and GitHub Issues.
**Decision:** Use `PB` as the prefix (e.g., `PB-001`).
**Reasoning:** Short, memorable, and derived from "ProjectBridge".
**Alternatives Considered:** BRIDGE, PROJ.
**Consequences:** All backlog items and issues use this prefix going forward.

### DEC-006: Initial backlog structure and prioritization

**Date:** 2026-02-08
**Status:** Accepted
**Context:** ProjectBridge is greenfield — only documentation exists. A comprehensive backlog is needed to capture all work items required to implement the system described in the README and technical specification.
**Decision:** Populate the backlog with 32 items (PB-001 through PB-032) across four priority tiers plus 8 parking lot ideas. Critical items (8) cover the foundational package structure, schemas, config, input processors, analysis layer, AI interface, and CLI. High items (8) cover the recommendation engine, example mode, orchestrator, and test infrastructure. Medium items (9) cover the Tauri UI, additional AI providers, and robustness features. Low items (7) cover polish, extensibility, and developer tooling.
**Reasoning:** Prioritization follows a dependency-driven approach: Critical items form the foundation everything else builds on, High items deliver core user value, Medium items add robustness and the desktop UI, Low items are polish. Each item uses a structured format (Description, up to 5 independently testable Acceptance Criteria, Metadata with dependencies) to ensure items are actionable and verifiable.
**Alternatives Considered:** Flat unprioritized list, milestone-based grouping, fewer coarser-grained items.
**Consequences:** The backlog serves as the single source of truth for planned work. Items should be implemented roughly in priority order, respecting dependency chains. Parking lot ideas are captured but not committed.

### DEC-007: DECISIONS.md replaces PROGRESS.md

**Date:** 2026-02-08
**Status:** Accepted
**Context:** The standard INSTRUCTIONS template uses `PROGRESS.md` (a chronological session log) for continuity between sessions. ProjectBridge needs a way to preserve reasoning across sessions but is greenfield — session-by-session narrative adds overhead without proportional value at this stage.
**Decision:** Use `DECISIONS.md` (structured decision records) instead of `PROGRESS.md`. Decisions are recorded in `DEC-###` format with context, reasoning, alternatives, and consequences.
**Reasoning:** A structured decision log better serves a greenfield project where *why* choices were made matters more than *when* work happened. Decision records are durable, searchable, and directly referenced by backlog items and technical spec. A chronological log can be introduced later if session continuity becomes a pain point.
**Alternatives Considered:** PROGRESS.md (chronological log), both PROGRESS.md and DECISIONS.md, ADR (Architecture Decision Records) directory structure.
**Consequences:** Session continuity relies on DECISIONS.md + BACKLOG.md state rather than a narrative log. The INSTRUCTIONS.md source of truth hierarchy reflects this ordering.

### DEC-008: Deterministic keyword matching for job description parsing

**Date:** 2026-02-08
**Status:** Accepted
**Context:** The job description parser (PB-005) needs to extract required technologies, experience domains, and architectural expectations from raw text. The parser sits in the input processing layer, upstream of the analysis engine.
**Decision:** Use regex word-boundary keyword matching against curated keyword lists (~70 technologies, ~20 domains, ~20 architectural patterns) rather than NLP or AI-based extraction.
**Reasoning:** The tech spec requires the analysis layer to be deterministic (Section 5.3). Pushing non-determinism into the input layer would undermine that guarantee. Keyword matching is transparent, testable, and produces identical results for identical input. AI-based parsing can be layered on later via the AI provider's `analyze_context` method without changing the core pipeline.
**Alternatives Considered:** spaCy/NLP entity extraction, AI provider-based parsing, hybrid (keywords + AI fallback).
**Consequences:** Parsing accuracy is limited by keyword coverage — uncommon technologies or unusual phrasing may be missed. The keyword lists must be maintained manually. This is acceptable because PB-021 (enhanced heuristics) is planned for iterative improvement, and the AI context enrichment stage can compensate.

### DEC-009: Adjacent skills scoped to job requirements

**Date:** 2026-02-08
**Status:** Accepted
**Context:** The analysis layer (PB-006) uses the skill taxonomy to find "adjacent skills" — technologies related to what a developer already knows. A developer with React knowledge has adjacents like Next.js, Redux, TypeScript, React Native, and Vite. Surfacing all reachable adjacents would produce noisy, unfocused output.
**Decision:** Only surface adjacent skills that are also present in the job requirements. An adjacent skill that the job doesn't ask for is filtered out.
**Reasoning:** The purpose of ProjectBridge is gap analysis against a specific job, not general career advice. Scoping adjacents to job requirements keeps the output actionable — every adjacent skill shown is both learnable (close to existing skills) and relevant (the job wants it). This also keeps the gaps list concise.
**Alternatives Considered:** Show all adjacents regardless of job requirements, show adjacents with a relevance score, separate "job-relevant adjacents" from "general growth paths."
**Consequences:** Adjacent skills are a strict subset of job requirements. A developer's broader growth potential is not surfaced unless the job asks for it. This could be revisited if a "career exploration" mode is added (see Parking Lot).

### DEC-010: AI providers as optional dependencies

**Date:** 2026-02-08
**Status:** Accepted
**Context:** The OpenAI provider (PB-015) requires the `openai` Python package, but most users running `--no-ai` or using other providers don't need it. Making it a hard dependency would bloat the install and require all users to pull in OpenAI's SDK and its transitive deps (httpx, etc.).
**Decision:** AI provider SDKs are optional dependencies (`pip install projectbridge[openai]`). The provider uses lazy imports and raises a descriptive `OpenAIProviderError` if the package is missing at instantiation time.
**Reasoning:** This follows the pattern established by DEC-004 (AI provider isolation). The engine must work with `--no-ai` and shouldn't penalize users who don't need a specific provider. Lazy imports keep the module registerable without the SDK installed — `register_provider("openai", OpenAIProvider)` succeeds at import time, and the missing dependency is only surfaced when someone actually tries to use it.
**Alternatives Considered:** Hard require all provider SDKs, separate installable packages per provider (e.g., `projectbridge-openai`).
**Consequences:** Users must explicitly opt into provider dependencies. Error messages must clearly explain how to install the missing package. This pattern applies to future providers (Anthropic, Ollama).

### DEC-011: JSON response mode for structured AI output

**Date:** 2026-02-08
**Status:** Accepted
**Context:** The OpenAI provider must return structured data (enriched context dicts, recommendation arrays) that downstream code can parse reliably. LLMs can return malformed JSON, markdown-wrapped JSON, or free-form text.
**Decision:** Use OpenAI's `response_format: {"type": "json_object"}` to guarantee valid JSON output, with prompts designed to specify the exact schema expected.
**Reasoning:** JSON mode eliminates an entire class of parsing failures. Without it, the provider would need fragile regex extraction or retry logic to handle markdown fences, trailing text, or truncated output. The prompts are stored as editable template files so the expected schema can evolve without code changes.
**Alternatives Considered:** Free-form responses with JSON extraction regex, function calling / tool use for structured output, Pydantic-based structured output mode.
**Consequences:** Responses are always valid JSON but the internal structure still needs validation (the model may omit fields or use unexpected types). The `analyze_context` method includes a fallback path for non-JSON responses as a safety net.

### DEC-012: Svelte + TypeScript + Tailwind CSS for Tauri frontend

**Date:** 2026-02-09
**Status:** Accepted
**Context:** DEC-003 chose Tauri as the desktop shell but left the frontend framework unspecified. The Tauri webview requires a web technology to render UI. The developer's existing portfolio is React/Next.js-heavy and would benefit from demonstrating a second frontend framework.
**Decision:** Use Svelte with TypeScript and Tailwind CSS as the frontend framework inside the Tauri webview.
**Reasoning:** Svelte is a compiler-based framework that produces minimal runtime code, pairing well with Tauri's lightweight philosophy. It's widely recognized in the industry and adds meaningful portfolio differentiation from React. TypeScript provides type safety. Tailwind CSS is already in the developer's toolkit, reducing friction. The Tauri + Svelte combination is well-supported with official templates.
**Alternatives Considered:** React (already well-represented in portfolio), Leptos/Rust WASM (not recognizable to most hiring managers), Vue (similar niche to React, less differentiation), vanilla JS (insufficient for maintainable UI).
**Consequences:** The `app/` directory will use npm-based tooling with Svelte, TypeScript, and Tailwind CSS. Contributors working on the UI need familiarity with Svelte's component model. The Svelte ecosystem is smaller than React's but sufficient for the project's thin UI layer.

### DEC-013: Inline text CLI flags for Tauri IPC

**Date:** 2026-02-09
**Status:** Accepted
**Context:** The CLI accepts `--job FILE` and `--resume FILE` for file paths, but the Tauri UI provides raw text from form inputs. The Rust IPC layer needs to pass text directly without writing temporary files for every analysis.
**Decision:** Add `--job-text TEXT` and `--resume-text TEXT` CLI flags as alternatives to `--job` and `--resume`. Each pair is mutually exclusive — providing both a file path and inline text for the same input produces an error.
**Reasoning:** Keeps the Rust IPC layer thin (just passes strings to CLI args) while maintaining the CLI as the single entry point per DEC-002. Temporary file management in Rust would add complexity and error surfaces. Mutual exclusion prevents ambiguity about which input source takes precedence.
**Alternatives Considered:** Write temp files in Rust and pass file paths, stdin piping from Rust to CLI, direct Python FFI from Rust.
**Consequences:** The CLI contract now includes 4 job/resume input flags. Tauri commands pass inline text directly. The orchestrator handles both file and text inputs transparently.

### DEC-014: MkDocs Material for documentation site

**Date:** 2026-02-09
**Status:** Accepted
**Context:** The project has substantial documentation in Markdown files (README, tech spec, contributing guide, decisions log, backlog, security policy) that would benefit from a browsable, searchable format.
**Decision:** Use MkDocs with the Material theme and the `include-markdown` plugin to publish existing docs as a static site.
**Reasoning:** MkDocs Material is the most popular Python documentation framework, aligning with the project's Python stack. The `include-markdown` plugin allows site pages to reference the canonical Markdown files in `docs/` rather than duplicating content. This means updating `docs/BACKLOG.md` automatically updates the site. No content migration required.
**Alternatives Considered:** Sphinx (more complex, better for API docs), Docusaurus (Node-based, misaligned with Python stack), raw GitHub Pages with Jekyll.
**Consequences:** Site source lives in `site_src/` with thin wrapper files. `mkdocs build` generates to `site/` (gitignored). Future: GitHub Actions can deploy to GitHub Pages on push.

### DEC-015: Ollama provider uses stdlib only

**Date:** 2026-02-09
**Status:** Accepted
**Context:** The Ollama AI provider (PB-027) needs to call the Ollama REST API at `localhost:11434`. The OpenAI and Anthropic providers use their respective SDKs as optional dependencies.
**Decision:** Use Python's stdlib `urllib.request` for the Ollama provider instead of adding a third-party HTTP library.
**Reasoning:** Ollama's API is a single POST endpoint (`/api/chat`) with a simple JSON payload. No SDK exists for Ollama in Python that matches the maturity of the OpenAI/Anthropic SDKs. Using stdlib means zero additional dependencies — fitting for a provider whose entire purpose is local, dependency-light AI inference.
**Alternatives Considered:** `requests` library (already a dependency but adds coupling), `httpx` (async-capable but overkill), `ollama` Python package (immature, unnecessary abstraction).
**Consequences:** The provider uses synchronous blocking HTTP. Error handling maps `urllib` exceptions to descriptive `OllamaProviderError` messages. No retry logic — Ollama runs locally so transient failures are unlikely.

### DEC-016: File-based caching with SHA-256 keys

**Date:** 2026-02-09
**Status:** Accepted
**Context:** Repeated analyses of the same GitHub user make redundant API calls. A caching layer (PB-028) is needed to reduce API usage and improve iteration speed.
**Decision:** Cache GitHub API responses as individual JSON files under `~/.cache/projectbridge/`, keyed by SHA-256 hash of the request path. Each file stores the response body and a timestamp. TTL is configurable (default: 1 hour).
**Reasoning:** File-based caching requires no additional dependencies (no Redis, SQLite, or shelve). SHA-256 hashing produces safe, fixed-length filenames from arbitrary API paths. The `~/.cache/` location follows XDG conventions. Individual files per request make cache invalidation simple — delete the file or let TTL expire.
**Alternatives Considered:** In-memory dict (lost between runs), SQLite (heavier, unnecessary for key-value lookups), `requests-cache` library (adds a dependency).
**Consequences:** Cache persists across CLI invocations. `--no-cache` bypasses reads but doesn't clear existing cache. Cache directory grows over time but entries are small (~1-10KB each).

### DEC-017: Standalone Rust scanner for local repository analysis

**Date:** 2026-02-13
**Status:** Accepted
**Context:** ProjectBridge only analyzes repos via the GitHub API — users need a GitHub account with public repos to use the tool. A local filesystem scanner would enable offline use, private/unpushed repo analysis, and faster scans without API rate limits.
**Decision:** Build `pb-scan` as a standalone Rust CLI under `scanner/` (separate Cargo project, not in the Tauri workspace). It outputs JSON matching the existing `dev_context` format so the Python pipeline works unchanged. The Python CLI adds `--local-repos` as an alternative to `--github-user`, invoking `pb-scan` via subprocess.
**Reasoning:** Rust is a natural fit — the project already has Rust in the Tauri app, and a compiled scanner is significantly faster than Python file walking for large codebases. The `ignore` crate (used by ripgrep) provides .gitignore-aware directory walking out of the box. Keeping it as a standalone project avoids Cargo workspace complexities with the Tauri app.
**Alternatives Considered:** Python implementation using `pathlib` (slower, no .gitignore awareness without extra deps), adding to Tauri workspace (workspace dependency conflicts), using `tree-sitter` for deep analysis (overkill for metadata-level scanning).
**Consequences:** Users need `pb-scan` on PATH for `--local-repos` to work. The scanner ports all detection heuristics from `github.py` to maintain parity. The output format has no `rate_limit` field (GitHub-specific) which the Python pipeline already doesn't use in the analysis path.
