from __future__ import annotations

import asyncio
import base64
import os
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv

    _root_env = PROJECT_ROOT / ".env"
    _backend_env = Path(__file__).resolve().parents[1] / ".env"
    if _root_env.exists():
        load_dotenv(_root_env)
    elif _backend_env.exists():
        load_dotenv(_backend_env)
except ImportError:
    pass

from app.domain import SpeechToText, TextToSpeech
from app.embeddings import SentenceTransformerEmbeddingProvider
from app.generation import GeminiGroundedLLM, OpenAIGroundedLLM
from app.ingestion import fixed_chunks, hierarchical_chunks, load_jsonl, sentence_chunks
from app.pipeline import ExtractiveGroundedGenerator, RAGPipeline
from app.query_normalizer import (extract_topic_from_query,
                                  generate_suggested_questions,
                                  normalize_spoken_query)
from app.retrieval import (BM25Retriever, CrossEncoderReranker, FAISSDenseRetriever,
                           HashingDenseRetriever, HashingEmbedder, HybridRetriever,
                           TransparentReranker)
from app.router import QueryIntent, classify_query
from app.stt import FasterWhisperSTT, MockSTT, OpenAIWhisperSTT, SpeechToTextError
from app.tts import EdgeTTS, MockTTS, TextToSpeechError
from app.vector_store import FaissVectorStore

DATA_PATH = Path(os.getenv("NOVARON_CORPUS_PATH", str(PROJECT_ROOT / "data" / "fixtures" / "sample_corpus.jsonl")))


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=20)
    chunking_strategy: Literal["fixed", "sentence", "hierarchical"] = "sentence"
    retrieval_mode: Literal["dense", "bm25", "hybrid", "hybrid_rerank"] = "hybrid_rerank"
    language: str | None = None
    previous_query: str | None = None


class SourceResponse(BaseModel):
    chunk_id: str
    document_id: str
    passage_id: str
    title: str | None
    language: str | None
    text: str
    relevance_score: float


class QueryResponse(BaseModel):
    answer: str
    refused: bool
    retrieval_strategy: str
    chunking_strategy: str
    sources: list[SourceResponse]
    latency_ms: dict[str, float]
    query_type: str | None = None
    normalized_query: str | None = None
    suggested_questions: list[str] = Field(default_factory=list)


class VoiceQueryResponse(BaseModel):
    query: str
    answer: str
    refused: bool
    retrieval_strategy: str
    chunking_strategy: str
    sources: list[SourceResponse]
    latency_ms: dict[str, float]
    audio_base64: str | None = None
    query_type: str | None = None
    normalized_query: str | None = None
    suggested_questions: list[str] = Field(default_factory=list)


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)
    language: str | None = Field(default="en")


_STORE_CACHE: dict[str, FaissVectorStore] = {}
_EMBEDDER_INSTANCE: SentenceTransformerEmbeddingProvider | None = None


def _get_shared_embedder() -> SentenceTransformerEmbeddingProvider:
    global _EMBEDDER_INSTANCE
    if _EMBEDDER_INSTANCE is None:
        _EMBEDDER_INSTANCE = SentenceTransformerEmbeddingProvider()
    return _EMBEDDER_INSTANCE


def _get_vector_store(strategy: str) -> FaissVectorStore | None:
    if strategy in _STORE_CACHE:
        return _STORE_CACHE[strategy]
    configured_path = Path(os.getenv("VECTOR_INDEX_DIR", "data/indexes"))
    index_root = configured_path if configured_path.is_absolute() else PROJECT_ROOT / configured_path
    index_dir = index_root / strategy
    if FaissVectorStore.exists(index_dir):
        embedder = _get_shared_embedder()
        store = FaissVectorStore.load(
            index_dir,
            expected_model=embedder.model_name,
            expected_strategy=strategy,
            expected_normalized=True,
        )
        _STORE_CACHE[strategy] = store
        return store
    return None


def _build_dense_retriever(chunks: list, strategy: str):
    provider = os.getenv("DENSE_RETRIEVER", "faiss").lower()
    if provider == "faiss":
        store = _get_vector_store(strategy)
        if store is not None:
            return FAISSDenseRetriever(store, _get_shared_embedder())
        return HashingDenseRetriever(chunks, HashingEmbedder())
    if provider == "hashing":
        return HashingDenseRetriever(chunks, HashingEmbedder())
    raise ValueError("DENSE_RETRIEVER must be either 'hashing' or 'faiss'.")


