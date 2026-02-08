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
