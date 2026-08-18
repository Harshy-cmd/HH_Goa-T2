"""Comprehensive Test Suite for NOVARON Multilingual Language Router (Loop 14C-5).
Validates:
1. Accurate script and language detection across all 15 languages (14 Indic + English).
2. Intent classification and confidence scoring.
3. Conversational shortcuts (greetings and courtesies) bypassing retrieval.
4. System identity shortcuts across Indic languages bypassing retrieval.
5. Strict false-positive isolation between related scripts.
6. Sub-millisecond execution performance (<5 ms).
"""
from __future__ import annotations

import time
import pytest

from app.router import (
    QueryIntent,
    RouteResult,
    classify_query,
    detect_language,
    detect_language_with_confidence,
)


# 1. Native-script knowledge queries across all 15 languages
@pytest.mark.parametrize(
    "query,expected_lang",
    [
        ("What is artificial intelligence and machine learning?", "en"),
        ("সালোক সংশ্লেষণ কিদৰে হয়?", "as"),
        ("সালোকসংশ্লেষণ কী এবং কিভাবে হয়?", "bn"),
        ("કૃત્રિમ બુદ્ધિ શું છે?", "gu"),
        ("कृत्रिम बुद्धिमत्ता क्या है और यह कैसे काम करती है?", "hi"),
        ("ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಎಂದರೇನು?", "kn"),
        ("പ്രകാശസംശ്ലേഷണം എന്താണ്?", "ml"),
        ("प्रकाशसंश्लेषण म्हणजे काय आणि ते कसे होते?", "mr"),
        ("प्रकाश संश्लेषण भनेको के हो?", "ne"),
        ("ଆଲୋକ ସଂଶ୍ଳେଷଣ କଣ?", "or"),
        ("ਪ੍ਰਕਾਸ਼ ਸੰਸਲੇਸ਼ਣ ਕੀ ਹੈ?", "pa"),
        ("प्रकाशसंश्लेषणं किम् अस्ति?", "sa"),
        ("செயற்கை நுண்ணறிவு என்றால் என்ன?", "ta"),
        ("కృత్రిమ మేధస్సు అంటే ఏమిటి?", "te"),
        ("مصنوعی ذہانت کیا ہے؟", "ur"),
    ],
)
def test_multilingual_language_detection(query: str, expected_lang: str):
    lang, conf = detect_language_with_confidence(query)
    assert lang == expected_lang, f"Query '{query}' expected '{expected_lang}', got '{lang}'"
    assert conf >= 0.85, f"Confidence too low: {conf}"

    route = classify_query(query)
    assert route.language == expected_lang
    assert route.intent == QueryIntent.KNOWLEDGE
    assert route.direct_answer is None
    assert route.confidence >= 0.85


# 2. Conversational shortcuts across multiple languages
def test_conversational_shortcuts():
    greetings = [
        ("Hello", "en"),
        ("Hi there", "en"),
        ("Good morning", "en"),
        ("नमस्ते", "hi"),
        ("प्रणाम", "hi"),
        ("வணக்கம்", "ta"),
        ("నమస్కారం", "te"),
        ("ನಮಸ್ಕಾರ", "kn"),
        ("നമസ്കാരം", "ml"),
        ("নমস্কার", "bn"),
        ("নমস্কাৰ", "as"),
        ("નમસ્તે", "gu"),
        ("नमस्कार", "mr"),
        ("ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ", "pa"),
        ("ନମସ୍କାର", "or"),
        ("سلام", "ur"),
        ("नमो नमः", "sa"),
    ]

    for g_text, exp_lang in greetings:
        route = classify_query(g_text)
        assert route.intent == QueryIntent.CONVERSATIONAL, f"Failed for '{g_text}'"
        assert route.direct_answer is not None, f"No direct answer for '{g_text}'"
        assert len(route.direct_answer) > 5


