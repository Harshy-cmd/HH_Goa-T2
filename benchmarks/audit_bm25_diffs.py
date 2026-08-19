"""
Audit script: Find and display all differences between old BM25 and new BM25.
Zero cloud calls.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

import dotenv
dotenv.load_dotenv(ROOT / ".env", override=True)

from app.retrieval import BM25Retriever
from app.vector_store import FaissVectorStore
from benchmarks.benchmark_latency import BENCHMARK_QUERIES

def main():
    index_dir = ROOT / "data" / "indexes" / "sentence"
    store = FaissVectorStore.load(index_dir)
    bm25 = BM25Retriever(store.chunks)

    baseline_file = ROOT / "benchmarks" / "results" / "bm25_baseline.json"
    with open(baseline_file, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    diffs = []

    for item in BENCHMARK_QUERIES:
        qid = item["id"]
        q = item["query"]
        old_hits = baseline[qid]["hits"]
        new_hits_raw, prof = bm25.search_with_profile(q, limit=10)
        new_hits = [
            {
                "chunk_id": h.chunk.chunk_id,
                "score": round(h.score, 6),
                "title": h.chunk.title,
            }
            for h in new_hits_raw
        ]

        old_ids = [h["chunk_id"] for h in old_hits]
        new_ids = [h["chunk_id"] for h in new_hits]

        old_scores = [h["score"] for h in old_hits]
        new_scores = [h["score"] for h in new_hits]

        is_diff = (old_ids != new_ids) or (old_scores != new_scores)
        if is_diff:
            diffs.append({
                "id": qid,
                "lang": item["lang"],
                "category": item["category"],
                "query": q,
                "old_hits": old_hits,
                "new_hits": new_hits,
                "old_ids": old_ids,
                "new_ids": new_ids,
                "old_scores": old_scores,
                "new_scores": new_scores,
            })

    print(f"Total queries with differences: {len(diffs)} / {len(BENCHMARK_QUERIES)}")
    for d in diffs:
        print("\n" + "=" * 80)
        print(f"QUERY ID: {d['id']} | LANG: {d['lang']} | CATEGORY: {d['category']}")
        print(f"QUERY: '{d['query']}'")
        print("-" * 80)
        print("OLD BM25 Top Hits:")
        for idx, h in enumerate(d["old_hits"], start=1):
            print(f"  {idx}. {h['chunk_id']:<35} | score={h['score']:.6f} | title='{h['title']}'")
        print("-" * 80)
        print("NEW BM25 Top Hits:")
        for idx, h in enumerate(d["new_hits"], start=1):
            print(f"  {idx}. {h['chunk_id']:<35} | score={h['score']:.6f} | title='{h['title']}'")

    # Output detailed report as JSON for precision analysis
    diff_report_file = ROOT / "benchmarks" / "results" / "bm25_diff_audit.json"
    with open(diff_report_file, "w", encoding="utf-8") as f:
        json.dump(diffs, f, indent=2, ensure_ascii=False)
    print(f"\nSaved diff report to {diff_report_file}")

if __name__ == "__main__":
    main()
