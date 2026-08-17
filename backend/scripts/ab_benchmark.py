import json
import os
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.generation import OpenAIGroundedLLM
from app.main import pipelines

p = pipelines["sentence"]["dense"]
hits = p.retriever.search("What is photosynthesis?", 3)


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


def benchmark_model(model_name: str, n_requests: int = 10):
    print(f"\n==================================================")
    print(f"BENCHMARKING: {model_name} ({n_requests} requests)")
    print(f"==================================================")
    gen = OpenAIGroundedLLM(model=model_name)
    client = gen._client_instance()
    prompt = gen._prompt("What is photosynthesis?", hits)

    durations = []
    reasoning_toks_list = []
    queue_times = []
    comp_times = []
    prompt_tokens_list = []
    comp_tokens_list = []

    for i in range(1, n_requests + 1):
        t0 = time.perf_counter()
        resp = client.chat.completions.create(
            model=model_name,
            messages=prompt,
            response_format={"type": "json_object"},
            temperature=0,
        )
        t1 = time.perf_counter()
        duration_ms = (t1 - t0) * 1000
        durations.append(duration_ms)

        usage = resp.usage
        prompt_tokens_list.append(usage.prompt_tokens if usage else 0)
        comp_tokens_list.append(usage.completion_tokens if usage else 0)

        details = getattr(usage, "completion_tokens_details", None)
        reasoning_toks = getattr(details, "reasoning_tokens", None) if details else None
        if reasoning_toks is not None:
            reasoning_toks_list.append(reasoning_toks)

        q_time = getattr(usage, "queue_time", None)
        if q_time is not None:
            queue_times.append(q_time)

        c_time = getattr(usage, "completion_time", None)
        if c_time is not None:
            comp_times.append(c_time)

        print(
            f"Run {i:2d}: Latency = {duration_ms:6.1f}ms | "
            f"PromptToks = {usage.prompt_tokens if usage else 0} | "
            f"CompToks = {usage.completion_tokens if usage else 0} (Reasoning = {reasoning_toks}) | "
            f"Queue = {q_time}s | CompTime = {c_time}s"
        )

    return {
        "model": model_name,
        "latency_stats": stats(durations),
        "prompt_tokens_mean": round(statistics.mean(prompt_tokens_list), 1) if prompt_tokens_list else 0,
        "comp_tokens_mean": round(statistics.mean(comp_tokens_list), 1) if comp_tokens_list else 0,
        "reasoning_tokens_mean": round(statistics.mean(reasoning_toks_list), 1) if reasoning_toks_list else "N/A",
        "queue_time_mean": round(statistics.mean(queue_times), 3) if queue_times else "N/A",
        "comp_time_mean": round(statistics.mean(comp_times), 3) if comp_times else "N/A",
    }


def main():
    results = {}
    for m in ["openai/gpt-oss-20b", "groq/compound-mini"]:
        results[m] = benchmark_model(m, 10)

    print("\n==================================================")
    print("A/B COMPARISON TABLE")
    print("==================================================")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
