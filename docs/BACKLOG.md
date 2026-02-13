# ProjectBridge Backlog

This is the single source of truth for committed work.

---

## Status Flow

```
Planned → In Progress → Done
              ↓
           Blocked
              ↓
           Archived
```

| Status          | Meaning                                               |
| --------------- | ----------------------------------------------------- |
| **Planned**     | Acknowledged, not started                             |
| **In Progress** | Actively being worked on                              |
| **Blocked**     | Cannot proceed without input, decision, or dependency |
| **Done**        | Complete                                              |
| **Archived**    | Was planned, no longer pursuing (kept for history)    |

---

## Priority

| Priority     | Level   |
| ------------ | ------- |
| **Critical** | Highest |
| **High**     |         |
| **Medium**   |         |
| **Low**      | Lowest  |

---

## Critical

### PB-001: Initialize Python engine package structure

**Description:**
Create the foundational Python package layout for the ProjectBridge engine under `engine/projectbridge/`. This includes the top-level `__init__.py`, subpackage directories for each major component (analysis, ai, recommend, input, config), a `requirements.txt`, and a `pyproject.toml` or `setup.py` for installability. Every other engine item depends on this skeleton existing first. The package should be importable locally with `pip install -e .` for development.

**Acceptance Criteria:**

1. Running `pip install -e ./engine` in a clean virtualenv succeeds without errors.
2. `import projectbridge` in a Python REPL returns without error after install.
3. Subpackage directories `analysis/`, `ai/`, `recommend/`, `input/`, and `config/` each contain an `__init__.py`.

**Metadata:**

- **Status:** Done
- **Priority:** Critical
- **Depends on:** —
- **Blocks:** PB-002, PB-003, PB-004, PB-005, PB-006, PB-007, PB-008

---

### PB-002: Define output schema v1.0

**Description:**
Create the versioned JSON schema that defines the contract between the engine and all consumers (CLI, UI, export). The schema must include top-level fields for `schema_version`, `strengths`, `gaps`, and `recommendations` as described in the README and tech spec. A JSON Schema file should live in `docs/schema/` and a Python dataclass or Pydantic model should represent it in the engine. This contract must be stable — UI and export features depend on it.

**Acceptance Criteria:**

1. A JSON Schema file at `docs/schema/analysis_output_v1.0.json` validates the documented output structure.
2. A Python model in `engine/projectbridge/schema.py` can serialize and deserialize a valid analysis result.
3. The `schema_version` field is present and set to `"1.0"` in all generated output.
4. An invalid payload (e.g., missing `recommendations`) raises a validation error when loaded through the model.

**Metadata:**

- **Status:** Done
- **Priority:** Critical
- **Depends on:** PB-001
- **Blocks:** PB-008, PB-012, PB-014

---

### PB-003: Implement configuration model

**Description:**
Build the configuration system that reads `projectbridge.config.yaml` and exposes typed settings to all engine components. Configuration governs AI provider selection, analysis thresholds, recommendation limits, and export preferences as described in Section 7 of the tech spec. The config model should provide sensible defaults so the engine works with no config file present, and should validate unknown keys to prevent silent misconfiguration.

**Acceptance Criteria:**

1. The engine loads configuration from `projectbridge.config.yaml` when the file exists in the working directory.
2. When no config file is present, all settings resolve to documented defaults without error.
3. Setting an unrecognized key in the config file produces a warning or validation error.

**Metadata:**

- **Status:** Done
- **Priority:** Critical
- **Depends on:** PB-001
- **Blocks:** PB-006, PB-007, PB-008, PB-012

---

### PB-004: Build GitHub repository analyzer

**Description:**
Implement the primary input processor that extracts signals from GitHub repositories. The analyzer should use the GitHub API (authenticated via a user-provided token) to retrieve repository metadata, language breakdowns, file trees, and key configuration files. It normalizes this data into a unified context model consumed by the analysis layer. As described in Section 5.2 of the tech spec, it operates on metadata and structure rather than deep static analysis to maintain performance and privacy.

**Acceptance Criteria:**

1. Given a GitHub username and valid token, the analyzer returns a context dict containing `languages`, `frameworks`, `project_structures`, and `infrastructure_signals`.
2. The analyzer detects at least languages, common frameworks (e.g., React, Django, Flask), and infrastructure markers (e.g., Dockerfile, CI config).
3. When given an invalid token or unreachable API, a descriptive error is raised (not an unhandled exception).
4. The analyzer respects GitHub API rate limits and reports remaining quota.

**Metadata:**

- **Status:** Done
- **Priority:** Critical
- **Depends on:** PB-001
- **Blocks:** PB-006, PB-012

---

### PB-005: Build job description parser

**Description:**
Implement the required input processor that extracts structured requirements from raw job description text. The parser should identify required technologies, implied experience domains, and architectural expectations as described in Section 5.2 of the tech spec. It produces a normalized requirements model that the analysis layer uses for gap detection. The parser should handle common job description formats including bullet lists, paragraph prose, and mixed formats.

**Acceptance Criteria:**

1. Given a plain-text job description, the parser returns a dict with `required_technologies`, `experience_domains`, and `architectural_expectations`.
2. The parser handles both bullet-list and prose-paragraph formats without error.
3. Empty or whitespace-only input produces a clear validation error, not an empty result.
4. Output conforms to a documented requirements schema that the analysis layer can consume.

**Metadata:**

- **Status:** Done
- **Priority:** Critical
- **Depends on:** PB-001
- **Blocks:** PB-006, PB-012

---

### PB-006: Implement core analysis layer

**Description:**
Build the analysis modules that compare GitHub-derived developer context against job requirements to produce `detected_skills`, `adjacent_skills`, and `missing_skills` as described in Section 5.3 of the tech spec. This is the central logic of ProjectBridge. The analysis layer must remain deterministic — AI is restricted to later interpretation and recommendation stages. The layer consumes normalized input from PB-004 and PB-005 and produces intermediate signals for the recommendation engine.

**Acceptance Criteria:**

1. Given a developer context and job requirements, the layer returns a dict with `detected_skills`, `adjacent_skills`, and `missing_skills` lists.
2. A skill present in both the developer context and job requirements appears in `detected_skills`.
3. The analysis is deterministic — identical inputs always produce identical outputs.
4. Adjacent skills are derived from a skill relationship mapping (not arbitrary).

**Metadata:**

- **Status:** Done
- **Priority:** Critical
- **Depends on:** PB-001, PB-003, PB-004, PB-005
- **Blocks:** PB-009, PB-012

