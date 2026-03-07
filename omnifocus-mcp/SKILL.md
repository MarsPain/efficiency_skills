---
name: omnifocus-mcp
description: Reliable OmniFocus execution with OmniFocus MCP tools. Use when Codex needs to capture, clarify, organize, review, or execute OmniFocus work; process inbox; plan today/this week; run weekly review; add/edit/remove tasks or projects; batch-create actions from notes; query by status, dates, tags, projects, folders, or perspectives.
---

# OmniFocus MCP

## Overview
Use this skill to run end-to-end OmniFocus workflows with predictable tool choice, low token usage, and safe write behavior.

Read first, then write. Prefer IDs over names for updates and removals.

## Tool Selection
Choose tools in this order:

1. Use `query_omnifocus` for almost all reads.
2. Use `list_tags` before assigning tags when tag names are uncertain.
3. Use `list_perspectives` and `get_perspective_view` only for perspective-specific requests.
4. Use `dump_database` only when the user asks for full-database analysis or when targeted queries cannot answer.
5. Use single-item tools for one change: `add_omnifocus_task`, `add_project`, `edit_item`, `remove_item`.
6. Use batch tools for multiple changes: `batch_add_items`, `batch_remove_items`.

## Core Guardrails
Apply these guardrails on every run:

1. Confirm scope before mutation: query candidate items first and summarize intended changes.
2. Mutate by `id` whenever possible; avoid name-only mutation if multiple matches are possible.
3. Keep payloads minimal: request only needed `fields`, add `limit`, and use `summary: true` for counts.
4. Re-query after writes and report the exact delta (created/updated/removed item names and IDs).
5. Split large writes into small batches to reduce failure blast radius.
6. Treat delete and complete as high-risk actions: preview candidates first and do not execute until the user gives explicit confirmation.
7. For delete and complete, always use `id`; do not execute name-only operations when any ambiguity exists.
8. Avoid bulk delete/complete by default; if user asks bulk changes, execute in small chunks after confirmation.

## Stability Rules (Known Edge Cases)
Use these mitigations for stable behavior:

1. Avoid raw single quotes (`'`) in names/notes when calling `add_project` or name-based `remove_item`; prefer ID-based removal and normalize apostrophes to a safe ASCII alternative when possible.
2. Treat `deferredUntil` as unreliable; emulate with explicit day windows using `deferOn` queries.
3. Treat `dueWithin` as possibly including overdue items; if the user wants future-only, filter out `Overdue` explicitly.
4. Use exact built-in perspective casing in `get_perspective_view` (for example: `Inbox`, `Projects`, `Flagged`).
5. Do not rely on `includeMetadata` in `get_perspective_view` or `createSequentially` in `batch_add_items` to change behavior.

## Workflow
Map user intent to this sequence.

### 1) Capture
Use when user dumps ideas, meeting notes, or transcript actions.

1. Parse candidate actions and project outcomes.
2. Create tasks in Inbox or target projects with `batch_add_items`.
3. Keep metadata light during capture: name + note + optional tag.

### 2) Clarify
Use when deciding actionable next steps.

1. Query Inbox tasks using `query_omnifocus` with `projectName: "inbox"`.
2. Rewrite vague tasks into concrete verbs.
3. Apply `edit_item` to update names, notes, tags, and dates.

### 3) Organize
Use when assigning context, project, and calendar intent.

1. Query projects/tags first (`query_omnifocus` + `list_tags`).
2. Set `deferDate`, `dueDate`, and `plannedDate` deliberately.
3. Move or refactor structure using `edit_item` or `batch_add_items` with hierarchy fields.

### 4) Reflect
Use for daily/weekly review.

1. Daily: query `status` in `["Next", "Available", "DueSoon", "Overdue"]`, sorted by `dueDate`.
2. Weekly: query stale tasks (old `modificationDate`, missing notes, blocked tasks).
3. Summarize risks, then propose edits before writing.

### 5) Engage
Use for focused execution lists.

1. Build short actionable lists by context (`tags`), energy/time (`estimatedMinutes`), and urgency (`dueOn`, `dueWithin`).
2. Return concise execution order with rationale.
3. Apply only user-approved changes.

## Query and Write Patterns
Load reusable payload templates from [references/tool-playbook.md](references/tool-playbook.md) before constructing tool calls.

## Response Contract
For each request:

1. State chosen tool strategy in one line.
2. Execute read(s), then write(s) only if required.
3. Return results in this order: summary, changed items, follow-up options.
4. For delete/complete requests, return a preview list first (name + id + project), then wait for explicit user confirmation before mutation.