def _build_reranker():
    provider = os.getenv("RERANKER_PROVIDER", "transparent").lower()
    if provider == "transparent":
        return TransparentReranker()
    if provider == "cross_encoder":
        return CrossEncoderReranker()
    raise ValueError("RERANKER_PROVIDER must be either 'transparent' or 'cross_encoder'.")


_GENERATOR_INSTANCE = None


def _build_generator():
    global _GENERATOR_INSTANCE
    if _GENERATOR_INSTANCE is not None:
        return _GENERATOR_INSTANCE
    provider = os.getenv("LLM_PROVIDER", "extractive").lower()
    if provider == "extractive":
        _GENERATOR_INSTANCE = ExtractiveGroundedGenerator()
        return _GENERATOR_INSTANCE
    if provider == "openai":
        _GENERATOR_INSTANCE = OpenAIGroundedLLM()
        return _GENERATOR_INSTANCE
    if provider == "gemini":
        _GENERATOR_INSTANCE = GeminiGroundedLLM()
        return _GENERATOR_INSTANCE
    raise ValueError("LLM_PROVIDER must be one of 'extractive', 'openai', or 'gemini'.")


def _build_stt() -> SpeechToText:
    provider = os.getenv("STT_PROVIDER", "local").lower()
    if provider in ("local", "faster-whisper", "faster_whisper", "whisper"):
        return FasterWhisperSTT()
    if provider in ("openai", "groq"):
        return OpenAIWhisperSTT()
    if provider == "mock":
        return MockSTT()
    raise ValueError(f"STT_PROVIDER must be 'local', 'openai', 'groq', or 'mock', got '{provider}'.")


def _build_tts() -> TextToSpeech:
    provider = os.getenv("TTS_PROVIDER", "edge").lower()
    if provider == "edge":
        return EdgeTTS()
    if provider == "mock":
        return MockTTS()
    raise ValueError(f"TTS_PROVIDER must be either 'edge' or 'mock', got '{provider}'.")


def build_pipeline(chunks: list, strategy: str = "sentence", mode: str = "dense", dense=None, bm25=None) -> RAGPipeline:
    dense_retriever = dense if dense is not None else _build_dense_retriever(chunks, strategy)
    bm25_retriever = bm25 if bm25 is not None else BM25Retriever(chunks)
    retriever = {
        "dense": dense_retriever,
        "bm25": bm25_retriever,
        "hybrid": HybridRetriever(dense_retriever, bm25_retriever),
        "hybrid_rerank": HybridRetriever(dense_retriever, bm25_retriever),
    }[mode]
    reranker = _build_reranker() if mode == "hybrid_rerank" else None
    threshold = float(os.getenv("MIN_RELEVANCE_SCORE", "0.12")) if reranker else float(
        os.getenv("MIN_UNRERANKED_RELEVANCE_SCORE", "0.70")
    )
    return RAGPipeline(retriever, reranker, _build_generator(), threshold)


def build_pipelines() -> dict[str, dict[str, RAGPipeline]]:
    passages = load_jsonl(DATA_PATH)
    corpora = {
        "fixed": fixed_chunks(passages),
        "sentence": sentence_chunks(passages),
        "hierarchical": hierarchical_chunks(passages),
    }
    result: dict[str, dict[str, RAGPipeline]] = {}
    for name, chunks in corpora.items():
        dense = _build_dense_retriever(chunks, name)
        bm25 = BM25Retriever(chunks)
        result[name] = {
            mode: build_pipeline(chunks, name, mode, dense=dense, bm25=bm25)
            for mode in ("dense", "bm25", "hybrid", "hybrid_rerank")
        }
    return result


from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Global state — initialised lazily inside lifespan so the server binds its
# port immediately and Render's port-scan timeout is never hit.
# ---------------------------------------------------------------------------
pipelines: dict | None = None
stt_adapter: SpeechToText | None = None
tts_adapter: TextToSpeech | None = None
_startup_complete: bool = False


