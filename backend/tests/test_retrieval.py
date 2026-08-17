from pathlib import Path

from app.ingestion import fixed_chunks, load_jsonl, sentence_chunks
from app.pipeline import ExtractiveGroundedGenerator, RAGPipeline
from app.retrieval import BM25Retriever, DenseRetriever, HashingEmbedder, HybridRetriever, OverlapReranker


def _pipeline() -> RAGPipeline:
    corpus = load_jsonl(Path(__file__).resolve().parents[2] / "data" / "fixtures" / "sample_corpus.jsonl")
    chunks = fixed_chunks(corpus, size_words=50, overlap_words=5)
    return RAGPipeline(HybridRetriever(DenseRetriever(chunks, HashingEmbedder()), BM25Retriever(chunks)), OverlapReranker(), ExtractiveGroundedGenerator(), 0.01)


def test_sentence_chunking_preserves_content() -> None:
    corpus = load_jsonl(Path(__file__).resolve().parents[2] / "data" / "fixtures" / "sample_corpus.jsonl")
    chunks = sentence_chunks(corpus, target_words=10)
    assert chunks
    assert all(chunk.text for chunk in chunks)


def test_hybrid_pipeline_returns_grounded_source() -> None:
    result = _pipeline().run("What is photosynthesis?")
    assert not result.refused
    assert result.sources
    assert result.sources[0].chunk.document_id.startswith("science-photosynthesis")

