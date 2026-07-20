# Context System Spec

## Purpose

Define one repository-native context protocol so humans and agents can locate accurate information with minimal token overhead. The protocol standardizes artifact responsibilities and discovery while allowing optional capabilities to appear only when needed.

## Principles

1. **One artifact, one job, one canonical home.** Do not duplicate a glossary in a design doc, issue state in a spec, or an accepted decision in multiple narratives.
2. **Progressive disclosure.** Keep entrypoints concise and link to canonical detail.
3. **Capability-aware structure.** Standardize locations without requiring empty files or directories.
4. **Protocol-owned locations.** Use `docs/` by default, but preserve stable consumer interfaces such as root/context-local `CONTEXT.md`, ADR directories, configured issue trackers, and `.scratch/`.
5. **Compatibility-first migration.** Do not replace a path that downstream tooling edits directly with a redirect stub.
6. **Executable governance.** Discover active capabilities before validating them.

## Artifact Registry

| Artifact | Responsibility | Canonical location | Activation |
| --- | --- | --- | --- |
| Human entrypoint | Onboarding, setup, common workflows | `README.md` | Required |
| Agent entrypoint | Cross-agent navigation plus concise tool-specific instructions | `AGENTS.md` by default, with declared alternatives or tool-specific entrypoints allowed | Required |
| Architecture map | Topology, domains, package boundaries | `ARCHITECTURE.md` | Required unless a documented alternative exists |
| Domain glossary | Canonical domain terms; no implementation detail | root or context-local `CONTEXT.md` | Lazy |
| Context map | Multi-context navigation and relationships | root `CONTEXT-MAP.md` | Lazy; alternative to root `CONTEXT.md` |
| Agent configuration | Issue tracker, triage labels, domain-doc consumption | `docs/agents/` | Lazy |
| Accepted decisions | One durable decision, its rationale, non-obvious consequences, and supersession history | root or context-local `docs/adr/` | Lazy |
| Design documents | Current/target system structure, interfaces, data flow, constraints, failure modes, and alternatives | `docs/design-docs/` and selected core docs | Lazy |
| Product specs | Desired behavior, requirements, acceptance framing | `docs/product-specs/` or configured issue tracker | Lazy |
| Issues | Work units, state, dependencies, assignment, discussion | Configured tracker; `.scratch/` for Local Markdown | Lazy |
| Docs index | Navigation across active docs areas | `docs/README.md` | Required when `docs/` contains canonical docs |

## Entrypoint Resolution

Use `AGENTS.md` as the default cross-agent entrypoint. Accept an established alternative when repository configuration deliberately selects it. Tool-specific entrypoints such as `CLAUDE.md` may coexist with the cross-agent map.

Resolve the cross-agent map in this order:

1. Follow an explicit repository declaration if one exists.
2. Otherwise use `AGENTS.md` when it exists.
3. If only a supported alternative exists, accept it as the map.
4. If neither exists, use `AGENTS.md` unless the repository intentionally chooses another supported control surface.

Resolve shared operational blocks independently from the cross-agent map. For example, `setup-matt-pocock-skills` may place `## Agent skills` in `CLAUDE.md` while `AGENTS.md` remains the cross-agent map. Keep the complete shared block in one file, keep its detailed configuration canonical in `docs/agents/`, and link to it from every entrypoint that needs it. `docs/README.md` also indexes that directory.

## Domain Context Discovery

Domain context is optional and created lazily.

- If root `CONTEXT-MAP.md` exists, treat the repository as multi-context. Follow it to each relevant canonical `CONTEXT.md` and validate every declared link.
- Else if root `CONTEXT.md` exists, treat the repository as single-context.
- If neither exists, do not create an empty placeholder. Create root `CONTEXT.md` only when canonical domain language first needs recording.

`CONTEXT.md` is a glossary. It does not contain architecture, implementation details, specifications, issue state, or temporary hypotheses.

For a multi-context repository:

- keep system relationships in `CONTEXT-MAP.md`;
- keep each context's vocabulary in the `CONTEXT.md` referenced by the map;
- keep system-wide decisions in root `docs/adr/`;
- keep context-specific decisions in that context's `docs/adr/`.

## Work Artifact Model

The work system contains four complementary artifacts:

