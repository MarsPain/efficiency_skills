#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional


ARXIV_API_URL = "http://export.arxiv.org/api/query"


@dataclass(frozen=True)
class ArxivPaper:
    arxiv_id: str
    title: str
    summary: str
    authors: list[str]
    published: str
    updated: str
    primary_category: str
    categories: list[str]
    pdf_url: str
    abs_url: str


def _strip_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _normalize_arxiv_id(arxiv_id: str) -> str:
    arxiv_id = arxiv_id.strip()
    arxiv_id = re.sub(r"^arxiv:", "", arxiv_id, flags=re.IGNORECASE)
    arxiv_id = re.sub(r"^https?://arxiv\.org/abs/", "", arxiv_id)
    arxiv_id = re.sub(r"^https?://arxiv\.org/pdf/", "", arxiv_id)
    arxiv_id = re.sub(r"\.pdf$", "", arxiv_id)
    return arxiv_id


def _parse_iso_date(d: Optional[str]) -> Optional[date]:
    if not d:
        return None
    return date.fromisoformat(d)


def _to_bibtex_key(paper: ArxivPaper) -> str:
    last = "unknown"
    if paper.authors:
        last = paper.authors[0].split()[-1]
    year = paper.published[:4] if paper.published else "0000"
    suffix = paper.arxiv_id.replace("/", "_").replace(".", "_")
    return f"{last}{year}_{suffix}"


def _paper_to_bibtex(paper: ArxivPaper) -> str:
    authors = " and ".join(paper.authors) if paper.authors else "Unknown"
    year = paper.published[:4] if paper.published else "0000"
    title = paper.title.replace("{", "\\{").replace("}", "\\}")
    key = _to_bibtex_key(paper)
    lines = [
        f"@article{{{key},",
        f"  title = {{{title}}},",
        f"  author = {{{authors}}},",
        f"  year = {{{year}}},",
        f"  eprint = {{{paper.arxiv_id}}},",
        "  archivePrefix = {arXiv},",
        f"  primaryClass = {{{paper.primary_category}}},",
        f"  url = {{{paper.abs_url}}},",
        "}",
    ]
    return "\n".join(lines)


def _build_search_query(query: Optional[str], categories: list[str]) -> str:
    parts: list[str] = []
    if query:
        parts.append(f"({query})")
    if categories:
        cats = " OR ".join([f"cat:{c}" for c in categories])
        parts.append(f"({cats})")
    if not parts:
        raise ValueError("Provide --query and/or at least one --category.")
    return " AND ".join(parts)


