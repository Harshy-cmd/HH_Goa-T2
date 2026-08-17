# NOVARON Voice RAG

<p align="center">
  <strong>Production-Ready, Multilingual, Grounded Voice-to-Voice RAG System</strong><br>
  <em>High-precision multilingual dense retrieval, grounded LLM generation, strict refusal guardrails, and real-time STT/TTS pipelines.</em>
</p>

---

## Overview

**NOVARON Voice RAG** is an end-to-end multilingual conversational intelligence system built for high-accuracy question answering across **English** and **Hindi**. It seamlessly converts spoken user audio into grounded answers with verified citations and returns natural, synthesized voice audio while strictly preventing hallucinations and prompt injections.

### Key Highlights
- **End-to-End Voice Pipeline**: Full Voice-to-Voice (`Audio Input` $\to$ `STT` $\to$ `Sentence FAISS` $\to$ `Grounded LLM` $\to$ `Evidence Guard` $\to$ `TTS` $\to$ `MP3 Audio`).
- **Multilingual Dense Retrieval**: Production `intfloat/multilingual-e5-small` embeddings indexed in high-performance cosine FAISS vector stores.
- **Strict Grounding & Citation Validation**: Answers are strictly validated against retrieved evidence hits. Unsupported questions are safely refused with standardized refusal messages.
- **Prompt-Injection Defense**: Evidence is isolated into passive data payloads, blocking untrusted retrieved content from overriding system instructions.
- **Real-Time Latency Tracking**: Granular stage-wise latency tracking (`stt`, `retrieval`, `reranking`, `generation`, `tts`, `rag_total`, `total`).
- **Offline & CI Determinism**: Includes `MockSTT` and `MockTTS` adapters alongside production provider implementations, enabling 100% offline unit/integration test coverage (73/73 tests passing).

---

## System Architecture

```text
                                  ┌────────────────────────┐
                                  │   User Spoken Audio    │
                                  └───────────┬────────────┘
                                              │
                                              ▼
                                  ┌────────────────────────┐
                                  │   Speech-to-Text       │
                                  │   (Groq Whisper Turbo) │
                                  └───────────┬────────────┘
                                              │ Transcript
                                              ▼
┌───────────────────────┐         ┌────────────────────────┐
│ Indexed Vector Store  │ ──────► │ Sentence FAISS Dense   │
│ (Multilingual E5 384) │         │ Retrieval              │
└───────────────────────┘         └───────────┬────────────┘
                                              │ Evidence Chunks
                                              ▼
                                  ┌────────────────────────┐
                                  │ Evidence Relevance     │
                                  │ & Grounding Guardrail  │
                                  └───────────┬────────────┘
                                              │ Validated Evidence
                                              ▼
                                  ┌────────────────────────┐
                                  │ Grounded LLM           │
                                  │ (Groq GPT-OSS 20B)     │
                                  └───────────┬────────────┘
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       │                                             │
             [Sufficient Evidence]                         [Insufficient Evidence]
                       ▼                                             ▼
         ┌───────────────────────────┐                 ┌───────────────────────────┐
         │ Grounded Text Answer      │                 │ Standard Refusal Text     │
         │ + Verified Citations      │                 │ (sources = [])            │
         └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                       │                                             │
                       └──────────────────────┬──────────────────────┘
                                              │
                                              ▼
                                  ┌────────────────────────┐
                                  │ Text-to-Speech         │
                                  │ (Edge Neural TTS / MP3)│
                                  └───────────┬────────────┘
                                              │
                                              ▼
                                  ┌────────────────────────┐
                                  │ Playable Audio Output  │
                                  └────────────────────────┘
```

---

## Production Technology Stack