def _initialize_all() -> None:
    """Build every heavy resource (model download, FAISS index, BM25, STT, TTS).
    Called once from lifespan *after* the ASGI server has already bound its port."""
    global pipelines, stt_adapter, tts_adapter, _startup_complete

    print("[STARTUP] Loading corpus and building pipelines…")
    t0 = time.perf_counter()
    pipelines = build_pipelines()
    print(f"[STARTUP] Pipelines ready in {round((time.perf_counter() - t0)*1000, 1)} ms")

    print("[STARTUP] Initialising STT adapter…")
    stt_adapter = _build_stt()

    print("[STARTUP] Initialising TTS adapter…")
    tts_adapter = _build_tts()

    # Optional warmup pass (embed a dummy query to prime the model cache)
    try:
        embedder = _get_shared_embedder()
        embedder.warmup()
    except Exception:
        pass

    _startup_complete = True
    print(f"[STARTUP] ✅ System ready — total {round((time.perf_counter() - t0)*1000, 1)} ms")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uvicorn binds its port only AFTER this function yields.
    We must yield immediately so Render's port scan succeeds, then run
    heavy initialisation (model download, FAISS, BM25) in the background.
    Routes guard themselves with _require_ready() until the task finishes."""
    # Fire-and-forget: start init in a thread pool, do NOT await before yield.
    asyncio.get_event_loop().run_in_executor(None, _initialize_all)
    yield  # ← port binds here; Render port scan passes immediately


app = FastAPI(title="NOVARON Voice RAG", version="0.5.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    """Health-check endpoint — responds immediately even while startup is loading."""
    return {
        "status": "ok" if _startup_complete else "starting",
        "service": "novaron-rag-core",
        "ready": _startup_complete,
    }


def _require_ready():
    """Raise HTTP 503 if startup hasn't finished yet."""
    if not _startup_complete:
        raise HTTPException(
            status_code=503,
            detail="Service is starting up — please retry in a few seconds.",
        )


