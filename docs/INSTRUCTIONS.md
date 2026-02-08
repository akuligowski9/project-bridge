# Project Orientation & AI Collaboration Contract

**Version:** 1.0
**Last Updated:** 2026-02-08

---

## Session Start Instruction (Read First)

At the beginning of **ANY** work session on this repository:

1. Read THIS FILE (`docs/INSTRUCTIONS.md`) in full.
2. Then read `docs/DECISIONS.md` to understand what has been decided and why.
3. Then read `docs/BACKLOG.md` to understand what work is planned and its current state.
4. Do NOT assume missing context.
5. Do NOT invent intent, structure, or rationale.
6. If there is any discrepancy, gap, or ambiguity between documentation, code, or conversation, **ASK QUESTIONS** before proceeding.

You may respond with:

- "I see a gap between documentation and implementation — do you want to update docs or preserve current behavior?"
- "This repository appears to be partially migrated — should I normalize it now while preserving existing material?"
- "There is no recorded decision explaining this — should we log it before continuing?"

> **Hallucination is strictly disallowed.**
> **Assumptions are strictly disallowed.**
> **Preservation of existing material is required unless explicitly overridden.**

---

## Purpose of This Document

This file defines the authoritative documentation structure, workflow rules, and collaboration expectations for ProjectBridge.

**Goals:**

- Consistency across sessions
- Safe handling of partial or evolving documentation
- No silent assumptions or hallucinated intent

> If any rule in this document is violated, pause and ask how to proceed.

---

## Source of Truth Hierarchy

When conflicts arise, resolve them in this order:

1. **INSTRUCTIONS.md** — collaboration rules and structure
2. **DECISIONS.md** — recorded architectural, design, and scope decisions with reasoning
3. **BACKLOG.md** — committed work and priorities
4. **TECHNICAL_SPEC.md** — design and technical reasoning
5. **README.md** — public-facing summary

> If a lower-priority document contradicts a higher-priority one, pause and ask how to reconcile.

---

## Authoritative Document Structure

### Root

- `README.md` — Public-facing overview (rendered by GitHub)

### docs/

- `INSTRUCTIONS.md` — This file (authoritative rules)
- `DECISIONS.md` — Architectural, design, and scope decisions with rationale
- `BACKLOG.md` — Source of truth for committed work
- `TECHNICAL_SPEC.md` — Internal architecture, system boundaries, implementation decisions
- `CONTRIBUTING.md` — Development setup, contribution areas, PR guidelines
- `SECURITY.md` — Security policy and responsible disclosure

### Root (Claude-specific)

- `CLAUDE.md` — Claude model behavior preferences (tone, style, reminders)

`CLAUDE.md` customizes Claude's behavior but does NOT override this file. If there is a conflict, `INSTRUCTIONS.md` always wins.

### Rules

- Do NOT create additional documentation files unless explicitly instructed.
- If this repository already contains documentation, preserve existing content and migrate it into this structure intentionally.
- Never delete or overwrite material without confirmation.

---

## Project Identifier Prefix

This project uses `PB` as the prefix for backlog items and GitHub Issues (see DEC-005).

### Format

```
PB-###
```

### Examples

- `PB-001`
- `PB-014`
- `PB-032`

### Rules

- The prefix must not change without explicit instruction.
- If changed, all references must be migrated together.
- Prefix changes must be logged in `DECISIONS.md`.

---

## Canonical Status Flow (Used Everywhere)

```
Planned → In Progress → Done
              ↓
           Blocked
              ↓
           Archived
```

### Definitions

| Status          | Meaning                                               |
| --------------- | ----------------------------------------------------- |
| **Planned**     | Acknowledged, not started                             |
| **In Progress** | Actively being worked on                              |
| **Blocked**     | Cannot proceed without input, decision, or dependency |
| **Done**        | Complete                                              |
| **Archived**    | Was planned, no longer pursuing (kept for history)    |

Use **Archived** for tasks that were planned but later abandoned, superseded, or deemed not worth doing. This preserves decision history without cluttering active work. Different from **Documented Gaps**, which are known limitations accepted by design from the start.

This flow must be used consistently in:

- `BACKLOG.md`
- GitHub Issues
- AI summaries and reasoning

---

