# NOVARON — Final Release Snapshot (Loop 14C-11)

**Release Date:** 2026-08-18 09:30:00 UTC  
**Git Commit:** `9cf94ba9e6eff5bd83eb1538858101abf00cc3e5`  
**System Status:** **FROZEN & HACKATHON DEMO READY**  

---

## 1. Knowledge Base & Corpus Composition

- **Total Documents:** `12,184`
  - Curated Knowledge Documents: `184`
  - AI4Bharat MSMARCO-XI Documents: `12,000` (800 per language)
- **Supported Languages (15):** `en, as, bn, gu, hi, kn, ml, mr, ne, or, pa, sa, ta, te, ur`
- **Chunk Corpora:**
  - Sentence: `12,206` chunks
  - Fixed: `12,231` chunks
  - Hierarchical: `24,414` chunks

---

## 2. Retrieval Architecture & Indexes

- **Embedding Model:** `intfloat/multilingual-e5-small` (384 dimensions, FP32)
- **FAISS Vector Store:** `IndexFlatIP` with L2 unit normalization
  - Sentence FAISS: `12,206` vectors (17.88 MB RAM)
  - Fixed FAISS: `12,231` vectors (17.91 MB RAM)
  - Hierarchical FAISS: `24,414` vectors (35.80 MB RAM)
- **Lexical Index:** BM25 inverted index across sentence chunks
- **Hybrid Fusion:** Reciprocal Rank Fusion (RRF) with constant `k=60`
- **Candidate Filtering:** Wide candidate pool search (`k=600`) + language-aware candidate filtering

---

## 3. Verified Benchmark Results

### Cross-Lingual Indic → English Retrieval (322 Valid Evaluation Pairs)
- **Baseline Recall@10:** `1.2%` (MRR `0.006`)
- **Language-Aware Candidate Filtering Recall@10:** **`62.7%`** (MRR **`0.359`**)
- **Recall@1:** `25.8%`, **Recall@3:** `39.8%`, **Recall@5:** `47.2%`
- **Language Threshold:** 12/14 Indic languages achieved >= 50% Recall@10 (Bengali: 78.3%, Malayalam: 78.3%, Hindi: 73.9%, Telugu: 73.9%, Kannada: 65.2%, Marathi: 65.2%, Nepali: 65.2%, Tamil: 65.2%, Gujarati: 60.9%, Punjabi: 60.9%, Odia: 56.5%, Urdu: 56.5%).

### Monolingual Retrieval (300 MSMARCO-XI Evaluation Queries)
- **Hybrid + Rerank Recall@10:** `66.3%` (MRR `0.323`)
- **Monolingual Hybrid Recall@5:** `55.7%`

---

## 4. Latency Telemetry (15 Languages Measured)

| Pipeline Stage | P50 (ms) | P95 (ms) | Target Met |
|---|---|---|---|
| **Language Router** | `0.05 ms` | `0.06 ms` | PASS (< 5.0 ms) |
| **E5 Embedding (Query)** | `14.30 ms` | `16.56 ms` | PASS (< 30.0 ms) |
| **FAISS Dense Search** | `1.21 ms` | `1.54 ms` | PASS (< 10.0 ms) |
| **Candidate Filtering** | `1.76 ms` | `2.17 ms` | PASS (< 5.0 ms) |
| **Total Dense Retrieval** | `16.07 ms` | `18.54 ms` | PASS (< 50.0 ms P50, < 100.0 ms P95) |
| **Filtering Overhead** | `+0.55 ms` | `+0.63 ms` | PASS (< 5.0 ms overhead) |
| **Voice Pipeline E2E** | `196.97 ms` | `221.13 ms` | PASS (< 500.0 ms) |

---

## 5. Test Suite & Build Verification

- **Backend Pytest Suite:** `124/124 passed (100%)`
- **Language Routing Tests:** `19/19 passed`
- **Cross-Lingual Retrieval Tests:** `15/15 passed`
- **Corpus Contract Validation:** `PASS`
- **Index Integrity Validation:** `PASS`
- **Frontend Production Build:** `PASS (0 errors, 0 warnings)`
- **Console & Network Errors:** `0`
- **Critical Blockers:** `0`
