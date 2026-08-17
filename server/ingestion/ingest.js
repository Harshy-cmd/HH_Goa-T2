/**
 * Document Ingestion — Voice RAG 2026
 * Handles document processing from upload to indexed chunks.
 */

async function ingestDocument(content, filename, chunkingPipeline, embeddingService, vectorStore) {
  if (!content || content.trim().length === 0) {
    throw new Error('Document is empty.');
  }

  // Detect document title from content
  const lines = content.split('\n');
  let title = filename;
  for (const line of lines.slice(0, 5)) {
    const trimmed = line.trim();
    if (trimmed.startsWith('# ')) {
      title = trimmed.replace(/^#+\s*/, '');
      break;
    }
    if (trimmed.length > 5 && !trimmed.startsWith('```') && !trimmed.startsWith('---')) {
      title = trimmed.slice(0, 80);
      break;
    }
  }

  const docMetadata = {
    filename,
    title,
    source: filename,
    ingestedAt: new Date().toISOString()
  };

  // Run chunking pipeline
  const chunks = chunkingPipeline.process(content, docMetadata);

  if (chunks.length === 0) {
    throw new Error('No valid chunks were produced from this document.');
  }

  // Index chunks in vector store
  vectorStore.addChunks(chunks);

  // Collect strategy statistics
  const strategies = {};
  for (const chunk of chunks) {
    strategies[chunk.strategy] = (strategies[chunk.strategy] || 0) + 1;
  }

  return {
    chunksCreated: chunks.length,
    strategies,
    title,
    documentId: chunks[0]?.documentId
  };
}

module.exports = { ingestDocument };