## Priority System (Used Everywhere)

| Priority     | Level   |
| ------------ | ------- |
| **Critical** | Highest |
| **High**     |         |
| **Medium**   |         |
| **Low**      | Lowest  |

### Rules

- Priority defines urgency and ordering.
- Within each section, items are ordered top-to-bottom by importance.

---

## Backlog Semantics (Source of Truth)

`BACKLOG.md` is the single source of truth for committed work.

### Rules

- Items in Critical / High / Medium / Low are committed to implementation.
- Timing may be undefined, but intent exists.
- Items in the **Parking Lot** are not yet tasks.

### Parking Lot

- Captures ideas worth remembering
- Not yet actionable or fully defined
- May be promoted later or discarded

---

## BACKLOG.md Required Structure

Must include:

1. Status Flow legend at the top
2. Sections in this exact order:
   - Critical
   - High
   - Medium
   - Low
   - Parking Lot
   - Documented Gaps (for known limitations accepted by design)
   - Done

### Item Format (Backlog)

```markdown
### PB-###: <Short title>

**Description:**
<Minimum 3 sentences: problem context, proposed solution, implementation notes.>

**Acceptance Criteria:**

1. <Specific, independently testable criterion>
2. <Specific, independently testable criterion>

**Metadata:**

- **Status:** Planned | In Progress | Blocked | Done | Archived
- **Priority:** Critical | High | Medium | Low
- **Depends on:** <PB-### list or —>
- **Blocks:** <PB-### list or —>
```

### Item Format (GitHub Issues)

When promoted to GitHub Issues, adapt the format:

```markdown
## PB-###: <Short title>

### Description

<Same description from backlog.>

### Acceptance Criteria

- [ ] <Specific, independently testable criterion>
- [ ] <Specific, independently testable criterion>

### Metadata

- **Status:** Planned | In Progress | Blocked | Done | Archived
- **Priority:** Critical | High | Medium | Low
- **Depends on:** <PB-### list or —>
- **Blocks:** <PB-### list or —>
```

### Acceptance Criteria Rules

- Each item has **up to 5** acceptance criteria — not exactly 5.
- Each criterion must be independently testable.
- Do not pad criteria to reach a count. If 3 criteria fully cover the item, use 3.

### Rules

- "GitHub Issue" is a synchronization indicator, not a status.
- If a GitHub Issue exists, backlog and issue state must remain aligned.
- Do NOT promote tasks to GitHub Issues unless explicitly instructed.

---

## DECISIONS.md Responsibilities

`DECISIONS.md` replaces a chronological progress log with a structured decision record. It captures *why* choices were made so future contributors (and future sessions) can understand reasoning without guessing.

### Purpose

- Record architectural, design, and scope decisions
- Preserve alternatives considered and reasoning
- Reduce re-orientation overhead across sessions

### Entry Format

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

### When to Add a Decision

Log a new decision when:

- An architectural or design choice is made
- A scope change affects backlog priorities
- A technology, pattern, or approach is chosen over alternatives
- A significant tradeoff is accepted

### Rules

- Decisions are numbered sequentially (`DEC-001`, `DEC-002`, etc.).
- Once accepted, a decision should not be silently changed — mark it `Superseded` and create a new entry.
- Decisions should be concise but complete enough to stand alone.

---

## TECHNICAL_SPEC.md Responsibilities

This is the deep reasoning document describing internal architecture, system boundaries, and implementation decisions.

### Required Sections

1. **Purpose**
2. **System Goals**
3. **System Boundaries** (inputs, outputs, non-goals)
4. **High-Level Architecture**
5. **Core Components** (with subsections per component)
6. **Data Model**
7. **Configuration Model**
8. **CLI Contract**
9. **Design Decisions** (summary — detail lives in DECISIONS.md)
10. **Non-Goals**

### Rules

- TECHNICAL_SPEC.md describes *what the system is and how it works*.
- DECISIONS.md describes *why specific choices were made*.
- Keep them complementary, not duplicative.

---

## README.md Responsibilities

`README.md` is the public entry point.

It must include:

- What the project is
- Quickstart (run locally)
- What it does (features)
- Privacy / local-first principles
- AI transparency
- Architecture (high level)
- Output format
- What this is / what this isn't
- Contributing section
- Links to relevant docs

