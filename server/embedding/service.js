/**
 * Embedding Service — Voice RAG 2026
 * Local TF-IDF based embedding for low-latency operation.
 * Can be extended with external embedding providers.
 */

class EmbeddingService {
  constructor() {
    this._vocabulary = new Map(); // word -> index
    this._idf = new Map(); // word -> IDF score
    this._docCount = 0;
    this._dimSize = 300; // Embedding dimension (trimmed)
    this._initialized = false;
  }

  /**
   * Build vocabulary and IDF scores from a corpus of texts
   * @param {string[]} texts
   */
  buildVocabulary(texts) {
    this._docCount = texts.length;
    const docFreq = new Map();

    for (const text of texts) {
      const words = this._tokenize(text);
      const uniqueWords = new Set(words);
      for (const word of uniqueWords) {
        docFreq.set(word, (docFreq.get(word) || 0) + 1);
      }
    }

    // Build vocabulary from most common words
    const sorted = [...docFreq.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, this._dimSize);

    this._vocabulary.clear();
    this._idf.clear();

    sorted.forEach(([word, freq], index) => {
      this._vocabulary.set(word, index);
      this._idf.set(word, Math.log((this._docCount + 1) / (freq + 1)) + 1);
    });

    this._initialized = true;
  }

  /**
   * Embed a single text into a vector
   * @param {string} text
   * @returns {number[]} Normalized embedding vector
   */
  embed(text) {
    const vector = new Float32Array(this._dimSize);
    const words = this._tokenize(text);
    const tf = new Map();

    // Term frequency
    for (const word of words) {
      tf.set(word, (tf.get(word) || 0) + 1);
    }

    // TF-IDF vector
    for (const [word, count] of tf) {
      const idx = this._vocabulary.get(word);
      if (idx !== undefined) {
        const idf = this._idf.get(word) || 1;
        vector[idx] = (count / words.length) * idf;
      }
    }

    // L2 normalize
    let norm = 0;
    for (let i = 0; i < vector.length; i++) {
      norm += vector[i] * vector[i];
    }
    norm = Math.sqrt(norm);
    if (norm > 0) {
      for (let i = 0; i < vector.length; i++) {
        vector[i] /= norm;
      }
    }

    return Array.from(vector);
  }

  /**
   * Embed multiple texts
   * @param {string[]} texts
   * @returns {number[][]}
   */
  embedBatch(texts) {
    return texts.map(t => this.embed(t));
  }

  /**
   * Compute cosine similarity between two vectors
   * @param {number[]} a
   * @param {number[]} b
   * @returns {number} Similarity score [0, 1]
   */
  static cosineSimilarity(a, b) {
    let dot = 0, normA = 0, normB = 0;
    const len = Math.min(a.length, b.length);
    for (let i = 0; i < len; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    const denom = Math.sqrt(normA) * Math.sqrt(normB);
    return denom > 0 ? dot / denom : 0;
  }

  _tokenize(text) {
    return text
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s]/gu, ' ')
      .split(/\s+/)
      .filter(w => w.length > 0);
  }

  get isInitialized() {
    return this._initialized;
  }

  get vocabSize() {
    return this._vocabulary.size;
  }
}

module.exports = { EmbeddingService };
