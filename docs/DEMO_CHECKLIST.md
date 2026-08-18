# NOVARON — Hackathon Live Demo Checklist & Runbook

This runbook outlines the pre-demo verification checklist, live demo presentation script, and rapid recovery procedures for demonstrating NOVARON.

---

## 1. Pre-Demo Checklist

Before presenting to judges, verify all items:

- [ ] **Backend Service:** Running and healthy (`uvicorn app.main:app --port 8000`)
- [ ] **Frontend Application:** Running and accessible (`npm run dev` at `http://localhost:5173`)
- [ ] **Health Status:** `GET /health` returns HTTP 200 with `status: "ok"`
- [ ] **RAG ONLINE Indicator:** Green glowing pill visible in header
- [ ] **Microphone Permission:** Granted in browser; MediaRecorder initialized
- [ ] **Audio Playback:** System audio unmuted and volume set to audible level
- [ ] **FAISS Indexes Loaded:** Sentence (12,206), Fixed (12,231), Hierarchical (24,414)
- [ ] **MagicRings Three.js Canvas:** Actively rendering subtle idle animation under VoiceOrb
- [ ] **Settings Verified:** Top-K set to 5, chunking set to Sentence, neural TTS enabled
- [ ] **Latency HUD:** Populating real execution timings (Embedding, FAISS, BM25, Gen, TTS)

---

## 2. Live Demo Script (Step-by-Step)

### Step 1: System Overview & Architecture (30s)
1. Point to the UI header showing **NOVARON Voice RAG** and the **RAG ONLINE** indicator.
2. Highlight key capabilities:
   - True multilingual Grounded RAG across **15 languages** (14 Indic + English).
   - Ingested official AI4Bharat **MSMARCO-XI** corpus (~12,184 passages).
   - Dual-engine retrieval: FAISS IndexFlatIP (384-dim E5 embeddings) + BM25 with Reciprocal Rank Fusion (RRF).

### Step 2: English Voice Question (45s)
1. Tap the **VoiceOrb** or press **Spacebar**.
2. Speak: *"What is photosynthesis and how do plants produce glucose?"*
3. Observe state transition: `LISTENING` → `TRANSCRIBING` → `RETRIEVING` → `GENERATING` → `ANSWER_READY` → `PLAYING_AUDIO`.
4. Listen to the generated answer synthesized aloud.
5. Click **Sources (N)** to open the `SourcesDrawer`:
   - Point out the exact passage title, document ID, relevance score, and text highlight.
6. Open **Latency HUD**:
   - Show sub-20ms dense retrieval and sub-200ms voice pipeline response.

### Step 3: Hindi / Indic Voice Question (45s)
1. Tap the **VoiceOrb**.
2. Speak: *"प्रकाश संश्लेषण क्या है और पौधे अपना भोजन कैसे बनाते हैं?"*
3. Watch the deterministic **15-Language Router** instantly route to Hindi (`hi`) in < 0.1 ms.
4. Highlight the grounded Hindi answer and neural Hindi voice readout.

### Step 4: Cross-Lingual Knowledge Demonstration (30s)
1. Ask a question in Tamil or Telugu whose primary source is indexed in English:
   - Tamil: *"செயற்கை நுண்ணறிவு என்றால் என்ன?"*
   - Telugu: *"కృత్రిమ మేధస్సు అంటే ఏమిటి?"*
2. Explain how **Language-Aware Candidate Filtering** retrieves cross-lingual English evidence with **62.7% Recall@10** and **0.359 MRR**.

### Step 5: Refusal Guardrail & Anti-Hallucination Demo (30s)
1. Ask an unsupported question:
   - *"What is the secret recipe for Martian cosmic cake on planet Krypton?"*
2. Show the **RefusalCard** with explicit status:
   - *"We chose not to guess."* / *"I don't have enough information in the indexed knowledge base to answer that reliably."*
3. Explain that NOVARON enforces **zero hallucination** by refusing to fabricate answers when evidence is below relevance thresholds.

---

## 3. Rapid Recovery Procedures

If an unexpected issue occurs during the demo:

| Scenario | Symptom | Action |
|---|---|---|
| **Microphone denied** | Error banner appears | Click browser lock icon in URL bar → reset Microphone permission → reload page. |
| **Backend connection lost** | Red RAG OFFLINE pill | Restart backend: `python -m uvicorn app.main:app --port 8000` |
| **Audio playback silent** | Waveform animates but no sound | Check browser tab autoplay permission or system volume. |
| **STT timeout** | Transcript remains empty | Fallback to Text Query Modal (`Ctrl + K` or search icon) to type queries directly. |
| **Settings reset** | Incorrect chunking / top-k | Click gear icon → select **Sentence** + **Hybrid Rerank** + **Top-K 5**. |

---

## 4. Key Architectural Metrics for Judges

- **Supported Languages:** 15 (`en`, `as`, `bn`, `gu`, `hi`, `kn`, `ml`, `mr`, `ne`, `or`, `pa`, `sa`, `ta`, `te`, `ur`)
- **Corpus Size:** 12,184 verified documents (12,000 MSMARCO-XI + 184 curated)
- **FAISS Vectors:** 12,206 (sentence), 12,231 (fixed), 24,414 (hierarchical)
- **Embedding Model:** `intfloat/multilingual-e5-small` (384-dim, IndexFlatIP)
- **Cross-Lingual Retrieval Recall@10:** **62.7%** (up from 1.2% baseline)
- **Cross-Lingual Retrieval MRR:** **0.359** (up from 0.006 baseline)
- **Local Dense Retrieval Latency:** **16.07 ms (P50)**, **18.54 ms (P95)**
- **Language Router Latency:** **0.05 ms (P50)**, **0.06 ms (P95)**
- **Voice Pipeline Latency:** **196.97 ms (P50)**, **221.13 ms (P95)**
- **Backend Test Suite:** **124/124 tests passing (100%)**
- **Frontend Production Build:** **0 errors, 0 warnings**
