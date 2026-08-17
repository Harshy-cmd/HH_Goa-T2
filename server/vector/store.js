/**
 * In-Memory Vector Store — Voice RAG 2026
 * Low-latency local vector store with metadata filtering.
 */

const { EmbeddingService } = require('../embedding/service');

class VectorStore {
  constructor(embeddingService) {
    this.embedding = embeddingService;
    this._chunks = [];      // Array of chunk objects with embeddings
    this._topK = parseInt(process.env.TOP_K) || 5;
    this._similarityThreshold = parseFloat(process.env.SIMILARITY_THRESHOLD) || 0.05;
  }

  /**
   * Add chunks to the store with pre-computed embeddings
   * @param {Array<object>} chunks - Enriched chunks from chunking pipeline
   */
  addChunks(chunks) {
    // Build/rebuild vocabulary with all texts
    const allTexts = [...this._chunks.map(c => c.text), ...chunks.map(c => c.text)];
    this.embedding.buildVocabulary(allTexts);

    // Compute embeddings for new chunks
    for (const chunk of chunks) {
      const embedding = this.embedding.embed(chunk.text);
      this._chunks.push({
        ...chunk,
        embedding
      });
    }

    // Re-compute all embeddings with updated vocabulary
    for (const chunk of this._chunks) {
      chunk.embedding = this.embedding.embed(chunk.text);
    }
  }

  /**
   * Search for similar chunks
   * @param {string} query
   * @param {object} options - { topK, filter }
   * @returns {Array<{chunk: object, score: number}>}
   */
  search(query, options = {}) {
    const topK = options.topK || this._topK;

    if (this._chunks.length === 0) {
      return [];
    }

    // Embed query
    const queryVec = this.embedding.embed(query);

    // Compute similarities
    let results = this._chunks.map(chunk => ({
      chunk,
      score: EmbeddingService.cosineSimilarity(queryVec, chunk.embedding)
    }));

    // Apply metadata filter if provided
    if (options.filter) {
      results = results.filter(r => {
        for (const [key, value] of Object.entries(options.filter)) {
          if (r.chunk[key] !== value) return false;
        }
        return true;
      });
    }

    // Sort by score descending
    results.sort((a, b) => b.score - a.score);

    // Apply threshold and take top K
    results = results
      .filter(r => r.score >= this._similarityThreshold)
      .slice(0, topK);

    // Deduplicate near-identical results
    const deduped = [];
    const seenHashes = new Set();

    for (const result of results) {
      if (!seenHashes.has(result.chunk.contentHash)) {
        seenHashes.add(result.chunk.contentHash);
        deduped.push(result);
      }
    }

    return deduped;
  }

  /**
   * Get neighboring chunks for context expansion
   * @param {string} chunkId
   * @param {number} windowSize - Number of neighbors on each side
   * @returns {Array<object>}
   */
  getNeighbors(chunkId, windowSize = 1) {
    const idx = this._chunks.findIndex(c => c.id === chunkId);
    if (idx === -1) return [];

    const start = Math.max(0, idx - windowSize);
    const end = Math.min(this._chunks.length - 1, idx + windowSize);

    // Only return neighbors from the same document
    const docId = this._chunks[idx].documentId;
    return this._chunks
      .slice(start, end + 1)
      .filter(c => c.documentId === docId);
  }

  /**
   * Get parent context (document-level)
   * @param {string} documentId
   * @returns {Array<object>}
   */
  getDocumentChunks(documentId) {
    return this._chunks.filter(c => c.documentId === documentId);
  }

  /**
   * Get store statistics
   */
  getStats() {
    const documents = new Set(this._chunks.map(c => c.documentId));
    const strategies = {};
    for (const chunk of this._chunks) {
      strategies[chunk.strategy] = (strategies[chunk.strategy] || 0) + 1;
    }

    return {
      totalChunks: this._chunks.length,
      totalDocuments: documents.size,
      strategies,
      vocabularySize: this.embedding.vocabSize
    };
  }

  /**
   * Clear all data
   */
  clear() {
    this._chunks = [];
  }
}

module.exports = { VectorStore };
