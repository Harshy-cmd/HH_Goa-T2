from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from app.domain import Chunk, Passage


def load_jsonl(path: Path) -> list[Passage]:
    passages: list[Passage] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        required = {"document_id", "passage_id", "text"}
        missing = required - record.keys()
        if missing:
            raise ValueError(f"{path}:{line_number} missing required fields: {sorted(missing)}")
        passages.append(Passage(
            document_id=str(record["document_id"]),
            passage_id=str(record["passage_id"]),
            text=str(record["text"]).strip(),
            title=record.get("title"),
            language=record.get("language"),
            metadata={str(key): str(value) for key, value in record.get("metadata", {}).items()},
        ))
    return passages


def _sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?।॥۔؟])\s+", text) if sentence.strip()]


def _chunk(passage: Passage, text: str, index: int, strategy: str, parent: str | None = None) -> Chunk:
    return Chunk(
        chunk_id=f"{passage.passage_id}:{strategy}:{index}", document_id=passage.document_id,
        passage_id=passage.passage_id, text=text, chunk_index=index, strategy=strategy,
        title=passage.title, language=passage.language, parent_chunk_id=parent,
    )


def fixed_chunks(passages: Iterable[Passage], size_words: int = 384, overlap_words: int = 64) -> list[Chunk]:
    if size_words <= 0 or not 0 <= overlap_words < size_words:
        raise ValueError("size_words must be positive and overlap_words must be smaller than size_words")
    output: list[Chunk] = []
    for passage in passages:
        words = passage.text.split()
        for index, start in enumerate(range(0, max(len(words), 1), size_words - overlap_words)):
            part = " ".join(words[start:start + size_words])
            if part:
                output.append(_chunk(passage, part, index, "fixed"))
            if start + size_words >= len(words):
                break
    return output


def sentence_chunks(passages: Iterable[Passage], target_words: int = 384) -> list[Chunk]:
    if target_words <= 0:
        raise ValueError("target_words must be positive")
    output: list[Chunk] = []
    for passage in passages:
        current: list[str] = []
        current_size = 0
        index = 0
        for sentence in _sentences(passage.text) or [passage.text]:
            sentence_size = len(sentence.split())
            if current and current_size + sentence_size > target_words:
                output.append(_chunk(passage, " ".join(current), index, "sentence"))
                index += 1
                current, current_size = [], 0
            current.append(sentence)
            current_size += sentence_size
        if current:
            output.append(_chunk(passage, " ".join(current), index, "sentence"))
    return output


def hierarchical_chunks(passages: Iterable[Passage], target_words: int = 192) -> list[Chunk]:
    output: list[Chunk] = []
    for passage in passages:
        parent = _chunk(passage, passage.text, 0, "hierarchical-parent")
        parent_id = parent.chunk_id
        output.append(parent)
        for child in sentence_chunks([passage], target_words=target_words):
            output.append(Chunk(**{**child.__dict__, "strategy": "hierarchical-child", "parent_chunk_id": parent_id}))
    return output