# 3. Identity and capabilities shortcuts across languages
def test_identity_and_capabilities_shortcuts():
    identity_queries = [
        ("What is your name?", "en"),
        ("Who are you?", "en"),
        ("Who created you?", "en"),
        ("आपका नाम क्या है?", "hi"),
        ("आप कौन हैं?", "hi"),
        ("உங்கள் பெயர் என்ன?", "ta"),
        ("మీ పేరు ఏమిటి?", "te"),
        ("ನಿಮ್ಮ ಹೆಸರೇನು?", "kn"),
        ("നിങ്ങളുടെ പേരെന്താണ്?", "ml"),
        ("আপনার নাম কি?", "bn"),
        ("আপোনাৰ নাম কি?", "as"),
        ("તમારું નામ શું છે?", "gu"),
        ("तुमचे नाव काय आहे?", "mr"),
        ("ਤੁਹਾਡਾ ਨਾਮ ਕੀ ਹੈ?", "pa"),
        ("ଆପଣଙ୍କ ନାମ କଣ?", "or"),
        ("آپ کا نام کیا ہے؟", "ur"),
        ("भवतः नाम किम्?", "sa"),
    ]

    for query, exp_lang in identity_queries:
        route = classify_query(query)
        assert route.intent == QueryIntent.SYSTEM, f"Query '{query}' was not routed to SYSTEM"
        assert route.direct_answer is not None
        assert "NOVARON" in route.direct_answer or "नोवारॉन" in route.direct_answer or "நோவாரோன்" in route.direct_answer or "నోవారన్" in route.direct_answer or "ನೊವಾರಾನ್" in route.direct_answer or "নোভারন" in route.direct_answer or "નોવારોન" in route.direct_answer or "নোৱাৰন" in route.direct_answer or "नोभारोन" in route.direct_answer or "نووارون" in route.direct_answer


# 4. False-positive isolation tests
def test_false_positive_script_isolation():
    # English vs Indic
    assert detect_language("What is Python?") == "en"
    assert detect_language("This is a long English text about computer science.") == "en"

    # Hindi vs Marathi vs Nepali vs Sanskrit
    assert detect_language("यह क्या है और कैसे काम करता है?") == "hi"
    assert detect_language("हे काय आहे आणि कसे चालते?") == "mr"
    assert detect_language("यो के हो र कसरी काम गर्छ?") == "ne"
    assert detect_language("इदं किम् अस्ति?") == "sa"

    # Bengali vs Assamese
    assert detect_language("এই বিষয়টির ব্যাখ্যা কী?") == "bn"
    assert detect_language("এই বিষয়টোৰ ব্যাখ্যা কিদৰে হয়?") == "as"
    assert detect_language("অসমৰ ৰাজধানী কি?") == "as"

    # Kannada vs Telugu
    assert detect_language("ಕನ್ನಡ ಭಾಷೆ") == "kn"
    assert detect_language("తెలుగు భాష") == "te"

    # Tamil vs Malayalam
    assert detect_language("தமிழ் மொழி") == "ta"
    assert detect_language("മലയാള ഭാഷ") == "ml"

    # Gujarati vs Punjabi vs Odia vs Urdu
    assert detect_language("ગુજરાતી ભાષા") == "gu"
    assert detect_language("ਪੰਜਾਬੀ ਭਾਸ਼ਾ") == "pa"
    assert detect_language("ଓଡ଼ିଆ ଭାଷା") == "or"
    assert detect_language("اردو زبان") == "ur"


# 5. Performance benchmark test (< 5ms per route)
def test_router_performance():
    queries = [
        "What is photosynthesis in biology?",
        "प्रकाश संश्लेषण क्या है?",
        "செயற்கை நுண்ணறிவு என்றால் என்ன?",
        "ਕ੍ਰਿਤਰਿਮ ਬੁੱਧੀ ਕੀ ਹੈ?",
        "Hello NOVARON",
        "Who are you?",
    ]

    t0 = time.perf_counter()
    iterations = 500
    for _ in range(iterations):
        for q in queries:
            classify_query(q)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    avg_per_query_ms = elapsed_ms / (iterations * len(queries))

    assert avg_per_query_ms < 5.0, f"Router too slow: {avg_per_query_ms:.4f} ms per query"
