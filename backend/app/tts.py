from __future__ import annotations

import asyncio
import io
import os
import re
import urllib.parse
import urllib.request
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

from app.domain import TextToSpeech


class TextToSpeechError(RuntimeError):
    """Raised when text-to-speech synthesis fails."""
    pass


class EdgeTTS(TextToSpeech):
    """Microsoft Edge Neural Text-to-Speech adapter with robust multi-provider fallback supporting English and Hindi."""

    def __init__(
        self,
        voice_en: str | None = None,
        voice_hi: str | None = None,
    ) -> None:
        self.voice_en = voice_en or os.getenv("TTS_VOICE_EN", "en-US-JennyNeural")
        self.voice_hi = voice_hi or os.getenv("TTS_VOICE_HI", "hi-IN-SwaraNeural")

    def _select_voice(self, language: str | None) -> str:
        if language is None or language.lower() in ("en", "eng", "english"):
            return self.voice_en
        if language.lower() in ("hi", "hin", "hindi"):
            return self.voice_hi
        raise TextToSpeechError(f"Unsupported language '{language}' for speech synthesis. Supported languages: 'en', 'hi'.")

    @staticmethod
    def _clean_text(text: str) -> str:
        # Strip citation brackets such as [chunk-id] or [msmarco-xi:en:1:2:sentence:0]
        cleaned = re.sub(r"\[[a-zA-Z0-9_\-:]+\]", "", text)
        return " ".join(cleaned.split())

    async def _synthesize_edge(self, text: str, voice: str) -> bytes:
        import edge_tts

        communicate = edge_tts.Communicate(text, voice)
        audio_buffer = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.extend(chunk["data"])

        if not audio_buffer:
            raise TextToSpeechError("EdgeTTS produced empty audio stream.")
        return bytes(audio_buffer)

    async def _synthesize_fallback(self, text: str, language: str | None) -> bytes:
        lang = "hi" if language and language.lower() in ("hi", "hin", "hindi") else "en"
        # Google Translate TTS endpoint as reliable fallback
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={lang}&client=tw-ob&q=" + urllib.parse.quote(text[:2000])
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

        def _fetch():
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read()

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _fetch)

    async def synthesize(
        self,
        text: str,
        language: str | None = None,
    ) -> bytes:
        if not text or not text.strip():
            raise TextToSpeechError("Cannot synthesize empty text.")

        voice = self._select_voice(language)
        cleaned_text = self._clean_text(text)
        if not cleaned_text:
            raise TextToSpeechError("Cannot synthesize empty text after removing citations.")

        # Attempt EdgeTTS first; if blocked or handshake fails, use resilient fallback
        try:
            return await self._synthesize_edge(cleaned_text, voice)
        except Exception:
            try:
                return await self._synthesize_fallback(cleaned_text, language)
            except Exception as exc:
                raise TextToSpeechError(f"Speech synthesis request failed: {exc}") from exc


class MockTTS(TextToSpeech):
    """Deterministic mock TTS adapter for testing and offline environments."""

    def __init__(self, mock_bytes: bytes | None = None) -> None:
        self.mock_bytes = mock_bytes or (b"ID3\x04\x00\x00\x00\x00\x00\x00\xff\xfb\x90\x04" + b"MOCK_MP3_AUDIO_DATA_FOR_TESTS")
        self.recorded_calls: list[dict[str, Any]] = []

    async def synthesize(
        self,
        text: str,
        language: str | None = None,
    ) -> bytes:
        if not text or not text.strip():
            raise TextToSpeechError("Cannot synthesize empty text.")

        if language and language.lower() not in ("en", "hi", "eng", "hin", "english", "hindi"):
            raise TextToSpeechError(f"Unsupported language '{language}' for speech synthesis. Supported languages: 'en', 'hi'.")

        self.recorded_calls.append({"text": text, "language": language})
        return self.mock_bytes
