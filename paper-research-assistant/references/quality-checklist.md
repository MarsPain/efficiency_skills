# Quality Checklist

Use this checklist before finalizing paper cards, literature matrices, critiques, or research plans.

## Evidence Grounding

- Tie important claims to section, page, figure, table, appendix, or a short textual locator when available.
- Separate paper claims from your interpretation.
- Do not treat abstract-level claims as proven unless results support them.
- Do not infer unstated datasets, baselines, metrics, sample sizes, or implementation details.
- If only abstract or metadata is available, label the output as abstract-based triage.

## Claims vs Evidence

Check whether the paper's main claims are supported by:

- Appropriate datasets, participants, simulations, or theoretical assumptions.
- Meaningful baselines or controls.
- Metrics aligned with the claim.
- Ablations, robustness checks, sensitivity analysis, or error analysis.
- Statistical uncertainty or repeated runs when relevant.
- Qualitative evidence when the claim is interpretive or human-centered.

Flag mismatches such as broad claims from narrow benchmarks, causal claims from correlational evidence, or novelty claims without sufficient related-work comparison.

## Reproducibility

Look for:

- Code, data, models, prompts, protocols, preregistration, or appendices.
- Hyperparameters, compute budget, training details, sample criteria, or preprocessing steps.
- Baseline implementation details.
- Enough information to reproduce the core result.

If reproducibility is unclear, say what is missing.

## Research Usefulness

A good output should help the user decide at least one of:

- Whether to read the paper deeply.
- Whether to trust a claim.
- Whether to reproduce a result.
- Which baseline, dataset, metric, or method to reuse.
- What gap or experiment to pursue next.

Avoid generic praise. Make usefulness concrete.

## Hallucination Guardrails

Use these labels consistently:

- **From paper**: directly grounded in the provided or retrieved text.
- **Inference**: reasoned interpretation that is not directly stated.
- **Suggestion**: research advice or next step.
- **Unknown**: not available from the current evidence.

Prefer `unknown` over plausible fabrication. If a PDF parse fails or sections are missing, report the failure and continue only within the available evidence.

## Final Confidence Statement

End substantial outputs with a confidence note covering:

- Evidence coverage: full paper, partial paper, abstract only, metadata only, or mixed corpus.
- Strongest grounded judgments.
- Main uncertainties.
- Which conclusions should be revisited after obtaining more text or running experiments.
