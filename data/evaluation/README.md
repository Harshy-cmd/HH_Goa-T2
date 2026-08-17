# MSMARCO-XI development subset

Create the subset; do not commit dataset text unless its license and storage policy permit it:

```bash
cd backend
python -m scripts.create_msmarco_subset --examples-per-language 50 --seed 20260817
```

The script deterministically samples from the Hindi (`validation/hinval.parquet`) and Kannada (`validation/kanval.parquet`) validation Parquet files of `ai4bharat/MSMARCO-XI` using PyArrow. English examples are the paired original English fields (`eng_Latn`) from the sampled Hindi records; Hindi (`hin_Deva`) and Kannada (`kan_Knda`) examples use their respective translated fields. It emits:

- `corpus.jsonl`: passages with stable synthetic IDs;
- `eval_cases.jsonl`: queries and selected-passage relevance IDs;
- `subset_manifest.json`: dataset, revision, split, seed, language mappings, sizes, and rejection stats.

The selection is seeded and rejects malformed or unannotated records (queries without positive selected passages).

3