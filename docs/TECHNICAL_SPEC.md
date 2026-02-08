# ProjectBridge Technical Specification

## 1. Purpose of This Document

This document describes the internal architecture, system boundaries, and implementation decisions behind ProjectBridge.

It is intended for:

- contributors extending the system
- engineers evaluating architectural decisions
- maintainers evolving the platform

For usage instructions and project overview, see the root [README.md](../README.md).

---

## 2. System Goals

ProjectBridge is designed as a local analysis engine that converts developer context into project recommendations.

The system must:

- Operate entirely locally.
- Produce deterministic structured outputs.
- Allow AI components to be replaced without modifying core logic.
- Remain usable via CLI without UI dependencies.
- Remain understandable by contributors unfamiliar with the original implementation.

The system intentionally prioritizes:

- **composability** over abstraction
- **transparency** over automation
- **extensibility** over completeness

---

## 3. System Boundaries

ProjectBridge operates within the following scope:

### Inputs

- GitHub repository metadata and structure (primary signal)
- Job description text (required)
- Optional resume text (secondary context only)

### Outputs

- structured analysis JSON
- project recommendations
- optional export artifacts

### The system does not:

- evaluate developer quality
- generate scores or rankings
- modify repositories
- interact with hiring systems

---

## 4. High-Level Architecture

```
[Tauri Application]
        ↓
[Engine Interface]
        ↓
[Input Processors]
        ↓
[Analysis Layer]
        ↓
[AI Provider Interface]
        ↓
[Recommendation Engine]
        ↓
[Structured Output]
```

The UI is a consumer of engine output and contains no business logic.

---

## 5. Core Components

### 5.1 Engine (Python)

The engine is the authoritative source of system behavior.

Responsibilities:

- collecting input context
- running analysis modules
- orchestrating AI providers
- generating recommendations
- producing structured output

The engine must remain runnable independently:

```bash
projectbridge analyze
```

This allows scripting, testing, and alternative frontends.

### 5.2 Input Processors

Input processors normalize external data into a unified context model.

#### GitHub Analyzer (Primary)

Extracts signals such as:

- language usage
- framework indicators
- project structure
- infrastructure signals

The analyzer operates on metadata and repository structure rather than deep static analysis to maintain performance and privacy.

#### Job Description Parser (Required)

Extracts:

- required technologies
- implied experience domains
- architectural expectations

#### Resume Context (Optional)

Resume input is treated as contextual enrichment only.

Resume data may influence interpretation but must not override GitHub-derived signals.

### 5.3 Analysis Layer

Analysis modules produce intermediate signals:

```
detected_skills
adjacent_skills
missing_skills
```

These modules should remain deterministic where possible.

AI usage is restricted to interpretation and recommendation stages.

### 5.4 AI Provider Interface

AI functionality is abstracted behind a provider interface.

**Responsibilities:**

- contextual interpretation
- recommendation generation

**Non-responsibilities:**

- repository parsing
- core analysis logic

Providers must implement:

```python
class AIProvider:
    def analyze_context(self, context: dict) -> dict:
        pass

    def generate_recommendations(self, gaps: dict) -> list:
        pass
```

The system must operate with:

```bash
--no-ai
```

where heuristic recommendations are used instead.

### 5.5 Recommendation Engine

The recommendation engine converts detected gaps into:

- small, realistic project suggestions
- demonstrable portfolio outcomes

Constraints:

- recommendations must be completable
- avoid multi-month project scope
- prioritize demonstrability over novelty

---

## 6. Data Model

All outputs conform to a versioned schema:

```json
{
  "schema_version": "1.0",
  "strengths": [],
  "gaps": [],
  "recommendations": []
}
```

Schema versioning allows forward compatibility between engine and UI.

---

## 7. Configuration Model

Behavior is configured via:

```
projectbridge.config.yaml
```

Configuration governs:

- AI provider selection
- analysis thresholds
- recommendation limits

Configuration replaces hardcoded behavior to support experimentation.

---

## 8. CLI Contract

The CLI is the primary interface.

The UI must call the CLI or engine interface rather than duplicating logic.

Example:

```bash
projectbridge analyze \
  --job job.txt \
  --github-user username \
  --output result.json
```

CLI behavior should remain stable across versions.

---

## 9. Design Decisions

**Local-First Execution**
Chosen to preserve privacy and simplify trust boundaries.

**Python Engine**
Chosen for accessibility and AI ecosystem maturity.

**Tauri UI**
Chosen for lightweight desktop distribution and local execution model.

**AI Isolation**
AI is isolated to prevent lock-in and enable experimentation.

---

## 10. Non-Goals

The following are intentionally excluded:

- resume scoring
- hiring prediction
- automated resume rewriting
- hosted infrastructure

These introduce scope and change system intent.

---

## 11. Future Evolution (Non-Binding)

Possible directions:

- additional input sources
- alternative recommendation strategies
- domain-specific analyzers

Any additions should preserve local-first execution and modularity.
