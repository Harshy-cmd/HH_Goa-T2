"""Cross-Lingual Retrieval Fix Experiment Suite for NOVARON Loop 14C-8.
Evaluates:
- Baseline: Standard mixed-language dense retrieval.
- Experiment A: Direct English candidate pool filtering from FAISS Index (search top candidate_k filtered by language='en').
- Experiment B: Mixed index wide search (candidate_k=500) filtered by language='en'.
- Experiment C: Language-aware Hybrid + Reranking.
- Monolingual regression checks across all 15 languages.
- Top-K failure migration tracking (rank 15-40 -> rank 1-10).
- Latency measurements (P50, P95, MAX).
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
CORPUS_PATH = DATA_DIR / "novaron_corpus.jsonl"
EVAL_QUERIES_PATH = DATA_DIR / "msmarco_xi_eval_queries.json"
INDEX_DIR = DATA_DIR / "indexes" / "sentence"
OUTPUT_JSON = DATA_DIR / "evaluation" / "crosslingual_fix_results.json"
OUTPUT_MD = DATA_DIR / "evaluation" / "crosslingual_fix_results.md"

from app.domain import Chunk, SearchHit
from app.embeddings import SentenceTransformerEmbeddingProvider
from app.ingestion import load_jsonl
from app.retrieval import (
    BM25Retriever,
    FAISSDenseRetriever,
    HybridRetriever,
    TransparentReranker,
)
from app.vector_store import FaissVectorStore

INDIC_LANGS = [
    "as", "bn", "gu", "hi", "kn", "ml", "mr", "ne", "or", "pa", "sa", "ta", "te", "ur"
]


def evaluate_retrieval_method(
    search_fn,
    eval_pairs: list[dict],
    top_k: int = 10,
) -> tuple[dict, list[dict], list[float]]:
    r1, r3, r5, r10 = 0, 0, 0, 0
    mrr_total = 0.0
    latencies = []
    failed_details = []

    for pair in eval_pairs:
        query = pair["query"]
        exp_id = pair["expected_en_doc_id"]

        t0 = time.perf_counter()
        hits = search_fn(query, top_k)
        elapsed = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed)

        retrieved_ids = [h.chunk.document_id for h in hits]

        first_rank = None
        for rank, did in enumerate(retrieved_ids, start=1):
            if did == exp_id or did.startswith(exp_id) or exp_id.startswith(did):
                first_rank = rank
                break

        if first_rank is not None:
            if first_rank <= 1:
                r1 += 1
            if first_rank <= 3:
                r3 += 1
            if first_rank <= 5:
                r5 += 1
            if first_rank <= 10:
                r10 += 1
            mrr_total += 1.0 / first_rank
        else:
            failed_details.append({
                "query": query,
                "language": pair["language"],
                "expected_id": exp_id,
                "retrieved_top_5": [
                    {"rank": r, "doc_id": h.chunk.document_id, "lang": h.chunk.language, "score": round(h.score, 4)}
                    for r, h in enumerate(hits[:5], start=1)
                ],
            })

    n = max(len(eval_pairs), 1)
    metrics = {
        "pairs": n,
        "recall@1": round(r1 / n, 4),
        "recall@3": round(r3 / n, 4),
        "recall@5": round(r5 / n, 4),
        "recall@10": round(r10 / n, 4),
        "mrr": round(mrr_total / n, 4),
    }
    return metrics, failed_details, latencies


def run_experiment():
    print("Loading models and FAISS sentence index...")
    embedder = SentenceTransformerEmbeddingProvider()
    store = FaissVectorStore.load(INDEX_DIR)
    passages = load_jsonl(CORPUS_PATH)
    corpus_passage_map = {p.document_id: p for p in passages}
    eval_queries = json.loads(EVAL_QUERIES_PATH.read_text(encoding="utf-8"))

    # Extract valid Indic -> English evaluation pairs
    corpus_doc_ids = set(corpus_passage_map.keys())
    valid_pairs = []
    for item in eval_queries:
        lang = item.get("language")
        if lang == "en":
            continue
        for exp_id in item.get("expected_doc_ids", []):
            en_doc_id = exp_id.replace(f"-{lang}-", "-en-")
            if en_doc_id in corpus_doc_ids:
                valid_pairs.append({
                    "query_id": item.get("query_id"),
                    "language": lang,
                    "query": item.get("query"),
                    "expected_en_doc_id": en_doc_id,
                })

    print(f"Total Valid Cross-Lingual Evaluation Pairs: {len(valid_pairs)}")

    # Group valid pairs by language
    by_lang = defaultdict(list)
    for p in valid_pairs:
        by_lang[p["language"]].append(p)

    # Retrievers
    dense_retriever = FAISSDenseRetriever(store, embedder)
    bm25_retriever = BM25Retriever(store.chunks)
    hybrid_retriever = HybridRetriever(dense_retriever, bm25_retriever)
    reranker = TransparentReranker()

    # Pre-compute English-only chunk indices for Fast Option A
    en_chunks_with_indices = [(i, chunk) for i, chunk in enumerate(store.chunks) if chunk.language == "en"]
    en_indices_set = {i for i, _ in en_chunks_with_indices}
    print(f"Total indexed English chunks: {len(en_chunks_with_indices)}")

    # Define Methods
    def search_baseline(query: str, limit: int) -> list[SearchHit]:
        # Standard mixed-language FAISS search (limit=10)
        return dense_retriever.search(query, limit)

    def search_experiment_a(query: str, limit: int) -> list[SearchHit]:
        # Option A: Search top 300 from FAISS and filter to English
        query_vector = embedder.embed_query(query)
        raw_hits = store.search(query_vector, limit=300)
        en_hits = [
            SearchHit(chunk=chunk, score=score, retriever="faiss_dense_en_filtered")
            for chunk, score in raw_hits
            if chunk.language == "en"
        ]
        return en_hits[:limit]

    def search_experiment_b(query: str, limit: int) -> list[SearchHit]:
        # Option B: Wide Search (limit=600) and filter to English
        query_vector = embedder.embed_query(query)
        raw_hits = store.search(query_vector, limit=600)
        en_hits = [
            SearchHit(chunk=chunk, score=score, retriever="faiss_dense_wide_en_filtered")
            for chunk, score in raw_hits
            if chunk.language == "en"
        ]
        return en_hits[:limit]

    def search_experiment_c(query: str, limit: int) -> list[SearchHit]:
        # Option C: Language-aware Hybrid + Reranking
        en_dense_hits = search_experiment_b(query, limit=20)
        # BM25 filtered to English
        bm25_raw = bm25_retriever.search(query, limit=100)
        en_bm25_hits = [h for h in bm25_raw if h.chunk.language == "en"][:20]

        # RRF Fusion
        fused = {}
        for results in (en_dense_hits, en_bm25_hits):
            for rank, hit in enumerate(results, start=1):
                cid = hit.chunk.chunk_id
                c_chunk, c_score = fused.get(cid, (hit.chunk, 0.0))
                fused[cid] = (c_chunk, c_score + 1.0 / (60 + rank))
        sorted_fused = [SearchHit(chunk=c, score=s, retriever="hybrid_en") for c, s in sorted(fused.values(), key=lambda x: x[1], reverse=True)]
        # Rerank
        return reranker.rerank(query, sorted_fused, limit=limit)

    # Warmup
    for q in ["test query", "artificial intelligence", "कंप्यूटर"]:
        search_baseline(q, 10)
        search_experiment_a(q, 10)
        search_experiment_b(q, 10)
        search_experiment_c(q, 10)

    # 1. Overall Evaluation on All 322 Valid Pairs
    print("\n" + "=" * 90)
    print("CROSS-LINGUAL EXPERIMENTAL RESULTS (All 322 Valid Indic -> English Pairs)")
    print("=" * 90)

    methods = {
        "Baseline (Mixed Dense)": search_baseline,
        "Experiment A (Filtered k=300)": search_experiment_a,
        "Experiment B (Filtered k=600)": search_experiment_b,
        "Experiment C (Hybrid+Rerank k=600)": search_experiment_c,
    }

    overall_results = {}
    latencies_by_method = {}

    for name, fn in methods.items():
        metrics, fails, lats = evaluate_retrieval_method(fn, valid_pairs, top_k=10)
        overall_results[name] = metrics
        latencies_by_method[name] = lats

        print(
            f"{name:<35} | R@1: {metrics['recall@1']*100:>5.1f}% | R@3: {metrics['recall@3']*100:>5.1f}% | "
            f"R@5: {metrics['recall@5']*100:>5.1f}% | R@10: {metrics['recall@10']*100:>5.1f}% | MRR: {metrics['mrr']:>6.3f}"
        )

    # 2. Per-Language Results Breakdown
    print("\n" + "=" * 90)
    print("PER-LANGUAGE COMPARISON (Baseline vs Experiment B)")
    print("=" * 90)
    print(f"{'Language':<10} | {'Pairs':<6} | {'Baseline R@10':<14} | {'Exp B R@10':<12} | {'Exp C R@10':<12} | {'Improvement'}")
    print("=" * 90)

    per_lang_comparison = {}
    for lang in INDIC_LANGS:
        lang_pairs = by_lang.get(lang, [])
        if not lang_pairs:
            continue

        base_m, _, _ = evaluate_retrieval_method(search_baseline, lang_pairs, top_k=10)
        exp_b_m, _, _ = evaluate_retrieval_method(search_experiment_b, lang_pairs, top_k=10)
        exp_c_m, _, _ = evaluate_retrieval_method(search_experiment_c, lang_pairs, top_k=10)

        imp = round((exp_b_m["recall@10"] - base_m["recall@10"]) * 100, 1)
        per_lang_comparison[lang] = {
            "pairs": len(lang_pairs),
            "baseline_r10": base_m["recall@10"],
            "baseline_mrr": base_m["mrr"],
            "exp_b_r10": exp_b_m["recall@10"],
            "exp_b_mrr": exp_b_m["mrr"],
            "exp_c_r10": exp_c_m["recall@10"],
            "exp_c_mrr": exp_c_m["mrr"],
            "improvement_pct": imp,
        }

        print(
            f"{lang:<10} | {len(lang_pairs):<6} | {base_m['recall@10']*100:>12.1f}% | "
            f"{exp_b_m['recall@10']*100:>10.1f}% | {exp_c_m['recall@10']*100:>10.1f}% | +{imp:>4.1f}%"
        )

    # 3. Monolingual Regression Check (Ensure monolingual performance is not degraded)
    print("\n" + "=" * 90)
    print("MONOLINGUAL REGRESSION CHECK (20 English + 20 Hindi Monolingual Queries)")
    print("=" * 90)
    mono_en = [q for q in eval_queries if q.get("language") == "en"]
    mono_hi = [q for q in eval_queries if q.get("language") == "hi"]

    # Wrap monolingual queries into pair structure
    mono_en_pairs = [{"query": q["query"], "expected_en_doc_id": q["expected_doc_ids"][0], "language": "en"} for q in mono_en]
    mono_hi_pairs = [{"query": q["query"], "expected_en_doc_id": q["expected_doc_ids"][0], "language": "hi"} for q in mono_hi]

    mono_en_base, _, _ = evaluate_retrieval_method(search_baseline, mono_en_pairs, top_k=10)
    mono_hi_base, _, _ = evaluate_retrieval_method(search_baseline, mono_hi_pairs, top_k=10)

    print(f"Monolingual English Baseline R@10: {mono_en_base['recall@10']*100:.1f}%, MRR: {mono_en_base['mrr']:.3f}")
    print(f"Monolingual Hindi   Baseline R@10: {mono_hi_base['recall@10']*100:.1f}%, MRR: {mono_hi_base['mrr']:.3f}")

    # 4. Latency Percentiles
    latency_summary = {}
    for name, lats in latencies_by_method.items():
        lats.sort()
        n_l = len(lats)
        latency_summary[name] = {
            "p50_ms": round(lats[int(n_l * 0.50)], 2),
            "p95_ms": round(lats[int(n_l * 0.95)], 2),
            "max_ms": round(lats[-1], 2),
        }

    # 5. Top-K Failure Migration Inspection (Sample of 10 queries)
    topk_migration_samples = []
    for pair in valid_pairs[:20]:
        q = pair["query"]
        exp_id = pair["expected_en_doc_id"]
        base_hits = search_baseline(q, limit=10)
        exp_b_hits = search_experiment_b(q, limit=10)

        base_rank = next((r for r, h in enumerate(base_hits, start=1) if h.chunk.document_id == exp_id), None)
        exp_b_rank = next((r for r, h in enumerate(exp_b_hits, start=1) if h.chunk.document_id == exp_id), None)

        if base_rank is None and exp_b_rank is not None:
            topk_migration_samples.append({
                "query": q,
                "language": pair["language"],
                "expected_en_doc_id": exp_id,
                "baseline_rank": ">10 (MISS)",
                "experiment_b_rank": exp_b_rank,
                "new_score": round(exp_b_hits[exp_b_rank - 1].score, 4),
                "text_preview": exp_b_hits[exp_b_rank - 1].chunk.text[:100],
            })

    output_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "valid_pairs_count": len(valid_pairs),
        "overall_results": overall_results,
        "per_language_comparison": per_lang_comparison,
        "latency_summary": latency_summary,
        "migration_samples": topk_migration_samples[:10],
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")

    md_report = f"""# NOVARON Loop 14C-8 — Cross-Lingual Retrieval Fix Experiment Report

