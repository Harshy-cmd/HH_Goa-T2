from __future__ import annotations

import pytest
from app.domain import Chunk, SearchHit
from app.retrieval import CrossEncoderReranker, TransparentReranker


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


class MockCrossEncoderModel:
    def __init__(self, scores_map: dict[str, float]) -> None:
        self.scores_map = scores_map
        self.recorded_pairs = []

    def predict(self, pairs: list[tuple[str, str]], batch_size: int = 16):
        self.recorded_pairs.extend(pairs)
        return [self.scores_map.get(text, 0.0) for _, text in pairs]


def test_cross_encoder_reranks_and_preserves_metadata() -> None:
    chunk_a = make_chunk("chunk-a", "doc-a", "Photosynthesis in green plants", "en")
    chunk_b = make_chunk("chunk-b", "doc-b", "Artificial neural networks in AI", "en")
    chunk_c = make_chunk("chunk-c", "doc-c", "Quantum computing fundamentals", "en")

    candidates = [
        SearchHit(chunk_b, 0.9, "dense"),
        SearchHit(chunk_c, 0.8, "dense"),
        SearchHit(chunk_a, 0.7, "dense"),
    ]

    reranker = CrossEncoderReranker(model_name="mock-model")
    reranker._model = MockCrossEncoderModel({
        chunk_a.text: 0.99,
        chunk_b.text: 0.10,
        chunk_c.text: 0.05,
    })

    hits = reranker.rerank("What is plant photosynthesis?", candidates, limit=2)

    assert len(hits) == 2
    assert hits[0].chunk.chunk_id == "chunk-a"
    assert hits[0].chunk.document_id == "doc-a"
    assert hits[0].chunk.language == "en"
    assert hits[0].score == 0.99
    assert hits[0].retriever == "cross_encoder"

    assert hits[1].chunk.chunk_id == "chunk-b"
    assert hits[1].score == 0.10


def test_cross_encoder_empty_candidates_returns_empty() -> None:
    reranker = CrossEncoderReranker(model_name="mock-model")
    assert reranker.rerank("query", [], limit=3) == []


def test_cross_encoder_fallback_on_exception() -> None:
    class FailingModel:
        def predict(self, pairs, **kwargs):
            raise RuntimeError("CUDA out of memory simulation")

    chunk_a = make_chunk("a", "doc-a", "photosynthesis sunlight")
    chunk_b = make_chunk("b", "doc-b", "unrelated text")
    candidates = [SearchHit(chunk_a, 0.5, "dense"), SearchHit(chunk_b, 0.4, "dense")]

    reranker = CrossEncoderReranker(model_name="failing-model")
    reranker._model = FailingModel()

    # Must not raise, but gracefully fallback to TransparentReranker
    results = reranker.rerank("photosynthesis", candidates, limit=2)
    assert len(results) == 2
    assert results[0].retriever == "reranked"  # TransparentReranker marker
