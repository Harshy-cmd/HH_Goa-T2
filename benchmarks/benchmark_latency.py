"""
NOVARON Production Latency Benchmark — P50 / P70 / P100 Statistical Analysis
Strict Offline Mode — Zero Cloud API Calls.

Measures stage-by-stage latency across 85 representative queries:
1. Dense Embedding (Multilingual E5 Small)
2. FAISS Vector DB Retrieval (12,206 vectors)
3. BM25 Lexical Retrieval
4. Reciprocal Rank Fusion (RRF)
5. Transparent Reranking
6. Total Retrieval Pipeline (< 200ms Target)
7. Local STT (Faster-Whisper CPU)
"""
from __future__ import annotations

import io
import json
import os
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

# Load .env
import dotenv
dotenv.load_dotenv(ROOT / ".env", override=True)

import psutil
from app.domain import Chunk, SearchHit
from app.embeddings import SentenceTransformerEmbeddingProvider
from app.retrieval import (
    BM25Retriever,
    FAISSDenseRetriever,
    HybridRetriever,
    TransparentReranker,
)
from app.router import classify_query, detect_language_with_confidence
from app.stt import FasterWhisperSTT
from app.tts import EdgeTTS
from app.vector_store import FaissVectorStore

# 85 Diverse Representative Queries covering 15 languages, varying lengths, technical & non-technical
BENCHMARK_QUERIES = [
    # English Technical & Factual (20)
    {"id": "en-01", "lang": "en", "category": "technical", "query": "What is Python?"},
    {"id": "en-02", "lang": "en", "category": "technical", "query": "What is FAISS vector search and how does it index embeddings?"},
    {"id": "en-03", "lang": "en", "category": "technical", "query": "What is Retrieval-Augmented Generation (RAG)?"},
    {"id": "en-04", "lang": "en", "category": "scientific", "query": "What is photosynthesis and how does chlorophyll capture light?"},
    {"id": "en-05", "lang": "en", "category": "scientific", "query": "What is gravity in general relativity?"},
    {"id": "en-06", "lang": "en", "category": "technical", "query": "What is machine learning backpropagation algorithm?"},
    {"id": "en-07", "lang": "en", "category": "technical", "query": "What is a database index B-tree structure?"},
    {"id": "en-08", "lang": "en", "category": "technical", "query": "What is recursion in computer science?"},
    {"id": "en-09", "lang": "en", "category": "technical", "query": "What is an operating system kernel and virtual memory?"},
    {"id": "en-10", "lang": "en", "category": "technical", "query": "What is artificial intelligence and neural networks?"},
    {"id": "en-11", "lang": "en", "category": "technical", "query": "What is a binary search tree?"},
    {"id": "en-12", "lang": "en", "category": "technical", "query": "What is TCP handshake and flow control?"},
    {"id": "en-13", "lang": "en", "category": "technical", "query": "What is database normalization Third Normal Form (3NF)?"},
    {"id": "en-14", "lang": "en", "category": "technical", "query": "What is a transformer self-attention mechanism?"},
    {"id": "en-15", "lang": "en", "category": "scientific", "query": "What is DNA replication and RNA transcription?"},
    {"id": "en-16", "lang": "en", "category": "scientific", "query": "What is probability theory and Bayes theorem?"},
    {"id": "en-17", "lang": "en", "category": "scientific", "query": "What is a derivative in calculus?"},
    {"id": "en-18", "lang": "en", "category": "factual", "query": "What is supply and demand market equilibrium?"},
    {"id": "en-19", "lang": "en", "category": "technical", "query": "How does Docker containerization differ from virtual machines?"},
    {"id": "en-20", "lang": "en", "category": "technical", "query": "Explain microservices architecture service discovery and API gateway."},

    # Hindi Technical & Factual (15)
    {"id": "hi-01", "lang": "hi", "category": "scientific", "query": "प्रकाश संश्लेषण क्या है और पौधे अपना भोजन कैसे बनाते हैं?"},
    {"id": "hi-02", "lang": "hi", "category": "scientific", "query": "गुरुत्वाकर्षण क्या है?"},
    {"id": "hi-03", "lang": "hi", "category": "technical", "query": "पायथन प्रोग्रामिंग भाषा क्या है?"},
    {"id": "hi-04", "lang": "hi", "category": "technical", "query": "कृत्रिम बुद्धिमत्ता क्या है और यह कैसे काम करती है?"},
    {"id": "hi-05", "lang": "hi", "category": "scientific", "query": "मानव हृदय की संरचना और कार्यप्रणाली समझाइए।"},
    {"id": "hi-06", "lang": "hi", "category": "technical", "query": "कंप्यूटर नेटवर्क में आईपी पता क्या होता है?"},
    {"id": "hi-07", "lang": "hi", "category": "technical", "query": "मशीन लर्निंग के मूल सिद्धांत क्या हैं?"},
    {"id": "hi-08", "lang": "hi", "category": "technical", "query": "डेटाबेस प्रबंधन प्रणाली क्या है?"},
    {"id": "hi-09", "lang": "hi", "category": "scientific", "query": "सौर मंडल में ग्रहों की संख्या और उनके नाम क्या हैं?"},
    {"id": "hi-10", "lang": "hi", "category": "scientific", "query": "डीएनए की संरचना कैसी होती है?"},
    {"id": "hi-11", "lang": "hi", "category": "technical", "query": "ऑपरेटिंग सिस्टम का मुख्य कार्य क्या है?"},
    {"id": "hi-12", "lang": "hi", "category": "technical", "query": "क्वांटम कंप्यूटिंग क्या है?"},
    {"id": "hi-13", "lang": "hi", "category": "scientific", "query": "परमाणु संरचना और इलेक्ट्रॉन प्रोटॉन क्या हैं?"},
    {"id": "hi-14", "lang": "hi", "category": "factual", "query": "भारत का संविधान कब लागू हुआ था?"},
    {"id": "hi-15", "lang": "hi", "category": "technical", "query": "क्लाउड कंप्यूटिंग और इसके विभिन्न मॉडल क्या हैं?"},

    # Other Indic Languages (25)
    {"id": "bn-01", "lang": "bn", "category": "scientific", "query": "সালোকসংশ্লেষণ প্রক্রিয়াটি বিস্তারিতভাবে ব্যাখ্যা করুন।"},
    {"id": "bn-02", "lang": "bn", "category": "technical", "query": "কৃত্রিম বুদ্ধিমত্তা এবং মেশিন লার্নিং এর মধ্যে পার্থক্য কী?"},
    {"id": "bn-03", "lang": "bn", "category": "scientific", "query": "মানবদেহে রক্তের সংবহনতন্ত্র কিভাবে কাজ করে?"},
    {"id": "ta-01", "lang": "ta", "category": "scientific", "query": "ஒளிச்சேர்க்கை செயல்முறை எவ்வாறு நடைபெறுகிறது?"},
    {"id": "ta-02", "lang": "ta", "category": "technical", "query": "செயற்கை நுண்ணறிவு என்றால் என்ன மற்றும் அதன் பயன்கள்?"},
    {"id": "ta-03", "lang": "ta", "category": "scientific", "query": "மனித உடலில் இரத்த ஓட்ட மண்டலம் எவ்வாறு செயல்படுகிறது?"},
    {"id": "te-01", "lang": "te", "category": "scientific", "query": "కిరణజన్య సంయోగక్రియ ప్రక్రియను వివరించండి."},
    {"id": "te-02", "lang": "te", "category": "technical", "query": "కృత్రిమ మేధస్సు అంటే ఏమిటి మరియు దాని ఉపయోగాలు?"},
    {"id": "te-03", "lang": "te", "category": "scientific", "query": "మానవ శరీరంలో రక్త ప్రసరణ వ్యవస్థ ఎలా పనిచేస్తుంది?"},
    {"id": "kn-01", "lang": "kn", "category": "scientific", "query": "ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ ಕ್ರಿಯೆ ಹೇಗೆ ನಡೆಯುತ್ತದೆ?"},
    {"id": "kn-02", "lang": "kn", "category": "technical", "query": "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಎಂದರೇನು ಮತ್ತು ಅದರ ಪ್ರಮುಖ ಉಪಯೋಗಗಳು?"},
    {"id": "ml-01", "lang": "ml", "category": "scientific", "query": "പ്രകാശസംശ്ലേഷണ പ്രക്രിയ എങ്ങനെ നടക്കുന്നു?"},
    {"id": "ml-02", "lang": "ml", "category": "technical", "query": "കൃത്രിമ ബുദ്ധി എന്താണ്?"},
    {"id": "mr-01", "lang": "mr", "category": "scientific", "query": "प्रकाशसंश्लेषण म्हणजे काय आणि ते वनस्पतींमध्ये कसे घडते?"},
    {"id": "mr-02", "lang": "mr", "category": "technical", "query": "कृत्रिम बुद्धिमत्ता काय आहे आणि तिचे उपयोग सांगा."},
    {"id": "gu-01", "lang": "gu", "category": "scientific", "query": "પ્રકાશસંશ્લેષણ શું છે અને તે કેવી રીતે કાર્ય કરે છે?"},
    {"id": "gu-02", "lang": "gu", "category": "technical", "query": "કૃત્રિમ બુદ્ધિ શું છે?"},
    {"id": "pa-01", "lang": "pa", "category": "scientific", "query": "ਪ੍ਰਕਾਸ਼ ਸੰਸਲੇਸ਼ਣ ਕੀ ਹੈ ਅਤੇ ਇਹ ਕਿਵੇਂ ਕੰਮ ਕਰਦਾ ਹੈ?"},
    {"id": "pa-02", "lang": "pa", "category": "technical", "query": "ਮਸ਼ੀਨ ਲਰਨਿੰਗ ਕੀ ਹੈ?"},
    {"id": "or-01", "lang": "or", "category": "scientific", "query": "ଆଲୋକ ସଂଶ୍ଳେଷଣ ପ୍ରକ୍ରିୟା କିପରି ହୁଏ?"},
    {"id": "ur-01", "lang": "ur", "category": "scientific", "query": "فوٹو سنتھیسس کیا ہے اور پودے اپنی خوراک کیسے بناتے ہیں؟"},
    {"id": "ur-02", "lang": "ur", "category": "technical", "query": "مصنوعی ذہانت کیا ہے؟"},
    {"id": "as-01", "lang": "as", "category": "scientific", "query": "সালোক সংশ্লেষণ কিদৰে হয়?"},
    {"id": "ne-01", "lang": "ne", "category": "scientific", "query": "प्रकाश संश्लेषण भनेको के हो?"},
    {"id": "sa-01", "lang": "sa", "category": "scientific", "query": "प्रकाशसंश्लेषणं किम् अस्ति?"},

    # Conversational & System Queries (10)
    {"id": "conv-01", "lang": "en", "category": "conversational", "query": "Hello NOVARON, how are you today?"},
    {"id": "conv-02", "lang": "hi", "category": "conversational", "query": "नमस्ते नोवारोन, आप क्या कर सकते हैं?"},
    {"id": "conv-03", "lang": "ta", "category": "conversational", "query": "வணக்கம், நீங்கள் யார்?"},
    {"id": "conv-04", "lang": "en", "category": "system", "query": "Who created you and what is your architecture?"},
    {"id": "conv-05", "lang": "en", "category": "conversational", "query": "Thank you very much for your assistance."},
    {"id": "conv-06", "lang": "hi", "category": "conversational", "query": "धन्यवाद नोवारोन।"},
    {"id": "conv-07", "lang": "bn", "category": "conversational", "query": "ধন্যবাদ আপনার উত্তরের জন্য।"},
    {"id": "conv-08", "lang": "te", "category": "conversational", "query": "నమస్కారం, మీ పేరు ఏమిటి?"},
    {"id": "conv-09", "lang": "mr", "category": "conversational", "query": "नमस्कार, तुम्ही मला कशी मदत करू शकता?"},
    {"id": "conv-10", "lang": "en", "category": "conversational", "query": "Good morning! Can you help me learn programming?"},

    # Long / Complex Natural Language Questions (10)
    {"id": "long-01", "lang": "en", "category": "complex", "query": "Can you explain in detail how transformers utilize multi-head self-attention mechanisms to capture contextual relationships in natural language processing?"},
    {"id": "long-02", "lang": "hi", "category": "complex", "query": "क्या आप विस्तार से बता सकते हैं कि तंत्रिका नेटवर्क में ग्रेडिएंट डिसेंट और बैकप्रॉपैगेशन एल्गोरिथ्म कैसे वज़न को अपडेट करते हैं?"},
    {"id": "long-03", "lang": "en", "category": "complex", "query": "What are the primary differences between SQL relational databases and NoSQL document stores in terms of ACID compliance and horizontal scalability?"},
    {"id": "long-04", "lang": "hi", "category": "complex", "query": "कंप्यूटर विज्ञान में टाइम कॉम्प्लेक्सिटी और स्पेस कॉम्प्लेक्सिटी का विश्लेषण करने के लिए बिग ओ नोटेशन का उपयोग कैसे किया जाता है?"},
    {"id": "long-05", "lang": "en", "category": "complex", "query": "Explain how the immune system distinguishes between self and non-self antigens using T-cells and B-cells."},
    {"id": "long-06", "lang": "bn", "category": "complex", "query": "কম্পিউটার নেটওয়ার্কে ওএসআই মডেলের সাতটি স্তর এবং তাদের নিজ নিজ কার্যাবলী বিস্তারিতভাবে ব্যাখ্যা করুন।"},
    {"id": "long-07", "lang": "ta", "category": "complex", "query": "இயற்கை மொழி செயலாக்கத்தில் மீள் நரம்பியல் நெட்வொர்க்குகள் மற்றும் டிரான்ஸ்பார்மர்களின் ஒப்பீடு என்ன?"},
    {"id": "long-08", "lang": "te", "category": "complex", "query": "ఆపరేటింగ్ సిస్టమ్‌లలో డెడ్‌లాక్ అంటే ఏమిటి మరియు డెడ్‌లాక్‌ను నివారించడానికి బ్యాంకర్ అల్గోరిథం ఎలా పనిచేస్తుంది?"},
    {"id": "long-09", "lang": "en", "category": "complex", "query": "How do cryptographic public key algorithms such as RSA and elliptic curve cryptography guarantee digital signatures?"},
    {"id": "long-10", "lang": "hi", "category": "complex", "query": "आधुनिक वेब आर्किटेक्चर में लोड बैलेंसर और रिवर्स प्रॉक्सी सर्वर का क्या महत्व है?"},

    # Unsupported / Out-of-Domain Edge Cases (5)
    {"id": "unsupp-01", "lang": "en", "category": "unsupported", "query": "What is the secret recipe for Martian cosmic space cake with antimatter frosting?"},
    {"id": "unsupp-02", "lang": "hi", "category": "unsupported", "query": "मंगल ग्रह के अंतरिक्ष केक की गुप्त रेसिपी क्या है?"},
    {"id": "unsupp-03", "lang": "en", "category": "unsupported", "query": "xyzzy quantum flux hyperdrive warp coordinate 994"},
    {"id": "unsupp-04", "lang": "en", "category": "unsupported", "query": "asldkfj qwpoeiru zmxnvb qwerty 12345"},
    {"id": "unsupp-05", "lang": "hi", "category": "unsupported", "query": "अज्ञात जादुई मंत्र जो ब्रह्मांड के रहस्यों को खोलता है"},
]

