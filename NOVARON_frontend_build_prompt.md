# NOVARON — "Ask Anything" Frontend Build Prompt
### HH Goa 2026 · Task #2 (Voice-Enabled RAG Model)

This is a ready-to-paste master prompt for an AI UI builder (Stitch, v0, Bolt, Lovable, Claude Code, etc.) plus the exact backend contract so the generated UI is wired correctly on the first try — not just a pretty mockup.

---

## 1. Why this direction

Your two reference shots already nail the brief — they're not just "nice," they're *on-brand for the hackathon itself* (deep green / pink / yellow, sun-and-wave motif, paper-cut organic shapes = the same visual family as hhgoa.com). Stitch's version is a generic dark dashboard with flat cards; it doesn't feel like Goa, it feels like any SaaS admin panel. The fix isn't "add more UI," it's **commit fully to the illustrated, tactile, sun-drenched identity** and let the RAG mechanics (grounding, citations, latency) show up as small, confident, almost jewelry-like details rather than dashboard clutter.

Also — reuse the type/color system from your **Builder ID app** (Stardom, Melodrama, Space Grotesk, IBM Plex Mono / deep green, yellow, pink). If both your Task #1 and Task #2 submissions share one visual language, it reads as a *studio*, not two disconnected hackathon projects. That consistency is itself a differentiator.

---

## 2. Design language

**Palette**
| Token | Hex | Use |
|---|---|---|
| `--goa-forest` | `#0F3D2E` | primary background |
| `--goa-forest-deep` | `#0A2E22` | secondary surfaces, header bg |
| `--goa-cream` | `#F4EDD8` | blob fill, bottom sheet, body text on dark |
| `--goa-pink` | `#EE2A6D` | mic button, active accents, alerts |
| `--goa-yellow` | `#F5C518` | sun icon, highlights, sparkle accents |
| `--goa-line` | `#F4EDD8` at 15–20% opacity | hairline borders / dotted rings |

**Typography** (match your Builder ID app for cross-project consistency)
- Display / hero questions ("What do you want to know?") → **Melodrama** or **Instrument Serif** — big, warm, slightly imperfect serif
- Eyebrow labels ("ASK ANYTHING", "VOICE RAG · HH GOA 2026") → **Space Grotesk**, uppercase, wide tracking, small size
- Body / transcript / answer text → **Space Grotesk** regular
- Technical readouts (latency ms, chunk ids, scores) → **IBM Plex Mono**, small, muted

**Shape language**
- One recurring motif: an organic "blob" (torn-paper / wax-seal edge, not a perfect circle) as the central voice orb. Layer it: outer dotted/dashed rings → cream blob → inner dark-green disc → sun glyph with pink rays.
- Dotted and dashed concentric rings around the orb, sparingly, like a radar/sound signature — these should **animate outward when the mic is active** to imply "listening."
- Rounded pill buttons and rounded bottom sheet, never sharp corners.
- Sparingly placed 4-point sparkle/asterisk marks (already in your reference images) as a signature accent — use 2-3 per screen max, not confetti.

