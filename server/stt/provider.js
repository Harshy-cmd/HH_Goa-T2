/**
 * STT Provider Abstraction — Voice RAG 2026
 * Allows swapping STT providers without changing the UI or pipeline.
 */

class STTProvider {
  /**
   * @param {Buffer} audioBuffer
   * @param {object} options
   * @returns {Promise<{transcript: string, language?: string}>}
   */
  async transcribe(audioBuffer, options = {}) {
    throw new Error('transcribe() must be implemented by subclass');
  }

  get name() {
    return 'base';
  }
}

/**
 * Sarvam AI STT Provider
 */
class SarvamSTTProvider extends STTProvider {
  constructor() {
    super();
    this.apiKey = process.env.SARVAM_API_KEY;
    this.apiUrl = process.env.SARVAM_STT_URL || 'https://api.sarvam.ai/speech-to-text';
    const https = require('https');
    this.httpsAgent = new https.Agent({ keepAlive: true, maxSockets: 20, keepAliveMsecs: 30000 });
  }

  get name() {
    return 'sarvam';
  }

  async transcribe(audioBuffer, options = {}) {
    if (!this.apiKey || this.apiKey === 'your_sarvam_api_key_here') {
      // Fallback to mock mode when API key is not configured
      console.warn('[Sarvam] API key not configured. Using mock transcription for demo.');
      return this._mockTranscribe();
    }

    const FormData = require('form-data');
    const https = require('https');

    const mime = options.mimeType || 'audio/webm';
    const ext = mime.includes('mp4') || mime.includes('aac') ? 'mp4' :
                mime.includes('ogg') ? 'ogg' :
                mime.includes('wav') ? 'wav' : 'webm';

    const form = new FormData();
    form.append('file', audioBuffer, {
      filename: `audio.${ext}`,
      contentType: mime
    });
    form.append('model', 'saaras:v3');
    form.append('mode', 'transcribe');

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        req.destroy();
        reject(new Error('Sarvam API timeout (30s)'));
      }, 30000);

      const url = new URL(this.apiUrl);
      const req = https.request({
        hostname: url.hostname,
        path: url.pathname,
        method: 'POST',
        agent: this.httpsAgent,
        headers: {
          ...form.getHeaders(),
          'api-subscription-key': this.apiKey
        }
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          clearTimeout(timeout);
          try {
            const parsed = JSON.parse(data);
            if (res.statusCode !== 200) {
              console.warn(`[Sarvam] API returned HTTP ${res.statusCode}, falling back to mock transcription.`);
              resolve({ ...this._mockTranscribe(), fallback: true, error: `HTTP ${res.statusCode}` });
              return;
            }
            resolve({
              transcript: parsed.transcript || '',
              language: parsed.language_code || 'en'
            });
          } catch (e) {
            reject(new Error(`Sarvam API: Invalid response: ${data.slice(0, 200)}`));
          }
        });
      });

      req.on('error', (err) => {
        clearTimeout(timeout);
        console.warn('[Sarvam] Network error, using fallback mock transcription:', err.message);
        resolve({ ...this._mockTranscribe(), fallback: true, error: err.message });
      });

      form.pipe(req);
    });
  }

  _mockTranscribe() {
    // Return a plausible mock for demo mode
    const mockTranscripts = [
      'Tell me how vector retrieval works',
      'What is RAG and how does it work',
      'Explain semantic chunking',
      'How does embedding search work',
    ];
    return {
      transcript: mockTranscripts[Math.floor(Math.random() * mockTranscripts.length)],
      language: 'en',
      mock: true
    };
  }
}

/**
 * Factory function to create STT providers
 */
function createSTTProvider(name = 'sarvam') {
  switch (name.toLowerCase()) {
    case 'sarvam':
      return new SarvamSTTProvider();
    default:
      throw new Error(`Unknown STT provider: ${name}`);
  }
}

module.exports = { STTProvider, SarvamSTTProvider, createSTTProvider };
