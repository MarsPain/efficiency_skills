---
name: arxiv-deep-research
description: >-
  Academic deep research centered on arXiv papers: systematic paper search,
  metadata collection, screening/triage with a quantitative rubric, structured
  reading notes, taxonomy building, conflict/bias detection, and synthesis into
  a citation-backed survey report. Use when the user asks to: (1) do literature
  review / related work / survey for a topic, (2) discover key papers and
  research gaps on arXiv, (3) find methods, benchmarks, or datasets for a
  research direction, (4) summarize or compare arXiv papers. Do NOT use when
  the request is purely: code implementation, hyperparameter tuning, debugging,
  writing non-academic content, or when the user explicitly says they do NOT
  want a literature review.
---

# arXiv Deep Research

Run an arXiv-first, research-grade literature workflow: search broadly, narrow
systematically, read deeply with structured notes, detect bias, and synthesize
insights (taxonomy + gaps + future directions) into a citation-backed report.

## Workflow router

Choose the lightest workflow that satisfies the request:

1. **Quick reading list**
   Use when the user asks for a starter list, reading list, seminal papers,
   recent papers, or a compact set of methods/datasets. Stop after search +
   triage unless the user explicitly asks for deeper synthesis.
   Deliver `papers.md`, `papers.bib`, `papers.json`, and a brief triage summary.

2. **Deep survey / insight report**
   Use when the user asks for related work, a literature review, a comparison,
   a taxonomy, research gaps, or a citation-backed report.
   Deliver `report.md`, `search_log.md`, and optionally `insights.json`.

3. **Incremental update**
   Use when `papers.json` already exists or the user asks to refresh/update an
   earlier review. Load `references/incremental-research.md` before searching.
   Deliver the updated paper set, updated report artifacts, and a changelog.

Default to **Deep survey / insight report** only when the user wants synthesis,
not when they merely want a paper list.

## Progressive disclosure

Keep `SKILL.md` lean. Read extra references only when they are needed:

- `references/arxiv-query-cheatsheet.md`: only when composing or refining arXiv
  queries.
- `references/triage-rubric.md`: when shrinking candidates into a core set.
- `references/deep-reading-template.md`: when writing per-paper notes.
- `references/evidence-table-template.md`: when building cross-paper evidence
  tables for synthesis.
- `references/report-outline.md`: before drafting `report.md`.
- `references/insights-schema.md`: only when producing `insights.json`.
- `references/quality-gate-checklist.md`: after drafting, before delivery.

## Step 0 — Clarify scope (high impact)

Ask at most one blocking question if the user intent is genuinely ambiguous.
Otherwise, apply defaults, state assumptions, and proceed.

Clarify only the fields that materially change the search:

| Parameter | Clarifying question | Default if unanswered |
|---|---|---|
| **Topic** | Keywords, synonyms, and what is *out of scope* | Use the user’s first message as topic; scope = "latest advances" |
| **Goal** | Reading list vs. survey vs. choosing a method/dataset | Infer from request; default to survey only if the user asks for synthesis |
| **Time window** | Last N years + seminal exceptions | Last 3 years + seminal pre-2023 |
| **arXiv areas** | Categories (e.g., cs.LG, cs.CV, cs.CL) | Infer from topic; default to cs.LG + cs.AI |
| **Output** | Language, length, format | Chinese if user asks in Chinese; English otherwise; ~3000–6000 words |
| **Core set size** | Target number of core papers | 20–30 |
| **Max papers fetched** | Upper bound on initial search | 200 |

## Step 1 — Search strategy (arXiv-first, iterative)

Use an iterative “high recall → high precision” loop:
- Start broad with 2–4 query variants (synonyms, abbreviations, related tasks).
- Add category constraints (`cat:`) to reduce noise.
- Add/replace keywords based on what appears in top abstracts/titles.
- **Log every iteration** in `search_log.md` with this line format:
  ```
  - [YYYY-MM-DD HH:MM] query: "..." | results: N | filter: ... | rationale: ...
  ```

Use `references/arxiv-query-cheatsheet.md` only when query syntax or narrowing
strategy is non-obvious.

## Step 2 — Collect papers (metadata export)

Use `scripts/arxiv_search.py` to fetch metadata and export `papers.json`,
`papers.md`, `papers.csv`, `papers.bib`. Prefer appending to `search_log.md`
from the script so the query trail stays reproducible. Run it with
`uv run python`:

```bash
uv run python scripts/arxiv_search.py \
  --query 'all:"diffusion model" AND (all:"image editing" OR all:"inpainting")' \
  --category cs.CV --category cs.LG \
  --max-results 200 \
  --search-log research/diffusion-image-editing/search_log.md \
  --log-rationale "Initial broad recall query for diffusion-based image editing" \
  --out-dir research/diffusion-image-editing
```