---

### PB-007: Define AI provider base interface and NoAI fallback

**Description:**
Create the abstract base class for AI providers as specified in Section 5.4 of the tech spec, with `analyze_context` and `generate_recommendations` methods. Also implement the `NoAIProvider` fallback that uses heuristic logic to fulfill the same interface without any external API calls. This establishes the architectural boundary that isolates AI from core logic and ensures the engine always works with `--no-ai`. All concrete AI providers (OpenAI, Claude, Ollama) will extend this base.

**Acceptance Criteria:**

1. An abstract `AIProvider` base class exists with `analyze_context(context: dict) -> dict` and `generate_recommendations(gaps: dict) -> list` methods.
2. A `NoAIProvider` class implements the interface using heuristic logic and returns valid results without any API keys or network calls.
3. A provider registry or factory function returns the correct provider based on configuration.

**Metadata:**

- **Status:** Done
- **Priority:** Critical
- **Depends on:** PB-001, PB-003
- **Blocks:** PB-009, PB-012, PB-015, PB-020, PB-027

---

### PB-008: Build CLI contract

**Description:**
Implement the command-line interface as the primary user-facing entry point to ProjectBridge. The CLI must support the `analyze` and `export` commands with flags documented in Section 8 of the tech spec (`--job`, `--github-user`, `--output`, `--no-ai`, `--example`). It orchestrates input processors, analysis, and output generation. The CLI contract must remain stable across versions as it is the interface the Tauri UI will call.

**Acceptance Criteria:**

1. `projectbridge analyze --help` displays usage information including all documented flags.
2. `projectbridge analyze --example` completes successfully and writes valid JSON to stdout or a file.
3. `projectbridge analyze --job job.txt --github-user testuser --output result.json` invokes the full pipeline and produces output.
4. `projectbridge analyze --no-ai` runs the full pipeline using only the NoAI heuristic provider.
5. Exit codes are non-zero on failure and zero on success.

**Metadata:**

- **Status:** Done
- **Priority:** Critical
- **Depends on:** PB-001, PB-002, PB-003
- **Blocks:** PB-010, PB-017

---

## High

### PB-009: Build recommendation engine

**Description:**
Implement the recommendation engine described in Section 5.5 of the tech spec. It converts detected skill gaps into small, realistic project suggestions that a developer can complete and add to their portfolio. Recommendations must be completable (not multi-month scope), prioritize demonstrability over novelty, and include enough detail for a developer to start immediately. The engine consumes analysis output and optionally uses an AI provider for enhanced suggestions.

**Acceptance Criteria:**

1. Given a gaps dict with `missing_skills`, the engine returns a list of project recommendations each including `title`, `description`, `skills_addressed`, and `estimated_scope`.
2. In NoAI mode, the engine produces heuristic-based recommendations from templates.
3. When an AI provider is configured, recommendations include AI-enhanced descriptions.
4. No recommendation addresses more than 3 skills simultaneously (to keep scope manageable).

**Metadata:**

- **Status:** Done
- **Priority:** High
- **Depends on:** PB-006, PB-007
- **Blocks:** PB-012, PB-022

---

### PB-010: Build example mode with bundled data

**Description:**
Implement the `--example` flag that allows users to try ProjectBridge without any setup — no GitHub token, no AI provider, no job description file. The example mode should bundle a realistic sample developer profile and job description, run the full analysis pipeline against them, and produce output identical in structure to a real analysis. This is the primary onboarding path described in the README quickstart section.

**Acceptance Criteria:**

1. `projectbridge analyze --example` runs to completion without requiring any environment variables or config.
2. Output from example mode passes schema validation against the v1.0 output schema.
3. Example mode exercises the same code paths as a real analysis (not a separate hardcoded response).
4. `projectbridge export --example` produces an export artifact from the bundled example data.

**Metadata:**

- **Status:** Done
- **Priority:** High
- **Depends on:** PB-008
- **Blocks:** —

---

### PB-011: Implement skill taxonomy and adjacency map

**Description:**
Build the data structure that maps known skills, technologies, and frameworks to each other with adjacency relationships. The analysis layer (PB-006) depends on this map to determine `adjacent_skills` — technologies that are related to what a developer already knows and represent natural growth paths. The taxonomy should be data-driven (loaded from a file or structured constant) rather than hardcoded in analysis logic, making it extensible by contributors.

**Acceptance Criteria:**

1. A taxonomy data file or module exists that defines skills and their adjacency relationships.
2. Querying the taxonomy for "React" returns adjacent skills like "Next.js", "TypeScript", "Redux".
3. The taxonomy contains at least 50 skills across frontend, backend, infrastructure, and data domains.
4. Adding a new skill and its adjacencies requires only data changes, not code changes.

**Metadata:**

- **Status:** Done
- **Priority:** High
- **Depends on:** PB-001
- **Blocks:** PB-006

---

### PB-012: Implement engine orchestrator

**Description:**
Build the orchestrator module that coordinates the full analysis pipeline: loading configuration, invoking input processors, running analysis, calling the AI provider (if configured), generating recommendations, and producing structured output. This is the central coordination point that the CLI and Tauri UI both call. It should accept a request object and return a complete analysis result conforming to the output schema.

**Acceptance Criteria:**

1. A single `run_analysis(request)` function or method executes the complete pipeline and returns a schema-valid result.
2. Passing `no_ai=True` skips the AI provider step and uses the NoAI fallback.
3. Errors in any pipeline stage produce descriptive error messages with the failing stage identified.
4. The orchestrator is callable from both the CLI module and a Python API (not CLI-only).

**Metadata:**

- **Status:** Done
- **Priority:** High
- **Depends on:** PB-002, PB-003, PB-004, PB-005, PB-006, PB-007, PB-009
- **Blocks:** PB-008

---

### PB-013: Add resume context processor

**Description:**
Implement the optional input processor for resume text as described in Section 5.2 of the tech spec. Resume input is treated as contextual enrichment only — it may influence interpretation but must not override GitHub-derived signals. The processor should extract skills, experience domains, and years of experience from common resume formats (plain text and basic structured text). This provides supplementary context for more nuanced analysis.

**Acceptance Criteria:**

1. Given plain-text resume content, the processor returns a dict with `skills`, `experience_domains`, and `years_of_experience` (if detectable).
2. Resume-derived data is merged into the analysis context as a secondary signal, not a primary override.
3. The analysis pipeline runs correctly when no resume is provided (resume is optional).
4. The CLI accepts a `--resume` flag that passes resume text to the processor.

