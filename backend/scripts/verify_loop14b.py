"""Comprehensive Loop 14B Live Application Verification Suite.
Tests live endpoints: GET /health, POST /v1/query, POST /v1/voice/query, POST /v1/tts.
Covers English, Hindi, Hinglish, Conversational, System, Grounded, and 10 Unsupported queries.
"""
from __future__ import annotations

import io
import struct
import sys
import time
import wave

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 95)
print("NOVARON LOOP 14B — END-TO-END APPLICATION & RETRIEVAL VERIFICATION")
print("=" * 95)

# 1. Health Check
health_resp = client.get("/health")
assert health_resp.status_code == 200
print(f"1. /health check: Status={health_resp.status_code} Response={health_resp.json()}")

# 2. English Knowledge Queries (Multi-domain)
en_queries = [
    "What is Python?",
    "What is recursion?",
    "What is a binary tree?",
    "What is TCP?",
    "What is SQL normalization?",
    "What is machine learning?",
    "What is a transformer?",
    "What is RAG?",
    "What is FAISS?",
    "What is gravity?",
    "What is photosynthesis?",
    "What is DNA?",
    "What is probability?",
    "What is a derivative?",
    "What is supply and demand?",
]

print("\n2. English Knowledge Queries (15 Real Questions):")
for q in en_queries:
    t0 = time.perf_counter()
    resp = client.post("/v1/query", json={"query": q, "top_k": 3, "chunking_strategy": "sentence", "retrieval_mode": "dense"})
    assert resp.status_code == 200, f"Query '{q}' failed with {resp.status_code}"
    data = resp.json()
    wall_ms = (time.perf_counter() - t0) * 1000
    top_doc = data["sources"][0]["document_id"] if data["sources"] else "--"
    top_score = data["sources"][0]["relevance_score"] if data["sources"] else "--"
    print(f"  [Q]: {q:<35} | Type: {data.get('query_type'):<10} | Refused: {data['refused']!s:<5} | TopDoc: {top_doc:<32} | Score: {str(top_score):<6} | Wall: {wall_ms:.1f}ms")
    assert not data["refused"], f"Query '{q}' was unexpectedly refused"
    assert len(data["sources"]) > 0, f"Query '{q}' had 0 sources"

# 3. Hindi & Hinglish Multilingual Queries
hi_queries = [
    ("Python kya hai?", "hi"),
    ("कृत्रिम बुद्धिमत्ता क्या है?", "hi"),
    ("मशीन लर्निंग क्या है?", "hi"),
    ("गुरुत्वाकर्षण क्या है?", "hi"),
    ("प्रकाश संश्लेषण क्या है?", "hi"),
    ("डेटाबेस क्या है?", "hi"),
]

print("\n3. Hindi & Hinglish Multilingual Queries (6 Real Questions):")
for q, lang in hi_queries:
    t0 = time.perf_counter()
    resp = client.post("/v1/query", json={"query": q, "top_k": 3, "chunking_strategy": "sentence", "retrieval_mode": "dense", "language": lang})
    assert resp.status_code == 200, f"Query '{q}' failed with {resp.status_code}"
    data = resp.json()
    wall_ms = (time.perf_counter() - t0) * 1000
    top_doc = data["sources"][0]["document_id"] if data["sources"] else "--"
    top_score = data["sources"][0]["relevance_score"] if data["sources"] else "--"
    print(f"  [Q]: {q:<35} | Type: {data.get('query_type'):<10} | Refused: {data['refused']!s:<5} | TopDoc: {top_doc:<30} | Score: {str(top_score):<6} | Wall: {wall_ms:.1f}ms")
    assert not data["refused"], f"Hindi Query '{q}' was unexpectedly refused"
    assert len(data["sources"]) > 0, f"Hindi Query '{q}' had 0 sources"

# 4. Conversational and Identity Queries
router_queries = [
    "What is your name?",
    "Who are you?",
    "Hello",
]

print("\n4. Conversational & Identity Routing:")
for q in router_queries:
    t0 = time.perf_counter()
    resp = client.post("/v1/query", json={"query": q, "top_k": 3})
    assert resp.status_code == 200, f"Query '{q}' failed with {resp.status_code}"
    data = resp.json()
    wall_ms = (time.perf_counter() - t0) * 1000
    print(f"  [Q]: {q:<25} | Type: {data.get('query_type'):<15} | Latency: {data['latency_ms'].get('total', 0):.2f}ms | Wall: {wall_ms:.1f}ms | Ans: {data['answer'][:60]}...")
    assert not data["refused"]
    assert len(data["sources"]) == 0

