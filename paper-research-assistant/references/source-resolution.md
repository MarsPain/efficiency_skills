# Source Resolution Framework

Use this before analyzing papers from links, PDFs, DOIs, or titles. The goal is to avoid reading or synthesizing the wrong paper.

## 1. Resolve Before Reading

Always produce or internally confirm a paper object before analysis:

- Title
- Authors
- Year
- Venue or source
- DOI
- arXiv ID
- Abstract URL, PDF URL, publisher URL, or local path
- Evidence coverage
- Resolution confidence
- Ambiguities or missing fields

For mechanical parsing, run:

```bash
uv run python /Users/H/.codex/skills/paper-research-assistant/scripts/normalize_paper_input.py <input> [...]
```

## 2. Link Mode

Use when the user provides a URL.

### arXiv URLs

For `arxiv.org/pdf/...` or `arxiv.org/abs/...`:

- Extract the arXiv ID, preserving version suffix when present.
- Normalize abstract URL as `https://arxiv.org/abs/<id>`.
- Normalize PDF URL as `https://arxiv.org/pdf/<id>`.
- Treat source identity as high confidence for the arXiv record.
- Use web access if metadata or full text is needed and not already provided.

### DOI URLs

For `doi.org/...` or raw DOI strings:

- Extract DOI exactly.
- Resolve through DOI or publisher page when possible.
- Treat source identity as medium to high confidence depending on title/metadata visibility.
- Prefer publisher metadata over third-party mirrors.

### Direct PDF URLs

For URLs ending in `.pdf`:

- Treat evidence as potentially full text, but source identity may remain medium confidence until title/authors are extracted.
- Prefer extracting first-page metadata or resolving a linked abstract page before analysis.

## 3. Title Mode

Use when the user provides one or more paper names.

Search and match in this order when available:

- Exact title on arXiv, DOI/publisher page, OpenReview, ACL Anthology, CVF, NeurIPS, ICML, ICLR, ACM, IEEE, PubMed, or the author's project page.
- Near-exact title with matching authors/year.
- Preprint version corresponding to a published version.
- Secondary indexes only when primary sources are unavailable.

If multiple plausible matches exist, list candidates with title, authors, year, source, and confidence instead of silently choosing. Ask for confirmation only when the ambiguity would materially change the analysis.

## 4. Multi-Paper Corpus Mode

For multiple titles or links:

- Build a paper object list first.
- Mark each paper's evidence coverage and confidence.
- Do not begin literature synthesis until the corpus identity is stable enough for the user's goal.
- If some papers are unresolved, continue with resolved papers only if the limitation is explicit.

## 5. Evidence Coverage Labels

Use these labels consistently:

- `full_text_pdf`: local or retrieved PDF text is available.
- `full_text_html`: full paper HTML is available.
- `abstract_only`: only abstract and metadata are available.
- `metadata_only`: title/authors/source are known but abstract/full text is unavailable.
- `partial_text`: selected sections, snippets, or user-provided excerpts only.
- `unknown`: coverage cannot be determined.

## 6. Resolution Confidence

Use calibrated source confidence:

- `high`: exact identifier or exact title from a primary source.
- `medium`: likely match but missing one stabilizing field, such as authors, year, or venue.
- `low`: title is ambiguous, source is secondary, or only partial metadata is available.

## 7. Source Resolution Output

Start substantive answers with:

```markdown
## Source Resolution

- Resolved paper:
- Source:
- Evidence coverage:
- Resolution confidence:
- Ambiguities:
```

If the user wants only a quick answer, keep this block short but do not omit it.
