from __future__ import annotations

import os
import re
import unicodedata
import math
from typing import Sequence

from app.domain import EmbeddingProvider


class EmbeddingProviderError(RuntimeError):
    """Raised when an embedding provider cannot produce a valid vector."""


def normalize_embedding_text(text: str) -> str:
    """Stable Unicode and whitespace normalization shared by indexing and querying."""
    normalized = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", normalized).strip()


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """Lazy multilingual sentence-transformers adapter with normalized vectors."""

    def __init__(self, model_name: str | None = None, device: str | None = None) -> None:
        self.model_name = model_name or os.getenv(
            "EMBEDDING_MODEL", "intfloat/multilingual-e5-small"
        )
        self.device = device or os.getenv("EMBEDDING_DEVICE")
        self.e5_prefixes = self._e5_prefixes_enabled()
        self._model = None

    def _e5_prefixes_enabled(self) -> bool:
        setting = os.getenv("EMBEDDING_E5_PREFIXES", "auto").lower()
        if setting in {"1", "true", "yes"}:
            return True
        if setting in {"0", "false", "no"}:
            return False
        return "e5" in self.model_name.casefold()

    def _load_model(self):
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise EmbeddingProviderError(
                "sentence-transformers is required for EMBEDDING_PROVIDER=sentence_transformers; "
                "install backend/requirements.txt production extras."
            ) from exc
        try:
            self._model = SentenceTransformer(self.model_name, device=self.device)
        except Exception as exc:  # model download, local cache, device, or provider failures
            raise EmbeddingProviderError(f"Unable to load embedding model '{self.model_name}': {exc}") from exc
        return self._model

    def _encode(self, texts: Sequence[str], batch_size: int | None, prefix: str) -> list[list[float]]:
        if not texts:
            return []
        model = self._load_model()
        prepared = [normalize_embedding_text(text) for text in texts]
        if not all(prepared):
            raise EmbeddingProviderError("Cannot embed empty text after normalization.")
        if prefix:
            prepared = [prefix + text for text in prepared]
        try:
            vectors = model.encode(
                prepared,
                batch_size=batch_size or int(os.getenv("EMBEDDING_BATCH_SIZE", "32")),
                normalize_embeddings=True,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
        except Exception as exc:
            raise EmbeddingProviderError(f"Embedding request failed: {exc}") from exc
        result = [vector.astype(float).tolist() for vector in vectors]
        if not all(math.isfinite(value) for vector in result for value in vector):
            raise EmbeddingProviderError("Embedding provider returned non-finite values.")
        return result

    def embed_documents(self, texts: Sequence[str], batch_size: int | None = None) -> list[list[float]]:
        return self._encode(texts, batch_size, "passage: " if self.e5_prefixes else "")

    def embed_many(self, texts: Sequence[str], batch_size: int | None = None) -> list[list[float]]:
        """Compatibility method: index-oriented batch embedding."""
        return self.embed_documents(texts, batch_size)

    def embed_query(self, text: str) -> list[float]:
        return self._encode([text], 1, "query: " if self.e5_prefixes else "")[0]

    def embed(self, text: str) -> list[float]:
        """Compatibility method: query-oriented embedding."""
        return self.embed_query(text)

    @property
    def embedding_dimension(self) -> int:
        try:
            return int(self._load_model().get_sentence_embedding_dimension())
        except Exception as exc:
            raise EmbeddingProviderError(f"Unable to determine embedding dimension: {exc}") from exc
