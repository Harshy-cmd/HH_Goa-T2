from __future__ import annotations

import json
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.embeddings import SentenceTransformerEmbeddingProvider
from app.ingestion import fixed_chunks, hierarchical_chunks, load_jsonl, sentence_chunks
from app.retrieval import (BM25Retriever, CrossEncoderReranker, FAISSDenseRetriever,
                           HashingDenseRetriever, HashingEmbedder, HybridRetriever,
                           TransparentReranker)
from app.vector_store import FaissVectorStore, VectorStoreError


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for case in cases:
        case.setdefault("language", case["query_id"].rsplit("-", 1)[-1])
    return cases


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(round((len(ordered) - 1) * fraction), len(ordered) - 1)]


def latency_summary(values: list[float]) -> dict[str, float]:
    return {"p50": round(statistics.median(values), 3), "p70": round(percentile(values, 0.70), 3),
            "p95": round(percentile(values, 0.95), 3), "p100": round(max(values), 3)} if values else {}


def evaluate(retriever, cases: list[dict[str, Any]], reranker=None, limit: int = 3) -> dict[str, Any]:
    languages: dict[str, dict[str, list[float]]] = {}
    for case in cases:
        language = case["language"]
        metrics = languages.setdefault(language, {"recall": [], "mrr": [], "total": []})
        started = time.perf_counter()
        if hasattr(retriever, "search_with_profile"):
            hits, profile = retriever.search_with_profile(case["query"], max(20, limit * 2))
        else:
            hits, profile = retriever.search(case["query"], max(20, limit * 2)), {}
        if reranker:
            rerank_started = time.perf_counter()
            hits = reranker.rerank(case["query"], hits, limit)
            profile["reranking"] = (time.perf_counter() - rerank_started) * 1000
        else:
            hits = hits[:limit]
        profile["total_retrieval"] = (time.perf_counter() - started) * 1000
        relevant = set(case["relevant_document_ids"])
        ranks = [rank for rank, hit in enumerate(hits, start=1) if hit.chunk.document_id in relevant]
        metrics["recall"].append(float(bool(ranks)))
        metrics["mrr"].append(1 / ranks[0] if ranks else 0.0)
        metrics["total"].append(profile["total_retrieval"])
        for stage, elapsed in profile.items():
            metrics.setdefault(stage, []).append(elapsed)
    return {language: {"recall_at_3": round(sum(values["recall"]) / len(values["recall"]), 3),
                       "mrr_at_3": round(sum(values["mrr"]) / len(values["mrr"]), 3),
                       "latency_ms": {stage: latency_summary(timings) for stage, timings in values.items()
                                      if stage not in {"recall", "mrr", "total"}}}
            for language, values in languages.items()}


def print_method(method: str, value: dict[str, Any]) -> None:
    if value.get("status") == "unavailable":
        print(f"  {method}: unavailable — {value['reason']}")
        return
    for language, metrics in value["languages"].items():
        total = metrics["latency_ms"]["total_retrieval"]
        print(f"  {method:<28} lang={language:<2} Recall@3={metrics['recall_at_3']:.3f} "
              f"MRR@3={metrics['mrr_at_3']:.3f} p50={total['p50']:.3f}ms p95={total['p95']:.3f}ms")


def available(retriever, cases, reranker=None) -> dict[str, Any]:
    return {"status": "available", "languages": evaluate(retriever, cases, reranker)}


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    corpus_path = Path(os.getenv("NOVARON_CORPUS_PATH", str(root / "data" / "fixtures" / "sample_corpus.jsonl")))
    eval_path = Path(os.getenv("NOVARON_EVAL_PATH", str(root / "benchmarks" / "eval_cases.jsonl")))
    index_config = Path(os.getenv("VECTOR_INDEX_DIR", "data/indexes"))
    index_root = index_config if index_config.is_absolute() else root / index_config
    corpus = load_jsonl(corpus_path)
    cases = load_cases(eval_path)
    strategies = (("fixed", fixed_chunks(corpus)), ("sentence", sentence_chunks(corpus)),
                  ("hierarchical", hierarchical_chunks(corpus)))
    report: dict[str, Any] = {"version": "v0.3", "generated_at": datetime.now(timezone.utc).isoformat(),
                              "corpus": str(corpus_path), "evaluation": str(eval_path), "case_count": len(cases),
                              "results": {}}
    print(f"Benchmark cases: {len(cases)} | corpus: {corpus_path}")
    for strategy, chunks in strategies:
        print(f"\nStrategy: {strategy} | chunks: {len(chunks)}")
        hashing = HashingDenseRetriever(chunks, HashingEmbedder())
        bm25 = BM25Retriever(chunks)
        hybrid = HybridRetriever(hashing, bm25)
        methods: dict[str, dict[str, Any]] = {
            "hashing_dense": available(hashing, cases), "bm25": available(bm25, cases),
            "hybrid_rrf": available(hybrid, cases),
            "hybrid_transparent_reranker": available(hybrid, cases, TransparentReranker()),
        }
        index_dir = index_root / strategy
        if not FaissVectorStore.exists(index_dir):
            methods["faiss_dense"] = {"status": "unavailable", "reason": f"Index not found: {index_dir}"}
        else:
            try:
                embedder = SentenceTransformerEmbeddingProvider()
                store = FaissVectorStore.load(index_dir, expected_model=embedder.model_name,
                                              expected_strategy=strategy, expected_normalized=True)
                faiss_dense = FAISSDenseRetriever(store, embedder)
                methods["faiss_dense"] = available(faiss_dense, cases)
            except (VectorStoreError, RuntimeError) as exc:
                methods["faiss_dense"] = {"status": "unavailable", "reason": str(exc)}
        if os.getenv("BENCHMARK_CROSS_ENCODER", "0") == "1":
            try:
                methods["hybrid_cross_encoder"] = available(hybrid, cases, CrossEncoderReranker())
            except RuntimeError as exc:
                methods["hybrid_cross_encoder"] = {"status": "unavailable", "reason": str(exc)}
        else:
            methods["hybrid_cross_encoder"] = {"status": "unavailable", "reason": "Set BENCHMARK_CROSS_ENCODER=1 after the reranker smoke test."}
        report["results"][strategy] = methods
        for name, result in methods.items():
            print_method(name, result)
    output = root / "benchmarks" / "results" / "v03_results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote machine-readable results: {output}")


if __name__ == "__main__":
    main()
