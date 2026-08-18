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
    default_corpus = root / "data" / "novaron_corpus.jsonl"
    if not default_corpus.exists():
        default_corpus = root / "data" / "fixtures" / "sample_corpus.jsonl"
    parser = argparse.ArgumentParser(description="Build persistent NOVARON FAISS indexes.")
    parser.add_argument("--corpus", type=Path, default=default_corpus)
    parser.add_argument("--strategy", choices=("fixed", "sentence", "hierarchical", "all"), default="sentence")
    parser.add_argument("--index-dir", type=Path, default=None)
    parser.add_argument("--model", default=None, help="Sentence-transformers model; defaults to EMBEDDING_MODEL.")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--corpus-id", default=None, help="Stable corpus identifier included in the index manifest.")
    return parser.parse_args()


def build_single_strategy(
    strategy: str,
    passages: list,
    provider: SentenceTransformerEmbeddingProvider,
    corpus_path: Path,
    index_root: Path,
    batch_size: int = 64,
    corpus_id: str | None = None,
) -> tuple[int, int, float]:
    started = time.perf_counter()
    chunker = {"fixed": fixed_chunks, "sentence": sentence_chunks, "hierarchical": hierarchical_chunks}[strategy]
    chunks = chunker(passages)
    index_dir = index_root / strategy
    
    print(f"Embedding {len(chunks)} chunks for '{strategy}' strategy with {provider.model_name}...")
    embeddings = provider.embed_documents([chunk.text for chunk in chunks], batch_size=batch_size)
    store = FaissVectorStore.build(chunks, embeddings)
    store.save(index_dir, {
        "embedding_model": provider.model_name,
        "chunking_strategy": strategy,
        "corpus_identifier": corpus_id or corpus_path.resolve().as_posix(),
        "chunk_count": len(chunks),
        "vector_count": len(chunks),
        "dimensions": store.dimensions,
        "normalized": True,
        "embedding_prefixes": {"query": "query: " if provider.e5_prefixes else "",
                               "document": "passage: " if provider.e5_prefixes else ""},
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    elapsed = time.perf_counter() - started
    print(f"  [OK] Built {strategy} index at {index_dir}: {len(chunks)} vectors (took {elapsed:.2f}s)")
    return len(chunks), store.dimensions, elapsed


def main() -> None:
    args = parse_args()
    passages = load_jsonl(args.corpus)
    print(f"Loaded {len(passages)} passages from {args.corpus}")
    
    provider = SentenceTransformerEmbeddingProvider(model_name=args.model)
    root = Path(__file__).resolve().parents[2]
    index_root = args.index_dir if args.index_dir else (root / "data" / "indexes")
    
    strategies = ["sentence", "fixed", "hierarchical"] if args.strategy == "all" else [args.strategy]
    
    for strat in strategies:
        target_dir = index_root if (args.index_dir and args.strategy != "all") else (index_root / strat)
        build_single_strategy(
            strategy=strat,
            passages=passages,
            provider=provider,
            corpus_path=args.corpus,
            index_root=index_root,
            batch_size=args.batch_size,
            corpus_id=args.corpus_id,
        )


if __name__ == "__main__":
    main()

