# Quality Gate Checklist (Step 6 — Definition of Done)

Run this checklist before delivering any report or reading-notes artifact.

## Citation coverage

- [ ] Every key claim (method advantage, trend, failure mode) has 1–2 arXiv citations.
- [ ] Every method family has at least 1 representative core paper cited.
- [ ] Every comparative table or ranking is backed by evidence, not inference alone.

## Conflict and bias handling

- [ ] Contradictory evidence is presented side-by-side, not suppressed.
- [ ] Publication bias is noted: are all positive results? Are negative/failed methods missing?
- [ ] Benchmark leakage is checked: do train/test sets overlap with pretraining data?
- [ ] Data contamination is noted: was the test data seen during training or in prior work?
- [ ] Cherry-picking is flagged: are reported metrics the only ones that improved?

## Structural completeness

- [ ] Taxonomy covers all core method families.
- [ ] Each family has at least one annotated paper.
- [ ] Open problems are concrete (each includes a testable experiment/benchmark).
- [ ] Scope, assumptions, and limitations of the review itself are stated.

## Reproducibility

- [ ] `search_log.md` exists with queries, timestamps, result counts, and filter rationale.
- [ ] `papers.json` and `papers.bib` match the cited set.
- [ ] `insights.json` (if produced) is valid JSON and covers taxonomy, gaps, and open questions.
