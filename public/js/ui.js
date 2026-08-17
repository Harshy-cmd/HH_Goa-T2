/* ===== UI CONTROLLER — Voice RAG 2026 ===== */

class UIController {
  constructor(stateMachine) {
    this.sm = stateMachine;
    this.elements = {};
    this._cacheElements();
    this._bindStateListener();
  }

  _cacheElements() {
    this.elements = {
      body: document.body,
      heroHeadline: document.getElementById('heroHeadline'),
      artworkZone: document.getElementById('artworkZone'),
      waveformVis: document.getElementById('waveformVis'),
      queryText: document.getElementById('queryText'),
      queryDisplay: document.getElementById('queryDisplay'),
      statusPills: document.getElementById('statusPills'),
      pillGrounded: document.getElementById('pillGrounded'),
      pillSources: document.getElementById('pillSources'),
      pillLatency: document.getElementById('pillLatency'),
      sourceCount: document.getElementById('sourceCount'),
      latencyValue: document.getElementById('latencyValue'),
      answerArea: document.getElementById('answerArea'),
      answerContent: document.getElementById('answerContent'),
      sourcesList: document.getElementById('sourcesList'),
      controlBar: document.getElementById('controlBar'),
      btnKeyboard: document.getElementById('btnKeyboard'),
      btnUpload: document.getElementById('btnUpload'),
      btnMic: document.getElementById('btnMic'),
      btnEnd: document.getElementById('btnEnd'),
      textInputOverlay: document.getElementById('textInputOverlay'),
      textInputForm: document.getElementById('textInputForm'),
      textInput: document.getElementById('textInput'),
      textClose: document.getElementById('textClose'),
      ragStatusPill: document.getElementById('ragStatusPill'),
      statusDot: document.getElementById('statusDot'),
      uploadOverlay: document.getElementById('uploadOverlay'),
    };
  }

  _bindStateListener() {
    this.sm.subscribe((newState, oldState, data) => {
      this._applyState(newState, oldState, data);
    });
  }

  _applyState(state, oldState, data) {
    // Apply data-state to body for CSS state styling
    this.elements.body.setAttribute('data-state', state);

    // Update mic button aria
    if (state === STATES.LISTENING) {
      this.elements.btnMic.setAttribute('aria-label', 'Stop recording');
      this.elements.btnMic.classList.add('listening');
    } else {
      this.elements.btnMic.setAttribute('aria-label', 'Start recording');
      this.elements.btnMic.classList.remove('listening');
    }

    // Handle answer area
    switch (state) {
      case STATES.IDLE:
        this._showIdle(data);
        break;
      case STATES.LISTENING:
        this._showListening();
        break;
      case STATES.TRANSCRIBING:
        this._showTranscribing();
        break;
      case STATES.RETRIEVING:
        this._showRetrieving(data);
        break;
      case STATES.GENERATING:
        this._showGenerating();
        break;
      case STATES.GROUNDED:
        this._showGrounded(data);
        break;
      case STATES.NO_CONTEXT:
        this._showNoContext(data);
        break;
      case STATES.REFUSED:
        this._showRefused(data);
        break;
      case STATES.ERROR:
        this._showError(data);
        break;
    }
  }

  _showIdle(data) {
    if (data && data.reset) {
      this.elements.queryText.textContent = '"Tell me how vector retrieval works..."';
      this.elements.answerArea.hidden = true;
      this.elements.answerArea.className = 'answer-area';
      this.elements.answerContent.textContent = '';
      this.elements.sourcesList.innerHTML = '';
      this.elements.pillGrounded.style.display = '';
      this.elements.sourceCount.textContent = '3';
      this.elements.latencyValue.textContent = '148';
    }
  }

  _showListening() {
    this.elements.queryText.textContent = 'Listening...';
  }

  _showTranscribing() {
    this.elements.queryText.textContent = 'Transcribing...';
  }

  _showRetrieving(data) {
    if (data && data.query) {
      this.elements.queryText.textContent = `"${data.query}"`;
    }
  }

