# Triage Rubric (0–2 scoring)

Score each candidate paper on four dimensions. Sum to a 0–8 total.

| Dimension | 0 (Drop) | 1 (Maybe) | 2 (Core) |
|---|---|---|---|
| **Relevance** | Off-topic or wrong task/modality | Related but peripheral (survey mentions, minor variant) | Directly addresses the research question |
| **Method novelty** | Trivial adaptation or re-implementation | Incremental improvement with some insight | New paradigm, key architectural/algorithmic contribution |
| **Experimental completeness** | No experiments or broken eval | Limited baselines or missing ablations | Strong baselines, proper ablations, reproducible metrics |
| **Reproduction value** | Proprietary data or no code | Partial details; requires guesswork | Code available, hyperparams reported, standard datasets |

## Decision thresholds

| Total score | Verdict | Action |
|---|---|---|
| 7–8 | Core | Must include; read deeply |
| 4–6 | Maybe | Include if it fills a gap; mark for targeted reading |
| 0–3 | Drop | Exclude; note reason in log if borderline |

## Coverage rules (override low totals when needed)

- **Baseline coverage**: At least one strong baseline per method family must be core, even if individually it scores 5–6.
- **Temporal coverage**: At least one seminal pre-time-window paper should be core if it founded a method family.
- **Conflict coverage**: If two papers contradict each other on a key claim, both should be core (or at least maybe) so the conflict can be analyzed.

## Quick pass heuristics

- **Pass A (exclude)**: off-topic, non-technical, missing eval, wrong modality/task → Drop (0–1 total).
- **Pass B (core)**: pick highest scorers per subtopic → Core (7–8).
- **Pass C (coverage)**: ensure each method family and dataset/eval protocol is represented; promote maybes to core if gaps exist.

When uncertain, keep the paper but mark it "maybe"; do not discard silently.
