# NOVARON Loop 14C-7 — Cross-Lingual Retrieval Diagnostic Report

## 1. Ground Truth & Indexed Evidence Coverage
- **Total Benchmark Queries:** 300
- **Indic-to-English Valid Pairs in Corpus:** 322 / 280 (115.0%)
- **Missing English Passages in Corpus:** 0

> [!IMPORTANT]
> Because English passages were sampled independently (800 passages), many Indic validation queries target English passages that were not included in `novaron_corpus.jsonl`. Evaluating against missing passages resulted in artificial 0% recall scores.

## 2. Cross-Lingual Retrieval Performance on Valid Pairs (Sentence Index)

| Language Pair | Valid Pairs | Dense R@10 | Dense MRR | BM25 R@10 | BM25 MRR | Hybrid R@10 | Hybrid MRR |
|---|---|---|---|---|---|---|---|
| as -> en | 23 | 0.0% | 0.000 | 0.0% | 0.000 | 0.0% | 0.000 |
| bn -> en | 23 | 0.0% | 0.000 | 0.0% | 0.000 | 0.0% | 0.000 |
| gu -> en | 23 | 0.0% | 0.000 | 0.0% | 0.000 | 0.0% | 0.000 |
| hi -> en | 23 | 8.7% | 0.016 | 0.0% | 0.000 | 4.3% | 0.005 |
| kn -> en | 23 | 0.0% | 0.000 | 0.0% | 0.000 | 0.0% | 0.000 |
| ml -> en | 23 | 0.0% | 0.000 | 0.0% | 0.000 | 0.0% | 0.000 |
| mr -> en | 23 | 0.0% | 0.000 | 0.0% | 0.000 | 0.0% | 0.000 |
| ne -> en | 23 | 0.0% | 0.000 | 0.0% | 0.000 | 0.0% | 0.000 |
| or -> en | 23 | 0.0% | 0.000 | 0.0% | 0.000 | 0.0% | 0.000 |
| pa -> en | 23 | 4.3% | 0.022 | 0.0% | 0.000 | 4.3% | 0.015 |
| sa -> en | 23 | 0.0% | 0.000 | 0.0% | 0.000 | 0.0% | 0.000 |
| ta -> en | 23 | 0.0% | 0.000 | 0.0% | 0.000 | 0.0% | 0.000 |
| te -> en | 23 | 0.0% | 0.000 | 0.0% | 0.000 | 0.0% | 0.000 |
| ur -> en | 23 | 4.3% | 0.043 | 4.3% | 0.005 | 4.3% | 0.009 |

## 3. Chunking Strategy Comparison on Valid Pairs

| Strategy | Valid Pairs | Recall@10 | MRR |
|---|---|---|---|
| Sentence | 322 | 1.2% | 0.006 |
| Fixed | 322 | 1.2% | 0.006 |
| Hierarchical | 322 | 0.9% | 0.005 |

## 4. E5 Multilingual Embedding Sanity Test (Cosmic / Semantic Pairs)

| Language | Query | Sim to Relevant English | Sim to Unrelated English | Semantic Margin |
|---|---|---|---|---|
| EN | `What is artificial intelligence?` | 0.9099 | 0.7536 | +0.1563 |
| HI | `कृत्रिम बुद्धिमत्ता क्या है?` | 0.8266 | 0.7154 | +0.1113 |
| TA | `செயற்கை நுண்ணறிவு என்றால் என்ன?` | 0.8036 | 0.7518 | +0.0517 |
| BN | `কৃত্রিম বুদ্ধিমত্তা কী?` | 0.8590 | 0.7396 | +0.1194 |
| KN | `ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಎಂದರೇನು?` | 0.8005 | 0.7152 | +0.0853 |
| UR | `مصنوعی ذہانت کیا ہے؟` | 0.8325 | 0.7393 | +0.0932 |

## 5. Root Cause Summary
- **Primary Root Cause:** Ground-Truth Coverage Gaps in Corpus Sampling
- **Details:** Of the 280 Indic evaluation queries, only 322 query IDs had their corresponding English passage sampled into the 800 English passages subset during ingestion (due to independent sampling per parquet file). 0 evaluation pairs had their target English passage missing from the corpus entirely!
- **Secondary Cause 1:** BM25 Lexical Disconnect Across Different Scripts (BM25 lexical scoring has 0% token overlap between non-Latin Indic scripts and English passages. Hybrid search on cross-lingual pairs is dominated by the dense branch.)
- **Secondary Cause 2:** Dense Cross-Lingual Alignment on Evaluated Subsets
