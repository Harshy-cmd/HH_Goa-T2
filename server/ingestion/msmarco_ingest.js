/**
 * MSMARCO-XI Ingestion Engine — HH Goa 2026 Task 2
 *
 * Implements:
 * 1. Passage extraction (English & Translated passages)
 * 2. SHA-256 Content Deduplication
 * 3. Multi-Strategy Chunking Pipeline integration
 * 4. Train / Validation Data Separation (No leakage into vector index)
 * 5. Metadata Enrichment (query_ids, language, passage_id, relevance)
 */

const crypto = require('crypto');
const path = require('path');
const fs = require('fs');

function contentHash(text) {
  return crypto.createHash('sha256').update(text.trim().toLowerCase()).digest('hex').slice(0, 16);
}

/**
 * Ingest MSMARCO-XI records into Vector Store & Evaluation Set
 * @param {Array<object>} records - Raw MSMARCO-XI records
 * @param {object} chunkingPipeline
 * @param {object} embeddingService
 * @param {object} vectorStore
 * @param {object} options - { isValidation: boolean, lang: string }
 */
async function ingestMSMARCORecords(records, chunkingPipeline, embeddingService, vectorStore, options = {}) {
  const isValidation = options.isValidation || false;
  const lang = options.lang || 'hi';

  const uniquePassages = new Map(); // hash -> passage object
  const valQueries = [];            // validation queries for evaluation

  for (const record of records) {
    const queryId = record.query_id || `q_${Math.random().toString(36).substr(2, 9)}`;
    const queryText = record.query || record.Eng_Query || '';
    const answerText = record.Answer || record.Eng_Answer || '';
    const passagesObj = record.passages || {};

    const engPassages = passagesObj.English_passages || [];
    const transPassages = passagesObj.Translated_passages || [];
    const isSelected = passagesObj.is_selected || [];

    const numPassages = Math.max(engPassages.length, transPassages.length);
    const selectedPassageHashes = [];

    for (let i = 0; i < numPassages; i++) {
      const engText = engPassages[i] || '';
      const transText = transPassages[i] || engText;
      const textToUse = transText.trim().length > 0 ? transText : engText;

      if (!textToUse || textToUse.length < 15) continue;

      const hash = contentHash(textToUse);
      const selected = isSelected[i] === 1;

      if (selected) {
        selectedPassageHashes.push(hash);
      }

      // If training data or new passage, index it
      if (!uniquePassages.has(hash)) {
        uniquePassages.set(hash, {
          passageId: `p_${hash}`,
          text: textToUse,
          englishText: engText,
          language: lang,
          queryIds: [queryId],
          isSelected: selected
        });
      } else {
        // Append query ID
        const existing = uniquePassages.get(hash);
        if (!existing.queryIds.includes(queryId)) {
          existing.queryIds.push(queryId);
        }
        if (selected) existing.isSelected = true;
      }
    }

    // Record evaluation query if validation split
    if (isValidation && queryText) {
      valQueries.push({
        queryId,
        query: queryText,
        answer: answerText,
        selectedHashes: selectedPassageHashes,
        language: lang
      });
    }
  }

  // If training mode, chunk and index unique passages into vector store
  let totalChunksCreated = 0;
  if (!isValidation) {
    const allChunks = [];
    for (const [hash, passage] of uniquePassages) {
      const docMetadata = {
        filename: `msmarco_${passage.passageId}.md`,
        title: `MSMARCO Passage ${passage.passageId}`,
        source: `MSMARCO-XI (${lang})`,
        passageId: passage.passageId,
        passageHash: hash,
        language: passage.language,
        queryIds: passage.queryIds,
        isSelected: passage.isSelected
      };

      const chunks = chunkingPipeline.process(passage.text, docMetadata);
      allChunks.push(...chunks);
    }

    if (allChunks.length > 0) {
      vectorStore.addChunks(allChunks);
      totalChunksCreated = allChunks.length;
    }
  }

  // Save validation queries if validation split
  if (isValidation && valQueries.length > 0) {
    const evalDir = path.join(__dirname, '..', '..', 'data', 'eval');
    if (!fs.existsSync(evalDir)) fs.mkdirSync(evalDir, { recursive: true });
    const evalFile = path.join(evalDir, `msmarco_val_${lang}.json`);
    fs.writeFileSync(evalFile, JSON.stringify(valQueries, null, 2));
  }

  return {
    recordsProcessed: records.length,
    uniquePassagesCount: uniquePassages.size,
    chunksCreated: totalChunksCreated,
    valQueriesCount: valQueries.length
  };
}

module.exports = { ingestMSMARCORecords, contentHash };
