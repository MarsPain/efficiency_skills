# Validation Rules

## Goal

Convert documentation governance into executable checks so context quality does not regress.

## Minimum Validator Coverage

1. Presence checks
- Required root entrypoints exist (`README.md`, `AGENTS.md`, `ARCHITECTURE.md`) unless the repository intentionally documents an alternative.
- Required core docs exist (`docs/README.md`, relevant `docs/*.md`).
- Required directories exist (`docs/exec-plans/*`, `docs/design-docs`, etc.).

2. Redirect checks
- Legacy root docs contain migration markers.
- Redirect docs point to canonical paths in `docs/`.

3. Link integrity
- Parse markdown links.
- Validate internal relative links resolve.
- Ignore external URLs and in-page anchors.
- Prefer ignoring links inside fenced code blocks to avoid template false positives.

4. AGENTS map constraints
- Enforce concise size budget (for example <=140 lines).
- Ensure links to core docs entrypoints exist.

5. Root document role checks
- `README.md` contains onboarding or workflow entry content, not deep architecture dumps.
- `ARCHITECTURE.md` links to deeper architecture/design docs.
- Root docs do not duplicate large canonical sections from `docs/`.

6. Plan hygiene
- Ensure plan buckets (`active/completed/tech-debt`) exist.
- Ensure at least one completed plan exists after first delivery.

7. Canonical coverage and consistency
- Ensure each declared major section under `docs/` is linked from a root map or docs index.
- Flag orphan docs with no inbound links from `README.md`, `AGENTS.md`, `ARCHITECTURE.md`, or `docs/README.md`.
- Flag likely duplicate source-of-truth files when the same topic exists in both root and `docs/` with non-stub content.
- Ensure repository-specific rule docs (for example `SECURITY.md`, `BACKEND.md`, `DATA.md`) are either present and linked or explicitly omitted by configuration.

## Test Enforcement

Add a unit test that executes the validator script and fails on non-zero exit:

```python
result = subprocess.run([sys.executable, "scripts/validate_docs.py"], ...)
assert result.returncode == 0
```

Integrate this test into standard unit test commands.

## Operational Cadence

Run docs validation:

- before opening PR;
- after moving plans between lifecycle states;
- after architecture/doc migration refactors;
- after changing root entrypoint docs or developer workflows;
- before release cut.

## Failure Handling

When validation fails:

1. Fix broken links first.
2. Resolve conflicting status claims or duplicate source-of-truth drift.
3. Re-run validator and unit tests.
4. Include validation output in review notes.
