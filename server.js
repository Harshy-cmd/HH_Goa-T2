/**
 * Voice RAG 2026 — Main Server
 * Express server serving the frontend and RAG API endpoints.
 */
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const multer = require('multer');

// Server modules
const { createSTTProvider } = require('./server/stt/provider');
const { ChunkingPipeline } = require('./server/chunking/pipeline');
const { VectorStore } = require('./server/vector/store');
const { EmbeddingService } = require('./server/embedding/service');
const { ModelHarness } = require('./server/model/harness');
const { Guardrails } = require('./server/guardrails/guardrails');
const { LatencyTracker } = require('./server/perf/latency');
const { BenchmarkRunner } = require('./server/perf/benchmark');
const { ingestDocument } = require('./server/ingestion/ingest');

const app = express();
const PORT = process.env.PORT || 3000;

// ── Middleware ──
app.use(cors());
app.use(express.json({ limit: '1mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// File upload config
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB
  fileFilter: (req, file, cb) => {
    const allowedExts = ['.txt', '.md', '.json', '.csv', '.wav', '.webm', '.mp4', '.ogg', '.m4a', '.aac'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowedExts.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error(`Unsupported file type: ${ext}`));
    }
  }
});

// ── Initialize services ──
const sttProvider = createSTTProvider('sarvam');
const embeddingService = new EmbeddingService();
const vectorStore = new VectorStore(embeddingService);
const chunkingPipeline = new ChunkingPipeline();
const guardrails = new Guardrails();
const modelHarness = new ModelHarness(vectorStore, embeddingService, guardrails);
const latencyTracker = new LatencyTracker();
const benchmarkRunner = new BenchmarkRunner(modelHarness, latencyTracker);

// ── API Routes ──

// Health check
app.get('/api/health', (req, res) => {
  const hasApiKey = !!process.env.SARVAM_API_KEY && process.env.SARVAM_API_KEY !== 'your_sarvam_api_key_here';
  const hasGeminiKey = !!process.env.GEMINI_API_KEY && process.env.GEMINI_API_KEY !== 'your_gemini_api_key_here';

  res.json({
    status: 'ok',
    services: {
      stt: hasApiKey ? 'configured' : 'missing_key',
      llm: hasGeminiKey ? 'configured' : 'missing_key',
      vectorStore: vectorStore.getStats(),
      embedding: 'ready'
    },
    timestamp: Date.now()
  });
});

// Speech-to-Text
app.post('/api/transcribe', upload.single('audio'), async (req, res) => {
  const timer = latencyTracker.start('stt');
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No audio file provided.' });
    }

    const result = await sttProvider.transcribe(req.file.buffer, {
      mimeType: req.file.mimetype
    });

    timer.stop();

    if (!result.transcript || result.transcript.trim() === '') {
      return res.json({ transcript: '', warning: 'No speech detected.' });
    }

    res.json({
      transcript: result.transcript,
      language: result.language || 'en',
      latency: timer.elapsed()
    });
  } catch (err) {
    timer.stop();
    console.error('[STT] Error:', err.message);
    res.status(500).json({ error: `Transcription failed: ${err.message}` });
  }
});

// RAG Query
app.post('/api/query', async (req, res) => {
  const pipelineTimer = latencyTracker.start('pipeline');
  try {
    const { query } = req.body;
    if (!query || typeof query !== 'string' || query.trim() === '') {
      return res.status(400).json({ error: 'Query is required.' });
    }

    // Sanitize input (basic XSS prevention)
    const sanitizedQuery = query.trim().slice(0, 1000);

    const result = await modelHarness.execute(sanitizedQuery, latencyTracker);
    pipelineTimer.stop();

    // Add total pipeline latency
    result.latency = result.latency || {};
    result.latency.total = pipelineTimer.elapsed();

    res.json(result);
  } catch (err) {
    pipelineTimer.stop();
    console.error('[Query] Error:', err.message);
    res.status(500).json({
      error: `Query failed: ${err.message}`,
      answer: 'An error occurred while processing your question.',
      grounded: false,
      sources: [],
      refused: false
    });
  }
});

// Document Upload
app.post('/api/upload', upload.single('document'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file provided.' });
    }

    const content = req.file.buffer.toString('utf-8');
    const filename = req.file.originalname;

    const result = await ingestDocument(content, filename, chunkingPipeline, embeddingService, vectorStore);

    res.json({
      success: true,
      filename,
      chunksCreated: result.chunksCreated,
      strategies: result.strategies
    });
  } catch (err) {
    console.error('[Upload] Error:', err.message);
    res.status(500).json({ error: `Upload failed: ${err.message}` });
  }
});

// Benchmark endpoint
app.get('/api/benchmark', async (req, res) => {
  try {
    const results = await benchmarkRunner.run();
    res.json(results);
  } catch (err) {
    console.error('[Benchmark] Error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// Latency stats endpoint
app.get('/api/latency', (req, res) => {
  res.json(latencyTracker.getStats());
});

// ── Error handling middleware ──
app.use((err, req, res, next) => {
  console.error('[Server] Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error.' });
});

// ── Load demo data on startup ──
async function loadDemoData() {
  try {
    const fs = require('fs');
    const demoDir = path.join(__dirname, 'data', 'demo');
    if (fs.existsSync(demoDir)) {
      const files = fs.readdirSync(demoDir);
      for (const file of files) {
        const content = fs.readFileSync(path.join(demoDir, file), 'utf-8');
        await ingestDocument(content, file, chunkingPipeline, embeddingService, vectorStore);
        console.log(`[Demo] Loaded: ${file}`);
      }
    }
    console.log(`[VectorStore] ${vectorStore.getStats().totalChunks} chunks indexed.`);
  } catch (err) {
    console.error('[Demo] Error loading demo data:', err.message);
  }
}

// ── Start server ──
app.listen(PORT, async () => {
  console.log(`\n  🎙️  Voice RAG 2026`);
  console.log(`  Server running at http://localhost:${PORT}`);
  console.log(`  STT Provider: Sarvam`);
  console.log(`  Embedding: Local TF-IDF`);
  console.log(`  Vector Store: In-Memory\n`);
  await loadDemoData();
});

module.exports = app;
