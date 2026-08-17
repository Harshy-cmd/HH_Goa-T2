from __future__ import annotations

"""Create a deterministic, labeled multilingual development subset from MSMARCO-XI Parquet data."""

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def resolve_parquet_file(dataset: str, split: str, lang_code: str, revision: str) -> str:
    """Download or locate the language-specific Parquet split from the Hugging Face Hub."""
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise RuntimeError("Install 'huggingface-hub' to download MSMARCO-XI Parquet files.") from exc

    prefix = split[:3] if split != "train" else "train"
    filename = f"{split}/{lang_code}{prefix}.parquet"
    return hf_hub_download(
        repo_id=dataset,
        filename=filename,
        repo_type="dataset",
        revision=revision,
    )


def load_parquet_table(file_path: str) -> Any:
    """Load Parquet table with PyArrow, selecting only relevant columns to minimize memory."""
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Install 'pyarrow' to read MSMARCO-XI Parquet files.") from exc

    columns = ["query_id", "query", "Eng_Query", "passages", "source_lang", "target_lang"]
    return pq.read_table(file_path, columns=columns)


def process_language_records(
    table: Any,
    indices: list[int],
    target_count: int,
    language: str,
    translated: bool,
    corpus_records: list[dict],
    eval_cases: list[dict],
) -> tuple[int, int]:
    """Deterministically extract and validate examples for a given language.

    Returns:
        (selected_count, rejected_count)
    """
    selected_count = 0
    rejected_count = 0
    seen_query_ids: set[str] = set()

    for idx in indices:
        if selected_count >= target_count:
            break

        row = {col: table[col][idx].as_py() for col in table.column_names}
        query_id = str(row.get("query_id", "")).strip()
        passages_struct = row.get("passages") or {}
        is_selected = passages_struct.get("is_selected") or []

        if translated:
            query = str(row.get("query", "")).strip()
            passage_texts = passages_struct.get("Translated_passages") or []
        else:
            query = str(row.get("Eng_Query", "")).strip()
            passage_texts = passages_struct.get("English_passages") or []

        # Validate completeness, non-empty query, presence of positive label and non-empty relevant passage text
        if (
            not query_id
            or query_id in seen_query_ids
            or not query
            or not passage_texts
            or len(passage_texts) != len(is_selected)
        ):
            rejected_count += 1
            continue

        relevant_docs: list[str] = []
        candidate_corpus: list[dict] = []

        for position, (text, selected) in enumerate(zip(passage_texts, is_selected)):
            clean_text = str(text or "").strip()
            if not clean_text:
                continue
            document_id = f"msmarco-xi:{language}:{query_id}:{position}"
            candidate_corpus.append({
                "document_id": document_id,
                "passage_id": document_id,
                "language": language,
                "title": f"MSMARCO-XI {language} query {query_id}",
                "text": clean_text,
                "metadata": {
                    "query_id": query_id,
                    "passage_position": str(position),
                },
            })
            if int(selected) == 1:
                relevant_docs.append(document_id)

        # Must have at least one relevant passage with non-empty content
        if not relevant_docs:
            rejected_count += 1
            continue

        # Accepted
        seen_query_ids.add(query_id)
        corpus_records.extend(candidate_corpus)
        eval_cases.append({
            "query_id": f"msmarco-xi:{language}:{query_id}",
            "language": language,
            "query": query,
            "relevant_document_ids": relevant_docs,
        })
        selected_count += 1

    return selected_count, rejected_count


def generate_msmarco_subset(
    dataset: str = "ai4bharat/MSMARCO-XI",
    revision: str = "main",
    split: str = "validation",
    examples_per_language: int = 50,
    seed: int = 20260817,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    if output_dir is None:
        root = Path(__file__).resolve().parents[2]
        output_dir = root / "data" / "evaluation" / "msmarco_xi_dev"

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Download and read Parquet files
    hin_path = resolve_parquet_file(dataset, split, "hin", revision)
    kan_path = resolve_parquet_file(dataset, split, "kan", revision)

    hin_table = load_parquet_table(hin_path)
    kan_table = load_parquet_table(kan_path)

    # 2. Compute deterministic shuffled permutation of rows
    num_rows = len(hin_table)
    rng = random.Random(seed)
    indices = list(range(num_rows))
    rng.shuffle(indices)

    corpus_records: list[dict] = []
    eval_cases: list[dict] = []

    # 3. Extract English (from Hindi table's English fields for paired baseline)
    en_selected, en_rejected = process_language_records(
        table=hin_table,
        indices=indices,
        target_count=examples_per_language,
        language="en",
        translated=False,
        corpus_records=corpus_records,
        eval_cases=eval_cases,
    )

    # 4. Extract Hindi
    hi_selected, hi_rejected = process_language_records(
        table=hin_table,
        indices=indices,
        target_count=examples_per_language,
        language="hi",
        translated=True,
        corpus_records=corpus_records,
        eval_cases=eval_cases,
    )

    # 5. Extract Kannada
    kn_selected, kn_rejected = process_language_records(
        table=kan_table,
        indices=indices,
        target_count=examples_per_language,
        language="kn",
        translated=True,
        corpus_records=corpus_records,
        eval_cases=eval_cases,
    )

    # 6. Write output files
    (output_dir / "corpus.jsonl").write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in corpus_records) + "\n",
        encoding="utf-8",
    )
    (output_dir / "eval_cases.jsonl").write_text(
        "\n".join(json.dumps(case, ensure_ascii=False) for case in eval_cases) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "dataset": dataset,
        "revision": revision,
        "split": split,
        "seed": seed,
        "language_mapping": {
            "en": {
                "source_lang": "eng_Latn",
                "target_lang": "hin_Deva",
                "translated": False,
                "parquet_file": f"{split}/hin{split[:3] if split != 'train' else 'train'}.parquet",
            },
            "hi": {
                "source_lang": "eng_Latn",
                "target_lang": "hin_Deva",
                "translated": True,
                "parquet_file": f"{split}/hin{split[:3] if split != 'train' else 'train'}.parquet",
            },
            "kn": {
                "source_lang": "eng_Latn",
                "target_lang": "kan_Knda",
                "translated": True,
                "parquet_file": f"{split}/kan{split[:3] if split != 'train' else 'train'}.parquet",
            },
        },
        "examples_per_language": examples_per_language,
        "languages": ["en", "hi", "kn"],
        "actual_examples_selected": {
            "en": en_selected,
            "hi": hi_selected,
            "kn": kn_selected,
        },
        "rejected_records_count": {
            "en": en_rejected,
            "hi": hi_rejected,
            "kn": kn_rejected,
        },
        "record_count": len(corpus_records),
        "query_count": len(eval_cases),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    (output_dir / "subset_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    args = parse_args()
    manifest = generate_msmarco_subset(
        dataset=args.dataset,
        revision=args.revision,
        split=args.split,
        examples_per_language=args.examples_per_language,
        seed=args.seed,
        output_dir=args.output_dir,
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
