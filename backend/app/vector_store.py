from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import numpy as np

from app.domain import Chunk


class VectorStoreError(RuntimeError):
    pass


class FaissVectorStore:
    """Persistent cosine-style FAISS store. Vectors must be unit normalized."""
    INDEX_FILE = "index.faiss"
    METADATA_FILE = "chunks.json"
    MANIFEST_FILE = "manifest.json"

    def __init__(self, index, chunks: Sequence[Chunk], dimensions: int, manifest: dict | None = None) -> None:
        self.index = index
        self.chunks = list(chunks)
        self.dimensions = dimensions
        self.manifest = manifest or {}
        self._validate_alignment()

    @staticmethod
    def _faiss():
        try:
            import faiss
            return faiss
        except ImportError as exc:
            raise VectorStoreError("faiss-cpu is required for FAISS retrieval. Install production dependencies.") from exc

    @staticmethod
    def _normalized(vectors: Sequence[Sequence[float]]) -> np.ndarray:
        matrix = np.asarray(vectors, dtype="float32")
        if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0:
            raise VectorStoreError("Embeddings must be a non-empty two-dimensional matrix.")
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise VectorStoreError("Embeddings cannot contain zero vectors.")
        return matrix / norms

    @classmethod
    def build(cls, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]) -> "FaissVectorStore":
        if len(chunks) != len(embeddings):
            raise VectorStoreError("Chunk metadata and embeddings must have equal lengths.")
        matrix = cls._normalized(embeddings)
        faiss = cls._faiss()
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        return cls(index, chunks, matrix.shape[1])

    def _validate_alignment(self) -> None:
        if self.index.ntotal != len(self.chunks):
            raise VectorStoreError(
                f"Index/metadata mismatch: index has {self.index.ntotal} vectors, metadata has {len(self.chunks)} chunks."
            )
        if self.index.d != self.dimensions:
            raise VectorStoreError("Index dimension does not match recorded metadata dimension.")

    def save(self, directory: Path, manifest_extra: dict | None = None) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        faiss = self._faiss()
        faiss.write_index(self.index, str(directory / self.INDEX_FILE))
        (directory / self.METADATA_FILE).write_text(
            json.dumps([asdict(chunk) for chunk in self.chunks], ensure_ascii=False), encoding="utf-8"
        )
        manifest = {**self.manifest, **(manifest_extra or {}), "dimensions": self.dimensions,
                    "vector_count": self.index.ntotal, "created_at": datetime.now(timezone.utc).isoformat()}
        (directory / self.MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        self.manifest = manifest

    @classmethod
    def load(cls, directory: Path, *, expected_model: str | None = None,
             expected_strategy: str | None = None, expected_normalized: bool | None = None) -> "FaissVectorStore":
        required = [directory / cls.INDEX_FILE, directory / cls.METADATA_FILE, directory / cls.MANIFEST_FILE]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise VectorStoreError("Missing FAISS index artifacts: " + ", ".join(missing))
        faiss = cls._faiss()
        try:
            index = faiss.read_index(str(directory / cls.INDEX_FILE))
            raw_chunks = json.loads((directory / cls.METADATA_FILE).read_text(encoding="utf-8"))
            manifest = json.loads((directory / cls.MANIFEST_FILE).read_text(encoding="utf-8"))
            store = cls(index, [Chunk(**raw) for raw in raw_chunks], int(manifest["dimensions"]), manifest)
            store.validate_manifest(expected_model, expected_strategy, expected_normalized)
            return store
        except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
            raise VectorStoreError(f"Unable to load FAISS index from {directory}: {exc}") from exc

    def validate_manifest(self, expected_model: str | None, expected_strategy: str | None,
                          expected_normalized: bool | None) -> None:
        expected = {"embedding_model": expected_model, "chunking_strategy": expected_strategy,
                    "normalized": expected_normalized}
        for field, value in expected.items():
            if value is None:
                continue
            if field not in self.manifest:
                raise VectorStoreError(f"Index manifest is missing required compatibility field '{field}'. Rebuild the index.")
            if self.manifest[field] != value:
                raise VectorStoreError(
                    f"Index manifest mismatch for '{field}': expected {value!r}, found {self.manifest[field]!r}. Rebuild the index."
                )

    @classmethod
    def exists(cls, directory: Path) -> bool:
        return all((directory / name).is_file() for name in (cls.INDEX_FILE, cls.METADATA_FILE, cls.MANIFEST_FILE))

    def search(self, vector: Sequence[float], limit: int) -> list[tuple[Chunk, float]]:
        if limit <= 0 or not self.chunks:
            return []
        matrix = self._normalized([vector])
        if matrix.shape[1] != self.dimensions:
            raise VectorStoreError(
                f"Embedding dimension {matrix.shape[1]} does not match index dimension {self.dimensions}."
            )
        scores, positions = self.index.search(matrix, min(limit, len(self.chunks)))
        return [(self.chunks[int(position)], float(score)) for score, position in zip(scores[0], positions[0]) if position >= 0]
