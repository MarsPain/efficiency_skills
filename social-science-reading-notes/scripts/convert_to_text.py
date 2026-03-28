#!/usr/bin/env python3
"""
Convert reading resources into model-friendly UTF-8 text, with caching.

Supported (no extra deps):
- .txt/.md: copied as-is (normalized to UTF-8)
- .html/.htm: stripped to text
- .epub: extracts html/xhtml files from the zip and strips to text

Supported via external tools:
- .pdf: requires `pdftotext` (Poppler)

Outputs live under {notes_dir}/_sources and optional {notes_dir}/_chunks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET
from zipfile import ZipFile


MANIFEST_NAME = "_manifest.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sanitize_path_component(name: str) -> str:
    # Keep Unicode (book titles), but remove path separators and control chars.
    name = name.replace("/", "_").replace("\\", "_").strip()
    name = re.sub(r"[\x00-\x1f\x7f]", "", name)
    return name or "untitled"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(notes_dir: Path) -> dict:
    manifest_path = notes_dir / MANIFEST_NAME
    if not manifest_path.exists():
        return {"version": 2, "items": []}
    try:
        manifest = json.loads(manifest_path.read_text("utf-8"))
        if not isinstance(manifest, dict):
            return {"version": 2, "items": []}
        if not isinstance(manifest.get("items"), list):
            manifest["items"] = []
        return manifest
    except Exception:
        return {"version": 2, "items": []}


def _manifest_key(item: dict) -> tuple[str, str] | None:
    digest = item.get("sha256")
    outputs = item.get("outputs") or {}
    main_txt = outputs.get("main_txt")
    if not isinstance(digest, str) or not digest:
        return None
    if not isinstance(main_txt, str) or not main_txt:
        return None
    return (digest, main_txt)


def compact_manifest(manifest: dict, max_entries: int = 2000) -> dict:
    items = manifest.get("items", [])
    if not isinstance(items, list):
        items = []

    dedup: dict[tuple[str, str], dict] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        key = _manifest_key(item)
        if key is None:
            continue
        prev = dedup.get(key)
        if prev is None:
            dedup[key] = item
            continue
        # Keep the most recent record when duplicates exist.
        if str(item.get("converted_at", "")) >= str(prev.get("converted_at", "")):
            dedup[key] = item

    compact_items = sorted(
        dedup.values(),
        key=lambda it: str(it.get("converted_at", "")),
        reverse=True,
    )
    if max_entries > 0:
        compact_items = compact_items[:max_entries]

    return {"version": 2, "items": compact_items}


def save_manifest(notes_dir: Path, manifest: dict) -> None:
    manifest = compact_manifest(manifest)
    manifest_path = notes_dir / MANIFEST_NAME
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")


def find_cached_item(manifest: dict, digest: str, input_abs: str | None = None) -> dict | None:
    candidates: list[dict] = []
    for it in manifest.get("items", []):
        if it.get("sha256") == digest:
            candidates.append(it)
    if not candidates:
        return None

    # Prefer matching original path when available, then any digest match.
    if input_abs:
        for it in candidates:
            if it.get("input_abs") == input_abs:
                return it
    for it in candidates:
        outputs = it.get("outputs") or {}
        main_txt = outputs.get("main_txt")
        if isinstance(main_txt, str) and main_txt:
            return it
    return None


def ensure_unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    for i in range(2, 10_000):
        candidate = parent / f"{stem}-{i}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"failed to find unique path for: {path}")


class _HtmlToText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[override]
        tag = tag.lower()
        if tag in {"script", "style", "nav"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in {"p", "div", "section", "article", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "hr"}:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        tag = tag.lower()
        if tag in {"script", "style", "nav"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag in {"p", "div", "section", "article", "li"}:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        if self._skip_depth:
            return
        if data:
            self._parts.append(data)

    def get_text(self) -> str:
        text = "".join(self._parts)
        # Normalize whitespace, preserve paragraph breaks.
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip() + "\n"


def strip_html_to_text(html: str) -> str:
    parser = _HtmlToText()
    parser.feed(html)
    parser.close()
    return parser.get_text()


def _epub_fallback_members(zf: ZipFile) -> list[str]:
    members = [m for m in zf.namelist() if m.lower().endswith((".xhtml", ".html", ".htm"))]
    members.sort()
    return members


def _resolve_zip_href(opf_path: str, href: str) -> str:
    href = href.replace("\\", "/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(opf_path), href))


def epub_members_in_reading_order(zf: ZipFile) -> list[str]:
    fallback = _epub_fallback_members(zf)
    if not fallback:
        return []

    normalized_to_actual: dict[str, str] = {}
    for name in zf.namelist():
        normalized_to_actual[name.lstrip("./").lower()] = name

    try:
        container_xml = zf.read("META-INF/container.xml")
        container_root = ET.fromstring(container_xml)
        rootfile = container_root.find(".//{*}rootfile")
        if rootfile is None:
            return fallback
        opf_path = rootfile.attrib.get("full-path", "").strip()
        if not opf_path:
            return fallback
        opf_xml = zf.read(opf_path)
        opf_root = ET.fromstring(opf_xml)
    except Exception:
        return fallback

    manifest_map: dict[str, str] = {}
    for item in opf_root.findall(".//{*}manifest/{*}item"):
        item_id = (item.attrib.get("id") or "").strip()
        href = (item.attrib.get("href") or "").strip()
        if not item_id or not href:
            continue
        resolved = _resolve_zip_href(opf_path, href).lstrip("./")
        manifest_map[item_id] = resolved

    ordered: list[str] = []
    seen: set[str] = set()
    for itemref in opf_root.findall(".//{*}spine/{*}itemref"):
        idref = (itemref.attrib.get("idref") or "").strip()
        if not idref:
            continue
        resolved = manifest_map.get(idref)
        if not resolved:
            continue
        actual = normalized_to_actual.get(resolved.lower())
        if not actual:
            continue
        if not actual.lower().endswith((".xhtml", ".html", ".htm")):
            continue
        if actual in seen:
            continue
        ordered.append(actual)
        seen.add(actual)

    for name in fallback:
        if name not in seen:
            ordered.append(name)
    return ordered


def convert_epub_to_text(epub_path: Path) -> str:
    parts: list[str] = []
    with ZipFile(epub_path, "r") as zf:
        members = epub_members_in_reading_order(zf)
        for name in members:
            try:
                data = zf.read(name)
            except KeyError:
                continue
            # Try utf-8 first; fall back to latin-1 to avoid hard failures.
            try:
                html = data.decode("utf-8")
            except UnicodeDecodeError:
                html = data.decode("latin-1", errors="replace")
            text = strip_html_to_text(html)
            if text.strip():
                parts.append(text)
    return "\n\n".join(parts).strip() + "\n"


def convert_pdf_to_text(pdf_path: Path, out_txt: Path) -> None:
    tool = shutil.which("pdftotext")
    if not tool:
        raise RuntimeError(
            "pdftotext not found. Install Poppler (macOS: `brew install poppler`) "
            "or provide a non-PDF source."
        )
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    # -layout keeps columns/spaces closer to the original layout. -nopgbrk avoids hard page breaks.
    cmd = [tool, "-layout", "-nopgbrk", str(pdf_path), str(out_txt)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"pdftotext failed ({proc.returncode}): {proc.stderr.strip()}")


def normalize_utf8_text(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), "utf-8")


def split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    paragraph = paragraph.strip()
    if not paragraph:
        return []
    if len(paragraph) <= max_chars:
        return [paragraph]

    # Prefer sentence-like boundaries, then fall back to hard splits.
    units = [u.strip() for u in re.split(r"(?<=[。！？!?\.])\s+|\n+", paragraph) if u.strip()]
    if not units:
        units = [paragraph]

    pieces: list[str] = []
    cur = ""
    for unit in units:
        if len(unit) > max_chars:
            if cur:
                pieces.append(cur.strip())
                cur = ""
            for i in range(0, len(unit), max_chars):
                pieces.append(unit[i : i + max_chars].strip())
            continue
        candidate = f"{cur} {unit}".strip() if cur else unit
        if len(candidate) > max_chars and cur:
            pieces.append(cur.strip())
            cur = unit
        else:
            cur = candidate
    if cur:
        pieces.append(cur.strip())
    return [p for p in pieces if p]


def chunk_text(text: str, chunk_chars: int) -> list[str]:
    if chunk_chars <= 0:
        return []
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    paras = re.split(r"\n{2,}", text)
    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for p in paras:
        for segment in split_long_paragraph(p, chunk_chars):
            piece = segment + "\n\n"
            if cur_len + len(piece) > chunk_chars and cur:
                chunks.append("".join(cur).strip() + "\n")
                cur = []
                cur_len = 0
            cur.append(piece)
            cur_len += len(piece)
    if cur:
        chunks.append("".join(cur).strip() + "\n")
    return chunks


@dataclass(frozen=True)
class ConvertResult:
    input_path: Path
    sha256: str
    main_txt: Path
    chunk_dir: Path | None


def convert_one(input_path: Path, notes_dir: Path, chunk_chars: int, force: bool) -> ConvertResult:
    input_abs = str(input_path.resolve())
    digest = sha256_file(input_path)

    sources_dir = notes_dir / "_sources"
    chunks_root = notes_dir / "_chunks"
    sources_dir.mkdir(parents=True, exist_ok=True)
    chunks_root.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(notes_dir)
    cached = None if force else find_cached_item(manifest, digest, input_abs=input_abs)
    if cached:
        main_txt = Path(cached["outputs"]["main_txt"])
        if main_txt.exists():
            chunk_dir = Path(cached["outputs"]["chunk_dir"]) if cached["outputs"].get("chunk_dir") else None
            return ConvertResult(input_path=input_path, sha256=digest, main_txt=main_txt, chunk_dir=chunk_dir)

    base = sanitize_path_component(input_path.stem)
    out_txt = ensure_unique_path(sources_dir / f"{base}.txt")

    ext = input_path.suffix.lower()
    if ext in {".txt", ".md"}:
        write_text(out_txt, normalize_utf8_text(input_path.read_bytes()))
    elif ext in {".html", ".htm"}:
        html = normalize_utf8_text(input_path.read_bytes())
        write_text(out_txt, strip_html_to_text(html))
    elif ext == ".epub":
        write_text(out_txt, convert_epub_to_text(input_path))
    elif ext == ".pdf":
        convert_pdf_to_text(input_path, out_txt)
    else:
        raise RuntimeError(f"unsupported input type: {input_path.name}")

    text = out_txt.read_text("utf-8", errors="replace")
    if ext == ".pdf" and len(text.strip()) < 1200:
        sys.stderr.write(
            f"warning: extracted text from PDF seems very short ({len(text.strip())} chars). "
            "If this is a scanned PDF, run OCR first (e.g. `ocrmypdf`) then re-convert.\n"
        )

    chunk_dir: Path | None = None
    chunks = chunk_text(text, chunk_chars)
    if chunks:
        # Use the actual output stem so multiple inputs with the same stem don't collide.
        chunk_dir = chunks_root / out_txt.stem
        chunk_dir.mkdir(parents=True, exist_ok=True)
        index = {"chunk_chars": chunk_chars, "chunks": []}
        for i, chunk in enumerate(chunks, start=1):
            p = chunk_dir / f"chunk-{i:04d}.txt"
            write_text(p, chunk)
            index["chunks"].append({"path": str(p), "chars": len(chunk)})
        write_text(chunk_dir / "index.json", json.dumps(index, ensure_ascii=False, indent=2) + "\n")

    manifest.setdefault("items", []).append(
        {
            "converted_at": _now_iso(),
            "input_abs": input_abs,
            "sha256": digest,
            "outputs": {"main_txt": str(out_txt), "chunk_dir": str(chunk_dir) if chunk_dir else None},
        }
    )
    save_manifest(notes_dir, manifest)

    return ConvertResult(input_path=input_path, sha256=digest, main_txt=out_txt, chunk_dir=chunk_dir)


def iter_inputs(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        yield input_path
        return
    for p in sorted(input_path.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".pdf", ".epub", ".txt", ".md", ".html", ".htm"}:
            yield p


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to a file or directory containing reading resources.")
    ap.add_argument(
        "--notes-dir",
        help="Target notes directory. If omitted, uses {book-title}-notes under --cwd or current directory.",
    )
    ap.add_argument("--book-title", help="Book title used to build {book-title}-notes when --notes-dir is omitted.")
    ap.add_argument("--cwd", help="Base directory for {book-title}-notes when --notes-dir is omitted.")
    ap.add_argument("--chunk-chars", type=int, default=25000, help="Chunk size in characters; 0 disables chunking.")
    ap.add_argument("--force", action="store_true", help="Re-convert even if already cached.")
    args = ap.parse_args(argv)

    input_path = Path(args.input).expanduser()
    if not input_path.exists():
        sys.stderr.write(f"error: input not found: {input_path}\n")
        return 2

    notes_dir: Path
    if args.notes_dir:
        notes_dir = Path(args.notes_dir).expanduser()
    else:
        if not args.book_title:
            sys.stderr.write("error: provide --notes-dir or --book-title\n")
            return 2
        base_dir = Path(args.cwd).expanduser() if args.cwd else Path.cwd()
        notes_dir = base_dir / f"{sanitize_path_component(args.book_title)}-notes"

    notes_dir.mkdir(parents=True, exist_ok=True)

    results: list[ConvertResult] = []
    for p in iter_inputs(input_path):
        results.append(convert_one(p, notes_dir=notes_dir, chunk_chars=args.chunk_chars, force=args.force))

    if not results:
        sys.stderr.write("error: no supported files found\n")
        return 2

    sys.stdout.write(f"notes_dir={notes_dir.resolve()}\n")
    for r in results:
        sys.stdout.write(f"- input={r.input_path.resolve()}\n")
        sys.stdout.write(f"  sha256={r.sha256}\n")
        sys.stdout.write(f"  main_txt={r.main_txt}\n")
        if r.chunk_dir:
            sys.stdout.write(f"  chunk_dir={r.chunk_dir}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
