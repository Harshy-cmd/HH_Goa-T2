"""Unit tests for NOVARON Query Normalization and Spoken Query Understanding."""
from __future__ import annotations

import time
from app.query_normalizer import (
    clean_excessive_punctuation,
    clean_repeated_words,
    extract_topic_from_query,
    generate_suggested_questions,
    normalize_spoken_query,
)
from app.router import QueryIntent, classify_query


def test_basic_query_normalization():
    res = normalize_spoken_query("what is python")
    assert res.normalized_query == "What is python"


def test_contractions_expansion():
    res = normalize_spoken_query("what's python")
    assert res.normalized_query == "What is python"

    res_who = normalize_spoken_query("who's python's creator")
    assert "who is" in res_who.normalized_query.lower()


def test_conversational_preamble_normalization():
    res1 = normalize_spoken_query("can you explain python")
    assert res1.normalized_query == "What is python"

    res2 = normalize_spoken_query("tell me about python")
    assert res2.normalized_query == "What is python"

    res3 = normalize_spoken_query("what do you know about python")
    assert res3.normalized_query == "What is python"


def test_spoken_filler_word_removal():
    res1 = normalize_spoken_query("uh what is python")
    assert res1.normalized_query == "What is python"

    res2 = normalize_spoken_query("so basically what is python")
    assert res2.normalized_query == "What is python"

    res3 = normalize_spoken_query("um actually what is machine learning please")
    assert res3.normalized_query == "What is machine learning"


def test_stutter_word_deduplication():
    res = normalize_spoken_query("what what is python")
    assert res.normalized_query == "What is python"

    res2 = normalize_spoken_query("python python is great")
    assert res2.normalized_query == "Python is great"


def test_hindi_query_normalization():
    res1 = normalize_spoken_query("पायथन के बारे में बताओ")
    assert res1.normalized_query == "पायथन क्या है"

    res2 = normalize_spoken_query("अरे प्रकाश संश्लेषण क्या है?")
    assert res2.normalized_query == "प्रकाश संश्लेषण क्या है?"


def test_unsupported_query_preservation():
    raw = "What is the secret recipe for Martian cosmic space cake?"
    res = normalize_spoken_query(raw)
    assert "Martian cosmic space cake" in res.normalized_query
    route = classify_query(res.normalized_query)
    assert route.intent == QueryIntent.KNOWLEDGE  # routed into RAG where refusal check triggers


def test_identity_and_conversational_query_routing():
    res_id = normalize_spoken_query("Who are you?")
    route_id = classify_query(res_id.normalized_query)
    assert route_id.intent == QueryIntent.SYSTEM
    assert "NOVARON" in (route_id.direct_answer or "")

    res_conv = normalize_spoken_query("Hello NOVARON, how are you?")
    route_conv = classify_query(res_conv.normalized_query)
    assert route_conv.intent == QueryIntent.CONVERSATIONAL


def test_bounded_followup_anaphora_resolution():
    res1 = normalize_spoken_query("what about its advantages?", previous_topic="Python")
    assert res1.normalized_query == "Advantages of Python"
    assert res1.was_anaphora_resolved is True

    res2 = normalize_spoken_query("who created it?", previous_topic="Python")
    assert res2.normalized_query == "Who created Python?"
    assert res2.was_anaphora_resolved is True

    res3 = normalize_spoken_query("इसके फायदे क्या हैं?", previous_topic="पायथन")
    assert "पायथन" in res3.normalized_query
    assert res3.was_anaphora_resolved is True


def test_suggested_questions_generation():
    suggestions_en = generate_suggested_questions("What is Python?", ["Python Programming Language"], language="en")
    assert len(suggestions_en) == 3
    assert all(isinstance(s, str) and len(s) > 5 for s in suggestions_en)

    suggestions_hi = generate_suggested_questions("प्रकाश संश्लेषण क्या है?", [], language="hi")
    assert len(suggestions_hi) == 3


def test_normalizer_latency_is_under_5ms():
    queries = [
        "what is python",
        "what's python",
        "tell me about python",
        "can you explain python",
        "uh what is python",
        "what what is python",
        "What is Python???",
        "पायथन के बारे में बताओ",
        "what about its advantages?",
    ]
    t0 = time.perf_counter()
    for q in queries:
        normalize_spoken_query(q, previous_topic="Python")
    dur_ms = (time.perf_counter() - t0) * 1000
    avg_ms = dur_ms / len(queries)
    assert avg_ms < 1.0  # Well under 5ms, typically < 0.1ms
