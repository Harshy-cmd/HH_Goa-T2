/**
 * Multi-Strategy Chunking Pipeline — Voice RAG 2026
 *
 * Strategies:
 * 1. Structural chunking (headings, sections, paragraphs)
 * 2. Semantic chunking (similarity boundaries)
 * 3. Token-aware chunking (max token limits + overlap)
 * 4. Recursive fallback (paragraph → sentence → phrase → token)
 * 5. Metadata-aware (retains provenance)
 */

const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');

// ── Chunk Quality Checks ──
function isEmptyChunk(text) {
  return !text || text.trim().length < 10;
}

function isRepetitiveChunk(text) {
  const words = text.toLowerCase().split(/\s+/);
  if (words.length < 5) return false;
  const unique = new Set(words);
  return unique.size / words.length < 0.3;
}

function contentHash(text) {
  return crypto.createHash('sha256').update(text.trim().toLowerCase()).digest('hex').slice(0, 16);
}

// ── Sentence Splitter ──
function splitSentences(text) {
  // Split on sentence boundaries
  return text.split(/(?<=[.!?])\s+/).filter(s => s.trim().length > 0);
}

// ── Rough Token Count ──
function estimateTokens(text) {
  // Approximate: ~4 chars per token for English
  return Math.ceil(text.length / 4);
}

