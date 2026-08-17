from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    _project_root = Path(__file__).resolve().parents[2]
    _root_env = _project_root / ".env"
    _backend_env = Path(__file__).resolve().parents[1] / ".env"
    if _root_env.exists():
        load_dotenv(_root_env)
    elif _backend_env.exists():
        load_dotenv(_backend_env)
except ImportError:
    pass

from app.domain import SpeechToText


class SpeechToTextError(RuntimeError):
    """Raised when audio transcription fails."""
    pass


class OpenAIWhisperSTT(SpeechToText):
    """OpenAI-compatible speech-to-text adapter supporting Groq and standard OpenAI Whisper endpoints."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.model = model or os.getenv("STT_MODEL", "whisper-large-v3-turbo")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self._client = client

    def _client_instance(self):
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise SpeechToTextError("OPENAI_API_KEY is required for OpenAI/Groq STT transcription.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise SpeechToTextError("openai package is required for OpenAIWhisperSTT.") from exc
        kwargs: dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        self._client = OpenAI(**kwargs)
        return self._client

    async def transcribe(
        self,
        audio: bytes,
        language: str | None = None,
        filename: str = "audio.wav",
    ) -> str:
        if not audio or len(audio) == 0:
            raise SpeechToTextError("Audio payload cannot be empty.")

        file_tuple = (filename, io.BytesIO(audio), "audio/wav")
        kwargs: dict[str, Any] = {
            "model": self.model,
            "file": file_tuple,
        }
        if language:
            kwargs["language"] = language

        try:
            client = self._client_instance()
            response = client.audio.transcriptions.create(**kwargs)
            # Response may be a pydantic model with `.text` or a dict
            transcript = getattr(response, "text", None) or (response.get("text") if isinstance(response, dict) else str(response))
            cleaned = str(transcript).strip()
            if not cleaned:
                raise SpeechToTextError("Transcribed audio yielded an empty transcript.")
            return cleaned
        except SpeechToTextError:
            raise
        except Exception as exc:
            raise SpeechToTextError(f"STT transcription request failed: {exc}") from exc


class MockSTT(SpeechToText):
    """Deterministic mock STT adapter for testing and offline environments."""

    def __init__(self, transcript: str = "What is photosynthesis?") -> None:
        self.transcript = transcript
        self.recorded_calls: list[dict[str, Any]] = []

    async def transcribe(
        self,
        audio: bytes,
        language: str | None = None,
        filename: str = "audio.wav",
    ) -> str:
        if not audio or len(audio) == 0:
            raise SpeechToTextError("Audio payload cannot be empty.")
        self.recorded_calls.append({
            "audio_len": len(audio),
            "language": language,
            "filename": filename,
        })
        return self.transcript
