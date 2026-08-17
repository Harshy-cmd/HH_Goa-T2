from __future__ import annotations

from pathlib import Path
from scripts.benchmark import evaluate, load_cases
from app.domain import Chunk, SearchHit


class DummyRetriever:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks

    def search_with_profile(self, query: str, limit: int) -> tuple[list[SearchHit], dict[str, float]]:
        return [SearchHit(c, 0.9, "dummy") for c in self.chunks[:limit]], {"embedding": 1.0, "faiss": 0.1}


def test_load_cases_filters_to_en_and_hi_scope() -> None:
    root = Path(__file__).resolve().parents[2]
    eval_path = root / "data" / "evaluation" / "msmarco_xi_dev" / "eval_cases.jsonl"

    # All cases
    all_cases = load_cases(eval_path, languages=None)
    assert len(all_cases) == 150
    assert sum(1 for c in all_cases if c["language"] == "en") == 50
    assert sum(1 for c in all_cases if c["language"] == "hi") == 50
    assert sum(1 for c in all_cases if c["language"] == "kn") == 50

    # Official scope (en, hi)
    official_cases = load_cases(eval_path, languages={"en", "hi"})
    assert len(official_cases) == 100
    assert sum(1 for c in official_cases if c["language"] == "en") == 50
    assert sum(1 for c in official_cases if c["language"] == "hi") == 50
    assert sum(1 for c in official_cases if c["language"] == "kn") == 0


def test_evaluate_metric_aggregation_scope() -> None:
    root = Path(__file__).resolve().parents[2]
    eval_path = root / "data" / "evaluation" / "msmarco_xi_dev" / "eval_cases.jsonl"
    cases = load_cases(eval_path, languages={"en", "hi"})

    chunk = Chunk("msmarco-xi:en:1098975:3", "msmarco-xi:en:1098975:3", "doc", "text", 0, "sentence", language="en")
    retriever = DummyRetriever([chunk])

    results = evaluate(retriever, cases, limit=3)

    # Keys must be en, hi, overall only
    assert set(results.keys()) == {"en", "hi", "overall"}
    assert results["en"]["query_count"] == 50
    assert results["hi"]["query_count"] == 50
    assert results["overall"]["query_count"] == 100
    assert "kn" not in results
