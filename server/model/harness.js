/**
 * Model Harness / Orchestration — Voice RAG 2026
 *
 * Structured orchestration pipeline:
 * 1. Input validation
 * 2. Query normalization
 * 3. Off-topic classification
 * 4. Retrieval
 * 5. Context assembly
 * 6. Model generation (External LLM provider when API key available, else Local Context Synthesis)
 * 7. Bounded retries
 * 8. Output schema validation
 * 9. Grounding validation
 * 10. Citation validation
 * 11. Final response formatting & metrics
 */

const https = require('https');

class ModelHarness {
  constructor(vectorStore, embeddingService, guardrails) {
    this.vectorStore = vectorStore;
    this.embedding = embeddingService;
    this.guardrails = guardrails;
    this._maxRetries = 2;
    this._retryDelayMs = 200;

    this.geminiApiKey = process.env.GEMINI_API_KEY;
    this.openaiApiKey = process.env.OPENAI_API_KEY;
    this.httpsAgent = new https.Agent({ keepAlive: true, maxSockets: 20, keepAliveMsecs: 30000 });
  }

  /**
   * Execute the full RAG pipeline
   * @param {string} query - User query
   * @param {object} latencyTracker - Optional latency tracker
   * @returns {Promise<object>} Structured response
   */
  async execute(query, latencyTracker = null) {
    const timings = {};
    const timer = (name) => latencyTracker ? latencyTracker.start(name) : { stop: () => {}, elapsed: () => 0 };

    // 1. Input validation
    const t1 = timer('input_validation');
    const validationResult = this._validateInput(query);
    t1.stop();
    timings.input_validation = t1.elapsed();

    if (!validationResult.valid) {
      return this._formatResponse({
        answer: validationResult.error,
        grounded: false,
        sources: [],
        refused: true,
        refusal_reason: validationResult.error
      }, timings);
    }

    // 2. Query normalization
    const t2 = timer('normalization');
    const normalizedQuery = this._normalizeQuery(query);
    t2.stop();
    timings.normalization = t2.elapsed();

    // 3. Off-topic classification
    const t3 = timer('offtopic_check');
    const offTopicResult = this.guardrails.checkOffTopic(normalizedQuery);
    t3.stop();
    timings.offtopic_check = t3.elapsed();

    if (offTopicResult.isOffTopic) {
      return this._formatResponse({
        answer: offTopicResult.message,
        grounded: false,
        sources: [],
        refused: true,
        refusal_reason: offTopicResult.message
      }, timings);
    }

    // 3b. Safety check
    const t3b = timer('safety_check');
    const safetyResult = this.guardrails.checkSafety(normalizedQuery);
    t3b.stop();
    timings.safety_check = t3b.elapsed();

    if (!safetyResult.safe) {
      return this._formatResponse({
        answer: safetyResult.message,
        grounded: false,
        sources: [],
        refused: true,
        refusal_reason: safetyResult.message
      }, timings);
    }

    // 4. Retrieval
    const t4 = timer('retrieval');
    const searchResults = this.vectorStore.search(normalizedQuery, { topK: 5 });
    t4.stop();
    timings.retrieval = t4.elapsed();

    // 4b. Retrieval-empty guardrail
    if (searchResults.length === 0) {
      return this._formatResponse({
        answer: 'I don\'t have enough relevant information to answer that question. Try uploading documents related to your query.',
        grounded: false,
        sources: [],
        refused: false
      }, timings);
    }

    // 5. Context assembly
    const t5 = timer('context_assembly');
    const context = this._assembleContext(searchResults);
    t5.stop();
    timings.context_assembly = t5.elapsed();

    // 6 & 7. Generation with retry
    let generationResult = null;
    let lastError = null;

    for (let attempt = 0; attempt <= this._maxRetries; attempt++) {
      try {
        const t7 = timer('generation');
        generationResult = await this._generate(normalizedQuery, context, searchResults);
        t7.stop();
        timings.generation = t7.elapsed();
        break;
      } catch (err) {
        lastError = err;
        if (attempt < this._maxRetries) {
          const delay = this._retryDelayMs * Math.pow(2, attempt);
          await new Promise(r => setTimeout(r, delay));
        }
      }
    }

    if (!generationResult) {
      // Fallback: return degraded response
      return this._formatResponse({
        answer: 'I found relevant information but was unable to generate a complete answer. Here are the most relevant sources.',
        grounded: false,
        sources: searchResults.map(r => ({
          id: r.chunk.id,
          title: r.chunk.title || r.chunk.source,
          relevance: r.score,
          section: r.chunk.section
        })),
        refused: false,
        degraded: true
      }, timings);
    }

    // 8. Output schema validation
    const t8 = timer('output_validation');
    const schemaValid = this._validateOutput(generationResult);
    t8.stop();
    timings.output_validation = t8.elapsed();

    if (!schemaValid.valid) {
      return this._formatResponse({
        answer: generationResult.answer || 'An error occurred while formatting the response.',
        grounded: false,
        sources: [],
        refused: false,
        degraded: true
      }, timings);
    }

    // 9. Grounding validation
    const t9 = timer('grounding_check');
    const groundingResult = this.guardrails.checkGrounding(generationResult.answer, context);
    t9.stop();
    timings.grounding_check = t9.elapsed();

    // 10. Citation validation
    const t10 = timer('citation_check');
    const citationValid = this.guardrails.validateCitations(generationResult.sources, searchResults);
    t10.stop();
    timings.citation_check = t10.elapsed();

    // 11. Final formatting
    return this._formatResponse({
      ...generationResult,
      grounded: groundingResult.grounded,
      sources: citationValid.validSources
    }, timings);
  }

