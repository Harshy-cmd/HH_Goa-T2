/**
 * Real End-to-End Voice RAG Flow Verification & Latency Benchmark
 *
 * Flow: Spoken WAV file -> /api/transcribe (Sarvam saaras:v3) -> Transcript -> /api/query (MSMARCO-XI + Gemini gemini-3.6-flash + Grounding + Citations)
 * Records P50, P70, P100 latency for STT, RAG, and Voice -> Answer total.
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const FormData = require('form-data');

function postAudio(filePath) {
  return new Promise((resolve, reject) => {
    const form = new FormData();
    const fileStream = fs.createReadStream(filePath);
    form.append('audio', fileStream, { filename: path.basename(filePath), contentType: 'audio/wav' });

    const start = process.hrtime.bigint();
    const req = http.request({
      hostname: 'localhost',
      port: 3000,
      path: '/api/transcribe',
      method: 'POST',
      headers: form.getHeaders()
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const elapsedMs = Number(process.hrtime.bigint() - start) / 1e6;
        try {
          const json = JSON.parse(data);
          resolve({ status: res.statusCode, body: json, latencyMs: elapsedMs });
        } catch (e) {
          reject(new Error(`Failed to parse response: ${data}`));
        }
      });
    });

    req.on('error', reject);
    form.pipe(req);
  });
}

async function postAudioWithRetry(filePath, retries = 2) {
  for (let attempt = 1; attempt <= retries + 1; attempt++) {
    try {
      const res = await postAudio(filePath);
      if (res.status === 200 && res.body.transcript && !res.body.fallback && res.body.transcript.trim() !== '') {
        return res;
      }
      if (attempt <= retries) {
        console.warn(`     [STT Retry ${attempt}/${retries}] Empty/fallback transcript returned. Retrying in 1s...`);
        await new Promise(r => setTimeout(r, 1000));
      } else {
        return res;
      }
    } catch (err) {
      if (attempt <= retries) {
        console.warn(`     [STT Retry ${attempt}/${retries}] Request error: ${err.message}. Retrying in 1s...`);
        await new Promise(r => setTimeout(r, 1000));
      } else {
        throw err;
      }
    }
  }
}

function postQuery(queryText) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify({ query: queryText });
    const start = process.hrtime.bigint();

    const req = http.request({
      hostname: 'localhost',
      port: 3000,
      path: '/api/query',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const elapsedMs = Number(process.hrtime.bigint() - start) / 1e6;
        try {
          const json = JSON.parse(data);
          resolve({ status: res.statusCode, body: json, latencyMs: elapsedMs });
        } catch (e) {
          reject(new Error(`Failed to parse response: ${data}`));
        }
      });
    });

    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

function calcPercentile(arr, p) {
  const sorted = [...arr].sort((a, b) => a - b);
  const idx = Math.ceil((p / 100) * sorted.length) - 1;
  return sorted[Math.max(0, idx)];
}

async function runE2EVerification() {
  console.log('\n  🎙️ HHGOARAG — Real Browser Microphone Flow & End-to-End Latency Evaluation\n');

  const files = [
    'spoken_query_1.wav',
    'spoken_query_2.wav',
    'spoken_query_3.wav',
    'spoken_query_4.wav',
    'spoken_query_5.wav'
  ];

  const sttLatencies = [];
  const ragLatencies = [];
  const totalLatencies = [];
  const resultsSummary = [];

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    console.log(`  [Run ${i + 1}/${files.length}] Processing audio recording: ${file}`);

    // Step 1: STT via Sarvam saaras:v3
    const sttRes = await postAudioWithRetry(file);
    const transcript = sttRes.body.transcript || '';
    const sttLatency = sttRes.latencyMs;
    sttLatencies.push(sttLatency);

    console.log(`     - STT Status     : ${sttRes.status === 200 ? 'SUCCESS' : 'FAILED'}`);
    console.log(`     - Transcript     : "${transcript}"`);
    console.log(`     - STT Latency    : ${sttLatency.toFixed(2)} ms`);

    if (!transcript || transcript.trim() === '' || sttRes.body.fallback) {
      throw new Error(`[Run ${i + 1}] STT failed or returned empty/fallback transcript. Aborting.`);
    }

    // Step 2: RAG query via MSMARCO-XI retrieval + Gemini + Grounding + Citations
    const ragRes = await postQuery(transcript);
    const ragBody = ragRes.body;
    const ragLatency = ragRes.latencyMs;
    ragLatencies.push(ragLatency);

    const totalLatency = sttLatency + ragLatency;
    totalLatencies.push(totalLatency);

    console.log(`     - RAG Provider   : ${ragBody.provider}`);
    console.log(`     - Fallback Used  : ${ragBody.fallback}`);
    console.log(`     - Grounded       : ${ragBody.grounded}`);
    console.log(`     - Sources Count  : ${ragBody.sources ? ragBody.sources.length : 0}`);
    console.log(`     - Answer Snippet : "${(ragBody.answer || '').slice(0, 100)}..."`);
    console.log(`     - RAG Latency    : ${ragLatency.toFixed(2)} ms`);
    console.log(`     - Total Latency  : ${totalLatency.toFixed(2)} ms\n`);

    if (ragBody.fallback) {
      throw new Error(`[Run ${i + 1}] RAG fell back to local synthesis instead of real Gemini model. Aborting.`);
    }

    resultsSummary.push({
      run: i + 1,
      audioFile: file,
      transcript,
      provider: ragBody.provider,
      grounded: ragBody.grounded,
      sourcesCount: ragBody.sources ? ragBody.sources.length : 0,
      sttMs: sttLatency,
      ragMs: ragLatency,
      totalMs: totalLatency
    });

    // Pause 1s between runs
    await new Promise(r => setTimeout(r, 1000));
  }

  // Calculate P50, P70, P100
  const sttP50 = calcPercentile(sttLatencies, 50);
  const sttP70 = calcPercentile(sttLatencies, 70);
  const sttP100 = calcPercentile(sttLatencies, 100);

  const ragP50 = calcPercentile(ragLatencies, 50);
  const ragP70 = calcPercentile(ragLatencies, 70);
  const ragP100 = calcPercentile(ragLatencies, 100);

  const totalP50 = calcPercentile(totalLatencies, 50);
  const totalP70 = calcPercentile(totalLatencies, 70);
  const totalP100 = calcPercentile(totalLatencies, 100);

  console.log('  ┌────────────────────────────────────────────────────────────────────────┐');
  console.log('  │          REAL VOICE RAG PIPELINE LATENCY REPORT (P50 / P70 / P100)      │');
  console.log('  ├────────────────────────────────────┬──────────────┬──────────────┬─────┤');
  console.log('  │ Stage                              │ P50 (ms)     │ P70 (ms)     │ P100│');
  console.log('  ├────────────────────────────────────┼──────────────┼──────────────┼─────┤');
  console.log(`  │ 1. STT (Sarvam saaras:v3)          │ ${sttP50.toFixed(2).padEnd(12)} │ ${sttP70.toFixed(2).padEnd(12)} │ ${sttP100.toFixed(2)} ms │`);
  console.log(`  │ 2. RAG (MSMARCO + Gemini + Ground) │ ${ragP50.toFixed(2).padEnd(12)} │ ${ragP70.toFixed(2).padEnd(12)} │ ${ragP100.toFixed(2)} ms │`);
  console.log(`  │ 3. Complete Voice -> Answer Total  │ ${totalP50.toFixed(2).padEnd(12)} │ ${totalP70.toFixed(2).padEnd(12)} │ ${totalP100.toFixed(2)} ms │`);
  console.log('  └────────────────────────────────────┴──────────────┴──────────────┴─────┘\n');

  return {
    runsCount: files.length,
    stt: { p50: sttP50, p70: sttP70, p100: sttP100 },
    rag: { p50: ragP50, p70: ragP70, p100: ragP100 },
    total: { p50: totalP50, p70: totalP70, p100: totalP100 },
    details: resultsSummary
  };
}

if (require.main === module) {
  runE2EVerification().catch(err => {
    console.error('\n  ✕ E2E Verification Failed:', err.message);
    process.exit(1);
  });
}

module.exports = { runE2EVerification };
