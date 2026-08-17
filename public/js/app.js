/* ===== APP ENTRY — Voice RAG 2026 ===== */

(function () {
  'use strict';

  // ── Initialize core modules ──
  const sm = window.appState;
  const ui = new UIController(sm);
  const api = new ApiClient('');
  const voice = new VoiceHandler();
  const uploader = new UploadHandler(api);

  // ── Set initial state ──
  document.body.setAttribute('data-state', STATES.IDLE);

  // ── Health check on load ──
  async function checkHealth() {
    try {
      const health = await api.health();
      const dot = document.getElementById('statusDot');
      if (health.status === 'ok') {
        dot.classList.add('online');
      } else {
        dot.classList.remove('online');
      }
    } catch {
      document.getElementById('statusDot').classList.remove('online');
    }
  }
  checkHealth();
  setInterval(checkHealth, 30000);

  // ── Microphone button ──
  const btnMic = document.getElementById('btnMic');
  btnMic.addEventListener('click', async () => {
    if (sm.state === STATES.LISTENING) {
      // Stop recording
      try {
        sm.transition(STATES.TRANSCRIBING);
        const audioBlob = await voice.stopRecording();
        // Send to STT
        const result = await api.transcribe(audioBlob);
        if (!result.transcript || result.transcript.trim() === '') {
          sm.transition(STATES.ERROR, { error: 'No speech detected. Please try again.' });
          return;
        }
        // Run RAG query
        await runQuery(result.transcript);
      } catch (err) {
        console.error('[Voice] Error:', err);
        sm.transition(STATES.ERROR, { error: err.message });
      }
    } else if (sm.state === STATES.IDLE || sm.state === STATES.GROUNDED || sm.state === STATES.NO_CONTEXT || sm.state === STATES.REFUSED || sm.state === STATES.ERROR) {
      // Start recording
      try {
        // Reset to idle first if needed
        if (sm.state !== STATES.IDLE) {
          sm.reset();
        }
        await voice.startRecording();
        sm.transition(STATES.LISTENING);
      } catch (err) {
        console.error('[Voice] Mic error:', err);
        sm.transition(STATES.ERROR, { error: err.message });
      }
    }
  });

  // ── Keyboard / Type button ──
  const btnKeyboard = document.getElementById('btnKeyboard');
  btnKeyboard.addEventListener('click', () => {
    ui.showTextInput();
  });

  // ── Text input form ──
  const textInputForm = document.getElementById('textInputForm');
  textInputForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('textInput').value.trim();
    if (!query) return;
    ui.hideTextInput();
    if (sm.state !== STATES.IDLE) sm.reset();
    await runQuery(query);
  });

  // ── Text close button ──
  const textClose = document.getElementById('textClose');
  textClose.addEventListener('click', () => {
    ui.hideTextInput();
  });

  // ── Upload button ──
  const btnUpload = document.getElementById('btnUpload');
  const uploadOverlay = document.getElementById('uploadOverlay');
  const uploadClose = document.getElementById('uploadClose');
  const uploadBrowse = document.getElementById('uploadBrowse');
  const fileInput = document.getElementById('fileInput');
  const uploadDropzone = document.getElementById('uploadDropzone');
  const uploadStatus = document.getElementById('uploadStatus');

  btnUpload.addEventListener('click', () => {
    uploadOverlay.hidden = false;
  });

  uploadClose.addEventListener('click', () => {
    uploadOverlay.hidden = true;
    uploadStatus.hidden = true;
  });

  uploadOverlay.addEventListener('click', (e) => {
    if (e.target === uploadOverlay) {
      uploadOverlay.hidden = true;
      uploadStatus.hidden = true;
    }
  });

  uploadBrowse.addEventListener('click', () => {
    fileInput.click();
  });

  fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    await handleFileUpload(file);
  });

  // Drag and drop
  uploadDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadDropzone.classList.add('dragover');
  });

  uploadDropzone.addEventListener('dragleave', () => {
    uploadDropzone.classList.remove('dragover');
  });

  uploadDropzone.addEventListener('drop', async (e) => {
    e.preventDefault();
    uploadDropzone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) await handleFileUpload(file);
  });

  async function handleFileUpload(file) {
    try {
      uploadStatus.hidden = false;
      uploadStatus.textContent = `Uploading ${file.name}...`;
      uploadStatus.style.background = 'rgba(26, 92, 58, 0.1)';
      uploadStatus.style.color = 'var(--green-primary)';

      const result = await uploader.upload(file);
      uploadStatus.textContent = `✓ ${file.name} uploaded — ${result.chunksCreated || 0} chunks created.`;
      uploadStatus.style.background = 'rgba(92, 224, 128, 0.1)';

      // Re-check health (vector store may have new data)
      checkHealth();
    } catch (err) {
      uploadStatus.textContent = `✕ ${err.message}`;
      uploadStatus.style.background = 'rgba(232, 80, 80, 0.1)';
      uploadStatus.style.color = 'var(--status-error)';
    }
    fileInput.value = '';
  }

  // ── End conversation ──
  const btnEnd = document.getElementById('btnEnd');
  btnEnd.addEventListener('click', () => {
    if (voice.isRecording) {
      voice.cancel();
    }
    api.abort();
    sm.reset();
  });

  // ── RAG Query Pipeline ──
  async function runQuery(query) {
    try {
      sm.transition(STATES.RETRIEVING, { query });
      const result = await api.query(query);

      // Handle different response types
      if (result.refused) {
        sm.transition(STATES.REFUSED, {
          answer: result.refusal_reason || result.answer,
          latency: result.latency?.total
        });
        return;
      }

      if (!result.grounded || (result.sources && result.sources.length === 0)) {
        sm.transition(STATES.NO_CONTEXT, {
          answer: result.answer || 'No relevant context found.',
          latency: result.latency?.total
        });
        return;
      }

      // Grounded answer
      sm.transition(STATES.GENERATING);
      // Brief delay to show generating state
      await new Promise(r => setTimeout(r, 200));

      sm.transition(STATES.GROUNDED, {
        answer: result.answer,
        sources: result.sources || [],
        sourceCount: result.sources?.length || 0,
        latency: result.latency?.total,
        grounded: result.grounded
      });

    } catch (err) {
      console.error('[Query] Error:', err);
      if (err.name === 'AbortError') return;
      sm.transition(STATES.ERROR, { error: err.message });
    }
  }

  // ── Keyboard shortcuts ──
  document.addEventListener('keydown', (e) => {
    // Escape closes overlays
    if (e.key === 'Escape') {
      if (!document.getElementById('textInputOverlay').hidden) {
        ui.hideTextInput();
      }
      if (!uploadOverlay.hidden) {
        uploadOverlay.hidden = true;
      }
      if (sm.state === STATES.LISTENING) {
        voice.cancel();
        sm.reset();
      }
    }
  });

  console.log('[VoiceRAG] Application initialized.');
})();
