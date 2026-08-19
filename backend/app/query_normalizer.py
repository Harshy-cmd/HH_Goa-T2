"""
NOVARON Local Deterministic Query Normalizer and Understanding Layer.
Provides:
1. Speech artifact & filler word removal (English, Hindi, Indic).
2. Stutter & duplicate word deduplication.
3. Conversational preamble normalization (e.g. "tell me about X" -> "what is X").
4. Bounded single-turn conversational anaphora resolution (e.g. "who created it?" -> "who created Python?").
5. Local, deterministic suggested follow-up questions based on corpus titles and topics.
Zero cloud API calls, sub-millisecond execution (< 0.5 ms).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

# Filler words at speech boundaries
_LEADING_FILLERS_EN = [
    r"^(?:uh+|um+|ah+|er+|like|so\s+basically|basically|actually|you\s+know|well|hey\s+novaron|ok\s+novaron|novaron|please|can\s+you\s+please|could\s+you\s+please)\s+",
]

_LEADING_FILLERS_HI = [
    r"^(?:अरे|अच्छा|सुनो|कृपया|नोवारॉन|हे\s*नोवारॉन)\s+",
]

_TRAILING_FILLERS_EN = [
    r"\s+(?:please|if\s+you\s+can|thank\s+you|thanks|you\s+know)$",
]

_TRAILING_FILLERS_HI = [
    r"\s+(?:कृपया|धन्यवाद|बताओ|बताइए)$",
]

# Common conversational contractions
_CONTRACTIONS = [
    (re.compile(r"\bwhat's\b", flags=re.IGNORECASE), "what is"),
    (re.compile(r"\bwho's\b", flags=re.IGNORECASE), "who is"),
    (re.compile(r"\bhow's\b", flags=re.IGNORECASE), "how is"),
    (re.compile(r"\bwhere's\b", flags=re.IGNORECASE), "where is"),
    (re.compile(r"\bit's\b", flags=re.IGNORECASE), "it is"),
    (re.compile(r"\bthere's\b", flags=re.IGNORECASE), "there is"),
    (re.compile(r"\bcan't\b", flags=re.IGNORECASE), "cannot"),
    (re.compile(r"\bdon't\b", flags=re.IGNORECASE), "do not"),
]

# Preamble normalization: "tell me about X", "can you explain X" -> "what is X" or X
_PREAMBLE_PATTERNS = [
    # English
    (re.compile(r"^(?:can\s+you\s+)?(?:please\s+)?(?:explain|describe|clarify)\s+(?:in\s+detail\s+)?(.+)$", flags=re.IGNORECASE), r"what is \1"),
    (re.compile(r"^(?:tell\s+me\s+about|what\s+do\s+you\s+know\s+about|give\s+me\s+information\s+on)\s+(.+)$", flags=re.IGNORECASE), r"what is \1"),
    (re.compile(r"^(?:i\s+want\s+to\s+learn\s+about|teach\s+me\s+about)\s+(.+)$", flags=re.IGNORECASE), r"what is \1"),
    # Hindi
    (re.compile(r"^(.+?)\s*(?:के\s*बारे\s*में\s*(?:बताओ|बताइए|जानकारी\s*दो|समझाओ))$", flags=re.IGNORECASE), r"\1 क्या है"),
    (re.compile(r"^(?:क्या\s*आप\s*(?:मुझे\s*)?)?(.+?)\s*(?:के\s*बारे\s*में\s*(?:बता\s*सकते\s*हैं|समझा\s*सकते\s*हैं))$", flags=re.IGNORECASE), r"\1 क्या है"),
]

# Anaphora replacement patterns
_ANAPHORA_PATTERNS_EN = [
    (re.compile(r"^(?:what\s+about\s+)?(?:its|their)\s+(advantages|disadvantages|features|applications|uses|benefits|architecture|history|syntax|types)\??$", flags=re.IGNORECASE), r"\1 of {topic}"),
    (re.compile(r"^(?:who\s+(?:created|made|invented|designed|developed))\s+it\??$", flags=re.IGNORECASE), r"who created {topic}?"),
    (re.compile(r"^(?:when\s+was\s+it\s+(?:created|made|invented|released|introduced|published))\??$", flags=re.IGNORECASE), r"when was {topic} released?"),
    (re.compile(r"^(?:how\s+does\s+it\s+work)\??$", flags=re.IGNORECASE), r"how does {topic} work?"),
    (re.compile(r"^(?:why\s+is\s+it\s+used)\??$", flags=re.IGNORECASE), r"why is {topic} used?"),
]

_ANAPHORA_PATTERNS_HI = [
    (re.compile(r"^(?:इसके|इसके\s*प्रमुख)\s*(फायदे|नुकसान|उपयोग|कार्य|लाभ|प्रकार)\s*(?:क्या\s*हैं|क्या\s*है)\??$", flags=re.IGNORECASE), r"{topic} के \1 क्या हैं?"),
    (re.compile(r"^(?:इसे\s*किसने\s*(?:बनाया|विकसित\s*किया))\??$", flags=re.IGNORECASE), r"{topic} को किसने बनाया?"),
    (re.compile(r"^(?:यह\s*कैसे\s*काम\s*करता\s*है)\??$", flags=re.IGNORECASE), r"{topic} कैसे काम करता है?"),
    (re.compile(r"^(?:यह\s*कब\s*(?:बनाया|आया|शुरू\s*हुआ))\??$", flags=re.IGNORECASE), r"{topic} कब शुरू हुआ?"),
]


@dataclass(frozen=True)
class NormalizedQuery:
    raw_query: str
    normalized_query: str
    cleaned_text: str
    resolved_topic: str | None = None
    was_anaphora_resolved: bool = False


def clean_repeated_words(text: str) -> str:
    """Removes accidental stutter / adjacent duplicate words (e.g. 'what what is' -> 'what is')."""
    words = text.split()
    if len(words) <= 1:
        return text
    deduped = [words[0]]
    for w in words[1:]:
        if w.lower() != deduped[-1].lower():
            deduped.append(w)
    return " ".join(deduped)


def clean_excessive_punctuation(text: str) -> str:
    """Normalizes repeated question marks, exclamation points, and spaces."""
    t = re.sub(r"\?+", "?", text)
    t = re.sub(r"!+", "!", t)
    t = re.sub(r"\.+", ".", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def normalize_spoken_query(
    query: str,
    previous_topic: str | None = None,
) -> NormalizedQuery:
    """
    Deterministically cleans speech artifacts, expands contractions, removes filler,
    normalizes preambles, and optionally resolves single-turn follow-up anaphora.
    """
    raw = query.strip()
    if not raw:
        return NormalizedQuery(raw_query="", normalized_query="", cleaned_text="")

    t = clean_excessive_punctuation(raw)

    # 1. Expand standard contractions
    for pat, repl in _CONTRACTIONS:
        t = pat.sub(repl, t)

    # 2. Strip repeated stutter words
    t = clean_repeated_words(t)

    # 3. Normalize conversational preambles ("tell me about X" -> "what is X", "X के बारे में बताओ" -> "X क्या है")
    for pat, repl in _PREAMBLE_PATTERNS:
        if pat.search(t):
            t = pat.sub(repl, t)
            break

    # 4. Strip leading/trailing spoken fillers (supports stacked fillers like 'um actually ... please')
    for _ in range(4):
        changed = False
        for pattern in _LEADING_FILLERS_EN + _LEADING_FILLERS_HI:
            new_t = re.sub(pattern, "", t, flags=re.IGNORECASE).strip()
            if new_t != t:
                t = new_t
                changed = True
        for pattern in _TRAILING_FILLERS_EN + _TRAILING_FILLERS_HI:
            new_t = re.sub(pattern, "", t, flags=re.IGNORECASE).strip()
            if new_t != t:
                t = new_t
                changed = True
        if not changed:
            break

    # Clean punctuation again if filler removal left dangling symbols
    t = clean_excessive_punctuation(t)

    # 5. Handle follow-up anaphora if previous topic is provided
    was_resolved = False
    resolved_topic = None
    if previous_topic and previous_topic.strip():
        clean_prev = previous_topic.strip()
        for pat, repl in _ANAPHORA_PATTERNS_EN:
            if pat.search(t):
                t = pat.sub(repl.format(topic=clean_prev), t)
                was_resolved = True
                resolved_topic = clean_prev
                break
        if not was_resolved:
            for pat, repl in _ANAPHORA_PATTERNS_HI:
                if pat.search(t):
                    t = pat.sub(repl.format(topic=clean_prev), t)
                    was_resolved = True
                    resolved_topic = clean_prev
                    break

    t = clean_excessive_punctuation(t)
    # Ensure standard casing if it starts lowercase
    if t and t[0].islower():
        t = t[0].upper() + t[1:]

    return NormalizedQuery(
        raw_query=raw,
        normalized_query=t if t else raw,
        cleaned_text=t.lower() if t else raw.lower(),
        resolved_topic=resolved_topic,
        was_anaphora_resolved=was_resolved,
    )


def extract_topic_from_query(query: str) -> str | None:
    """Heuristically extracts the core topic entity from a factual query for follow-up context."""
    q = query.strip()
    # Match "what is X", "what are X", "explain X"
    m = re.search(r"^(?:what\s+(?:is|are)\s+|who\s+(?:is|was)\s+|explain\s+|describe\s+)(.+?)(?:\?|\.|$)", q, flags=re.IGNORECASE)
    if m:
        candidate = m.group(1).strip()
        # Remove trailing words like "in python", "algorithm", etc. if too broad
        if candidate and len(candidate.split()) <= 4:
            return candidate

    # Hindi match: "X क्या है", "X क्या होता है"
    m_hi = re.search(r"^(.+?)\s*(?:क्या\s*है|क्या\s*होता\s*है|किसे\s*कहते\s*हैं)(?:\?|।|$)", q, flags=re.IGNORECASE)
    if m_hi:
        candidate_hi = m_hi.group(1).strip()
        if candidate_hi and len(candidate_hi.split()) <= 4:
            return candidate_hi

    return None


def generate_suggested_questions(
    query: str,
    source_titles: Sequence[str | None] = (),
    language: str = "en",
) -> list[str]:
    """
    Deterministically produces 3 relevant follow-up questions derived from
    retrieved source titles and the current query topic without any cloud LLM calls.
    """
    topic = extract_topic_from_query(query)
    
    # Derive from source titles if available
    valid_titles = [t.strip() for t in source_titles if t and t.strip()]
    
    suggestions: list[str] = []
    
    if language == "hi":
        if topic:
            suggestions.append(f"{topic} के मुख्य लाभ क्या हैं?")
            suggestions.append(f"{topic} कैसे काम करता है?")
            suggestions.append(f"{topic} के विभिन्न प्रकार क्या हैं?")
        elif valid_titles:
            primary_title = valid_titles[0].split(":")[0].strip()
            suggestions.append(f"{primary_title} का क्या महत्व है?")
            suggestions.append(f"{primary_title} के प्रमुख सिद्धांत क्या हैं?")
            suggestions.append(f"{primary_title} के अनुप्रयोग क्या हैं?")
        else:
            suggestions = [
                "प्रकाश संश्लेषण क्या है?",
                "मशीन लर्निंग के मूल सिद्धांत क्या हैं?",
                "कंप्यूटर नेटवर्क में आईपी पता क्या होता है?",
            ]
    else:
        if topic:
            suggestions.append(f"How does {topic} work in practice?")
            suggestions.append(f"What are the main advantages and use cases of {topic}?")
            suggestions.append(f"What is the underlying architecture of {topic}?")
        elif valid_titles:
            primary_title = valid_titles[0].split(":")[0].strip()
            suggestions.append(f"What are the key concepts of {primary_title}?")
            suggestions.append(f"How is {primary_title} applied in real-world systems?")
            suggestions.append(f"What are the advantages of {primary_title}?")
        else:
            suggestions = [
                "What is Retrieval-Augmented Generation (RAG)?",
                "How does FAISS index high-dimensional vectors?",
                "What is the difference between supervised and unsupervised learning?",
            ]

    return suggestions[:3]