1. **Spec:** defines the desired outcome, motivation, constraints, acceptance behavior, accepted implementation/testing decisions, and change-scoped migration or delivery considerations.
2. **Issue:** owns an actionable work unit, dependency edges, assignment, current state, and discussion.
3. **Design doc:** explains deeper current or target-system structure and technical design that outlives one change.
4. **ADR:** records one accepted, durable decision that future work should not silently re-litigate.

## Design Docs and ADRs

Use design docs to answer how a system works or should work. They may compare alternatives while a design is unsettled, and they are revised as the current or target system changes.

Create an ADR only when all three conditions hold:

1. reversing the decision would be meaningfully costly;
2. a future reader would find the choice surprising without its context;
3. credible alternatives existed and the decision resolved a real trade-off.

Use these ownership rules:

- one ADR records one accepted decision, its rationale, and only the non-obvious consequences worth preserving;
- an accepted ADR is authoritative for that decision's status and historical rationale;
- a design doc is authoritative for the current or target system design;
- before acceptance, keep alternatives and exploration in the design doc;
- after acceptance, keep a concise decision summary and ADR link in the design doc instead of copying the full rationale;
- when broader context helps, link the ADR back to the design doc;
- when a decision changes, create a superseding ADR and update the design doc to reflect the newly accepted system;
- do not require every design doc to produce an ADR or every ADR to have a design doc.

Use links instead of duplication:

- each implementation issue links to its parent spec; tracker-native relationships or generated views may provide spec-to-issue backlinks;
- issues link to relevant design docs or ADRs when needed;
- design docs do not reproduce live issue state or change-scoped acceptance criteria;
- an ADR links to the motivating spec, issue, or design doc when useful but remains independently durable.

The configured issue tracker is authoritative for task state, dependencies, assignment, discussion, and technical debt. Put migration, rollout, rollback, and system-level verification in the spec when they belong to one change; keep slice-local checklists in the relevant issue. Do not introduce a parallel execution-plan lifecycle.

## Standard Layout

```text
README.md
AGENTS.md                         # default cross-agent map
CLAUDE.md                         # optional tool-specific entrypoint
ARCHITECTURE.md
CONTEXT.md                        # optional single-context glossary
CONTEXT-MAP.md                    # optional multi-context alternative
.scratch/                         # optional Local Markdown tracker
docs/
├── README.md
├── DESIGN.md                     # optional
├── agents/                       # optional operational configuration
├── adr/                          # optional system-wide ADRs
├── design-docs/                  # optional deep designs
├── generated/                    # optional
├── product-specs/                # optional
└── references/                   # optional
```

Multi-context repositories may also contain:

```text
src/<context>/CONTEXT.md
src/<context>/docs/adr/
```

The paths are examples; `CONTEXT-MAP.md` is authoritative for locating contexts.

## Migration Pattern

1. Inventory active artifact types and their actual consumers.
2. Select one canonical home for each type.
3. Preserve directly edited protocol paths; move only artifacts whose consumers can follow redirects or updated configuration.
4. Separate mixed documents into glossary, architecture, design, decision, spec, and issue responsibilities.
5. Normalize cross-links and indexes.
6. Add capability-aware validation and unit-test enforcement.
7. Remove redirects after all consumers and references have migrated.

If the repository already has `docs/exec-plans/`, treat it as legacy material:

- preserve completed records and inbound links;
- move active task state and dependencies to the configured issue tracker;
- move change-scoped requirements, migration, rollout, rollback, and verification into the relevant spec or issues;
- move durable target-system design into design docs and durable decisions into ADRs;
- leave a concise historical pointer when moving content would otherwise break consumers;
- do not create new execution-plan lifecycle artifacts under the unified protocol.

## Change Synchronization Rules

- Setup or contributor workflow change: update `README.md` and linked docs.
- Agent workflow or tracker configuration change: update the relevant agent entrypoint or shared-block owner and `docs/agents/`.
- Domain vocabulary change: update the relevant `CONTEXT.md` and, for multi-context topology, `CONTEXT-MAP.md`.
- Architecture boundary or topology change: update `ARCHITECTURE.md` and relevant design docs; create an ADR only for a qualifying durable decision.
- Accepted decision change: create a superseding ADR and update affected design docs to reflect the current or target system.
- Product behavior or acceptance change: update the product spec and linked issues.
- Change-scoped migration, rollout, rollback, or system-level verification change: update the spec and affected issues.
- Issue state, dependency, assignment, or discussion change: update only the configured issue tracker.
