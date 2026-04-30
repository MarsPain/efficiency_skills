#!/usr/bin/env python3
"""Normalize paper inputs into lightweight paper objects.

This script performs deterministic parsing only. It does not fetch metadata or
search the web; unresolved titles and PDFs should be resolved by the agent using
source-resolution rules.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

ARXIV_ID_RE = re.compile(r"(?P<id>(?:\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?)", re.IGNORECASE)
DOI_RE = re.compile(r"(?P<doi>10\.\d{4,9}/[^\s<>\"']+)", re.IGNORECASE)


def blank_object(source: str) -> dict[str, Any]:
    return {
        "title": None,
        "authors": [],
        "year": None,
        "venue_or_source": None,
        "doi": None,
        "arxiv_id": None,
        "urls": {"abstract": None, "pdf": None, "publisher": None, "source": None},
        "input_type": "unknown",
        "evidence_coverage": "unknown",
        "resolution_confidence": "low",
        "source_input": source,
        "ambiguities": [],
        "notes": [],
    }


def clean_doi(raw: str) -> str:
    return raw.rstrip(".,);]")


def normalize_arxiv_id(raw_id: str) -> str:
    return raw_id.rstrip(".pdf")


def parse_arxiv(source: str, obj: dict[str, Any]) -> bool:
    parsed = urlparse(source)
    haystack = unquote(parsed.path if parsed.netloc else source)
    if "arxiv.org" not in parsed.netloc and not haystack.lower().startswith("arxiv:"):
        if not re.fullmatch(ARXIV_ID_RE, source.strip()):
            return False

    match = ARXIV_ID_RE.search(haystack)
    if not match:
        return False

    arxiv_id = normalize_arxiv_id(match.group("id"))
    obj["arxiv_id"] = arxiv_id
    obj["urls"]["abstract"] = f"https://arxiv.org/abs/{arxiv_id}"
    obj["urls"]["pdf"] = f"https://arxiv.org/pdf/{arxiv_id}"
    obj["urls"]["source"] = source if parsed.scheme else obj["urls"]["abstract"]
    obj["input_type"] = "arxiv_url" if parsed.scheme else "arxiv_id"
    obj["venue_or_source"] = "arXiv"
    obj["evidence_coverage"] = "full_text_pdf" if "/pdf/" in haystack or source.lower().endswith(".pdf") else "abstract_only"
    obj["resolution_confidence"] = "high"
    obj["notes"].append("Parsed arXiv identifier deterministically; fetch metadata before detailed analysis.")
    return True


def parse_doi(source: str, obj: dict[str, Any]) -> bool:
    match = DOI_RE.search(source)
    if not match:
        return False

    doi = clean_doi(match.group("doi"))
    obj["doi"] = doi
    obj["urls"]["publisher"] = f"https://doi.org/{doi}"
    obj["urls"]["source"] = source if source.startswith(("http://", "https://")) else obj["urls"]["publisher"]
    obj["input_type"] = "doi_url" if source.startswith(("http://", "https://")) else "doi"
    obj["evidence_coverage"] = "metadata_only"
    obj["resolution_confidence"] = "medium"
    obj["notes"].append("Parsed DOI deterministically; resolve publisher metadata before analysis.")
    return True


def parse_pdf(source: str, obj: dict[str, Any]) -> bool:
    parsed = urlparse(source)
    lower = source.lower()
    if parsed.scheme in {"http", "https"} and lower.split("?")[0].endswith(".pdf"):
        obj["urls"]["pdf"] = source
        obj["urls"]["source"] = source
        obj["input_type"] = "pdf_url"
        obj["evidence_coverage"] = "full_text_pdf"
        obj["resolution_confidence"] = "medium"
        obj["ambiguities"].append("Direct PDF URL needs title/authors extraction or source page resolution.")
        return True

    path = Path(source).expanduser()
    if lower.endswith(".pdf"):
        obj["input_type"] = "local_pdf"
        obj["urls"]["source"] = str(path)
        obj["evidence_coverage"] = "full_text_pdf" if path.exists() else "unknown"
        obj["resolution_confidence"] = "medium" if path.exists() else "low"
        if not path.exists():
            obj["ambiguities"].append("Local PDF path does not exist in the current environment.")
        else:
            obj["notes"].append("Extract text with extract_pdf_text.py before detailed analysis.")
        return True

    return False


def parse_title(source: str, obj: dict[str, Any]) -> None:
    obj["title"] = source.strip()
    obj["input_type"] = "title"
    obj["evidence_coverage"] = "metadata_only"
    obj["resolution_confidence"] = "low"
    obj["ambiguities"].append("Title requires search and source confirmation before analysis.")


def normalize_one(source: str) -> dict[str, Any]:
    source = source.strip()
    obj = blank_object(source)
    if not source:
        obj["notes"].append("Empty input ignored by caller.")
        return obj

    if parse_arxiv(source, obj):
        return obj
    if parse_doi(source, obj):
        return obj
    if parse_pdf(source, obj):
        return obj

    parse_title(source, obj)
    return obj


def collect_inputs(args: argparse.Namespace) -> list[str]:
    items = list(args.inputs)
    for input_file in args.input_file or []:
        with open(input_file, "r", encoding="utf-8") as handle:
            items.extend(line.strip() for line in handle if line.strip())
    return [item for item in items if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize arXiv, DOI, PDF, and title inputs into paper objects.")
    parser.add_argument("inputs", nargs="*", help="Paper inputs: URL, DOI, arXiv ID, local PDF path, or title.")
    parser.add_argument("--input-file", action="append", help="Read one paper input per non-empty line from a file.")
    parser.add_argument("--output", "-o", help="Write JSON output to this file instead of stdout.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")
    args = parser.parse_args()

    items = collect_inputs(args)
    result = {"papers": [normalize_one(item) for item in items]}
    text = json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2)

    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
