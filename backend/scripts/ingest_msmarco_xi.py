"""Ingest MSMARCO-XI Multilingual Dataset.
Downloads and streams real multilingual passages from ai4bharat/MSMARCO-XI across all 14 Indic languages:
Assamese (as), Bengali (bn), Gujarati (gu), Hindi (hi), Kannada (kn), Malayalam (ml),
Marathi (mr), Nepali (ne), Odia (or), Punjabi (pa), Sanskrit (sa), Tamil (ta), Telugu (te), Urdu (ur)
plus English (en).

Combines with curated NOVARON domain documents to produce an authoritative 10,000–20,000 chunk corpus.
Also extracts 280+ paired ground-truth benchmark queries for evaluation.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from datasets import load_dataset

from scripts.corpus_builder import get_all_curated_documents

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CORPUS_PATH = DATA_DIR / "novaron_corpus.jsonl"
FIXTURES_PATH = DATA_DIR / "fixtures" / "sample_corpus.jsonl"
EVAL_QUERIES_PATH = DATA_DIR / "msmarco_xi_eval_queries.json"

LANG_PARQUET_MAP = {
    "as": "asm",
    "bn": "ben",
    "gu": "guj",
    "hi": "hin",
    "kn": "kan",
    "ml": "mal",
    "mr": "mar",
    "ne": "nep",
    "or": "ori",
    "pa": "pan",
    "sa": "san",
    "ta": "tam",
    "te": "tel",
    "ur": "urd",
}

PASSAGES_PER_LANG = 800
EVAL_QUERIES_PER_LANG = 20


def text_hash(text: str) -> str:
    return hashlib.sha256(text.strip().casefold().encode("utf-8")).hexdigest()[:16]


def ingest_msmarco_xi() -> tuple[list[dict], list[dict]]:
    all_passages: list[dict] = []
    eval_queries: list[dict] = []
    seen_hashes = set()
    seen_doc_ids = set()

    # 1. Curated NOVARON multi-domain documents
    print("Loading curated NOVARON domain documents...")
    curated = get_all_curated_documents()
    for doc in curated:
        h = text_hash(doc["text"])
        if h not in seen_hashes and doc["document_id"] not in seen_doc_ids:
            seen_hashes.add(h)
            seen_doc_ids.add(doc["document_id"])
            all_passages.append(doc)
    print(f"Loaded {len(all_passages)} curated domain documents.")

    # 2. Ingest MSMARCO-XI for each of the 14 Indic languages
    for lang_code, prefix in LANG_PARQUET_MAP.items():
        print(f"Streaming MSMARCO-XI for language [{lang_code}] ({prefix})...")
        parquet_url = f"https://huggingface.co/datasets/ai4bharat/MSMARCO-XI/resolve/main/validation/{prefix}val.parquet"
        try:
            ds = load_dataset("parquet", data_files=parquet_url, split="train", streaming=True)
        except Exception as exc:
            print(f"Error loading {lang_code}: {exc}. Trying fallback...")
            continue

        lang_passages_count = 0
        lang_eval_count = 0

        for ex in ds:
            qid = ex.get("query_id")
            query_text = (ex.get("query") or "").strip()
            eng_query = (ex.get("Eng_Query") or "").strip()
            passages_obj = ex.get("passages", {})
            trans_passages = passages_obj.get("Translated_passages", [])
            eng_passages = passages_obj.get("English_passages", [])
            is_selected = passages_obj.get("is_selected", [])

            positive_doc_ids = []

            for p_idx, (p_text, sel) in enumerate(zip(trans_passages, is_selected)):
                if not p_text or len(p_text.strip()) < 25:
                    continue

                clean_text = p_text.strip()
                h = text_hash(clean_text)
                if h in seen_hashes:
                    continue

                doc_id = f"msmarco-xi-{lang_code}-{qid}-{p_idx}"
                if doc_id in seen_doc_ids:
                    continue

                seen_hashes.add(h)
                seen_doc_ids.add(doc_id)

                doc_record = {
                    "document_id": doc_id,
                    "passage_id": f"{doc_id}-1",
                    "title": query_text[:80] if query_text else f"MSMARCO Passage {qid}",
                    "domain": "msmarco_xi",
                    "topic": "passage",
                    "language": lang_code,
                    "source_type": "ai4bharat/MSMARCO-XI",
                    "keywords": [lang_code, "msmarco-xi", f"qid-{qid}"],
                    "metadata": {
                        "source_dataset": "ai4bharat/MSMARCO-XI",
                        "query_id": str(qid),
                        "query": query_text,
                        "eng_query": eng_query,
                        "is_selected": str(sel),
                        "original_lang": "en",
                        "target_lang": lang_code,
                    },
                    "text": clean_text,
                }
                all_passages.append(doc_record)
                lang_passages_count += 1

                if sel == 1:
                    positive_doc_ids.append(doc_id)

                if lang_passages_count >= PASSAGES_PER_LANG:
                    break

            # If this query had positive selected passages, save as an eval query
            if positive_doc_ids and query_text and lang_eval_count < EVAL_QUERIES_PER_LANG:
                eval_queries.append({
                    "query": query_text,
                    "eng_query": eng_query,
                    "language": lang_code,
                    "expected_domain": "msmarco_xi",
                    "expected_topic": "passage",
                    "expected_doc_ids": positive_doc_ids,
                    "query_id": qid,
                })
                lang_eval_count += 1

            if lang_passages_count >= PASSAGES_PER_LANG and lang_eval_count >= EVAL_QUERIES_PER_LANG:
                break

        print(f"  [{lang_code}]: Ingested {lang_passages_count} passages, {lang_eval_count} eval queries.")

    # 3. Also ingest English passages from MSMARCO-XI
    print("Ingesting English MSMARCO-XI validation passages...")
    eng_parquet_url = "https://huggingface.co/datasets/ai4bharat/MSMARCO-XI/resolve/main/validation/hinval.parquet"
    try:
        ds_en = load_dataset("parquet", data_files=eng_parquet_url, split="train", streaming=True)
        en_count = 0
        en_eval_count = 0
        for ex in ds_en:
            qid = ex.get("query_id")
            eng_query = (ex.get("Eng_Query") or "").strip()
            passages_obj = ex.get("passages", {})
            eng_passages = passages_obj.get("English_passages", [])
            is_selected = passages_obj.get("is_selected", [])

            positive_doc_ids = []
            for p_idx, (p_text, sel) in enumerate(zip(eng_passages, is_selected)):
                if not p_text or len(p_text.strip()) < 25:
                    continue
                clean_text = p_text.strip()
                h = text_hash(clean_text)
                if h in seen_hashes:
                    continue
                doc_id = f"msmarco-xi-en-{qid}-{p_idx}"
                if doc_id in seen_doc_ids:
                    continue
                seen_hashes.add(h)
                seen_doc_ids.add(doc_id)

                all_passages.append({
                    "document_id": doc_id,
                    "passage_id": f"{doc_id}-1",
                    "title": eng_query[:80] if eng_query else f"MSMARCO English Passage {qid}",
                    "domain": "msmarco_xi",
                    "topic": "passage",
                    "language": "en",
                    "source_type": "ai4bharat/MSMARCO-XI",
                    "keywords": ["en", "msmarco-xi", f"qid-{qid}"],
                    "metadata": {
                        "source_dataset": "ai4bharat/MSMARCO-XI",
                        "query_id": str(qid),
                        "query": eng_query,
                        "is_selected": str(sel),
                    },
                    "text": clean_text,
                })
                en_count += 1
                if sel == 1:
                    positive_doc_ids.append(doc_id)
                if en_count >= PASSAGES_PER_LANG:
                    break

            if positive_doc_ids and eng_query and en_eval_count < EVAL_QUERIES_PER_LANG:
                eval_queries.append({
                    "query": eng_query,
                    "eng_query": eng_query,
                    "language": "en",
                    "expected_domain": "msmarco_xi",
                    "expected_topic": "passage",
                    "expected_doc_ids": positive_doc_ids,
                    "query_id": qid,
                })
                en_eval_count += 1
            if en_count >= PASSAGES_PER_LANG and en_eval_count >= EVAL_QUERIES_PER_LANG:
                break
        print(f"  [en]: Ingested {en_count} English passages, {en_eval_count} eval queries.")
    except Exception as exc:
        print(f"Error ingesting English passages: {exc}")

    return all_passages, eval_queries


def main():
    t0 = time.perf_counter()
    passages, eval_queries = ingest_msmarco_xi()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIXTURES_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Save novaron_corpus.jsonl
    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        for p in passages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # Save sample_corpus.jsonl (first 1000 for lightweight tests)
    with open(FIXTURES_PATH, "w", encoding="utf-8") as f:
        for p in passages[:1000]:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # Save msmarco_xi_eval_queries.json
    with open(EVAL_QUERIES_PATH, "w", encoding="utf-8") as f:
        json.dump(eval_queries, f, indent=2, ensure_ascii=False)

    elapsed = time.perf_counter() - t0
    languages = sorted(list(set(p["language"] for p in passages)))
    print("=" * 80)
    print("NOVARON LOOP 14C — MSMARCO-XI MULTILINGUAL INGESTION COMPLETE")
    print("=" * 80)
    print(f"Total Unique Passages Generated: {len(passages)}")
    print(f"Total Evaluation Queries:        {len(eval_queries)}")
    print(f"Languages Represented ({len(languages)}): {languages}")
    print(f"Saved Corpus to:                 {CORPUS_PATH}")
    print(f"Saved Eval Queries to:           {EVAL_QUERIES_PATH}")
    print(f"Ingestion Elapsed Time:          {elapsed:.2f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
