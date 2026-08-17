from __future__ import annotations

import json
import math

from app.embeddings import SentenceTransformerEmbeddingProvider


def main() -> None:
    provider = SentenceTransformerEmbeddingProvider()
    samples = {
        "en": "What is photosynthesis?",
        "hi": "प्रकाश संश्लेषण क्या है?",
        "kn": "ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ ಎಂದರೇನು?",
    }
    vectors = {language: provider.embed_query(text) for language, text in samples.items()}
    dimensions = {len(vector) for vector in vectors.values()}
    norms = {language: math.sqrt(sum(value * value for value in vector)) for language, vector in vectors.items()}
    if len(dimensions) != 1 or not all(math.isfinite(value) for vector in vectors.values() for value in vector):
        raise RuntimeError("Embedding smoke test failed: inconsistent dimension or non-finite vector.")
    if not all(math.isclose(norm, 1.0, abs_tol=1e-4) for norm in norms.values()):
        raise RuntimeError(f"Embedding smoke test failed: expected unit-normalized vectors, got {norms}.")
    print(json.dumps({"model": provider.model_name, "dimension": dimensions.pop(), "norms": norms,
                      "e5_prefixes": provider.e5_prefixes}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
