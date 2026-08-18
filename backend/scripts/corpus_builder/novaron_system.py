"""NOVARON System Domain Knowledge Generator.
Authoritative, highly detailed documentation of every internal component, subsystem, and algorithm in NOVARON.
"""
from __future__ import annotations

def get_novaron_documents() -> list[dict]:
    data = [
        ("novaron-sys-overview", "NOVARON System Overview and Mission", "architecture",
         "NOVARON is a production-grade, voice-enabled grounded Retrieval-Augmented Generation (RAG) assistant designed for verifiable, hallucination-free question answering. Built for the HH Goa Hackathon, NOVARON ensures that every factual claim is strictly supported by indexed source passages, returning exact chunk citations or refusing to guess when evidence is insufficient."),

        ("novaron-sys-mission", "NOVARON Mission and Design Principles", "architecture",
         "The core mission of NOVARON is to bridge conversational voice interaction with rigorous evidence grounding. The architecture adheres to five core design principles: Zero Hallucination (refusal over fabrication), Deterministic Routing (sub-millisecond non-knowledge shortcuts), Multilingual Parity (seamless English and Hindi support), Observable Latency Telemetry (granular per-stage profiling), and Premium Aesthetics (VoiceOrb and MagicRings)."),

        ("novaron-sys-voice-pipeline", "NOVARON End-to-End Voice Pipeline", "voice",
         "NOVARON features an asynchronous bilingual voice pipeline supporting English and Hindi. Spoken user queries are captured via browser Web Audio API in WAV format (16kHz, 16-bit mono) and sent via multipart POST to /v1/voice/query. Transcriptions from Whisper STT are routed through the RAG engine, and grounded answers are synthesized into speech using Microsoft EdgeTTS with base64 audio streaming."),

        ("novaron-sys-stt-adapter", "NOVARON Speech-to-Text (STT) Adapter", "voice",
         "NOVARON's speech recognition layer supports multiple STT engines with seamless fallback. The primary production engine utilizes Faster-Whisper and OpenAI Whisper models (such as whisper-base or whisper-large-v3) with automatic language detection across English and Hindi. A deterministic MockSTT adapter is provided for testing and offline CI environments."),

        ("novaron-sys-tts-adapter", "NOVARON Text-to-Speech (TTS) Adapter", "voice",
         "NOVARON's speech synthesis engine uses Microsoft EdgeTTS (edge-tts) for high-fidelity neural voice generation. It defaults to 'en-US-JennyNeural' for English queries and 'hi-IN-SwaraNeural' for Hindi queries. The backend streams binary audio/mpeg bytes or encoded base64 strings directly to the frontend HTML5 Audio Player."),

        ("novaron-sys-retrieval-hybrid", "NOVARON Hybrid Retrieval Architecture", "retrieval",
         "NOVARON implements a hybrid retrieval engine combining dense semantic vector search with sparse lexical search. Dense retrieval uses FAISS IndexFlatIP over multilingual E5 embeddings, while sparse retrieval uses BM25 Okapi with custom multilingual tokenization. This two-pronged approach captures both conceptual semantic intent and exact keyword matches."),

        ("novaron-sys-rrf", "Reciprocal Rank Fusion (RRF) in NOVARON", "retrieval",
         "NOVARON fuses ranked candidate lists from FAISS and BM25 using Reciprocal Rank Fusion (RRF). The fusion formula computes score(d) = sum(1 / (k + rank_i(d))) with smoothing constant k=60. RRF eliminates the need for delicate score calibration between dense cosine similarities and unbounded BM25 scores, producing a robust unified top-k candidate set."),

        ("novaron-sys-embeddings", "Multilingual E5 Embeddings in NOVARON", "embeddings",
         "NOVARON standardizes on intfloat/multilingual-e5-small (384 embedding dimensions) for dense semantic vector representations. Query embeddings prepend the 'query: ' prefix, while document passages prepend 'passage: '. Vectors are L2-normalized upon embedding generation, enabling exact inner-product search (IndexFlatIP) to compute exact cosine similarity."),

        ("novaron-sys-vector-store", "FAISS Vector Store Persistence and Manifest", "vector_store",
         "NOVARON's vector storage layer wraps FAISS IndexFlatIP with persistent file-backed serialization. Each index directory contains 'index.faiss', 'chunks.json' (preserving rich chunk metadata), and 'manifest.json' (storing embedding model, dimension, normalization flag, creation timestamp, and chunk count for strict build validation)."),

        ("novaron-sys-bm25-retriever", "BM25 Okapi Lexical Retriever in NOVARON", "retrieval",
         "NOVARON's lexical retrieval engine uses BM25 Okapi with parameters k1=1.5 (term frequency saturation) and b=0.75 (document length normalization). The internal tokenizer handles alphanumeric English tokens as well as Devanagari Unicode scripts, ensuring robust lexical search across mixed English and Hindi queries."),

        ("novaron-sys-reranking", "Two-Stage Retrieval and Reranking in NOVARON", "reranking",
         "To maximize precision, NOVARON employs a two-stage retrieval pipeline. First-stage hybrid retrieval retrieves candidate passages (default top 10), which are then passed to a reranker. NOVARON supports CrossEncoder models (such as cross-encoder/mmarco-mMiniLMv2-L12-H384-v1) and a deterministic Transparent Term-Overlap fallback reranker for ultra-low latency environments."),

        ("novaron-sys-grounding-guardrail", "Zero-Hallucination Grounding Guardrail", "grounding",
         "NOVARON enforces a strict Zero-Hallucination policy. If retrieved candidates do not satisfy the minimum relevance score threshold (default 0.12 for reranked, 0.01 for unranked) or if evidence is insufficient, NOVARON issues a deterministic refusal: 'I don\\'t have enough information in the indexed knowledge base to answer that reliably.' NOVARON never guesses or fabricates facts."),

        ("novaron-sys-citation-validation", "Citation Validation and Provenance", "citations",
         "Every response generated by NOVARON includes explicit chunk citations resolving directly to indexed knowledge passages. During generation, the backend verifies that cited chunk IDs exist within the retrieved evidence set. Any unverified citation is stripped, and answers citing non-existent chunks are rejected to guarantee complete provenance."),

        ("novaron-sys-query-router", "Deterministic Regex Query Router", "router",
         "NOVARON incorporates a high-performance deterministic regex router that classifies queries in under 1 millisecond. Queries are categorized into: CONVERSATIONAL (greetings and courtesy), SYSTEM (bot identity and capabilities), KNOWLEDGE (factual queries requiring RAG retrieval), and UNSUPPORTED. Conversational and system queries receive immediate direct answers without incurring FAISS or LLM latency."),

        ("novaron-sys-chunking-strategies", "Ingestion and Chunking Strategies", "ingestion",
         "NOVARON supports three distinct chunking strategies in ingestion: Fixed-word chunking (fixed 384-word windows with 64-word overlap), Sentence chunking (boundary-preserving sentence segmentation up to target word limit), and Hierarchical chunking (parent-child chunking linking specific sentence chunks to full passage parents for hierarchical context expansion)."),

        ("novaron-sys-frontend-voiceorb", "VoiceOrb and Audio Visualization", "frontend",
         "NOVARON's user interface features the VoiceOrb, an interactive SVG/CSS visualizer reflecting real-time assistant state: Idle (ambient pulse), Listening (reactive sound rings), Processing (glowing orbital rotation), Speaking (pulsing audio waveform), and Error (rose accent pulse)."),

        ("novaron-sys-frontend-magicrings", "MagicRings Microphone Visualizer", "frontend",
         "The MagicRings component surrounds the primary voice input trigger on the frontend. When the user speaks, MagicRings dynamically scales concentric glowing rings based on microphone input volume, providing visual feedback during voice capture in both mobile and desktop viewports."),

        ("novaron-sys-latency-telemetry", "Granular Latency Telemetry HUD", "telemetry",
         "Every query response in NOVARON returns a granular latency breakdown in milliseconds, capturing STT transcription, query embedding, FAISS search, BM25 lookup, RRF fusion, reranking, LLM generation, and TTS synthesis. The frontend displays this in an expandable HUD with color-coded millisecond badges."),

        ("novaron-sys-history-storage", "Query History and Local Storage Cache", "frontend",
         "NOVARON maintains an in-memory and LocalStorage-backed query history list on the frontend. Users can view past queries, inspect previous answers, re-open source citation drawers, replay audio responses, and clear history with a single click."),

        ("novaron-sys-error-handling", "Resilient Error Handling and Fallbacks", "architecture",
         "NOVARON implements graceful error degradation across every layer. If the external LLM provider experiences network timeout or 429 rate limit errors, the system retries with backoff and falls back to alternate models. If FAISS indexes are unbuilt, it gracefully falls back to hashing retrievers, ensuring the application never crashes.")
    ]
    docs = []
    for doc_id, title, topic, text in data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "novaron_system",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })
    return docs
