"""Audit Multilingual State of NOVARON.
Inspects active corpus, index files, language distributions, chunking strategies, and manifest metadata.
Outputs a structured, machine-readable JSON summary.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CORPUS_PATH = DATA_DIR / "novaron_corpus.jsonl"
INDEXES_DIR = DATA_DIR / "indexes"

from app.ingestion import fixed_chunks, hierarchical_chunks, load_jsonl, sentence_chunks


def audit_state() -> dict:
    if not CORPUS_PATH.exists():
        return {"error": f"Corpus not found at {CORPUS_PATH}"}

    docs = load_jsonl(CORPUS_PATH)
    sent_c = sentence_chunks(docs)
    fix_c = fixed_chunks(docs)
    hier_c = hierarchical_chunks(docs)

    lang_doc_counts = dict(Counter(d.language or "unknown" for d in docs))
    lang_chunk_counts = dict(Counter(c.language or "unknown" for c in sent_c))

    manifest_info = {}
    faiss_vectors = {}
    for strat in ["sentence", "fixed", "hierarchical"]:
        m_file = INDEXES_DIR / strat / "manifest.json"
        if m_file.exists():
            m = json.loads(m_file.read_text(encoding="utf-8"))
            manifest_info[strat] = m
            faiss_vectors[strat] = m.get("vector_count", 0)

    summary = {
        "corpus_documents": len(docs),
        "sentence_chunks": len(sent_c),
        "fixed_chunks": len(fix_c),
        "hierarchical_chunks": len(hier_c),
        "faiss_vectors": faiss_vectors.get("sentence", 0),
        "faiss_vectors_by_strategy": faiss_vectors,
        "bm25_documents": len(sent_c),
        "languages_present": sorted(list(lang_doc_counts.keys())),
        "documents_per_language": lang_doc_counts,
        "chunks_per_language": lang_chunk_counts,
        "embedding_model": manifest_info.get("sentence", {}).get("embedding_model", "intfloat/multilingual-e5-small"),
        "embedding_dimension": manifest_info.get("sentence", {}).get("dimensions", 384),
        "retrieval_modes": ["dense", "bm25", "hybrid", "hybrid_rerank"],
        "chunking_strategies": ["sentence", "fixed", "hierarchical"],
    }
    return summary


def main():
    state = audit_state()
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