> If README content becomes inaccurate, it must be updated during the next documentation sync.

---

## CLAUDE.md Responsibilities

`CLAUDE.md` lives in the repository root and customizes Claude model behavior only.

### Rules

- `CLAUDE.md` must NOT contain project-specific technical details (those belong in TECHNICAL_SPEC.md).
- `CLAUDE.md` must NOT duplicate rules from INSTRUCTIONS.md.
- `CLAUDE.md` is for AI model behavior preferences only.
- If INSTRUCTIONS.md and CLAUDE.md conflict, INSTRUCTIONS.md always wins.

---

## Questions Before Action (Anti-Overreach Rule)

Before taking action, ask clarifying questions if:

- Requirements are ambiguous
- Multiple valid interpretations exist
- Documentation is silent
- A decision affects architecture, scope, or public API

> Default behavior is to **ask, not assume**.

---

## Task Scoping Rule

When breaking down work:

- Maximum 3 file modifications per step before pausing to summarize
- One backlog item at a time unless explicitly told to batch
- After completing each step, state what changed and ask to proceed
- If a task needs more than 5 steps, present the plan and ask for confirmation before starting

This prevents drift and ensures the user stays informed of progress.

---

## Destructive Action Protocol

Before ANY of the following operations, Claude must:

1. State the exact command/action
2. List affected files/data
3. Explain the risk
4. Describe the undo path (or state if irreversible)
5. Wait for user to type "yes", "proceed", or "confirm"

**Operations requiring this protocol:**

- File deletion (rm, unlink)
- Git destructive operations (reset --hard, clean -f, push --force, branch -D)
- Overwriting existing files
- Any action that cannot be undone

> Do NOT proceed on silence or ambiguity. Explicit confirmation required.

---

## Major Scope Change Definition

A major scope change includes:

- Adding/removing a feature or view
- Changing a core user flow
- Introducing a new external dependency
- Changing data ownership or persistence
- Re-prioritizing Critical or High backlog items

**Major scope changes require:**

1. A new entry in `DECISIONS.md`
2. Updates to affected documentation

---

## Documentation Sync

Trigger a documentation sync prompt when ANY of these occur:

- 5 backlog items completed since last sync
- Before ending any session (non-negotiable)
- After a major scope change

When triggered, ask: "Do you want to run a documentation sync?"

If yes:

1. Update `BACKLOG.md`
2. Update `TECHNICAL_SPEC.md`
3. Update `README.md` if needed
4. Add entries to `DECISIONS.md` for any unrecorded decisions

> This is a consistency pass, not a rewrite.

---

## GitHub Issues (When Promoted)

Promote backlog items **only when explicitly instructed**.

Use the GitHub Issues item format defined above. Copy the item directly from backlog to GitHub Issue. After promotion, update the backlog item's metadata to reference the issue number and keep states aligned.

---

## Documentation Minimalism Principle

Documentation should:

- Explain intent, not restate code
- Be concise but sufficient
- Be updated for correctness, not completeness

> If a section adds no clarity, ask whether it should be removed.

---

## End of Work Block (Cool-Down)

Before ending a session:

1. Ask whether to perform a final documentation sync.
2. Review `BACKLOG.md` for items suitable for GitHub Issue promotion.
3. Ensure `DECISIONS.md` captures any unrecorded decisions from the session.
4. If deployable changes were made, ask whether to tag a release:
   - Use semantic versioning: `vMAJOR.MINOR.PATCH`
   - Create annotated tag: `git tag -a v1.2.0 -m "Brief description"`
   - Push tags with code: `git push origin main --tags`

> This cool-down ensures the project is safe to pause and easy to resume.

---

## Safe Word: "MUFFINS" (Pause & Recovery Mode)

If the user says **"muffins"** at any time, immediately do the following:

1. **Stop** advancing work.
2. **Read** `DECISIONS.md` and `BACKLOG.md`.
3. **Provide a concise summary:**
   - Where we left off
   - Current priorities
   - Open questions or blockers
4. **Ask whether to:**
   - Run a documentation sync
   - Promote items to GitHub Issues
   - Pause safely

> This is a **non-negotiable interrupt** and overrides all other instructions.
