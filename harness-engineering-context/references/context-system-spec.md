# Context System Spec

## Purpose

Define a repository-native context system so agents can quickly find accurate information with minimal token overhead.

## Principles

1. Map vs record separation:
- `AGENTS.md` is a map.
- `docs/` is the record.

2. Progressive disclosure:
- Keep high-frequency guidance in `AGENTS.md`.
- Keep deep detail in domain files under `docs/`.

3. Versioned planning:
- Represent execution lifecycle through `docs/exec-plans/{active,completed,tech-debt}`.

4. Compatibility-first migration:
- Keep old top-level docs as redirect stubs during transition.

## Recommended File Responsibilities

- `docs/DESIGN.md`: architecture overview and contracts.
- `docs/FRONTEND.md`: frontend scope/constraints (or explicitly state backend-only).
- `docs/PLANS.md`: plan index, state legend, and stage summary.
- `docs/PRODUCT_SENSE.md`: value model, users, north-star metrics.
- `docs/ROADMAP.md`: milestone-level direction and go/no-go criteria.
- `docs/design-docs/*`: deep technical designs.
- `docs/generated/*`: generated artifacts + index.
- `docs/product-specs/*`: product/API specs.
- `docs/references/*`: external references and supporting material.

## Migration Pattern

1. Extract detailed sections from root docs into `docs/`.
2. Replace root docs with short migration stubs and links.
3. Normalize cross-links to canonical files.
4. Add automated validation and unit test enforcement.