If network is blocked, ask the user for arXiv IDs and use `--ids`:

```bash
uv run python scripts/arxiv_search.py \
  --ids 2301.00001 2206.12345 2005.14165 \
  --search-log research/seed-set/search_log.md \
  --log-rationale "Seed-set import because arXiv network access is blocked" \
  --out-dir research/seed-set
```

If the request is only a quick reading list, stop after Step 3 unless the user
asks for deeper analysis.

## Step 3 — Triage and selection (from list → core set)

Goal: shrink to a manageable core set (default 20–30 papers) without missing
the backbone.

Use the quantitative rubric in `references/triage-rubric.md`:
- Score each paper 0–2 on: Relevance, Method novelty, Experimental completeness,
  Reproduction value (total 0–8).
- Verdict thresholds: 7–8 = Core, 4–6 = Maybe, 0–3 = Drop.
- Apply coverage rules to ensure baselines, seminal works, and conflicting
  evidence are represented.

Passes:
- Pass A (exclude): off-topic, non-technical, missing eval, wrong modality/task.
- Pass B (core): highest scorers per subtopic.
- Pass C (coverage): ensure each major method family and eval protocol is covered.

When uncertain, keep the paper but mark it “maybe”; do not discard silently.

Record borderline keep/drop decisions in `search_log.md` or a short triage note.

## Step 4 — Deep reading (turn papers into structured evidence)

For each core paper, fill the structured note template in
`references/deep-reading-template.md`. Key fields:

- Problem setting + assumptions
- Key novelty (what’s new vs. prior work)
- Method details (architecture/loss/objective/training data)
- Experiments (datasets, metrics, baselines, ablations)
- Limitations / failure modes / compute & data requirements
- Critical assessment (claims vs. evidence gap, reproducibility confidence)
- Cross-links (builds on, conflicts with)

Keep an evidence table so synthesis stays grounded in citations. Start from
`references/evidence-table-template.md` and extend only the columns you need.

## Step 5 — Synthesis (deep insights, not summaries)

Produce:
- **Taxonomy**: organize by task → method family → key design choices.
- **Comparative insights**: why/when methods differ; what really drives gains
  (and what doesn’t).
- **Trends**: what changed over time (data scale, objectives, evaluation norms).
- **Open problems**: concrete gaps with testable research directions.
- **Conflict handling**: present contradictory evidence side-by-side; explain
  likely causes (dataset shift, metric choice, compute differences).
- **Bias notes**: flag publication bias, benchmark leakage, data contamination,
  and cherry-picked metrics.

Use `references/report-outline.md` as the default structure for `report.md`.
Only read `references/insights-schema.md` when you need to emit
machine-readable `insights.json`.

## Step 6 — Quality Gate (Definition of Done)

Before delivering, first run the deterministic bundle validator, then do the
manual research-quality pass:

```bash
uv run python scripts/validate_research_bundle.py \
  --bundle-dir research/diffusion-image-editing \
  --require-search-log \
  --require-report
```

Then run `references/quality-gate-checklist.md`:

- Every key claim has 1–2 arXiv citations.
- Every method family has at least 1 representative paper cited.
- Contradictory evidence is presented side-by-side.
- `search_log.md` exists with all queries, timestamps, result counts, and filter
  rationale.
- `papers.json` and `papers.bib` match the cited set.

## Deliverables (default)

| File | Purpose |
|---|---|
| `papers.md` | Searchable paper table (title/authors/date/arXiv ID/categories/link) |
| `papers.csv` | Spreadsheet-friendly export for sorting/filtering outside Markdown |
| `papers.bib` | BibTeX entries (arXiv eprint + URL) |
| `papers.json` | Machine-readable metadata (for incremental updates) |
| `search_log.md` | Reproducibility log: query, time, results count, filter rationale |
| `report.md` | Survey-style writeup with citations + limitations + open problems |
| `evidence-table.md` *(recommended for deep survey)* | Cross-paper evidence table used during synthesis |
| `insights.json` *(optional)* | Machine-readable summary: taxonomy, trends, gaps, open questions |

Create a report skeleton from `papers.json`:

```bash
uv run python scripts/make_report_skeleton.py \
  --papers-json research/diffusion-image-editing/papers.json \
  --topic "Diffusion-based image editing" \
  --out research/diffusion-image-editing/report.md
```

Create an evidence table skeleton when doing deep survey work:

```bash
cp references/evidence-table-template.md \
  research/diffusion-image-editing/evidence-table.md
```

## Guardrails (research quality)

- Do not claim a paper “proves” something unless the experiments support it;
  cite the exact paper.
- Separate: *what the paper shows* vs. *your inference* vs. *speculation*.
- When evidence conflicts, present both sides and explain likely causes
  (dataset, metrics, compute).
- Flag bias explicitly: publication bias, benchmark leakage, data contamination,
  cherry-picking.
