from __future__ import annotations

import hashlib
import math
import re
import threading
import time
from collections import Counter, defaultdict
from typing import Any, Iterable, Sequence

from app.domain import Chunk, Embedder, Reranker, Retriever, SearchHit
from app.vector_store import FaissVectorStore


def tokenize(text: str) -> list[str]:
    return re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE)


class HashingEmbedder(Embedder):
    """Dependency-free baseline; replace with a true multilingual embedding provider in production."""
    def __init__(self, dimensions: int = 512) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            slot = int.from_bytes(hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest(), "big") % self.dimensions
            vector[slot] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector] if norm else vector


class HashingDenseRetriever:
    def __init__(self, chunks: Iterable[Chunk], embedder: Embedder) -> None:
        self.chunks = list(chunks)
        self.embedder = embedder
        self.vectors = [embedder.embed(chunk.text) for chunk in self.chunks]

    def search(self, query: str, limit: int) -> list[SearchHit]:
        hits, _ = self.search_with_profile(query, limit)
        return hits

    def search_with_profile(self, query: str, limit: int) -> tuple[list[SearchHit], dict[str, float]]:
        started = time.perf_counter()
        query_vector = self.embedder.embed(query)
        embedded_at = time.perf_counter()
        scored = [(sum(a * b for a, b in zip(query_vector, vector)), chunk) for chunk, vector in zip(self.chunks, self.vectors)]
        hits = [SearchHit(chunk=chunk, score=score, retriever="dense") for score, chunk in sorted(scored, reverse=True, key=lambda pair: pair[0])[:limit]]
        return hits, {"embedding": (embedded_at - started) * 1000, "dense_search": (time.perf_counter() - embedded_at) * 1000}


# v0.1 compatibility alias. New code should name the baseline explicitly.
DenseRetriever = HashingDenseRetriever


class FAISSDenseRetriever:
    def __init__(self, store: FaissVectorStore, embedder: Embedder) -> None:
        self.store = store
        self.embedder = embedder

    def search(self, query: str, limit: int) -> list[SearchHit]:
        hits, _ = self.search_with_profile(query, limit)
        return hits

    def search_with_profile(self, query: str, limit: int) -> tuple[list[SearchHit], dict[str, float]]:
        started = time.perf_counter()
        query_vector = self.embedder.embed_query(query) if hasattr(self.embedder, "embed_query") else self.embedder.embed(query)
        embedded_at = time.perf_counter()
        hits = [SearchHit(chunk=chunk, score=score, retriever="faiss_dense")
                for chunk, score in self.store.search(query_vector, limit)]
        return hits, {"embedding": (embedded_at - started) * 1000, "faiss": (time.perf_counter() - embedded_at) * 1000}