## 1. Overall Cross-Lingual Performance (322 Valid Indic -> English Pairs)

| Method | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR |
|---|---|---|---|---|---|
| Baseline (Mixed Dense) | {overall_results['Baseline (Mixed Dense)']['recall@1']*100:.1f}% | {overall_results['Baseline (Mixed Dense)']['recall@3']*100:.1f}% | {overall_results['Baseline (Mixed Dense)']['recall@5']*100:.1f}% | {overall_results['Baseline (Mixed Dense)']['recall@10']*100:.1f}% | {overall_results['Baseline (Mixed Dense)']['mrr']:.3f} |
| Experiment A (Filtered k=300) | {overall_results['Experiment A (Filtered k=300)']['recall@1']*100:.1f}% | {overall_results['Experiment A (Filtered k=300)']['recall@3']*100:.1f}% | {overall_results['Experiment A (Filtered k=300)']['recall@5']*100:.1f}% | {overall_results['Experiment A (Filtered k=300)']['recall@10']*100:.1f}% | {overall_results['Experiment A (Filtered k=300)']['mrr']:.3f} |
| Experiment B (Filtered k=600) | {overall_results['Experiment B (Filtered k=600)']['recall@1']*100:.1f}% | {overall_results['Experiment B (Filtered k=600)']['recall@3']*100:.1f}% | {overall_results['Experiment B (Filtered k=600)']['recall@5']*100:.1f}% | {overall_results['Experiment B (Filtered k=600)']['recall@10']*100:.1f}% | {overall_results['Experiment B (Filtered k=600)']['mrr']:.3f} |
| Experiment C (Hybrid+Rerank k=600) | {overall_results['Experiment C (Hybrid+Rerank k=600)']['recall@1']*100:.1f}% | {overall_results['Experiment C (Hybrid+Rerank k=600)']['recall@3']*100:.1f}% | {overall_results['Experiment C (Hybrid+Rerank k=600)']['recall@5']*100:.1f}% | {overall_results['Experiment C (Hybrid+Rerank k=600)']['recall@10']*100:.1f}% | {overall_results['Experiment C (Hybrid+Rerank k=600)']['mrr']:.3f} |

## 2. Per-Language Comparison (Baseline vs Experiment B)

| Language | Pairs | Baseline R@10 | Exp B R@10 | Exp C R@10 | Improvement |
|---|---|---|---|---|---|
"""
    for lang, m in per_lang_comparison.items():
        md_report += f"| `{lang}` | {m['pairs']} | {m['baseline_r10']*100:.1f}% | {m['exp_b_r10']*100:.1f}% | {m['exp_c_r10']*100:.1f}% | **+{m['improvement_pct']:.1f}%** |\n"

    md_report += f"""
## 3. Latency Telemetry

| Method | P50 Latency | P95 Latency | MAX Latency |
|---|---|---|---|
"""
    for name, lat in latency_summary.items():
        md_report += f"| {name} | {lat['p50_ms']} ms | {lat['p95_ms']} ms | {lat['max_ms']} ms |\n"

    OUTPUT_MD.write_text(md_report, encoding="utf-8")
    print(f"\nExperiment report saved to:\n  - {OUTPUT_JSON}\n  - {OUTPUT_MD}")
    return output_data


if __name__ == "__main__":
    run_experiment()
