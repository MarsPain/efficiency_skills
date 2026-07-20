---
name: harness-engineering-context
description: Use when restructuring repository context systems, defining roles for root entrypoints and canonical docs, integrating CONTEXT.md, ADRs, design docs, issue-tracker configuration, and specs, or adding automated validation for structure, cross-links, source-of-truth boundaries, and context hygiene.
---

# Harness Engineering Context

## Overview

Build and maintain one repository-native context system. Give every artifact type a clear job and one canonical home, keep entrypoints compact, create optional artifacts only when needed, and enforce the selected structure with executable checks.

## Core Contract

1. Keep root entrypoints compact and non-duplicative:
   - `README.md`: human onboarding and repository entrypoint.
   - `AGENTS.md` by default, or a deliberately selected alternative: cross-agent working map and operational constraints. Tool-specific entrypoints such as `CLAUDE.md` may coexist when they stay concise and link to shared configuration.
   - `ARCHITECTURE.md`: top-level architecture map linking into deeper design and decision records.
2. Give each artifact type exactly one canonical location. Use `docs/` by default, while preserving standard protocol-owned locations such as root or context-local `CONTEXT.md`, context-local ADRs, configured issue trackers, and `.scratch/` for a local Markdown tracker.
3. Treat domain language as distinct from architecture and implementation detail. Recognize `CONTEXT.md` or `CONTEXT-MAP.md` when present, but create them lazily rather than as empty governance shells.
4. Keep specs, issues, design docs, and ADRs distinct:
   - specs define a change's desired behavior, constraints, implementation decisions, testing decisions, and change-scoped delivery considerations;
   - issues own work units, dependencies, assignees, and task state;
   - design docs explain current or target-system structure, interfaces, data flow, constraints, failure modes, and alternatives;
   - ADRs preserve one accepted, durable decision, its rationale, and non-obvious consequences.
5. Keep the configured issue tracker as the only source of truth for work state, dependencies, assignment, and technical debt.
6. Enforce structure, cross-link validity, and source-of-truth boundaries with executable checks.
7. Update implementation and its affected docs in the same change set.

## Standard Layout

Use this unified baseline unless the repository has a documented stronger convention. Entries marked optional are created only when the corresponding information or workflow exists.

```text
README.md
AGENTS.md                         # default cross-agent map; a declared alternative is allowed
ARCHITECTURE.md
CONTEXT.md                        # optional: single-context domain glossary
CONTEXT-MAP.md                    # optional alternative: multi-context map
.scratch/                         # optional: local Markdown issue tracker only
docs/
├── README.md                     # docs navigation index
├── DESIGN.md                     # optional architecture overview and contracts
├── FRONTEND.md                   # optional
├── SECURITY.md                   # optional
├── BACKEND.md                    # optional
├── DATA.md                       # optional
├── PRODUCT_SENSE.md              # optional
├── ROADMAP.md                    # optional
├── agents/                       # optional agent/skill operational configuration
├── adr/                          # optional system-wide accepted decisions
├── design-docs/                  # optional deep designs and alternatives
├── generated/                    # optional generated technical artifacts
├── product-specs/                # optional product and API specifications
└── references/                   # optional external/supporting references
```

For multiple bounded contexts, a root `CONTEXT-MAP.md` points to each context's canonical `CONTEXT.md`. Context-specific ADRs may live beside that context under `docs/adr/`; system-wide ADRs remain in root `docs/adr/`.

Do not create every optional file or directory. Document the active subset, link it from an entrypoint or index, and validate only the capabilities the repository has adopted.

## Workflow

### 1. Assess Current State

Run a fast audit before editing:

