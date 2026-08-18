# NOVARON Loop 14C-9 — Full Multilingual Latency & Performance Report

**Generated:** 2026-08-18 08:56:43 UTC  
**Languages Tested:** `en, hi, bn, ta, te, kn, ml, mr, gu, pa, or, ur, as, ne, sa`  
**Total Measured Samples:** 480 (after 3 warmup passes)  
**Embedding Provider:** `intfloat/multilingual-e5-small` (384 dimensions)  

---

## 1. Stage-by-Stage Latency Breakdown

| Pipeline Stage | P50 (ms) | P70 (ms) | P95 (ms) | P99 (ms) | MAX (ms) | Mean (ms) |
|---|---|---|---|---|---|---|
| **Language Detection** | 0.01 | 0.01 | 0.02 | 0.02 | 0.05 | 0.01 |
| **Query Routing** | 0.05 | 0.05 | 0.06 | 0.07 | 0.11 | 0.05 |
| **E5 Embedding (Query)** | 14.3 | 14.96 | 16.56 | 19.62 | 35.66 | 14.42 |
| **FAISS Dense Search** | 1.21 | 1.3 | 1.54 | 1.7 | 1.99 | 1.24 |
| **Lang-Aware Filtering** | 1.76 | 1.94 | 2.17 | 2.41 | 2.83 | 1.83 |
| **BM25 Inverted Search** | 242.54 | 262.32 | 344.15 | 445.72 | 474.22 | 239.57 |
| **RRF Score Fusion** | 0.04 | 0.04 | 0.05 | 0.07 | 0.1 | 0.04 |
| **Reranking** | 0.42 | 0.52 | 0.93 | 1.41 | 1.46 | 0.51 |
| **Grounded Generation** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| **TTS Synthesis** | 0.02 | 0.02 | 0.03 | 0.09 | 0.09 | 0.02 |

---

## 2. End-to-End Pipeline Performance

| Modality | P50 (ms) | P70 (ms) | P95 (ms) | P99 (ms) | MAX (ms) |
|---|---|---|---|---|---|
| **Dense Retrieval Baseline** | 15.51 | 16.22 | 17.85 | 21.03 | 37.36 |
| **Lang-Aware Retrieval** | 16.07 | 16.81 | 18.54 | 21.43 | 38.49 |
| **Full Hybrid Retrieval** | 258.43 | 278.86 | 360.4 | 462.12 | 489.98 |
| **Text E2E (Router + Retrieval + Gen)** | 258.48 | 278.91 | 360.45 | 462.18 | 490.03 |
| **Voice E2E (STT + RAG + TTS)** | 196.97 | 206.5 | 221.13 | 221.15 | 221.15 |

---

## 3. Candidate Filtering Overhead Analysis

- **Baseline FAISS Search (k=10):** P50: `1.21 ms`, P95: `1.54 ms`
- **Language-Aware Filtered Search (k=600):** P50: `1.76 ms`, P95: `2.17 ms`
- **Measured Net Overhead:** `+0.55 ms` (P50), `+0.63 ms` (P95)

---

## 4. Resource Profile

- **Indexed FAISS Vectors:** `12,206` vectors (17.88 MB in RAM)
- **Indexed Chunks:** `12,206` chunks
- **Embedding Model Footprint:** ~`133.0 MB`
