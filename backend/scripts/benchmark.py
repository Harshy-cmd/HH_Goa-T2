from __future__ import annotations

import argparse
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


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Run NOVARON multilingual retrieval benchmark.")
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path(os.getenv("NOVARON_CORPUS_PATH", str(root / "data" / "fixtures" / "sample_corpus.jsonl"))),
        help="Path to JSONL corpus file.",
    )
    parser.add_argument(
        "--eval-cases",
        type=Path,
        default=Path(os.getenv("NOVARON_EVAL_PATH", str(root / "benchmarks" / "eval_cases.jsonl"))),
        help="Path to JSONL eval cases file.",
    )
    parser.add_argument(
        "--index-dir",
        type=Path,
        default=Path(os.getenv("VECTOR_INDEX_DIR", "data/indexes")),
        help="Parent directory containing strategy-specific FAISS indexes.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(os.getenv("BENCHMARK_OUTPUT", str(root / "benchmarks" / "results" / "v03_results.json"))),
        help="Path to write machine-readable benchmark JSON output.",
    )
    parser.add_argument("--limit", type=int, default=3, help="Number of retrieved candidates to evaluate.")
    return parser.parse_args()


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
    return {
        "p50": round(statistics.median(values), 3),
        "p70": round(percentile(values, 0.70), 3),
        "p95": round(percentile(values, 0.95), 3),
        "p100": round(max(values), 3),
    } if values else {}


def evaluate(retriever, cases: list[dict[str, Any]], reranker=None, limit: int = 3) -> dict[str, Any]:
    # Warm up retriever / embedder once before timing to exclude lazy model download/initialization
    try:
        if hasattr(retriever, "search_with_profile"):
            retriever.search_with_profile("warmup query", 1)
        else:
            retriever.search("warmup query", 1)
    except Exception:
        pass

    languages: dict[str, dict[str, list[float]]] = {}
    overall: dict[str, list[float]] = {"recall": [], "mrr": [], "total": []}

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
        recall_val = float(bool(ranks))
        mrr_val = 1.0 / ranks[0] if ranks else 0.0

        metrics["recall"].append(recall_val)
        metrics["mrr"].append(mrr_val)
        metrics["total"].append(profile["total_retrieval"])

        overall["recall"].append(recall_val)
        overall["mrr"].append(mrr_val)
        overall["total"].append(profile["total_retrieval"])

        for stage, elapsed in profile.items():
            metrics.setdefault(stage, []).append(elapsed)
            overall.setdefault(stage, []).append(elapsed)

    results = {
        language: {
            "recall_at_3": round(sum(values["recall"]) / len(values["recall"]), 3),
            "mrr_at_3": round(sum(values["mrr"]) / len(values["mrr"]), 3),
            "query_count": len(values["recall"]),
            "latency_ms": {
                stage: latency_summary(timings)
                for stage, timings in values.items()
                if stage not in {"recall", "mrr", "total"}
            },
        }
        for language, values in languages.items()
    }

    if overall["recall"]:
        results["overall"] = {
            "recall_at_3": round(sum(overall["recall"]) / len(overall["recall"]), 3),
            "mrr_at_3": round(sum(overall["mrr"]) / len(overall["mrr"]), 3),
            "query_count": len(overall["recall"]),
            "latency_ms": {
                stage: latency_summary(timings)
                for stage, timings in overall.items()
                if stage not in {"recall", "mrr", "total"}
            },
        }

    return results


def print_method(method: str, value: dict[str, Any]) -> None:
    if value.get("status") == "unavailable":
        print(f"  {method}: unavailable — {value['reason']}")
        return
    for language, metrics in value["languages"].items():
        total = metrics["latency_ms"]["total_retrieval"]
        print(
            f"  {method:<28} lang={language:<7} (n={metrics['query_count']:>3}) "
            f"Recall@3={metrics['recall_at_3']:.3f} MRR@3={metrics['mrr_at_3']:.3f} "
            f"p50={total['p50']:.3f}ms p70={total['p70']:.3f}ms p95={total['p95']:.3f}ms p100={total['p100']:.3f}ms"
        )


def available(retriever, cases, reranker=None, limit: int = 3) -> dict[str, Any]:
    return {"status": "available", "languages": evaluate(retriever, cases, reranker, limit)}


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    corpus_path = args.corpus.resolve() if args.corpus.is_absolute() or args.corpus.exists() else (root / args.corpus).resolve()
    eval_path = args.eval_cases.resolve() if args.eval_cases.is_absolute() or args.eval_cases.exists() else (root / args.eval_cases).resolve()
    index_root = args.index_dir.resolve() if args.index_dir.is_absolute() or args.index_dir.exists() else (root / args.index_dir).resolve()

    corpus = load_jsonl(corpus_path)
    cases = load_cases(eval_path)
    strategies = (
        ("fixed", fixed_chunks(corpus)),
        ("sentence", sentence_chunks(corpus)),
        ("hierarchical", hierarchical_chunks(corpus)),
    )
    report: dict[str, Any] = {
        "version": "v0.3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "corpus": str(corpus_path),
        "evaluation": str(eval_path),
        "case_count": len(cases),
        "results": {},
    }
    print(f"Benchmark cases: {len(cases)} | corpus: {corpus_path}")
    for strategy, chunks in strategies:
        print(f"\nStrategy: {strategy} | chunks: {len(chunks)}")
        hashing = HashingDenseRetriever(chunks, HashingEmbedder())
        bm25 = BM25Retriever(chunks)
        hybrid = HybridRetriever(hashing, bm25)
        methods: dict[str, dict[str, Any]] = {
            "hashing_dense": available(hashing, cases, limit=args.limit),
            "bm25": available(bm25, cases, limit=args.limit),
            "hybrid_rrf": available(hybrid, cases, limit=args.limit),
            "hybrid_transparent_reranker": available(hybrid, cases, TransparentReranker(), limit=args.limit),
        }
        index_dir = index_root / strategy
        if not FaissVectorStore.exists(index_dir):
            methods["faiss_dense"] = {"status": "unavailable", "reason": f"Index not found: {index_dir}"}
        else:
            try:
                embedder = SentenceTransformerEmbeddingProvider()
                store = FaissVectorStore.load(
                    index_dir,
                    expected_model=embedder.model_name,
                    expected_strategy=strategy,
                    expected_normalized=True,
                )
                faiss_dense = FAISSDenseRetriever(store, embedder)
                methods["faiss_dense"] = available(faiss_dense, cases, limit=args.limit)
            except (VectorStoreError, RuntimeError) as exc:
                methods["faiss_dense"] = {"status": "unavailable", "reason": str(exc)}
        if os.getenv("BENCHMARK_CROSS_ENCODER", "0") == "1":
            try:
                methods["hybrid_cross_encoder"] = available(hybrid, cases, CrossEncoderReranker(), limit=args.limit)
            except RuntimeError as exc:
                methods["hybrid_cross_encoder"] = {"status": "unavailable", "reason": str(exc)}
        else:
            methods["hybrid_cross_encoder"] = {
                "status": "unavailable",
                "reason": "Set BENCHMARK_CROSS_ENCODER=1 after the reranker smoke test.",
            }
        report["results"][strategy] = methods
        for name, result in methods.items():
            print_method(name, result)

    output = args.output.resolve() if args.output.is_absolute() or args.output.parent.exists() else (root / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote machine-readable results: {output}")


if __name__ == "__main__":
    main()
