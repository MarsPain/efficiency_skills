# OmniFocus MCP Playbook

Use these templates as starting points. Keep only needed fields.

## Safe Query Defaults

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

## Safe Field and Sort Set

Prefer these fields for `tasks` queries:

- `id`, `name`, `taskStatus`, `flagged`, `dueDate`, `deferDate`, `plannedDate`
- `estimatedMinutes`, `tagNames`, `projectName`, `note`, `modificationDate`

Prefer these `sortBy` values:

- `dueDate`, `plannedDate`, `modificationDate`, `estimatedMinutes`, `name`

Avoid dynamically constructing field names from user text.

## Workflow Templates

### Capture Inbox

```json
{
  "items": [
    {
      "type": "task",
      "name": "[actionable verb phrase]",
      "note": "[source context]"
    }
  ]
}
```

Tool: `batch_add_items`

### Clarify Inbox

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

Tool: `query_omnifocus`

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

Tool: `query_omnifocus`

### Weekly Review (Stale Items)

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

Tool: `query_omnifocus`

### Context View by Tag

```json
{
  "entity": "tasks",
  "filters": {
    "tags": ["@computer"],
    "status": ["Next", "Available"]
  },
  "fields": ["id", "name", "estimatedMinutes", "projectName", "dueDate"],
  "sortBy": "estimatedMinutes",
  "sortOrder": "asc",
  "limit": 40
}
```

Tool: `query_omnifocus`

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

Tool: `query_omnifocus`

## Write Playbook

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

### Complete Task Safely

1. Query first and present candidate list (name + id + project).
2. Complete only after explicit user confirmation.
3. Complete by `id`, then re-query to verify status changed.

```json
{
  "itemType": "task",
  "id": "[task-id]",
  "newStatus": "completed"
}
```

Tool: `edit_item`

### Remove Item Safely

1. Query first to get exact `id`.
2. Present preview and wait for explicit confirmation.
3. Remove by `id`, then re-query to verify.

```json
{
  "itemType": "task",
  "id": "[task-id]"
}
```

Tool: `remove_item`

### Batch Add with Hierarchy

```json
{
  "items": [
    { "type": "task", "name": "Plan sprint", "tempId": "t1" },
    { "type": "task", "name": "Write draft", "parentTempId": "t1" },
    { "type": "task", "name": "Review draft", "parentTempId": "t1" }
  ]
}
```

Tool: `batch_add_items`

## Fallback Rules

1. If query result is too large, reduce `fields` and add stricter `filters` + `limit`.
2. If a write fails, retry with smaller batch size and explicit IDs.
3. If perspective output looks inconsistent, use `query_omnifocus` equivalent filters as fallback.
4. For delete/complete failures, stop further mutations, report partial results, and request user decision before retry.
