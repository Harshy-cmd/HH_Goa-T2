from __future__ import annotations

import json
import time

from app.domain import Chunk, SearchHit
from app.retrieval import CrossEncoderReranker


def main() -> None:
    candidates = [
        SearchHit(Chunk("relevant", "doc-1", "passage-1", "Photosynthesis uses sunlight to make sugars.", 0, "fixed"), 0.1, "hybrid"),
        SearchHit(Chunk("other", "doc-2", "passage-2", "Mars is the fourth planet from the Sun.", 0, "fixed"), 0.2, "hybrid"),
    ]
    reranker = CrossEncoderReranker()
    started = time.perf_counter()
    results = reranker.rerank("What is photosynthesis?", candidates, limit=2)
    elapsed = (time.perf_counter() - started) * 1000
    if not results or results[0].retriever != "cross_encoder":
        raise RuntimeError("Cross-encoder smoke test fell back to the transparent reranker; inspect model/dependency configuration.")
    print(json.dumps({"model": reranker.model_name, "top_chunk_id": results[0].chunk.chunk_id,
                      "latency_ms": round(elapsed, 3)}, indent=2))


if __name__ == "__main__":
    main()
