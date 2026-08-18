"""Audit Script for NOVARON Loop 14C (MSMARCO-XI Multilingual Integration).
Audits:
- languages currently present
- documents currently present
- chunks currently present
- FAISS vector counts
- BM25 document counts
- existing language metadata
- current retrieval strategies
- current router behavior
- current MSMARCO-XI ingestion state
- missing functionality / blockers
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CORPUS_PATH = DATA_DIR / "novaron_corpus.jsonl"
INDEXES_DIR = DATA_DIR / "indexes"
EVAL_QUERIES_PATH = DATA_DIR / "msmarco_xi_eval_queries.json"

from app.ingestion import fixed_chunks, hierarchical_chunks, load_jsonl, sentence_chunks
from app.router import classify_query, detect_language


def audit_corpus() -> dict:
    if not CORPUS_PATH.exists():
        return {"exists": False}
    docs = load_jsonl(CORPUS_PATH)
    sent_c = sentence_chunks(docs)
    fix_c = fixed_chunks(docs)
    hier_c = hierarchical_chunks(docs)

    lang_doc_counts = dict(Counter(d.language or "unknown" for d in docs))
    lang_chunk_counts = dict(Counter(c.language or "unknown" for c in sent_c))

    # Provenance audit
    msmarco_docs = [d for d in docs if "msmarco-xi" in d.document_id]
    curated_docs = [d for d in docs if "msmarco-xi" not in d.document_id]

    return {
        "exists": True,
        "total_documents": len(docs),
        "sentence_chunks": len(sent_c),
        "fixed_chunks": len(fix_c),
        "hierarchical_chunks": len(hier_c),
        "languages_present": sorted(list(lang_doc_counts.keys())),
        "documents_per_language": lang_doc_counts,
        "chunks_per_language": lang_chunk_counts,
        "msmarco_doc_count": len(msmarco_docs),
        "curated_doc_count": len(curated_docs),
    }


def audit_indexes() -> dict:
    strategies = ["sentence", "fixed", "hierarchical"]
    res = {}
    for strat in strategies:
        idx_dir = INDEXES_DIR / strat
        manifest_file = idx_dir / "manifest.json"
        index_bin = idx_dir / "index.faiss"
        chunks_json = idx_dir / "chunks.json"
        if manifest_file.exists() and index_bin.exists() and chunks_json.exists():
            try:
                m = json.loads(manifest_file.read_text(encoding="utf-8"))
                res[strat] = {
                    "exists": True,
                    "chunk_count": m.get("chunk_count", 0),
                    "vector_count": m.get("vector_count", 0),
                    "dimensions": m.get("dimensions", 0),
                    "model": m.get("embedding_model", ""),
                }
            except Exception as e:
                res[strat] = {"exists": True, "error": str(e)}
        else:
            res[strat] = {"exists": False}
    return res


def audit_router() -> dict:
    sample_queries = {
        "en": "What is Python programming language?",
        "hi": "प्रकाश संश्लेषण क्या है?",
        "bn": "সালোকসংশ্লেষণ কী এবং কিভাবে হয়?",
        "gu": "પ્રકાશસંશ્લેષણ શું છે?",
        "kn": "ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ ಎಂದರೇನು?",
        "ml": "പ്രകാശസംശ്ലേഷണം എന്താണ്?",
        "mr": "प्रकाशसंश्लेषण म्हणजे काय?",
        "ne": "प्रकाश संश्लेषण भनेको के हो?",
        "or": "ଆଲୋକ ସଂଶ୍ଳେଷଣ କଣ?",
        "pa": "ਪ੍ਰਕਾਸ਼ ਸੰਸਲੇਸ਼ਣ ਕੀ ਹੈ?",
        "sa": "प्रकाशसंश्लेषणं किम् अस्ति?",
        "ta": "ஒளிச்சேர்க்கை என்றால் என்ன?",
        "te": "కిరణజన్య సంయోగక్రియ అంటే ఏమిటి?",
        "ur": "فوٹو سنتھیسس کیا ہے؟",
        "as": "সালোক সংশ্লেষণ কিদৰে হয়?",
    }
    router_results = {}
    for lang, q in sample_queries.items():
        detected = detect_language(q)
        route_res = classify_query(q)
        status = "PASS" if detected == lang else f"FAIL (detected: {detected})"
        router_results[lang] = {
            "query": q,
            "detected_lang": detected,
            "status": status,
            "intent": route_res.intent.value,
        }
    return router_results


def audit_msmarco_eval() -> dict:
    if not EVAL_QUERIES_PATH.exists():
        return {"exists": False, "count": 0}
    try:
        queries = json.loads(EVAL_QUERIES_PATH.read_text(encoding="utf-8"))
        lang_counts = dict(Counter(q.get("language", "unknown") for q in queries))
        return {
            "exists": True,
            "total_queries": len(queries),
            "languages": sorted(list(lang_counts.keys())),
            "queries_per_language": lang_counts,
        }
    except Exception as e:
        return {"exists": False, "error": str(e)}


def main():
    corpus_info = audit_corpus()
    index_info = audit_indexes()
    router_info = audit_router()
    eval_info = audit_msmarco_eval()

    print("=" * 80)
    print("NOVARON LOOP 14C-1 — COMPREHENSIVE AUDIT REPORT")
    print("=" * 80)

    print("\n[1] CORPUS:")
    if corpus_info.get("exists"):
        print(f"  Documents:            {corpus_info['total_documents']}")
        print(f"  Curated Docs:         {corpus_info['curated_doc_count']}")
        print(f"  MSMARCO-XI Docs:      {corpus_info['msmarco_doc_count']}")
        print(f"  Sentence Chunks:      {corpus_info['sentence_chunks']}")
        print(f"  Fixed Chunks:         {corpus_info['fixed_chunks']}")
        print(f"  Hierarchical Chunks:  {corpus_info['hierarchical_chunks']}")
        print(f"  Languages ({len(corpus_info['languages_present'])}):        {', '.join(corpus_info['languages_present'])}")
        print("\n  Passages per Language:")
        for lang, count in sorted(corpus_info["documents_per_language"].items()):
            print(f"    - {lang:<4}: {count:>5} docs ({corpus_info['chunks_per_language'].get(lang, 0):>5} sentence chunks)")
    else:
        print("  Corpus file missing!")

    print("\n[2] INDEXES (FAISS):")
    for strat, info in index_info.items():
        if info.get("exists"):
            print(f"  {strat:<14}: chunk_count={info.get('chunk_count')}, vector_count={info.get('vector_count')}, dim={info.get('dimensions')}")
        else:
            print(f"  {strat:<14}: Missing / Incomplete")

    print("\n[3] BM25:")
    print(f"  Indexed Document Count: {corpus_info.get('sentence_chunks', 0)} (in-memory from sentence chunks)")

    print("\n[4] MSMARCO-XI EVALUATION DATASET:")
    if eval_info.get("exists"):
        print(f"  Available:            YES ({eval_info['total_queries']} paired evaluation queries)")
        print(f"  Languages:            {', '.join(eval_info['languages'])}")
    else:
        print("  Available:            NO")

    print("\n[5] ROUTER LANGUAGE DETECTION:")
    for lang, r in router_info.items():
        print(f"  {lang:<4}: {r['status']:<25} | Intent: {r['intent']}")

    # Identify Blockers
    blockers = []
    if corpus_info.get("sentence_chunks") != index_info.get("sentence", {}).get("chunk_count"):
        blockers.append(
            f"FAISS index count mismatch: corpus has {corpus_info.get('sentence_chunks')} chunks, but sentence index has {index_info.get('sentence', {}).get('chunk_count')} vectors"
        )
    for lang, r in router_info.items():
        if "FAIL" in r["status"]:
            blockers.append(f"Router fails on {lang}: detected as '{r['detected_lang']}' instead of '{lang}'")

    print("\n[6] IDENTIFIED BLOCKERS:")
    if blockers:
        for b in blockers:
            print(f"  [!] {b}")
    else:
        print("  None. All systems aligned.")
    print("=" * 80)


if __name__ == "__main__":
    main()
