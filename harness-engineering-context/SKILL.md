---
name: harness-engineering-context
description: Use when restructuring repository context systems, defining roles for AGENTS.md/README.md/ARCHITECTURE.md, migrating canonical knowledge into docs/, managing versioned execution plans, or adding automated validation for documentation structure, cross-links, and context hygiene.
---

# Harness Engineering Context

## Overview

Build and maintain a stable repository-native context system: compact entrypoints at the root, canonical detail in `docs/`, versioned execution plans, and enforceable validation.

## Core Contract

1. Keep `AGENTS.md` as a compact map (target around 100 lines, avoid deep detail).
2. Treat root documents as entrypoints with distinct jobs:
   - `README.md`: human onboarding and repository entrypoint.
   - `AGENTS.md`: agent working map and operational constraints.
   - `ARCHITECTURE.md`: top-level architecture map linking into deeper design docs.
3. Keep detailed knowledge under `docs/` as the system of record.
4. Treat plans as first-class artifacts with clear lifecycle states.
5. Enforce structure, cross-link validity, and source-of-truth boundaries with executable checks.
6. Update implementation and its affected docs in the same change set.

## Standard Layout

Use this baseline unless the repository already has a stronger convention:

```text
README.md
AGENTS.md
ARCHITECTURE.md
docs/
├── README.md                    # docs navigation index
├── DESIGN.md
├── FRONTEND.md                  # if frontend exists or will exist
├── SECURITY.md                  # if auth, secrets, data handling, or external surfaces exist
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

Keep root files concise. Put depth in `docs/`. If a repository already uses top-level docs beyond the three root entrypoints, either:

- keep them as short maps that link to canonical files in `docs/`; or
- replace them with redirect stubs during migration.

## Lifecycle Workflow

### 1. Assess Current State

Run a fast audit before editing:

- Identify root entrypoints (`README.md`, `AGENTS.md`, `ARCHITECTURE.md`) and `docs/`.
- Find duplicate or contradictory sources of truth.
- Find broken links and stale references.
- Find undocumented root docs or orphaned docs pages with no inbound links.
- Confirm whether validation exists and is executed by tests/CI.

### 2. Restructure Information Architecture

Apply progressive disclosure:

- `README.md`: setup, main workflows, and navigation for humans.
- `AGENTS.md`: map only (navigation, core constraints, high-level commands for agents).
- `ARCHITECTURE.md`: top-level domain/package map and links to deeper design docs.
- `docs/*.md`: canonical rules, constraints, and subsystem details.
- `docs/design-docs/`: deep architecture and subsystem design.
- `docs/exec-plans/*`: execution lifecycle artifacts.
- `docs/generated/`: generated technical artifacts and README index.
- `docs/product-specs/`: user flows, product requirements, and acceptance framing.
- `docs/references/`: external references, tool conventions, and source material.

Prefer explicit core rule docs when the repository needs them, for example:

- `docs/DESIGN.md`
- `docs/FRONTEND.md`
- `docs/SECURITY.md`
- `docs/BACKEND.md`
- `docs/DATA.md`

Do not force every repository to have every file. Require only what the system actually needs, then validate that the chosen set is documented and linked.

### 3. Manage Plans as First-Class Artifacts

Maintain `docs/PLANS.md` plus concrete files under `docs/exec-plans/`:

- `active/`: currently executing plans.
- `completed/`: accepted plans with completion date.
- `tech-debt/`: unresolved debt with impact and target stage.

When a plan finishes, move it from `active/` to `completed/` and sync status in `PLANS.md`.

### 4. Enforce Validation Guardrails

Add an executable validator (for example `scripts/validate_docs.py`) and ensure it checks:

- required files/directories exist;
- required root entrypoints exist and stay concise;
- migration redirect docs are present when expected and point to canonical files;
- markdown internal links resolve;
- `AGENTS.md` links to core docs entrypoints;
- `ARCHITECTURE.md` links to relevant architecture/design docs;
- `docs/README.md` or equivalent docs index links to major sections;
- core rule docs declared by the repository are present and reachable;
- duplicate source-of-truth patterns are flagged;
- plan buckets exist and are populated as expected.

Add a unit test (for example `tests/test_docs_validation.py`) that runs the validator and fails on violations.

### 5. Keep Docs and Code in Lockstep

For any architecture, workflow, or entrypoint change:

- update implementation;
- update canonical `docs/` files in the same PR/commit;
- update `README.md` when setup, entrypoints, or contributor workflows change;
- update `AGENTS.md` when agent instructions, navigation, or operating constraints change;
- update `ARCHITECTURE.md` when domain boundaries, package structure, or system topology change;
- run docs validator and unit tests;
- include validation command output in review notes.

## Review Checklist

Use this checklist for review or pre-merge:

- Do `README.md`, `AGENTS.md`, and `ARCHITECTURE.md` each have a clear non-overlapping role?
- Is `AGENTS.md` only a map and not a dump of detailed specs?
- Is `ARCHITECTURE.md` a top-level map rather than a second full copy of `docs/DESIGN.md`?
- Is each major domain documented in `docs/` once (single source of truth)?
- Are core rule docs present for the domains the repository actually has?
- Are plan states (`active/completed/tech-debt`) current and non-contradictory?
- Do redirect stubs clearly route to canonical docs?
- Do automated validators catch broken links, structure regressions, and misplaced source-of-truth drift?
- Are validation checks wired into unit tests and CI flow?

## Editing Rules

1. Prefer minimal, incremental docs refactors over big-bang rewrites.
2. Preserve backward compatibility by keeping temporary redirect docs.
3. Remove stale claims immediately when code behavior changes.
4. Avoid putting volatile implementation detail in `AGENTS.md`.
5. Keep `README.md`, `AGENTS.md`, and `ARCHITECTURE.md` short and link outward instead of duplicating deep detail.
6. Do not add extra governance docs outside `docs/` unless they serve as root entrypoints.

## References

- For concrete folder schema and migration decisions, read `references/context-system-spec.md`.
- For validator scope and enforcement patterns, read `references/validation-rules.md`.