**Metadata:**

- **Status:** Done
- **Priority:** High
- **Depends on:** PB-001
- **Blocks:** PB-012

---

### PB-014: Implement JSON export and shareable snapshot

**Description:**
Build the export functionality that takes a completed analysis result and produces a shareable snapshot file. The README describes generating "a shareable skill-gap snapshot" as a core feature. The export should write a self-contained JSON file that includes the analysis result, metadata (timestamp, engine version, schema version), and enough context to be interpretable without the engine. The `export` CLI command triggers this.

**Acceptance Criteria:**

1. `projectbridge export --input result.json --output snapshot.json` produces a valid snapshot file.
2. The snapshot includes analysis results, `exported_at` timestamp, `engine_version`, and `schema_version`.
3. The snapshot file passes schema validation independently (without the engine running).
4. Exporting from example mode (`--example`) works without requiring a prior analysis run.

**Metadata:**

- **Status:** Done
- **Priority:** High
- **Depends on:** PB-002
- **Blocks:** PB-026, PB-031

---

### PB-015: Implement OpenAI AI provider

**Description:**
Build the first concrete AI provider implementation using the OpenAI API. This provider implements the `AIProvider` interface (PB-007) and calls OpenAI models to enhance context interpretation and recommendation generation. The provider must handle API key management (read from environment or config), respect rate limits, and produce output that conforms to the expected provider response format. Prompts should be transparent and stored as editable templates.

**Acceptance Criteria:**

1. The OpenAI provider implements `analyze_context` and `generate_recommendations` from the base interface.
2. The provider reads the API key from `OPENAI_API_KEY` environment variable or config file, and produces a descriptive error when the key is missing or invalid.
3. Prompts sent to the API are stored as editable template files in the package.
4. The provider is selectable via config: `ai_provider: openai`.

**Metadata:**

- **Status:** Done
- **Priority:** High
- **Depends on:** PB-007
- **Blocks:** —

---

### PB-016: Add test infrastructure and CI

**Description:**
Set up the testing framework and continuous integration pipeline for the engine. This includes pytest configuration, test directory structure mirroring the source layout, fixture utilities for common test scenarios (mock GitHub responses, sample job descriptions), and a GitHub Actions workflow that runs tests on push and PR. Test infrastructure is essential for maintaining quality as the engine grows and for contributor confidence.

**Acceptance Criteria:**

1. `pytest engine/tests/` runs and discovers tests from a structured test directory.
2. A `conftest.py` provides shared fixtures for mock GitHub API responses and sample input data.
3. A GitHub Actions workflow at `.github/workflows/test.yml` runs pytest on push to `main` and on pull requests.
4. At least one integration test exercises the full pipeline in example mode.

**Metadata:**

- **Status:** Done
- **Priority:** High
- **Depends on:** PB-001
- **Blocks:** —

---

## Medium

### PB-017: Scaffold Tauri desktop application

**Description:**
Initialize the Tauri application shell under `app/` that wraps the engine's output in a desktop UI. The scaffold should include the Tauri project configuration, a minimal frontend framework (e.g., React or Svelte with TypeScript), and the IPC bridge for calling the Python engine CLI. Per DEC-003, Tauri is chosen for lightweight desktop distribution. The UI is a visualization layer only — no business logic.

**Acceptance Criteria:**

1. `npm run dev` in the `app/` directory launches a Tauri development window.
2. The Tauri app can invoke `projectbridge analyze --example` via IPC and receive JSON output.
3. The project structure includes `src-tauri/` for Rust backend and a frontend source directory with a basic view rendering.
4. `npm run build` produces a distributable desktop application binary.

**Metadata:**

- **Status:** Done
- **Priority:** Medium
- **Depends on:** PB-008
- **Blocks:** PB-018, PB-019, PB-031

---

### PB-018: Tauri UI — analysis dashboard view

**Description:**
Build the primary results view in the Tauri application that displays a completed analysis. The dashboard should visualize detected skills (strengths), skill gaps, adjacent skills, and project recommendations in an organized layout. It consumes the v1.0 output schema and renders it without any business logic — all data comes from the engine. The view should be clear and actionable, helping users understand their position and next steps at a glance.

**Acceptance Criteria:**

1. The dashboard renders `strengths`, `gaps`, and `recommendations` sections from a valid analysis JSON.
2. Each recommendation displays its title, description, and skills addressed.
3. The view handles empty arrays gracefully (e.g., "No gaps detected" message).
4. The layout is responsive and readable at common desktop window sizes (1024px+).

**Metadata:**

- **Status:** Done
- **Priority:** Medium
- **Depends on:** PB-017
- **Blocks:** —

**Done:** Polished dashboard with summary stat cards (strengths/gaps/recommendations counts), skill grouping by category (Languages, Frameworks, Infrastructure, Tools, Concepts), color-coded scope badges on recommendations (green/amber/red for small/medium/large), dismissable error banner, and card-based layout for strengths and gaps sections.

---

### PB-019: Tauri UI — analysis input form

**Description:**
Build the input form view in the Tauri application where users enter their GitHub username, paste or upload a job description, and optionally provide resume text. The form should validate inputs before submission and invoke the engine via IPC. It should support the same options available in the CLI (GitHub user, job text, no-ai toggle) and display progress feedback while the engine runs.

**Acceptance Criteria:**

1. The form includes fields for GitHub username, job description text, and an optional resume text area.
2. Submitting the form invokes `projectbridge analyze` via Tauri IPC with the provided inputs.
3. Client-side validation prevents submission when required fields (GitHub user, job description) are empty.
4. On completion, the view navigates to the dashboard (PB-018) with the results.

**Metadata:**

- **Status:** Done
- **Priority:** Medium
- **Depends on:** PB-017
- **Blocks:** —

**Done:** Built input form with GitHub username, job description (required), resume text (optional), and no-AI toggle. Client-side validation shows inline errors for empty required fields. Form submits via `run_analysis_form` Tauri IPC command. Added `--job-text` and `--resume-text` inline CLI flags (mutually exclusive with `--job`/`--resume`). View switches from form → loading → results dashboard on completion. "Run Example Instead" button preserved. 2 new integration tests (133 total).

---

### PB-020: Add Anthropic Claude AI provider

