import json
import statistics
import sys
import time
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"


def send_get(path: str) -> tuple[int, dict, float]:
    t0 = time.perf_counter()
    req = urllib.request.Request(f"{BASE_URL}{path}", method="GET")
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        status = resp.status
    t1 = time.perf_counter()
    return status, body, (t1 - t0) * 1000


def send_post(path: str, payload: dict) -> tuple[int, dict, float]:
    data = json.dumps(payload).encode("utf-8")
    t0 = time.perf_counter()
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        status = resp.status
    t1 = time.perf_counter()
    return status, body, (t1 - t0) * 1000


def stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {}
    return {
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
    }


def main():
    print("==================================================")
    print("1. HEALTH CHECK")
    print("==================================================")
    status, body, wall_ms = send_get("/health")
    print(f"Status: {status} | Wall: {wall_ms:.2f}ms | Response: {body}")
    assert status == 200, f"Health check failed with {status}"

    print("\n==================================================")
    print("2. COLD START QUERY (First post-startup query)")
    print("==================================================")
    payload_cold = {
        "query": "What is photosynthesis?",
        "top_k": 3,
        "retrieval_mode": "dense",
        "chunking_strategy": "sentence",
    }
    status, body, cold_wall_ms = send_post("/v1/query", payload_cold)
    print(f"Status: {status} | Wall: {cold_wall_ms:.2f}ms")
    print(f"Refused: {body.get('refused')} | Strategy: {body.get('retrieval_strategy')}")
    print(f"Latency telemetry (ms): {body.get('latency_ms')}")
    print(f"Sources returned: {len(body.get('sources', []))}")
    print(f"Answer: {body.get('answer')[:120]}...")

    print("\n==================================================")
    print("3. WARM REQUESTS: 10 CONSECUTIVE ENGLISH QUERIES")
    print("==================================================")
    en_walls = []
    en_latencies = []
    for i in range(1, 11):
        status, body, wall_ms = send_post("/v1/query", payload_cold)
        en_walls.append(wall_ms)
        en_latencies.append(body.get("latency_ms", {}))
        print(f"Request {i:2d}: Wall: {wall_ms:6.2f}ms | Telemetry: {body.get('latency_ms')}")

    print("\nEnglish 10-Request Summary:")
    print("Wall Time (ms):", stats(en_walls))
    for key in ["embedding", "faiss", "retrieval", "generation", "rag_total"]:
        vals = [lat.get(key, 0.0) for lat in en_latencies if key in lat]
        if vals:
            print(f"{key:<12} (ms):", stats(vals))

    print("\n==================================================")
    print("4. WARM REQUESTS: 10 CONSECUTIVE HINDI QUERIES")
    print("==================================================")
    payload_hi = {
        "query": "प्रकाश संश्लेषण क्या है?",
        "top_k": 3,
        "retrieval_mode": "dense",
        "chunking_strategy": "sentence",
    }
    hi_walls = []
    hi_latencies = []
    for i in range(1, 11):
        status, body, wall_ms = send_post("/v1/query", payload_hi)
        hi_walls.append(wall_ms)
        hi_latencies.append(body.get("latency_ms", {}))
        print(f"Request {i:2d}: Wall: {wall_ms:6.2f}ms | Telemetry: {body.get('latency_ms')}")

    print(f"Hindi Answer: {body.get('answer')[:120]}...")
    print("\nHindi 10-Request Summary:")
    print("Wall Time (ms):", stats(hi_walls))
    for key in ["embedding", "faiss", "retrieval", "generation", "rag_total"]:
        vals = [lat.get(key, 0.0) for lat in hi_latencies if key in lat]
        if vals:
            print(f"{key:<12} (ms):", stats(vals))

    print("\n==================================================")
    print("5. REFUSAL GUARDRAILS TEST")
    print("==================================================")
    payload_refusal = {
        "query": "What is the exact recipe for Martian cosmic space cake?",
        "top_k": 3,
        "retrieval_mode": "dense",
        "chunking_strategy": "sentence",
    }
    status, body, ref_wall_ms = send_post("/v1/query", payload_refusal)
    print(f"Status: {status} | Wall: {ref_wall_ms:.2f}ms")
    print(f"Refused: {body.get('refused')} | Sources count: {len(body.get('sources', []))}")
    print(f"Answer: {body.get('answer')}")
    print(f"Latency telemetry: {body.get('latency_ms')}")
    assert body.get("refused") is True, "Expected refused=True"
    assert "reliably" in body.get("answer", "").lower() or "enough information" in body.get("answer", "").lower()

    print("\n==================================================")
    print("6. ALL 12 PIPELINE CONFIGURATIONS (Strategy × Mode)")
    print("==================================================")
    strategies = ["sentence", "fixed", "hierarchical"]
    modes = ["dense", "bm25", "hybrid", "hybrid_rerank"]
    for strat in strategies:
        for mode in modes:
            payload = {
                "query": "What is photosynthesis?",
                "top_k": 3,
                "retrieval_mode": mode,
                "chunking_strategy": strat,
            }
            status, body, wall_ms = send_post("/v1/query", payload)
            print(f"Strat: {strat:<12} | Mode: {mode:<14} | Wall: {wall_ms:6.2f}ms | Latency: {body.get('latency_ms')}")

    print("\nAll benchmark tests executed successfully against live backend!")


if __name__ == "__main__":
    main()
