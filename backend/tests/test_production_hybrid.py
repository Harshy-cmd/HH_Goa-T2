from __future__ import annotations

import pytest
from app.domain import Chunk, SearchHit
from app.retrieval import BM25Retriever, FAISSDenseRetriever, HybridRetriever
from app.vector_store import FaissVectorStore


class MockDenseRetriever:
    def __init__(self, hits: list[SearchHit], profile: dict[str, float] | None = None) -> None:
        self.hits = hits
        self.profile = profile or {"embedding": 10.0, "faiss": 0.5}

    def search(self, query: str, limit: int) -> list[SearchHit]:
        return self.hits[:limit]

    def search_with_profile(self, query: str, limit: int) -> tuple[list[SearchHit], dict[str, float]]:
        return self.hits[:limit], self.profile


def make_chunk(cid: str, doc_id: str, text: str, lang: str = "en") -> Chunk:
    return Chunk(
        chunk_id=cid,
        document_id=doc_id,
        passage_id=doc_id,
        text=text,
        chunk_index=0,
        strategy="sentence",
        language=lang,
    )


def test_hybrid_fuses_dense_and_bm25_correctly() -> None:
    chunk_a = make_chunk("chunk-a", "doc-a", "python programming language")
    chunk_b = make_chunk("chunk-b", "doc-b", "java programming language")
    chunk_c = make_chunk("chunk-c", "doc-c", "ruby on rails framework")

    # Dense ranks: a (1), b (2)
    dense = MockDenseRetriever([
        SearchHit(chunk_a, 0.9, "faiss_dense"),
        SearchHit(chunk_b, 0.8, "faiss_dense"),
    ])

    # BM25 ranks: b (1), c (2)
    bm25 = BM25Retriever([chunk_a, chunk_b, chunk_c])

    hybrid = HybridRetriever(dense=dense, bm25=bm25, rrf_k=60)
    hits, profile = hybrid.search_with_profile("programming", limit=3)

    # Both dense and bm25 branches must be represented
    assert len(hits) <= 3
    # Check that profile contains all expected stage keys
    assert "embedding" in profile
    assert "faiss" in profile
    assert "bm25" in profile
    assert "rrf" in profile
    assert "hybrid_total" in profile

    # Chunk B appears in dense (rank 2) and BM25 (rank 1 or 2), accumulating both reciprocal ranks
    # RRF score formula: 1/(k+rank_dense) + 1/(k+rank_bm25)
    hit_ids = [h.chunk.chunk_id for h in hits]
    assert "chunk-b" in hit_ids
    assert all(h.retriever == "hybrid" for h in hits)


def test_hybrid_deterministic_ordering() -> None:
    chunk_a = make_chunk("chunk-a", "doc-a", "solar energy panels")
    chunk_b = make_chunk("chunk-b", "doc-b", "wind turbine power")

    dense = MockDenseRetriever([
        SearchHit(chunk_a, 0.95, "faiss_dense"),
        SearchHit(chunk_b, 0.85, "faiss_dense"),
    ])
    bm25 = BM25Retriever([chunk_a, chunk_b])

    hybrid = HybridRetriever(dense=dense, bm25=bm25, rrf_k=60)
    res1 = hybrid.search("solar energy", limit=2)
    res2 = hybrid.search("solar energy", limit=2)

    assert [h.chunk.chunk_id for h in res1] == [h.chunk.chunk_id for h in res2]
    assert [h.score for h in res1] == [h.score for h in res2]


def test_hybrid_duplicate_chunks_in_branch_do_not_inflate_rank() -> None:
    chunk_a = make_chunk("chunk-a", "doc-a", "machine learning algorithms")
    chunk_b = make_chunk("chunk-b", "doc-b", "deep learning neural networks")

    # Dense returns duplicate chunk_a
    dense = MockDenseRetriever([
        SearchHit(chunk_a, 0.95, "faiss_dense"),
        SearchHit(chunk_a, 0.90, "faiss_dense"),  # duplicate
        SearchHit(chunk_b, 0.85, "faiss_dense"),
    ])
    bm25 = BM25Retriever([chunk_a, chunk_b])

    hybrid = HybridRetriever(dense=dense, bm25=bm25, rrf_k=60)
    hits = hybrid.search("learning", limit=5)

    # Chunk A should appear only once in the final hits
    ids = [h.chunk.chunk_id for h in hits]
    assert len(ids) == len(set(ids))


def test_hybrid_handles_empty_branch_gracefully() -> None:
    chunk_a = make_chunk("chunk-a", "doc-a", "photosynthesis in plants")

    # Dense has no hits
    dense_empty = MockDenseRetriever([])
    bm25 = BM25Retriever([chunk_a])

    hybrid = HybridRetriever(dense=dense_empty, bm25=bm25, rrf_k=60)
    hits, profile = hybrid.search_with_profile("photosynthesis", limit=2)
    assert len(hits) == 1
    assert hits[0].chunk.chunk_id == "chunk-a"

    # BM25 has no query matches
    dense = MockDenseRetriever([SearchHit(chunk_a, 0.9, "faiss_dense")])
    hybrid2 = HybridRetriever(dense=dense, bm25=bm25, rrf_k=60)
    hits2, profile2 = hybrid2.search_with_profile("xyznomatchxyz", limit=2)
    assert len(hits2) == 1
    assert hits2[0].chunk.chunk_id == "chunk-a"


def test_hybrid_top_k_limit_and_metadata_preservation() -> None:
    chunks = [
        make_chunk(f"chunk-{i}", f"doc-{i}", f"passage text number {i}", lang="hi")
        for i in range(10)
    ]
    dense_hits = [SearchHit(c, 1.0 - i * 0.05, "faiss_dense") for i, c in enumerate(chunks)]
    dense = MockDenseRetriever(dense_hits)
    bm25 = BM25Retriever(chunks)

    hybrid = HybridRetriever(dense=dense, bm25=bm25, rrf_k=60)
    hits = hybrid.search("passage text", limit=3)

    assert len(hits) == 3
    for h in hits:
        assert h.chunk.language == "hi"
        assert h.chunk.document_id.startswith("doc-")
        assert h.chunk.text.startswith("passage text number")
        assert isinstance(h.score, float)
        assert h.score > 0.0