| Component | Production Engine | Details |
| --- | --- | --- |
| **Speech-to-Text (STT)** | Groq Whisper | `whisper-large-v3-turbo` with automatic language detection (`en`, `hi`) |
| **Embeddings** | SentenceTransformers | `intfloat/multilingual-e5-small` (384-dimensional dense vectors) |
| **Vector Index** | FAISS CPU | Normalized inner-product (cosine similarity) indexed per chunking strategy |
| **Reranking** | Optional Cross-Encoder | `cross-encoder/ms-marco-MiniLM-L-6-v2` / transparent pass-through |
| **Grounded LLM** | Groq OpenAI-Compatible | `openai/gpt-oss-20b` structured grounded output schema |
| **Text-to-Speech (TTS)** | Microsoft Edge Neural | `en-US-JennyNeural` (English), `hi-IN-SwaraNeural` (Hindi) with chunked fallback |
| **API Framework** | FastAPI + Uvicorn | Async REST endpoints with multipart/form-data upload support |

---

## API Reference

### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "ok",
  "service": "novaron-rag-core"
}
```

---

### 2. Text Query
```http
POST /v1/query
Content-Type: application/json
```
**Request Body:**
```json
{
  "query": "What is photosynthesis?",
  "top_k": 5,
  "chunking_strategy": "sentence",
  "retrieval_mode": "dense"
}
```
**Response:**
```json
{
  "answer": "Photosynthesis is the light-driven process in which plants use photosystems...",
  "refused": false,
  "retrieval_strategy": "dense",
  "chunking_strategy": "sentence",
  "sources": [
    {
      "chunk_id": "msmarco-xi:en:400625:7:sentence:0",
      "document_id": "msmarco-xi:en:400625:7",
      "passage_id": "400625",
      "title": null,
      "language": "en",
      "text": "Photosynthesis is the process...",
      "relevance_score": 0.8842
    }
  ],
  "latency_ms": {
    "retrieval": 16.49,
    "reranking": 0.0,
    "generation": 1022.64,
    "rag_total": 1039.13
  }
}
```

---

### 3. Voice Query (Voice-to-Voice / Voice-to-Text)
```http
POST /v1/voice/query
Content-Type: multipart/form-data
```
**Form Parameters:**
- `file`: Audio file (`.wav`, `.mp3`, `.m4a`, `.ogg`)
- `language`: `en` or `hi` (optional, auto-detected if omitted)
- `top_k`: Number of evidence passages (default: `5`)
- `chunking_strategy`: `sentence` | `fixed` | `hierarchical` (default: `sentence`)
- `retrieval_mode`: `dense` | `bm25` | `hybrid` | `hybrid_rerank` (default: `dense`)
- `synthesize_audio`: `true` | `false` (default: `false`)

**Response:**
```json
{
  "query": "What is photosynthesis?",
  "answer": "Photosynthesis is the light-driven process in which plants...",
  "refused": false,
  "retrieval_strategy": "dense",
  "chunking_strategy": "sentence",
  "sources": [...],
  "latency_ms": {
    "stt": 279.32,
    "retrieval": 16.49,
    "reranking": 0.0,
    "generation": 1022.64,
    "tts": 1616.06,
    "rag_total": 1039.13,
    "total": 2936.61
  },
  "audio_base64": "SUQzBAAAAAAA..."
}
```

---

### 4. Text-to-Speech Synthesis
```http
POST /v1/tts
Content-Type: application/json
```
**Request Body:**
```json
{
  "text": "What is photosynthesis?",
  "language": "en"
}
```
**Response:**
- Binary stream (`media_type="audio/mpeg"`) with valid MP3 headers.

---

## Guardrails & Grounding Safety

NOVARON implements strict multi-layer guardrails to maintain factual integrity and security:

1. **Evidence-Based Refusal**:
   - Queries with insufficient evidence relevance scores or empty retrieval results automatically trigger standardized refusal:
     `"I don't have enough information in the indexed knowledge base to answer that reliably."`
   - `refused=true` with `sources=[]`.
2. **Citation Verification**:
   - Grounded LLM responses must strictly cite valid retrieved `chunk_id` values. Fabricated or invalid citations result in immediate refusal.
   - Raw citation markers (`[chunk_id]`) are automatically stripped before speech synthesis to ensure natural audio.
3. **Prompt-Injection Defense**:
   - Retrieved text is treated strictly as passive data inside JSON structures, completely separated from system prompt directives.
4. **Refusal Speech Safety**:
   - When a refusal occurs, TTS synthesizes only the standard refusal message, preventing ungrounded speculation or hallucinated speech.

---

## Installation & Setup

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Clone and Install Dependencies
```bash
git clone https://github.com/Harshy-cmd/HH_Goa-T2.git
cd HH_Goa-T2/backend
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` in the project root:
```bash
cp ../.env.example ../.env
```

Configure your provider credentials in `.env`:
```env
# LLM Provider (Groq / OpenAI-compatible)
LLM_PROVIDER=openai
LLM_MODEL=openai/gpt-oss-20b
OPENAI_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.groq.com/openai/v1