@app.post("/v1/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    _require_ready()
    t_start = time.perf_counter()

    # 1. Deterministic Local Query Normalization & Anaphora Context
    prev_topic = extract_topic_from_query(request.previous_query) if request.previous_query else None
    normalized = normalize_spoken_query(request.query, previous_topic=prev_topic)
    norm_elapsed = round((time.perf_counter() - t_start) * 1000, 3)

    # 2. Route Query
    route = classify_query(normalized.normalized_query, preferred_language=request.language)

    # 3. Handle Conversational / System directly
    if route.intent in (QueryIntent.CONVERSATIONAL, QueryIntent.SYSTEM) and route.direct_answer:
        route_ms = round((time.perf_counter() - t_start) * 1000, 3)
        return QueryResponse(
            answer=route.direct_answer,
            refused=False,
            retrieval_strategy=f"direct_{route.intent.value}",
            chunking_strategy=request.chunking_strategy,
            query_type=route.intent.value,
            normalized_query=normalized.normalized_query,
            sources=[],
            latency_ms={"norm": norm_elapsed, "route": route_ms, "total": route_ms},
            suggested_questions=generate_suggested_questions(normalized.normalized_query, [], language=route.language),
        )

    # 4. Handle Knowledge Queries through Grounded RAG Pipeline
    result = pipelines[request.chunking_strategy][request.retrieval_mode].run(normalized.normalized_query, answer_limit=request.top_k)
    labels = {
        "dense": "dense",
        "bm25": "bm25",
        "hybrid": "hybrid_rrf",
        "hybrid_rerank": "hybrid_rrf + reranker",
    }
    source_titles = [hit.chunk.title for hit in result.sources if hit.chunk.title]
    suggestions = generate_suggested_questions(normalized.normalized_query, source_titles, language=route.language)

    latencies = {"norm": norm_elapsed, **result.latency_ms}
    latencies["total"] = round(norm_elapsed + result.latency_ms.get("rag_total", 0.0), 3)

    return QueryResponse(
        answer=result.answer,
        refused=result.refused,
        retrieval_strategy=labels[request.retrieval_mode],
        chunking_strategy=request.chunking_strategy,
        query_type="knowledge" if not result.refused else "refusal",
        normalized_query=normalized.normalized_query,
        latency_ms=latencies,
        suggested_questions=suggestions,
        sources=[
            SourceResponse(
                chunk_id=hit.chunk.chunk_id,
                document_id=hit.chunk.document_id,
                passage_id=hit.chunk.passage_id,
                title=hit.chunk.title,
                language=hit.chunk.language,
                text=hit.chunk.text,
                relevance_score=round(hit.score, 4),
            )
            for hit in result.sources
        ],
    )


@app.post("/v1/voice/query", response_model=VoiceQueryResponse)
async def voice_query(
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
    top_k: int = Form(default=5),
    chunking_strategy: Literal["fixed", "sentence", "hierarchical"] = Form(default="sentence"),
    retrieval_mode: Literal["dense", "bm25", "hybrid", "hybrid_rerank"] = Form(default="dense"),
    synthesize_audio: bool = Form(default=False),
    previous_query: str | None = Form(default=None),
) -> VoiceQueryResponse:
    _require_ready()
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Audio file is required.")

    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

    if len(audio_bytes) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file exceeds maximum size of 25MB.")

    stt_start = time.perf_counter()
    try:
        transcript = await stt_adapter.transcribe(
            audio=audio_bytes,
            language=language,
            filename=file.filename or "audio.wav",
        )
    except SpeechToTextError as exc:
        raise HTTPException(status_code=502, detail=f"Speech-to-text transcription error: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal error during voice transcription.") from exc

    stt_elapsed = round((time.perf_counter() - stt_start) * 1000, 3)

    if chunking_strategy not in pipelines or retrieval_mode not in pipelines[chunking_strategy]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid chunking strategy '{chunking_strategy}' or retrieval mode '{retrieval_mode}'.",
        )

    # 1. Deterministic Local Query Normalization & Anaphora Context
    t_norm_start = time.perf_counter()
    prev_topic = extract_topic_from_query(previous_query) if previous_query else None
    normalized = normalize_spoken_query(transcript, previous_topic=prev_topic)
    norm_elapsed = round((time.perf_counter() - t_norm_start) * 1000, 3)

    # 2. Route Query
    route = classify_query(normalized.normalized_query, preferred_language=language)
    labels = {
        "dense": "dense",
        "bm25": "bm25",
        "hybrid": "hybrid_rrf",
        "hybrid_rerank": "hybrid_rrf + reranker",
    }

    if route.intent in (QueryIntent.CONVERSATIONAL, QueryIntent.SYSTEM) and route.direct_answer:
        answer = route.direct_answer
        refused = False
        strategy = f"direct_{route.intent.value}"
        sources: list[SourceResponse] = []
        latency_ms = {
            "stt": stt_elapsed,
            "norm": norm_elapsed,
            "route": 0.5,
            "total": round(stt_elapsed + norm_elapsed + 0.5, 3),
        }
        query_type = route.intent.value
        suggestions = generate_suggested_questions(normalized.normalized_query, [], language=route.language)
    else:
        loop = asyncio.get_running_loop()
        pipeline_instance = pipelines[chunking_strategy][retrieval_mode]
        result = await loop.run_in_executor(
            None,
            lambda: pipeline_instance.run(normalized.normalized_query, answer_limit=top_k),
        )
        answer = result.answer
        refused = result.refused
        strategy = labels[retrieval_mode]
        sources = [
            SourceResponse(
                chunk_id=hit.chunk.chunk_id,
                document_id=hit.chunk.document_id,
                passage_id=hit.chunk.passage_id,
                title=hit.chunk.title,
                language=hit.chunk.language,
                text=hit.chunk.text,
                relevance_score=round(hit.score, 4),
            )
            for hit in result.sources
        ]
        source_titles = [hit.chunk.title for hit in result.sources if hit.chunk.title]
        suggestions = generate_suggested_questions(normalized.normalized_query, source_titles, language=route.language)
        latency_ms = {
            "stt": stt_elapsed,
            "norm": norm_elapsed,
            **result.latency_ms,
            "total": round(stt_elapsed + norm_elapsed + result.latency_ms.get("rag_total", 0.0), 3),
        }
        query_type = "knowledge" if not refused else "refusal"

    audio_b64 = None
    if synthesize_audio and answer:
        tts_start = time.perf_counter()
        try:
            tts_audio = await tts_adapter.synthesize(answer, language=language or route.language)
            tts_elapsed = round((time.perf_counter() - tts_start) * 1000, 3)
            latency_ms["tts"] = tts_elapsed
            latency_ms["total"] = round(latency_ms["total"] + tts_elapsed, 3)
            audio_b64 = base64.b64encode(tts_audio).decode("ascii")
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Speech synthesis error: {exc}") from exc

    return VoiceQueryResponse(
        query=transcript,
        normalized_query=normalized.normalized_query,
        answer=answer,
        refused=refused,
        retrieval_strategy=strategy,
        chunking_strategy=chunking_strategy,
        query_type=query_type,
        latency_ms=latency_ms,
        audio_base64=audio_b64,
        suggested_questions=suggestions,
        sources=sources,
    )


@app.post("/v1/tts")
async def synthesize_speech(request: TTSRequest) -> Response:
    _require_ready()
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text to synthesize cannot be empty.")
    try:
        audio_bytes = await tts_adapter.synthesize(request.text, language=request.language)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except TextToSpeechError as exc:
        msg = str(exc)
        status = 400 if "Unsupported language" in msg or "Cannot synthesize empty" in msg else 502
        raise HTTPException(status_code=status, detail=msg) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal error during speech synthesis.") from exc
