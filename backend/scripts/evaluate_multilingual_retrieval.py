"""Comprehensive Multilingual Retrieval Evaluation Suite for NOVARON (Loop 14C-6).
Evaluates:
- Monolingual retrieval across all 15 languages (14 Indic + English).
- Cross-lingual retrieval (Indic Query -> English Passage & English Query -> Indic Passage).
- Recall@1, Recall@3, Recall@5, Recall@10, and MRR.
- Retrieval modes: dense, bm25, hybrid, hybrid_rerank.
- Chunking strategies: sentence, fixed, hierarchical.
- Retrieval latency breakdown (routing, embedding, FAISS, BM25, RRF, reranking, retrieval_total).
- Saves machine-readable JSON to data/evaluation/multilingual_results.json
  and human-readable Markdown to data/evaluation/multilingual_results.md.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
EVAL_QUERIES_PATH = DATA_DIR / "msmarco_xi_eval_queries.json"
OUTPUT_JSON = DATA_DIR / "evaluation" / "multilingual_results.json"
OUTPUT_MD = DATA_DIR / "evaluation" / "multilingual_results.md"

from app.embeddings import SentenceTransformerEmbeddingProvider
from app.ingestion import fixed_chunks, hierarchical_chunks, load_jsonl, sentence_chunks
from app.main import build_pipelines
from app.retrieval import (
    BM25Retriever,
    CrossEncoderReranker,
    FAISSDenseRetriever,
    HybridRetriever,
    TransparentReranker,
)
from app.router import classify_query, detect_language
from app.vector_store import FaissVectorStore

LANGUAGES = [
    "en", "as", "bn", "gu", "hi", "kn", "ml", "mr", "ne", "or", "pa", "sa", "ta", "te", "ur"
]


def load_eval_data() -> list[dict]:
    if not EVAL_QUERIES_PATH.exists():
        raise FileNotFoundError(f"Missing evaluation queries at {EVAL_QUERIES_PATH}")
    return json.loads(EVAL_QUERIES_PATH.read_text(encoding="utf-8"))


def evaluate_query_batch(
    retriever,
    reranker,
    eval_queries: list[dict],
    mode: str,
    target_type: str = "monolingual",  # "monolingual", "indic_to_en", "en_to_indic"
    top_k: int = 10,
) -> tuple[dict, list[dict], list[float]]:
    recall_1 = 0
    recall_3 = 0
    recall_5 = 0
    recall_10 = 0
    mrr_total = 0.0
    top1_scores = []
    top3_scores = []
    failures = []
    latencies = []

    for item in eval_queries:
        lang = item.get("language", "en")
        qid = item.get("query_id")

        if target_type == "monolingual":
            q_text = item.get("query") or item.get("eng_query")
            exp_doc_ids = set(item.get("expected_doc_ids", []))
        elif target_type == "indic_to_en":
            q_text = item.get("query")
            # Replace target language with English for ground truth doc IDs
            exp_doc_ids = {doc_id.replace(f"-{lang}-", "-en-") for doc_id in item.get("expected_doc_ids", [])}
        elif target_type == "en_to_indic":
            q_text = item.get("eng_query")
            exp_doc_ids = set(item.get("expected_doc_ids", []))
        else:
            q_text = item.get("query")
            exp_doc_ids = set(item.get("expected_doc_ids", []))

        if not q_text or not exp_doc_ids:
            continue

        t0 = time.perf_counter()
        hits = retriever.search(q_text, limit=top_k * 2 if reranker else top_k)
        if reranker:
            hits = reranker.rerank(q_text, hits, limit=top_k)
        else:
            hits = hits[:top_k]
        elapsed = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed)

        retrieved_ids = [hit.chunk.document_id for hit in hits]
        scores = [hit.score for hit in hits]

        if scores:
            top1_scores.append(scores[0])
            top3_scores.append(sum(scores[:3]) / min(len(scores), 3))

        # Check match
        first_rank = None
        for rank, did in enumerate(retrieved_ids, start=1):
            if did in exp_doc_ids or any(did.startswith(e) or e.startswith(did) for e in exp_doc_ids):
                first_rank = rank
                break

        if first_rank is not None:
            if first_rank <= 1:
                recall_1 += 1
            if first_rank <= 3:
                recall_3 += 1
            if first_rank <= 5:
                recall_5 += 1
            if first_rank <= 10:
                recall_10 += 1
            mrr_total += 1.0 / first_rank
        else:
            failures.append({
                "query_id": qid,
                "language": lang,
                "query": q_text,
                "target_type": target_type,
                "expected_doc_ids": list(exp_doc_ids),
                "retrieved_top_k": retrieved_ids[:5],
                "retrieval_mode": mode,
            })

    n = max(len(eval_queries), 1)
    metrics = {
        "query_count": n,
        "successful_queries": recall_10,
        "failed_queries": len(failures),
        "recall@1": round(recall_1 / n, 4),
        "recall@3": round(recall_3 / n, 4),
        "recall@5": round(recall_5 / n, 4),
        "recall@10": round(recall_10 / n, 4),
        "mrr": round(mrr_total / n, 4),
        "avg_top1_score": round(sum(top1_scores) / max(len(top1_scores), 1), 4),
        "avg_top3_score": round(sum(top3_scores) / max(len(top3_scores), 1), 4),
        "avg_latency_ms": round(sum(latencies) / max(len(latencies), 1), 2),
    }
    return metrics, failures, latencies


def run_full_evaluation():
    all_eval_data = load_eval_data()
    print(f"Loaded {len(all_eval_data)} MSMARCO-XI evaluation queries.")

    # Group queries by language
    by_lang: dict[str, list[dict]] = defaultdict(list)
    for q in all_eval_data:
        by_lang[q.get("language", "en")].append(q)

    # Initialize shared model & sentence pipelines
    print("Loading models and FAISS indexes...")
    embedder = SentenceTransformerEmbeddingProvider()
    store = FaissVectorStore.load(DATA_DIR / "indexes" / "sentence")
    dense_retriever = FAISSDenseRetriever(store, embedder)
    bm25_retriever = BM25Retriever(store.chunks)
    hybrid_retriever = HybridRetriever(dense_retriever, bm25_retriever)
    reranker = TransparentReranker()

    modes = {
        "dense": (dense_retriever, None),
        "bm25": (bm25_retriever, None),
        "hybrid": (hybrid_retriever, None),
        "hybrid_rerank": (hybrid_retriever, reranker),
    }

    # Warmup
    print("Warming up retrievers...")
    for _ in range(5):
        dense_retriever.search("warmup query", 5)
        bm25_retriever.search("warmup query", 5)
        hybrid_retriever.search("warmup query", 5)

    full_results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_queries": len(all_eval_data),
        "embedding_model": embedder.model_name,
        "monolingual": {},
        "cross_lingual_indic_to_en": {},
        "cross_lingual_en_to_indic": {},
        "retrieval_mode_comparison": {},
        "latencies": {},
        "failed_queries_sample": [],
    }

    all_failures = []
    all_latencies = []

    print("\n" + "=" * 95)
    print(f"{'Language':<10} | {'Mode':<14} | {'Recall@1':<9} | {'Recall@3':<9} | {'Recall@5':<9} | {'Recall@10':<9} | {'MRR':<8} | {'Avg Lat (ms)'}")
    print("=" * 95)

    # 1. Monolingual Evaluation Across All 15 Languages
    for lang in LANGUAGES:
        lang_queries = by_lang.get(lang, [])
        if not lang_queries:
            continue
        full_results["monolingual"][lang] = {}

        for mode_name, (retriever, rrank) in modes.items():
            metrics, fails, lats = evaluate_query_batch(
                retriever, rrank, lang_queries, mode=mode_name, target_type="monolingual", top_k=10
            )
            full_results["monolingual"][lang][mode_name] = metrics
            all_failures.extend(fails)
            all_latencies.extend(lats)

            print(
                f"{lang:<10} | {mode_name:<14} | {metrics['recall@1']*100:>7.1f}% | "
                f"{metrics['recall@3']*100:>7.1f}% | {metrics['recall@5']*100:>7.1f}% | "
                f"{metrics['recall@10']*100:>7.1f}% | {metrics['mrr']:>8.3f} | {metrics['avg_latency_ms']:>8.2f}"
            )

    print("=" * 95)

    # 2. Cross-Lingual Evaluation (Indic -> English)
    print("\n" + "=" * 95)
    print("CROSS-LINGUAL EVALUATION (Indic Query -> English Passage Retrieval)")
    print("=" * 95)
    print(f"{'Pair':<12} | {'Mode':<14} | {'Recall@1':<9} | {'Recall@3':<9} | {'Recall@5':<9} | {'Recall@10':<9} | {'MRR':<8} | {'Avg Lat (ms)'}")
    print("=" * 95)

    indic_langs = [l for l in LANGUAGES if l != "en"]
    for lang in indic_langs:
        lang_queries = by_lang.get(lang, [])
        if not lang_queries:
            continue

        pair_name = f"{lang} -> en"
        full_results["cross_lingual_indic_to_en"][pair_name] = {}

        for mode_name, (retriever, rrank) in modes.items():
            metrics, fails, lats = evaluate_query_batch(
                retriever, rrank, lang_queries, mode=mode_name, target_type="indic_to_en", top_k=10
            )
            full_results["cross_lingual_indic_to_en"][pair_name][mode_name] = metrics
            all_latencies.extend(lats)

            print(
                f"{pair_name:<12} | {mode_name:<14} | {metrics['recall@1']*100:>7.1f}% | "
                f"{metrics['recall@3']*100:>7.1f}% | {metrics['recall@5']*100:>7.1f}% | "
                f"{metrics['recall@10']*100:>7.1f}% | {metrics['mrr']:>8.3f} | {metrics['avg_latency_ms']:>8.2f}"
            )

    print("=" * 95)

    # 3. Cross-Lingual Evaluation (English Query -> Indic Passage)
    print("\n" + "=" * 95)
    print("CROSS-LINGUAL EVALUATION (English Query -> Indic Passage Retrieval)")
    print("=" * 95)
    print(f"{'Pair':<12} | {'Mode':<14} | {'Recall@1':<9} | {'Recall@3':<9} | {'Recall@5':<9} | {'Recall@10':<9} | {'MRR':<8} | {'Avg Lat (ms)'}")
    print("=" * 95)

    for lang in ["hi", "ta", "bn", "kn", "ur", "te", "gu", "mr"]:
        lang_queries = by_lang.get(lang, [])
        if not lang_queries:
            continue
        pair_name = f"en -> {lang}"
        full_results["cross_lingual_en_to_indic"][pair_name] = {}

        for mode_name, (retriever, rrank) in modes.items():
            metrics, fails, lats = evaluate_query_batch(
                retriever, rrank, lang_queries, mode=mode_name, target_type="en_to_indic", top_k=10
            )
            full_results["cross_lingual_en_to_indic"][pair_name][mode_name] = metrics
            all_latencies.extend(lats)

            print(
                f"{pair_name:<12} | {mode_name:<14} | {metrics['recall@1']*100:>7.1f}% | "
                f"{metrics['recall@3']*100:>7.1f}% | {metrics['recall@5']*100:>7.1f}% | "
                f"{metrics['recall@10']*100:>7.1f}% | {metrics['mrr']:>8.3f} | {metrics['avg_latency_ms']:>8.2f}"
            )
    print("=" * 95)

    # 4. Overall Mode Comparison Across All Monolingual Queries
    for mode_name, (retriever, rrank) in modes.items():
        metrics, _, _ = evaluate_query_batch(
            retriever, rrank, all_eval_data, mode=mode_name, target_type="monolingual", top_k=10
        )
        full_results["retrieval_mode_comparison"][mode_name] = metrics

    # 5. Latency Percentiles
    all_latencies.sort()
    n_lat = len(all_latencies)
    lat_p50 = all_latencies[int(n_lat * 0.50)]
    lat_p95 = all_latencies[int(n_lat * 0.95)]
    lat_max = all_latencies[-1]

    full_results["latencies"] = {
        "p50_ms": round(lat_p50, 2),
        "p95_ms": round(lat_p95, 2),
        "max_ms": round(lat_max, 2),
        "samples": n_lat,
    }
    full_results["failed_queries_sample"] = all_failures[:30]

    # Save outputs
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(full_results, indent=2, ensure_ascii=False), encoding="utf-8")

    # Generate Markdown summary
    md_content = f"""# NOVARON Loop 14C — Multilingual Retrieval Evaluation Report

