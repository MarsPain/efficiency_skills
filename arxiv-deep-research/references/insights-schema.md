# insights.json Schema

A machine-readable summary of the review for downstream processing.

## Schema (JSON)

```json
{
  "meta": {
    "topic": "Diffusion-based image editing",
    "generated_at": "2026-04-18",
    "time_window": "2021-01-01 to 2026-04-18",
    "search_queries": [
      "all:\"diffusion model\" AND (all:\"image editing\" OR all:inpainting) AND cat:cs.CV"
    ],
    "total_papers_fetched": 200,
    "core_set_size": 28
  },
  "taxonomy": [
    {
      "family": "Inversion-based editing",
      "description": "Invert image to noise and edit in latent space",
      "key_papers": ["ho2022imaginative_v1", "meng2021sdedit_v1"],
      "design_choices": ["inversion method", "guidance scale", "cross-attention control"]
    }
  ],
  "trends": [
    {
      "claim": "Training-free methods are closing the gap with finetuned methods",
      "evidence_papers": ["paper_key_1", "paper_key_2"],
      "confidence": "medium"
    }
  ],
  "gaps": [
    {
      "gap": "No standardized benchmark for identity-preserving editing",
      "why_it_matters": "Prevents fair comparison across methods",
      "suggested_experiment": "Propose EditBench-Identity with paired before/after metrics"
    }
  ],
  "open_questions": [
    {
      "question": "Can diffusion editing be made real-time on consumer GPUs?",
      "related_papers": ["paper_key_3"],
      "testable_direction": "Distill a 4-step latent editor under 8 GB VRAM"
    }
  ],
  "bias_notes": {
    "publication_bias": "Most papers report only best-case metrics; negative results are absent.",
    "benchmark_leakage": "LAION pretraining may overlap with editing benchmarks.",
    "data_contamination": "Some test prompts appear in CLIP training data."
  }
}
```

## Field definitions

- `meta`: provenance and scope.
- `taxonomy`: method families with key papers and design choices.
- `trends`: evidence-backed claims about how the field is evolving.
- `gaps`: concrete missing pieces with suggested experiments.
- `open_questions`: high-level questions with testable directions.
- `bias_notes`: explicit warnings about reliability of the evidence base.
