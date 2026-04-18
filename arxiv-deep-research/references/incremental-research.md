# Incremental Research Mode

Use this workflow when a `papers.json` already exists and you need to update the survey with recent work.

## Preconditions

- An existing `papers.json` (and optionally `papers.bib`, `papers.md`) from a prior run.
- A target date window (e.g., last 3 months, last 6 months, last N months).

## Workflow

1. **Load existing set**
   ```bash
   # Optional: extract existing arXiv IDs for deduplication
   cat existing/papers.json | uv run python -c "import sys,json; ids=[p['arxiv_id'] for p in json.load(sys.stdin)]; print('\n'.join(ids))" > existing_ids.txt
   ```

2. **Run delta search**
   Use the same query as the original run, but add `--date-from`:
   ```bash
   uv run python scripts/arxiv_search.py \
     --query 'all:"diffusion model" AND (all:"image editing" OR all:"inpainting")' \
     --category cs.CV --category cs.LG \
     --date-from 2025-10-01 \
     --max-results 200 \
     --out-dir research/diffusion-image-editing/delta
   ```

3. **Deduplicate**
   - Compare `delta/papers.json` against `existing/papers.json` by `arxiv_id`.
   - Remove exact arXiv ID matches.
   - Flag near-duplicates (same title or very similar abstract) for manual review.

4. **Triage delta papers**
   - Apply the same triage rubric (`references/triage-rubric.md`) to the new set.
   - Promote to core only if they fill a gap, introduce a new method family, or overturn prior conclusions.

5. **Merge and re-synthesize**
   - Append new core papers to the existing core set.
   - Re-run deep reading for new core papers only.
   - Update taxonomy, comparative insights, and open problems to reflect the delta.
   - Append to `search_log.md` (do not overwrite; keep a chronological trail).

6. **Version deliverables**
   - Update `papers.json` / `papers.bib` / `papers.md` (overwrite or append with a timestamp).
   - Update `report.md` with a "What’s New" section.
   - Update `insights.json` if it exists.
   - Re-run `scripts/validate_research_bundle.py` against the updated bundle.