  // ── Step implementations ──

  _validateInput(query) {
    if (!query || typeof query !== 'string') {
      return { valid: false, error: 'Invalid query: must be a non-empty string.' };
    }
    if (query.trim().length < 2) {
      return { valid: false, error: 'Query too short. Please provide a more specific question.' };
    }
    if (query.length > 1000) {
      return { valid: false, error: 'Query too long. Please keep your question under 1000 characters.' };
    }
    return { valid: true };
  }

  _normalizeQuery(query) {
    return query
      .trim()
      .replace(/\s+/g, ' ')
      .replace(/[""]/g, '"')
      .replace(/['']/g, "'");
  }

  _assembleContext(searchResults) {
    return searchResults
      .slice(0, 3)
      .map(r => {
        const meta = `[Source: ${r.chunk.title || r.chunk.source} | Section: ${r.chunk.section || 'Main'}]`;
        return `${meta}\n${r.chunk.text}`;
      })
      .join('\n\n---\n\n');
  }

  async _generate(query, context, searchResults) {
    // 1. Check if Google Gemini API key is configured
    if (this.geminiApiKey) {
      for (let gAttempt = 1; gAttempt <= 2; gAttempt++) {
        try {
          const geminiAnswer = await this._callGeminiAPI(query, context);
          if (geminiAnswer) {
            return {
              answer: geminiAnswer,
              grounded: true,
              sources: searchResults.map(r => ({
                id: r.chunk.id,
                title: r.chunk.title || r.chunk.source,
                relevance: r.score,
                section: r.chunk.section
              })),
              provider: 'google-gemini',
              fallback: false
            };
          }
        } catch (err) {
          console.warn(`[ModelHarness] Gemini API call attempt ${gAttempt} failed:`, err.message);
          if (gAttempt < 2) await new Promise(r => setTimeout(r, 1000));
        }
      }
    }

    // 2. Check if OpenAI API key is configured
    if (this.openaiApiKey) {
      try {
        const openaiAnswer = await this._callOpenAIAPI(query, context);
        if (openaiAnswer) {
          return {
            answer: openaiAnswer,
            grounded: true,
            sources: searchResults.map(r => ({
              id: r.chunk.id,
              title: r.chunk.title || r.chunk.source,
              relevance: r.score,
              section: r.chunk.section
            })),
            provider: 'openai',
            fallback: false
          };
        }
      } catch (err) {
        console.warn('[ModelHarness] OpenAI API call failed, falling back to local context synthesis:', err.message);
      }
    }

    // 3. Fallback / Default: Local Context Synthesis Engine
    const answer = this._extractAnswer(query, context, searchResults);

    return {
      answer,
      grounded: true,
      sources: searchResults.map(r => ({
        id: r.chunk.id,
        title: r.chunk.title || r.chunk.source,
        relevance: r.score,
        section: r.chunk.section
      })),
      provider: 'local-context-synthesis',
      fallback: !!(this.geminiApiKey || this.openaiApiKey),
      refusal_reason: null
    };
  }

