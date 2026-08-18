"""Corpus Builder Aggregator Package for NOVARON.
"""
from __future__ import annotations

from .novaron_system import get_novaron_documents
from .computer_science import get_computer_science_documents
from .ai_ml import get_ai_ml_documents
from .general_science import get_general_science_documents
from .mathematics import get_mathematics_documents
from .general_knowledge import get_general_knowledge_documents
from .hindi_knowledge import get_hindi_documents

def get_all_curated_documents() -> list[dict]:
    docs = []
    docs.extend(get_novaron_documents())
    docs.extend(get_computer_science_documents())
    docs.extend(get_ai_ml_documents())
    docs.extend(get_general_science_documents())
    docs.extend(get_mathematics_documents())
    docs.extend(get_general_knowledge_documents())
    docs.extend(get_hindi_documents())
    return docs
