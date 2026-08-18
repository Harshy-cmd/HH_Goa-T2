export interface Source {
  chunk_id: string;
  document_id: string;
  passage_id: string;
  title: string | null;
  language: string | null;
  text: string;
  relevance_score: number;
}

export interface LatencyBreakdown {
  stt?: number;
  retrieval?: number;
  reranking?: number;
  generation?: number;
  tts?: number;
  rag_total?: number;
  total?: number;
}

export interface QueryResponse {
  answer: string;
  refused: boolean;
  retrieval_strategy: string;
  chunking_strategy: string;
  sources: Source[];
  latency_ms: LatencyBreakdown;
  audio_base64?: string | null;
  query_type?: 'conversational' | 'system' | 'knowledge' | 'refusal' | string | null;
}

export interface VoiceQueryResponse {
  query: string;
  answer: string;
  refused: boolean;
  retrieval_strategy: string;
  chunking_strategy: string;
  sources: Source[];
  latency_ms: LatencyBreakdown;
  audio_base64?: string | null;
  query_type?: 'conversational' | 'system' | 'knowledge' | 'refusal' | string | null;
}

export type AppState =
  | 'IDLE'
  | 'LISTENING'
  | 'TRANSCRIBING'
  | 'RETRIEVING'
  | 'GENERATING'
  | 'ANSWER_READY'
  | 'REFUSED'
  | 'ERROR'
  | 'PLAYING_AUDIO';

export interface Settings {
  language: 'en' | 'hi' | 'auto';
  chunking_strategy: 'fixed' | 'sentence' | 'hierarchical';
  retrieval_mode: 'dense' | 'bm25' | 'hybrid' | 'hybrid_rerank';
  top_k: number;
  synthesize_audio: boolean;
  apiBaseUrl: string;
}