// ── Structural Chunker ──
class StructuralChunker {
  chunk(text, metadata = {}) {
    const chunks = [];
    const lines = text.split('\n');
    let currentSection = '';
    let currentHeading = metadata.title || 'Untitled';
    let currentSubheading = '';

    for (const line of lines) {
      const trimmed = line.trim();

      // Detect markdown headings
      const h1Match = trimmed.match(/^#\s+(.+)/);
      const h2Match = trimmed.match(/^##\s+(.+)/);
      const h3Match = trimmed.match(/^###\s+(.+)/);

      if (h1Match || h2Match || h3Match) {
        // Flush current section
        if (currentSection.trim()) {
          chunks.push({
            text: currentSection.trim(),
            section: currentHeading,
            subsection: currentSubheading,
            strategy: 'structural'
          });
          currentSection = '';
        }

        if (h1Match) {
          currentHeading = h1Match[1];
          currentSubheading = '';
        } else if (h2Match) {
          currentSubheading = h2Match[1];
        } else if (h3Match) {
          currentSubheading = h3Match[1];
        }
      } else if (trimmed === '' && currentSection.trim().length > 100) {
        // Paragraph boundary — flush if substantial
        chunks.push({
          text: currentSection.trim(),
          section: currentHeading,
          subsection: currentSubheading,
          strategy: 'structural'
        });
        currentSection = '';
      } else {
        currentSection += line + '\n';
      }
    }

    // Flush remaining
    if (currentSection.trim()) {
      chunks.push({
        text: currentSection.trim(),
        section: currentHeading,
        subsection: currentSubheading,
        strategy: 'structural'
      });
    }

    return chunks;
  }
}

// ── Semantic Chunker ──
class SemanticChunker {
  constructor(similarityThreshold = 0.3) {
    this.threshold = similarityThreshold;
  }

  chunk(text, metadata = {}) {
    const sentences = splitSentences(text);
    if (sentences.length <= 1) {
      return [{ text: text.trim(), strategy: 'semantic', section: metadata.section || '' }];
    }

    const chunks = [];
    let currentChunk = sentences[0];

    for (let i = 1; i < sentences.length; i++) {
      const similarity = this._jaccardSimilarity(currentChunk, sentences[i]);

      if (similarity < this.threshold && currentChunk.length > 50) {
        chunks.push({
          text: currentChunk.trim(),
          strategy: 'semantic',
          section: metadata.section || ''
        });
        currentChunk = sentences[i];
      } else {
        currentChunk += ' ' + sentences[i];
      }
    }

    if (currentChunk.trim()) {
      chunks.push({
        text: currentChunk.trim(),
        strategy: 'semantic',
        section: metadata.section || ''
      });
    }

    return chunks;
  }

  _jaccardSimilarity(a, b) {
    const setA = new Set(a.toLowerCase().split(/\s+/));
    const setB = new Set(b.toLowerCase().split(/\s+/));
    const intersection = new Set([...setA].filter(x => setB.has(x)));
    const union = new Set([...setA, ...setB]);
    return union.size > 0 ? intersection.size / union.size : 0;
  }
}

// ── Token-Aware Chunker ──
class TokenAwareChunker {
  constructor(maxTokens = 512, overlapTokens = 50) {
    this.maxTokens = maxTokens;
    this.overlapTokens = overlapTokens;
  }

  chunk(text, metadata = {}) {
    const tokens = estimateTokens(text);
    if (tokens <= this.maxTokens) {
      return [{ text: text.trim(), strategy: 'token_aware', section: metadata.section || '' }];
    }

    const chunks = [];
    const sentences = splitSentences(text);
    let currentChunk = '';
    let currentTokens = 0;

    for (const sentence of sentences) {
      const sentenceTokens = estimateTokens(sentence);

      if (currentTokens + sentenceTokens > this.maxTokens && currentChunk) {
        chunks.push({
          text: currentChunk.trim(),
          strategy: 'token_aware',
          tokenCount: currentTokens,
          section: metadata.section || ''
        });

        // Overlap: keep last part of chunk for context continuity
        const overlapText = this._getOverlap(currentChunk);
        currentChunk = overlapText + ' ' + sentence;
        currentTokens = estimateTokens(currentChunk);
      } else {
        currentChunk += (currentChunk ? ' ' : '') + sentence;
        currentTokens += sentenceTokens;
      }
    }

    if (currentChunk.trim()) {
      chunks.push({
        text: currentChunk.trim(),
        strategy: 'token_aware',
        tokenCount: currentTokens,
        section: metadata.section || ''
      });
    }

    return chunks;
  }

  _getOverlap(text) {
    const sentences = splitSentences(text);
    let overlap = '';
    let overlapTokens = 0;

    for (let i = sentences.length - 1; i >= 0; i--) {
      const sentTokens = estimateTokens(sentences[i]);
      if (overlapTokens + sentTokens > this.overlapTokens) break;
      overlap = sentences[i] + (overlap ? ' ' + overlap : '');
      overlapTokens += sentTokens;
    }

    return overlap;
  }
}

// ── Recursive Fallback Chunker ──
class RecursiveFallbackChunker {
  constructor(maxTokens = 512) {
    this.maxTokens = maxTokens;
  }

  chunk(text, metadata = {}) {
    return this._recursiveChunk(text, metadata, 0);
  }

  _recursiveChunk(text, metadata, level) {
    if (estimateTokens(text) <= this.maxTokens) {
      return [{
        text: text.trim(),
        strategy: 'recursive_fallback',
        fallbackLevel: level,
        section: metadata.section || ''
      }];
    }

    const separators = ['\n\n', '\n', '. ', ', ', ' '];
    const separator = separators[Math.min(level, separators.length - 1)];

    const parts = text.split(separator).filter(p => p.trim());
    if (parts.length <= 1 && level < separators.length - 1) {
      return this._recursiveChunk(text, metadata, level + 1);
    }

    const chunks = [];
    let current = '';

    for (const part of parts) {
      const combined = current ? current + separator + part : part;
      if (estimateTokens(combined) > this.maxTokens && current) {
        chunks.push(...this._recursiveChunk(current, metadata, level + 1));
        current = part;
      } else {
        current = combined;
      }
    }

    if (current.trim()) {
      if (estimateTokens(current) > this.maxTokens) {
        chunks.push(...this._recursiveChunk(current, metadata, level + 1));
      } else {
        chunks.push({
          text: current.trim(),
          strategy: 'recursive_fallback',
          fallbackLevel: level,
          section: metadata.section || ''
        });
      }
    }

    return chunks;
  }
}

// ── Main Chunking Pipeline ──
class ChunkingPipeline {
  constructor(options = {}) {
    this.maxTokens = options.maxTokens || parseInt(process.env.MAX_CHUNK_TOKENS) || 512;
    this.overlapTokens = options.overlapTokens || parseInt(process.env.CHUNK_OVERLAP_TOKENS) || 50;
    this.similarityThreshold = options.similarityThreshold || parseFloat(process.env.SIMILARITY_THRESHOLD) || 0.3;

    this.structural = new StructuralChunker();
    this.semantic = new SemanticChunker(this.similarityThreshold);
    this.tokenAware = new TokenAwareChunker(this.maxTokens, this.overlapTokens);
    this.recursive = new RecursiveFallbackChunker(this.maxTokens);
  }

  /**
   * Run the complete chunking pipeline on a document.
   * @param {string} text - Document text
   * @param {object} docMetadata - Document-level metadata
   * @returns {Array<object>} Enriched chunks with full metadata
   */
  process(text, docMetadata = {}) {
    if (!text || text.trim().length === 0) {
      return [];
    }

    const docId = docMetadata.id || uuidv4();
    const timestamp = new Date().toISOString();

    // Step 1: Structural chunking first
    let chunks = this.structural.chunk(text, docMetadata);

    // Step 2: Apply semantic chunking to large structural chunks
    let refined = [];
    for (const chunk of chunks) {
      if (estimateTokens(chunk.text) > this.maxTokens) {
        const semanticChunks = this.semantic.chunk(chunk.text, chunk);
        refined.push(...semanticChunks.map(sc => ({
          ...sc,
          section: chunk.section,
          subsection: chunk.subsection || sc.subsection
        })));
      } else {
        refined.push(chunk);
      }
    }

    // Step 3: Apply token-aware chunking to still-oversized chunks
    let tokenChecked = [];
    for (const chunk of refined) {
      if (estimateTokens(chunk.text) > this.maxTokens) {
        const tokenChunks = this.tokenAware.chunk(chunk.text, chunk);
        tokenChecked.push(...tokenChunks.map(tc => ({
          ...tc,
          section: chunk.section,
          subsection: chunk.subsection
        })));
      } else {
        tokenChecked.push(chunk);
      }
    }

    // Step 4: Recursive fallback for anything still oversized
    let finalChunks = [];
    for (const chunk of tokenChecked) {
      if (estimateTokens(chunk.text) > this.maxTokens) {
        finalChunks.push(...this.recursive.chunk(chunk.text, chunk));
      } else {
        finalChunks.push(chunk);
      }
    }

    // Step 5: Quality checks + metadata enrichment + deduplication
    const seenHashes = new Set();
    const enriched = [];

    for (let i = 0; i < finalChunks.length; i++) {
      const chunk = finalChunks[i];

      // Quality checks
      if (isEmptyChunk(chunk.text)) continue;
      if (isRepetitiveChunk(chunk.text)) continue;

      // Deduplication
      const hash = contentHash(chunk.text);
      if (seenHashes.has(hash)) continue;
      seenHashes.add(hash);

      // Enrich metadata
      const chunkId = uuidv4();
      enriched.push({
        id: chunkId,
        documentId: docId,
        source: docMetadata.source || docMetadata.filename || 'unknown',
        title: docMetadata.title || docMetadata.filename || 'Untitled',
        section: chunk.section || '',
        subsection: chunk.subsection || '',
        text: chunk.text,
        chunkIndex: i,
        parentId: docId,
        strategy: chunk.strategy || 'structural',
        tokenCount: estimateTokens(chunk.text),
        charCount: chunk.text.length,
        contentHash: hash,
        timestamp,
        version: 1
      });
    }

    return enriched;
  }
}

module.exports = {
  ChunkingPipeline,
  StructuralChunker,
  SemanticChunker,
  TokenAwareChunker,
  RecursiveFallbackChunker,
  estimateTokens,
  contentHash,
  isEmptyChunk,
  isRepetitiveChunk,
  splitSentences
};
