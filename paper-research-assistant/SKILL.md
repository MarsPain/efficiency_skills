---
name: paper-research-assistant
description: Read, analyze, critique, and synthesize academic papers from PDFs, arXiv links, DOI links, titles, pasted text, or paper collections. Use when Codex needs to resolve paper sources, normalize arXiv/PDF/DOI/title inputs, summarize papers, perform deep paper reading, compare methods, build related-work notes, identify research gaps, assess evidence quality, save reusable local Markdown paper cards/research notes, or plan follow-up experiments.
---

# Paper Research Assistant

Use this skill as a research judgment workbench, not a generic paper summarizer. Convert papers into reusable, evidence-backed judgments that help decide what to read deeply, trust, compare, reproduce, or build on.

Core principle: never analyze before resolving the source. First identify the exact paper, evidence coverage, and ambiguity level; then read, critique, or synthesize.

## Task Router

Classify the request before reading deeply:

- **Link mode**: user gives an arXiv/PDF/DOI/publisher URL. Resolve the exact paper and evidence coverage first.
- **Title mode**: user gives one or more paper names. Search for candidates, prefer exact title matches from primary sources, and state ambiguity before analysis.
- **Single-paper skim**: answer what the paper says, whether it is worth deeper reading, and why.
- **Single-paper deep read**: decompose problem, method, assumptions, experiments, claims, evidence, and limitations.
- **Multi-paper synthesis**: build comparison dimensions first, then synthesize consensus, disagreement, missing pieces, and opportunities.
- **Research planning**: extract research gaps, reproducible experiments, baselines, ablations, and next-step ideas.

## Input Handling

Normalize every source into a paper object when possible. For structured normalization, use:

```bash
uv run python /Users/H/.codex/skills/paper-research-assistant/scripts/normalize_paper_input.py <input> [...]
```

Use `assets/paper-object-template.md` for the canonical fields. For source matching rules, read `references/source-resolution.md`.

Prefer full-text PDF or arXiv HTML when available. If only metadata or abstract is available, state the limitation before making judgments. If web lookup is needed for current metadata, DOI resolution, title search, or paper retrieval, use reliable primary sources when possible.

For local PDFs, extract text with page markers when useful:

```bash
uv run python /Users/H/.codex/skills/paper-research-assistant/scripts/extract_pdf_text.py <paper.pdf> --output <paper-text.md>
```

If `pypdf` is not installed in the uv environment, run the same command with `uv run --with pypdf python ...`.

## Reading Workflow

1. Resolve source identity and evidence coverage before analysis.
2. Identify the task type and desired output depth.
3. Load only the needed framework:
   - For arXiv/PDF/DOI/title matching, read `references/source-resolution.md`.
   - For one paper, read `references/reading-framework.md`.
   - For several papers, read `references/synthesis-framework.md`.
   - Before finalizing research judgments, read `references/quality-checklist.md`.
4. Extract the paper structure: problem, context, method, assumptions, experiments, results, claims, and limitations.
5. Separate three layers explicitly:
   - **Paper says**: grounded in the paper text.
   - **Inference**: model interpretation from the evidence.
   - **Research suggestion**: actionable advice or follow-up direction.
6. Use the relevant asset template for stable output:
   - `assets/paper-object-template.md`
   - `assets/single-paper-template.md`
   - `assets/literature-matrix-template.md`
   - `assets/research-note-template.md`
7. Attach evidence markers to important claims: section, figure, table, page, appendix, or quoted phrase when available.

## Output Rules

- Start with a short `Source Resolution` block before substantive analysis.
- Use the two-layer structure: first **what the paper says**, then **what it means for the user's research**.
- Include `Relation To My Research` whenever the user provides their research direction, project, hypothesis, method, dataset, or evaluation goal.
- For multi-paper work, do not stack isolated summaries. Define comparison dimensions first, then fill a matrix and synthesize across papers.
- Say `unknown` or `not established from available text` when evidence is missing.
- Do not overclaim causality, generality, novelty, or reproducibility beyond what the paper supports.

## Local Report Saving

Default to saving substantive reading outputs as Markdown files unless the user explicitly asks for chat-only output. This applies to single-paper skims, deep reads, paper cards, multi-paper syntheses, literature matrices, and research notes.

Choose a low-surprise location:

1. If the user gives an output path, write there.
2. If working from a local PDF or paper folder, write next to the source in a `paper-notes/` or `<paper-name>-notes/` directory.
3. Otherwise, create `paper-notes/` in the current working directory.

Use stable, readable filenames:

- Single paper: `<year>-<short-title>-paper-card.md` or `<year>-<short-title>-deep-read.md`.
- Multi-paper synthesis: `<topic>-literature-matrix.md` and/or `<topic>-research-note.md`.
- Unknown year: use `unknown-year` rather than inventing one.

After writing the file, include a brief chat summary plus the saved path. Do not paste the entire saved report into chat unless the user asks for it.

## Quality Gate

Before finalizing, check:

- Is the exact source identified, or is ambiguity clearly reported?
- Are major judgments tied to paper evidence or clearly labeled as inference?
- Are limitations and missing details visible rather than smoothed over?
- Are datasets, metrics, baselines, and ablations named when available?
- Are practical follow-ups concrete enough to reproduce, compare, extend, or falsify?
- Is confidence calibrated to the amount and quality of available paper text?
- Was the substantive reading output saved locally, or did the user explicitly request chat-only output?
