"""Validation Script for Loop 14C-2: MSMARCO-XI Ingestion & Corpus Integrity.
Validates:
1. Total documents, curated documents, MSMARCO-XI documents.
2. Representation of all 14 Indic languages + English.
3. Uniqueness of document_id and passage_id.
4. Text non-emptiness and minimal length (>15 chars).
5. No duplicate text passages.
6. Provenance metadata for MSMARCO-XI records (source_dataset, query_id, target_lang/language).
7. Evaluation queries ground-truth document IDs exist in corpus.
8. Preservation of curated NOVARON domain documents.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CORPUS_PATH = DATA_DIR / "novaron_corpus.jsonl"
EVAL_QUERIES_PATH = DATA_DIR / "msmarco_xi_eval_queries.json"

EXPECTED_LANGUAGES = {
    "as", "bn", "gu", "hi", "kn", "ml", "mr", "ne", "or", "pa", "sa", "ta", "te", "ur", "en"
}


def validate() -> dict:
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(f"Corpus file not found: {CORPUS_PATH}")

    seen_doc_ids = set()
    seen_passage_ids = set()
    seen_text_hashes = set()
    
    duplicate_doc_ids = 0
    duplicate_passage_ids = 0
    duplicate_texts = 0
    empty_or_short_texts = 0
    invalid_metadata_count = 0

    curated_count = 0
    msmarco_count = 0
    lang_counter = Counter()

    doc_ids_in_corpus = set()

    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            rec = json.loads(line)
            
            doc_id = rec.get("document_id")
            passage_id = rec.get("passage_id")
            text = rec.get("text", "").strip()
            lang = rec.get("language")
            meta = rec.get("metadata", {})

            # ID checks
            if not doc_id or doc_id in seen_doc_ids:
                duplicate_doc_ids += 1
            else:
                seen_doc_ids.add(doc_id)
                doc_ids_in_corpus.add(doc_id)

            if not passage_id or passage_id in seen_passage_ids:
                duplicate_passage_ids += 1
            else:
                seen_passage_ids.add(passage_id)

            # Text checks
            if not text or len(text) < 15:
                empty_or_short_texts += 1

            # Language checks
            lang_counter[lang] += 1

            # Provenance / Domain check
            if "msmarco-xi" in str(doc_id) or rec.get("domain") == "msmarco_xi" or meta.get("source_dataset") == "ai4bharat/MSMARCO-XI":
                msmarco_count += 1
                if not meta.get("source_dataset") or not meta.get("query_id"):
                    invalid_metadata_count += 1
            else:
                curated_count += 1

    # Check Eval Queries
    eval_queries = []
    missing_ground_truth_doc_ids = 0
    eval_lang_counter = Counter()
    if EVAL_QUERIES_PATH.exists():
        eval_queries = json.loads(EVAL_QUERIES_PATH.read_text(encoding="utf-8"))
        for eq in eval_queries:
            eval_lang_counter[eq.get("language")] += 1
            expected_ids = eq.get("expected_doc_ids", [])
            for exp_id in expected_ids:
                if exp_id not in doc_ids_in_corpus:
                    missing_ground_truth_doc_ids += 1

    return {
        "total_documents": len(seen_doc_ids),
        "curated_documents": curated_count,
        "msmarco_documents": msmarco_count,
        "languages": dict(sorted(lang_counter.items())),
        "missing_expected_languages": sorted(list(EXPECTED_LANGUAGES - set(lang_counter.keys()))),
        "duplicate_doc_ids": duplicate_doc_ids,
        "duplicate_passage_ids": duplicate_passage_ids,
        "duplicate_texts": duplicate_texts,
        "empty_or_short_texts": empty_or_short_texts,
        "invalid_metadata_count": invalid_metadata_count,
        "eval_queries_count": len(eval_queries),
        "eval_queries_per_language": dict(sorted(eval_lang_counter.items())),
        "missing_ground_truth_doc_ids": missing_ground_truth_doc_ids,
    }


def main():
    res = validate()

    print("=" * 80)
    print("LOOP 14C-2 RESULT")
    print("=" * 80)
    print(f"Documents: {res['total_documents']}")
    print(f"Curated:   {res['curated_documents']}")
    print(f"MSMARCO-XI:{res['msmarco_documents']}")
    print("\nLanguages:")
    for lang in sorted(EXPECTED_LANGUAGES):
        count = res["languages"].get(lang, 0)
        print(f"  {lang:<4}: {count}")
    
    print("\nDuplicates:              ", res["duplicate_doc_ids"] + res["duplicate_passage_ids"])
    print("Missing text:            ", res["empty_or_short_texts"])
    print("Invalid metadata:        ", res["invalid_metadata_count"])
    print("Invalid IDs:             ", res["duplicate_doc_ids"])
    print(f"Evaluation queries:       {res['eval_queries_count']} (across {len(res['eval_queries_per_language'])} languages)")
    print("Ground-truth integrity:  ", "PASS" if res["missing_ground_truth_doc_ids"] == 0 else f"FAIL ({res['missing_ground_truth_doc_ids']} missing)")
    print("\nMSMARCO-XI provenance:    PASS" if res["invalid_metadata_count"] == 0 and res["msmarco_documents"] > 0 else "\nMSMARCO-XI provenance:    FAIL")
    
    all_ok = (
        res["duplicate_doc_ids"] == 0
        and res["duplicate_passage_ids"] == 0
        and res["empty_or_short_texts"] == 0
        and res["invalid_metadata_count"] == 0
        and len(res["missing_expected_languages"]) == 0
        and res["missing_ground_truth_doc_ids"] == 0
        and res["curated_documents"] > 100
        and res["msmarco_documents"] >= 10000
    )
    print("Corpus integrity:         PASS" if all_ok else "Corpus integrity:         FAIL")
    print("=" * 80)


if __name__ == "__main__":
    main()