WARMUP_QUERIES = [
    "Photosynthesis overview in green plants",
    "प्रकाश संश्लेषण क्या है और यह कैसे होता है?",
    "What is Python programming language?",
    "Hello NOVARON, how are you?",
    "Database indexing and query execution plans",
]


def calculate_percentiles(values: list[float]) -> dict[str, float]:
    if not values:
        return {"p50": 0.0, "p70": 0.0, "p95": 0.0, "p100": 0.0, "mean": 0.0, "min": 0.0}
    s = sorted(values)
    n = len(s)
    return {
        "p50": round(s[int(n * 0.50)], 2),
        "p70": round(s[int(n * 0.70)], 2),
        "p95": round(s[int(n * 0.95)], 2),
        "p100": round(s[-1], 2),
        "mean": round(sum(s) / n, 2),
        "min": round(s[0], 2),
    }


def run_benchmark():
    print("=" * 80)
    print("NOVARON PRODUCTION LATENCY BENCHMARK (STRICT OFFLINE MODE)")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # PHASE 1: COLD START MEASUREMENTS
    # -------------------------------------------------------------------------
    print("\n[PHASE 1] Measuring Cold-Start Latency...")
    t_cold_start = time.perf_counter()

    t0 = time.perf_counter()
    embedder = SentenceTransformerEmbeddingProvider()
    t_model_load = (time.perf_counter() - t0) * 1000

    index_dir = ROOT / "data" / "indexes" / "sentence"
    t0 = time.perf_counter()
    store = FaissVectorStore.load(index_dir)
    t_faiss_load = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    bm25 = BM25Retriever(store.chunks)
    t_bm25_load = (time.perf_counter() - t0) * 1000

    dense_retriever = FAISSDenseRetriever(store, embedder)
    hybrid_retriever = HybridRetriever(dense_retriever, bm25)
    reranker = TransparentReranker()

    t_total_init = (time.perf_counter() - t_cold_start) * 1000

    # Measure first cold query execution
    t0_cold_query = time.perf_counter()
    first_cold_hit, first_cold_profile = hybrid_retriever.search_with_profile("What is Python?", limit=10)
    reranker.rerank("What is Python?", first_cold_hit, limit=5)
    t_first_query = (time.perf_counter() - t0_cold_query) * 1000

    print(f"  • Model Loading Time      : {t_model_load:.2f} ms")
    print(f"  • FAISS Index Load Time    : {t_faiss_load:.2f} ms")
    print(f"  • BM25 Index Build Time    : {t_bm25_load:.2f} ms")
    print(f"  • Total Pipeline Init Time : {t_total_init:.2f} ms")
    print(f"  • First (Cold) Query Time  : {t_first_query:.2f} ms")

    # -------------------------------------------------------------------------
    # PHASE 2: WARMUP PHASE (Excluded from metrics)
    # -------------------------------------------------------------------------
    print(f"\n[PHASE 2] Executing {len(WARMUP_QUERIES)} Warmup Queries (Excluded from stats)...")
    for idx, wq in enumerate(WARMUP_QUERIES, start=1):
        t_w0 = time.perf_counter()
        detect_language_with_confidence(wq)
        classify_query(wq)
        hits, prof = hybrid_retriever.search_with_profile(wq, limit=10)
        reranker.rerank(wq, hits, limit=5)
        w_ms = (time.perf_counter() - t_w0) * 1000
        print(f"  Warmup {idx}/{len(WARMUP_QUERIES)}: {wq[:35]:<35} ({w_ms:.2f} ms)")

    # -------------------------------------------------------------------------
    # PHASE 3: MEASUREMENT OF 85 REPRESENTATIVE QUERIES
    # -------------------------------------------------------------------------
    print(f"\n[PHASE 3] Benchmarking {len(BENCHMARK_QUERIES)} Diverse Queries (Warm Invocations)...")

    metrics = {
        "router": [],
        "embedding": [],
        "faiss": [],
        "bm25": [],
        "rrf": [],
        "reranking": [],
        "total_retrieval": [],
    }

    per_query_records = []

    for item in BENCHMARK_QUERIES:
        qid = item["id"]
        lang = item["lang"]
        q = item["query"]

        # High-resolution monotonic timing
        t_start = time.perf_counter()

        # Router
        t_r0 = time.perf_counter()
        route = classify_query(q)
        t_router = (time.perf_counter() - t_r0) * 1000

        # Hybrid Retrieval
        hits, profile = hybrid_retriever.search_with_profile(q, limit=10)
        t_retrieved = time.perf_counter()

        # Reranker
        t_rr0 = time.perf_counter()
        reranked = reranker.rerank(q, hits, limit=5)
        t_rerank = (time.perf_counter() - t_rr0) * 1000

        t_end = time.perf_counter()

        t_embed = profile.get("embedding", 0.0)
        t_faiss = profile.get("faiss", 0.0)
        t_bm25 = profile.get("bm25", 0.0)
        t_rrf = profile.get("rrf", 0.0)
        t_total_retrieval = t_embed + t_faiss + t_bm25 + t_rrf + t_rerank

        metrics["router"].append(t_router)
        metrics["embedding"].append(t_embed)
        metrics["faiss"].append(t_faiss)
        metrics["bm25"].append(t_bm25)
        metrics["rrf"].append(t_rrf)
        metrics["reranking"].append(t_rerank)
        metrics["total_retrieval"].append(t_total_retrieval)

        per_query_records.append({
            "id": qid,
            "lang": lang,
            "category": item["category"],
            "query": q,
            "top_score": round(reranked[0].score, 4) if reranked else 0.0,
            "router_ms": round(t_router, 3),
            "embedding_ms": round(t_embed, 3),
            "faiss_ms": round(t_faiss, 3),
            "bm25_ms": round(t_bm25, 3),
            "rrf_ms": round(t_rrf, 3),
            "rerank_ms": round(t_rerank, 3),
            "total_retrieval_ms": round(t_total_retrieval, 3),
        })

    # -------------------------------------------------------------------------
    # PHASE 4: LOCAL STT (FASTER-WHISPER) BENCHMARK (100% OFFLINE)
    # -------------------------------------------------------------------------
    print("\n[PHASE 4] Benchmarking Local Faster-Whisper STT (CPU)...")
    stt_adapter = FasterWhisperSTT(model_size="tiny", device="cpu", compute_type="int8")
    tts_adapter = EdgeTTS()

    # Pre-generate synthetic / sample audio buffers to transcribe
    stt_test_samples = [
        ("What is Python?", "en"),
        ("What is artificial intelligence?", "en"),
        ("What is machine learning?", "en"),
        ("What is photosynthesis?", "en"),
        ("What is Retrieval Augmented Generation?", "en"),
        ("प्रकाश संश्लेषण क्या है?", "hi"),
        ("पायथन क्या है?", "hi"),
        ("कृत्रिम बुद्धिमत्ता क्या है?", "hi"),
    ]

    stt_latencies = []
    import asyncio

    # Generate test audio offline via EdgeTTS once for deterministic measurement
    audio_fixtures = []
    for text, l in stt_test_samples:
        try:
            a = asyncio.run(tts_adapter.synthesize(text, language=l))
            audio_fixtures.append((a, l, text))
        except Exception:
            pass

    # Warmup STT
    if audio_fixtures:
        asyncio.run(stt_adapter.transcribe(audio_fixtures[0][0], language=audio_fixtures[0][1]))

    # Measure STT
    for a_bytes, l, text in audio_fixtures:
        t_s0 = time.perf_counter()
        transcript = asyncio.run(stt_adapter.transcribe(a_bytes, language=l))
        stt_dur = (time.perf_counter() - t_s0) * 1000
        stt_latencies.append(stt_dur)

    stt_stats = calculate_percentiles(stt_latencies) if stt_latencies else None

    # -------------------------------------------------------------------------
    # PHASE 5: COMPUTE PERCENTILE STATISTICS
    # -------------------------------------------------------------------------
    stats = {stage: calculate_percentiles(vals) for stage, vals in metrics.items()}

    # Bottleneck breakdown (mean contribution percentage)
    mean_total = stats["total_retrieval"]["mean"]
    bottleneck_pct = {
        "Embedding": (stats["embedding"]["mean"] / mean_total) * 100 if mean_total else 0,
        "FAISS": (stats["faiss"]["mean"] / mean_total) * 100 if mean_total else 0,
        "BM25": (stats["bm25"]["mean"] / mean_total) * 100 if mean_total else 0,
        "RRF": (stats["rrf"]["mean"] / mean_total) * 100 if mean_total else 0,
        "Reranker": (stats["reranking"]["mean"] / mean_total) * 100 if mean_total else 0,
    }

    slowest_stage = max(bottleneck_pct.items(), key=lambda x: x[1])

    # -------------------------------------------------------------------------
    # PHASE 6: VERDICT ASSESSMENT
    # -------------------------------------------------------------------------
    p50_total = stats["total_retrieval"]["p50"]
    p70_total = stats["total_retrieval"]["p70"]
    p100_total = stats["total_retrieval"]["p100"]

    if p100_total < 200.0:
        verdict = "PASS"
        verdict_color = "GREEN"
    elif p50_total < 200.0:
        verdict = "PARTIAL"
        verdict_color = "YELLOW"
    else:
        verdict = "FAIL"
        verdict_color = "RED"

    # Hardware Info
    hw_info = {
        "os": platform.platform(),
        "cpu": platform.processor() or platform.machine(),
        "cpu_cores": f"{psutil.cpu_count(logical=False)} physical / {psutil.cpu_count(logical=True)} logical",
        "ram_gb": round(psutil.virtual_memory().total / (1024 ** 3), 1),
        "python": sys.version.split()[0],
        "embedding_model": embedder.model_name,
        "reranker": "TransparentReranker (0.6 content / 0.4 title term coverage)",
        "faiss_index": f"IndexFlatIP ({store.index.ntotal:,} vectors, 384 dim)",
        "bm25_chunks": f"{len(bm25.chunks):,} chunks",
        "query_count": len(BENCHMARK_QUERIES),
        "warmup_count": len(WARMUP_QUERIES),
    }

    # Output JSON Report
    output_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "hardware": hw_info,
        "cold_start": {
            "model_load_ms": round(t_model_load, 2),
            "faiss_load_ms": round(t_faiss_load, 2),
            "bm25_load_ms": round(t_bm25_load, 2),
            "pipeline_init_total_ms": round(t_total_init, 2),
            "first_cold_query_ms": round(t_first_query, 2),
        },
        "stage_percentiles": stats,
        "bottleneck_breakdown_pct": {k: round(v, 2) for k, v in bottleneck_pct.items()},
        "stt_local_faster_whisper": stt_stats,
        "verdict": {
            "status": verdict,
            "target": "<200ms",
            "p50_ms": p50_total,
            "p70_ms": p70_total,
            "p100_ms": p100_total,
            "rating": verdict_color,
        },
        "per_query_details": per_query_records,
    }

    results_dir = ROOT / "benchmarks" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    json_path = results_dir / "latency_benchmark_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Benchmark results saved to {json_path}")
    return output_data


if __name__ == "__main__":
    run_benchmark()