# 5. Unsupported Questions (Zero Hallucination Guardrail Check - 10 queries)
unsupported_queries = [
    "What is the exact secret recipe for Martian cosmic space cake?",
    "How many invisible purple dragons live inside Mount Olympus?",
    "What was the winning lottery number in the Andromeda galaxy last week?",
    "How do you convert fairy dust into quantum gravity engines?",
    "What is the phone number of the emperor of Atlantis?",
    "How many unicorns were registered in Hogwarts in the year 1842?",
    "What is the airspeed velocity of an unladen flying magic carpet?",
    "Who won the 1923 Olympic gold medal for time traveling?",
    "Where is the exact GPS coordinate of King Arthur's floating castle?",
    "What temperature does chocolate vapor turn into dark matter?",
]

print("\n5. Unsupported Questions (Grounding Refusal Check - 10 Queries):")
for q in unsupported_queries:
    t0 = time.perf_counter()
    resp = client.post("/v1/query", json={"query": q, "top_k": 3, "chunking_strategy": "sentence", "retrieval_mode": "dense"})
    assert resp.status_code == 200, f"Query '{q}' failed with {resp.status_code}"
    data = resp.json()
    wall_ms = (time.perf_counter() - t0) * 1000
    print(f"  [Q]: {q[:45]:<45}... | Type: {data.get('query_type'):<10} | Refused: {data['refused']!s:<5} | Sources: {len(data['sources'])} | Wall: {wall_ms:.1f}ms")
    assert data["refused"] is True, f"Expected refusal for unsupported query '{q}', got refused=False"
    assert len(data["sources"]) == 0, f"Expected 0 sources for refused query '{q}', got {len(data['sources'])}"

# 6. Voice Query Test across domains (/v1/voice/query)
print("\n6. Voice Query Flow (/v1/voice/query):")
wav_buf = io.BytesIO()
with wave.open(wav_buf, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    samples = [0] * 8000
    wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
dummy_wav_bytes = wav_buf.getvalue()

from app.stt import MockSTT
import app.main as main_mod

voice_test_cases = [
    ("What is Python programming?", "CS Question"),
    ("What is machine learning?", "AI Question"),
    ("What is gravity?", "Science Question"),
    ("प्रकाश संश्लेषण क्या है?", "Hindi Question"),
    ("What is the secret recipe for Martian cosmic space cake?", "Unsupported Voice Question"),
]

for v_query, label in voice_test_cases:
    main_mod.stt_adapter = MockSTT(v_query)
    voice_resp = client.post(
        "/v1/voice/query",
        files={"file": ("speech.wav", dummy_wav_bytes, "audio/wav")},
        data={"chunking_strategy": "sentence", "retrieval_mode": "dense", "synthesize_audio": "true"},
    )
    assert voice_resp.status_code == 200
    v_data = voice_resp.json()
    print(f"  [{label}]: Transcript='{v_data['query']}' | Type={v_data.get('query_type')} | Refused={v_data['refused']} | Sources={len(v_data['sources'])} | AudioChars={len(v_data.get('audio_base64') or '')}")

# 7. TTS Synthesis
print("\n7. Text-to-Speech (/v1/tts):")
tts_en = client.post("/v1/tts", json={"text": "Python is a high-level, interpreted programming language.", "language": "en"})
assert tts_en.status_code == 200
print(f"  TTS English: Status={tts_en.status_code} | Bytes={len(tts_en.content)}")

tts_hi = client.post("/v1/tts", json={"text": "पायथन एक उच्च-स्तरीय प्रोग्रामिंग भाषा है।", "language": "hi"})
assert tts_hi.status_code == 200
print(f"  TTS Hindi:   Status={tts_hi.status_code} | Bytes={len(tts_hi.content)}")

print("\n" + "=" * 95)
print("ALL LOOP 14B LIVE ENDPOINT VERIFICATIONS COMPLETED SUCCESSFULLY WITH 100% PASS RATE!")
print("=" * 95)
