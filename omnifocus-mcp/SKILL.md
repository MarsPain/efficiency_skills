---
name: omnifocus-mcp
description: Reliable OmniFocus execution with MCP tools, including safe fuzzy retrieval and deterministic candidate confirmation for ambiguous requests. Use when Codex needs to capture, clarify, organize, reflect, or engage on OmniFocus work; process inbox; plan today/this week; run weekly review; query by status, dates, tags, projects, folders, or perspectives; and create/update/remove tasks or projects with low-risk mutation flow.
---

# OmniFocus MCP

## Overview
Run end-to-end OmniFocus workflows with predictable tool choice, low token usage, and safe write behavior.

Read first, then write. Mutate by `id`.

## Tool Strategy
Choose tools in this order:

1. Use `query_omnifocus` for almost all reads.
2. Use `list_tags` before assigning tags when names are uncertain.
3. Use `list_perspectives` and `get_perspective_view` only for perspective-specific requests.
4. Use `dump_database` only when:
   - the user explicitly asks for full-database analysis, or
   - two targeted `query_omnifocus` attempts still cannot answer.
5. Use single-item tools for one change: `add_omnifocus_task`, `add_project`, `edit_item`, `remove_item`.
6. Use batch tools for multiple changes: `batch_add_items`, `batch_remove_items`.

Load templates from [references/tool-playbook.md](references/tool-playbook.md) before constructing payloads.

## Mutation Safety Protocol
Apply this fixed sequence for all writes:

1. Preview scope with a read query.
2. Summarize intended changes.
3. If action is high-risk (`delete` or `complete`), always ask explicit confirmation.
4. Execute mutation by `id` only.
5. Re-query and report exact delta.
6. Assert target state transition by `id` before claiming success.

### Completion Targeting Guardrail
For completing subtasks by natural language:

1. Resolve and retain both `parent_id` and `child_id` before mutation.
2. Do not complete by child name alone.
3. If parent path is missing or ambiguous, stop and request disambiguation.

### Ambiguity Policy
Use this policy whenever matching by name/text:

1. `matches > 1`: stop mutation, return candidates, ask user to choose.
2. `matches = 0`: stop mutation, broaden query, and return retry options.
3. `matches = 1`: continue only if candidate confidence is high.

### Same-Name Hard Stop
If normalized names collide across candidates (especially short names like `RL`):

1. stop mutation,
2. return candidate list with `id + parent_path`,
3. require explicit user selection by `id`.

Do not execute name-only delete/complete operations.

### Batch Policy
1. Use small write batches (default 10-20 items per batch).
2. Re-query after each batch.
3. Stop remaining batches immediately if one batch fails.

### Failure Recovery
When a write partially succeeds, return:

1. `succeeded`: name + id
2. `failed`: name/id + error
3. `next step`: safe retry plan (usually smaller batch or explicit id-only retry)

## Fuzzy Search and Ranking Protocol
Use fuzzy search only for candidate discovery, never as direct mutation targeting.

1. Expand query semantically with model-generated variants (synonyms, abbreviations, typo variants).
2. Run broad reads for each variant and merge by `id`.
3. Re-rank candidates with hybrid scoring:
   - model semantic judgment for intent fit
   - deterministic tie-breakers: exact > prefix > token overlap > edit-distance similarity
4. Return top candidates with `id`, `name`, `project`, and brief match reason.
5. Require user confirmation before any write.

If needed, run deterministic local ranking with:

```bash
uv run python scripts/fuzzy_rank.py --query "<query>" --input <candidates.json>
```

For non-trivial write payloads, run preflight checks with:

```bash
uv run python scripts/payload_lint.py --tool <tool_name> --input <payload.json>
```

Load full protocol from [references/fuzzy-search.md](references/fuzzy-search.md).

## Date and Time Semantics
1. Interpret relative dates in the user's locale timezone.
2. For `today`/`tomorrow`/windows, always echo absolute dates in output (for example `2026-03-21`).
3. Treat `dueWithin` as potentially including overdue items; if user wants future-only, filter out `Overdue`.
4. Treat `deferredUntil` as unreliable; emulate with explicit `deferOn` day windows.

More edge cases: [references/stability-rules.md](references/stability-rules.md).
Execution assurance details: [references/mutation-assurance.md](references/mutation-assurance.md).

## Workflow
Map user intent to this sequence.

### 1) Capture
1. Parse candidate actions and project outcomes.
2. Create tasks in Inbox or target projects with `batch_add_items`.
3. Keep capture payload lean: `name` + `note` + optional tag.

### 2) Clarify
1. Query Inbox tasks with `projectName: "inbox"`.
2. Rewrite vague tasks into concrete verb phrases.
3. Apply `edit_item` for names, notes, tags, dates.

### 3) Organize
1. Query projects and tags first (`query_omnifocus` + `list_tags`).
2. Set `deferDate`, `dueDate`, `plannedDate` deliberately.
3. Use `edit_item` / `batch_add_items` for structure changes.

### 4) Reflect
1. Daily: query `status` in `["Next", "Available", "DueSoon", "Overdue"]`, sort by `dueDate`.
2. Weekly: query stale tasks (old `modificationDate`, blocked status, missing notes).
3. Summarize risks before proposing writes.

### 5) Engage
1. Build short action lists by context (`tags`), time (`estimatedMinutes`), and urgency (`dueOn`, `dueWithin`).
2. Return concise execution order with rationale.
3. Apply only user-approved changes.

## Performance Hints
1. Keep payloads minimal: request only needed `fields`, set `limit`, use `summary: true` for counts.
2. Cache tag list within the same turn/session unless user asks to refresh.
3. Prefer targeted reads over broad dumps.
4. For high-risk or large writes, run `payload_lint.py` before mutation.

## Response Contract
For each request, return in this order:

1. Tool strategy in one line.
2. Summary (include absolute date interpretation when relative dates are used).
3. Changed items with names and IDs, including before/after counts for writes.
4. Execution receipt (for writes):
   - `target_id`
   - `target_name`
   - `parent_id` (if applicable)
   - `parent_name` (if applicable)
   - `before_status`
   - `after_status`
   - `assertion` (`pass` or `fail`)
5. Follow-up options.

For delete/complete requests, always return preview first (`name + id + parent_path`) and wait for explicit confirmation before mutation.