class BM25Retriever:
    def __init__(self, chunks: Iterable[Chunk], k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks = list(chunks)
        self.k1, self.b = k1, b
        self.tokens = [tokenize(chunk.text) for chunk in self.chunks]
        self.lengths = [len(tokens) for tokens in self.tokens]
        self.average_length = sum(self.lengths) / len(self.lengths) if self.lengths else 0.0
        self.document_frequency: dict[str, int] = defaultdict(int)
        for terms in self.tokens:
            for term in set(terms):
                self.document_frequency[term] += 1

    def search(self, query: str, limit: int) -> list[SearchHit]:
        hits, _ = self.search_with_profile(query, limit)
        return hits

    def search_with_profile(self, query: str, limit: int) -> tuple[list[SearchHit], dict[str, float]]:
        started = time.perf_counter()
        total = len(self.chunks)
        query_terms = tokenize(query)
        scored: list[tuple[float, Chunk]] = []
        for chunk, terms, length in zip(self.chunks, self.tokens, self.lengths):
            frequency = Counter(terms)
            score = 0.0
            for term in query_terms:
                df = self.document_frequency.get(term, 0)
                if not df:
                    continue
                idf = math.log(1 + (total - df + 0.5) / (df + 0.5))
                denominator = frequency[term] + self.k1 * (1 - self.b + self.b * length / max(self.average_length, 1))
                score += idf * (frequency[term] * (self.k1 + 1) / denominator)
            scored.append((score, chunk))
        hits = [SearchHit(chunk=chunk, score=score, retriever="bm25") for score, chunk in sorted(scored, reverse=True, key=lambda pair: pair[0])[:limit]]
        return hits, {"bm25": (time.perf_counter() - started) * 1000}


class HybridRetriever:
    def __init__(self, dense: Retriever, bm25: BM25Retriever, rrf_k: int = 60) -> None:
        self.dense, self.bm25, self.rrf_k = dense, bm25, rrf_k

    def search(self, query: str, limit: int) -> list[SearchHit]:
        hits, _ = self.search_with_profile(query, limit)
        return hits

    def search_with_profile(self, query: str, limit: int) -> tuple[list[SearchHit], dict[str, float]]:
        candidates = max(limit * 2, 20)
        started = time.perf_counter()
        dense_results, dense_profile = self.dense.search_with_profile(query, candidates) if hasattr(self.dense, "search_with_profile") \
            else (self.dense.search(query, candidates), {})
        dense_at = time.perf_counter()
        bm25_results, bm25_profile = self.bm25.search_with_profile(query, candidates)
        bm25_at = time.perf_counter()
        fused: dict[str, tuple[Chunk, float]] = {}
        for results in (dense_results, bm25_results):
            seen_in_branch: set[str] = set()
            for rank, hit in enumerate(results, start=1):
                if hit.chunk.chunk_id in seen_in_branch:
                    continue
                seen_in_branch.add(hit.chunk.chunk_id)
                current_chunk, current_score = fused.get(hit.chunk.chunk_id, (hit.chunk, 0.0))
                fused[hit.chunk.chunk_id] = (current_chunk, current_score + 1.0 / (self.rrf_k + rank))
        ordered = sorted(fused.values(), key=lambda item: item[1], reverse=True)[:limit]
        profile = {**dense_profile, **bm25_profile, "rrf": (time.perf_counter() - bm25_at) * 1000,
                   "hybrid_total": (time.perf_counter() - started) * 1000}
        return [SearchHit(chunk=chunk, score=score, retriever="hybrid") for chunk, score in ordered], profile


_CROSS_ENCODER_CACHE: dict[str, Any] = {}
_CROSS_ENCODER_LOCK = threading.Lock()


class TransparentReranker(Reranker):
    """Transparent baseline reranker; replace with a cross-encoder adapter after baseline evaluation."""
    def rerank(self, query: str, candidates: Sequence[SearchHit], limit: int) -> list[SearchHit]:
        query_terms = set(tokenize(query))
        rescored = []
        for hit in candidates:
            terms = set(tokenize(hit.chunk.text))
            coverage = len(query_terms & terms) / max(len(query_terms), 1)
            rescored.append(SearchHit(hit.chunk, (0.7 * hit.score) + (0.3 * coverage), "reranked"))
        return sorted(rescored, key=lambda hit: hit.score, reverse=True)[:limit]


# v0.1 compatibility alias.
OverlapReranker = TransparentReranker


class CrossEncoderReranker(Reranker):
    """Optional sentence-transformers cross-encoder with transparent fallback on runtime failure."""
    def __init__(self, model_name: str | None = None, batch_size: int = 16, fallback: Reranker | None = None) -> None:
        self.model_name = model_name or __import__("os").getenv(
            "RERANKER_MODEL", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
        )
        self.batch_size = batch_size
        self.fallback = fallback or TransparentReranker()
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model
        with _CROSS_ENCODER_LOCK:
            if self.model_name in _CROSS_ENCODER_CACHE:
                self._model = _CROSS_ENCODER_CACHE[self.model_name]
                return self._model
            try:
                from sentence_transformers import CrossEncoder
                model = CrossEncoder(self.model_name)
                _CROSS_ENCODER_CACHE[self.model_name] = model
                self._model = model
                return self._model
            except Exception as exc:
                raise RuntimeError(f"Unable to load reranker model '{self.model_name}': {exc}") from exc

    def rerank(self, query: str, candidates: Sequence[SearchHit], limit: int) -> list[SearchHit]:
        if not candidates:
            return []
        try:
            scores = self._load_model().predict([(query, hit.chunk.text) for hit in candidates], batch_size=self.batch_size)
            ranked = [SearchHit(hit.chunk, float(score), "cross_encoder") for hit, score in zip(candidates, scores)]
            return sorted(ranked, key=lambda hit: hit.score, reverse=True)[:limit]
        except Exception:
            return self.fallback.rerank(query, candidates, limit)
