"""Comprehensive Loop 14 Live Application Verification Suite.
Tests live endpoints: GET /health, POST /v1/query, POST /v1/voice/query, POST /v1/tts.
Covers English, Hindi, Conversational, System, Grounded, and 5+ Unsupported queries.
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

print("=" * 90)
print("NOVARON LOOP 14 — END-TO-END APPLICATION & RETRIEVAL VERIFICATION")
print("=" * 90)

# 1. Health Check
health_resp = client.get("/health")
assert health_resp.status_code == 200
print(f"1. /health check: Status={health_resp.status_code} Response={health_resp.json()}")

# 2. English Knowledge Queries
en_queries = [
    "What is Python?",
    "What is FAISS?",
    "What is RAG?",
    "What is gravity?",
    "What is photosynthesis?",
    "What is machine learning?",
    "What is a database?",
    "What is recursion?",
    "What is an operating system?",
    "What is artificial intelligence?",
]

print("\n2. English Knowledge Queries:")
for q in en_queries:
    t0 = time.perf_counter()
    resp = client.post("/v1/query", json={"query": q, "top_k": 3, "chunking_strategy": "sentence", "retrieval_mode": "dense"})
    assert resp.status_code == 200, f"Query '{q}' failed with {resp.status_code}"
    data = resp.json()
    wall_ms = (time.perf_counter() - t0) * 1000
    top_doc = data["sources"][0]["document_id"] if data["sources"] else "--"
    top_score = data["sources"][0]["relevance_score"] if data["sources"] else "--"
    print(f"  [Q]: {q:<35} | Type: {data.get('query_type'):<10} | Refused: {data['refused']!s:<5} | TopDoc: {top_doc:<25} | Score: {str(top_score):<6} | Wall: {wall_ms:.1f}ms")
    assert not data["refused"], f"Query '{q}' was unexpectedly refused"
    assert len(data["sources"]) > 0, f"Query '{q}' had 0 sources"

# 3. Hindi Multilingual Queries
hi_queries = [
    "पायथन क्या है?",
    "कृत्रिम बुद्धिमत्ता क्या है?",
    "गुरुत्वाकर्षण क्या है?",
    "प्रकाश संश्लेषण क्या है?",
]

print("\n3. Hindi Multilingual Queries:")
for q in hi_queries:
    t0 = time.perf_counter()
    resp = client.post("/v1/query", json={"query": q, "top_k": 3, "chunking_strategy": "sentence", "retrieval_mode": "dense", "language": "hi"})
    assert resp.status_code == 200, f"Query '{q}' failed with {resp.status_code}"
    data = resp.json()
    wall_ms = (time.perf_counter() - t0) * 1000
    top_doc = data["sources"][0]["document_id"] if data["sources"] else "--"
    top_score = data["sources"][0]["relevance_score"] if data["sources"] else "--"
    print(f"  [Q]: {q:<30} | Type: {data.get('query_type'):<10} | Refused: {data['refused']!s:<5} | TopDoc: {top_doc:<25} | Score: {str(top_score):<6} | Wall: {wall_ms:.1f}ms")
    assert not data["refused"], f"Hindi Query '{q}' was unexpectedly refused"
    assert len(data["sources"]) > 0, f"Hindi Query '{q}' had 0 sources"

# 4. Conversational and Identity Queries
router_queries = [
    "What is your name?",
    "Who are you?",
    "What can you do?",
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

# 5. Unsupported Questions (Zero Hallucination Guardrail)
unsupported_queries = [
    "What is the exact secret recipe for Martian cosmic space cake?",
    "How many invisible purple dragons live inside Mount Olympus?",
    "What was the winning lottery number in the Andromeda galaxy last week?",
    "How do you convert fairy dust into quantum gravity engines?",
    "What is the phone number of the emperor of Atlantis?",
]

print("\n5. Unsupported Questions (Grounding Refusal Check):")
for q in unsupported_queries:
    t0 = time.perf_counter()
    resp = client.post("/v1/query", json={"query": q, "top_k": 3, "chunking_strategy": "sentence", "retrieval_mode": "dense"})
    assert resp.status_code == 200, f"Query '{q}' failed with {resp.status_code}"
    data = resp.json()
    wall_ms = (time.perf_counter() - t0) * 1000
    print(f"  [Q]: {q[:45]:<45}... | Type: {data.get('query_type'):<10} | Refused: {data['refused']!s:<5} | Sources: {len(data['sources'])} | Wall: {wall_ms:.1f}ms")
    assert data["refused"] is True, f"Expected refusal for unsupported query '{q}', got refused=False"
    assert len(data["sources"]) == 0, f"Expected 0 sources for refused query '{q}', got {len(data['sources'])}"

# 6. Voice Query Test (/v1/voice/query)
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

main_mod.stt_adapter = MockSTT("What is Python programming?")
voice_resp = client.post(
    "/v1/voice/query",
    files={"file": ("speech.wav", dummy_wav_bytes, "audio/wav")},
    data={"chunking_strategy": "sentence", "retrieval_mode": "dense", "synthesize_audio": "true"},
)
assert voice_resp.status_code == 200
v_data = voice_resp.json()
print(f"  Transcript:   '{v_data['query']}'")
print(f"  Query Type:   {v_data.get('query_type')}")
print(f"  Refused:      {v_data['refused']}")
print(f"  Sources:      {len(v_data['sources'])}")
print(f"  Audio Base64: {'Present (' + str(len(v_data['audio_base64'])) + ' chars)' if v_data.get('audio_base64') else 'None'}")
print(f"  Latency:      {v_data['latency_ms']}")

# 7. TTS Synthesis
print("\n7. Text-to-Speech (/v1/tts):")
tts_en = client.post("/v1/tts", json={"text": "Python is a high-level, interpreted programming language.", "language": "en"})
assert tts_en.status_code == 200
print(f"  TTS English: Status={tts_en.status_code} | Bytes={len(tts_en.content)}")

tts_hi = client.post("/v1/tts", json={"text": "पायथन एक उच्च-स्तरीय प्रोग्रामिंग भाषा है।", "language": "hi"})
assert tts_hi.status_code == 200
print(f"  TTS Hindi:   Status={tts_hi.status_code} | Bytes={len(tts_hi.content)}")

print("\n" + "=" * 90)
print("ALL LIVE ENDPOINT VERIFICATIONS COMPLETED SUCCESSFULLY WITH 100% PASS RATE!")
print("=" * 90)
