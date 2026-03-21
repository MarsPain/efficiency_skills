#!/usr/bin/env python3
"""Deterministic fuzzy ranking helper for OmniFocus candidates.

Usage:
  uv run python scripts/fuzzy_rank.py --query "followup legal" --input candidates.json --top 8
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass
class ScoreBreakdown:
    exact: float
    prefix: float
    token_overlap: float
    edit_similarity: float
    project_overlap: float
    semantic: float

    @property
    def total(self) -> float:
        return (
            self.exact
            + self.prefix
            + self.token_overlap
            + self.edit_similarity
            + self.project_overlap
            + self.semantic
        )


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> set[str]:
    return set(TOKEN_RE.findall(normalize(text)))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def to_float01(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def score_candidate(query: str, item: dict[str, Any]) -> tuple[float, ScoreBreakdown, list[str]]:
    name = str(item.get("name") or "")
    project = str(item.get("projectName") or item.get("project") or "")
    semantic_score = to_float01(item.get("semantic_score"))

    qn = normalize(query)
    nn = normalize(name)

    q_tokens = tokenize(query)
    n_tokens = tokenize(name)
    p_tokens = tokenize(project)

    exact = 1.0 if qn and qn == nn else 0.0
    prefix = 0.35 if qn and nn.startswith(qn) else 0.0
    token_overlap = 0.25 * jaccard(q_tokens, n_tokens)
    edit_similarity = 0.25 * SequenceMatcher(None, qn, nn).ratio() if qn and nn else 0.0
    project_overlap = 0.1 * jaccard(q_tokens, p_tokens)
    semantic = 0.4 * semantic_score

    breakdown = ScoreBreakdown(
        exact=exact,
        prefix=prefix,
        token_overlap=token_overlap,
        edit_similarity=edit_similarity,
        project_overlap=project_overlap,
        semantic=semantic,
    )

    reasons: list[str] = []
    if exact > 0:
        reasons.append("exact")
    if prefix > 0:
        reasons.append("prefix")
    if token_overlap >= 0.08:
        reasons.append("token-overlap")
    if edit_similarity >= 0.15:
        reasons.append("edit-sim")
    if semantic >= 0.2:
        reasons.append("semantic")

    return breakdown.total, breakdown, reasons


def load_items(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, dict):
        items = raw.get("items")
        if isinstance(items, list):
            return [x for x in items if isinstance(x, dict)]
    raise ValueError("input must be a JSON list or an object with an 'items' list")


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic fuzzy ranking helper")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--input", required=True, help="Path to candidate JSON")
    parser.add_argument("--top", type=int, default=10, help="Top N results")
    args = parser.parse_args()

    items = load_items(Path(args.input))

    ranked: list[dict[str, Any]] = []
    for item in items:
        score, breakdown, reasons = score_candidate(args.query, item)
        ranked.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "projectName": item.get("projectName") or item.get("project"),
                "score": round(score, 6),
                "reasons": reasons,
                "breakdown": {
                    "exact": round(breakdown.exact, 6),
                    "prefix": round(breakdown.prefix, 6),
                    "token_overlap": round(breakdown.token_overlap, 6),
                    "edit_similarity": round(breakdown.edit_similarity, 6),
                    "project_overlap": round(breakdown.project_overlap, 6),
                    "semantic": round(breakdown.semantic, 6),
                },
            }
        )

    ranked.sort(
        key=lambda x: (
            x["score"],
            1 if "exact" in x["reasons"] else 0,
            1 if "prefix" in x["reasons"] else 0,
            -(len(str(x.get("name") or ""))),
            str(x.get("id") or ""),
        ),
        reverse=True,
    )

    output = {
        "query": args.query,
        "count": len(ranked),
        "results": ranked[: max(1, args.top)],
    }
    print(json.dumps(output, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
