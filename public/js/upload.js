/* ===== UPLOAD HANDLER — Voice RAG 2026 ===== */

class UploadHandler {
  constructor(apiClient) {
    this.api = apiClient;
    this._maxSizeBytes = 5 * 1024 * 1024; // 5MB
    this._allowedTypes = ['.txt', '.md', '.json', '.csv'];
    this._allowedMimes = [
      'text/plain',
      'text/markdown',
      'text/csv',
      'application/json',
      'application/octet-stream'
    ];
  }

  /**
   * Validate and upload a file
   * @param {File} file
   * @returns {Promise<object>}
   */
  async upload(file) {
    // Validate size
    if (file.size > this._maxSizeBytes) {
      throw new Error(`File too large. Maximum size is ${this._maxSizeBytes / 1024 / 1024}MB.`);
    }

    // Validate extension
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!this._allowedTypes.includes(ext)) {
      throw new Error(`Unsupported file type: ${ext}. Allowed: ${this._allowedTypes.join(', ')}`);
    }

    // Validate MIME (loose check)
    if (file.type && !this._allowedMimes.includes(file.type)) {
      console.warn(`[Upload] Unexpected MIME type: ${file.type}, proceeding with extension-based validation.`);
    }

    return this.api.uploadDocument(file);
  }
}

window.UploadHandler = UploadHandler;
