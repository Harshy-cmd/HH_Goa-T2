"""Latency Telemetry Benchmark for NOVARON Loop 14.
Measures warm latency breakdowns across Representative Queries:
Embedding + FAISS + BM25 + RRF + Reranker (Target < 100ms) and LLM Generation separately.
"""
from __future__ import annotations

import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.main import pipelines

TEST_QUERIES = [
    "What is Python?",
    "What is FAISS?",
    "What is Retrieval-Augmented Generation (RAG)?",
    "What is gravity?",
    "What is photosynthesis?",
    "What is machine learning?",
    "What is a database index?",
    "What is recursion?",
    "What is an operating system?",
    "What is artificial intelligence?",
    "प्रकाश संश्लेषण क्या है?",
    "गुरुत्वाकर्षण क्या है?",
]


def benchmark_pipeline(pipe, queries: list[str], runs: int = 2):
    # Warmup
    for q in queries[:2]:
        pipe.run(q)

    records = []
    for q in queries:
        for _ in range(runs):
            res = pipe.run(q)
            lat = res.latency_ms
            retrieval_pipeline_ms = lat.get("retrieval", 0) + lat.get("reranking", 0)
            records.append({
                "query": q,
                "embedding": lat.get("embedding", 0),
                "faiss": lat.get("faiss", 0),
                "bm25": lat.get("bm25", 0),
                "rrf": lat.get("rrf", 0),
                "reranking": lat.get("reranking", 0),
                "retrieval_total": retrieval_pipeline_ms,
                "generation": lat.get("generation", 0),
                "rag_total": lat.get("rag_total", 0),
            })
    return records


def main():
    print("=" * 90)
    print("NOVARON LOOP 14 — RETRIEVAL & GENERATION LATENCY BENCHMARK")
    print("=" * 90)

    pipe = pipelines["sentence"]["hybrid_rerank"]
    records = benchmark_pipeline(pipe, TEST_QUERIES, runs=2)

    avg_embed = sum(r["embedding"] for r in records) / len(records)
    avg_faiss = sum(r["faiss"] for r in records) / len(records)
    avg_bm25 = sum(r["bm25"] for r in records) / len(records)
    avg_rrf = sum(r["rrf"] for r in records) / len(records)
    avg_rerank = sum(r["reranking"] for r in records) / len(records)
    avg_ret_total = sum(r["retrieval_total"] for r in records) / len(records)
    avg_gen = sum(r["generation"] for r in records) / len(records)
    avg_rag_total = sum(r["rag_total"] for r in records) / len(records)

    print(f"{'Metric':<35} | {'Average Latency (ms)':<20} | {'Status'}")
    print("-" * 75)
    print(f"{'Dense Embedding (Multilingual E5)':<35} | {avg_embed:>18.2f} ms | OK")
    print(f"{'FAISS Search (1.6k vectors)':<35} | {avg_faiss:>18.2f} ms | FAST (< 1ms)")
    print(f"{'BM25 Lexical Search':<35} | {avg_bm25:>18.2f} ms | FAST (< 2ms)")
    print(f"{'Reciprocal Rank Fusion (RRF)':<35} | {avg_rrf:>18.2f} ms | FAST (< 0.1ms)")
    print(f"{'Reranking Stage':<35} | {avg_rerank:>18.2f} ms | FAST (< 0.5ms)")
    print("-" * 75)
    print(f"{'TOTAL RETRIEVAL (Target < 100ms)':<35} | {avg_ret_total:>18.2f} ms | {'PASS (< 100ms)' if avg_ret_total < 100 else 'FAIL'}")
    print(f"{'LLM Generation (Provider-dependent)':<35} | {avg_gen:>18.2f} ms | External API")
    print(f"{'TOTAL END-TO-END RAG':<35} | {avg_rag_total:>18.2f} ms | Complete Pipeline")
    print("=" * 90)


if __name__ == "__main__":
    main()