**Description:**
Build a second AI provider implementation using the Anthropic Claude API. This provider implements the same `AIProvider` interface as the OpenAI provider, offering users a choice of AI backend. It should follow the same patterns established in PB-015: key management via environment variable or config, editable prompt templates, and graceful error handling. Having multiple providers validates the pluggable architecture from DEC-004.

**Acceptance Criteria:**

1. The Claude provider implements `analyze_context` and `generate_recommendations` from the base interface.
2. The provider reads the API key from `ANTHROPIC_API_KEY` environment variable or config file, and produces a descriptive error when the key is missing or invalid.
3. The provider is selectable via config: `ai_provider: anthropic`.

**Metadata:**

- **Status:** Done
- **Priority:** Medium
- **Depends on:** PB-007
- **Blocks:** —

---

### PB-021: Enhance framework detection heuristics

**Description:**
Improve the GitHub repository analyzer's ability to detect frameworks, libraries, and tools beyond basic language identification. The README roadmap lists "improved repository detection heuristics" as a short-term goal. This includes detecting frameworks from dependency files (package.json, requirements.txt, Cargo.toml), configuration files (webpack, tsconfig, docker-compose), and project structure patterns. Better detection directly improves analysis accuracy.

**Acceptance Criteria:**

1. The analyzer detects frameworks from dependency manifests (package.json dependencies, requirements.txt, Gemfile, etc.).
2. Infrastructure tools are detected from config files (Dockerfile, docker-compose.yml, .github/workflows/).
3. At least 20 frameworks/tools are detectable beyond raw language identification.
4. Detection logic is organized as a registry of heuristic rules, not a monolithic if-else chain.

**Metadata:**

- **Status:** Done
- **Priority:** Medium
- **Depends on:** PB-004
- **Blocks:** —

---

### PB-022: Implement recommendation templates

**Description:**
Build a template system for the recommendation engine that maps common skill gaps to pre-written project suggestions. The README roadmap includes "better project recommendation templates" as a short-term goal. Templates provide high-quality baseline recommendations even in NoAI mode and serve as seeds that AI providers can enhance. Templates should be data-driven and contributor-extensible — adding a new recommendation template should require no code changes.

**Acceptance Criteria:**

1. A templates data file or directory exists containing structured recommendation templates each with `title`, `description`, `skills_addressed`, `estimated_scope`, and `difficulty`.
2. The recommendation engine selects relevant templates based on the skills in the gap analysis.
3. Adding a new template requires only adding a data entry, not modifying engine code.
4. At least 15 templates exist covering frontend, backend, infrastructure, and full-stack gaps.

**Metadata:**

- **Status:** Done
- **Priority:** Medium
- **Depends on:** PB-009
- **Blocks:** —

---

### PB-023: Add structured logging and error handling

**Description:**
Implement a consistent logging and error handling strategy across the engine. Currently there is no logging infrastructure. The engine should use Python's `logging` module with structured output (JSON format for machine consumption, readable format for CLI). Error handling should produce user-friendly messages at the CLI level while preserving full tracebacks for debugging. This improves debuggability for contributors and usability for end users.

**Acceptance Criteria:**

1. All engine modules use the `logging` module with a consistent logger naming convention (`projectbridge.*`).
2. A `--verbose` CLI flag increases log output to DEBUG level.
3. Unhandled exceptions at the CLI boundary produce a user-friendly message and a non-zero exit code.

**Metadata:**

- **Status:** Done
- **Priority:** Medium
- **Depends on:** PB-001, PB-008
- **Blocks:** —

---

### PB-024: Implement GitHub token management

**Description:**
Build secure, user-friendly GitHub token handling for the repository analyzer. Tokens should be readable from environment variables (`GITHUB_TOKEN`), the config file, or an interactive prompt. The engine must never log, display, or write tokens to output files. Per the project's privacy principles, tokens never leave the user's machine. The implementation should also support unauthenticated access (with reduced rate limits) for public repositories.

**Acceptance Criteria:**

1. The analyzer reads a GitHub token from the `GITHUB_TOKEN` environment variable or `projectbridge.config.yaml`.
2. Tokens are never included in log output, analysis results, or export files.
3. The analyzer works without a token for public repositories (with appropriate rate-limit warnings).

**Metadata:**

- **Status:** Done
- **Priority:** Medium
- **Depends on:** PB-003, PB-004
- **Blocks:** —

---

### PB-025: Add input validation layer

**Description:**
Implement centralized input validation for all data entering the engine: CLI arguments, job description text, GitHub usernames, resume content, and configuration values. Validation should happen early in the pipeline (before any processing) and produce clear, actionable error messages. This prevents confusing downstream errors and improves the user experience. Validation rules should be colocated with input models rather than scattered across the codebase.

**Acceptance Criteria:**

1. Invalid GitHub usernames (empty, containing spaces, too long) produce a specific validation error.
2. All validation errors include the field name and a human-readable description of the constraint.
3. Validation runs before any API calls or expensive processing.
4. Validation logic is testable independently of CLI or orchestrator code.

**Metadata:**

- **Status:** Done
- **Priority:** Medium
- **Depends on:** PB-001
- **Blocks:** —

---

## Low

### PB-026: Add Markdown export format

**Description:**
Extend the export system (PB-014) to support Markdown output in addition to JSON. A Markdown export produces a human-readable document summarizing the analysis — suitable for sharing in GitHub READMEs, portfolio pages, or documents. The export should include sections for strengths, gaps, and recommendations formatted as readable prose with lists and headers. This is an alternative output format, not a replacement for JSON.

**Acceptance Criteria:**

1. `projectbridge export --format markdown --input result.json --output snapshot.md` produces a valid Markdown file.
2. The Markdown output includes sections for Strengths, Skill Gaps, and Recommendations with readable formatting.
3. The `--format` flag defaults to `json` when not specified (backward compatible).

**Metadata:**

- **Status:** Done
- **Priority:** Low
- **Depends on:** PB-014
- **Blocks:** —

**Done:** Added `render_markdown()` to export module producing a formatted Markdown document with Strengths, Skill Gaps, Recommendations sections. CLI `--format markdown` flag added to `export` command. Enum values render as lowercase strings. Footer includes version and timestamp. 6 new export tests + 1 CLI integration test (140 total).

---

### PB-027: Add Ollama local AI provider

**Description:**
Build an AI provider implementation that uses Ollama for fully local AI inference with no external API calls. This is the most privacy-preserving AI option — no data leaves the machine at all. The provider should detect whether Ollama is running locally, list available models, and use a configured model for analysis and recommendations. This aligns with the project's local-first philosophy and offers users complete data sovereignty.