- Identify human, agent, and architecture entrypoints, including `AGENTS.md` and `CLAUDE.md`.
- Inspect `CONTEXT.md`, `CONTEXT-MAP.md`, root and context-local `docs/adr/`, `docs/agents/`, `docs/design-docs/`, `docs/product-specs/`, and `.scratch/` when present.
- Read `docs/agents/domain.md` and `docs/agents/issue-tracker.md` when present; treat them as operational configuration, not duplicate narrative documentation.
- Identify which artifact capabilities are active and where each source of truth lives.
- Find duplicate or contradictory sources of truth, broken links, stale references, and orphaned canonical docs.
- Confirm whether validation exists and is executed by tests or CI.

### 2. Establish Entrypoints and Canonical Homes

Apply progressive disclosure:

- `README.md`: setup, main workflows, and navigation for humans.
- selected agent entrypoint: navigation, core constraints, high-level commands, and links to `docs/agents/` when configured.
- `ARCHITECTURE.md`: top-level domain/package map plus links to deep designs and relevant ADRs.
- `CONTEXT.md`: glossary only; no implementation detail, specifications, or task state.
- `CONTEXT-MAP.md`: map of multiple contexts and their relationships; link to each canonical glossary.
- `docs/README.md`: index the active documentation areas.
- `docs/agents/`: issue-tracker, triage-label, domain-doc, and other agent workflow configuration.
- `docs/adr/`: accepted system-wide architectural or domain decisions plus their supersession history.
- context-local `docs/adr/`: decisions scoped to that context.
- `docs/design-docs/`: current or target-system designs, alternatives under exploration, and subsystem analysis.
- `docs/product-specs/`: user flows, requirements, and acceptance framing.
- `docs/references/`: external references, tool conventions, and source material.

If both `AGENTS.md` and `CLAUDE.md` exist, allow tool-specific instructions in each, but keep shared operational configuration canonical under `docs/agents/` and link to it. Do not duplicate a full `## Agent skills` block or another shared rule set.

### 3. Model Work Without Duplication

Determine the configured issue tracker from `docs/agents/issue-tracker.md` when it exists. Issues may live on an external service or under `.scratch/`; that tracker owns task status, dependency edges, assignment, and discussion.

Use the spec as the change-scoped source of truth for desired behavior, accepted implementation and testing decisions, and any migration, rollout, rollback, or system-level verification that belongs only to that change.

Use design docs for deeper current or target-system structure and alternatives that outlive one change. Update them as the system evolves.

Create an ADR only when a decision meets all three conditions:

1. it is costly to reverse;
2. it would surprise a future reader without context;
3. it resolves a real trade-off among credible alternatives.

An ADR records one accepted decision. Preserve its history by superseding it with a new ADR rather than rewriting the old rationale. While a design is still being explored, keep alternatives in the design doc. Once a qualifying decision is accepted, make its ADR authoritative for decision status and rationale; keep only a concise summary and link in the design doc. Link the ADR back to the design doc when broader context is useful.

Do not force a pair: a design doc may need no ADR, and a focused ADR may need no design doc.

Link work artifacts rather than copying them:

- each implementation issue links to its parent spec; tracker-native parent/child relationships or generated views may provide backlinks without editing the spec;
- an issue also links to relevant design docs or ADRs when needed;
- design docs do not mirror live task state;
- ADRs record the decision and consequences, not the implementation checklist;
- migration or delivery checklists local to one slice remain in the relevant issue;
- technical-debt items are recorded in the configured issue tracker; a roadmap may summarize and link them but does not own their state.

Existing `docs/exec-plans/` content is legacy material, not part of the standard layout. Do not delete it during migration. Move active canonical content by responsibility into the relevant spec, issues, design docs, or ADRs; preserve completed records and inbound links as historical documentation.

### 4. Enforce Validation Guardrails

Add an executable validator, for example `scripts/validate_docs.py`. Automate structural, link, scope, and explicit-status checks; keep semantic judgments such as whether a decision deserves an ADR in the review checklist unless repository metadata makes them deterministic. The validator should first discover the active artifact capabilities and canonical locations, then check:

