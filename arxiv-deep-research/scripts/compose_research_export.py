#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


SECTION_FILES = [
    ("Survey report", "report.md"),
    ("Paper table", "papers.md"),
    ("Evidence table", "evidence-table.md"),
    ("Search log", "search_log.md"),
]


def _strip_bibtex_sections(text: str) -> str:
    lines = text.splitlines()
    kept: list[str] = []
    skipping = False

    for line in lines:
        if line.strip().lower() == "## bibtex":
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            kept.append(line)

    return "\n".join(kept).strip()


def _read_optional(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return text or None


def _load_papers(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return [item for item in data if isinstance(item, dict)]


def _paper_summary(papers: list[dict]) -> list[str]:
    if not papers:
        return ["- Papers: not available"]

    dates = sorted((str(p.get("published", ""))[:10] for p in papers if p.get("published")))
    categories: dict[str, int] = {}
    for paper in papers:
        cat = str(paper.get("primary_category", "")).strip() or "unknown"
        categories[cat] = categories.get(cat, 0) + 1

    top_categories = sorted(categories.items(), key=lambda item: (-item[1], item[0]))[:8]
    lines = [f"- Papers: {len(papers)}"]
    if dates:
        lines.append(f"- Published range: {dates[0]} to {dates[-1]}")
    if top_categories:
        joined = ", ".join(f"{cat} ({count})" for cat, count in top_categories)
        lines.append(f"- Top primary categories: {joined}")
    return lines


def _append_markdown_section(lines: list[str], title: str, filename: str, text: str) -> None:
    lines.append(f"## {title}")
    lines.append("")
    lines.append(f"_Source: `{filename}`_")
    lines.append("")
    lines.append(text)
    lines.append("")


def _append_code_section(lines: list[str], title: str, filename: str, text: str, language: str) -> None:
    lines.append(f"## {title}")
    lines.append("")
    lines.append(f"_Source: `{filename}`_")
    lines.append("")
    lines.append(f"```{language}")
    lines.append(text)
    lines.append("```")
    lines.append("")


def compose(bundle_dir: Path, topic: str, include_bibtex: bool, include_raw_json: bool) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    papers = _load_papers(bundle_dir / "papers.json")

    lines: list[str] = []
    lines.append(f"# {topic}")
    lines.append("")
    lines.append(f"_Copy-ready research export. Generated: {generated_at}._")
    lines.append("")
    lines.append("## Export summary")
    lines.append("")
    lines.extend(_paper_summary(papers))
    lines.append("")
    lines.append("## How to use this file")
    lines.append("")
    lines.append("- Paste this Markdown into Notion, Craft, Obsidian, or another notes app.")
    lines.append("- Treat the report as the main narrative and the later sections as audit trail / reusable evidence.")
    lines.append("- Keep `papers.json` and `papers.bib` in the research bundle for incremental updates and citation tooling.")
    lines.append("")

    for title, filename in SECTION_FILES:
        text = _read_optional(bundle_dir / filename)
        if text:
            if filename == "report.md":
                text = _strip_bibtex_sections(text)
            _append_markdown_section(lines, title, filename, text)

    bib = _read_optional(bundle_dir / "papers.bib")
    if include_bibtex and bib:
        _append_code_section(lines, "BibTeX", "papers.bib", bib, "bibtex")

    insights = _read_optional(bundle_dir / "insights.json")
    if insights:
        _append_code_section(lines, "Machine-readable insights", "insights.json", insights, "json")

    if include_raw_json:
        papers_json = _read_optional(bundle_dir / "papers.json")
        if papers_json:
            _append_code_section(lines, "Raw paper metadata", "papers.json", papers_json, "json")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Compose a copy-ready Markdown export from an arxiv-deep-research bundle.")
    parser.add_argument("--bundle-dir", required=True, help="Directory containing report.md, papers.*, and search artifacts")
    parser.add_argument("--topic", required=True, help="Title to use for the export")
    parser.add_argument("--out", help="Output Markdown path. Defaults to <bundle-dir>/research-export.md")
    parser.add_argument("--include-bibtex", action="store_true", help="Append papers.bib as a fenced BibTeX section")
    parser.add_argument("--include-raw-json", action="store_true", help="Append papers.json as a fenced JSON section")
    args = parser.parse_args(argv)

    bundle_dir = Path(args.bundle_dir)
    out = Path(args.out) if args.out else bundle_dir / "research-export.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(compose(bundle_dir, args.topic, args.include_bibtex, args.include_raw_json), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
