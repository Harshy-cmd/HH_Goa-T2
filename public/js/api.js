/* ===== API CLIENT — Voice RAG 2026 ===== */

class ApiClient {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
    this._abortController = null;
  }

  /**
   * Send audio to the server for STT transcription
   * @param {Blob} audioBlob
   * @returns {Promise<{transcript: string}>}
   */
  async transcribe(audioBlob) {
    this._abortController = new AbortController();
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    const response = await fetch(`${this.baseUrl}/api/transcribe`, {
      method: 'POST',
      body: formData,
      signal: this._abortController.signal
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `Transcription failed (${response.status})`);
    }

    return response.json();
  }

  /**
   * Send a text query to the RAG pipeline
   * @param {string} query
   * @returns {Promise<object>} RAG response
   */
  async query(query) {
    this._abortController = new AbortController();

    const response = await fetch(`${this.baseUrl}/api/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
      signal: this._abortController.signal
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `Query failed (${response.status})`);
    }

    return response.json();
  }

  /**
   * Upload a document file for ingestion
   * @param {File} file
   * @returns {Promise<object>}
   */
  async uploadDocument(file) {
    this._abortController = new AbortController();
    const formData = new FormData();
    formData.append('document', file);

    const response = await fetch(`${this.baseUrl}/api/upload`, {
      method: 'POST',
      body: formData,
      signal: this._abortController.signal
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `Upload failed (${response.status})`);
    }

    return response.json();
  }

  /**
   * Check system health
   * @returns {Promise<object>}
   */
  async health() {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return response.json();
  }

  /**
   * Get latency benchmark results
   * @returns {Promise<object>}
   */
  async benchmarkLatency() {
    const response = await fetch(`${this.baseUrl}/api/benchmark`);
    return response.json();
  }

  /**
   * Abort any in-flight request
   */
  abort() {
    if (this._abortController) {
      this._abortController.abort();
      this._abortController = null;
    }
  }
}

window.ApiClient = ApiClient;
