# Document Chunking Strategies

## Why Chunking Matters

Chunking is the process of splitting large documents into smaller, semantically meaningful segments for storage and retrieval. The quality of chunking directly impacts retrieval accuracy—poorly chunked documents lead to either incomplete context (chunks too small) or diluted relevance (chunks too large).

## Chunking Strategies

### 1. Structural Chunking

Structural chunking uses the document's inherent structure—headings, sections, paragraphs, lists—to determine split points. This is the most natural approach for well-formatted documents like markdown files, HTML pages, or structured reports.

Key advantages:
- Preserves the author's intended information grouping
- Respects topic boundaries
- Works well for documents with clear hierarchical structure

Limitations:
- Depends on consistent document formatting
- May produce very uneven chunk sizes
- Doesn't work well for unstructured text

### 2. Semantic Chunking

Semantic chunking uses the actual meaning of text to determine where to split. By computing embeddings for adjacent passages, the system can detect when the topic shifts significantly and place a boundary at that point.

The process works by:
1. Computing embeddings for each sentence or paragraph
2. Calculating similarity between adjacent segments
3. Placing split points where similarity drops below a threshold

This approach produces chunks that are topically coherent regardless of document formatting.

### 3. Token-Aware Chunking

Token-aware chunking enforces hard limits on chunk size measured in tokens (not characters). This ensures that no chunk exceeds the model's context window and that chunks are appropriately sized for embedding models.

Important considerations:
- Different models have different tokenizers (GPT, BERT, etc.)
- Chunks should typically be 256-512 tokens for retrieval
- Overlap between chunks preserves cross-boundary context
- Overlap is typically 10-20% of chunk size

### 4. Recursive Fallback Chunking

Recursive chunking uses a hierarchy of separators, trying the most natural split first and falling back to finer-grained splits when chunks are still too large:

1. Split by double newline (paragraph boundary)
2. Split by single newline (line boundary)
3. Split by sentence boundary (period, question mark, exclamation)
4. Split by phrase boundary (comma, semicolon)
5. Split by word boundary (space)
6. Split by character (last resort)

This ensures every chunk meets size requirements while preserving as much structure as possible.

## Overlap Handling

Overlap between adjacent chunks is crucial for preserving context that spans chunk boundaries. A typical overlap strategy:

- Overlap size: 50-100 tokens
- Overlap content: last N sentences of the previous chunk prepended to the next
- Deduplication: During retrieval, overlapping content is deduplicated to avoid redundant results

## Metadata Preservation

Each chunk should retain comprehensive metadata:

- **Document ID**: Links back to the original document
- **Source**: File name or URL of the original
- **Title**: Document or section title
- **Section/Subsection**: Hierarchical location within the document
- **Chunk Index**: Position within the document's chunk sequence
- **Parent ID**: Reference to the parent section or document
- **Strategy**: Which chunking strategy produced this chunk
- **Token Count**: Number of tokens in the chunk
- **Character Count**: Number of characters
- **Content Hash**: For deduplication
- **Timestamp**: When the chunk was created
- **Version**: For tracking updates

## Chunk Quality Checks

Not all chunks are useful. Quality checks should reject:

- Empty or near-empty chunks (under 10 characters)
- Extremely repetitive chunks (word diversity ratio below 0.3)
- Chunks containing only metadata or boilerplate
- Duplicate chunks (same content hash as existing chunk)
- Malformed chunks with corrupted or garbled text

## Parent-Child Retrieval

In parent-child retrieval, the system retrieves precise child chunks for ranking but expands to the parent section for generation context. This provides the best of both worlds:

- **Child chunks**: High precision for relevance scoring
- **Parent context**: Broader context for answer generation

The parent-child relationship is maintained through chunk IDs and parent IDs in the metadata.