  _callGeminiAPI(query, context) {
    return new Promise((resolve, reject) => {
      const prompt = `System: You are a Voice RAG assistant. Answer the user question based ONLY on the provided context. Be concise.\n\nContext:\n${context}\n\nUser Question: ${query}`;
      const payload = JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { maxOutputTokens: 256 }
      });

      const modelName = process.env.GEMINI_MODEL || 'gemini-3.5-flash-lite';
      const req = https.request({
        hostname: 'generativelanguage.googleapis.com',
        path: `/v1beta/models/${modelName}:generateContent?key=${this.geminiApiKey}`,
        method: 'POST',
        agent: this.httpsAgent,
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(payload)
        }
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const json = JSON.parse(data);
            const answer = json.candidates?.[0]?.content?.parts?.[0]?.text;
            resolve(answer || null);
          } catch (e) {
            reject(e);
          }
        });
      });

      req.setTimeout(20000, () => {
        req.destroy();
        reject(new Error('Gemini API timeout (20s)'));
      });

      req.on('error', reject);
      req.write(payload);
      req.end();
    });
  }

  _callOpenAIAPI(query, context) {
    return new Promise((resolve, reject) => {
      const payload = JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: 'You are a Voice RAG assistant. Answer based ONLY on the provided context.' },
          { role: 'user', content: `Context:\n${context}\n\nQuestion: ${query}` }
        ]
      });

      const req = https.request({
        hostname: 'api.openai.com',
        path: '/v1/chat/completions',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.openaiApiKey}`,
          'Content-Length': Buffer.byteLength(payload)
        }
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const json = JSON.parse(data);
            const answer = json.choices?.[0]?.message?.content;
            resolve(answer || null);
          } catch (e) {
            reject(e);
          }
        });
      });

      req.on('error', reject);
      req.write(payload);
      req.end();
    });
  }

  _extractAnswer(query, context, searchResults) {
    // Extract and synthesize answer from retrieved chunks
    const topChunks = searchResults.slice(0, 3);
    const queryWords = query.toLowerCase().split(/\s+/).filter(w => w.length > 2);

    // Find sentences most relevant to the query
    const allSentences = [];
    for (const result of topChunks) {
      const sentences = result.chunk.text.split(/(?<=[.!?])\s+/);
      for (const sentence of sentences) {
        const lowerSentence = sentence.toLowerCase();
        const relevanceScore = queryWords.filter(w => lowerSentence.includes(w)).length;
        allSentences.push({ text: sentence.trim(), score: relevanceScore, source: result.chunk });
      }
    }

    // Sort by relevance
    allSentences.sort((a, b) => b.score - a.score);

    // Take top sentences that answer the query
    const answerSentences = allSentences
      .filter(s => s.score > 0 && s.text.length > 20)
      .slice(0, 5)
      .map(s => s.text);

    if (answerSentences.length === 0) {
      // Fallback: return the most relevant chunk text
      return topChunks[0]?.chunk.text.split(/(?<=[.!?])\s+/).slice(0, 3).join(' ') ||
        'The available context does not contain a direct answer to your question.';
    }

    return answerSentences.join(' ');
  }

  _validateOutput(result) {
    if (!result || typeof result !== 'object') {
      return { valid: false, error: 'Output is not an object' };
    }
    if (typeof result.answer !== 'string') {
      return { valid: false, error: 'Missing answer string' };
    }
    if (typeof result.grounded !== 'boolean') {
      return { valid: false, error: 'Missing grounded boolean' };
    }
    if (!Array.isArray(result.sources)) {
      return { valid: false, error: 'Missing sources array' };
    }
    for (const src of result.sources) {
      if (!src.id || typeof src.id !== 'string') {
        return { valid: false, error: 'Source missing valid id' };
      }
    }
    return { valid: true };
  }

  _formatResponse(result, timings) {
    return {
      answer: result.answer,
      grounded: result.grounded || false,
      sources: result.sources || [],
      refused: result.refused || false,
      refusal_reason: result.refusal_reason || null,
      degraded: result.degraded || false,
      provider: result.provider || 'local-context-synthesis',
      fallback: result.fallback || false,
      latency: timings
    };
  }
}

module.exports = { ModelHarness };