**Acceptance Criteria:**

1. The Ollama provider implements the `AIProvider` interface with `analyze_context` and `generate_recommendations`.
2. The provider detects whether Ollama is running at `localhost:11434` and produces a clear error if not.
3. The provider is selectable via config: `ai_provider: ollama` with an optional `ollama_model` setting.

**Metadata:**

- **Status:** Done
- **Priority:** Low
- **Depends on:** PB-007
- **Blocks:** —

**Done:** Created `engine/projectbridge/ai/ollama_provider.py` using stdlib `urllib.request` (zero extra deps). Calls Ollama REST API at `localhost:11434/api/chat` with `stream: false` and `format: json`. Server reachability check on init. Model configurable via `ai.ollama_model` config key. Orchestrator passes model kwarg for ollama provider. 13 tests with mocked HTTP (153 total).

---

### PB-028: Add repository caching layer

**Description:**
Implement a local caching mechanism for GitHub API responses to reduce redundant API calls and improve performance on repeated analyses. The cache should store repository metadata, language stats, and file tree data with a configurable TTL (time-to-live). This is especially valuable for users iterating on job descriptions against the same set of repositories. The cache should be transparent — analysis results must be identical whether served from cache or fresh API calls.

**Acceptance Criteria:**

1. Repeated analysis of the same GitHub user within the TTL window does not make additional API calls.
2. Cache TTL is configurable via `projectbridge.config.yaml` (default: 1 hour).
3. A `--no-cache` CLI flag forces fresh API calls regardless of cache state.
4. Analysis results are identical whether produced from cached or fresh data.

**Metadata:**

- **Status:** Done
- **Priority:** Low
- **Depends on:** PB-004, PB-003
- **Blocks:** —

**Done:** Created `engine/projectbridge/input/cache.py` — file-based JSON cache under `~/.cache/projectbridge/`, SHA-256 hashed keys, configurable TTL. Integrated into `GitHubClient._request` with `cache_enabled` and `cache_ttl` params. Added `--no-cache` CLI flag. Orchestrator reads `config.cache.enabled` and `config.cache.ttl_seconds`. 5 cache tests (158 total).

---

### PB-029: Add progress indicators to CLI

**Description:**
Enhance the CLI experience with progress indicators for long-running operations such as GitHub API fetching, AI provider calls, and analysis processing. The current CLI will run silently during these operations, which can take several seconds. Progress indicators (spinners, step announcements, or progress bars) provide feedback that the tool is working and help users identify which stage is running or stalled.

**Acceptance Criteria:**

1. The CLI displays a spinner or status message during GitHub API calls.
2. Each major pipeline stage (input processing, analysis, AI, recommendations) announces when it starts.
3. Progress output does not interfere with JSON output on stdout (suppressed in non-TTY or piped contexts).

**Metadata:**

- **Status:** Done
- **Priority:** Low
- **Depends on:** PB-008
- **Blocks:** —

**Done:** Created `engine/projectbridge/progress.py` with `Progress` class — step announcements and braille spinners to stderr. Auto-detects TTY (silent when piped). Integrated into orchestrator at each pipeline stage: provider resolution, GitHub fetch (with spinner), resume processing, job parsing, AI analysis (with spinner), skill analysis, recommendations. CLI creates `Progress()` automatically. 158 tests still passing.

---

### PB-030: Add documentation site scaffold

**Description:**
Set up a static documentation site (e.g., using MkDocs or Sphinx) that publishes the project's existing documentation in a browsable, searchable format. The site should include the README, tech spec, contributing guide, schema documentation, and API reference. This makes the project more approachable for potential contributors and users who prefer browsing docs over reading raw Markdown files in the repo.

**Acceptance Criteria:**

1. A documentation site builds from existing Markdown files in the repository.
2. The site includes navigation for README, Technical Spec, Contributing, and Schema docs.
3. A local serve command builds and previews the site during development.

**Metadata:**

- **Status:** Done
- **Priority:** Low
- **Depends on:** —
- **Blocks:** —

**Done:** Scaffolded MkDocs Material site. `mkdocs.yml` at repo root, source files in `site_src/` using `include-markdown` plugin to reference existing docs. Nav includes Home, Technical Spec, Contributing, Decisions, Backlog, Security. `mkdocs build` generates to `site/` (gitignored). `mkdocs serve` for local preview.

---

### PB-031: Tauri UI — export and share screen

**Description:**
Build the export view in the Tauri application that allows users to export their analysis results in supported formats (JSON, Markdown) and optionally copy a shareable snapshot to the clipboard. The view should display a preview of the export output and provide format selection. This completes the Tauri UI workflow: input (PB-019) → dashboard (PB-018) → export (this item).

**Acceptance Criteria:**

1. The export screen displays a preview of the analysis output in the selected format.
2. Users can select between JSON and Markdown export formats.
3. A "Save" button writes the export to a user-selected file path via native file dialog.
4. A "Copy to Clipboard" button copies the export content to the system clipboard.

**Metadata:**

- **Status:** Done
- **Priority:** Low
- **Depends on:** PB-014, PB-017
- **Blocks:** —

**Done:** Built export view with Markdown/JSON format toggle, live preview via `export_analysis` Tauri IPC command, "Save to File" button using native file dialog (`tauri-plugin-dialog`), and "Copy to Clipboard" button (`tauri-plugin-clipboard-manager`). Added `tauri-plugin-fs` for file writing. Export accessible from dashboard header and bottom actions. Full flow: input → results → export.

---

### PB-032: Add developer contribution tooling

**Description:**
Set up development tooling that makes contributing easier and maintains code quality. This includes a code formatter (e.g., Black, Ruff), a linter, pre-commit hooks, and a Makefile or task runner with common commands (`make test`, `make lint`, `make format`). Good tooling reduces friction for contributors and ensures consistent code style. The CONTRIBUTING.md should be updated to reference these tools.

**Acceptance Criteria:**

1. `make lint` and `make format` (or equivalent) run linting and auto-formatting across the engine codebase.
2. Pre-commit hooks are configured to run formatting and linting before each commit.
3. `CONTRIBUTING.md` is updated to document the development tooling setup.

**Metadata:**

- **Status:** Done
- **Priority:** Low
- **Depends on:** PB-001
- **Blocks:** —

---

## Parking Lot

_Ideas worth remembering — not yet actionable or fully defined._

