---
name: git-commit
description: Use when an agent needs to create a local git commit; when the user says commit, checkpoint, save changes, record this work, or similar; when a long coding task accumulates many related modifications worth preserving before continuing; or before any git commit command.
---

# Git Commit

## Overview

Create local commits deliberately: preserve the user's work, stage only intentional changes, choose the largest coherent commit that remains reviewable, write English Conventional Commit messages, and never perform remote or history-rewriting operations.

## Non-Negotiable Safety Rules

- Do not push, pull, fetch, rebase, reset, clean, stash, amend, squash, force, tag, or rewrite history.
- Do not use `git commit --amend`, `git push`, `git reset`, `git checkout --`, `git restore`, `git clean`, or `git stash` unless the user explicitly asks for that specific operation in the current turn.
- Do not use `--no-verify` unless the user explicitly asks and accepts the risk.
- Do not stage unrelated changes, generated junk, credentials, local config, or files outside the task scope.
- Do not discard, overwrite, or "tidy up" user changes to make the commit cleaner.
- Treat untracked files as suspicious until inspected or clearly explained by the task.
- If anything is ambiguous, ask before committing. A local commit is allowed only after the staged content is understood.

## Workflow

1. Inspect repository state:
   - Run `git status --short`.
   - Run `git branch --show-current` when the branch matters.
   - Review unstaged, staged, and untracked changes with `git diff`, `git diff --staged`, and targeted file reads.
   - Check recent commit style with `git log -5 --oneline` when writing the message.

2. Classify changes:
   - `ours`: changes made for the current task.
   - `user`: pre-existing or unrelated changes; leave them unstaged unless the user clearly includes them.
   - `generated`: build outputs, caches, logs, secrets, local env files; normally exclude.
   - `unclear`: inspect further or ask the user.

3. Choose commit granularity:
   - Default to one commit containing the largest coherent set of related changes.
   - Split commits only when separate commits clearly improve reviewability or maintainability: unrelated features, distinct bug fixes, mechanical refactor plus behavior change, or user-requested partial commits.
   - Do not split just because many files changed if they serve one goal.

4. Verify before committing:
   - Run the most relevant fast checks already used in the task, such as focused tests, lint, typecheck, or project quality scripts.
   - At minimum, run `git diff --check` when practical.
   - If verification fails, diagnose whether the failure is caused by the current changes. Do not commit a known broken state without explicit user approval.
   - If verification cannot run, state why in the final response.

5. Interact with the user when needed:
   - Ask before committing when there are unrelated changes, unclear untracked files, multiple plausible commit groupings, failing checks, sensitive-looking files, or no explicit commit request.
   - If the user explicitly asked to commit and the staged plan is obvious, proceed without another confirmation.
   - For long tasks where the agent decides a checkpoint commit would be prudent, propose the commit and wait for user approval.
   - When asking, provide the planned files, commit scope, proposed message, and any excluded changes.

6. Stage deliberately:
   - Prefer explicit path staging: `git add path1 path2`.
   - Use `git add -p` for mixed files when only part of a file belongs in the commit.
   - Avoid `git add -A` unless the repository contains only intentional task changes and that has been verified.
   - Re-run `git status --short` and `git diff --staged` after staging.

7. Commit:
   - Write the commit message in English.
   - Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `build:`, `ci:`, `perf:`, or another standard type that fits the staged change.
   - Prefer one concise subject line, for example `docs: add safe git commit workflow`.
   - For broad or complex changes, add a blank line after the subject and use unordered list bullets for concrete details; keep list items contiguous with no blank lines between bullets.
   - Put all body bullets in one body argument. Do not pass one `-m` per bullet, because Git renders each `-m` argument as a separate paragraph with a blank line between them.
   - Keep the subject focused on the committed outcome, not the process.
   - Run `git commit -m "type: subject"` for simple commits, or `git commit -m "type: subject" -m $'- Bullet one\n- Bullet two\n- Bullet three'` for complex commits.
   - After complex commits, verify the rendered message with `git log -1 --pretty=%B` if practical.
   - If hooks modify files or the commit fails, inspect the new state before retrying.

8. Report:
   - Provide commit hash, commit message, verification performed, and any changes intentionally left uncommitted.
   - Say explicitly that no push was performed.

## Interaction Templates

When approval is required:

```text
I can create one local commit with:
- Scope: <short scope>
- Files: <intentional files>
- Message: <proposed message>

I will leave these uncommitted:
- <excluded files or "none">

Checks: <checks already run or planned>

Confirm and I will commit locally. I will not push or amend.
```

When declining to commit immediately:

```text
I am not committing yet because <specific risk>. The safe next step is <inspection, test, or user choice>.
```

## Common Mistakes

- Assuming every dirty file is part of the task. Inspect first.
- Making many tiny commits for one coherent change. Prefer one larger, meaningful commit.
- Forgetting staged changes already present before the agent started. Review `git diff --staged`.
- Committing because tests are inconvenient. Either verify, explain why verification was not possible, or ask.
- Using history-rewriting commands as cleanup. This skill creates ordinary local commits only.

## Commit Message Format

Use this shape for simple commits:

```text
type: concise English subject
```

Use this shape for complex commits:

```text
type: concise English subject

- Add concrete detail about one meaningful part of the change
- Update another meaningful part of the change
- Preserve any important compatibility, migration, or verification note
```

Keep exactly one blank line between the subject and the body list. Do not insert blank lines between bullets in the same list.

Use this command shape for complex commits so Git renders the bullets as one contiguous list:

```bash
git commit -m "type: concise English subject" -m $'- Add concrete detail about one meaningful part of the change\n- Update another meaningful part of the change\n- Preserve any important compatibility, migration, or verification note'
```

Do not write complex commit bodies like this:

```bash
git commit -m "type: concise English subject" \
  -m "- Add concrete detail about one meaningful part of the change" \
  -m "- Update another meaningful part of the change" \
  -m "- Preserve any important compatibility, migration, or verification note"
```

That command creates blank lines between every bullet because Git treats each body `-m` as a separate paragraph.

Choose the type by primary intent:

- `feat`: user-visible feature or capability
- `fix`: bug fix
- `docs`: documentation or skill guidance
- `refactor`: structure change without intended behavior change
- `test`: tests only or test infrastructure
- `chore`: maintenance that does not affect runtime behavior
- `build` or `ci`: build system or automation
- `perf`: performance improvement
