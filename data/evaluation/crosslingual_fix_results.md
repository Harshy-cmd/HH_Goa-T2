# NOVARON Loop 14C-8 — Cross-Lingual Retrieval Fix Experiment Report

## 1. Overall Cross-Lingual Performance (322 Valid Indic -> English Pairs)

| Method | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR |
|---|---|---|---|---|---|
| Baseline (Mixed Dense) | 0.3% | 0.6% | 0.9% | 1.2% | 0.006 |
| Experiment A (Filtered k=300) | 23.6% | 35.7% | 41.6% | 51.2% | 0.318 |
| Experiment B (Filtered k=600) | 25.8% | 39.8% | 47.2% | 62.7% | 0.359 |
| Experiment C (Hybrid+Rerank k=600) | 25.5% | 39.4% | 47.2% | 62.7% | 0.356 |

## 2. Per-Language Comparison (Baseline vs Experiment B)

| Language | Pairs | Baseline R@10 | Exp B R@10 | Exp C R@10 | Improvement |
|---|---|---|---|---|---|
| `as` | 23 | 0.0% | 26.1% | 26.1% | **+26.1%** |
| `bn` | 23 | 0.0% | 78.3% | 78.3% | **+78.3%** |
| `gu` | 23 | 0.0% | 60.9% | 60.9% | **+60.9%** |
| `hi` | 23 | 8.7% | 73.9% | 73.9% | **+65.2%** |
| `kn` | 23 | 0.0% | 65.2% | 65.2% | **+65.2%** |
| `ml` | 23 | 0.0% | 78.3% | 78.3% | **+78.3%** |
| `mr` | 23 | 0.0% | 65.2% | 65.2% | **+65.2%** |
| `ne` | 23 | 0.0% | 65.2% | 65.2% | **+65.2%** |
| `or` | 23 | 0.0% | 56.5% | 56.5% | **+56.5%** |
| `pa` | 23 | 4.3% | 60.9% | 60.9% | **+56.5%** |
| `sa` | 23 | 0.0% | 52.2% | 52.2% | **+52.2%** |
| `ta` | 23 | 0.0% | 65.2% | 65.2% | **+65.2%** |
| `te` | 23 | 0.0% | 73.9% | 73.9% | **+73.9%** |
| `ur` | 23 | 4.3% | 56.5% | 56.5% | **+52.2%** |

## 3. Latency Telemetry

| Method | P50 Latency | P95 Latency | MAX Latency |
|---|---|---|---|
| Baseline (Mixed Dense) | 15.65 ms | 18.13 ms | 21.58 ms |
| Experiment A (Filtered k=300) | 15.87 ms | 18.62 ms | 25.88 ms |
| Experiment B (Filtered k=600) | 15.88 ms | 18.24 ms | 20.15 ms |
| Experiment C (Hybrid+Rerank k=600) | 227.37 ms | 362.32 ms | 483.37 ms |