- **Multi-job comparison:** Analyze a developer profile against multiple job descriptions simultaneously to identify the highest-leverage skills to learn. Would require a comparison output schema extension.

- **Historical tracking:** Store analysis results over time and show progress as a developer builds projects and acquires new skills. Would require a local database or structured file store.

- **Team mode:** Allow a team lead to run ProjectBridge across multiple team members' profiles against a shared set of job descriptions. Raises privacy and consent considerations.

- **Custom skill taxonomies:** Let users define their own skill adjacency maps or override the built-in taxonomy for niche domains (e.g., embedded systems, bioinformatics).

- **Learning platform integration:** Enrich recommendations with links to relevant courses or tutorials from platforms like freeCodeCamp, Exercism, or official documentation.

- **VSCode extension:** Provide a lightweight ProjectBridge integration as a VSCode extension that shows skill gap insights alongside code, without requiring the full Tauri app.

- **Portfolio generator:** Automatically generate a portfolio page or README section from a ProjectBridge analysis showing a developer's strengths and growth trajectory.

- **Alternative input sources (GitLab/Bitbucket):** Extend the repository analyzer to support GitLab and Bitbucket in addition to GitHub, broadening the user base.

---

## Documented Gaps

_Known limitations accepted by design._

- **No deep static analysis.** The GitHub analyzer operates on metadata and structure, not source code ASTs. This is intentional for performance and privacy (see DEC-001, Tech Spec Section 5.2).

- **AI recommendations are non-deterministic.** When an AI provider is used, recommendations may vary between runs for identical inputs. This is accepted; core analysis (detected/adjacent/missing skills) remains deterministic.

- **Single-user scope.** The system is designed for individual developers analyzing their own profiles. Multi-user or team features are deferred to the parking lot.

---

## Done

### PB-001: Initialize Python engine package structure

**Status:** Done

Created the foundational Python package layout under `engine/projectbridge/` with subpackages for `ai/`, `analysis/`, `config/`, `input/`, and `recommend/`. Includes `pyproject.toml` (PEP 621, setuptools, Python >=3.10), `requirements.txt` (pyyaml, pydantic), and root `__init__.py` exposing `__version__ = "0.1.0"`. Verified with `pip install -e ./engine` and successful import of all subpackages.

---

### PB-002: Define output schema v1.0

**Status:** Done

Created JSON Schema at `docs/schema/analysis_output_v1.0.json` and Pydantic models in `engine/projectbridge/schema.py`. Schema defines `schema_version`, `strengths`, `gaps`, and `recommendations` with `Skill` and `Recommendation` sub-models. All fields required; missing fields raise `ValidationError`. Verified serialize/deserialize roundtrip, schema_version default, and validation of invalid payloads.

---

### PB-003: Implement configuration model

**Status:** Done

Created `engine/projectbridge/config/settings.py` with Pydantic-based config model loading from `projectbridge.config.yaml`. Sections: `ai` (provider, ollama_model), `analysis` (max_recommendations), `cache` (enabled, ttl_seconds), `export` (default_format). All fields have sensible defaults. Unknown keys produce warnings. Verified loading from YAML, defaults without config file, and unknown key warnings.

---

### PB-004: Build GitHub repository analyzer

**Status:** Done

Created `engine/projectbridge/input/github.py` with `GitHubAnalyzer` and `GitHubClient` classes. Extracts languages (with percentages), frameworks (React, Django, Flask, Express, etc.), project structures, and infrastructure signals (Docker, CI) from a user's public repos via the GitHub REST API. Custom exceptions for auth errors, user-not-found, rate limits, and connectivity issues. Rate limit tracking from response headers. Added `requests` dependency.

---

### PB-005: Build job description parser

**Status:** Done

Created `engine/projectbridge/input/job_description.py` with `parse_job_description()` and `JobRequirements` Pydantic model. Extracts `required_technologies`, `experience_domains`, and `architectural_expectations` via keyword matching with word-boundary regex. Handles bullet-list, prose, and mixed formats. Empty input raises `EmptyJobDescriptionError`. Covers 70+ technologies, 20+ domains, and 20+ architectural patterns.

---

### PB-006: Implement core analysis layer

**Status:** Done

Created `engine/projectbridge/analysis/engine.py` with `analyze()` function that compares developer context against job requirements. Produces `detected_skills` (intersection), `adjacent_skills` (reachable via taxonomy and required), and `missing_skills` (required but not detected or adjacent). Fully deterministic. Uses the skill taxonomy from PB-011.

---

### PB-011: Implement skill taxonomy and adjacency map

**Status:** Done

Created `engine/projectbridge/analysis/taxonomy.py` with 71 skills across language, framework, infrastructure, and tool categories. Each skill maps to adjacent skills representing natural growth paths. Data-driven dict constant — adding skills requires only data changes. Implemented alongside PB-006.

---

### PB-007: Define AI provider base interface and NoAI fallback

**Status:** Done

Created `engine/projectbridge/ai/provider.py` with abstract `AIProvider` base class (`analyze_context`, `generate_recommendations`) and a provider registry with `get_provider()` factory. Created `engine/projectbridge/ai/no_ai.py` with `NoAIProvider` that generates heuristic recommendations from skill gaps without any API keys or network calls. Unknown provider names raise `ValueError`.

---

### PB-008: Build CLI contract

**Status:** Done

Created `engine/projectbridge/cli.py` with `projectbridge` console script entry point. Supports `analyze` (--job, --github-user, --output, --no-ai, --example) and `export` (--input, --output, --format, --example) commands. Added entry point in pyproject.toml. Non-zero exit codes on failure, zero on success.

---

### PB-009: Build recommendation engine

**Status:** Done

Created `engine/projectbridge/recommend/engine.py` with `generate_recommendations()` that delegates to the active AI provider, enforces max-3 skills per recommendation, caps total recommendations, and returns schema-valid `Recommendation` objects. Implemented alongside PB-008.

---

### PB-012: Implement engine orchestrator

**Status:** Done

Created `engine/projectbridge/orchestrator.py` with `run_analysis()` that coordinates the full pipeline: config loading, AI provider resolution, GitHub analysis, job parsing, core analysis, and recommendations. Includes bundled example data for --example mode. `PipelineError` identifies the failing stage. Callable from CLI and Python API. Implemented alongside PB-008.

---

### PB-010: Build example mode with bundled data

**Status:** Done

