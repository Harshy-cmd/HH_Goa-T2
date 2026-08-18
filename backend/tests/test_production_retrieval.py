from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.domain import Chunk, SearchHit
from app.embeddings import SentenceTransformerEmbeddingProvider, normalize_embedding_text
from app.generation import OpenAIGroundedLLM
from app.ingestion import fixed_chunks, load_jsonl
from app.main import QueryRequest, pipelines, query
from app.pipeline import ExtractiveGroundedGenerator, RAGPipeline, REFUSAL
from app.retrieval import (BM25Retriever, CrossEncoderReranker, HashingDenseRetriever,
                           HashingEmbedder, HybridRetriever, TransparentReranker)
from app.vector_store import FaissVectorStore, VectorStoreError


ROOT = Path(__file__).resolve().parents[2]


class FakeEmbeddingModel:
    def __init__(self) -> None:
        self.last_texts = []

    def encode(self, texts, **_kwargs):
        self.last_texts = texts
        return __import__("numpy").asarray([[float(len(text)), 1.0] for text in texts])

    def get_sentence_embedding_dimension(self):
        return 2


def test_embedding_adapter_normalizes_and_batches_without_network() -> None:
    provider = SentenceTransformerEmbeddingProvider(model_name="test-model")
    provider._model = FakeEmbeddingModel()
    assert normalize_embedding_text("  क\u094dया\t है? ") == "क्या है?"
    vectors = provider.embed_many(["  hello\nworld ", "नमस्ते"], batch_size=2)
    assert len(vectors) == 2
    assert vectors[0][0] > 0


def test_e5_prefixes_distinguish_query_and_documents(monkeypatch) -> None:
    monkeypatch.setenv("EMBEDDING_E5_PREFIXES", "auto")
    provider = SentenceTransformerEmbeddingProvider(model_name="intfloat/multilingual-e5-small")
    fake = FakeEmbeddingModel()
    provider._model = fake
    provider.embed_documents(["दस्तावेज़"])
    assert fake.last_texts == ["passage: दस्तावेज़"]
    provider.embed_query("प्रश्न")
    assert fake.last_texts == ["query: प्रश्न"]


def test_faiss_persistence_and_metadata_alignment(tmp_path: Path) -> None:
    pytest.importorskip("faiss")
    chunks = [
        Chunk("one", "doc-1", "passage-1", "hello", 0, "fixed"),
        Chunk("two", "doc-2", "passage-2", "नमस्ते", 0, "fixed", language="hi"),
    ]
    store = FaissVectorStore.build(chunks, [[1, 0], [0, 1]])
    store.save(tmp_path)
    loaded = FaissVectorStore.load(tmp_path)
    assert loaded.search([1, 0], 1)[0][0].chunk_id == "one"
    metadata = json.loads((tmp_path / "chunks.json").read_text(encoding="utf-8"))
    metadata.pop()
    (tmp_path / "chunks.json").write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(VectorStoreError, match="mismatch"):
        FaissVectorStore.load(tmp_path)


def test_faiss_manifest_rejects_incompatible_model(tmp_path: Path) -> None:
    pytest.importorskip("faiss")
    chunk = Chunk("one", "doc", "passage", "text", 0, "fixed")
    store = FaissVectorStore.build([chunk], [[1, 0]])
    store.save(tmp_path, {"embedding_model": "model-a", "chunking_strategy": "fixed", "normalized": True})
    with pytest.raises(VectorStoreError, match="embedding_model"):
        FaissVectorStore.load(tmp_path, expected_model="model-b", expected_strategy="fixed", expected_normalized=True)


def test_cross_encoder_reranker_uses_batch_scores() -> None:
    chunk_a = Chunk("a", "a", "a", "first", 0, "fixed")
    chunk_b = Chunk("b", "b", "b", "second", 0, "fixed")
    reranker = CrossEncoderReranker(model_name="test")
    reranker._model = type("Model", (), {"predict": lambda self, pairs, batch_size: [0.1, 0.9]})()
    ranked = reranker.rerank("query", [SearchHit(chunk_a, 0.1, "hybrid"), SearchHit(chunk_b, 0.2, "hybrid")], 2)
    assert [hit.chunk.chunk_id for hit in ranked] == ["b", "a"]
    assert ranked[0].retriever == "cross_encoder"


def test_grounded_llm_rejects_unknown_citations() -> None:
    hit = SearchHit(Chunk("known", "doc", "passage", "Evidence text", 0, "fixed"), 0.9, "hybrid")
    completion = type("Completion", (), {"choices": [type("Choice", (), {"message": type("Message", (), {
        "content": '{"answer":"unsupported","citation_chunk_ids":["unknown"],"refused":false}'
    })()})()]})()
    client = type("Client", (), {"chat": type("Chat", (), {"completions": type("Completions", (), {
        "create": lambda self, **kwargs: completion
    })()})()})()
    result = OpenAIGroundedLLM(client=client).answer("question", [hit])
    assert result.refused
    assert result.answer == REFUSAL


def test_refusal_on_insufficient_evidence() -> None:
    corpus = load_jsonl(ROOT / "data" / "fixtures" / "sample_corpus.jsonl")
    chunks = fixed_chunks(corpus)
    dense = HashingDenseRetriever(chunks, HashingEmbedder())
    pipeline = RAGPipeline(dense, None, ExtractiveGroundedGenerator(), minimum_score=0.99)
    result = pipeline.run("unrelated terms that are absent")
    assert result.refused
    assert result.answer == REFUSAL


def test_api_v01_request_shape_remains_compatible() -> None:
    response = query(QueryRequest(query="What is photosynthesis?"))
    assert not response.refused
    assert response.sources
    assert response.retrieval_strategy == "hybrid_rrf + reranker"
