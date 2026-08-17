/**
 * Live Credentials Verification Script — HH Goa 2026 Task 2
 * Tests real network API connections to Sarvam STT & Google Gemini LLM.
 * NEVER prints API keys or secrets to logs or console.
 */

require('dotenv').config();
const { createSTTProvider } = require('../server/stt/provider');
const { ModelHarness } = require('../server/model/harness');
const { VectorStore } = require('../server/vector/store');
const { EmbeddingService } = require('../server/embedding/service');
const { ChunkingPipeline } = require('../server/chunking/pipeline');
const { Guardrails } = require('../server/guardrails/guardrails');

async function testLiveProviders() {
  console.log('\n  🔐 HHGOARAG — Live Credential & Real Provider Verification\n');

  const sarvamKey = process.env.SARVAM_API_KEY;
  const geminiKey = process.env.GEMINI_API_KEY;

  console.log('  1. Environment Credential Check:');
  console.log(`     - SARVAM_API_KEY : ${sarvamKey ? 'CONFIGURED [Length: ' + sarvamKey.length + ']' : 'MISSING'}`);
  console.log(`     - GEMINI_API_KEY : ${geminiKey ? 'CONFIGURED [Length: ' + geminiKey.length + ']' : 'MISSING'}\n`);

  // Initialize components
  const embedding = new EmbeddingService();
  const store = new VectorStore(embedding);
  const pipeline = new ChunkingPipeline();
  const guardrails = new Guardrails();
  const stt = createSTTProvider('sarvam');
  const harness = new ModelHarness(store, embedding, guardrails);

  // Ingest sample MSMARCO passage into vector store
  const sampleDoc = `Medicine is the science and practice of caring for a patient, managing the diagnosis, prognosis, prevention, treatment, palliation of their injury or disease. Medicine encompasses a variety of health care practices evolved to maintain and restore health by the prevention and treatment of illness.`;
  const chunks = pipeline.process(sampleDoc, { title: 'MSMARCO Medicine Definition', source: 'MSMARCO-XI' });
  store.addChunks(chunks);

  // 2. Real Gemini LLM Model Test
  console.log('  2. Testing Real Gemini LLM Model API Call...');
  const query = 'What is the definition of medicine?';
  const startGemini = process.hrtime.bigint();

  try {
    const response = await harness.execute(query);
    const elapsedGemini = Number(process.hrtime.bigint() - startGemini) / 1e6;

    console.log(`     - Status           : SUCCESS`);
    console.log(`     - Provider Reported: ${response.provider}`);
    console.log(`     - Fallback Used    : ${response.fallback}`);
    console.log(`     - Grounded         : ${response.grounded}`);
    console.log(`     - Sources Count    : ${response.sources.length}`);
    console.log(`     - Latency (Total)  : ${elapsedGemini.toFixed(2)} ms`);
    console.log(`     - Answer Snippet   : "${response.answer.slice(0, 120)}..."\n`);
  } catch (err) {
    console.error(`     - Status : FAILED (${err.message})\n`);
  }

  // 3. Real Sarvam STT API Test (using a minimal valid 16kHz WAV header/pcm buffer)
  console.log('  3. Testing Real Sarvam Speech-to-Text API Call...');

  // Create a minimal 1-second silent WAV buffer for network call verification
  const sampleRate = 16000;
  const numChannels = 1;
  const bitsPerSample = 16;
  const byteRate = sampleRate * numChannels * (bitsPerSample / 8);
  const blockAlign = numChannels * (bitsPerSample / 8);
  const dataSize = sampleRate * blockAlign;
  const buffer = Buffer.alloc(44 + dataSize);

  buffer.write('RIFF', 0);
  buffer.writeUInt32LE(36 + dataSize, 4);
  buffer.write('WAVE', 8);
  buffer.write('fmt ', 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(numChannels, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(byteRate, 28);
  buffer.writeUInt16LE(blockAlign, 32);
  buffer.writeUInt16LE(bitsPerSample, 34);
  buffer.write('data', 36);
  buffer.writeUInt32LE(dataSize, 40);

  const startSarvam = process.hrtime.bigint();
  try {
    const sttResult = await stt.transcribe(buffer, { mimeType: 'audio/wav' });
    const elapsedSarvam = Number(process.hrtime.bigint() - startSarvam) / 1e6;

    console.log(`     - Status           : SUCCESS`);
    console.log(`     - Transcript       : "${sttResult.transcript}"`);
    console.log(`     - Language Code    : ${sttResult.language || 'en'}`);
    console.log(`     - Network Latency  : ${elapsedSarvam.toFixed(2)} ms\n`);
  } catch (err) {
    console.error(`     - Status : FAILED (${err.message})\n`);
  }
}

if (require.main === module) {
  testLiveProviders().catch(console.error);
}

module.exports = { testLiveProviders };