- required entrypoints exist and remain concise;
- each shared operational rule set has exactly one owner even when multiple tool-specific entrypoints exist;
- internal Markdown links resolve;
- `CONTEXT-MAP.md` links to every declared context glossary;
- a single-context glossary and multi-context map are not both authoritative;
- root and context-local ADR scopes are valid and reachable;
- design docs describe current or target-system design while ADRs preserve qualifying accepted decisions and supersession history;
- accepted ADR-worthy decisions are linked rather than fully duplicated in design docs;
- `docs/agents/` configuration is reachable from the entrypoint that owns the corresponding shared block and from the docs index;
- `.scratch/` is treated as an issue store only when the configured tracker is Local Markdown;
- specs, issues, design docs, and ADRs retain distinct ownership without duplicated canonical sections;
- the configured issue tracker uniquely owns work state, dependencies, assignment, and technical debt;
- legacy execution-plan material is preserved or migrated without becoming a second active source of truth.

Add a unit test, for example `tests/test_docs_validation.py`, that runs the validator and fails on violations.

Read `references/validation-rules.md` before designing or changing validation behavior.

### 5. Keep Docs and Code in Lockstep

For any architecture, workflow, domain-language, or entrypoint change:

- update implementation where applicable;
- update the canonical artifact in the same change set;
- update `README.md` when setup, entrypoints, or contributor workflows change;
- update the relevant agent entrypoint or shared configuration owner when agent instructions, navigation, or operating constraints change;
- update `ARCHITECTURE.md`, designs, and ADRs when boundaries, topology, or durable decisions change;
- update `CONTEXT.md` only when canonical domain language changes;
- run docs validation and relevant unit tests;
- include validation command output in review notes.

## Review Checklist

- Do the human, agent, and architecture entrypoints have clear non-overlapping roles?
- Does each shared operational rule set have one canonical owner, without preventing concise tool-specific entrypoints?
- Does every active artifact type have one canonical location?
- Is `CONTEXT.md` a glossary only, and is it absent when the repository has no domain language to record?
- Does `CONTEXT-MAP.md` reach every relevant context glossary without competing with a root glossary?
- Are system-wide and context-local ADRs clearly scoped?
- Does each ADR record one decision that is costly to reverse, surprising without context, and based on a real trade-off?
- Do design docs describe the current/target system and link accepted ADR-worthy decisions without copying their full rationale?
- Are changed decisions represented by superseding ADRs and corresponding design-doc updates?
- Are `docs/agents/` files configuration rather than duplicated narrative guidance?
- Does the configured issue tracker uniquely own task state and dependencies?
- Are specs, issues, design docs, and ADRs linked rather than copied?
- Does change-scoped migration or delivery detail live in the spec or relevant issue rather than a parallel planning system?
- Do validators catch broken links, orphaned canonical artifacts, invalid scopes, and source-of-truth drift?
- Are validation checks wired into unit tests and CI flow?

## Editing Rules

1. Prefer minimal, incremental refactors over big-bang rewrites.
2. Preserve backward compatibility with temporary redirect documents where consumers can follow them; do not replace a path that downstream tooling directly edits with a redirect stub.
3. Preserve established protocol-owned paths such as `CONTEXT.md`, `CONTEXT-MAP.md`, context-local ADRs, `docs/agents/`, and a configured `.scratch/` issue store.
4. Remove stale claims immediately when code behavior changes.
5. Avoid volatile implementation detail in root entrypoints and domain glossaries.
6. Create optional governance artifacts lazily, only when they have real content or an active workflow to govern.
7. Do not duplicate issue state in specs/design docs or durable decisions in issue discussion.
8. Update design docs in place to reflect the current or target system; preserve accepted decision history by superseding ADRs instead of rewriting them.

## References

- Read `references/context-system-spec.md` for artifact responsibilities, discovery rules, work boundaries, and migration decisions.
- Read `references/validation-rules.md` for capability-aware validator scope and enforcement patterns.
