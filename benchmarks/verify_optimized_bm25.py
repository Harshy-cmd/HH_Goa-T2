"""
Verification and correctness test comparing Old BM25 vs New Inverted-Index BM25.
Strictly offline — zero cloud calls.
"""
from __future__ import annotations

import heapq
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from app.domain import Chunk, SearchHit
from app.retrieval import tokenize
from app.vector_store import FaissVectorStore
from benchmarks.benchmark_latency import BENCHMARK_QUERIES


class OptimizedBM25Retriever:
    def __init__(self, chunks: Iterable[Chunk], k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks = list(chunks)
        self.k1, self.b = k1, b
        total_docs = len(self.chunks)

        self.tokens = [tokenize(chunk.text) for chunk in self.chunks]
        self.lengths = [len(toks) for toks in self.tokens]
        self.average_length = sum(self.lengths) / max(total_docs, 1)

        avg_len = max(self.average_length, 1.0)
        self.doc_len_norm = [
            self.k1 * (1.0 - self.b + self.b * (l / avg_len))
            for l in self.lengths
        ]

        self.document_frequency: dict[str, int] = defaultdict(int)
        postings_builder: dict[str, list[tuple[int, int]]] = defaultdict(list)

        for doc_idx, terms in enumerate(self.tokens):
            term_counts = Counter(terms)
            for term, count in term_counts.items():
                postings_builder[term].append((doc_idx, count))
                self.document_frequency[term] += 1

        self.postings: dict[str, list[tuple[int, int]]] = dict(postings_builder)

        self.idf: dict[str, float] = {}
        for term, df in self.document_frequency.items():
            self.idf[term] = math.log(1.0 + (total_docs - df + 0.5) / (df + 0.5))

    def search(self, query: str, limit: int) -> list[SearchHit]:
        hits, _ = self.search_with_profile(query, limit)
        return hits

    def search_with_profile(self, query: str, limit: int) -> tuple[list[SearchHit], dict[str, float]]:
        started = time.perf_counter()
        query_terms = tokenize(query)
        if not query_terms or not self.chunks:
            return [], {"bm25": (time.perf_counter() - started) * 1000}

        query_counts = Counter(query_terms)
        scores: dict[int, float] = defaultdict(float)
        k1_plus_1 = self.k1 + 1.0

        for term, q_freq in query_counts.items():
            idf_val = self.idf.get(term)
            if idf_val is None:
                continue
            term_weight = q_freq * idf_val * k1_plus_1
            postings_list = self.postings.get(term)
            if postings_list is None:
                continue
            for doc_idx, tf in postings_list:
                scores[doc_idx] += term_weight * tf / (tf + self.doc_len_norm[doc_idx])

        if not scores:
            return [], {"bm25": (time.perf_counter() - started) * 1000}

        if len(scores) <= limit:
            top_items = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        else:
            top_items = heapq.nlargest(limit, scores.items(), key=lambda item: item[1])

        hits = [
            SearchHit(chunk=self.chunks[doc_idx], score=score, retriever="bm25")
            for doc_idx, score in top_items
        ]
        return hits, {"bm25": (time.perf_counter() - started) * 1000}


def main():
    print("Loading chunks for correctness verification...")
    index_dir = ROOT / "data" / "indexes" / "sentence"
    store = FaissVectorStore.load(index_dir)

    t0 = time.perf_counter()
    new_bm25 = OptimizedBM25Retriever(store.chunks)
    init_time = (time.perf_counter() - t0) * 1000
    print(f"Optimized BM25 index built in {init_time:.2f} ms")

    baseline_file = ROOT / "benchmarks" / "results" / "bm25_baseline.json"
    with open(baseline_file, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    top1_agreements = 0
    top3_overlaps = []
    top5_overlaps = []
    top10_overlaps = []
    latencies = []
    total_queries_with_results = 0

    print("\nVerifying correctness against baseline across 85 queries...")
    for item in BENCHMARK_QUERIES:
        qid = item["id"]
        q = item["query"]
        base_hits = baseline[qid]["hits"]

        hits, prof = new_bm25.search_with_profile(q, limit=10)
        latencies.append(prof["bm25"])

        if not base_hits and not hits:
            # Both returned 0 hits (e.g. out of domain / gibberish)
            top1_agreements += 1
            top3_overlaps.append(1.0)
            top5_overlaps.append(1.0)
            top10_overlaps.append(1.0)
            continue

        total_queries_with_results += 1
        base_ids = [h["chunk_id"] for h in base_hits]
        new_ids = [h.chunk.chunk_id for h in hits]

        # Top 1 agreement
        if base_ids and new_ids and base_ids[0] == new_ids[0]:
            top1_agreements += 1

        # Overlaps
        def overlap(a, b, k):
            set_a = set(a[:k])
            set_b = set(b[:k])
            if not set_a and not set_b:
                return 1.0
            if not set_a or not set_b:
                return 0.0
            return len(set_a & set_b) / max(len(set_a), len(set_b))

        top3_overlaps.append(overlap(base_ids, new_ids, 3))
        top5_overlaps.append(overlap(base_ids, new_ids, 5))
        top10_overlaps.append(overlap(base_ids, new_ids, 10))

    n = len(BENCHMARK_QUERIES)
    top1_pct = (top1_agreements / n) * 100
    top3_pct = (sum(top3_overlaps) / n) * 100
    top5_pct = (sum(top5_overlaps) / n) * 100
    top10_pct = (sum(top10_overlaps) / n) * 100

    sorted_lats = sorted(latencies)
    p50_lat = sorted_lats[int(n * 0.5)]
    p70_lat = sorted_lats[int(n * 0.7)]
    p100_lat = sorted_lats[-1]
    mean_lat = sum(sorted_lats) / n

    print("\n" + "=" * 60)
    print("CORRECTNESS TEST RESULTS (Old BM25 vs Optimized Inverted BM25)")
    print("=" * 60)
    print(f"Total Queries Evaluated : {n}")
    print(f"Top-1 Agreement         : {top1_pct:.2f}%")
    print(f"Top-3 Overlap           : {top3_pct:.2f}%")
    print(f"Top-5 Overlap           : {top5_pct:.2f}%")
    print(f"Top-10 Overlap          : {top10_pct:.2f}%")
    print("-" * 60)
    print("NEW BM25 LATENCY:")
    print(f"  • P50  : {p50_lat:.3f} ms")
    print(f"  • P70  : {p70_lat:.3f} ms")
    print(f"  • P100 : {p100_lat:.3f} ms")
    print(f"  • Mean : {mean_lat:.3f} ms")
    print("=" * 60)

if __name__ == "__main__":
    main()
