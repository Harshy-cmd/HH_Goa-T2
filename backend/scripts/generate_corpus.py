"""Generate authoritative multi-domain NOVARON corpus.
"""
from __future__ import annotations

import json
from pathlib import Path

from corpus_builder import get_all_curated_documents

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
FIXTURES_DIR = DATA_DIR / "fixtures"

def generate_corpus() -> None:
    curated_docs = get_all_curated_documents()
    
    # Load evaluation MS MARCO passages
    eval_corpus_path = DATA_DIR / "evaluation" / "msmarco_xi_dev" / "corpus.jsonl"
    msmarco_docs = []
    if eval_corpus_path.exists():
        with open(eval_corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    doc = json.loads(line)
                    if "domain" not in doc:
                        doc["domain"] = "general_knowledge"
                    if "topic" not in doc:
                        doc["topic"] = "msmarco_eval"
                    if "source_type" not in doc:
                        doc["source_type"] = "msmarco"
                    msmarco_docs.append(doc)

    all_docs = curated_docs + msmarco_docs
    
    # Deduplicate and validate
    seen_ids = set()
    unique_docs = []
    for doc in all_docs:
        pid = doc.get("passage_id") or doc.get("document_id")
        if not pid or pid in seen_ids:
            continue
        seen_ids.add(pid)
        
        # Validation checks
        assert doc.get("document_id"), f"Missing document_id in {doc}"
        assert doc.get("text"), f"Empty text in {doc}"
        assert doc.get("language") in {"en", "hi", "kn"}, f"Invalid language {doc.get('language')}"
        unique_docs.append(doc)

    # 1. Save core fixtures to sample_corpus.jsonl
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    sample_corpus_file = FIXTURES_DIR / "sample_corpus.jsonl"
    with open(sample_corpus_file, "w", encoding="utf-8") as f:
        for doc in curated_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    # 2. Save full unified corpus to novaron_corpus.jsonl
    novaron_corpus_file = DATA_DIR / "novaron_corpus.jsonl"
    with open(novaron_corpus_file, "w", encoding="utf-8") as f:
        for doc in unique_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"Successfully generated NOVARON knowledge corpus:")
    print(f"  Curated multi-domain documents: {len(curated_docs)}")
    print(f"  MS MARCO evaluation passages:   {len(msmarco_docs)}")
    print(f"  Total unique documents:         {len(unique_docs)}")
    print(f"  Saved to: {sample_corpus_file}")
    print(f"  Saved to: {novaron_corpus_file}")

if __name__ == "__main__":
    generate_corpus()
