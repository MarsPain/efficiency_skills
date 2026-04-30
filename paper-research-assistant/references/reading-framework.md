# Single-Paper Reading Framework

Use this framework for single-paper skim or deep-read tasks. The goal is to convert the paper into a reusable research judgment, not to restate every section.

## 1. Bibliographic Object

Capture the stable identity of the paper:

- Title
- Authors
- Year
- Venue, preprint server, or source
- DOI, arXiv ID, URL, or local PDF path
- Available evidence: full text, abstract only, selected sections, figures/tables, appendix, or user notes

If any field is unavailable, mark it as `unknown` instead of inventing it.

## 2. Reading Modes

### Skim Mode

Use when the user needs fast triage.

Answer:

- What is the paper about in 3-5 sentences?
- What is the central contribution or claim?
- What evidence does it rely on?
- Is it worth deeper reading for the user's stated goal?
- What sections, figures, or tables should be read first?

### Deep Mode

Use when the user wants careful analysis.

Extract:

- Research problem: what failure, gap, inefficiency, or unanswered question motivates the work?
- Prior context: what existing line of work does it position against?
- Core method: what mechanism, architecture, algorithm, intervention, theory, or experimental design is proposed?
- Assumptions: what has to be true for the method or argument to work?
- Evidence: datasets, benchmarks, participant samples, metrics, baselines, ablations, qualitative evidence, or proofs.
- Claims: explicit author claims, especially abstract/introduction/conclusion claims.
- Limitations: stated limitations plus limitations implied by the evidence.
- Transferability: where the findings likely apply, and where they may not.

## 3. Evidence Extraction

For each important judgment, attach the best available locator:

- Section name or number
- Page number if visible
- Figure or table number
- Appendix section
- Short phrase from the paper when exact location is unavailable

Use short quotations sparingly. Prefer paraphrase plus locator.

## 4. Claims vs Evidence

Evaluate support with calibrated language:

- **Strongly supported**: direct evidence, appropriate baseline/control, robust metric, and clear ablation or sensitivity analysis.
- **Partially supported**: evidence exists but is narrow, missing ablations, weak baselines, limited sample, or unclear external validity.
- **Weakly supported**: claim is plausible but mostly asserted, only shown in examples, or not tested directly.
- **Not established**: available text does not provide enough evidence.

## 5. Research Usefulness

Translate the paper into future use:

- Reusable method, dataset, benchmark, metric, prompt, framework, theory, or failure case.
- Baselines to reproduce.
- Ablations or controls to borrow.
- Negative results or limitations that narrow the research space.
- Open questions that become concrete follow-up experiments.

## 6. Confidence Calibration

End with a confidence note that separates:

- Conclusions directly supported by paper text.
- Inferences from the structure of the method or experiments.
- Speculative research suggestions.
- Unknowns caused by missing full text, inaccessible appendix, unclear reporting, or extraction limits.
