#!/usr/bin/env python3
"""Lightweight payload guardrail checker for OmniFocus MCP write calls.

Usage:
  uv run python scripts/payload_lint.py --tool edit_item --input payload.json
  uv run python scripts/payload_lint.py --tool batch_add_items --input payload.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _err(errors: list[str], message: str) -> None:
    errors.append(message)


def _validate_edit_item(payload: Any, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(payload, dict):
        _err(errors, "payload must be an object")
        return
    if payload.get("itemType") not in {"task", "project"}:
        _err(errors, "itemType must be 'task' or 'project'")

    item_id = payload.get("id")
    name = payload.get("name")
    if not item_id and not name:
        _err(errors, "edit_item should include id (preferred) or name")
    if name and not item_id:
        warnings.append("name-only mutation is ambiguous; prefer id")

    status = payload.get("newStatus")
    if status == "completed" and not item_id:
        _err(errors, "complete action requires id")


def _validate_remove_item(payload: Any, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(payload, dict):
        _err(errors, "payload must be an object")
        return
    if payload.get("itemType") not in {"task", "project"}:
        _err(errors, "itemType must be 'task' or 'project'")

    item_id = payload.get("id")
    name = payload.get("name")
    if not item_id:
        _err(errors, "remove_item requires id")
    if name and not item_id:
        warnings.append("name-only remove is unsafe; id is mandatory")


def _validate_batch_add_items(payload: Any, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(payload, dict):
        _err(errors, "payload must be an object")
        return
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        _err(errors, "items must be a non-empty list")
        return
    if len(items) > 20:
        warnings.append("batch size > 20; split into smaller batches")

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            _err(errors, f"items[{idx}] must be an object")
            continue
        if item.get("type") not in {"task", "project"}:
            _err(errors, f"items[{idx}].type must be 'task' or 'project'")
        if not item.get("name"):
            _err(errors, f"items[{idx}].name is required")


def _validate_batch_remove_items(payload: Any, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(payload, dict):
        _err(errors, "payload must be an object")
        return
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        _err(errors, "items must be a non-empty list")
        return
    if len(items) > 20:
        warnings.append("batch size > 20; split into smaller batches")

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            _err(errors, f"items[{idx}] must be an object")
            continue
        if item.get("itemType") not in {"task", "project"}:
            _err(errors, f"items[{idx}].itemType must be 'task' or 'project'")
        if not item.get("id"):
            _err(errors, f"items[{idx}].id is required")


def _validate_add_task(payload: Any, errors: list[str], _warnings: list[str]) -> None:
    if not isinstance(payload, dict):
        _err(errors, "payload must be an object")
        return
    if not payload.get("name"):
        _err(errors, "name is required")


def _validate_add_project(payload: Any, errors: list[str], _warnings: list[str]) -> None:
    if not isinstance(payload, dict):
        _err(errors, "payload must be an object")
        return
    if not payload.get("name"):
        _err(errors, "name is required")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate OmniFocus MCP write payloads")
    parser.add_argument(
        "--tool",
        required=True,
        choices=[
            "add_omnifocus_task",
            "add_project",
            "edit_item",
            "remove_item",
            "batch_add_items",
            "batch_remove_items",
        ],
        help="Tool name",
    )
    parser.add_argument("--input", required=True, help="Path to JSON payload file")
    args = parser.parse_args()

    payload = _load_json(Path(args.input))
    errors: list[str] = []
    warnings: list[str] = []

    validators = {
        "add_omnifocus_task": _validate_add_task,
        "add_project": _validate_add_project,
        "edit_item": _validate_edit_item,
        "remove_item": _validate_remove_item,
        "batch_add_items": _validate_batch_add_items,
        "batch_remove_items": _validate_batch_remove_items,
    }
    validators[args.tool](payload, errors, warnings)

    result = {
        "tool": args.tool,
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
