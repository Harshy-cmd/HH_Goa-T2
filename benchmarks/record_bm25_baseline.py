"""
Record baseline BM25 retrieval results on benchmark queries before optimization.
Strictly offline — zero cloud calls.
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

from benchmarks.benchmark_latency import BENCHMARK_QUERIES
from app.retrieval import BM25Retriever
from app.vector_store import FaissVectorStore

def main():
    print("Loading FAISS store for baseline chunk collection...")
    index_dir = ROOT / "data" / "indexes" / "sentence"
    store = FaissVectorStore.load(index_dir)
    bm25 = BM25Retriever(store.chunks)

    baseline_results = {}
    print(f"Running baseline BM25 on {len(BENCHMARK_QUERIES)} queries...")
    for item in BENCHMARK_QUERIES:
        qid = item["id"]
        q = item["query"]
        hits = bm25.search(q, limit=10)
        baseline_results[qid] = {
            "query": q,
            "lang": item["lang"],
            "hits": [
                {
                    "chunk_id": h.chunk.chunk_id,
                    "score": round(h.score, 6),
                    "title": h.chunk.title,
                }
                for h in hits
            ],
        }

    out_file = ROOT / "benchmarks" / "results" / "bm25_baseline.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(baseline_results, f, indent=2, ensure_ascii=False)

    print(f"Saved baseline BM25 results for {len(baseline_results)} queries to {out_file}")

if __name__ == "__main__":
    main()
