# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] - 2026-02-13

### Added
- Experience level inference (junior/mid/senior) from GitHub signals and resume
- Portfolio-level gap insights (domain balance, infrastructure gaps, depth vs breadth)
- Interview topic mapping for 40 skills with common question areas
- Personalized recommendations that reference the developer's actual repos
- Ollama local AI provider (zero external dependencies, full privacy)
- `pb-scan` Rust CLI for local repository scanning (`--local-repos` flag)
- `export-project` command generating rich Markdown project specs with tier-based features
- `skill_context` field on recommendations with career mentorship context
- Non-technical job description rejection with clear error message
- Tauri UI: recommendation cards with beginner/intermediate/advanced tier tabs
- Tauri UI: portfolio insights section
- Tauri IPC: `scan_local_repos` command for local directory scanning
- Documentation links and skill features data files (`resources.yaml`, `skill_features.yaml`)
- AI setup guide (`docs/AI_SETUP.md`) with Ollama walkthrough

### Changed
- Schema bumped to v1.2 (backwards compatible with v1.0, v1.1)
- Recommendation templates expanded from 20 to 31 with difficulty tiers
- Skill taxonomy expanded to 71 skills
- Framework detection expanded from 24 to 97+ unique signals
- Tauri UI redesigned with tab-append UX and colored tier pills
- Version bumped to 0.2.0

### Removed
- Dead code: `confidence_threshold` config, unused AI enrichment fields

## [0.1.1] - 2026-02-12

### Fixed
- Include README in PyPI package metadata
- Exclude test files from wheel distribution
- Include YAML data files in package build

## [0.1.0] - 2026-02-12

### Added
- Core analysis engine: skill matching, gap detection, adjacent skill discovery
- GitHub repository analyzer with 97+ framework/tool detections
- Job description parser (bullet-list, prose, and mixed formats)
- Resume context processor (optional secondary signal)
- Output schema v1.0 with strengths, gaps, and recommendations
- 71-skill taxonomy with adjacency relationships
- 20 curated recommendation templates (frontend, backend, infrastructure, data, full-stack)
- AI provider interface with pluggable architecture
- NoAI heuristic fallback (works without any API keys)
- OpenAI provider (`gpt-4o`, editable prompt templates)
- Anthropic Claude provider (shared prompt templates)
- CLI entry point: `projectbridge analyze` and `projectbridge export`
- `--example` mode with bundled sample data (no setup required)
- `--no-ai` flag for heuristic-only mode
- JSON and Markdown export formats
- File-based caching for GitHub API responses
- Progress indicators (braille spinner, step announcements)
- Structured logging with `--verbose` flag
- Input validation (GitHub username, job text, resume text)
- Tauri 2.0 desktop app with Svelte 5 + TypeScript + Tailwind CSS v4
- Tauri UI: analysis input form, results dashboard, export/share screen
- GitHub Actions CI (pytest matrix: Python 3.10, 3.12)
- Ruff linting/formatting, pre-commit hooks, Makefile
- MkDocs documentation site scaffold
- CONTRIBUTING.md, SECURITY.md, issue templates
- MIT license
