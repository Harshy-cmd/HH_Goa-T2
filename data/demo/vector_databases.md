# Vector Databases and Embedding Search

## What are Vector Databases?

A vector database is a specialized database designed to store, index, and query high-dimensional vector embeddings. Unlike traditional databases that work with structured rows and columns, vector databases operate on mathematical representations of data—vectors—that capture semantic meaning. These vectors are typically produced by machine learning models called embedding models.

## How Embeddings Work

Embeddings are dense numerical representations of data (text, images, audio) in a continuous vector space. The key property of embeddings is that semantically similar items are mapped to nearby points in the vector space. For text, this means that "dog" and "puppy" would have vectors that are close together, while "dog" and "microprocessor" would be far apart.

### Creating Embeddings

Text embeddings are typically created using transformer-based models such as:

- **Sentence Transformers**: Models like all-MiniLM-L6-v2 that produce 384-dimensional vectors.
- **OpenAI Embeddings**: Models like text-embedding-ada-002 that produce 1536-dimensional vectors.
- **Cohere Embed**: Models that produce embeddings optimized for search and classification.
- **Local TF-IDF**: A simpler but faster approach using term frequency-inverse document frequency weighting.

### Similarity Metrics

Common similarity metrics for comparing vectors include:

- **Cosine Similarity**: Measures the angle between two vectors. Most commonly used for text.
- **Dot Product**: Faster computation, equivalent to cosine similarity when vectors are normalized.
- **Euclidean Distance**: Measures straight-line distance between vector endpoints.

## Vector Retrieval Process

The vector retrieval process in a RAG system follows these steps:

1. **Ingestion**: Documents are split into chunks and each chunk is embedded into a vector.
2. **Indexing**: Vectors are stored in an index structure (e.g., HNSW, IVF) for efficient search.
3. **Query Embedding**: The user's query is embedded using the same model.
4. **Approximate Nearest Neighbors (ANN)**: The index finds the K nearest vectors to the query.
5. **Post-filtering**: Results are filtered by metadata (date, source, category).
6. **Reranking**: Optionally, a cross-encoder reranks the top candidates for better precision.

## Performance Considerations

For voice RAG applications with sub-200ms latency targets, key performance considerations include:

- **Pre-compute Embeddings**: Never embed documents at query time. Embed during ingestion.
- **Keep Index Warm**: Avoid cold starts by keeping the vector index in memory.
- **Small Top-K**: Retrieve a small number of candidates (5-10) to minimize processing time.
- **Local Storage**: Use in-process vector stores for demos to avoid network latency.
- **Batch Operations**: Embed and index documents in batches during ingestion.
- **Metadata Filtering**: Use metadata pre-filtering to reduce the search space before vector comparison.

## Popular Vector Databases

Common vector database options include:

- **Pinecone**: Managed cloud vector database with low-latency search.
- **Weaviate**: Open-source vector database with built-in vectorization.
- **Qdrant**: High-performance vector search engine.
- **ChromaDB**: Lightweight, developer-friendly embedding database.
- **FAISS**: Facebook's library for efficient similarity search (not a full database).
- **In-memory stores**: Custom implementations for demo and development environments.
