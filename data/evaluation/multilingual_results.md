# NOVARON Loop 14C — Multilingual Retrieval Evaluation Report

**Generated:** 2026-08-18 08:11:44 UTC  
**Embedding Model:** `intfloat/multilingual-e5-small` (384 dimensions, IndexFlatIP)  
**Total Benchmark Queries:** 300  

## 1. Monolingual Retrieval Performance (Hybrid Mode)

| Language | Code | Queries | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR |
|---|---|---|---|---|---|---|---|
| EN | `en` | 20 | 35.0% | 65.0% | 85.0% | 100.0% | 0.543 |
| AS | `as` | 20 | 15.0% | 35.0% | 35.0% | 60.0% | 0.277 |
| BN | `bn` | 20 | 5.0% | 30.0% | 55.0% | 60.0% | 0.223 |
| GU | `gu` | 20 | 25.0% | 45.0% | 45.0% | 65.0% | 0.361 |
| HI | `hi` | 20 | 5.0% | 35.0% | 55.0% | 60.0% | 0.233 |
| KN | `kn` | 20 | 5.0% | 20.0% | 35.0% | 45.0% | 0.152 |
| ML | `ml` | 20 | 30.0% | 50.0% | 60.0% | 75.0% | 0.441 |
| MR | `mr` | 20 | 20.0% | 35.0% | 40.0% | 55.0% | 0.287 |
| NE | `ne` | 20 | 15.0% | 25.0% | 35.0% | 45.0% | 0.237 |
| OR | `or` | 20 | 10.0% | 35.0% | 50.0% | 60.0% | 0.233 |
| PA | `pa` | 20 | 5.0% | 35.0% | 40.0% | 50.0% | 0.189 |
| SA | `sa` | 20 | 5.0% | 5.0% | 20.0% | 25.0% | 0.093 |
| TA | `ta` | 20 | 20.0% | 40.0% | 45.0% | 60.0% | 0.319 |
| TE | `te` | 20 | 25.0% | 30.0% | 40.0% | 65.0% | 0.328 |
| UR | `ur` | 20 | 35.0% | 50.0% | 50.0% | 60.0% | 0.424 |

## 2. Cross-Lingual Retrieval Performance (Indic Query -> English Passage)

| Language Pair | Mode | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR |
|---|---|---|---|---|---|---|
| as -> en | dense | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |
| bn -> en | dense | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |
| gu -> en | dense | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |
| hi -> en | dense | 0.0% | 0.0% | 5.0% | 10.0% | 0.018 |
| kn -> en | dense | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |
| ml -> en | dense | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |
| mr -> en | dense | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |
| ne -> en | dense | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |
| or -> en | dense | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |
| pa -> en | dense | 0.0% | 5.0% | 5.0% | 5.0% | 0.025 |
| sa -> en | dense | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |
| ta -> en | dense | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |
| te -> en | dense | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |
| ur -> en | dense | 5.0% | 5.0% | 5.0% | 5.0% | 0.050 |

## 3. Retrieval Mode Overall Comparison

| Mode | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR | Avg Latency |
|---|---|---|---|---|---|---|
| dense | 16.3% | 28.7% | 35.0% | 44.3% | 0.241 | 16.00 ms |
| bm25 | 9.0% | 26.7% | 34.7% | 48.0% | 0.200 | 183.60 ms |
| hybrid | 17.0% | 35.7% | 46.0% | 59.0% | 0.289 | 246.43 ms |
| hybrid_rerank | 17.7% | 39.3% | 55.7% | 66.3% | 0.323 | 229.53 ms |

## 4. Latency Telemetry

- **P50:** 167.72 ms
- **P95:** 328.36 ms
- **MAX:** 636.93 ms
- **Evaluated Query Invocations:** 2960
