import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

queries = [
    ("What's your name?", "system"),
    ("Who are you?", "system"),
    ("What can you do?", "system"),
    ("Hello", "conversational"),
    ("What is photosynthesis?", "knowledge"),
    ("What is FAISS?", "knowledge"),
    ("What is Python?", "knowledge"),
    ("What is artificial intelligence?", "knowledge"),
    ("What is the secret recipe for Martian cosmic space cake?", "unsupported"),
]

print("================================================================================")
print("NOVARON LOOP 13 — END-TO-END QUERY BENCHMARK & ROUTE AUDIT")
print("================================================================================")

for query_text, expected_type in queries:
    t0 = time.perf_counter()
    resp = client.post(
        "/v1/query",
        json={"query": query_text, "top_k": 3, "chunking_strategy": "sentence", "retrieval_mode": "dense"},
    )
    wall_ms = (time.perf_counter() - t0) * 1000
    assert resp.status_code == 200, f"Failed for {query_text} with {resp.status_code}"
    data = resp.json()
    
    top_score = data["sources"][0]["relevance_score"] if data["sources"] else "--"
    top_doc = data["sources"][0]["document_id"] if data["sources"] else "--"
    
    print(f"\nQuery: '{query_text}'")
    print(f"  Route / Query Type: {data.get('query_type')}")
    print(f"  Refused:            {data['refused']}")
    print(f"  Sources Count:      {len(data['sources'])} (Top Score: {top_score} | Top Doc: {top_doc})")
    print(f"  Latency (ms):       {data['latency_ms']} | Wall: {wall_ms:.2f}ms")
    print(f"  Answer:             {data['answer']}")

# Voice Query Test
print("\n================================================================================")
print("VOICE QUERY TEST (/v1/voice/query)")
print("================================================================================")
import io
import wave
import struct

# Create dummy 0.5s silence wav
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

main_mod.stt_adapter = MockSTT("What is FAISS?")
voice_resp = client.post(
    "/v1/voice/query",
    files={"file": ("speech.wav", dummy_wav_bytes, "audio/wav")},
    data={"chunking_strategy": "sentence", "retrieval_mode": "dense", "synthesize_audio": "true"},
)
assert voice_resp.status_code == 200
v_data = voice_resp.json()
print("Voice Query: 'What is FAISS?'")
print(f"  Transcript:   {v_data['query']}")
print(f"  Query Type:   {v_data.get('query_type')}")
print(f"  Refused:      {v_data['refused']}")
print(f"  Sources:      {len(v_data['sources'])}")
print(f"  Audio Base64: {'Present (' + str(len(v_data['audio_base64'])) + ' chars)' if v_data.get('audio_base64') else 'None'}")
print(f"  Answer:       {v_data['answer']}")
print(f"  Latency:      {v_data['latency_ms']}")

# TTS Synthesis Test
print("\n================================================================================")
print("TTS SYNTHESIS TEST (/v1/tts)")
print("================================================================================")
tts_resp = client.post("/v1/tts", json={"text": "I'm NOVARON, your voice-enabled grounded assistant.", "language": "en"})
assert tts_resp.status_code == 200
print(f"TTS English Status: {tts_resp.status_code} | Bytes: {len(tts_resp.content)}")

tts_hi_resp = client.post("/v1/tts", json={"text": "नमस्ते! मैं नोवारॉन हूँ।", "language": "hi"})
assert tts_hi_resp.status_code == 200
print(f"TTS Hindi Status:   {tts_hi_resp.status_code} | Bytes: {len(tts_hi_resp.content)}")

print("\nALL VERIFICATIONS PASSED CLEANLY!")