  _showGenerating() {
    this.elements.queryText.textContent = this.elements.queryText.textContent || 'Generating answer...';
  }

  _showGrounded(data) {
    if (!data) return;

    this.elements.answerArea.hidden = false;
    this.elements.answerArea.className = 'answer-area';
    this.elements.answerContent.textContent = data.answer || '';

    // Update status pills
    this.elements.pillGrounded.style.display = '';
    this.elements.sourceCount.textContent = data.sourceCount || '0';
    const latVal = typeof data.latency === 'number' ? data.latency : (data.latency?.total || 0);
    this.elements.latencyValue.textContent = latVal > 0 ? (latVal < 1 ? latVal.toFixed(2) : Math.round(latVal)) : '—';

    // Render sources
    this._renderSources(data.sources || []);
  }

  _showNoContext(data) {
    this.elements.answerArea.hidden = false;
    this.elements.answerArea.className = 'answer-area no-context';
    this.elements.answerContent.textContent = data?.answer || 'I don\'t have enough context to answer that question. Try uploading relevant documents.';
    this.elements.pillGrounded.style.display = 'none';
    this.elements.sourceCount.textContent = '0';
    const latVal = typeof data?.latency === 'number' ? data.latency : (data?.latency?.total || 0);
    this.elements.latencyValue.textContent = latVal > 0 ? (latVal < 1 ? latVal.toFixed(2) : Math.round(latVal)) : '—';
    this.elements.sourcesList.innerHTML = '';
  }

  _showRefused(data) {
    this.elements.answerArea.hidden = false;
    this.elements.answerArea.className = 'answer-area refusal';
    this.elements.answerContent.textContent = data?.answer || 'I\'m unable to answer that question. Please ask something related to the available knowledge base.';
    this.elements.pillGrounded.style.display = 'none';
    this.elements.sourceCount.textContent = '0';
    const latVal = typeof data?.latency === 'number' ? data.latency : (data?.latency?.total || 0);
    this.elements.latencyValue.textContent = latVal > 0 ? (latVal < 1 ? latVal.toFixed(2) : Math.round(latVal)) : '—';
    this.elements.sourcesList.innerHTML = '';
  }

  _showError(data) {
    this.elements.answerArea.hidden = false;
    this.elements.answerArea.className = 'answer-area error';
    this.elements.answerContent.textContent = data?.error || 'An error occurred. Please try again.';
    this.elements.sourcesList.innerHTML = '';
    // Show retry hint
    this.elements.sourcesList.innerHTML = '<p style="color:var(--text-muted); font-style:italic;">Click the microphone or type to try again.</p>';
  }

  _renderSources(sources) {
    this.elements.sourcesList.innerHTML = '';
    if (!sources.length) return;

    const heading = document.createElement('p');
    heading.style.fontWeight = '600';
    heading.style.marginBottom = '8px';
    heading.textContent = 'Sources:';
    this.elements.sourcesList.appendChild(heading);

    sources.forEach((src, i) => {
      const item = document.createElement('div');
      item.className = 'source-item';
      item.innerHTML = `
        <span class="source-badge">${i + 1}</span>
        <span>${src.title || src.id || 'Unknown'}</span>
        ${src.relevance != null ? `<span style="opacity:0.5; margin-left:auto;">${Math.round(src.relevance * 100)}%</span>` : ''}
      `;
      this.elements.sourcesList.appendChild(item);
    });
  }

  /**
   * Show the text input overlay
   */
  showTextInput() {
    this.elements.textInputOverlay.hidden = false;
    this.elements.controlBar.style.visibility = 'hidden';
    this.elements.textInput.focus();
  }

  /**
   * Hide the text input overlay
   */
  hideTextInput() {
    this.elements.textInputOverlay.hidden = true;
    this.elements.controlBar.style.visibility = '';
    this.elements.textInput.value = '';
  }

  /**
   * Update the query display text
   */
  setQueryText(text) {
    this.elements.queryText.textContent = text ? `"${text}"` : '';
  }
}

// Will be initialized in app.js
window.UIController = UIController;
