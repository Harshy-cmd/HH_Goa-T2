# MSMARCO-XI development subset

Create the subset; do not commit dataset text unless its license and storage policy permit it:

```bash
cd backend
python -m scripts.create_msmarco_subset --examples-per-language 50 --seed 20260817
```

The script streams deterministic samples from the `hi` and `kn` validation configurations of `ai4bharat/MSMARCO-XI`. English examples are the original English fields for the deterministically sampled Hindi records; Hindi and Kannada examples use their translated fields. It emits:

- `corpus.jsonl`: passages with stable synthetic IDs;
- `eval_cases.jsonl`: queries and selected-passage relevance IDs;
- `subset_manifest.json`: dataset, revision, split, seed, sizes, and timestamp.

The selection is seeded and applies no relevance, answer-length, or difficulty filtering. The dataset card defines the selected-passage labels and documents the source language configurations.
