# NOVARON Voice RAG

NOVARON is a multilingual, grounded Voice RAG system. RAG Core v0.2 keeps the dependency-free v0.1 baseline while adding optional provider-backed embeddings, persistent FAISS indexes, cross-encoder reranking, and structured grounded generation.

## Architecture

```text
JSONL corpus → selected chunker → embedding provider → persisted FAISS index
                                      ↘ BM25 ↗
query → dense / BM25 → reciprocal-rank fusion → optional reranker → evidence guardrail
      → extractive or grounded LLM answer → sources + stage latency
```

The API remains backward-compatible: `POST /v1/query` still accepts `query`, `top_k`, and `chunking_strategy`. It additionally accepts `retrieval_mode`: `dense`, `bm25`, `hybrid`, or `hybrid_rerank` (the default).

## Baseline versus production retrieval

| Capability | Baseline | Provider-backed option |
| --- | --- | --- |
| Dense vectors | Local hashing vectors | Multilingual SentenceTransformer + FAISS |
| Reranking | Transparent lexical overlap | SentenceTransformers cross-encoder |
| Answering | Extractive top evidence | OpenAI-compatible structured grounded adapter |
| Storage | In-memory | Persisted `index.faiss`, `chunks.json`, and manifest |

No production adapter is activated by default. This lets the project run without a model download or secret, and ensures baseline benchmarks remain comparable.

## Setup

1. Use Python 3.11+ and create a virtual environment.
2. Install `pip install -r backend/requirements.txt`.
3. Copy `.env.example` to `.env` and select only the providers you have configured.
4. From `backend`, run `uvicorn app.main:app --reload`.

The fixture corpus is deliberately tiny and is only for smoke tests. It is not MSMARCO-XI and cannot establish production quality.

## Build a FAISS index

The server never rebuilds an index at startup. Build each chunking strategy explicitly:

```bash
cd backend
python -m scripts.build_index --strategy fixed --index-dir ../data/indexes/fixed
python -m scripts.build_index --strategy sentence --index-dir ../data/indexes/sentence
python -m scripts.build_index --strategy hierarchical --index-dir ../data/indexes/hierarchical
```

Then configure `DENSE_RETRIEVER=faiss` and `VECTOR_INDEX_DIR=data/indexes`. The embedding model used at query time must match the model used when building the index.

## Benchmark and tests

From `backend`:

```bash
python -m scripts.benchmark
python -m pytest tests -q
```

The benchmark reports Recall@3, MRR@3, p50, and p95 per English, Hindi, and Kannada fixture query. FAISS comparisons are explicitly reported as unavailable until their matching index is built; no results are fabricated.

## Refusal and Guardrail Protections (Phase 8)

NOVARON enforces strict grounding and refusal guardrails to ensure reliable, unhallucinated responses:

- **Evidence-Based Refusal**: When retrieved evidence scores fall below the relevance threshold or no evidence supports the query, the pipeline returns a standardized refusal message (`"I don't have enough information in the indexed knowledge base to answer that reliably."`) with `refused=true` and empty sources.
- **Strict Citation Enforcement**: Grounded LLM responses validate returned `citation_chunk_ids` against actual retrieved evidence hits. Uncited, partially invalid, or empty/whitespace non-refused answers are refused. Structured output schemas guarantee that a refusal never crashes Pydantic validation.
- **Prompt Injection Defense**: Retrieved evidence is treated strictly as untrusted data and isolated within JSON payloads in user messages, never interpolated into system prompt instructions. System prompts explicitly instruct the model to disregard instructions embedded in evidence.
- **Phase 8 Guardrail Test Suite**: Located in `backend/tests/test_refusal_guardrails.py`, testing five canonical scenarios:
  - **Case A**: Relevant question with supporting evidence $\to$ grounded answer with valid citations.
  - **Case B**: Query with weak retrieval evidence $\to$ pipeline refusal.
  - **Case C**: Completely unrelated query $\to$ pipeline refusal.
  - **Case D**: Unsupported claim with topical evidence $\to$ model-level refusal.
  - **Case E**: Adversarial prompt injection inside retrieved document $\to$ treated as passive data, instructions ignored, fabricated citations blocked.

## Environment variables

- `DENSE_RETRIEVER`: `hashing` (default) or `faiss`
- `EMBEDDING_MODEL`, `EMBEDDING_DEVICE`, `EMBEDDING_BATCH_SIZE`: multilingual embedding configuration
- `VECTOR_INDEX_DIR`: parent directory for strategy-specific FAISS indexes
- `RERANKER_PROVIDER`: `transparent` (default) or `cross_encoder`
- `RERANKER_MODEL`: cross-encoder model name
- `LLM_PROVIDER`: `extractive` (default) or `openai`
- `LLM_MODEL`, `OPENAI_API_KEY`: grounded generation configuration
- `MIN_RELEVANCE_SCORE`, `MIN_UNRERANKED_RELEVANCE_SCORE`: evidence thresholds

All secrets belong in environment variables; none are stored in source code.

## Known limitations

- **Tiny Fixture Corpus**: The 6-passage fixture corpus (`data/fixtures/sample_corpus.jsonl`) is a minimal smoke test for sanity checking pipelines. Due to tiny corpus size, BM25 IDF weights common shared words heavily; negative query tests use zero-overlap vocabulary. Production thresholds must be calibrated against the target MSMARCO-XI evaluation set.
- **Provider Prerequisites**: Real SentenceTransformer, cross-encoder, and OpenAI provider paths require model downloads/credentials and must be benchmarked on target hardware and datasets.
- **Text-Only Core**: The current API is text-only by design; voice/STT integration is deliberately deferred until RAG grounding is fully verified.