Already implemented as part of PB-008/PB-012. Bundled example developer profile and job description in `orchestrator.py`. `projectbridge analyze --example` and `projectbridge export --example` both work without any env vars, tokens, or config. Example mode exercises the full pipeline (job parser, analysis engine, recommendation engine) — not a hardcoded response.

---

### PB-013: Add resume context processor

**Status:** Done

Created `engine/projectbridge/input/resume.py` with `parse_resume()` and `ResumeContext` model. Extracts skills, experience domains, and years of experience via keyword matching. `merge_resume_context()` adds resume skills as `resume_skills` secondary signal without overriding GitHub-derived data. Analysis engine reads `resume_skills` to enrich developer skill set. Added `--resume FILE` flag to CLI and `resume_text` parameter to `run_analysis()`.

---

### PB-014: Implement JSON export and shareable snapshot

**Status:** Done

Created `engine/projectbridge/export.py` with `Snapshot` model and `create_snapshot()`. Snapshots wrap the analysis result with `exported_at` (ISO 8601), `engine_version`, and `schema_version` metadata. Updated CLI export command to produce snapshots from `--input FILE` or `--example`. Snapshots validate independently via the `Snapshot` Pydantic model.

---

### PB-016: Add test infrastructure and CI

**Status:** Done

Set up pytest test infrastructure with `engine/tests/conftest.py` providing shared fixtures (sample dev contexts, job texts, resume text, mock GitHub responses). Created 8 test files covering all modules: schema, config, job description parser, GitHub analyzer, analysis engine, AI provider, resume processor, export, and full integration pipeline. 57 tests total, all passing. Added GitHub Actions workflow at `.github/workflows/test.yml` running pytest on push to main and PRs with Python 3.10 and 3.12 matrix.

---

### PB-015: Implement OpenAI AI provider

**Status:** Done

Created `engine/projectbridge/ai/openai_provider.py` implementing the `AIProvider` interface with OpenAI API. Reads API key from `OPENAI_API_KEY` env var or constructor parameter. Uses `gpt-4o` by default with JSON response format. Editable prompt templates stored in `engine/projectbridge/ai/prompts/` (analyze_context.txt, generate_recommendations.txt). Handles auth errors, rate limits, and connection failures with descriptive `OpenAIProviderError` messages. Registered as `"openai"` provider. Added `openai>=1.0` as optional dependency. 16 new tests covering init, registry, context enrichment, recommendations, error handling, and template files.

---

### PB-020: Add Anthropic Claude AI provider

**Status:** Done

Created `engine/projectbridge/ai/anthropic_provider.py` implementing the `AIProvider` interface with Anthropic Claude API. Mirrors the OpenAI provider pattern: reads API key from `ANTHROPIC_API_KEY` env var or constructor parameter, uses `claude-sonnet-4-5-20250929` by default, reuses shared prompt templates from `prompts/` directory. Handles Anthropic's content-block response format (extracts first text block). Auth errors, rate limits, and connection failures produce descriptive `AnthropicProviderError` messages. Registered as `"anthropic"` provider. Added `anthropic>=0.39.0` as optional dependency. 16 new tests covering init, registry, context enrichment, recommendations, error handling, and response parsing.

---

### PB-025: Add input validation layer

**Status:** Done

