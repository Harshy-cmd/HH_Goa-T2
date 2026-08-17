require('dotenv').config();
const https = require('https');
const FormData = require('form-data');

console.log('SARVAM_API_KEY present:', !!process.env.SARVAM_API_KEY);
console.log('GEMINI_API_KEY present:', !!process.env.GEMINI_API_KEY);

// 1. Diagnose Gemini API
const geminiKey = process.env.GEMINI_API_KEY;
if (geminiKey) {
  const payload = JSON.stringify({
    contents: [{ parts: [{ text: "Hello, answer in 5 words." }] }]
  });

  const req = https.request({
    hostname: 'generativelanguage.googleapis.com',
    path: `/v1beta/models/gemini-3.6-flash:generateContent?key=${geminiKey}`,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(payload)
    }
  }, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      console.log('\n[Gemini Response Status]:', res.statusCode);
      console.log('[Gemini Response Body]:', data.slice(0, 300));
    });
  });
  req.on('error', (e) => console.error('[Gemini Error]:', e.message));
  req.write(payload);
  req.end();
}

// 2. Diagnose Sarvam API
const sarvamKey = process.env.SARVAM_API_KEY;
if (sarvamKey) {
  const form = new FormData();
  const sampleRate = 16000;
  const dataSize = sampleRate * 2;
  const buf = Buffer.alloc(44 + dataSize);
  buf.write('RIFF', 0);
  buf.writeUInt32LE(36 + dataSize, 4);
  buf.write('WAVE', 8);
  buf.write('fmt ', 12);
  buf.writeUInt32LE(16, 16);
  buf.writeUInt16LE(1, 20);
  buf.writeUInt16LE(1, 22);
  buf.writeUInt32LE(sampleRate, 24);
  buf.writeUInt32LE(sampleRate * 2, 28);
  buf.writeUInt16LE(2, 32);
  buf.writeUInt16LE(16, 34);
  buf.write('data', 36);
  buf.writeUInt32LE(dataSize, 40);

  form.append('file', buf, { filename: 'audio.wav', contentType: 'audio/wav' });
  form.append('model', 'saaras:v2');

  const req = https.request({
    hostname: 'api.sarvam.ai',
    path: '/speech-to-text-translate',
    method: 'POST',
    headers: {
      ...form.getHeaders(),
      'api-subscription-key': sarvamKey
    }
  }, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      console.log('\n[Sarvam Response Status]:', res.statusCode);
      console.log('[Sarvam Response Body]:', data.slice(0, 300));
    });
  });
  req.on('error', (e) => console.error('[Sarvam Error]:', e.message));
  form.pipe(req);
}