**Motion**
- Sun/orb idles with a slow (6-8s) breathing scale + subtle rotation of the inner ring.
- On mic-active: waveform bars around the orb react to live input volume (Web Audio API `AnalyserNode`), rings pulse outward on each voiced syllable.
- On "thinking": orb switches to a soft pulsing glow, dotted ring rotates continuously (indeterminate, since retrieval is fast but generation isn't instant).
- Answer arrival: text reveals with a gentle staggered fade/rise, not a hard cut.

---

## 3. Screen-by-screen spec

### A. Idle / Home
- Header: `HH GOA` wordmark + "ASK ANYTHING / VOICE RAG · HH GOA 2026" eyebrow, left. Right: live `● RAG ONLINE` pill (green dot, pulses gently — should reflect a real `GET /health` poll every 15–30s, not be fake) and a settings gear.
- Hero serif headline: "What do you want to know?"
- Two ghost example prompts left/right of the orb (rotate through 4-5 suggested questions pulled from your actual corpus topics so they're not generic — e.g. "How does vector retrieval work?", "What is hybrid reranking?").
- Center: the blob/sun orb, idle breathing state.
- Below orb: last/placeholder transcript line in quotes.
- Status chip row: `✓ GROUNDED` / `✦ N SOURCES` / `✦ latency ms` — populate with the **real values from the last response**, not static demo numbers. Hide this row entirely until a first answer exists.
- Bottom sheet (cream, rounded top corners): four actions — Keyboard/Type, Upload/Context, big pink Microphone (primary), End Conversation. Add a small `Voice → Context → Answer` caption strip underneath as a pipeline breadcrumb — nice touch, keep it.

### B. Listening
- Orb morphs into active waveform state (see Motion above), mic button gets a pink glow ring, caption below switches to "I'm listening…"
- Live partial transcript (if you stream STT) or a simple animated "recording" dot count if you don't.
- Cancel affordance (tap mic again / swipe down) to abort.

### C. Thinking / Retrieving
- Orb pulses in an indeterminate state.
- Optional: cycle small status text under the orb through actual pipeline stages as they complete — "Transcribing…" → "Retrieving evidence…" → "Grounding answer…" — driven by real timing if you can stream stage updates, otherwise a believable simulated sequence timed to typical latencies (~injects some perceived transparency without lying about numbers).

### D. Answer / Grounded response
- Orb settles, answer text streams into a card above the bottom sheet.
- Status chip row now live: `✓ GROUNDED` (or `✕ NOT GROUNDED — refused` styling in a muted red/pink if `refused: true`) + source count + total latency in ms.
- Expandable source strip: small pill cards per source (`document_id`, relevance score as a thin progress bar, snippet on tap) — this directly visualizes the "retrieval that's actually engineered" judging criterion, make it feel deliberate.
- Play button to hear the TTS answer (`audio_base64` from the API, or a follow-up `/v1/tts` call) with a tiny animated audio-bar icon while playing.
- Refusal state is a **first-class screen**, not an error toast — the brief explicitly rewards "guardrails that know when not to answer," so design a calm, on-brand refusal card (not a red error box) that visually communicates "we chose not to guess" as a feature.

### E. Settings / control panel (small, don't over-build)
- Language: EN / HI toggle (maps to `language` form field).
- Chunking strategy: fixed / sentence / hierarchical (segmented control).
- Retrieval mode: dense / bm25 / hybrid / hybrid_rerank.
- Top-k slider.
- Toggle for "speak answers aloud" (`synthesize_audio`).
- This is genuinely useful in a demo: judges can watch you flip retrieval mode live and see grounding/latency change in the chip row.

---

## 4. Backend contract (already built — wire to this exactly)

Base: FastAPI app, `backend/app/main.py`, default `http://localhost:8000`.

```
GET  /health
→ { "status": "ok", "service": "novaron-rag-core" }
```

```
POST /v1/query           (typed question)
Content-Type: application/json
Body: {
  "query": string,                 // 1–2000 chars
  "top_k": int,                    // 1–20, default 5
  "chunking_strategy": "fixed" | "sentence" | "hierarchical",
  "retrieval_mode": "dense" | "bm25" | "hybrid" | "hybrid_rerank"
}
→ {
  "answer": string,
  "refused": bool,
  "retrieval_strategy": string,
  "chunking_strategy": string,
  "sources": [{ chunk_id, document_id, passage_id, title, language, text, relevance_score }],
  "latency_ms": { retrieval, reranking, generation, rag_total, ... }
}
```

```
POST /v1/voice/query     (the main flow — mic button uses this)
Content-Type: multipart/form-data
Fields: file (audio blob: wav/mp3/m4a/ogg, ≤25MB), language?, top_k?, chunking_strategy?, retrieval_mode?, synthesize_audio (bool)
→ same as above, plus:
  { "query": <transcribed text>, "audio_base64": string | null,
    "latency_ms": { stt, retrieval, reranking, generation, tts?, total } }
```

```
POST /v1/tts
Body: { "text": string, "language": "en" | "hi" }
→ binary audio/mpeg stream
```

**Frontend implementation notes:**
- Record mic input with `MediaRecorder` → `audio/webm` or `audio/wav` blob → send as `multipart/form-data` to `/v1/voice/query`.
- Decode `audio_base64` with `atob` → `Uint8Array` → `Blob(['audio/mpeg'])` → `URL.createObjectURL` → `<audio>` element, don't fetch `/v1/tts` again if `synthesize_audio=true` already returned audio.
- `refused: true` always means `sources: []` — branch your UI on this flag, not on empty answer text.
- Poll `/health` for the "RAG ONLINE" pill; treat network failure as `● OFFLINE` in a muted color, don't hide the pill.
- **Add CORS to the backend** — `main.py` currently has no `CORSMiddleware`. You'll need this before the frontend can call it from a different origin/port:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
  ```
- Latency numbers are real and fast (backend targets sub-200ms retrieval per the hackathon brief) — display them, don't fake slower "thinking" delays that contradict your own benchmark story.

---

## 5. Stand-out elements worth adding (pick 3–4, don't do all — polish beats quantity)

1. **Live waveform mic** driven by `AnalyserNode` — visually proves "real voice input, not typed," which is literally a scored criterion.
2. **Latency HUD toggle** — a small mono-font readout (`stt 279ms · retrieval 16ms · gen 1022ms · total 2.9s`) that expands from the chip row. Judges love seeing engineering, not just UX.
3. **Retrieval mode A/B** — a subtle before/after: run the same question through `dense` vs `hybrid_rerank` side by side once, screenshot it for your demo video. Huge for the "engineered retrieval" criterion.
4. **Source relevance visualized** as tiny horizontal bars, not just numbers — reads as more "designed."
5. **Refusal as a calm, branded state** (see Section 3D) instead of an error — most teams will just show a red toast; a deliberate on-brand refusal screen signals guardrail maturity.
6. **Bilingual toggle (EN/HI)** shown prominently, since multilingual is a core backend feature most teams won't visually surface at all.
7. **A subtle Goa-coastline horizon line** at the very bottom of the idle screen (thin animated wave/sun-glow gradient) — ties back to hhgoa.com's own beach/sunset imagery without copying it directly.
8. **Shareable answer card** — one-tap export of question+answer+sources as an image (reuse your `html2canvas` know-how from the Builder ID app) captioned for X, since the hackathon explicitly rewards social posts (`#RAGInGoa`).

Keep it to a **single scrolling screen + bottom sheet**, mobile-first, no navigation chrome — this is a voice-first utility, not a multi-page app.

---

## 6. The paste-ready prompt

Copy everything below into your UI builder of choice:

```
Design and build a mobile-first, single-screen voice assistant web app called
"NOVARON — Ask Anything," branded for HH Goa 2026 hackathon Task #2 (Voice RAG).

VISUAL STYLE:
Deep forest green background (#0F3D2E), cream (#F4EDD8) bottom sheet and blob
shapes, hot pink (#EE2A6D) primary accent, warm yellow (#F5C518) secondary
accent. Organic torn-paper blob shapes, not perfect circles. Dotted/dashed
concentric rings. Serif display font (Melodrama/Instrument Serif) for
headlines, Space Grotesk for UI text and labels, IBM Plex Mono for technical
readouts (latency, scores). Small 4-point sparkle accents used sparingly.
Rounded pill buttons, rounded-top bottom sheet, no sharp corners, no dark
dashboard clichés.

LAYOUT (single screen, states not pages):
- Header: "HH GOA / ASK ANYTHING · VOICE RAG · HH GOA 2026" wordmark left,
  live "RAG ONLINE" status pill + settings gear right.
- Hero serif headline "What do you want to know?" with two rotating example
  prompts flanking a central animated blob/sun orb (cream blob, dark green
  inner disc, yellow sun with pink rays).
- Below orb: live transcript line in quotes, then a status chip row
  (Grounded/Refused, source count, latency ms) that only appears after a
  real answer exists.
- Expandable answer card: streamed answer text, play-audio button, and a
  horizontal strip of source pill cards (doc id + relevance bar).
- Bottom sheet: Keyboard/Type, Upload/Context, large pink Microphone
  (primary, glows + orb goes into live-waveform mode while recording), End
  Conversation. Tiny "Voice → Context → Answer" pipeline caption beneath.
- Settings drawer: EN/HI language toggle, chunking strategy segmented
  control (fixed/sentence/hierarchical), retrieval mode segmented control
  (dense/bm25/hybrid/hybrid_rerank), top-k slider, "speak answers" toggle.

STATES: idle (breathing orb) → listening (live mic waveform, rings pulse
outward) → thinking (indeterminate pulse, cycling stage labels) → answered
(chips populate, source strip, audio playback) → refused (calm on-brand
card, not an error toast — communicate "chose not to guess" as a feature).

BACKEND INTEGRATION (already built, FastAPI):
- POST /v1/voice/query — multipart form: file (recorded audio blob),
  language, top_k, chunking_strategy, retrieval_mode, synthesize_audio.
  Returns { query, answer, refused, sources[], latency_ms{}, audio_base64 }.
- POST /v1/query — JSON typed-text equivalent.
- POST /v1/tts — { text, language } → mp3 stream.
- GET /health — poll for the status pill.
Record audio with MediaRecorder, send as multipart/form-data. Decode
audio_base64 to a Blob and play in an <audio> element. Branch UI on the
`refused` boolean, not on empty text. Show real latency_ms values, never
simulated ones.

Motion: slow breathing idle animation, live audio-reactive waveform while
recording (Web Audio AnalyserNode), staggered fade-in for answer text.
Accessible, responsive, works one-handed on a phone.
```

---

## 7. Suggested stack

Given the backend is Python/FastAPI, keep the frontend simple and fast to iterate on during a live hackathon:
- **Vite + React + Tailwind + Framer Motion** for the orb/waveform animation — fastest path from this spec to working code, and pairs well if you later want to reuse components across your Builder ID app and this one.
- If you want zero build step for a quick demo, a single `index.html` with vanilla JS + `MediaRecorder` + CSS animations works fine too — your Builder ID app already used that pattern successfully.

If you want, I can go ahead and scaffold this as actual code (React or vanilla) wired to your real `/v1/voice/query` endpoint — just say the word and whether you want it in the repo's structure or as a standalone `frontend/` folder.