Created `engine/projectbridge/input/validation.py` with centralized validators: `validate_github_username()` (regex matching GitHub's rules — 1-39 chars, alphanumeric/hyphens, no leading/trailing hyphens), `validate_job_text()` (minimum 20 chars), and `validate_resume_text()` (optional, minimum 20 chars if provided). Each raises `ValidationError` with `field` and `constraint` attributes. Wired into orchestrator as the first step before any processing or API calls. 24 new tests covering all validators, edge cases, and error attributes.

---

### PB-023: Add structured logging and error handling

**Status:** Done

Added `logging.getLogger(__name__)` to orchestrator with INFO-level messages at each pipeline stage (AI provider resolution, GitHub analysis, job parsing, AI enrichment, core analysis, recommendations). Added `--verbose` / `-v` CLI flag that sets the `projectbridge.*` logger hierarchy to DEBUG level (default: WARNING). Logs go to stderr to avoid interfering with JSON output on stdout. Unhandled exceptions at the CLI boundary produce a user-friendly message and non-zero exit code, with full traceback available at DEBUG level. 2 new integration tests for verbose flags.

---

### PB-024: Implement GitHub token management

**Status:** Done

Centralized token resolution in the orchestrator with priority: explicit parameter > `GITHUB_TOKEN` env var > `github.token` in config file. Added `GitHubSettings` section to config model with optional `token` field. When no token is found, logs a WARNING about unauthenticated access (60 req/hour limit) and proceeds. Removed env var fallback from `GitHubClient` — the orchestrator now owns token resolution. Tokens never appear in log output, analysis results, or exports. 5 new tests covering token presence, absence, and header behavior.

---

### PB-021: Enhance framework detection heuristics

**Status:** Done

Expanded the GitHub analyzer's detection from 24 to 97 unique detectable frameworks, tools, and infrastructure signals. Added 7 data-driven detection registries: file indicators (38 entries), npm packages (32), Python packages (18), Rust crates (11), Ruby gems (4), Go modules (5), and PHP packages (3). New manifest parsers for Cargo.toml, Gemfile, go.mod, and composer.json. All detection logic is organized as registry dicts — adding a new detection requires only a data entry. 2 new tests verifying the registry approach and minimum detection count.

---

### PB-022: Implement recommendation templates

**Status:** Done

Created `engine/projectbridge/recommend/templates.yaml` with 20 pre-written project recommendations covering frontend (React, Vue, Svelte, React Native), backend (Django, FastAPI, Flask, Rails, Go/Gin), infrastructure (Docker, K8s, Terraform, CI/CD, AWS), data (pandas, scikit-learn), and full-stack (Next.js+Postgres, Tauri+Svelte) gaps. Added `templates.py` loader with `select_templates()` that ranks by skill overlap. Updated NoAI provider to use templates first, falling back to generic heuristic for uncovered skills. Adding a template requires only a YAML entry. 9 new tests.

---

### PB-017: Scaffold Tauri desktop application

**Status:** Done

Scaffolded Tauri 2.0 desktop app under `app/` with Svelte 5 + SvelteKit + TypeScript + Tailwind CSS v4 (per DEC-012). Frontend renders a basic ProjectBridge view with Strengths, Skill Gaps, and Recommendations sections using Tailwind utility classes. Rust backend (`src-tauri/`) exposes a `run_analysis` Tauri command that invokes the `projectbridge` CLI as a subprocess and returns JSON. Shell plugin (`tauri-plugin-shell`) added for IPC. Frontend calls `invoke("run_analysis", {args: ["analyze", "--example", "--no-ai"]})` and parses the JSON response. `npm run build` produces static site, `cargo check` compiles the Rust backend. Window configured at 1024x768 with 800x600 minimum.

---

### PB-018: Tauri UI — analysis dashboard view

**Status:** Done

Polished dashboard with summary stat cards (strengths/gaps/recommendations counts), skill grouping by category (Languages, Frameworks, Infrastructure, Tools, Concepts), color-coded scope badges on recommendations (green/amber/red for small/medium/large), dismissable error banner, and card-based layout for strengths and gaps sections.

---

### PB-019: Tauri UI — analysis input form

**Status:** Done

Built input form with GitHub username, job description (required), resume text (optional), and no-AI toggle. Client-side validation shows inline errors for empty required fields. Form submits via `run_analysis_form` Tauri IPC command. Added `--job-text` and `--resume-text` inline CLI flags (mutually exclusive with `--job`/`--resume`) per DEC-013. View state machine (form → loading → results → export) drives the single-page app. "Run Example Instead" button preserved. 2 new integration tests.

---

### PB-026: Add Markdown export format

**Status:** Done

Added `render_markdown()` to export module producing a formatted Markdown document with Strengths, Skill Gaps, Recommendations sections. CLI `--format markdown` flag added to `export` command. Enum values render as lowercase strings via `.value`. Footer includes version and timestamp. 6 new export tests + 1 CLI integration test.

---

### PB-027: Add Ollama local AI provider

**Status:** Done

Created `engine/projectbridge/ai/ollama_provider.py` using stdlib `urllib.request` (zero extra deps, per DEC-015). Calls Ollama REST API at `localhost:11434/api/chat` with `stream: false` and `format: json`. Server reachability check on init. Model configurable via `ai.ollama_model` config key. Orchestrator passes model kwarg for ollama provider. 13 tests with mocked HTTP.

---

### PB-028: Add repository caching layer

**Status:** Done

Created `engine/projectbridge/input/cache.py` — file-based JSON cache under `~/.cache/projectbridge/`, SHA-256 hashed keys, configurable TTL (per DEC-016). Integrated into `GitHubClient._request` with `cache_enabled` and `cache_ttl` params. Added `--no-cache` CLI flag. Orchestrator reads `config.cache.enabled` and `config.cache.ttl_seconds`. 5 cache tests.

---

### PB-029: Add progress indicators to CLI

**Status:** Done

Created `engine/projectbridge/progress.py` with `Progress` class — step announcements and braille spinners to stderr. Auto-detects TTY (silent when piped). Integrated into orchestrator at each pipeline stage: provider resolution, GitHub fetch (with spinner), resume processing, job parsing, AI analysis (with spinner), skill analysis, recommendations. CLI creates `Progress()` automatically.

---

### PB-030: Add documentation site scaffold

**Status:** Done

Scaffolded MkDocs Material site (per DEC-014). `mkdocs.yml` at repo root, source files in `site_src/` using `include-markdown` plugin to reference existing docs. Nav includes Home, Technical Spec, Contributing, Decisions, Backlog, Security. `mkdocs build` generates to `site/` (gitignored). `mkdocs serve` for local preview.

---

### PB-031: Tauri UI — export and share screen

**Status:** Done

Built export view with Markdown/JSON format toggle, live preview via `export_analysis` Tauri IPC command, "Save to File" button using native file dialog (`tauri-plugin-dialog`), and "Copy to Clipboard" button (`tauri-plugin-clipboard-manager`). Added `tauri-plugin-fs` for file writing. Export accessible from dashboard header and bottom actions. Full flow: input → results → export.

---

### PB-032: Add developer contribution tooling

**Status:** Done

Added Ruff (linter + formatter) with `pyproject.toml` config (Python 3.10, line-length 99, E/F/W/I/UP rules). Created `Makefile` with `install`, `test`, `lint`, `format`, `check`, `docs` targets. Added `.pre-commit-config.yaml` with `astral-sh/ruff-pre-commit` hooks. Created `.editorconfig` for cross-editor consistency. Updated CI workflow to run a `lint` job before the test matrix. Rewrote `CONTRIBUTING.md` with dev setup, make commands, and concrete AI provider contribution steps. Added GitHub PR template and issue templates (bug report, new AI provider). Fixed all existing lint/format issues across the codebase.

---

### Dead code cleanup

**Status:** Done

Removed `confidence_threshold` from `AnalysisSettings` (defined but never consumed by any downstream logic). Removed dead AI enrichment fields (`ai_summary`, `ai_seniority_signals`, `ai_tech_depth`) from the `analyze_context.txt` prompt and all three provider fallback paths — these were merged into the context dict but nothing downstream read them. Updated tests across config, OpenAI, Anthropic, and Ollama provider test files. 158 tests passing, lint clean.

---

### PyPI prep and README refresh

**Status:** Done

Polished `engine/pyproject.toml` for PyPI readiness: added `license = "MIT"` (SPDX), `authors`, `keywords`, `classifiers`, `[project.urls]` with Homepage/Documentation/Repository/Issues, and updated `description`. Refreshed `README.md` for a public audience: added CI/Python/License badges, screenshot placeholder, `pip install projectbridge` quickstart, collapsible sample JSON output, expanded features list (4 providers, 97+ detections, 22 templates), AI providers table, Desktop App section. Verified: 158 tests passing, lint clean, `python -m build` produces valid sdist + wheel.

---

### Add skill_context to recommendations (schema v1.1)

**Status:** Done

Added optional `skill_context` field to `Recommendation` model — mentor-style career context explaining *why* skills matter, not just listing them. Bumped schema to v1.1 (backwards compatible with 1.0). Added `skill_context` to all 31 templates (was 21, added 10 new: Kafka, Playwright/Jest, Elasticsearch, WebSockets, Spring Boot, Astro/CMS, RabbitMQ, Flutter, Angular, monitoring). Updated NoAI provider with `_CATEGORY_CONTEXT` dict for heuristic fallback by skill category. Updated recommendation engine passthrough, AI prompt, and Markdown export (blockquote rendering). Created `docs/schema/analysis_output_v1.1.json`. Updated Svelte UI with blue callout rendering and mock data. 170 tests passing, lint clean.

---
