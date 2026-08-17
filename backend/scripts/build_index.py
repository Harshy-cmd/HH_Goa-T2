from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

from app.embeddings import SentenceTransformerEmbeddingProvider
from app.ingestion import fixed_chunks, hierarchical_chunks, load_jsonl, sentence_chunks
from app.vector_store import FaissVectorStore


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Build a persistent NOVARON FAISS index.")
    parser.add_argument("--corpus", type=Path, default=root / "data" / "fixtures" / "sample_corpus.jsonl")
    parser.add_argument("--strategy", choices=("fixed", "sentence", "hierarchical"), default="fixed")
    parser.add_argument("--index-dir", type=Path, default=root / "data" / "indexes" / "fixed")
    parser.add_argument("--model", default=None, help="Sentence-transformers model; defaults to EMBEDDING_MODEL.")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--corpus-id", default=None, help="Stable corpus identifier included in the index manifest.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    passages = load_jsonl(args.corpus)
    chunker = {"fixed": fixed_chunks, "sentence": sentence_chunks, "hierarchical": hierarchical_chunks}[args.strategy]
    chunks = chunker(passages)
    provider = SentenceTransformerEmbeddingProvider(model_name=args.model)
    embeddings = provider.embed_documents([chunk.text for chunk in chunks], batch_size=args.batch_size)
    store = FaissVectorStore.build(chunks, embeddings)
    store.save(args.index_dir, {
        "embedding_model": provider.model_name,
        "chunking_strategy": args.strategy,
        "corpus_identifier": args.corpus_id or args.corpus.resolve().as_posix(),
        "chunk_count": len(chunks),
        "normalized": True,
        "embedding_prefixes": {"query": "query: " if provider.e5_prefixes else "",
                               "document": "passage: " if provider.e5_prefixes else ""},
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    elapsed = time.perf_counter() - started
    print(f"Built FAISS index: {args.index_dir}")
    print(f"Corpus passages: {len(passages)} | chunks: {len(chunks)} | dimensions: {store.dimensions}")
    print(f"Embedding model: {provider.model_name} | elapsed: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
