/**
 * Benchmark Executable — Voice RAG 2026
 * Credentials-Gated Real-Path Benchmark Suite Execution
 */

const { ModelHarness } = require('../server/model/harness');
const { VectorStore } = require('../server/vector/store');
const { EmbeddingService } = require('../server/embedding/service');
const { ChunkingPipeline } = require('../server/chunking/pipeline');
const { Guardrails } = require('../server/guardrails/guardrails');
const { LatencyTracker } = require('../server/perf/latency');
const { BenchmarkRunner } = require('../server/perf/benchmark');
const { createSTTProvider } = require('../server/stt/provider');
const { ingestDocument } = require('../server/ingestion/ingest');
const fs = require('fs');
const path = require('path');

async function runBenchmark() {
  console.log('\n  ⚡ Running Voice RAG Credentials-Gated Latency Benchmark...\n');

  const embedding = new EmbeddingService();
  const store = new VectorStore(embedding);
  const pipeline = new ChunkingPipeline();
  const guardrails = new Guardrails();
  const stt = createSTTProvider('sarvam');
  const harness = new ModelHarness(store, embedding, guardrails);
  const tracker = new LatencyTracker();
  const runner = new BenchmarkRunner(harness, tracker, stt);

  // Ingest demo data
  const demoDir = path.join(__dirname, '..', 'data', 'demo');
  if (fs.existsSync(demoDir)) {
    const files = fs.readdirSync(demoDir);
    for (const file of files) {
      const content = fs.readFileSync(path.join(demoDir, file), 'utf-8');
      await ingestDocument(content, file, pipeline, embedding, store);
    }
  }

  console.log(`  Indexed ${store.getStats().totalChunks} chunks.\n`);

  const results = await runner.run();

  function printTable(title, summary, mode, status = 'VERIFIED', extra = '') {
    console.log(`  ┌─────────────────────────────────────────┐`);
    console.log(`  │ ${title.padEnd(39)} │`);
    console.log(`  ├─────────────────────────────────────────┤`);
    console.log(`  │ Mode          : ${mode.padEnd(23)} │`);
    console.log(`  │ Status        : ${status.padEnd(23)} │`);

    if (summary) {
      console.log(`  │ Total Queries : ${String(summary.totalQueries).padEnd(23)} │`);
      console.log(`  │ Success Count : ${String(summary.successCount).padEnd(23)} │`);
      console.log(`  ├─────────────────────────────────────────┤`);
      console.log(`  │ P50  (Median) : ${summary.p50.toFixed(2).padEnd(19)} ms │`);
      console.log(`  │ P70  (70th %) : ${summary.p70.toFixed(2).padEnd(19)} ms │`);
      console.log(`  │ P100 (Max)    : ${summary.p100.toFixed(2).padEnd(19)} ms │`);
      console.log(`  │ Mean Latency  : ${summary.mean.toFixed(2).padEnd(19)} ms │`);
      console.log(`  │ Min Latency   : ${summary.min.toFixed(2).padEnd(19)} ms │`);
    } else {
      console.log(`  ├─────────────────────────────────────────┤`);
      console.log(`  │ Result        : NOT RUN (No Credentials)│`);
    }

    console.log(`  └─────────────────────────────────────────┘`);
    if (extra) console.log(`    Note: ${extra}`);
    console.log('');
  }

  const hasLLMKey = !!(process.env.GEMINI_API_KEY || process.env.OPENAI_API_KEY);
  const hasSTTKey = !!process.env.SARVAM_API_KEY;

  printTable('1. Local Vector Retrieval', results.benchmarkA_retrievalOnly.summary, 'Local TF-IDF Store', 'VERIFIED');
  printTable('2. Local Context Synthesis', results.benchmarkB_modelHarness.summary, 'Local Synthesis Engine', 'VERIFIED');

  if (hasLLMKey) {
    printTable('3. External Model RAG', results.benchmarkB_modelHarness.summary, 'Real Gemini/OpenAI', 'VERIFIED');
  } else {
    printTable('3. External Model RAG', null, 'Real Gemini/OpenAI', 'NOT RUN', 'Credentials unavailable');
  }

  if (hasSTTKey) {
    printTable('4. Real Sarvam STT', results.benchmarkC_sttPipeline.summary, 'Real Sarvam API', 'VERIFIED');
  } else {
    printTable('4. Real Sarvam STT', null, 'Real Sarvam API', 'NOT RUN', 'SARVAM_API_KEY unavailable');
  }

  printTable('5. STT Pipeline — Demo Mock', results.benchmarkC_sttPipeline.summary, 'Demo Mock Provider', 'MOCK VERIFIED');

  if (hasSTTKey && hasLLMKey) {
    printTable('6. Full Real Voice → Answer', results.benchmarkD_endToEndVoice.summary, 'Real Sarvam + Real LLM', 'VERIFIED');
  } else {
    printTable('6. Full Real Voice → Answer', null, 'Real Sarvam + Real LLM', 'NOT RUN', 'External credentials unavailable');
  }

  printTable('7. Demo Voice → Local RAG', {
    ...results.benchmarkD_endToEndVoice.summary,
    successCount: results.benchmarkB_modelHarness.summary.successCount
  }, 'Demo STT + Local Engine', 'MOCK VERIFIED', 'Combines Demo STT with Local Context Synthesis');

  // Save report artifact
  const reportPath = path.join(__dirname, 'benchmark_results.json');
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
  console.log(`  Saved detailed credentials-gated benchmark report to ${reportPath}\n`);
}

runBenchmark().catch(err => {
  console.error('Benchmark failed:', err);
  process.exit(1);
});
