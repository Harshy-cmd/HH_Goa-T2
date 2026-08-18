"""Comprehensive Multi-Domain Retrieval Evaluation Suite for NOVARON (Loop 14B).
Evaluates Recall@1, Recall@3, Recall@5, Recall@10, MRR, Domain Accuracy@1, and Topic Accuracy@3
across dense, BM25, hybrid, and hybrid_rerank pipelines for 150 multi-domain benchmark queries.
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
    # --- 1. NOVARON SYSTEM (15 queries) ---
    EvalQuery("What is NOVARON?", "novaron_system", "architecture", ["novaron-sys-overview", "hindi-novaron-sys"]),
    EvalQuery("What is the mission of NOVARON?", "novaron_system", "architecture", ["novaron-sys-mission"]),
    EvalQuery("How does NOVARON voice pipeline work?", "novaron_system", "voice", ["novaron-sys-voice-pipeline"]),
    EvalQuery("What speech to text STT adapter is used?", "novaron_system", "voice", ["novaron-sys-stt-adapter"]),
    EvalQuery("How does text to speech TTS work in NOVARON?", "novaron_system", "voice", ["novaron-sys-tts-adapter"]),
    EvalQuery("Explain NOVARON hybrid retrieval architecture", "novaron_system", "retrieval", ["novaron-sys-retrieval-hybrid"]),
    EvalQuery("How does Reciprocal Rank Fusion RRF work in NOVARON?", "novaron_system", "retrieval", ["novaron-sys-rrf"]),
    EvalQuery("What embedding model does NOVARON use?", "novaron_system", "embeddings", ["novaron-sys-embeddings"]),
    EvalQuery("How does FAISS vector store persist indexes?", "novaron_system", "vector_store", ["novaron-sys-vector-store"]),
    EvalQuery("Explain the BM25 lexical retriever in NOVARON", "novaron_system", "retrieval", ["novaron-sys-bm25-retriever"]),
    EvalQuery("How does NOVARON prevent hallucinations?", "novaron_system", "grounding", ["novaron-sys-grounding-guardrail"]),
    EvalQuery("How does citation validation work in NOVARON?", "novaron_system", "citations", ["novaron-sys-citation-validation"]),
    EvalQuery("What is the NOVARON deterministic query router?", "novaron_system", "router", ["novaron-sys-query-router"]),
    EvalQuery("Explain VoiceOrb and audio visualizer in NOVARON", "novaron_system", "frontend", ["novaron-sys-frontend-voiceorb"]),
    EvalQuery("What latency telemetry does NOVARON track?", "novaron_system", "telemetry", ["novaron-sys-latency-telemetry"]),

    # --- 2. COMPUTER SCIENCE (35 queries) ---
    EvalQuery("What is Python programming language?", "computer_science", "programming", ["tech-lang-python", "hindi-tech-python"]),
    EvalQuery("Explain Python GIL and garbage collector", "computer_science", "programming", ["tech-lang-python-internals"]),
    EvalQuery("What is the C programming language?", "computer_science", "programming", ["tech-lang-c"]),
    EvalQuery("How do pointers and malloc work in C?", "computer_science", "programming", ["tech-lang-c-pointers"]),
    EvalQuery("Explain C++ and RAII resource management", "computer_science", "programming", ["tech-lang-cpp", "tech-lang-cpp-stl"]),
    EvalQuery("What is Java JVM and garbage collection?", "computer_science", "programming", ["tech-lang-java"]),
    EvalQuery("How does JavaScript event loop work?", "computer_science", "programming", ["tech-lang-javascript"]),
    EvalQuery("What is TypeScript static typing?", "computer_science", "programming", ["tech-lang-typescript"]),
    EvalQuery("What is Rust memory safety and ownership?", "computer_science", "programming", ["tech-lang-rust"]),
    EvalQuery("Explain Go goroutines and channels", "computer_science", "programming", ["tech-lang-go"]),
    EvalQuery("What is an array and dynamic array?", "computer_science", "data_structures", ["tech-ds-array"]),
    EvalQuery("How do singly and doubly linked lists work?", "computer_science", "data_structures", ["tech-ds-linked-list"]),
    EvalQuery("What is a stack LIFO data structure?", "computer_science", "data_structures", ["tech-ds-stack"]),
    EvalQuery("Explain queues and circular buffers", "computer_science", "data_structures", ["tech-ds-queue"]),
    EvalQuery("What is a hash table and collision resolution?", "computer_science", "data_structures", ["tech-ds-hash-table"]),
    EvalQuery("What are binary tree traversals?", "computer_science", "data_structures", ["tech-ds-binary-tree"]),
    EvalQuery("What is a binary search tree BST?", "computer_science", "data_structures", ["tech-ds-bst"]),
    EvalQuery("How do AVL tree rotations work?", "computer_science", "data_structures", ["tech-ds-avl-tree"]),
    EvalQuery("What is a Red-Black tree?", "computer_science", "data_structures", ["tech-ds-red-black-tree"]),
    EvalQuery("Explain binary heaps and priority queues", "computer_science", "data_structures", ["tech-ds-heap"]),
    EvalQuery("What is a trie or prefix tree?", "computer_science", "data_structures", ["tech-ds-trie"]),
    EvalQuery("How do Disjoint Set Union DSU work?", "computer_science", "data_structures", ["tech-ds-dsu"]),
    EvalQuery("What is Big-O asymptotic notation?", "computer_science", "algorithms", ["tech-algo-big-o"]),
    EvalQuery("How do quicksort and mergesort work?", "computer_science", "algorithms", ["tech-algo-sorting"]),
    EvalQuery("Explain binary search algorithm", "computer_science", "algorithms", ["tech-algo-binary-search"]),
    EvalQuery("What is dynamic programming memoization?", "computer_science", "algorithms", ["tech-algo-dp"]),
    EvalQuery("How does Dijkstra algorithm find shortest paths?", "computer_science", "algorithms", ["tech-algo-dijkstra"]),
    EvalQuery("What is the four pillars of OOP?", "computer_science", "oop", ["tech-oop-principles"]),
    EvalQuery("Explain the SOLID design principles", "computer_science", "oop", ["tech-oop-solid"]),
    EvalQuery("What are ACID properties in databases?", "computer_science", "databases", ["tech-db-acid"]),
    EvalQuery("Explain database normalization 1NF 2NF 3NF BCNF", "computer_science", "databases", ["tech-db-normalization"]),
    EvalQuery("What is virtual memory and paging in OS?", "computer_science", "operating_systems", ["tech-os-virtual-memory"]),
    EvalQuery("How does TCP 3-way handshake work?", "computer_science", "networking", ["tech-net-tcp-udp"]),
    EvalQuery("Explain DNS resolution process", "computer_science", "networking", ["tech-net-dns"]),
    EvalQuery("What is React Virtual DOM and reconciliation?", "computer_science", "web_development", ["tech-web-react"]),

    # --- 3. AI / MACHINE LEARNING (30 queries) ---
    EvalQuery("What is artificial intelligence AI?", "ai_ml", "ai_foundations", ["ai-fundamentals", "hindi-tech-ai"]),
    EvalQuery("Explain supervised unsupervised and reinforcement learning", "ai_ml", "machine_learning", ["ai-machine-learning-types", "hindi-tech-ml"]),
    EvalQuery("What is linear regression and ordinary least squares?", "ai_ml", "machine_learning", ["ai-linear-regression"]),
    EvalQuery("What is L1 Lasso and L2 Ridge regularization?", "ai_ml", "machine_learning", ["ai-regularization"]),
    EvalQuery("Explain logistic regression and sigmoid function", "ai_ml", "machine_learning", ["ai-logistic-regression"]),
    EvalQuery("How do decision trees use Gini impurity and entropy?", "ai_ml", "machine_learning", ["ai-decision-trees"]),
    EvalQuery("What is a Random Forest ensemble?", "ai_ml", "machine_learning", ["ai-random-forests"]),
    EvalQuery("Explain gradient boosting and XGBoost", "ai_ml", "machine_learning", ["ai-gradient-boosting"]),
    EvalQuery("How does Support Vector Machine SVM kernel trick work?", "ai_ml", "machine_learning", ["ai-svm"]),
    EvalQuery("What is K-Means clustering algorithm?", "ai_ml", "machine_learning", ["ai-clustering-kmeans-dbscan"]),
    EvalQuery("Explain Principal Component Analysis PCA", "ai_ml", "machine_learning", ["ai-dimensionality-reduction"]),
    EvalQuery("What is Precision Recall F1 score and ROC-AUC?", "ai_ml", "machine_learning", ["ai-model-evaluation-metrics"]),
    EvalQuery("How does backpropagation train neural networks?", "ai_ml", "deep_learning", ["ai-neural-networks-backprop"]),
    EvalQuery("What is ReLU and GELU activation function?", "ai_ml", "deep_learning", ["ai-activation-functions"]),
    EvalQuery("Explain Adam optimizer and gradient descent", "ai_ml", "deep_learning", ["ai-optimization-adam-sgd"]),
    EvalQuery("How do CNNs and ResNet residual connections work?", "ai_ml", "deep_learning", ["ai-cnn-architectures"]),
    EvalQuery("Explain LSTM gates and cell state", "ai_ml", "deep_learning", ["ai-rnn-lstm-gru"]),
    EvalQuery("What is Transformer self-attention mechanism?", "ai_ml", "transformers", ["ai-transformers-attention", "hindi-tech-transformers-rag"]),
    EvalQuery("How do Rotary Position Embeddings RoPE work?", "ai_ml", "transformers", ["ai-positional-encodings"]),
    EvalQuery("What is the difference between BERT and GPT?", "ai_ml", "transformers", ["ai-bert-gpt"]),
    EvalQuery("Explain BPE and WordPiece tokenization", "ai_ml", "nlp", ["ai-nlp-tokenization"]),
    EvalQuery("What are dense vector embeddings and cosine similarity?", "ai_ml", "nlp", ["ai-embeddings-vector-spaces"]),
    EvalQuery("How does FAISS vector search work?", "ai_ml", "information_retrieval", ["ai-faiss", "hindi-tech-faiss"]),
    EvalQuery("Explain BM25 Okapi lexical ranking formula", "ai_ml", "information_retrieval", ["ai-bm25-lexical"]),
    EvalQuery("What is hybrid search and Reciprocal Rank Fusion RRF?", "ai_ml", "information_retrieval", ["ai-hybrid-rrf"]),
    EvalQuery("How does cross-encoder reranking work?", "ai_ml", "information_retrieval", ["ai-cross-encoder-reranking"]),
    EvalQuery("What is Retrieval-Augmented Generation RAG?", "ai_ml", "rag", ["ai-rag-architecture", "hindi-tech-transformers-rag"]),
    EvalQuery("What are chunking strategies in RAG?", "ai_ml", "rag", ["ai-rag-chunking"]),
    EvalQuery("How does OpenAI Whisper speech recognition work?", "ai_ml", "speech", ["ai-speech-whisper-stt"]),
    EvalQuery("Explain neural text to speech TTS and EdgeTTS", "ai_ml", "speech", ["ai-speech-tts-neural"]),

    # --- 4. GENERAL SCIENCE (25 queries) ---
    EvalQuery("What are Newton's three laws of motion?", "general_science", "physics", ["sci-phys-newton-laws"]),
    EvalQuery("Explain conservation of energy and kinetic energy", "general_science", "physics", ["sci-phys-work-energy-momentum"]),
    EvalQuery("What is gravity and universal gravitation?", "general_science", "physics", ["sci-phys-gravity", "hindi-science-gravity"]),
    EvalQuery("What are the laws of thermodynamics and entropy?", "general_science", "physics", ["sci-phys-thermodynamics"]),
    EvalQuery("Explain Maxwell's equations in electromagnetism", "general_science", "physics", ["sci-phys-electromagnetism"]),
    EvalQuery("What is Snell's law of light refraction?", "general_science", "physics", ["sci-phys-waves-optics"]),
    EvalQuery("Explain Einstein's special relativity and quantum mechanics", "general_science", "physics", ["sci-phys-relativity-quantum"]),
    EvalQuery("What is atomic structure protons and electrons?", "general_science", "chemistry", ["sci-chem-atomic-structure"]),
    EvalQuery("Explain the periodic table and periodic trends", "general_science", "chemistry", ["sci-chem-periodic-table"]),
    EvalQuery("What is the difference between covalent and ionic bonds?", "general_science", "chemistry", ["sci-chem-chemical-bonding"]),
    EvalQuery("Explain chemical stoichiometry and mole concept", "general_science", "chemistry", ["sci-chem-reactions-stoichiometry"]),
    EvalQuery("What is the pH scale for acids and bases?", "general_science", "chemistry", ["sci-chem-acids-bases-ph"]),
    EvalQuery("What are organelles in eukaryotic cells?", "general_science", "biology", ["sci-bio-cell-structure"]),
    EvalQuery("Explain DNA structure and the central dogma", "general_science", "biology", ["sci-bio-dna-genetics", "hindi-science-dna"]),
    EvalQuery("What is photosynthesis in green plants?", "general_science", "biology", ["science-photosynthesis-en", "science-photosynthesis-hi"]),
    EvalQuery("Explain cellular respiration and ATP generation", "general_science", "biology", ["sci-bio-cellular-respiration"]),
    EvalQuery("What is biological evolution and natural selection?", "general_science", "biology", ["sci-bio-evolution-genetics"]),
    EvalQuery("How do the circulatory and immune systems work?", "general_science", "biology", ["sci-bio-human-physiology"]),
    EvalQuery("What are the layers of Earth's atmosphere?", "general_science", "earth_science", ["sci-earth-atmosphere-climate"]),
    EvalQuery("Explain the water cycle hydrologic process", "general_science", "earth_science", ["sci-earth-water-cycle"]),
    EvalQuery("What is plate tectonics and continental drift?", "general_science", "earth_science", ["sci-earth-plate-tectonics"]),
    EvalQuery("What planets are in the Solar System?", "general_science", "astronomy", ["sci-astro-solar-system", "hindi-science-solar-system"]),
    EvalQuery("Explain Kepler's laws of planetary motion", "general_science", "astronomy", ["sci-astro-solar-system"]),
    EvalQuery("What is stellar evolution and black holes?", "general_science", "astronomy", ["sci-astro-stellar-evolution-black-holes"]),
    EvalQuery("What happens in a supernova explosion?", "general_science", "astronomy", ["sci-astro-stellar-evolution-black-holes"]),

    # --- 5. MATHEMATICS (15 queries) ---
    EvalQuery("What is a prime number and fundamental theorem of arithmetic?", "mathematics", "arithmetic", ["math-arithmetic-primes"]),
    EvalQuery("Explain modular arithmetic and congruence", "mathematics", "arithmetic", ["math-modular-arithmetic"]),
    EvalQuery("How to solve quadratic equations using discriminant?", "mathematics", "algebra", ["math-algebra-linear-quadratic"]),
    EvalQuery("What are the properties of logarithms and exponents?", "mathematics", "algebra", ["math-algebra-logarithms-exponents"]),
    EvalQuery("Explain arithmetic and geometric progressions", "mathematics", "algebra", ["math-sequences-series"]),
    EvalQuery("What is the Pythagorean theorem in geometry?", "mathematics", "geometry", ["math-geometry-euclidean"]),
    EvalQuery("What are trigonometric identities on the unit circle?", "mathematics", "trigonometry", ["math-trigonometry-functions"]),
    EvalQuery("Explain derivatives and the power rule in calculus", "mathematics", "calculus", ["math-calculus-limits-derivatives"]),
    EvalQuery("What is the Fundamental Theorem of Calculus?", "mathematics", "calculus", ["math-calculus-integrals"]),
    EvalQuery("What is gradient and Jacobian in multivariable calculus?", "mathematics", "calculus", ["math-calculus-multivariable"]),
    EvalQuery("Explain matrix multiplication in linear algebra", "mathematics", "linear_algebra", ["math-linear-algebra-matrices"]),
    EvalQuery("What are eigenvalues and eigenvectors?", "mathematics", "linear_algebra", ["math-linear-algebra-eigenvalues"]),
    EvalQuery("Explain Bayes' theorem and conditional probability", "mathematics", "probability_statistics", ["math-prob-axioms-bayes"]),
    EvalQuery("What is the normal Gaussian distribution?", "mathematics", "probability_statistics", ["math-stats-distributions"]),
    EvalQuery("Explain set theory unions and intersections", "mathematics", "discrete_math", ["math-discrete-set-theory-logic"]),

    # --- 6. GENERAL KNOWLEDGE (15 queries) ---
    EvalQuery("What are the seven continents and five oceans?", "general_knowledge", "geography", ["gk-geo-continents-oceans"]),
    EvalQuery("What is the highest mountain range on Earth?", "general_knowledge", "geography", ["gk-geo-mountains-rivers"]),
    EvalQuery("Explain latitude longitude and time zones", "general_knowledge", "geography", ["gk-geo-coordinates-climate-zones"]),
    EvalQuery("What is the law of supply and demand in economics?", "general_knowledge", "economics", ["gk-econ-supply-demand"]),
    EvalQuery("What is Gross Domestic Product GDP and inflation?", "general_knowledge", "economics", ["gk-econ-macro-gdp-inflation"]),
    EvalQuery("Explain perfect competition and monopoly market structures", "general_knowledge", "economics", ["gk-econ-market-structures"]),
    EvalQuery("What were the ancient civilizations of Mesopotamia and Egypt?", "general_knowledge", "history", ["gk-hist-ancient-civilizations"]),
    EvalQuery("What was the Indus Valley civilization?", "general_knowledge", "history", ["gk-hist-ancient-civilizations"]),
    EvalQuery("Explain classical antiquity in Greece and Rome", "general_knowledge", "history", ["gk-hist-classical-antiquity"]),
    EvalQuery("What was the Scientific Revolution and Enlightenment?", "general_knowledge", "history", ["gk-hist-scientific-revolution"]),
    EvalQuery("How did the Industrial Revolution transform manufacturing?", "general_knowledge", "history", ["gk-hist-industrial-revolution"]),
    EvalQuery("What are the steps of the scientific method?", "general_knowledge", "science_method", ["gk-sci-scientific-method"]),
    EvalQuery("What are renewable energy sources for sustainability?", "general_knowledge", "science_method", ["gk-sci-sustainability-energy"]),
    EvalQuery("What is the longest river in the world?", "general_knowledge", "geography", ["gk-geo-mountains-rivers"]),
    EvalQuery("What is fiscal policy vs monetary policy?", "general_knowledge", "economics", ["gk-econ-macro-gdp-inflation"]),

    # --- 7. MULTILINGUAL HINDI & HINGLISH (15 queries) ---
    EvalQuery("पायथन क्या है?", "computer_science", "programming", ["hindi-tech-python", "tech-lang-python"], "hi"),
    EvalQuery("Python kya hai?", "computer_science", "programming", ["hindi-tech-python", "tech-lang-python"], "hi"),
    EvalQuery("कृत्रिम बुद्धिमत्ता क्या है?", "ai_ml", "ai_foundations", ["hindi-tech-ai", "ai-fundamentals"], "hi"),
    EvalQuery("AI kya hai?", "ai_ml", "ai_foundations", ["hindi-tech-ai", "ai-fundamentals"], "hi"),
    EvalQuery("मशीन लर्निंग क्या होती है?", "ai_ml", "machine_learning", ["hindi-tech-ml", "ai-machine-learning-types"], "hi"),
    EvalQuery("गुरुत्वाकर्षण क्या है?", "general_science", "physics", ["hindi-science-gravity", "sci-phys-gravity"], "hi"),
    EvalQuery("Gravity kya hai?", "general_science", "physics", ["hindi-science-gravity", "sci-phys-gravity"], "hi"),
    EvalQuery("प्रकाश संश्लेषण क्या है?", "general_science", "biology", ["science-photosynthesis-hi", "science-photosynthesis-en"], "hi"),
    EvalQuery("Photosynthesis kya hota hai?", "general_science", "biology", ["science-photosynthesis-hi", "science-photosynthesis-en"], "hi"),
    EvalQuery("सौर मंडल में कितने ग्रह हैं?", "general_science", "astronomy", ["hindi-science-solar-system", "sci-astro-solar-system"], "hi"),
    EvalQuery("डेटाबेस और SQL क्या है?", "computer_science", "databases", ["hindi-tech-db", "tech-db-rdbms"], "hi"),
    EvalQuery("ऑपरेटिंग सिस्टम क्या होता है?", "computer_science", "operating_systems", ["hindi-tech-os", "tech-os-processes-threads"], "hi"),
    EvalQuery("FAISS कैसे काम करता है?", "ai_ml", "information_retrieval", ["hindi-tech-faiss", "ai-faiss"], "hi"),
    EvalQuery("RAG क्या है?", "ai_ml", "rag", ["hindi-tech-transformers-rag", "ai-rag-architecture"], "hi"),
    EvalQuery("नोवारॉन क्या है?", "novaron_system", "architecture", ["hindi-novaron-sys", "novaron-sys-overview"], "hi"),
]


def evaluate_pipeline(pipe, queries: list[EvalQuery], top_k: int = 10):
    recall_1 = 0
    recall_3 = 0
    recall_5 = 0
    recall_10 = 0
    mrr_total = 0.0
    domain_acc_1 = 0
    topic_acc_3 = 0
    latencies = []

    domain_hits = {}
    domain_totals = {}

    for q in queries:
        d = q.expected_domain
        domain_totals[d] = domain_totals.get(d, 0) + 1

        t0 = time.perf_counter()
        hits = pipe.retriever.search(q.query, limit=top_k)
        if hasattr(pipe, "reranker") and pipe.reranker:
            hits = pipe.reranker.rerank(q.query, hits, limit=top_k)
        elapsed = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed)

        retrieved_doc_ids = [hit.chunk.document_id for hit in hits]

        # Find first rank of any expected document
        found_rank = None
        for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
            if any(doc_id == exp or doc_id.startswith(exp) or exp.startswith(doc_id) for exp in q.expected_doc_ids):
                found_rank = rank
                break

        if found_rank is not None:
            if found_rank <= 1:
                recall_1 += 1
                domain_hits[d] = domain_hits.get(d, 0) + 1
            if found_rank <= 3:
                recall_3 += 1
            if found_rank <= 5:
                recall_5 += 1
            if found_rank <= 10:
                recall_10 += 1
            mrr_total += 1.0 / found_rank

        # Domain and Topic Accuracy
        if hits:
            top_hit = hits[0]
            top_doc = top_hit.chunk.document_id
            if any(top_doc == exp or top_doc.startswith(exp) or exp.startswith(top_doc) for exp in q.expected_doc_ids):
                domain_acc_1 += 1

            # Check if any of top 3 hits match expected topic
            for h in hits[:3]:
                if any(h.chunk.document_id == exp or h.chunk.document_id.startswith(exp) or exp.startswith(h.chunk.document_id) for exp in q.expected_doc_ids):
                    topic_acc_3 += 1
                    break

    n = len(queries)
    return {
        "recall@1": recall_1 / n,
        "recall@3": recall_3 / n,
        "recall@5": recall_5 / n,
        "recall@10": recall_10 / n,
        "mrr": mrr_total / n,
        "domain_acc@1": domain_acc_1 / n,
        "topic_acc@3": topic_acc_3 / n,
        "avg_latency_ms": sum(latencies) / len(latencies),
        "domain_breakdown": {d: domain_hits.get(d, 0) / domain_totals[d] for d in domain_totals},
    }


def main():
    print(f"Loading corpus from {DATA_PATH}...")
    docs = load_jsonl(DATA_PATH)
    chunks = sentence_chunks(docs)
    print(f"Corpus loaded: {len(docs)} documents | {len(chunks)} sentence chunks")

    print(f"\nInitializing pipelines for evaluation across {len(BENCHMARK_QUERIES)} benchmark queries...")
    from app.main import pipelines as app_pipelines
    sent_pipelines = app_pipelines["sentence"]

    modes = ["dense", "bm25", "hybrid", "hybrid_rerank"]
    results = {}

    print("=" * 95)
    print(f"{'Mode':<16} | {'Recall@1':<9} | {'Recall@3':<9} | {'Recall@5':<9} | {'Recall@10':<9} | {'MRR':<8} | {'Topic@3':<8} | {'Avg Latency'}")
    print("=" * 95)

    for mode in modes:
        pipe = sent_pipelines[mode]
        res = evaluate_pipeline(pipe, BENCHMARK_QUERIES, top_k=10)
        results[mode] = res
        print(f"{mode:<16} | {res['recall@1']*100:>7.1f}% | {res['recall@3']*100:>7.1f}% | {res['recall@5']*100:>7.1f}% | {res['recall@10']*100:>7.1f}% | {res['mrr']:>8.3f} | {res['topic_acc@3']*100:>6.1f}% | {res['avg_latency_ms']:>8.2f} ms")

    print("=" * 95)

    print("\nDomain-by-Domain Recall@1 Breakdown (Hybrid Mode):")
    hybrid_domains = results["hybrid"]["domain_breakdown"]
    for d, score in sorted(hybrid_domains.items()):
        print(f"  - {d:<20}: {score*100:.1f}%")

    print("\nBenchmark Evaluation Complete!")


if __name__ == "__main__":
    main()
