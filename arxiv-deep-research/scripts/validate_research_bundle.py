#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SEARCH_LOG_RE = re.compile(
    r'^- \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\] query: ".+" \| results: \d+ \| filter: .+ \| rationale: .+$'
)
ARXIV_URL_RE = re.compile(r"https?://arxiv\.org/abs/([A-Za-z0-9._/-]+)")
BIB_KEY_RE = re.compile(r"@article\{([^,]+),")
BIB_EPRINT_RE = re.compile(r"^\s*eprint\s*=\s*\{([^}]+)\},?\s*$", re.MULTILINE)
PANDOC_CITE_RE = re.compile(r"(?<![\w/])@([A-Za-z0-9:_-]+)")


def _strip_fenced_code_blocks(text: str) -> str:
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_arxiv_id(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^arxiv:", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^https?://arxiv\.org/abs/", "", value)
    value = re.sub(r"^https?://arxiv\.org/pdf/", "", value)
    value = re.sub(r"\.pdf$", "", value)
    return value


def _require_file(path: Path, label: str, errors: list[str]) -> bool:
    if not path.exists():
        errors.append(f"Missing required file: {label} ({path})")
        return False
    if path.is_file() and path.stat().st_size == 0:
        errors.append(f"Required file is empty: {label} ({path})")
        return False
    return True


def _validate_papers_json(path: Path, errors: list[str]) -> tuple[set[str], list[dict]]:
    if not _require_file(path, "papers.json", errors):
        return set(), []
    data = _load_json(path)
    if not isinstance(data, list):
        errors.append("papers.json must contain a JSON array.")
        return set(), []

    ids: set[str] = set()
    papers: list[dict] = []
    for i, paper in enumerate(data):
        if not isinstance(paper, dict):
            errors.append(f"papers.json item {i} is not an object.")
            continue
        arxiv_id = _normalize_arxiv_id(str(paper.get("arxiv_id", "")))
        title = str(paper.get("title", "")).strip()
        if not arxiv_id:
            errors.append(f"papers.json item {i} is missing arxiv_id.")
        if not title:
            errors.append(f"papers.json item {i} is missing title.")
        if arxiv_id:
            ids.add(arxiv_id)
        papers.append(paper)
    return ids, papers


def _validate_bib(path: Path, paper_ids: set[str], errors: list[str]) -> set[str]:
    if not _require_file(path, "papers.bib", errors):
        return set()
    text = path.read_text(encoding="utf-8")
    keys = set(BIB_KEY_RE.findall(text))
    eprints = {_normalize_arxiv_id(v) for v in BIB_EPRINT_RE.findall(text)}
    if not keys:
        errors.append("papers.bib does not contain any BibTeX entries.")
    if paper_ids and eprints != paper_ids:
        missing = sorted(paper_ids - eprints)
        extra = sorted(eprints - paper_ids)
        if missing:
            errors.append("papers.bib is missing eprint IDs from papers.json: " + ", ".join(missing[:10]))
        if extra:
            errors.append("papers.bib contains eprint IDs not found in papers.json: " + ", ".join(extra[:10]))
    return keys


def _validate_markdown_export(path: Path, label: str, errors: list[str]) -> None:
    if not _require_file(path, label, errors):
        return
    text = path.read_text(encoding="utf-8")
    if "|" not in text:
        errors.append(f"{label} does not look like a markdown table export.")


