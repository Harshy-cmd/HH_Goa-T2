from __future__ import annotations

import asyncio
import pytest
from fastapi.testclient import TestClient

from app.domain import GeneratedAnswer
from app.main import app
from app.pipeline import ExtractiveGroundedGenerator, REFUSAL
from app.stt import MockSTT, OpenAIWhisperSTT, SpeechToTextError


class FakeTranscriptionResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeAudioTranscriptions:
    def __init__(self, response_text: str = "What is photosynthesis?", should_fail: bool = False) -> None:
        self.response_text = response_text
        self.should_fail = should_fail
        self.last_kwargs: dict = {}

    def create(self, **kwargs):
        if self.should_fail:
            raise RuntimeError("Fake provider network connection timeout")
        self.last_kwargs = kwargs
        return FakeTranscriptionResponse(self.response_text)


class FakeAudio:
    def __init__(self, response_text: str = "What is photosynthesis?", should_fail: bool = False) -> None:
        self.transcriptions = FakeAudioTranscriptions(response_text, should_fail)


class FakeOpenAIClient:
    def __init__(self, response_text: str = "What is photosynthesis?", should_fail: bool = False) -> None:
        self.audio = FakeAudio(response_text, should_fail)


class RefusingGenerator:
    def answer(self, query, evidence):
        return GeneratedAnswer(REFUSAL, (), refused=True)


# 1. MockSTT returns deterministic transcript
def test_mock_stt_returns_deterministic_transcript():
    mock = MockSTT(transcript="Hello world")
    result = asyncio.run(mock.transcribe(b"fake-audio-bytes"))
    assert result == "Hello world"
    assert len(mock.recorded_calls) == 1
    assert mock.recorded_calls[0]["audio_len"] == len(b"fake-audio-bytes")


# 2. OpenAIWhisperSTT sends the correct model
def test_openai_whisper_stt_sends_correct_model():
    fake_client = FakeOpenAIClient("Transcribed text")
    stt = OpenAIWhisperSTT(model="whisper-large-v3-turbo", api_key="fake-key", client=fake_client)
    res = asyncio.run(stt.transcribe(b"audio-data"))
    assert res == "Transcribed text"
    assert fake_client.audio.transcriptions.last_kwargs["model"] == "whisper-large-v3-turbo"


# 3. Language parameter is forwarded
def test_openai_whisper_stt_forwards_language():
    fake_client = FakeOpenAIClient("प्रकाश संश्लेषण")
    stt = OpenAIWhisperSTT(api_key="fake-key", client=fake_client)
    res = asyncio.run(stt.transcribe(b"audio-data", language="hi"))
    assert res == "प्रकाश संश्लेषण"
    assert fake_client.audio.transcriptions.last_kwargs["language"] == "hi"


# 4. Provider response is converted to string
def test_openai_whisper_stt_converts_response_to_clean_string():
    fake_client = FakeOpenAIClient("  \n  Photosynthesis in plants.  \n ")
    stt = OpenAIWhisperSTT(api_key="fake-key", client=fake_client)
    res = asyncio.run(stt.transcribe(b"audio-data"))
    assert res == "Photosynthesis in plants."


# 5. Empty transcription raises STT error
def test_openai_whisper_stt_empty_transcript_raises_error():
    fake_client = FakeOpenAIClient("   ")
    stt = OpenAIWhisperSTT(api_key="fake-key", client=fake_client)
    with pytest.raises(SpeechToTextError, match="empty transcript"):
        asyncio.run(stt.transcribe(b"audio-data"))


# 6. Provider failure raises STT error
def test_openai_whisper_stt_provider_failure_raises_error():
    fake_client = FakeOpenAIClient(should_fail=True)
    stt = OpenAIWhisperSTT(api_key="fake-key", client=fake_client)
    with pytest.raises(SpeechToTextError, match="STT transcription request failed"):
        asyncio.run(stt.transcribe(b"audio-data"))


# 7. Empty audio is rejected by endpoint
def test_voice_endpoint_rejects_empty_audio():
    client = TestClient(app)
    response = client.post(
        "/v1/voice/query",
        files={"file": ("empty.wav", b"", "audio/wav")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


# 8. Voice endpoint successfully passes transcript into RAG
def test_voice_endpoint_passes_transcript_into_rag(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "stt_adapter", MockSTT("What is photosynthesis?"))
    monkeypatch.setattr(main.pipelines["sentence"]["dense"], "generator", ExtractiveGroundedGenerator())
    client = TestClient(app)
    response = client.post(
        "/v1/voice/query",
        files={"file": ("query.wav", b"fake-audio-payload", "audio/wav")},
        data={"chunking_strategy": "sentence", "retrieval_mode": "dense"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "What is photosynthesis?"
    assert not data["refused"]
    assert len(data["sources"]) > 0
    assert "stt" in data["latency_ms"]
    assert "rag_total" in data["latency_ms"]
    assert "total" in data["latency_ms"]


# 9. Hindi transcript path works
def test_voice_endpoint_hindi_path(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "stt_adapter", MockSTT("प्रकाश संश्लेषण क्या है?"))
    monkeypatch.setattr(main.pipelines["sentence"]["dense"], "generator", ExtractiveGroundedGenerator())
    client = TestClient(app)
    response = client.post(
        "/v1/voice/query",
        files={"file": ("hindi.wav", b"fake-hindi-audio", "audio/wav")},
        data={"language": "hi", "chunking_strategy": "sentence", "retrieval_mode": "dense"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "प्रकाश संश्लेषण क्या है?"
    assert not data["refused"]
    assert "latency_ms" in data
    assert data["latency_ms"]["stt"] >= 0.0


# 10. RAG refusal is preserved through voice endpoint
def test_voice_endpoint_preserves_refusal(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "stt_adapter", MockSTT("What is the recipe for baking traditional panettone with sourdough?"))
    monkeypatch.setattr(main.pipelines["sentence"]["dense"], "generator", RefusingGenerator())
    client = TestClient(app)
    response = client.post(
        "/v1/voice/query",
        files={"file": ("unsupported.wav", b"fake-audio-payload", "audio/wav")},
        data={"chunking_strategy": "sentence", "retrieval_mode": "dense"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["refused"] is True
    assert data["sources"] == []
    assert "reliably" in data["answer"].lower()
