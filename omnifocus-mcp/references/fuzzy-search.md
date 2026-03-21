# Fuzzy Search and Ranking Protocol

## Objective
Improve recall for ambiguous language while keeping mutation safety strict.

Use fuzzy search for discovery only. Mutations still require explicit `id` targeting.

## Pipeline

### 1) Query Expansion (Model-Led)
Generate 3-8 variants from user text:
- synonyms
- abbreviations
- typo variants
- mixed-language variants when relevant

Keep original query as anchor. Do not over-expand unrelated terms.

### 2) Broad Retrieval
For each variant, run targeted `query_omnifocus` reads with minimal fields:
- `id`, `name`, `projectName`, `note`, `tagNames`, `modificationDate`

Merge all hits by `id`.

### 3) Hybrid Ranking
Rank merged candidates with two layers:

1. Model semantic fit score (0-1), based on intent alignment.
2. Deterministic tie-breakers:
- exact normalized name match
- prefix match
- token overlap
- edit-distance similarity

For large candidate sets, run local deterministic ranking:

```bash
uv run python scripts/fuzzy_rank.py --query "<query>" --input <candidates.json>
```

### 4) Confidence Gate
Use both top score and top-gap:

- high: `top >= 0.75` and `gap >= 0.15`
- medium: `top >= 0.60` and `gap >= 0.10`
- low: otherwise

Policy:
- high: suggest top candidate first, still show alternatives
- medium/low: require explicit user disambiguation before any write

### 5) Mutation Gate (Mandatory)
Before update/delete/complete:
1. show candidate list (`name`, `id`, `project`)
2. ask for explicit confirmation
3. execute by `id` only

Never execute mutation by fuzzy text match directly.

## Output Format for Ambiguous Matches
Return top 3-8 candidates:

```text
1) <name> | <id> | <project> | reason: <short reason>
2) ...
```

If confidence is low, ask user for ID selection or extra constraint (project/tag/date).
