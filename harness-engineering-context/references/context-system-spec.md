# Context System Spec

## Purpose

Define a repository-native context system so agents can quickly find accurate information with minimal token overhead.

## Principles

1. Map vs record separation:
- `README.md` is the human entrypoint.
- `AGENTS.md` is the agent map.
- `ARCHITECTURE.md` is the architecture map.
- `docs/` is the canonical record.

2. Progressive disclosure:
- Keep high-frequency entry guidance in root maps.
- Keep deep detail in domain files under `docs/`.

3. Versioned planning:
- Represent execution lifecycle through `docs/exec-plans/{active,completed,tech-debt}`.

4. Compatibility-first migration:
- Keep old top-level docs as redirect stubs during transition.

## Recommended File Responsibilities

- `README.md`: onboarding, setup, common commands, contribution entrypoints.
- `AGENTS.md`: navigation for agents, repository constraints, key commands, docs map.
- `ARCHITECTURE.md`: top-level domains, package boundaries, system topology, links to deep design docs.
- `docs/README.md`: docs index and section navigation.
- `docs/DESIGN.md`: architecture overview and contracts.
- `docs/FRONTEND.md`: frontend scope/constraints (or explicitly state backend-only).
- `docs/SECURITY.md`: trust boundaries, auth, secrets, data handling, external exposure.
- `docs/PLANS.md`: plan index, state legend, and stage summary.
- `docs/PRODUCT_SENSE.md`: value model, users, north-star metrics.
- `docs/ROADMAP.md`: milestone-level direction and go/no-go criteria.
- `docs/design-docs/*`: deep technical designs.
- `docs/generated/*`: generated artifacts + index.
- `docs/product-specs/*`: product/API specs.
- `docs/references/*`: external references and supporting material.

Optional but often useful:

- `docs/BACKEND.md`: service boundaries, APIs, async jobs, integration rules.
- `docs/DATA.md`: schemas, ownership, migrations, retention, and lineage.

Only require documents that match the repository's real complexity. Avoid empty governance shells.

## Migration Pattern

1. Extract detailed sections from root docs into `docs/`.
2. Keep `README.md`, `AGENTS.md`, and `ARCHITECTURE.md` as short maps; replace other old root docs with redirect stubs and links.
3. Normalize cross-links to canonical files.
4. Add automated validation and unit test enforcement.

## Change Synchronization Rules

Update the relevant root entrypoints and canonical docs in the same change set:

- Setup or contributor workflow change:
  - update `README.md`
  - update linked docs under `docs/` as needed
- Agent workflow or navigation change:
  - update `AGENTS.md`
  - update linked docs under `docs/` as needed
- Architecture boundary or topology change:
  - update `ARCHITECTURE.md`
  - update `docs/DESIGN.md` and related `docs/design-docs/*`
- Product flow or acceptance change:
  - update `docs/product-specs/*`
- Security boundary or secret handling change:
  - update `docs/SECURITY.md`
