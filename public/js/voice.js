/* ===== VOICE HANDLER — Voice RAG 2026 ===== */

class VoiceHandler {
  constructor() {
    this._mediaRecorder = null;
    this._audioChunks = [];
    this._stream = null;
    this._isRecording = false;
  }

  get isRecording() {
    return this._isRecording;
  }

  /**
   * Check if the browser supports microphone access
   */
  static isSupported() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }

  /**
   * Start recording audio from the microphone
   * @returns {Promise<void>}
   */
  async startRecording() {
    if (this._isRecording) return;

    if (!VoiceHandler.isSupported()) {
      throw new Error('Microphone access is not supported in this browser.');
    }

    try {
      this._stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });
    } catch (err) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        throw new Error('Microphone permission denied. Please allow microphone access and try again.');
      }
      if (err.name === 'NotFoundError') {
        throw new Error('No microphone found. Please connect a microphone and try again.');
      }
      throw new Error(`Microphone error: ${err.message}`);
    }

    this._audioChunks = [];

    // Select supported MIME type dynamically
    let mimeType = '';
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported) {
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) mimeType = 'audio/webm;codecs=opus';
      else if (MediaRecorder.isTypeSupported('audio/webm')) mimeType = 'audio/webm';
      else if (MediaRecorder.isTypeSupported('audio/mp4')) mimeType = 'audio/mp4';
      else if (MediaRecorder.isTypeSupported('audio/aac')) mimeType = 'audio/aac';
    }

    this._mediaRecorder = mimeType ? new MediaRecorder(this._stream, { mimeType }) : new MediaRecorder(this._stream);

    this._mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        this._audioChunks.push(event.data);
      }
    };

    this._mediaRecorder.start(100); // 100ms timeslice
    this._isRecording = true;
  }

  /**
   * Stop recording and return the audio blob
   * @returns {Promise<Blob>} Audio blob
   */
  async stopRecording() {
    return new Promise((resolve, reject) => {
      if (!this._mediaRecorder || !this._isRecording) {
        reject(new Error('Not recording'));
        return;
      }

      this._mediaRecorder.onstop = () => {
        const blob = new Blob(this._audioChunks, {
          type: this._mediaRecorder.mimeType
        });
        this._cleanup();

        if (blob.size === 0) {
          reject(new Error('Recording produced no audio. Please try again.'));
          return;
        }

        resolve(blob);
      };

      this._mediaRecorder.onerror = (err) => {
        this._cleanup();
        reject(new Error(`Recording failed: ${err.error?.message || 'Unknown error'}`));
      };

      this._mediaRecorder.stop();
      this._isRecording = false;
    });
  }

  /**
   * Cancel recording without producing audio
   */
  cancel() {
    if (this._mediaRecorder && this._isRecording) {
      this._mediaRecorder.stop();
    }
    this._isRecording = false;
    this._cleanup();
  }

  _cleanup() {
    if (this._stream) {
      this._stream.getTracks().forEach(track => track.stop());
      this._stream = null;
    }
    this._mediaRecorder = null;
    this._audioChunks = [];
  }
}

window.VoiceHandler = VoiceHandler;
