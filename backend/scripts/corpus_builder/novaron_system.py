"""NOVARON System Domain Knowledge Generator.
Contains authoritative, self-contained documentation of NOVARON architecture, components, and workflows.
"""
from __future__ import annotations

def get_novaron_documents() -> list[dict]:
    return [
        {
            "document_id": "novaron-sys-overview",
            "passage_id": "novaron-sys-overview-1",
            "title": "NOVARON System Overview and Mission",
            "domain": "novaron_system",
            "topic": "architecture",
            "language": "en",
            "source_type": "curated",
            "keywords": ["novaron", "overview", "mission", "rag", "voice assistant"],
            "text": "NOVARON is a production-grade, voice-enabled grounded Retrieval-Augmented Generation (RAG) assistant designed for verifiable, hallucination-free question answering. NOVARON ensures that every factual claim is strictly supported by indexed source passages, returning exact chunk citations or refusing to guess when evidence is insufficient."
        },
        {
            "document_id": "novaron-sys-voice-pipeline",
            "passage_id": "novaron-sys-voice-pipeline-1",
            "title": "NOVARON Voice Pipeline Architecture",
            "domain": "novaron_system",
            "topic": "voice",
            "language": "en",
            "source_type": "curated",
            "keywords": ["voice", "stt", "tts", "whisper", "edge-tts", "audio"],
            "text": "NOVARON features an end-to-end bilingual voice pipeline supporting English and Hindi. Spoken user queries are captured in the browser and transcribed using Whisper STT or Faster-Whisper. Transcribed queries are routed through the RAG engine, and grounded answers are synthesized into natural speech using neural Text-to-Speech (EdgeTTS) with synchronized audio waveforms."
        },
        {
            "document_id": "novaron-sys-retrieval-hybrid",
            "passage_id": "novaron-sys-retrieval-hybrid-1",
            "title": "NOVARON Hybrid Retrieval and Reciprocal Rank Fusion",
            "domain": "novaron_system",
            "topic": "retrieval",
            "language": "en",
            "source_type": "curated",
            "keywords": ["hybrid retrieval", "rrf", "dense", "bm25", "faiss", "rank fusion"],
            "text": "NOVARON implements a hybrid retrieval engine combining dense semantic vector search via FAISS with lexical keyword search via BM25 Okapi. Results from both retrievers are merged using Reciprocal Rank Fusion (RRF with constant k=60), balancing exact keyword matching with semantic concept generalization across multilingual texts."
        },
        {
            "document_id": "novaron-sys-embeddings",
            "passage_id": "novaron-sys-embeddings-1",
            "title": "NOVARON Multilingual E5 Embedding Architecture",
            "domain": "novaron_system",
            "topic": "embeddings",
            "language": "en",
            "source_type": "curated",
            "keywords": ["embeddings", "multilingual-e5", "dense vectors", "sentence-transformers"],
            "text": "NOVARON utilizes intfloat/multilingual-e5-small (384 embedding dimensions) for dense semantic vector representations. Query embeddings use the 'query: ' prefix and document chunks use the 'passage: ' prefix with L2 normalization (IndexFlatIP), ensuring high cosine similarity accuracy across English, Hindi, and Kannada passages."
        },
        {
            "document_id": "novaron-sys-reranking",
            "passage_id": "novaron-sys-reranking-1",
            "title": "NOVARON Cross-Encoder and Transparent Reranking",
            "domain": "novaron_system",
            "topic": "reranking",
            "language": "en",
            "source_type": "curated",
            "keywords": ["reranker", "cross-encoder", "transparent reranker", "score refinement"],
            "text": "NOVARON employs a two-stage retrieval pipeline where top candidate passages from hybrid RRF are scored by a reranker. The system supports cross-encoder models (such as cross-encoder/mmarco-mMiniLMv2-L12-H384-v1) with a deterministic Transparent Term-Overlap fallback, refining candidate relevance prior to LLM context generation."
        },
        {
            "document_id": "novaron-sys-grounding-guardrail",
            "passage_id": "novaron-sys-grounding-guardrail-1",
            "title": "NOVARON Grounding Check and Refusal Guardrail",
            "domain": "novaron_system",
            "topic": "grounding",
            "language": "en",
            "source_type": "curated",
            "keywords": ["grounding", "guardrail", "refusal", "hallucination prevention", "zero hallucination"],
            "text": "NOVARON enforces a strict Zero-Hallucination policy. If retrieved candidates do not satisfy minimum relevance thresholds (minimum score check) or if candidate evidence lacks factual support for the query, NOVARON issues a deterministic refusal: 'I don\\'t have enough information in the indexed knowledge base to answer that reliably.' NOVARON never invents unverified claims or citations."
        },
        {
            "document_id": "novaron-sys-citation-validation",
            "passage_id": "novaron-sys-citation-validation-1",
            "title": "NOVARON Citation Validation and Verification",
            "domain": "novaron_system",
            "topic": "citations",
            "language": "en",
            "source_type": "curated",
            "keywords": ["citations", "verification", "provenance", "chunk citation"],
            "text": "Every response produced by NOVARON includes explicit chunk citations that resolve directly to indexed knowledge passages. During generation, the backend verifies that cited chunk IDs exist within the retrieved evidence set. Any hallucinated citation is stripped or triggers a safety refusal, guaranteeing complete provenance for all answers."
        },
        {
            "document_id": "novaron-sys-query-router",
            "passage_id": "novaron-sys-query-router-1",
            "title": "NOVARON Deterministic Query Router",
            "domain": "novaron_system",
            "topic": "router",
            "language": "en",
            "source_type": "curated",
            "keywords": ["query router", "deterministic routing", "intents", "conversational", "system"],
            "text": "NOVARON incorporates a high-performance deterministic regex router that classifies queries in under 1 millisecond into four intents: CONVERSATIONAL (greetings and courtesy), SYSTEM (bot identity and capabilities), KNOWLEDGE (factual queries requiring RAG retrieval), and UNSUPPORTED. Conversational and system queries receive immediate direct answers without incurring FAISS or LLM latency overhead."
        },
        {
            "document_id": "novaron-sys-frontend-ui",
            "passage_id": "novaron-sys-frontend-ui-1",
            "title": "NOVARON Frontend UI and Visual Components",
            "domain": "novaron_system",
            "topic": "frontend",
            "language": "en",
            "source_type": "curated",
            "keywords": ["frontend", "react", "voiceorb", "magicrings", "answer card", "tailwind"],
            "text": "NOVARON's web interface is built with React, TypeScript, Vite, and TailwindCSS. It features interactive components including the animated VoiceOrb, MagicRings microphone visualizer, Grounded Answer cards with source drawers, latency breakdowns HUD, query history cache, and dark-forest Goa aesthetics."
        },
        {
            "document_id": "novaron-sys-telemetry",
            "passage_id": "novaron-sys-telemetry-1",
            "title": "NOVARON Latency Telemetry and Profiling",
            "domain": "novaron_system",
            "topic": "telemetry",
            "language": "en",
            "source_type": "curated",
            "keywords": ["telemetry", "latency", "profiling", "timing", "breakdown"],
            "text": "Every query response in NOVARON returns a granular latency breakdown in milliseconds, capturing STT transcription, query embedding, FAISS search, BM25 lookup, RRF fusion, reranking, LLM generation, and TTS synthesis. This ensures transparent observability into performance bottlenecks across the stack."
        }
    ]
