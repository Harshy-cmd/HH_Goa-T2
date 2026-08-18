"""AI and Machine Learning Domain Knowledge Generator.
Comprehensive coverage of AI, ML paradigms, Deep Learning, Transformers, NLP, Vector Search, FAISS, RAG, Speech.
"""
from __future__ import annotations

def get_ai_ml_documents() -> list[dict]:
    data = [
        ("ai-fundamentals", "Artificial Intelligence (AI) Foundations", "ai_foundations",
         "Artificial Intelligence (AI) is the subfield of computer science dedicated to building computational systems capable of performing cognitive tasks that traditionally require human intelligence. These tasks include visual perception, speech recognition, reasoning, natural language understanding, planning, problem-solving, and decision-making."),
        ("ai-machine-learning", "Machine Learning Paradigms and Concepts", "machine_learning",
         "Machine Learning (ML) is a branch of artificial intelligence focused on algorithms that learn patterns and predictive models directly from data without being explicitly programmed with static rules. The three primary learning paradigms are Supervised Learning (labeled input-output pairs), Unsupervised Learning (discovering latent patterns in unlabeled data), and Reinforcement Learning (learning optimal decision policies via reward feedback)."),
        ("ai-supervised-learning", "Supervised Learning Algorithms (Classification and Regression)", "machine_learning",
         "Supervised learning trains models on labeled datasets consisting of input features and corresponding ground-truth targets. For continuous numerical targets, regression algorithms (Linear Regression, Polynomial Regression, Ridge, Lasso) predict continuous values. For discrete categorical targets, classification algorithms (Logistic Regression, Support Vector Machines, Decision Trees, Random Forests) predict discrete class labels."),
        ("ai-unsupervised-learning", "Unsupervised Learning and Clustering", "machine_learning",
         "Unsupervised learning analyzes unlabeled datasets to identify hidden structures, clusters, and representations. Clustering algorithms like K-Means partition data into k distinct clusters by minimizing intra-cluster variance, while DBSCAN groups points based on density. Dimensionality reduction techniques like Principal Component Analysis (PCA) and t-SNE project high-dimensional data onto lower-dimensional manifolds."),
        ("ai-reinforcement-learning", "Reinforcement Learning (RL) and Markov Decision Processes", "machine_learning",
         "Reinforcement Learning (RL) trains autonomous agents to make sequences of decisions by interacting with an environment to maximize cumulative reward. Formulated mathematically as Markov Decision Processes (MDPs), RL algorithms include Q-Learning, Deep Q-Networks (DQN), Policy Gradients, and Proximal Policy Optimization (PPO), widely used in robotics, gaming, and RLHF for LLMs."),
        ("ai-neural-networks", "Artificial Neural Networks and Deep Learning", "deep_learning",
         "Deep Learning is a subset of machine learning based on Artificial Neural Networks with multiple hidden layers. Input features propagate forward through linear matrix multiplications and non-linear activation functions (ReLU, GELU, Sigmoid). Training minimizes a loss function using gradient descent optimization (Adam, SGD) and backpropagation via the calculus chain rule."),
        ("ai-cnn", "Convolutional Neural Networks (CNNs)", "deep_learning",
         "Convolutional Neural Networks (CNNs) are specialized deep learning architectures designed for grid-structured data like images. CNNs apply learnable spatial filters (convolutional kernels) to extract translation-invariant visual features (edges, textures, object parts), followed by pooling layers for downsampling and fully connected layers for final classification."),
        ("ai-rnn-lstm", "Recurrent Neural Networks (RNNs) and LSTMs", "deep_learning",
         "Recurrent Neural Networks (RNNs) process sequential data by maintaining internal hidden state vectors across time steps. Long Short-Term Memory (LSTM) networks and Gated Recurrent Units (GRUs) introduce specialized gating mechanisms (input, forget, output gates) that mitigate the vanishing gradient problem, allowing networks to capture long-range temporal dependencies."),
        ("ai-transformers", "The Transformer Architecture and Self-Attention", "transformers",
         "The Transformer architecture, introduced by Vaswani et al. in 'Attention Is All You Need', replaces recurrent connections entirely with multi-head self-attention mechanisms. Self-attention computes dynamic attention weights between all pairs of tokens in parallel using Query (Q), Key (K), and Value (V) matrices with Scaled Dot-Product Attention: Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) * V."),
        ("ai-nlp-embeddings", "Natural Language Processing (NLP) and Word Embeddings", "nlp",
         "Natural Language Processing (NLP) enables computers to process, understand, and generate human languages. Tokenization converts text into discrete subword units (Byte-Pair Encoding, WordPiece). Dense word and sentence embeddings (such as Word2Vec, GloVe, BERT, and E5) map linguistic units into continuous geometric vector spaces where semantic similarity corresponds to geometric proximity."),
        ("ai-vector-search", "Vector Search and Dense Semantic Retrieval", "information_retrieval",
         "Vector search (dense retrieval) searches high-dimensional vector spaces for the nearest neighbors to a query vector using distance metrics such as Cosine Similarity, Euclidean Distance (L2), or Normalized Inner Product. Dense retrieval captures semantic intent, synonyms, and multilingual equivalence that traditional keyword matching misses."),
        ("ai-faiss", "FAISS (Facebook AI Similarity Search)", "information_retrieval",
         "FAISS is an open-source library developed by Meta AI optimized for billion-scale similarity search and dense vector clustering. Written in highly optimized C++ with Python bindings and GPU acceleration, FAISS supports exact flat indexes (IndexFlatIP, IndexFlatL2) and approximate nearest neighbor (ANN) indexes like Inverted File (IVFFlat) and Hierarchical Navigable Small World (HNSW) graphs."),
        ("ai-bm25", "BM25 (Best Matching 25) Lexical Retrieval", "information_retrieval",
         "BM25 is a probabilistic lexical ranking function used in information retrieval search engines. Evolving from TF-IDF, BM25 scores document relevance based on term frequencies with non-linear saturation parameters (k1) and document length normalization (b), providing robust exact keyword search resistant to vocabulary mismatch."),
        ("ai-hybrid-rrf", "Hybrid Search and Reciprocal Rank Fusion (RRF)", "information_retrieval",
         "Hybrid search combines the strengths of dense semantic vector retrieval (FAISS) and sparse lexical keyword retrieval (BM25). Reciprocal Rank Fusion (RRF) merges ranked candidate lists into a single consolidated ranking using the formula RRF_Score(d) = sum(1 / (k + rank_i(d))), where k is a smoothing constant (typically 60), eliminating the need for delicate score calibration."),
        ("ai-reranking", "Two-Stage Retrieval and Cross-Encoder Reranking", "information_retrieval",
         "In modern search pipelines, two-stage retrieval first retrieves a broad set of candidate passages using fast bi-encoder/BM25 retrieval, then applies a high-capacity cross-encoder reranker. Cross-encoders process query and passage jointly through transformer self-attention layers, computing fine-grained token-level cross-interactions for superior ranking precision."),
        ("ai-rag", "Retrieval-Augmented Generation (RAG)", "rag",
         "Retrieval-Augmented Generation (RAG) is an architectural framework that enhances Large Language Models (LLMs) by retrieving relevant factual documents from external knowledge indexes to ground LLM prompt contexts. RAG mitigates hallucinations, allows dynamic real-time knowledge updates without expensive model retraining, and provides verifiable document citations."),
        ("ai-grounding-hallucinations", "Grounding and Hallucination Mitigation in RAG", "rag",
         "Hallucinations in language models occur when an LLM produces plausible-sounding but factually unsupported statements. Evidence grounding requires the model to derive its answers strictly from retrieved evidence chunks. Grounded systems employ citation validation, relevance score thresholds, and deterministic refusal guardrails when evidence is insufficient."),
        ("ai-speech-stt-tts", "Speech Recognition (STT) and Synthesis (TTS)", "speech",
         "Automatic Speech Recognition (ASR/STT) models like OpenAI Whisper transcribe spoken audio signals into text using encoder-decoder sequence-to-sequence transformers trained on multilingual acoustic data. Text-to-Speech (TTS) systems convert written text into natural acoustic speech waveforms using neural vocoders and prosody prediction models.")
    ]
    docs = []
    for doc_id, title, topic, text in data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "ai_ml",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })
    return docs
