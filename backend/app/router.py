"""NOVARON Deterministic Multilingual Query Router.
Supports:
- 14 Indic languages: Assamese (as), Bengali (bn), Gujarati (gu), Hindi (hi), Kannada (kn),
  Malayalam (ml), Marathi (mr), Nepali (ne), Odia (or), Punjabi (pa), Sanskrit (sa),
  Tamil (ta), Telugu (te), Urdu (ur)
- English (en) and Hinglish.
- Deterministic Unicode script detection and lexical disambiguation.
- Sub-millisecond direct shortcuts for greetings, courtesies, system identity, and capabilities.
"""
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
    confidence: float = 1.0


# --- Unicode Ranges for Deterministic Script Detection ---
_SCRIPT_PATTERNS = [
    ("gu", re.compile(r"[\u0A80-\u0AFF]")),          # Gujarati
    ("pa", re.compile(r"[\u0A00-\u0A7F]")),          # Gurmukhi (Punjabi)
    ("or", re.compile(r"[\u0B00-\u0B7F]")),          # Odia
    ("ta", re.compile(r"[\u0B80-\u0BFF]")),          # Tamil
    ("te", re.compile(r"[\u0C00-\u0C7F]")),          # Telugu
    ("kn", re.compile(r"[\u0C80-\u0CFF]")),          # Kannada
    ("ml", re.compile(r"[\u0D00-\u0D7F]")),          # Malayalam
    ("ur", re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")), # Arabic / Nastaliq
    ("bengali_block", re.compile(r"[\u0980-\u09FF]")), # Bengali / Assamese
    ("devanagari_block", re.compile(r"[\u0900-\u097F]")), # Devanagari (hi, mr, ne, sa)
]

_ASSAMESE_CHARS = re.compile(r"[\u09F0\u09F1]")  # Assamese Ra (ৰ), Wa (ৱ)
_ASSAMESE_WORDS = re.compile(r"(হৈছে|কিয়|কেনেকৈ|নহয়|আছিল|হলে|হব|আপোনাৰ|আপুনি|ধন্যবাদ|অসমীয়া|নমস্কাৰ|নেকি|বুলি|লগত|কিদৰে|আহিছে)")
_BENGALI_WORDS = re.compile(r"(কী|কেন|কিভাবে|হয়েছে|নয়|ছিল|হবে|আপনার|আপনি|নমস্কার|আছেন|কেমন|করে|করা|নেই|সাথে|বলতে\s*কী)")

# Devanagari Sub-language lexical and character signals
_MARATHI_CHARS = re.compile(r"[\u0933]")  # Marathi Lla (ळ)
_MARATHI_WORDS = re.compile(r"(आहे|नाही|काय|कसे|आणि|म्हणजे|होते|केले|करावे|झाले|त्यांचे|तुमचे|तुम्ही|नमस्कार|कशास|कशाला|बद्दल|सांगा)")

_NEPALI_WORDS = re.compile(r"(के\s*हो|के\s*छ|भनेको\s*के|कसरी|किन|छ\?|छन्|भनेको|हुन|गर्छ|थियो|गर्नु|लाई|बाट|अनि|तपाईं|तपाईंको|हुनुहुन्छ|नेपाली|भयो|हुन्छ|गर्न)")

_SANSKRIT_WORDS = re.compile(r"(किम्|अस्ति|भवति|कथम्|उच्यते|संस्कृत|सन्ति|विद्यते|कियत्|कुत्र|कदा|भवतः|भवन्तः|शास्त्रम्|वेद|अर्थः|नास्ति|इति\s*च)")
_SANSKRIT_CHARS = re.compile(r"[\u0903]")  # Visarga (ः)

_HINDI_WORDS = re.compile(r"(क्या\s*है|क्या\s*होता|कैसे\s*होता|क्यों\s*होता|किसे\s*कहते|कहा\s*जाता|होता\s*है|होती\s*है|होते\s*हैं|सकता\s*है|सकती\s*है|सकते\s*हैं|आपका\s*नाम|आप\s*कौन|नमस्ते|प्रणाम|नहीं\s*है|और|में|से|को|पर)")


def detect_language_with_confidence(text: str) -> tuple[str, float]:
    """Deterministically identifies the language of the given query text using script and lexical rules."""
    t = text.strip()
    if not t:
        return "en", 1.0

    # 1. Check Unique Indic Scripts
    for lang, pattern in _SCRIPT_PATTERNS:
        if lang == "bengali_block":
            if pattern.search(t):
                # Disambiguate Assamese vs Bengali
                if _ASSAMESE_CHARS.search(t):
                    return "as", 0.99
                if _ASSAMESE_WORDS.search(t):
                    return "as", 0.95
                if _BENGALI_WORDS.search(t):
                    return "bn", 0.98
                return "bn", 0.90
        elif lang == "devanagari_block":
            if pattern.search(t):
                # Disambiguate Devanagari: mr, ne, sa, hi
                if _MARATHI_CHARS.search(t) or _MARATHI_WORDS.search(t):
                    return "mr", 0.98
                if _NEPALI_WORDS.search(t):
                    return "ne", 0.98
                if _SANSKRIT_WORDS.search(t) or _SANSKRIT_CHARS.search(t):
                    return "sa", 0.98
                if _HINDI_WORDS.search(t):
                    return "hi", 0.98
                return "hi", 0.85  # Safe default Devanagari
        else:
            if pattern.search(t):
                return lang, 0.99

    # 2. Latin Script (English / Hinglish)
    return "en", 0.99


def detect_language(text: str) -> str:
    lang, _ = detect_language_with_confidence(text)
    return lang


# --- Conversational and Identity Shortcut Patterns Across Languages ---

_GREETING_PATTERNS = [
    # English / Latin
    r"^\s*(hello|hi|hey|greetings|good\s+(morning|afternoon|evening|day)|howdy)\b",
    # Hindi / Devanagari
    r"^\s*(नमस्ते|प्रणाम|हेलो|हाय|शुभ\s*(प्रभात|संध्या|दिन))",
    # Tamil
    r"^\s*(வணக்கம்|ஹலோ)",
    # Telugu
    r"^\s*(నమస్కారం|నమస్తే|హలో)",
    # Kannada
    r"^\s*(ನಮಸ್ಕಾರ|ನಮಸ್ತೆ|ಹಲೋ)",
    # Malayalam
    r"^\s*(നമസ്കാരം|ഹലോ)",
    # Bengali / Assamese
    r"^\s*(নমস্কার|নমস্কাৰ|সালাম|হ্যালো)",
    # Gujarati
    r"^\s*(નમસ્તે|નમસ્કાર|હેલો)",
    # Marathi
    r"^\s*(नमस्कार|जय\s*महाराष्ट्र|हॅलो)",
    # Punjabi
    r"^\s*(ਸਤਿ\s*ਸ੍ਰੀ\s*ਅਕਾਲ|ਨਮਸਤੇ|ਹੈਲੋ)",
    # Odia
    r"^\s*(ନମସ୍କାର|ହେଲୋ)",
    # Urdu
    r"^\s*(سلام|السلام\s*عليكم|آداب|ہیلو)",
    # Sanskrit
    r"^\s*(नमस्ते|नमो\s*नमः|प्रणामाः)",
]

_COURTESY_PATTERNS = [
    # English
    r"^\s*(thanks|thank\s+you|thank\s+you\s+very\s+much|much\s+appreciated|cheers)\b",
    r"^\s*(how\s+are\s+you|how\s+are\s+you\s+doing|how's\s+it\s+going|how\s+do\s+you\s+do)\b",
    # Hindi / Indic Courtesy
    r"(धन्यवाद|शुक्रिया|आप\s*कैसे\s*हैं|कैसा\s*चल\s*रहा\s*है|ధన్యవాదాలు|நன்றி|ಧನ್ಯವಾದಗಳು|നന്ദി|ধন্যবাদ|આભાર|ਮਿਹਰਬਾਨੀ)",
]

_IDENTITY_NAME_PATTERNS = [
    # English
    r"\b(what('s|\s+is)\s+your\s+name|who\s+are\s+you|your\s+name\b|who\s+made\s+you|who\s+created\s+you)\b",
    # Hindi
    r"(आपका\s*नाम\s*क्या\s*है|आप\s*कौन\s*हैं|तुम्हारा\s*नाम\s*क्या\s*है|आपको\s*किसने\s*बनाया|नोवारॉन\s*क्या\s*है)",
    # Tamil
    r"(உங்கள்\s*பெயர்\s*என்ன|நீங்கள்\s*யார்)",
    # Telugu
    r"(మీ\s*పేరు\s*ఏమిటి|మీరు\s*ఎవరు)",
    # Kannada
    r"(ನಿಮ್ಮ\s*ಹೆಸರೇನು|ನೀವು\s*ಯಾರು)",
    # Malayalam
    r"(നിങ്ങളുടെ\s*പേരെന്താണ്|നിങ്ങൾ\s*ആരാണ്)",
    # Bengali / Assamese
    r"(আপনার\s*নাম\s*কি|আপোনাৰ\s*নাম\s*কি|আপনি\s*কে|আপুনি\s*কোন)",
    # Gujarati
    r"(તમારું\s*નામ\s*શું\s*છે|તમે\s*કોણ\s*છો)",
    # Marathi
    r"(तुमचे\s*नाव\s*काय\s*आहे|तुम्ही\s*कोण\s*आहात)",
    # Punjabi
    r"(ਤੁਹਾਡਾ\s*ਨਾਮ\s*ਕੀ\s*ਹੈ|ਤੁਸੀਂ\s*ਕੌਣ\s*ਹੋ)",
    # Odia
    r"(ଆପଣଙ୍କ\s*ନାମ\s*କଣ|ଆପଣ\s*କିଏ)",
    # Urdu
    r"(آپ\s*کا\s*نام\s*[کك]یا\s*ہے|آپ\s*[کك]ون\s*ہیں)",
    # Sanskrit
    r"(भवतः\s*नाम\s*किम्|भवन्तः\s*के\s*सन्ति)",
]

_CAPABILITIES_PATTERNS = [
    # English
    r"\b(what\s+can\s+you\s+do|how\s+do\s+i\s+use\s+you|what\s+are\s+your\s+features|what\s+are\s+your\s+capabilities|help\s+me)\b",
    # Hindi
    r"(आप\s*क्या\s*कर\s*सकते\s*हैं|आपकी\s*क्षमताएं|मैं\s*आपका\s*उपयोग\s*कैसे\s*करूं)",
]

# Standard identity responses tailored by language
_IDENTITY_RESPONSES = {
    "hi": "मैं नोवारॉन (NOVARON) हूँ, एक आवाज़-सक्षम ग्राउंडेड आरएजी (Voice-Enabled Grounded RAG) सहायक, जिसे सत्यापित तथ्यों और शून्य मतिभ्रम (Zero Hallucination) के साथ उत्तर देने के लिए बनाया गया है।",
    "en": "I'm NOVARON, a voice-enabled grounded RAG assistant built for verifiable, hallucination-free question answering.",
    "ta": "நான் நோவாரோன் (NOVARON), சரிபார்க்கப்பட்ட உண்மைகளுடன் பதிலளிக்கும் குரல் ஆதரவு RAG உதவியாளர்.",
    "te": "నేను నోవారన్ (NOVARON), ధృవీకరించబడిన వాస్తవాలతో సమాధానాలు ఇచ్చే వాయిస్ RAG సహాయకుడిని.",
    "kn": "ನಾನು ನೊವಾರಾನ್ (NOVARON), ನಿಖರ ಮತ್ತು ಪರಿಶೀಲಿಸಿದ ಮಾಹಿತಿಯೊಂದಿಗೆ ಉತ್ತರಿಸುವ ಧ್ವನಿ ಸಕ್ರಿಯ RAG ಸಹಾಯಕ.",
    "ml": "ഞാൻ നൊവാരോൺ (NOVARON), കൃത്യമായ വിവരങ്ങളോടെ മറുപടി നൽകുന്ന വോയ്‌സ് RAG അസിസ്റ്റന്റ് ആണ്.",
    "bn": "আমি নোভারন (NOVARON), যাচাইকৃত তথ্যের সাথে উত্তর প্রদানকারী একটি ভয়েস-সক্ষম RAG সহকারী।",
    "gu": "હું નોવારોન (NOVARON) છું, ચકાસાયેલ તથ્યો સાથે ઉત્તર આપતો અવાજ-સક્ષમ RAG સહાયક.",
    "mr": "मी नोव्हारॉन (NOVARON) आहे, अचूक आणि पडताळणीयोग्य माहिती देणारा व्हॉइस-सक्षम RAG सहाय्यक.",
    "pa": "ਮੈਂ ਨੋਵਾਰੋਨ (NOVARON) ਹਾਂ, ਪ੍ਰਮਾਣਿਤ ਤੱਥਾਂ ਨਾਲ ਜਵਾਬ ਦੇਣ ਵਾਲਾ ਇੱਕ ਵੌਇਸ RAG ਸਹਾਇਕ।",
    "or": "ମୁଁ ନୋଭାରନ୍ (NOVARON), ପ୍ରମାଣିତ ତଥ୍ୟ ସହିତ ଉତ୍ତର ଦେଉଥିବା ଭଏସ୍ RAG ସହାୟକ।",
    "ur": "میں نووارون (NOVARON) ہوں، تصدیق شدہ شواہد کے ساتھ جواب دینے والا ایک صوتی RAG اسسٹنٹ۔",
    "as": "মই নোৱাৰন (NOVARON), প্ৰমাণিত তথ্যৰ সৈতে উত্তৰ দিয়া এটা ভইচ RAG সহায়ক।",
    "ne": "म नोभारोन (NOVARON) हुँ, प्रमाणित तथ्यहरूका साथ उत्तर दिने भ्वाइस RAG सहायक।",
    "sa": "अहं नोवारान् (NOVARON) अस्मि, प्रमाणसहितं सत्यं उत्तरं दातुं निर्मितः वाक्-समर्थः RAG सहायकः।",
}

_GREETING_RESPONSES = {
    "hi": "नमस्ते! मैं नोवारॉन हूँ। आप मुझसे ज्ञानकोष या तकनीकी विषयों से संबंधित कोई भी प्रश्न पूछ सकते हैं।",
    "en": "Hello! I'm NOVARON. Ask me anything or tap the microphone to speak in English or Indic languages.",
    "ta": "வணக்கம்! நான் நோவாரோன். நீங்கள் எந்த கேள்வியையும் கேட்கலாம்.",
    "te": "నమస్కారం! నేను నోవారన్. మీరు ఏదైనా ప్రశ్న అడగవచ్చు.",
    "kn": "ನಮಸ್ಕಾರ! ನಾನು ನೊವಾರಾನ್. ನೀವು ಯಾವುದೇ ಪ್ರಶ್ನೆ ಕೇಳಬಹುದು.",
    "ml": "നമസ്കാരം! ഞാൻ നൊവാരോൺ. നിങ്ങൾക്ക് എന്തും ചോദിക്കാം.",
    "bn": "নমস্কার! আমি নোভারন। আপনি যেকোনো প্রশ্ন জিজ্ঞাসা করতে পারেন।",
    "gu": "નમસ્તે! હું નોવારોન છું. તમે કોઈપણ પ્રશ્ન પૂછી શકો છો.",
    "mr": "नमस्कार! मी नोव्हारॉन आहे. आपण कोणताही प्रश्न विचारू शकता.",
    "pa": "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਨੋਵਾਰੋਨ ਹਾਂ। ਤੁਸੀਂ ਕੋਈ ਵੀ ਸਵਾਲ ਪੁੱਛ ਸਕਦੇ ਹੋ।",
    "or": "ନମସ୍କାର! ମୁଁ ନୋଭାରନ୍। ଆପଣ ଯେକୌଣସି ପ୍ରଶ୍ନ ପଚାରିପାରିବେ।",
    "ur": "سلام! میں نووارون ہوں۔ آپ مجھ سے کوئی भी سوال پوچھ سکتے ہیں۔",
    "as": "নমস্কাৰ! মই নোৱাৰন। আপুনি যিকোনো প্ৰশ্ন সুধিব পাৰে।",
    "ne": "नमस्ते! म नोभारोन हुँ। तपाईं कुनै पनि प्रश्न सोध्न सक्नुहुन्छ।",
    "sa": "नमस्ते! अहं नोवारान् अस्मि। भवान् किमपि प्रष्टुं शक्नोति।",
}


def classify_query(query: str, preferred_language: str | None = None) -> RouteResult:
    q = query.strip()
    if not q:
        return RouteResult(
            intent=QueryIntent.CONVERSATIONAL,
            direct_answer="Hello! How can I help you today?",
            language="en",
            confidence=1.0,
        )

    if preferred_language and preferred_language != "auto":
        lang, conf = preferred_language, 1.0
    else:
        lang, conf = detect_language_with_confidence(q)

    # 1. Identity questions (Name, Who are you, Creator) -> SYSTEM
    for pat in _IDENTITY_NAME_PATTERNS:
        if re.search(pat, q, flags=re.IGNORECASE):
            answer = _IDENTITY_RESPONSES.get(lang, _IDENTITY_RESPONSES["en"])
            return RouteResult(intent=QueryIntent.SYSTEM, direct_answer=answer, language=lang, confidence=conf)

    # 2. Capability questions (What can you do, how to use) -> SYSTEM
    for pat in _CAPABILITIES_PATTERNS:
        if re.search(pat, q, flags=re.IGNORECASE):
            if lang == "hi":
                answer = "मैं आपकी आवाज़ या लिखित पाठ के माध्यम से पूछे गए प्रश्नों को समझकर ज्ञानकोष से प्रमाणित उत्तर दे सकता हूँ। मेरी क्षमताओं में व्हिस्पर वाक् पहचान (STT), बहुभाषी FAISS खोज, संदर्भ उद्धरण (Citations), और 14 भारतीय भाषाओं में वाक् संश्लेषण (TTS) शामिल हैं।"
            else:
                answer = "I can answer questions across 14 Indic languages and English using strict evidence-grounded RAG. I search indexed knowledge with FAISS and BM25, provide verified citations, speak answers aloud via neural TTS, and refuse to guess when evidence is insufficient."
            return RouteResult(intent=QueryIntent.SYSTEM, direct_answer=answer, language=lang, confidence=conf)

    # 3. Simple Greetings & Courtesy -> CONVERSATIONAL
    for pat in _GREETING_PATTERNS:
        if re.search(pat, q, flags=re.IGNORECASE):
            answer = _GREETING_RESPONSES.get(lang, _GREETING_RESPONSES["en"])
            return RouteResult(intent=QueryIntent.CONVERSATIONAL, direct_answer=answer, language=lang, confidence=conf)

    for pat in _COURTESY_PATTERNS:
        if re.search(pat, q, flags=re.IGNORECASE):
            if "how are you" in q.lower() or "कैसे" in q:
                answer = "मैं बिल्कुल ठीक हूँ, धन्यवाद! आपकी क्या सहायता कर सकता हूँ?" if lang == "hi" else "I'm doing well, ready to answer your questions with grounded evidence! What would you like to know?"
            else:
                answer = "आपका बहुत-बहुत धन्यवाद! क्या आपके पास कोई अन्य प्रश्न है?" if lang == "hi" else "You're welcome! Let me know if you have any more questions."
            return RouteResult(intent=QueryIntent.CONVERSATIONAL, direct_answer=answer, language=lang, confidence=conf)

    # 4. All factual and general queries -> KNOWLEDGE (Route into Grounded RAG)
    return RouteResult(intent=QueryIntent.KNOWLEDGE, direct_answer=None, language=lang, confidence=conf)
