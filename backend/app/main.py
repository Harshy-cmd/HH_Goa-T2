from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
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

from app.domain import SpeechToText
from app.embeddings import SentenceTransformerEmbeddingProvider
from app.generation import OpenAIGroundedLLM
from app.ingestion import fixed_chunks, hierarchical_chunks, load_jsonl, sentence_chunks
from app.pipeline import ExtractiveGroundedGenerator, RAGPipeline
from app.retrieval import (BM25Retriever, CrossEncoderReranker, FAISSDenseRetriever,
                           HashingDenseRetriever, HashingEmbedder, HybridRetriever,
                           TransparentReranker)
from app.stt import MockSTT, OpenAIWhisperSTT, SpeechToTextError
from app.vector_store import FaissVectorStore

DATA_PATH = Path(os.getenv("NOVARON_CORPUS_PATH", str(PROJECT_ROOT / "data" / "fixtures" / "sample_corpus.jsonl")))


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=20)
    chunking_strategy: Literal["fixed", "sentence", "hierarchical"] = "fixed"
    retrieval_mode: Literal["dense", "bm25", "hybrid", "hybrid_rerank"] = "hybrid_rerank"


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


class VoiceQueryResponse(BaseModel):
    query: str
    answer: str
    refused: bool
    retrieval_strategy: str
    chunking_strategy: str
    sources: list[SourceResponse]
    latency_ms: dict[str, float]


def _build_dense_retriever(chunks: list, strategy: str):
    provider = os.getenv("DENSE_RETRIEVER", "faiss").lower()
    if provider == "faiss":
        configured_path = Path(os.getenv("VECTOR_INDEX_DIR", "data/indexes"))
        index_root = configured_path if configured_path.is_absolute() else PROJECT_ROOT / configured_path
        index_dir = index_root / strategy
        if FaissVectorStore.exists(index_dir):
            embedder = SentenceTransformerEmbeddingProvider()
            store = FaissVectorStore.load(
                index_dir,
                expected_model=embedder.model_name,
                expected_strategy=strategy,
                expected_normalized=True,
            )
            return FAISSDenseRetriever(store, embedder)
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


def _build_generator():
    provider = os.getenv("LLM_PROVIDER", "extractive").lower()
    if provider == "extractive":
        return ExtractiveGroundedGenerator()
    if provider == "openai":
        return OpenAIGroundedLLM()
    raise ValueError("LLM_PROVIDER must be either 'extractive' or 'openai'.")


def _build_stt() -> SpeechToText:
    provider = os.getenv("STT_PROVIDER", "openai").lower()
    if provider in ("openai", "groq"):
        return OpenAIWhisperSTT()
    if provider == "mock":
        return MockSTT()
    raise ValueError(f"STT_PROVIDER must be either 'openai', 'groq', or 'mock', got '{provider}'.")


def build_pipeline(chunks: list, strategy: str = "sentence", mode: str = "dense") -> RAGPipeline:
    dense = _build_dense_retriever(chunks, strategy)
    bm25 = BM25Retriever(chunks)
    retriever = {
        "dense": dense,
        "bm25": bm25,
        "hybrid": HybridRetriever(dense, bm25),
        "hybrid_rerank": HybridRetriever(dense, bm25),
    }[mode]
    reranker = _build_reranker() if mode == "hybrid_rerank" else None
    threshold = float(os.getenv("MIN_RELEVANCE_SCORE", "0.12")) if reranker else float(
        os.getenv("MIN_UNRERANKED_RELEVANCE_SCORE", "0.01")
    )
    return RAGPipeline(retriever, reranker, _build_generator(), threshold)


def build_pipelines() -> dict[str, dict[str, RAGPipeline]]:
    passages = load_jsonl(DATA_PATH)
    corpora = {
        "fixed": fixed_chunks(passages),
        "sentence": sentence_chunks(passages),
        "hierarchical": hierarchical_chunks(passages),
    }
    return {
        name: {mode: build_pipeline(chunks, name, mode) for mode in ("dense", "bm25", "hybrid", "hybrid_rerank")}
        for name, chunks in corpora.items()
    }


pipelines = build_pipelines()
stt_adapter = _build_stt()
app = FastAPI(title="NOVARON Voice RAG", version="0.4.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "novaron-rag-core"}


@app.post("/v1/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    result = pipelines[request.chunking_strategy][request.retrieval_mode].run(request.query, answer_limit=request.top_k)
    labels = {
        "dense": "dense",
        "bm25": "bm25",
        "hybrid": "hybrid_rrf",
        "hybrid_rerank": "hybrid_rrf + reranker",
    }
    return QueryResponse(
        answer=result.answer,
        refused=result.refused,
        retrieval_strategy=labels[request.retrieval_mode],
        chunking_strategy=request.chunking_strategy,
        latency_ms=result.latency_ms,
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
) -> VoiceQueryResponse:
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

    result = pipelines[chunking_strategy][retrieval_mode].run(transcript, answer_limit=top_k)
    labels = {
        "dense": "dense",
        "bm25": "bm25",
        "hybrid": "hybrid_rrf",
        "hybrid_rerank": "hybrid_rrf + reranker",
    }

    latency_ms = {
        "stt": stt_elapsed,
        "retrieval": result.latency_ms.get("retrieval", 0.0),
        "reranking": result.latency_ms.get("reranking", 0.0),
        "generation": result.latency_ms.get("generation", 0.0),
        "rag_total": result.latency_ms.get("rag_total", 0.0),
        "total": round(stt_elapsed + result.latency_ms.get("rag_total", 0.0), 3),
    }

    return VoiceQueryResponse(
        query=transcript,
        answer=result.answer,
        refused=result.refused,
        retrieval_strategy=labels[retrieval_mode],
        chunking_strategy=chunking_strategy,
        latency_ms=latency_ms,
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
