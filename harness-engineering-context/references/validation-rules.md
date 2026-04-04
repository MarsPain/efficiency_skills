# Validation Rules

## Goal

Convert documentation governance into executable checks so context quality does not regress.

## Minimum Validator Coverage

1. Presence checks
- Required files exist (`AGENTS.md`, core `docs/*.md`).
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

5. Plan hygiene
- Ensure plan buckets (`active/completed/tech-debt`) exist.
- Ensure at least one completed plan exists after first delivery.

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
- before release cut.

## Failure Handling

When validation fails:

1. Fix broken links first.
2. Resolve conflicting status claims across docs.
3. Re-run validator and unit tests.
4. Include validation output in review notes.
