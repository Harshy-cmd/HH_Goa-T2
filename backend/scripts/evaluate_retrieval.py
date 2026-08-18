"""Comprehensive Multi-Domain Retrieval Evaluation Suite for NOVARON (Loop 14).
Evaluates Recall@1, Recall@3, Recall@5, Recall@10, MRR, Domain Accuracy@1, and Topic Accuracy@3
across dense, BM25, hybrid, and hybrid_rerank pipelines.
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.ingestion import load_jsonl, sentence_chunks
from app.main import build_pipelines

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "novaron_corpus.jsonl"


@dataclass
class EvalQuery:
    query: str
    expected_domain: str
    expected_topic: str
    expected_doc_ids: list[str]
    language: str = "en"


BENCHMARK_QUERIES: list[EvalQuery] = [
    # NOVARON System
    EvalQuery("What is NOVARON?", "novaron_system", "architecture", ["novaron-sys-overview", "hindi-novaron-sys"]),
    EvalQuery("How does NOVARON voice pipeline work?", "novaron_system", "voice", ["novaron-sys-voice-pipeline"]),
    EvalQuery("Explain NOVARON hybrid retrieval", "novaron_system", "retrieval", ["novaron-sys-retrieval-hybrid"]),
    EvalQuery("What embedding model does NOVARON use?", "novaron_system", "embeddings", ["novaron-sys-embeddings"]),
    EvalQuery("How does NOVARON prevent hallucinations?", "novaron_system", "grounding", ["novaron-sys-grounding-guardrail"]),
    EvalQuery("How does citation validation work in NOVARON?", "novaron_system", "citations", ["novaron-sys-citation-validation"]),
    EvalQuery("What is the NOVARON deterministic query router?", "novaron_system", "router", ["novaron-sys-query-router"]),
    EvalQuery("What frontend components does NOVARON have?", "novaron_system", "frontend", ["novaron-sys-frontend-ui"]),

    # Computer Science - Programming & Data Structures
    EvalQuery("What is Python programming language?", "computer_science", "programming", ["tech-lang-python", "hindi-tech-python"]),
    EvalQuery("Explain the C programming language", "computer_science", "programming", ["tech-lang-c"]),
    EvalQuery("What is TypeScript?", "computer_science", "programming", ["tech-lang-typescript"]),
    EvalQuery("What is Rust memory safety and ownership?", "computer_science", "programming", ["tech-lang-rust"]),
    EvalQuery("What is an array data structure?", "computer_science", "data_structures", ["tech-ds-array"]),
    EvalQuery("How does a linked list work?", "computer_science", "data_structures", ["tech-ds-linked-list"]),
    EvalQuery("What is a hash table and how are collisions resolved?", "computer_science", "data_structures", ["tech-ds-hash-table"]),
    EvalQuery("What is a binary search tree?", "computer_science", "data_structures", ["tech-ds-binary-tree"]),
    EvalQuery("Explain binary heaps and priority queues", "computer_science", "data_structures", ["tech-ds-heap"]),
    EvalQuery("What is a trie or prefix tree?", "computer_science", "data_structures", ["tech-ds-trie"]),

    # Computer Science - Algorithms, OOP, DB, OS, Net
    EvalQuery("What is Big-O notation?", "computer_science", "algorithms", ["tech-algo-big-o"]),
    EvalQuery("How does quicksort and mergesort work?", "computer_science", "algorithms", ["tech-algo-sorting"]),
    EvalQuery("Explain binary search algorithm", "computer_science", "algorithms", ["tech-algo-binary-search"]),
    EvalQuery("What is recursion in computer science?", "computer_science", "algorithms", ["tech-algo-recursion"]),
    EvalQuery("What is dynamic programming?", "computer_science", "algorithms", ["tech-algo-dp"]),
    EvalQuery("How does Dijkstra's algorithm find the shortest path?", "computer_science", "algorithms", ["tech-algo-dijkstra"]),
    EvalQuery("What are the four pillars of OOP?", "computer_science", "oop", ["tech-oop-principles"]),
    EvalQuery("What are ACID transactions in databases?", "computer_science", "databases", ["tech-db-acid", "hindi-tech-db"]),
    EvalQuery("What is database normalization and 3NF?", "computer_science", "databases", ["tech-db-normalization"]),
    EvalQuery("What is virtual memory and paging?", "computer_science", "operating_systems", ["tech-os-virtual-memory", "hindi-tech-os"]),
    EvalQuery("What are the conditions for deadlock in operating systems?", "computer_science", "operating_systems", ["tech-os-deadlocks"]),
    EvalQuery("What is the difference between TCP and UDP?", "computer_science", "networking", ["tech-net-tcpip"]),
    EvalQuery("What is RESTful API architecture?", "computer_science", "web_development", ["tech-net-rest"]),
    EvalQuery("What is FastAPI in Python?", "computer_science", "web_development", ["tech-web-fastapi"]),

    # AI / Machine Learning
    EvalQuery("What is artificial intelligence?", "ai_ml", "ai_foundations", ["ai-fundamentals", "hindi-tech-ai"]),
    EvalQuery("What is the difference between supervised and unsupervised learning?", "ai_ml", "machine_learning", ["ai-machine-learning", "hindi-tech-ml"]),
    EvalQuery("How does reinforcement learning work?", "ai_ml", "machine_learning", ["ai-reinforcement-learning"]),
    EvalQuery("What is a convolutional neural network (CNN)?", "ai_ml", "deep_learning", ["ai-cnn"]),
    EvalQuery("How does the Transformer self-attention mechanism work?", "ai_ml", "transformers", ["ai-transformers"]),
    EvalQuery("What are dense vector embeddings in NLP?", "ai_ml", "nlp", ["ai-nlp-embeddings"]),
    EvalQuery("What is FAISS vector search?", "ai_ml", "information_retrieval", ["ai-faiss", "hindi-tech-faiss"]),
    EvalQuery("What is BM25 lexical search?", "ai_ml", "information_retrieval", ["ai-bm25"]),
    EvalQuery("What is Reciprocal Rank Fusion (RRF)?", "ai_ml", "information_retrieval", ["ai-hybrid-rrf"]),
    EvalQuery("How does a cross-encoder reranker work?", "ai_ml", "information_retrieval", ["ai-reranking"]),
    EvalQuery("What is Retrieval-Augmented Generation (RAG)?", "ai_ml", "rag", ["ai-rag", "hindi-tech-rag"]),
    EvalQuery("How do RAG systems prevent hallucinations?", "ai_ml", "rag", ["ai-grounding-hallucinations", "novaron-sys-grounding-guardrail"]),
    EvalQuery("What is Whisper speech recognition?", "ai_ml", "speech", ["ai-speech-stt-tts"]),

    # General Science
    EvalQuery("What are Newton's three laws of motion?", "general_science", "physics", ["sci-phys-newton-laws"]),
    EvalQuery("What is gravity and Newton's universal gravitation?", "general_science", "physics", ["sci-phys-gravity", "hindi-science-gravity"]),
    EvalQuery("What are the laws of thermodynamics?", "general_science", "physics", ["sci-phys-thermodynamics"]),
    EvalQuery("What is the periodic table of elements?", "general_science", "chemistry", ["sci-chem-periodic-table"]),
    EvalQuery("What is the structure of an atom?", "general_science", "chemistry", ["sci-chem-atomic-structure"]),
    EvalQuery("What is DNA and genetics?", "general_science", "biology", ["sci-bio-dna-genetics", "hindi-science-dna"]),
    EvalQuery("What is photosynthesis?", "general_science", "biology", ["sci-bio-photosynthesis", "hindi-science-photosynthesis"]),
    EvalQuery("What is cellular respiration and ATP?", "general_science", "biology", ["sci-bio-cellular-respiration"]),
    EvalQuery("How does the water cycle work?", "general_science", "earth_science", ["sci-earth-water-cycle"]),
    EvalQuery("What planets are in the Solar System?", "general_science", "astronomy", ["sci-astro-solar-system", "hindi-science-solar-system"]),
    EvalQuery("What is a black hole and how is it formed?", "general_science", "astronomy", ["sci-astro-stellar-evolution"]),

    # Mathematics
    EvalQuery("What is a prime number and fundamental theorem of arithmetic?", "mathematics", "arithmetic", ["math-arithmetic-primes"]),
    EvalQuery("What is the Pythagorean theorem?", "mathematics", "geometry", ["math-geometry-euclidean"]),
    EvalQuery("What are trigonometric functions and sine cosine tangent?", "mathematics", "trigonometry", ["math-trigonometry"]),
    EvalQuery("What is a derivative in calculus?", "mathematics", "calculus", ["math-calculus-derivatives"]),
    EvalQuery("What is an integral and fundamental theorem of calculus?", "mathematics", "calculus", ["math-calculus-integrals"]),
    EvalQuery("What are matrices and eigenvalues in linear algebra?", "mathematics", "linear_algebra", ["math-linear-algebra-matrices"]),
    EvalQuery("What is Bayes' theorem in probability?", "mathematics", "probability_statistics", ["math-prob-stats"]),

    # General Knowledge
    EvalQuery("What are the seven continents and five oceans?", "general_knowledge", "geography", ["gk-geo-continents-oceans"]),
    EvalQuery("What is the law of supply and demand in economics?", "general_knowledge", "economics", ["gk-econ-fundamentals"]),
    EvalQuery("What is Gross Domestic Product (GDP) and inflation?", "general_knowledge", "economics", ["gk-econ-macroeconomics"]),
    EvalQuery("What was the Industrial Revolution?", "general_knowledge", "history", ["gk-hist-industrial-revolution"]),
    EvalQuery("What are the steps of the scientific method?", "general_knowledge", "science_method", ["gk-sci-scientific-method"]),

    # Multilingual Hindi
    EvalQuery("प्रकाश संश्लेषण क्या है?", "general_science", "biology", ["hindi-science-photosynthesis", "sci-bio-photosynthesis"], language="hi"),
    EvalQuery("गुरुत्वाकर्षण क्या है?", "general_science", "physics", ["hindi-science-gravity", "sci-phys-gravity"], language="hi"),
    EvalQuery("सौर मंडल में कौन से ग्रह हैं?", "general_science", "astronomy", ["hindi-science-solar-system", "sci-astro-solar-system"], language="hi"),
    EvalQuery("डीएनए क्या है?", "general_science", "biology", ["hindi-science-dna", "sci-bio-dna-genetics"], language="hi"),
    EvalQuery("कृत्रिम बुद्धिमत्ता क्या है?", "ai_ml", "ai_foundations", ["hindi-tech-ai", "ai-fundamentals"], language="hi"),
    EvalQuery("मशीन लर्निंग क्या है?", "ai_ml", "machine_learning", ["hindi-tech-ml", "ai-machine-learning"], language="hi"),
    EvalQuery("पायथन प्रोग्रामिंग क्या है?", "computer_science", "programming", ["hindi-tech-python", "tech-lang-python"], language="hi"),
    EvalQuery("FAISS क्या है?", "ai_ml", "information_retrieval", ["hindi-tech-faiss", "ai-faiss"], language="hi"),
    EvalQuery("RAG क्या है?", "ai_ml", "rag", ["hindi-tech-rag", "ai-rag"], language="hi"),
    EvalQuery("नोवारॉन क्या है?", "novaron_system", "architecture", ["hindi-novaron-sys", "novaron-sys-overview"], language="hi"),
]


def evaluate_pipeline(pipeline_name: str, pipeline, queries: list[EvalQuery], top_k: int = 10):
    recall_1 = 0
    recall_3 = 0
    recall_5 = 0
    recall_10 = 0
    mrr_sum = 0.0
    domain_acc_1 = 0
    topic_acc_3 = 0
    total = len(queries)
    latencies = []

    for eq in queries:
        t0 = time.perf_counter()
        if hasattr(pipeline.retriever, "search"):
            candidates = pipeline.retriever.search(eq.query, top_k)
        else:
            candidates = []
        if pipeline.reranker:
            hits = pipeline.reranker.rerank(eq.query, candidates, top_k)
        else:
            hits = candidates[:top_k]
        elapsed = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed)

        retrieved_doc_ids = [h.chunk.document_id for h in hits]

        # Domain & Topic accuracy
        if hits:
            # Check domain of top-1 hit
            top_hit = hits[0]
            # Domain accuracy check
            if getattr(top_hit.chunk, "domain", None) == eq.expected_domain or any(
                eq.expected_domain in (h.chunk.document_id or "") for h in hits[:1]
            ):
                domain_acc_1 += 1
            
            # Topic accuracy in top-3
            if any(
                getattr(h.chunk, "topic", None) == eq.expected_topic or any(doc_id in (h.chunk.document_id or "") for doc_id in eq.expected_doc_ids)
                for h in hits[:3]
            ):
                topic_acc_3 += 1

        # Recall@K check
        found_rank = None
        for rank, h in enumerate(hits, 1):
            if any(doc_id in (h.chunk.document_id or "") for doc_id in eq.expected_doc_ids):
                if found_rank is None:
                    found_rank = rank

        if found_rank is not None:
            if found_rank <= 1:
                recall_1 += 1
            if found_rank <= 3:
                recall_3 += 1
            if found_rank <= 5:
                recall_5 += 1
            if found_rank <= 10:
                recall_10 += 1
            mrr_sum += 1.0 / found_rank

    avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
    return {
        "pipeline": pipeline_name,
        "queries": total,
        "recall@1": recall_1 / total,
        "recall@3": recall_3 / total,
        "recall@5": recall_5 / total,
        "recall@10": recall_10 / total,
        "mrr": mrr_sum / total,
        "domain_acc@1": domain_acc_1 / total,
        "topic_acc@3": topic_acc_3 / total,
        "avg_retrieval_ms": avg_lat,
    }


def main():
    print("=" * 80)
    print("NOVARON LOOP 14 — MULTI-DOMAIN RETRIEVAL QUALITY EVALUATION")
    print(f"Total Benchmark Queries: {len(BENCHMARK_QUERIES)}")
    print("=" * 80)

    pipelines = build_pipelines()
    sentence_pipes = pipelines["sentence"]

    results = []
    for mode in ["dense", "bm25", "hybrid", "hybrid_rerank"]:
        pipe = sentence_pipes[mode]
        res = evaluate_pipeline(mode, pipe, BENCHMARK_QUERIES)
        results.append(res)

    print("\n" + "-" * 105)
    print(f"{'Retrieval Mode':<15} | {'Recall@1':<9} | {'Recall@3':<9} | {'Recall@5':<9} | {'Recall@10':<9} | {'MRR':<7} | {'Domain@1':<9} | {'Topic@3':<9} | {'Avg Latency':<10}")
    print("-" * 105)
    for r in results:
        print(
            f"{r['pipeline']:<15} | "
            f"{r['recall@1']:>8.1%} | "
            f"{r['recall@3']:>8.1%} | "
            f"{r['recall@5']:>8.1%} | "
            f"{r['recall@10']:>8.1%} | "
            f"{r['mrr']:>6.3f} | "
            f"{r['domain_acc@1']:>8.1%} | "
            f"{r['topic_acc@3']:>8.1%} | "
            f"{r['avg_retrieval_ms']:>8.2f}ms"
        )
    print("-" * 105)

    # Domain breakdown for best pipeline (hybrid)
    best_pipe = sentence_pipes["hybrid"]
    print("\n" + "=" * 80)
    print("DOMAIN-BY-DOMAIN BREAKDOWN (Hybrid Retrieval)")
    print("=" * 80)
    domains = sorted(set(q.expected_domain for q in BENCHMARK_QUERIES))
    for d in domains:
        d_queries = [q for q in BENCHMARK_QUERIES if q.expected_domain == d]
        d_res = evaluate_pipeline(d, best_pipe, d_queries)
        print(f"Domain: {d:<18} ({len(d_queries):>2} queries) -> Recall@1: {d_res['recall@1']:>6.1%} | Recall@3: {d_res['recall@3']:>6.1%} | Recall@5: {d_res['recall@5']:>6.1%} | MRR: {d_res['mrr']:>5.3f}")

    # Multilingual Hindi Breakdown
    hi_queries = [q for q in BENCHMARK_QUERIES if q.language == "hi"]
    hi_res = evaluate_pipeline("Hindi", best_pipe, hi_queries)
    print(f"\nLanguage: Hindi          ({len(hi_queries):>2} queries) -> Recall@1: {hi_res['recall@1']:>6.1%} | Recall@3: {hi_res['recall@3']:>6.1%} | Recall@5: {hi_res['recall@5']:>6.1%} | MRR: {hi_res['mrr']:>5.3f}")

    print("\nRETRIEVAL EVALUATION COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