# Speech-to-Text (STT)
STT_PROVIDER=openai
STT_MODEL=whisper-large-v3-turbo

# Text-to-Speech (TTS)
TTS_PROVIDER=edge
TTS_VOICE_EN=en-US-JennyNeural
TTS_VOICE_HI=hi-IN-SwaraNeural

# Retrieval & Vector Index
DENSE_RETRIEVER=faiss
VECTOR_INDEX_DIR=data/indexes
```

### 4. Build FAISS Indexes
Build the persistent FAISS indexes for each chunking strategy:
```bash
cd backend
python -m scripts.build_index --strategy fixed --index-dir ../data/indexes/fixed
python -m scripts.build_index --strategy sentence --index-dir ../data/indexes/sentence
python -m scripts.build_index --strategy hierarchical --index-dir ../data/indexes/hierarchical
```

### 5. Launch the Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.

---

## Test Suite & Verification

The repository includes a comprehensive 73-test regression suite covering vector retrieval, hybrid ranking, citation validation, refusal guardrails, STT transcription, TTS synthesis, and end-to-end voice-to-voice flows:

```bash
cd backend
python -m pytest tests -q
```

### Test Coverage Summary:
- `test_retrieval.py` & `test_production_retrieval.py`: Dense FAISS and multilingual retrieval benchmarks.
- `test_refusal_guardrails.py`: 5 canonical guardrail cases (grounded answering, weak evidence refusal, unrelated query refusal, unsupported claims, adversarial injection).
- `test_stt.py`: Speech-to-Text transcription, audio validation, and multipart upload handling.
- `test_tts.py`: Text-to-Speech language routing, error handling, refusal synthesis, and `/v1/tts` endpoint.
- `test_voice_to_voice.py`: Full end-to-end offline integration tests (`Audio` $\to$ `STT` $\to$ `RAG` $\to$ `TTS`).

---

## Repository Structure

```text
HH_Goa-T2/
├── .env.example               # Template environment configuration
├── README.md                  # System documentation
├── benchmarks/                # Evaluation cases and gold judgments
├── data/
│   ├── evaluation/            # MSMARCO-XI evaluation splits and subsets
│   ├── fixtures/              # Sample multilingual corpus
│   └── indexes/               # Persisted FAISS vector stores (sentence, fixed, hierarchical)
└── backend/
    ├── requirements.txt       # Production dependencies
    ├── app/
    │   ├── domain.py          # Core domain models and protocols (Retriever, Generator, STT, TTS)
    │   ├── embeddings.py      # Multilingual SentenceTransformer embedder
    │   ├── vector_store.py    # FAISS persistent index manager
    │   ├── retrieval.py       # Dense, BM25, and Hybrid retrievers
    │   ├── generation.py      # Grounded LLM generator and citation validator
    │   ├── pipeline.py        # Complete RAG pipeline and refusal logic
    │   ├── stt.py             # Whisper STT and MockSTT adapters
    │   ├── tts.py             # EdgeTTS and MockTTS adapters
    │   └── main.py            # FastAPI application routes (/health, /query, /voice/query, /tts)
    ├── scripts/               # Indexing and benchmarking utilities
    └── tests/                 # 73 automated unit and integration tests
```

---

## License
MIT License. Built for the Hackathon 2026 Multilingual Voice RAG Challenge.
