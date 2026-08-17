from __future__ import annotations

"""Create a deterministic, labeled development subset from MSMARCO-XI validation splits."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Create deterministic English/Hindi/Kannada MSMARCO-XI evaluation data.")
    parser.add_argument("--dataset", default="ai4bharat/MSMARCO-XI")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--split", default="validation")
    parser.add_argument("--examples-per-language", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20260817)
    parser.add_argument("--output-dir", type=Path, default=root / "data" / "evaluation" / "msmarco_xi_dev")
    return parser.parse_args()


def selected_examples(dataset, count: int, seed: int):
    """Datasets streaming shuffle is deterministic for a fixed seed and source revision."""
    return list(dataset.shuffle(seed=seed, buffer_size=10_000).take(count))


def add_language(records: list[dict], cases: list[dict], examples: list[dict], language: str, translated: bool) -> None:
    for example in examples:
        query_id = str(example["query_id"])
        passages = example["passages"]
        texts = passages["Translated_passages"] if translated else passages["English_passages"]
        relevant: list[str] = []
        for position, (text, selected) in enumerate(zip(texts, passages["is_selected"])):
            if not text.strip():
                continue
            document_id = f"msmarco-xi:{language}:{query_id}:{position}"
            records.append({"document_id": document_id, "passage_id": document_id, "language": language,
                            "title": f"MSMARCO-XI {language} query {query_id}", "text": text,
                            "metadata": {"query_id": query_id, "passage_position": str(position)}})
            if int(selected) == 1:
                relevant.append(document_id)
        query = example["query"] if translated else example["Eng_Query"]
        if query.strip() and relevant:
            cases.append({"query_id": f"msmarco-xi:{language}:{query_id}", "language": language,
                          "query": query, "relevant_document_ids": relevant})


def main() -> None:
    args = parse_args()
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("Install the 'datasets' package to create an MSMARCO-XI subset.") from exc
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    cases: list[dict] = []
    # English uses the original fields from the same deterministically sampled Hindi examples.
    hindi = selected_examples(load_dataset(args.dataset, "hi", split=args.split, streaming=True,
                                          revision=args.revision), args.examples_per_language, args.seed)
    add_language(records, cases, hindi, "en", translated=False)
    add_language(records, cases, hindi, "hi", translated=True)
    kannada = selected_examples(load_dataset(args.dataset, "kn", split=args.split, streaming=True,
                                             revision=args.revision), args.examples_per_language, args.seed)
    add_language(records, cases, kannada, "kn", translated=True)
    (args.output_dir / "corpus.jsonl").write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")
    (args.output_dir / "eval_cases.jsonl").write_text("\n".join(json.dumps(case, ensure_ascii=False) for case in cases) + "\n", encoding="utf-8")
    manifest = {"dataset": args.dataset, "revision": args.revision, "split": args.split, "seed": args.seed,
                "examples_per_language": args.examples_per_language, "languages": ["en", "hi", "kn"],
                "record_count": len(records), "query_count": len(cases),
                "created_at": datetime.now(timezone.utc).isoformat()}
    (args.output_dir / "subset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
