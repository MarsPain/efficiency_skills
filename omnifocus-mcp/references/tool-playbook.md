# OmniFocus MCP Playbook

## Table of Contents
1. Safe read defaults
2. Read templates
3. Write templates
4. High-risk action runbook
5. Parent-constrained complete runbook
6. Batch execution runbook
7. Failure recovery template
8. Fuzzy search quickstart
9. Payload lint quickstart
10. Execution receipt template

## 1) Safe Read Defaults
Use this default shape for targeted reads:

```json
{
  "entity": "tasks",
  "filters": {},
  "fields": ["id", "name", "taskStatus", "dueDate", "projectName"],
  "limit": 50
}
```

Use `summary: true` for counts.

Preferred task fields:
- `id`, `name`, `taskStatus`, `flagged`, `dueDate`, `deferDate`, `plannedDate`
- `estimatedMinutes`, `tagNames`, `projectName`, `note`, `modificationDate`

Preferred sort fields:
- `dueDate`, `plannedDate`, `modificationDate`, `estimatedMinutes`, `name`

## 2) Read Templates

### Inbox Clarify

```json
{
  "entity": "tasks",
  "filters": {
    "projectName": "inbox"
  },
  "fields": ["id", "name", "note", "flagged", "dueDate", "tagNames"],
  "limit": 100
}
```

### Daily Focus List

```json
{
  "entity": "tasks",
  "filters": {
    "status": ["Next", "Available", "DueSoon", "Overdue"]
  },
  "fields": ["id", "name", "taskStatus", "dueDate", "plannedDate", "projectName"],
  "sortBy": "dueDate",
  "sortOrder": "asc",
  "limit": 25
}
```

### Weekly Review (Stale)

```json
{
  "entity": "tasks",
  "filters": {
    "status": ["Available", "Blocked"],
    "hasNote": false
  },
  "fields": ["id", "name", "taskStatus", "projectName", "modificationDate"],
  "sortBy": "modificationDate",
  "sortOrder": "asc",
  "limit": 50
}
```

### Count Items in a Project

```json
{
  "entity": "tasks",
  "filters": {
    "projectName": "[project name]"
  },
  "summary": true
}
```

## 3) Write Templates

### Single Task Update by ID

```json
{
  "itemType": "task",
  "id": "[task-id]",
  "newName": "[new task title]",
  "newDueDate": "2026-03-10",
  "replaceTags": ["@computer", "deep-work"]
}
```

Tool: `edit_item`

### Remove Item by ID

```json
{
  "itemType": "task",
  "id": "[task-id]"
}
```

Tool: `remove_item`

## 4) High-Risk Action Runbook
For `delete` and `complete`:

1. Query candidates first.
2. Return preview (`name`, `id`, `parent_path`).
3. Wait for explicit user confirmation.
4. Execute by `id` only.
5. Re-query and assert target state transition before success claim.

## 5) Parent-Constrained Complete Runbook
Use this when user says "complete child task X under parent Y".

1. Resolve parent candidate and keep `parent_id`.
2. Resolve child candidate under that parent and keep `child_id`.
3. If child name collisions exist, stop and require explicit `child_id` confirmation.
4. Execute completion by `child_id`:

```json
{
  "itemType": "task",
  "id": "[child-id]",
  "newStatus": "completed"
}
```

5. Assert write by re-querying `child_id` and checking `before_status -> after_status`.

## 6) Batch Execution Runbook
1. Default batch size: 10-20 items.
2. Run each batch independently.
3. Re-query after each batch.
4. Stop remaining batches on first failure.
5. Return partial-success report.

## 7) Failure Recovery Template
When partial success occurs, return:

```text
Succeeded:
- <name> (<id>)

Failed:
- <name or id>: <error>

Next step:
- Retry failed items only in smaller batch (<=5), id-based.
```

## 8) Fuzzy Search Quickstart
Use fuzzy matching only for candidate discovery.

1. Expand query with model-generated variants.
2. Run broad reads and merge by `id`.
3. Re-rank:
- first by model semantic fit
- then deterministic tie-breakers (exact, prefix, token overlap, edit distance)
4. Return top candidates with reasons and IDs.
5. For writes, require user selection by ID.

Deterministic local ranking helper:

```bash
uv run python scripts/fuzzy_rank.py --query "followup legal" --input /tmp/of_candidates.json --top 8
```

Full protocol: [fuzzy-search.md](fuzzy-search.md)
Edge rules: [stability-rules.md](stability-rules.md)

## 9) Payload Lint Quickstart
For non-trivial writes, validate payload before calling mutation tools.

```bash
uv run python scripts/payload_lint.py --tool edit_item --input /tmp/of_edit_payload.json
uv run python scripts/payload_lint.py --tool batch_add_items --input /tmp/of_batch_payload.json
```

Behavior:
- exits `0` when no hard errors
- exits `1` when safety checks fail
- returns JSON with `errors` and `warnings`

## 10) Execution Receipt Template
For every write, return a structured receipt:

```text
target_id: <id>
target_name: <name>
parent_id: <id or n/a>
parent_name: <name or n/a>
before_status: <status>
after_status: <status>
assertion: <pass|fail>
```

Do not claim success if `assertion=fail`.