def _fetch_arxiv_feed(search_query: str, start: int, max_results: int, sort_by: str, sort_order: str) -> str:
    params = {
        "search_query": search_query,
        "start": str(start),
        "max_results": str(max_results),
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "arxiv-deep-research/1.0 (mailto:unknown)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _parse_feed(xml_text: str) -> list[ArxivPaper]:
    ns = {
        "a": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    root = ET.fromstring(xml_text)
    papers: list[ArxivPaper] = []

    for entry in root.findall("a:entry", ns):
        entry_id = (entry.findtext("a:id", default="", namespaces=ns) or "").strip()
        arxiv_id = _normalize_arxiv_id(entry_id)

        title = _strip_whitespace(entry.findtext("a:title", default="", namespaces=ns) or "")
        summary = _strip_whitespace(entry.findtext("a:summary", default="", namespaces=ns) or "")
        published = (entry.findtext("a:published", default="", namespaces=ns) or "").strip()
        updated = (entry.findtext("a:updated", default="", namespaces=ns) or "").strip()
        authors = []
        for a in entry.findall("a:author", ns):
            name = _strip_whitespace(a.findtext("a:name", default="", namespaces=ns) or "")
            if name:
                authors.append(name)

        categories = []
        for c in entry.findall("a:category", ns):
            term = c.attrib.get("term", "").strip()
            if term:
                categories.append(term)

        primary_category = (entry.find("arxiv:primary_category", ns).attrib.get("term", "") if entry.find("arxiv:primary_category", ns) is not None else "")

        abs_url = f"https://arxiv.org/abs/{arxiv_id}"
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        papers.append(
            ArxivPaper(
                arxiv_id=arxiv_id,
                title=title,
                summary=summary,
                authors=authors,
                published=published,
                updated=updated,
                primary_category=primary_category,
                categories=sorted(set(categories)),
                pdf_url=pdf_url,
                abs_url=abs_url,
            )
        )
    return papers


def _filter_by_date(papers: list[ArxivPaper], date_from: Optional[date], date_to: Optional[date]) -> list[ArxivPaper]:
    if not date_from and not date_to:
        return papers

    def _paper_published_date(p: ArxivPaper) -> Optional[date]:
        if not p.published:
            return None
        try:
            # arXiv uses RFC3339 timestamps, e.g. 2023-01-01T00:00:00Z
            return datetime.fromisoformat(p.published.replace("Z", "+00:00")).date()
        except Exception:
            return None

    filtered: list[ArxivPaper] = []
    for p in papers:
        d = _paper_published_date(p)
        if d is None:
            continue
        if date_from and d < date_from:
            continue
        if date_to and d > date_to:
            continue
        filtered.append(p)
    return filtered


def _append_search_log(
    path: Path,
    *,
    query_text: str,
    result_count: int,
    filter_text: str,
    rationale: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = (
        f'- [{timestamp}] query: "{query_text}" | results: {result_count} | '
        f"filter: {filter_text or 'none'} | rationale: {rationale or 'none'}"
    )
    with path.open("a", encoding="utf-8") as f:
        if path.exists() and path.stat().st_size > 0:
            f.write("\n")
        f.write(line + "\n")


def _write_outputs(out_dir: Path, papers: list[ArxivPaper]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "papers.json").write_text(
        json.dumps([asdict(p) for p in papers], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    with (out_dir / "papers.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "arxiv_id",
                "title",
                "authors",
                "published",
                "primary_category",
                "categories",
                "abs_url",
                "pdf_url",
            ]
        )
        for p in papers:
            w.writerow(
                [
                    p.arxiv_id,
                    p.title,
                    "; ".join(p.authors),
                    p.published,
                    p.primary_category,
                    "; ".join(p.categories),
                    p.abs_url,
                    p.pdf_url,
                ]
            )

    lines = [
        "# Papers",
        "",
        f"Count: {len(papers)}",
        "",
        "| arXiv | Title | Published | Primary cat |",
        "|---|---|---|---|",
    ]
    for p in papers:
        title = p.title.replace("|", "\\|")
        published = p.published[:10] if p.published else ""
        lines.append(f"| [{p.arxiv_id}]({p.abs_url}) | {title} | {published} | {p.primary_category} |")
    (out_dir / "papers.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    bib = "\n\n".join([_paper_to_bibtex(p) for p in papers]).strip() + "\n"
    (out_dir / "papers.bib").write_text(bib, encoding="utf-8")


def _chunked(seq: list[str], n: int) -> Iterable[list[str]]:
    for i in range(0, len(seq), n):
        yield seq[i : i + n]

def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Search arXiv and export metadata (json/csv/md/bib).")
    p.add_argument("--query", help="arXiv API search_query string, e.g. all:\"diffusion\" AND cat:cs.CV")
    p.add_argument("--category", action="append", default=[], help="Category filter, e.g. cs.CV (repeatable)")
    p.add_argument("--max-results", type=int, default=200, help="Max results to fetch (API paginates)")
    p.add_argument("--page-size", type=int, default=100, help="Per-request page size (<= 200 recommended)")
    p.add_argument("--sort-by", default="relevance", choices=["relevance", "lastUpdatedDate", "submittedDate"])
    p.add_argument("--sort-order", default="descending", choices=["ascending", "descending"])
    p.add_argument("--date-from", help="Filter by published date >= YYYY-MM-DD (client-side)")
    p.add_argument("--date-to", help="Filter by published date <= YYYY-MM-DD (client-side)")
    p.add_argument("--search-log", help="Optional path to append a Step 1 search log line")
    p.add_argument("--log-filter", default="", help="Optional filter summary for search_log.md")
    p.add_argument("--log-rationale", default="", help="Optional rationale for search_log.md")
    p.add_argument("--out-dir", required=True, help="Output directory")
    p.add_argument("--ids", nargs="*", help="Fetch specific arXiv IDs (bypasses --query/--category)")
    args = p.parse_args(argv)

    out_dir = Path(args.out_dir)
    date_from = _parse_iso_date(args.date_from)
    date_to = _parse_iso_date(args.date_to)

    papers: list[ArxivPaper] = []

    if args.ids:
        normalized = [_normalize_arxiv_id(i) for i in args.ids]
        # arXiv API doesn't have a direct "id list" param; use id_list with batching.
        for batch in _chunked(normalized, 50):
            params = {"id_list": ",".join(batch)}
            url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={"User-Agent": "arxiv-deep-research/1.0 (mailto:unknown)"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                xml_text = resp.read().decode("utf-8", errors="replace")
            papers.extend(_parse_feed(xml_text))
            time.sleep(0.4)
    else:
        search_query = _build_search_query(args.query, args.category)
        start = 0
        remaining = max(0, int(args.max_results))
        while remaining > 0:
            batch_size = min(int(args.page_size), remaining)
            xml_text = _fetch_arxiv_feed(search_query, start=start, max_results=batch_size, sort_by=args.sort_by, sort_order=args.sort_order)
            batch = _parse_feed(xml_text)
            if not batch:
                break
            papers.extend(batch)
            start += len(batch)
            remaining -= len(batch)
            time.sleep(0.4)

    papers = _filter_by_date(papers, date_from=date_from, date_to=date_to)
    seen: set[str] = set()
    deduped: list[ArxivPaper] = []
    for paper in papers:
        if paper.arxiv_id in seen:
            continue
        seen.add(paper.arxiv_id)
        deduped.append(paper)

    _write_outputs(out_dir, deduped)
    if args.search_log:
        if args.ids:
            query_text = "id_list:" + ",".join(normalized)
        else:
            query_text = _build_search_query(args.query, args.category)
        filter_parts: list[str] = []
        if args.category:
            filter_parts.append("categories=" + ",".join(args.category))
        if args.date_from:
            filter_parts.append(f"date_from={args.date_from}")
        if args.date_to:
            filter_parts.append(f"date_to={args.date_to}")
        if args.sort_by != "relevance" or args.sort_order != "descending":
            filter_parts.append(f"sort={args.sort_by}/{args.sort_order}")
        if args.log_filter:
            filter_parts.append(args.log_filter)
        _append_search_log(
            Path(args.search_log),
            query_text=query_text,
            result_count=len(deduped),
            filter_text="; ".join(filter_parts),
            rationale=args.log_rationale,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
