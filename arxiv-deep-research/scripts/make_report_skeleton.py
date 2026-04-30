#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _load_papers(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _render(topic: str, papers: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines: list[str] = []
    lines.append(f"# {topic} — arXiv-centered literature review")
    lines.append("")
    lines.append(f"_Generated: {now} (UTC)_")
    lines.append("")
    lines.append("## TL;DR")
    lines.append("")
    lines.append("- [Fill in: 5–10 bullet insights grounded in citations]")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- In scope:")
    lines.append("- Out of scope:")
    lines.append("- Time window:")
    lines.append("")
    lines.append("## Methodology")
    lines.append("")
    lines.append("- Search strategy:")
    lines.append("- Inclusion criteria:")
    lines.append("- Exclusion criteria:")
    lines.append("- Review limitations:")
    lines.append("")
    lines.append("## Taxonomy (working)")
    lines.append("")
    lines.append("- [Fill in: task → method family → key design choices]")
    lines.append("")
    lines.append("## Key papers (core set)")
    lines.append("")
    lines.append("- [Fill in: 15–40 papers after triage; annotate why each is key]")
    lines.append("")
    lines.append("## Comparative insights")
    lines.append("")
    lines.append("### What drives performance?")
    lines.append("")
    lines.append("### Trade-offs (accuracy / compute / data / robustness)")
    lines.append("")
    lines.append("### Failure modes and limitations")
    lines.append("")
    lines.append("### Contradictory evidence")
    lines.append("")
    lines.append("- [List key disagreements side-by-side with likely causes]")
    lines.append("")
    lines.append("### Bias and reliability notes")
    lines.append("")
    lines.append("- Publication bias:")
    lines.append("- Benchmark leakage:")
    lines.append("- Data contamination:")
    lines.append("- Cherry-picking risk:")
    lines.append("")
    lines.append("## Open problems and research directions")
    lines.append("")
    lines.append("- [Each item: gap → why it matters → a concrete experiment to test]")
    lines.append("")
    lines.append("## Paper list (export)")
    lines.append("")
    lines.append(f"Count: {len(papers)}")
    lines.append("")
    lines.append("| arXiv | Title | Published | Primary cat |")
    lines.append("|---|---|---|---|")
    for p in papers:
        arxiv_id = p.get("arxiv_id", "")
        abs_url = p.get("abs_url", "")
        title = (p.get("title", "") or "").replace("|", "\\|")
        published = (p.get("published", "") or "")[:10]
        primary_category = p.get("primary_category", "")
        lines.append(f"| [{arxiv_id}]({abs_url}) | {title} | {published} | {primary_category} |")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- papers.bib contains BibTeX entries for citation tooling.")
    lines.append("- Add per-paper notes in a separate reading-notes.md if needed.")
    lines.append("- Use evidence-table.md to track cross-paper claims before final synthesis.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Create a report skeleton from papers.json.")
    ap.add_argument("--papers-json", required=True, help="Path to papers.json (from arxiv_search.py)")
    ap.add_argument("--topic", required=True, help="Report topic/title")
    ap.add_argument("--out", required=True, help="Output markdown path")
    args = ap.parse_args(argv)

    papers_json = Path(args.papers_json)
    out = Path(args.out)
    papers = _load_papers(papers_json)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render(args.topic, papers), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