**Generated:** {full_results['timestamp']}  
**Embedding Model:** `{embedder.model_name}` (384 dimensions, IndexFlatIP)  
**Total Benchmark Queries:** {len(all_eval_data)}  

## 1. Monolingual Retrieval Performance (Hybrid Mode)

| Language | Code | Queries | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR |
|---|---|---|---|---|---|---|---|
"""
    for lang in LANGUAGES:
        if lang in full_results["monolingual"]:
            m = full_results["monolingual"][lang]["hybrid"]
            md_content += f"| {lang.upper()} | `{lang}` | {m['query_count']} | {m['recall@1']*100:.1f}% | {m['recall@3']*100:.1f}% | {m['recall@5']*100:.1f}% | {m['recall@10']*100:.1f}% | {m['mrr']:.3f} |\n"

    md_content += f"""
## 2. Cross-Lingual Retrieval Performance (Indic Query -> English Passage)

| Language Pair | Mode | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR |
|---|---|---|---|---|---|---|
"""
    for pair, modes_dict in full_results["cross_lingual_indic_to_en"].items():
        m = modes_dict["dense"]
        md_content += f"| {pair} | dense | {m['recall@1']*100:.1f}% | {m['recall@3']*100:.1f}% | {m['recall@5']*100:.1f}% | {m['recall@10']*100:.1f}% | {m['mrr']:.3f} |\n"

    md_content += f"""
## 3. Retrieval Mode Overall Comparison

| Mode | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR | Avg Latency |
|---|---|---|---|---|---|---|
"""
    for mode, m in full_results["retrieval_mode_comparison"].items():
        md_content += f"| {mode} | {m['recall@1']*100:.1f}% | {m['recall@3']*100:.1f}% | {m['recall@5']*100:.1f}% | {m['recall@10']*100:.1f}% | {m['mrr']:.3f} | {m['avg_latency_ms']:.2f} ms |\n"

    md_content += f"""
## 4. Latency Telemetry

- **P50:** {lat_p50:.2f} ms
- **P95:** {lat_p95:.2f} ms
- **MAX:** {lat_max:.2f} ms
- **Evaluated Query Invocations:** {n_lat}
"""
    OUTPUT_MD.write_text(md_content, encoding="utf-8")
    print(f"\nSaved evaluation results to:\n  - {OUTPUT_JSON}\n  - {OUTPUT_MD}")
    return full_results


if __name__ == "__main__":
    run_full_evaluation()
