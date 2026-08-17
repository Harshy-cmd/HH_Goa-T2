from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from app.domain import Chunk, SearchHit
from app.generation import GroundedGenerationError, OpenAIGroundedLLM


def test_openai_client_default_no_base_url(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("LLM_BASE_URL", raising=False)

    with patch("openai.OpenAI") as mock_openai_cls:
        llm = OpenAIGroundedLLM()
        _ = llm._client_instance()
        mock_openai_cls.assert_called_once_with(api_key="test-key")


def test_openai_client_env_base_url(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")

    with patch("openai.OpenAI") as mock_openai_cls:
        llm = OpenAIGroundedLLM()
        _ = llm._client_instance()
        mock_openai_cls.assert_called_once_with(
            api_key="test-key",
            base_url="https://api.groq.com/openai/v1",
        )


def test_openai_client_explicit_constructor_base_url(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://env.base.url/v1")

    with patch("openai.OpenAI") as mock_openai_cls:
        llm = OpenAIGroundedLLM(
            api_key="explicit-key",
            base_url="https://openrouter.ai/api/v1",
            model="meta-llama/llama-3-8b-instruct",
        )
        _ = llm._client_instance()
        mock_openai_cls.assert_called_once_with(
            api_key="explicit-key",
            base_url="https://openrouter.ai/api/v1",
        )
        assert llm.model == "meta-llama/llama-3-8b-instruct"


def test_openai_client_missing_api_key_raises(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    llm = OpenAIGroundedLLM(api_key=None)
    with pytest.raises(GroundedGenerationError, match="OPENAI_API_KEY is required"):
        llm._client_instance()
