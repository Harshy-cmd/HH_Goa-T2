import json
import statistics
import sys
import time
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"


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


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * pct
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return round(d0 + d1, 2)


def stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {}
    return {
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "p95": percentile(values, 0.95),
    }


def main():
    print("==================================================")
    print("NOVARON 20-REQUEST GENERATION BENCHMARK")
    print("==================================================")
    payload = {
        "query": "What is photosynthesis?",
        "top_k": 3,
        "retrieval_mode": "dense",
        "chunking_strategy": "sentence",
    }

    walls = []
    generations = []
    rag_totals = []
    retrievals = []
    embeddings = []
    faiss_times = []

    for i in range(1, 21):
        status, body, wall_ms = send_post("/v1/query", payload)
        assert status == 200
        lat = body.get("latency_ms", {})
        gen_ms = lat.get("generation", 0.0)
        rag_ms = lat.get("rag_total", 0.0)
        ret_ms = lat.get("retrieval", 0.0)
        emb_ms = lat.get("embedding", 0.0)
        fai_ms = lat.get("faiss", 0.0)

        walls.append(wall_ms)
        generations.append(gen_ms)
        rag_totals.append(rag_ms)
        retrievals.append(ret_ms)
        embeddings.append(emb_ms)
        faiss_times.append(fai_ms)

        print(
            f"Run {i:2d}: Wall = {wall_ms:7.2f}ms | Generation = {gen_ms:7.2f}ms | "
            f"Retrieval = {ret_ms:5.2f}ms (Emb: {emb_ms:5.2f}ms, FAISS: {fai_ms:4.2f}ms) | "
            f"RAG Total = {rag_ms:7.2f}ms"
        )

    print("\n==================================================")
    print("20-REQUEST BENCHMARK STATISTICAL SUMMARY")
    print("==================================================")
    print("Generation Latency (ms):", stats(generations))
    print("Retrieval Latency  (ms):", stats(retrievals))
    print("Embedding Latency  (ms):", stats(embeddings))
    print("FAISS Latency      (ms):", stats(faiss_times))
    print("Total RAG Latency  (ms):", stats(rag_totals))
    print("HTTP Wall-Clock    (ms):", stats(walls))


if __name__ == "__main__":
    main()
