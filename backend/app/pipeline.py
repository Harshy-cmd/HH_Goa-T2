from __future__ import annotations

import time
from dataclasses import dataclass

from app.domain import GeneratedAnswer, GroundedGenerator, Reranker, Retriever, SearchHit


REFUSAL = "I don't have enough information in the indexed knowledge base to answer that reliably."


class ExtractiveGroundedGenerator(GroundedGenerator):
    """Safe local baseline. A hosted LLM adapter can replace this implementation later."""
    def answer(self, query: str, evidence: list[SearchHit]) -> str:
        return evidence[0].chunk.text if evidence else REFUSAL


@dataclass(frozen=True)
class PipelineResult:
    answer: str
    sources: list[SearchHit]
    refused: bool
    latency_ms: dict[str, float]


class RAGPipeline:
    def __init__(self, retriever: Retriever, reranker: Reranker | None, generator: GroundedGenerator, minimum_score: float) -> None:
        self.retriever, self.reranker = retriever, reranker
        self.generator, self.minimum_score = generator, minimum_score

    def run(self, query: str, retrieval_limit: int = 10, answer_limit: int = 5) -> PipelineResult:
        started = time.perf_counter()
        candidates = self.retriever.search(query, retrieval_limit)
        retrieved_at = time.perf_counter()
        evidence = self.reranker.rerank(query, candidates, answer_limit) if self.reranker else candidates[:answer_limit]
        reranked_at = time.perf_counter()
        supported = bool(evidence) and evidence[0].score >= self.minimum_score
        generated = self.generator.answer(query, evidence) if supported else REFUSAL
        if isinstance(generated, GeneratedAnswer):
            supported = supported and not generated.refused
            answer = generated.answer if supported else REFUSAL
            cited = set(generated.citation_chunk_ids)
            evidence = [hit for hit in evidence if hit.chunk.chunk_id in cited] if supported else []
        else:
            answer = generated
        completed_at = time.perf_counter()
        return PipelineResult(
            answer=answer, sources=evidence if supported else [], refused=not supported,
            latency_ms={
                "retrieval": round((retrieved_at - started) * 1000, 3),
                "reranking": round((reranked_at - retrieved_at) * 1000, 3),
                "generation": round((completed_at - reranked_at) * 1000, 3),
                "rag_total": round((completed_at - started) * 1000, 3),
            },
        )