def _validate_search_log(path: Path, errors: list[str]) -> None:
    if not _require_file(path, "search_log.md", errors):
        return
    lines = [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    matched = 0
    for line in lines:
        if SEARCH_LOG_RE.match(line):
            matched += 1
            continue
        if line.startswith("#"):
            continue
        errors.append("search_log.md contains a line that does not match the required format: " + line)
    if matched == 0:
        errors.append("search_log.md does not contain any valid log entries.")


def _validate_report(path: Path, paper_ids: set[str], bib_keys: set[str], errors: list[str]) -> None:
    if not _require_file(path, "report.md", errors):
        return
    text = _strip_fenced_code_blocks(path.read_text(encoding="utf-8"))

    cited_ids = {_normalize_arxiv_id(m) for m in ARXIV_URL_RE.findall(text)}
    cited_keys = set(PANDOC_CITE_RE.findall(text))

    unknown_ids = sorted(cited_ids - paper_ids)
    if unknown_ids:
        errors.append("report.md cites arXiv IDs not present in papers.json: " + ", ".join(unknown_ids[:10]))

    unknown_keys = sorted(cited_keys - bib_keys)
    if unknown_keys:
        errors.append("report.md cites BibTeX keys not present in papers.bib: " + ", ".join(unknown_keys[:10]))

    if not cited_ids and not cited_keys:
        errors.append("report.md does not contain any detectable citations (@bibkey or arXiv abs links).")


def _validate_export(path: Path, errors: list[str]) -> None:
    if not _require_file(path, "research-export.md", errors):
        return
    text = path.read_text(encoding="utf-8")
    required_headings = ["## Export summary", "## Paper table"]
    for heading in required_headings:
        if heading not in text:
            errors.append(f"research-export.md is missing required heading: {heading}")


def _validate_insights(path: Path, errors: list[str]) -> None:
    if not _require_file(path, "insights.json", errors):
        return
    data = _load_json(path)
    if not isinstance(data, dict):
        errors.append("insights.json must contain a JSON object.")
        return

    required_top_level = ["meta", "taxonomy", "trends", "gaps", "open_questions", "bias_notes"]
    for key in required_top_level:
        if key not in data:
            errors.append(f"insights.json is missing top-level field: {key}")

    meta = data.get("meta")
    if isinstance(meta, dict):
        for key in ["topic", "generated_at", "time_window", "search_queries", "total_papers_fetched", "core_set_size"]:
            if key not in meta:
                errors.append(f"insights.json meta is missing field: {key}")
    else:
        errors.append("insights.json meta must be an object.")

    for key in ["taxonomy", "trends", "gaps", "open_questions"]:
        if key in data and not isinstance(data[key], list):
            errors.append(f"insights.json field '{key}' must be an array.")

    if "bias_notes" in data and not isinstance(data["bias_notes"], dict):
        errors.append("insights.json field 'bias_notes' must be an object.")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate a research bundle produced by arxiv-deep-research.")
    parser.add_argument("--bundle-dir", required=True, help="Directory containing papers/report/search artifacts")
    parser.add_argument("--require-search-log", action="store_true", help="Fail if search_log.md is missing or invalid")
    parser.add_argument("--require-report", action="store_true", help="Fail if report.md is missing or invalid")
    parser.add_argument("--require-export", action="store_true", help="Fail if research-export.md is missing or incomplete")
    parser.add_argument("--require-insights", action="store_true", help="Fail if insights.json is missing or invalid")
    args = parser.parse_args(argv)

    bundle_dir = Path(args.bundle_dir)
    errors: list[str] = []

    paper_ids, _papers = _validate_papers_json(bundle_dir / "papers.json", errors)
    bib_keys = _validate_bib(bundle_dir / "papers.bib", paper_ids, errors)
    _validate_markdown_export(bundle_dir / "papers.md", "papers.md", errors)

    if args.require_search_log or (bundle_dir / "search_log.md").exists():
        _validate_search_log(bundle_dir / "search_log.md", errors)

    if args.require_report or (bundle_dir / "report.md").exists():
        _validate_report(bundle_dir / "report.md", paper_ids, bib_keys, errors)

    if args.require_export or (bundle_dir / "research-export.md").exists():
        _validate_export(bundle_dir / "research-export.md", errors)

    if args.require_insights or (bundle_dir / "insights.json").exists():
        _validate_insights(bundle_dir / "insights.json", errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Research bundle is valid!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
