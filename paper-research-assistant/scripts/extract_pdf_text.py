#!/usr/bin/env python3
"""Extract PDF text with page markers for paper analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract text from a PDF into Markdown with page markers.")
    parser.add_argument("pdf", help="Path to a local PDF file.")
    parser.add_argument("--output", "-o", help="Output Markdown/text path. Defaults to stdout.")
    parser.add_argument("--start-page", type=int, default=1, help="1-based first page to extract. Default: 1.")
    parser.add_argument("--end-page", type=int, help="1-based final page to extract. Default: last page.")
    parser.add_argument("--max-pages", type=int, help="Maximum number of pages to extract after start-page.")
    return parser.parse_args()


def fail(message: str, code: int = 1) -> int:
    print(message, file=sys.stderr)
    return code


def main() -> int:
    args = parse_args()
    pdf_path = Path(args.pdf).expanduser()
    if not pdf_path.exists():
        return fail(f"PDF not found: {pdf_path}")
    if not pdf_path.is_file():
        return fail(f"Not a file: {pdf_path}")
    if args.start_page < 1:
        return fail("--start-page must be >= 1")
    if args.end_page is not None and args.end_page < args.start_page:
        return fail("--end-page must be >= --start-page")
    if args.max_pages is not None and args.max_pages < 1:
        return fail("--max-pages must be >= 1")

    try:
        from pypdf import PdfReader
    except ModuleNotFoundError:
        return fail(
            "Missing dependency: pypdf. Run with `uv run --with pypdf python "
            "/Users/H/.codex/skills/paper-research-assistant/scripts/extract_pdf_text.py <paper.pdf>`.",
            code=2,
        )

    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)
    start_index = args.start_page - 1
    end_index = args.end_page if args.end_page is not None else page_count
    end_index = min(end_index, page_count)
    if args.max_pages is not None:
        end_index = min(end_index, start_index + args.max_pages)
    if start_index >= page_count:
        return fail(f"--start-page exceeds PDF length ({page_count} pages)")

    chunks = [
        "# Extracted PDF Text",
        "",
        f"Source: {pdf_path}",
        f"Pages: {start_index + 1}-{end_index} of {page_count}",
        "",
    ]

    for index in range(start_index, end_index):
        page = reader.pages[index]
        text = page.extract_text() or ""
        chunks.extend([f"## Page {index + 1}", "", text.strip() or "[No extractable text]", ""])

    output = "\n".join(chunks).rstrip() + "\n"
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
