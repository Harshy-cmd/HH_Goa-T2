from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.router import QueryIntent, classify_query


# 1. Deterministic Query Router Tests
def test_router_conversational_english():
    res = classify_query("Hello")
    assert res.intent == QueryIntent.CONVERSATIONAL
    assert res.direct_answer is not None
    assert "NOVARON" in res.direct_answer or "Hello" in res.direct_answer

    res_hi = classify_query("Hi NOVARON")
    assert res_hi.intent == QueryIntent.CONVERSATIONAL

    res_how = classify_query("How are you doing today?")
    assert res_how.intent == QueryIntent.CONVERSATIONAL
    assert res_how.direct_answer is not None


def test_router_conversational_hindi():
    res = classify_query("नमस्ते")
    assert res.intent == QueryIntent.CONVERSATIONAL
    assert res.direct_answer is not None
    assert "नमस्ते" in res.direct_answer


def test_router_system_identity_and_capabilities():
    res_name = classify_query("What's your name?")
    assert res_name.intent == QueryIntent.SYSTEM
    assert "NOVARON" in res_name.direct_answer

    res_who = classify_query("Who are you?")
    assert res_who.intent == QueryIntent.SYSTEM
    assert "NOVARON" in res_who.direct_answer

    res_can = classify_query("What can you do?")
    assert res_can.intent == QueryIntent.SYSTEM
    assert "RAG" in res_can.direct_answer or "questions" in res_can.direct_answer

    res_hi_name = classify_query("आपका नाम क्या है?")
    assert res_hi_name.intent == QueryIntent.SYSTEM
    assert "नोवारॉन" in res_hi_name.direct_answer


def test_router_knowledge_routing():
    for q in [
        "What is photosynthesis?",
        "What is FAISS?",
        "What is BM25?",
        "What is Python?",
        "What is artificial intelligence?",
        "What is RAG?",
        "What is gravity?",
        "What is the secret recipe for Martian cosmic space cake?",
    ]:
        res = classify_query(q)
        assert res.intent == QueryIntent.KNOWLEDGE
        assert res.direct_answer is None


# 2. End-to-End API Query Tests
@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_api_query_conversational(client):
    resp = client.post("/v1/query", json={"query": "Hello", "top_k": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert not data["refused"]
    assert data["query_type"] == "conversational"
    assert "NOVARON" in data["answer"] or "Hello" in data["answer"]
    assert len(data["sources"]) == 0
    assert "route" in data["latency_ms"]


def test_api_query_system_identity(client):
    resp = client.post("/v1/query", json={"query": "Who are you?", "top_k": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert not data["refused"]
    assert data["query_type"] == "system"
    assert "NOVARON" in data["answer"]
    assert len(data["sources"]) == 0


def test_api_query_system_capabilities(client):
    resp = client.post("/v1/query", json={"query": "What can you do?", "top_k": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert not data["refused"]
    assert data["query_type"] == "system"
    assert len(data["sources"]) == 0


def test_api_query_knowledge_photosynthesis(client):
    resp = client.post(
        "/v1/query",
        json={"query": "What is photosynthesis?", "top_k": 3, "chunking_strategy": "sentence", "retrieval_mode": "dense"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not data["refused"]
    assert len(data["sources"]) > 0
    assert any("photosynthesis" in s["text"].lower() or "light" in s["text"].lower() for s in data["sources"])


def test_api_query_knowledge_faiss(client):
    resp = client.post(
        "/v1/query",
        json={"query": "What is FAISS?", "top_k": 3, "chunking_strategy": "sentence", "retrieval_mode": "dense"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not data["refused"]
    assert len(data["sources"]) > 0
    assert any("faiss" in s["text"].lower() or "similarity" in s["text"].lower() for s in data["sources"])


def test_api_query_knowledge_python(client):
    resp = client.post(
        "/v1/query",
        json={"query": "What is Python?", "top_k": 3, "chunking_strategy": "sentence", "retrieval_mode": "dense"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not data["refused"]
    assert len(data["sources"]) > 0
    assert any("python" in s["text"].lower() for s in data["sources"])


def test_api_query_knowledge_ai(client):
    resp = client.post(
        "/v1/query",
        json={"query": "What is artificial intelligence?", "top_k": 3, "chunking_strategy": "sentence", "retrieval_mode": "dense"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not data["refused"]
    assert len(data["sources"]) > 0
    assert any("artificial intelligence" in s["text"].lower() or "machine learning" in s["text"].lower() for s in data["sources"])


def test_api_query_unsupported_refusal(client):
    resp = client.post(
        "/v1/query",
        json={
            "query": "What is the exact secret recipe for Martian cosmic space cake?",
            "top_k": 3,
            "chunking_strategy": "sentence",
            "retrieval_mode": "dense",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["refused"] is True
    assert len(data["sources"]) == 0
    assert "don't have enough information" in data["answer"].lower() or "refuse" in data["answer"].lower()
