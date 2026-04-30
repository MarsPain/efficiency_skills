# Multi-Paper Synthesis Framework

Use this framework for literature review, related work, method comparison, and research-gap tasks. The goal is cross-paper judgment, not a pile of summaries.

## 1. Normalize The Corpus

Create one paper object per source:

- Paper identifier: short title or author-year.
- Bibliographic fields: title, authors, year, venue/source, DOI/arXiv/URL/path.
- Evidence status: full text, abstract only, skimmed, deeply read, or user-provided notes only.
- Task relevance: why this paper belongs in the set.

Mark incomplete objects clearly.

## 2. Choose Comparison Dimensions First

Before writing summaries, decide the matrix columns that answer the user's question. Common dimensions:

- Problem framing
- Method family
- Key mechanism or hypothesis
- Dataset, domain, or sample
- Evaluation protocol
- Metrics
- Baselines or controls
- Main result
- Claimed contribution
- Limitation
- Reproducibility assets
- Useful for the user's research

Add or remove dimensions based on the topic. Do not default to generic columns if better dimensions exist.

## 3. Build The Matrix

Keep matrix entries compact and comparable. Prefer phrases over paragraphs. Use `unknown` when a paper does not report something or the available text does not include it.

After the matrix, synthesize rather than repeat:

- Consensus: what the papers jointly support.
- Disagreements: where methods, assumptions, or results conflict.
- Lineage: how ideas evolve across time or method families.
- Tradeoffs: what each approach gains and gives up.
- Missing pieces: untested settings, weak baselines, absent ablations, narrow datasets, or unresolved theory.
- Opportunities: concrete research questions, experiments, benchmarks, or hybrid methods.

## 4. Avoid Summary Stacking

Do not write one long section per paper unless the user explicitly asks. If per-paper notes are needed, keep them after the synthesis or in an appendix-style section.

Good synthesis language:

- `Across these papers, the main split is...`
- `The strongest shared assumption is...`
- `The evidence is consistent on X but thin on Y...`
- `Paper A and Paper B disagree because they evaluate under different...`
- `A useful next experiment would isolate...`

## 5. Research Planning From A Corpus

When asked to propose next steps, produce:

- Research gap: precise missing claim, setting, mechanism, or evaluation.
- Why it matters: what decision this gap blocks.
- Testable hypothesis: falsifiable statement.
- Minimal experiment: dataset, baseline, metric, and expected comparison.
- Risk: why the experiment may fail or be uninformative.
- Reuse: which papers provide code, datasets, baselines, metrics, or protocols.

## 6. Evidence And Uncertainty

For each cross-paper conclusion, indicate whether it is based on:

- Directly reported results across multiple papers.
- A contrast between methods or experimental setups.
- An inference from limited or uneven evidence.
- The absence of reported evidence.

Be explicit when corpus coverage is too small to support a strong field-level claim.
