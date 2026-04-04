---
name: harness-engineering-context
description: Lifecycle management of agent-readable context systems for software repositories. Use when users ask to restructure AGENTS.md, migrate knowledge into docs/, manage versioned plans (active/completed/tech-debt), enforce cross-link integrity, or add automated validation so agents run more reliably and efficiently across design, implementation, review, and maintenance.
---

# Harness Engineering Context

## Overview

Build and maintain a stable context system centered on the code repository: concise map at root, detailed knowledge in `docs/`, versioned execution plans, and enforceable validation.

## Core Contract

1. Keep `AGENTS.md` as a compact map (target around 100 lines, avoid deep detail).
2. Keep detailed knowledge under `docs/` as the system of record.
3. Treat plans as first-class artifacts with clear lifecycle states.
4. Enforce structure and cross-link validity with executable checks.
5. Update docs in the same change set as architecture or workflow changes.

## Standard Layout

Use this baseline unless the repository already has a stronger convention:

```text
docs/
├── DESIGN.md
├── FRONTEND.md                  # if frontend exists or will exist
├── PLANS.md
├── PRODUCT_SENSE.md
├── ROADMAP.md
├── design-docs/
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt/
├── generated/
├── product-specs/
└── references/
```

Keep legacy top-level documents as short redirect stubs pointing into `docs/`.

## Lifecycle Workflow

### 1. Assess Current State

Run a fast audit before editing:

- Identify context entrypoints (`AGENTS.md`, roadmap/stage docs, `docs/`).
- Find duplicate or contradictory sources of truth.
- Find broken links and stale references.
- Confirm whether validation exists and is executed by tests/CI.

### 2. Restructure Information Architecture

Apply progressive disclosure:

- `AGENTS.md`: map only (navigation, core constraints, high-level commands).
- `docs/*.md`: canonical details.
- `docs/design-docs/`: deep architecture and subsystem design.
- `docs/exec-plans/*`: execution lifecycle artifacts.
- `docs/generated/`: generated technical artifacts and README index.

### 3. Manage Plans as First-Class Artifacts

Maintain `docs/PLANS.md` plus concrete files under `docs/exec-plans/`:

- `active/`: currently executing plans.
- `completed/`: accepted plans with completion date.
- `tech-debt/`: unresolved debt with impact and target stage.

When a plan finishes, move it from `active/` to `completed/` and sync status in `PLANS.md`.

### 4. Enforce Validation Guardrails

Add an executable validator (for example `scripts/validate_docs.py`) and ensure it checks:

- required files/directories exist;
- migration redirect docs are present and point to `docs/`;
- markdown internal links resolve;
- `AGENTS.md` stays concise;
- plan buckets exist and are populated as expected.

Add a unit test (for example `tests/test_docs_validation.py`) that runs the validator and fails on violations.

### 5. Keep Docs and Code in Lockstep

For any architecture or flow change:

- update implementation;
- update relevant `docs/` files in the same PR/commit;
- run docs validator and unit tests;
- include validation command output in review notes.

## Review Checklist

Use this checklist for review or pre-merge:

- Is `AGENTS.md` only a map and not a dump of detailed specs?
- Is each major domain documented in `docs/` once (single source of truth)?
- Are plan states (`active/completed/tech-debt`) current and non-contradictory?
- Do redirect stubs clearly route to canonical docs?
- Do automated validators catch broken links and structure regressions?
- Are validation checks wired into unit tests and CI flow?

## Editing Rules

1. Prefer minimal, incremental docs refactors over big-bang rewrites.
2. Preserve backward compatibility by keeping temporary redirect docs.
3. Remove stale claims immediately when code behavior changes.
4. Avoid putting volatile implementation detail in `AGENTS.md`.
5. Do not add extra governance docs outside `docs/` unless necessary.

## References

- For concrete folder schema and migration decisions, read `references/context-system-spec.md`.
- For validator scope and enforcement patterns, read `references/validation-rules.md`.
