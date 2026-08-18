"""Deterministic Latency Benchmark for NOVARON Language Router (Loop 14C-5).
Measures P50, P95, and MAX routing/detection latency across all 15 languages.
"""
from __future__ import annotations

import statistics
import time
from app.router import classify_query, detect_language

SAMPLE_QUERIES = [
    "What is artificial intelligence and machine learning in computer science?",
    "সালোক সংশ্লেষণ কিদৰে হয়?",
    "সালোকসংশ্লেষণ কী এবং কিভাবে হয়?",
    "કૃત્રિમ બુદ્ધિ શું છે?",
    "कृत्रिम बुद्धिमत्ता क्या है और यह कैसे काम करती है?",
    "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಎಂದರೇನು?",
    "പ്രകാശസംശ്ലേഷണം എന്താണ്?",
    "प्रकाशसंश्लेषण म्हणजे काय आणि ते कसे होते?",
    "प्रकाश संश्लेषण भनेको के हो?",
    "ଆଲୋକ ସଂଶ୍ଳେଷଣ କଣ?",
    "ਪ੍ਰਕਾਸ਼ ਸੰਸਲੇਸ਼ਣ ਕੀ ਹੈ?",
    "प्रकाशसंश्लेषणं किम् अस्ति?",
    "செயற்கை நுண்ணறிவு என்றால் என்ன?",
    "కృత్రిమ మేధస్సు అంటే ఏమిటి?",
    "مصنوعی ذہانت کیا ہے؟",
    "Hello NOVARON!",
    "Who are you?",
    "आपका नाम क्या है?",
    "మీ పేరు ఏమిటి?",
    "Thank you very much",
]


def benchmark_router(runs_per_query: int = 100) -> dict:
    latencies_ms = []
    # Warmup
    for q in SAMPLE_QUERIES:
        for _ in range(5):
            classify_query(q)

    for _ in range(runs_per_query):
        for q in SAMPLE_QUERIES:
            t0 = time.perf_counter()
            classify_query(q)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            latencies_ms.append(elapsed_ms)

    latencies_ms.sort()
    n = len(latencies_ms)
    p50 = latencies_ms[int(n * 0.50)]
    p95 = latencies_ms[int(n * 0.95)]
    max_lat = latencies_ms[-1]

    return {
        "p50": round(p50, 4),
        "p95": round(p95, 4),
        "max": round(max_lat, 4),
        "mean": round(statistics.mean(latencies_ms), 4),
        "samples": n,
    }


if __name__ == "__main__":
    res = benchmark_router()
    print("Router Latency Benchmark Results:")
    print(f"  P50:  {res['p50']} ms")
    print(f"  P95:  {res['p95']} ms")
    print(f"  MAX:  {res['max']} ms")
    print(f"  Mean: {res['mean']} ms across {res['samples']} measurements")
