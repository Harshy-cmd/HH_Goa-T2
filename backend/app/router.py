from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Literal


class QueryIntent(str, Enum):
    CONVERSATIONAL = "conversational"
    SYSTEM = "system"
    KNOWLEDGE = "knowledge"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class RouteResult:
    intent: QueryIntent
    direct_answer: str | None = None
    language: str = "en"


_GREETING_PATTERNS = [
    r"^\s*(hello|hi|hey|greetings|good\s+(morning|afternoon|evening|day)|howdy)\b",
    r"^\s*(नमस्ते|प्रणाम|हेलो|हाय|शुभ\s*(प्रभात|संध्या|दिन))",
]

_COURTESY_PATTERNS = [
    r"^\s*(thanks|thank\s+you|thank\s+you\s+very\s+much|much\s+appreciated|cheers)\b",
    r"^\s*(how\s+are\s+you|how\s+are\s+you\s+doing|how's\s+it\s+going|how\s+do\s+you\s+do)\b",
    r"(धन्यवाद|शुक्रिया|आप\s*कैसे\s*हैं|कैसा\s*चल\s*रहा\s*है)",
]

_IDENTITY_NAME_PATTERNS = [
    r"\b(what('s|\s+is)\s+your\s+name|who\s+are\s+you|your\s+name\b|who\s+made\s+you|who\s+created\s+you)\b",
    r"(आपका\s*नाम\s*क्या\s*है|आप\s*कौन\s*हैं|तुम्हारा\s*नाम\s*क्या\s*है|आपको\s*किसने\s*बनाया|नोवारॉन\s*क्या\s*है)",
]

_CAPABILITIES_PATTERNS = [
    r"\b(what\s+can\s+you\s+do|how\s+do\s+i\s+use\s+you|what\s+are\s+your\s+features|what\s+are\s+your\s+capabilities|help\s+me)\b",
    r"(आप\s*क्या\s*कर\s*सकते\s*हैं|आपकी\s*क्षमताएं|मैं\s*आपका\s*उपयोग\s*कैसे\s*करूं)",
]


def detect_language(text: str) -> str:
    # Check if text contains Devanagari Unicode range (\u0900-\u097F)
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"
    return "en"


def classify_query(query: str, preferred_language: str | None = None) -> RouteResult:
    q = query.strip()
    if not q:
        return RouteResult(intent=QueryIntent.CONVERSATIONAL, direct_answer="Hello! How can I help you today?", language="en")

    lang = preferred_language if preferred_language and preferred_language != "auto" else detect_language(q)

    # 1. Identity questions (Name, Who are you, Creator) -> SYSTEM
    for pat in _IDENTITY_NAME_PATTERNS:
        if re.search(pat, q, flags=re.IGNORECASE):
            if lang == "hi":
                answer = "मैं नोवारॉन (NOVARON) हूँ, एक आवाज़-सक्षम ग्राउंडेड आरएजी (Voice-Enabled Grounded RAG) सहायक, जिसे सत्यापित तथ्यों और शून्य मतिभ्रम (Zero Hallucination) के साथ उत्तर देने के लिए बनाया गया है।"
            else:
                answer = "I'm NOVARON, a voice-enabled grounded RAG assistant built for verifiable, hallucination-free question answering."
            return RouteResult(intent=QueryIntent.SYSTEM, direct_answer=answer, language=lang)

    # 2. Capability questions (What can you do, how to use) -> SYSTEM
    for pat in _CAPABILITIES_PATTERNS:
        if re.search(pat, q, flags=re.IGNORECASE):
            if lang == "hi":
                answer = "मैं आपकी आवाज़ या लिखित पाठ के माध्यम से पूछे गए प्रश्नों को समझकर ज्ञानकोष से प्रमाणित उत्तर दे सकता हूँ। मेरी क्षमताओं में व्हिस्पर वाक् पहचान (STT), बहुभाषी FAISS खोज, संदर्भ उद्धरण (Citations), और हिंदी व अंग्रेज़ी में वाक् संश्लेषण (TTS) शामिल हैं।"
            else:
                answer = "I can answer questions using strict evidence-grounded RAG. You can speak or type in English and Hindi. I search indexed knowledge with FAISS and BM25, provide verified passage citations, speak answers aloud via neural TTS, and refuse to guess when evidence is insufficient."
            return RouteResult(intent=QueryIntent.SYSTEM, direct_answer=answer, language=lang)

    # 3. Simple Greetings & Courtesy -> CONVERSATIONAL
    for pat in _GREETING_PATTERNS:
        if re.search(pat, q, flags=re.IGNORECASE):
            if lang == "hi":
                answer = "नमस्ते! मैं नोवारॉन हूँ। आप मुझसे ज्ञानकोष या तकनीकी विषयों से संबंधित कोई भी प्रश्न पूछ सकते हैं।"
            else:
                answer = "Hello! I'm NOVARON. Ask me anything or tap the microphone to speak in English or Hindi."
            return RouteResult(intent=QueryIntent.CONVERSATIONAL, direct_answer=answer, language=lang)

    for pat in _COURTESY_PATTERNS:
        if re.search(pat, q, flags=re.IGNORECASE):
            if "how are you" in q.lower() or "कैसे" in q:
                answer = "मैं बिल्कुल ठीक हूँ, धन्यवाद! आपकी क्या सहायता कर सकता हूँ?" if lang == "hi" else "I'm doing well, ready to answer your questions with grounded evidence! What would you like to know?"
            else:
                answer = "आपका बहुत-बहुत धन्यवाद! क्या आपके पास कोई अन्य प्रश्न है?" if lang == "hi" else "You're welcome! Let me know if you have any more questions."
            return RouteResult(intent=QueryIntent.CONVERSATIONAL, direct_answer=answer, language=lang)

    # 4. All factual and general queries -> KNOWLEDGE (Route into RAG)
    return RouteResult(intent=QueryIntent.KNOWLEDGE, direct_answer=None, language=lang)
