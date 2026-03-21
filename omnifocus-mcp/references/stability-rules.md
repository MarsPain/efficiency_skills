# Stability Rules and Edge Cases

Apply these mitigations for reliable behavior.

1. Avoid raw single quotes (`'`) in names/notes when calling `add_project` or name-based `remove_item`.
2. Prefer ID-based removal and normalization of apostrophes to safe ASCII alternatives where possible.
3. Treat `deferredUntil` as unreliable; emulate with explicit `deferOn` day windows.
4. Treat `dueWithin` as potentially including overdue items; filter out `Overdue` when user asks future-only.
5. Use exact built-in perspective casing in `get_perspective_view` (for example: `Inbox`, `Projects`, `Flagged`).
6. Do not rely on `includeMetadata` in `get_perspective_view` to change behavior.
7. Do not rely on `createSequentially` in `batch_add_items` to change behavior.
8. Interpret relative dates in user locale timezone and echo absolute dates in responses.
9. For delete/complete, always preview and require explicit confirmation before mutation.
10. For delete/complete, always mutate by `id`, never by name-only matching.
