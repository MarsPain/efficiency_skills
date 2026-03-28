#!/usr/bin/env python3
"""
Write reading notes with deterministic path and mode management.

This script enforces chapter/section-scoped note files, non-overwrite defaults,
and index updates under {book-title}-notes/.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path


def sanitize_path_component(name: str) -> str:
    name = name.replace("/", "_").replace("\\", "_").strip()
    name = re.sub(r"[\x00-\x1f\x7f]", "", name)
    return name or "untitled"


def normalize_text(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")


def now_iso_local() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def now_stamp() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")


def scope_to_slug(scope: str) -> str | None:
    s = scope.strip()
    if not s:
        return None

    m = re.search(r"第\s*([0-9]{1,4})\s*章", s)
    if m:
        return f"chapter-{int(m.group(1)):02d}"
    m = re.search(r"\bchapter\s*([0-9]{1,4})\b", s, flags=re.IGNORECASE)
    if m:
        return f"chapter-{int(m.group(1)):02d}"

    m = re.search(r"第\s*([0-9]{1,4})\s*节", s)
    if m:
        return f"section-{int(m.group(1)):02d}"
    m = re.search(r"\bsection\s*([0-9]{1,4})\b", s, flags=re.IGNORECASE)
    if m:
        return f"section-{int(m.group(1)):02d}"

    slug = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return slug or None


def ensure_unique_new_path(path: Path, stamp: str) -> Path:
    if not path.exists():
        return path
    parent = path.parent
    stem = path.stem
    suffix = path.suffix
    candidate = parent / f"{stem}-{stamp}{suffix}"
    if not candidate.exists():
        return candidate
    for i in range(2, 10000):
        fallback = parent / f"{stem}-{stamp}-{i}{suffix}"
        if not fallback.exists():
            return fallback
    raise RuntimeError(f"failed to allocate unique path under: {parent}")


def resolve_notes_dir(args: argparse.Namespace) -> Path:
    if args.notes_dir:
        return Path(args.notes_dir).expanduser()
    if not args.book_title:
        raise ValueError("provide --notes-dir or --book-title")
    base_dir = Path(args.cwd).expanduser() if args.cwd else Path.cwd()
    return base_dir / f"{sanitize_path_component(args.book_title)}-notes"


def resolve_target_path(notes_dir: Path, scope: str, output_file: str | None, stamp: str) -> Path:
    if output_file:
        p = Path(output_file).expanduser()
        if not p.is_absolute():
            p = notes_dir / p
        return p

    slug = scope_to_slug(scope) or f"section-{stamp}"
    return notes_dir / "notes" / f"{slug}.md"


def read_content(args: argparse.Namespace) -> str:
    if args.content is not None:
        return normalize_text(args.content)
    if args.content_file:
        return normalize_text(Path(args.content_file).expanduser().read_text("utf-8"))
    if args.stdin:
        return normalize_text(sys.stdin.read())
    raise ValueError("provide one of --content, --content-file, or --stdin")


def ensure_file_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_text(text, "utf-8")


def append_with_block(path: Path, content: str, timestamp_iso: str) -> str:
    content = content.strip()
    if not path.exists():
        ensure_file_text(path, content + "\n")
        return "created"

    old = path.read_text("utf-8", errors="replace").rstrip()
    block = (
        f"{old}\n\n---\n\n"
        f"#### 更新于 {timestamp_iso}\n\n"
        f"{content}\n"
    )
    ensure_file_text(path, block)
    return "appended"


def relative_to_notes_dir(path: Path, notes_dir: Path) -> str:
    try:
        return str(path.resolve().relative_to(notes_dir.resolve()))
    except Exception:
        return str(path.resolve())


def esc_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "<br>")


def update_index(
    notes_dir: Path,
    scope: str,
    note_path: Path,
    mode: str,
    action: str,
    timestamp_iso: str,
    source: str,
    source_sha256: str,
    content_sha256: str,
) -> Path:
    index_path = notes_dir / "index.md"
    rel_note = relative_to_notes_dir(note_path, notes_dir)
    entry_key_src = "\n".join([scope, rel_note, mode, source, source_sha256, content_sha256])
    entry_key = hashlib.sha256(entry_key_src.encode("utf-8")).hexdigest()[:12]
    entry = (
        f"| {esc_cell(timestamp_iso)} | {esc_cell(scope)} | "
        f"`{esc_cell(rel_note)}` | `{esc_cell(mode)}` | `{esc_cell(action)}` | "
        f"`{esc_cell(source)}` | `{esc_cell(source_sha256)}` | `{esc_cell(content_sha256)}` | `{entry_key}` |"
    )

    if index_path.exists():
        body = index_path.read_text("utf-8", errors="replace")
        if f"`{entry_key}` |" in body:
            return index_path
        if not body.endswith("\n"):
            body += "\n"
        body += entry + "\n"
    else:
        body = (
            "#### Notes Index\n\n"
            "| Time | Scope | File | Mode | Action | Source | SourceSHA256 | ContentSHA256 | EntryKey |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
            f"{entry}\n"
        )
    ensure_file_text(index_path, body)
    return index_path


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", required=True, help="Reading scope (chapter/section/topic).")
    ap.add_argument("--notes-dir", help="Target notes directory.")
    ap.add_argument("--book-title", help="Book title used to build {book-title}-notes when --notes-dir is omitted.")
    ap.add_argument("--cwd", help="Base directory when --book-title is used.")
    ap.add_argument("--output-file", help="Output note file (absolute or relative to notes dir).")
    ap.add_argument("--mode", choices=["new", "append", "overwrite"], default="new")
    ap.add_argument("--allow-overwrite", action="store_true", help="Required when --mode overwrite.")
    ap.add_argument("--source", default="", help="Optional source path/label (for index tracking).")
    ap.add_argument("--source-sha256", default="", help="Optional source SHA256 (for index tracking).")
    ap.add_argument("--content", help="Inline note content.")
    ap.add_argument("--content-file", help="Path to a UTF-8 Markdown content file.")
    ap.add_argument("--stdin", action="store_true", help="Read content from stdin.")
    args = ap.parse_args(argv)

    try:
        notes_dir = resolve_notes_dir(args)
        notes_dir.mkdir(parents=True, exist_ok=True)
        content = read_content(args)
    except Exception as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2

    stamp = now_stamp()
    ts_iso = now_iso_local()
    target = resolve_target_path(notes_dir, args.scope, args.output_file, stamp=stamp)
    target.parent.mkdir(parents=True, exist_ok=True)

    action = "created"
    if args.mode == "new":
        target = ensure_unique_new_path(target, stamp=stamp)
        ensure_file_text(target, content)
        action = "created"
    elif args.mode == "append":
        action = append_with_block(target, content, ts_iso)
    else:
        if not args.allow_overwrite:
            sys.stderr.write("error: overwrite mode requires --allow-overwrite\n")
            return 2
        ensure_file_text(target, content)
        action = "overwritten"

    content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    index_path = update_index(
        notes_dir=notes_dir,
        scope=args.scope,
        note_path=target,
        mode=args.mode,
        action=action,
        timestamp_iso=ts_iso,
        source=args.source.strip(),
        source_sha256=args.source_sha256.strip(),
        content_sha256=content_sha256,
    )

    sys.stdout.write(f"notes_dir={notes_dir.resolve()}\n")
    sys.stdout.write(f"note_path={target.resolve()}\n")
    sys.stdout.write(f"index_path={index_path.resolve()}\n")
    sys.stdout.write(f"mode={args.mode}\n")
    sys.stdout.write(f"action={action}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
