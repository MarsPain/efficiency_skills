# Validation Rules

## Goal

Convert documentation governance into executable, capability-aware checks so context quality does not regress without forcing unused artifacts into every repository.

## Discovery Before Validation

Build an in-memory artifact registry before applying checks:

1. Resolve the human entrypoint, cross-agent map, tool-specific agent entrypoints, and architecture entrypoint.
2. Detect `CONTEXT.md` versus `CONTEXT-MAP.md` and follow multi-context links.
3. Discover root and context-local `docs/adr/` directories.
4. Read `docs/agents/domain.md`, `docs/agents/issue-tracker.md`, and `docs/agents/triage-labels.md` when present.
5. Determine whether the configured issue tracker is external or Local Markdown.
6. Record one expected canonical location for each active artifact type.

Do not infer a special mode from a filename alone. Validate the unified artifact contract against the capabilities actually present or declared.

## Minimum Validator Coverage

### 1. Entrypoint checks

- Require `README.md`.
- Require `ARCHITECTURE.md` unless the repository explicitly documents an alternative.
- Require one cross-agent map; prefer `AGENTS.md` by default and accept a declared alternative.
- Enforce a concise size budget on map-style entrypoints, for example no more than 140 lines.
- If both `AGENTS.md` and `CLAUDE.md` exist, allow distinct tool-specific instructions but flag duplicated shared operational blocks.

### 2. Domain-context checks

- Allow neither domain file to exist; domain documentation is lazy.
- If root `CONTEXT.md` exists, validate that it is the single-context glossary and that root `CONTEXT-MAP.md` is not simultaneously authoritative.
- If `CONTEXT-MAP.md` exists, validate every declared context link and ensure relevant context glossaries are reachable through it.
- Flag likely implementation detail, task state, or copied specifications in a glossary when a reliable repository-specific rule can detect it.
- Treat context-local `CONTEXT.md` files as canonical artifacts, not orphan docs, when the map links to them.

### 3. ADR checks

Automate paths, links, naming, explicit status, and supersession relationships. Keep the three-part ADR-worthiness test and rationale-duplication judgment in review unless repository metadata or declared conventions make them deterministic; do not implement brittle keyword heuristics.

- Discover root and context-local `docs/adr/` lazily.
- Ensure system-wide ADRs are reachable from `ARCHITECTURE.md` or `docs/README.md`.
- Ensure context-local ADRs are reachable from their context glossary, context documentation, or the docs index.
- In review, confirm each ADR is scoped to one accepted decision and do not require ADRs for reversible, obvious, or no-alternative choices.
- Check that accepted ADRs preserve their original rationale and use status/supersession links when revisited rather than being silently rewritten.
- Flag the same accepted decision copied into multiple ADR scopes; allow cross-links and supersession records.
- Flag ADRs that grow into full system designs or implementation checklists.
- Validate repository numbering and naming conventions when declared.

### 4. Agent-configuration checks

- When `docs/agents/` exists, require its major configuration files to be reachable from the entrypoint that owns the corresponding shared block and from `docs/README.md`.
- Treat `docs/agents/*.md` as operational configuration, not as human onboarding or duplicate design documentation.
- When `docs/agents/issue-tracker.md` declares Local Markdown, allow `.scratch/` as the issue store.
- When an external tracker is configured, flag repository claims that make `.scratch/` a competing authoritative issue store unless explicitly documented as archival or temporary.
- Require triage-label configuration only when the repository declares that triage capability.

### 5. Link and index integrity

- Parse Markdown links and validate internal relative targets.
- Ignore external URLs and in-page anchors.
- Ignore links inside fenced code blocks to avoid template false positives.
- Require `docs/README.md` when `docs/` contains canonical documents.
- Ensure each active docs area is linked from an entrypoint, `docs/README.md`, a context map, or its owning context.
- Exclude issue files under a configured `.scratch/` tracker from documentation-orphan rules.

### 6. Source-of-truth boundaries

- Flag likely duplicate canonical topics across root files, `docs/`, context-local docs, specs, issues, design docs, and ADRs.
- Permit short maps, summaries, links, redirect stubs, and ADR supersession pointers.
- Ensure `CONTEXT.md` owns vocabulary, `ARCHITECTURE.md` owns the top-level system map, specs own change-scoped behavior and accepted implementation/testing decisions, design docs own current/target system design, ADRs own qualifying accepted decisions and their historical rationale, and the issue tracker owns task state.
- Do not require deep detail to live under `docs/` when the artifact registry assigns it to a protocol-owned location.

### 7. Work-artifact checks

- Require each implementation issue to identify its parent spec; validate reverse relationships only when the tracker provides them without requiring parent-spec mutation.
- Flag live task state, dependency graphs, or technical-debt queues copied outside the configured issue tracker.
- Allow change-scoped migration, rollout, rollback, and system-level verification in the spec; allow slice-local checklists in the relevant issue.
- Flag design docs that duplicate live issue state or change-scoped acceptance criteria.
- In review, require an accepted ADR-worthy decision to appear in the design doc only as a concise summary and link instead of duplicated full rationale; allow design-only exploration before acceptance.
- When an ADR is superseded, check that affected design docs describe the newly accepted current/target system rather than the historical one.
- Flag ADRs that act as implementation checklists instead of durable decision records.
- When legacy `docs/exec-plans/` exists, validate its links and historical reachability without requiring lifecycle buckets or treating it as an active source of truth.

## Suggested Scenario Tests

Exercise the validator against at least these fixtures:

1. Minimal repository with only the required entrypoints and no domain or work artifacts.
2. Single-context repository with root `CONTEXT.md` and root `docs/adr/`.
3. Multi-context repository with `CONTEXT-MAP.md`, context-local glossaries, and mixed system/context ADRs.
4. Repository whose selected agent entrypoint is `CLAUDE.md` and whose `AGENTS.md` is absent or a concise pointer.
5. GitHub/GitLab/other external tracker configured through `docs/agents/issue-tracker.md`.
6. Local Markdown tracker using `.scratch/` without orphan-doc false positives.
7. Complex migration expressed through one spec, linked issues, an optional design doc, and an optional ADR without a parallel plan lifecycle.
8. Legacy execution-plan archive with preserved links and no active task-state ownership.
9. Design-only exploration with no premature ADR.
10. Focused ADR that needs no design doc.
11. Design doc with several accepted decisions linked to separate ADRs, followed by one superseding ADR and an updated design doc.
12. Duplicate glossary, duplicated operational block, broken context link, and spec/issue/design/ADR ownership failure cases.

## Test Enforcement

Add a unit test that executes the validator and fails on non-zero exit:

```python
result = subprocess.run([sys.executable, "scripts/validate_docs.py"], ...)
assert result.returncode == 0
```

Integrate this test into standard unit-test and CI commands.

## Operational Cadence

Run docs validation:

- before opening a PR;
- after changing entrypoints or agent configuration;
- after adding or changing domain contexts or ADR scopes;
- after changing specs, issue-tracker ownership, design docs, or ADR boundaries;
- after changing the configured issue tracker;
- after architecture or documentation migrations;
- before a release cut.

## Failure Handling

1. Fix broken links and unresolved canonical locations first.
2. Resolve competing entrypoints, duplicate sources of truth, or invalid artifact scopes.
3. Correct work-artifact ownership or index drift.
4. Re-run the validator and unit tests.
5. Include validation output in review notes.
