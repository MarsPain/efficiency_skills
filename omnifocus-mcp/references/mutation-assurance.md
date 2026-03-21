# Mutation Assurance

Use this checklist before and after any mutation.

## Pre-Mutation
1. Confirm target scope via read query.
2. Resolve explicit IDs for mutation.
3. For child-task completion, capture both `parent_id` and `child_id`.
4. If same-name candidates exist, stop and require user selection by ID.

## Mutation
1. Execute write by `id` only.
2. Do not use name-only mutation for `delete` or `complete`.

## Post-Mutation Assertion
1. Re-query mutated target by scope.
2. Verify expected transition (for example `available -> completed`).
3. If transition not observed, mark operation as failed.
4. Return remediation steps instead of success language.

## Mandatory Receipt Fields
Return all fields on write operations:

- `target_id`
- `target_name`
- `parent_id` (if applicable)
- `parent_name` (if applicable)
- `before_status`
- `after_status`
- `assertion` (`pass` or `fail`)

## Same-Name Collision Rule
When candidate names collide after normalization:

1. Return top candidates with `id + parent_path`.
2. Do not mutate until user selects exact `id`.
