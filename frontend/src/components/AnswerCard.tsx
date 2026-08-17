import React, { useState } from 'react';
import { Volume2, VolumeX, CheckCircle, Database, Zap, ChevronDown, ChevronUp, Copy, Check, Share2, Play, Pause } from 'lucide-react';
import { QueryResponse, VoiceQueryResponse } from '../types';

interface AnswerCardProps {
  data: QueryResponse | VoiceQueryResponse;
  isPlaying: boolean;
  onToggleAudio: () => void;
  onShare?: () => void;
}

export const AnswerCard: React.FC<AnswerCardProps> = ({
  data,
  isPlaying,
  onToggleAudio,
  onShare,
}) => {
  const [sourcesExpanded, setSourcesExpanded] = useState(false);
  const [latencyExpanded, setLatencyExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const queryText = 'query' in data ? data.query : undefined;
  const sources = data.sources || [];
  const latency = data.latency_ms || {};

  const handleCopy = () => {
    navigator.clipboard.writeText(data.answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const totalLatencyFormatted = latency.total
    ? `${Math.round(latency.total)}ms`
    : `${Math.round(latency.rag_total || 0)}ms`;

  return (
    <div className="w-full max-w-2xl mx-auto my-2 transition-all duration-500 animate-fade-in">
      <div className="bg-goa-forest-deep/95 border border-goa-line/30 rounded-3xl p-5 sm:p-7 shadow-2xl backdrop-blur-xl relative">
        {/* User Query Transcript (if from Voice) */}
        {queryText && (
          <div className="mb-4 pb-3 border-b border-goa-line/20">
            <span className="text-[10px] uppercase font-mono tracking-widest text-goa-yellow font-semibold">
              Voice Transcript
            </span>
            <p className="text-base sm:text-lg font-medium text-goa-cream italic mt-0.5">
              "{queryText}"
            </p>
          </div>
        )}

        {/* Top Metadata Header Row */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4 pb-3 border-b border-goa-line/20">
          {/* Left: Grounded Badge */}
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold bg-emerald-950/80 border border-emerald-500/50 text-emerald-300">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            <span>GROUNDED</span>
          </div>

          {/* Right: Sources Count & Latency */}
          <div className="flex items-center gap-2 font-mono text-xs">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-goa-cream/10 border border-goa-line/40 text-goa-cream font-semibold">
              <Database className="w-3.5 h-3.5 text-goa-yellow" />
              <span>{sources.length} SOURCES</span>
            </div>

            <button
              onClick={() => setLatencyExpanded(!latencyExpanded)}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-goa-yellow/15 hover:bg-goa-yellow/25 border border-goa-yellow/40 text-goa-yellow font-bold transition-colors"
            >
              <Zap className="w-3.5 h-3.5 text-goa-yellow" />
              <span>{totalLatencyFormatted}</span>
              {latencyExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>
          </div>
        </div>

        {/* Grounded Answer Text */}
        <div className="text-goa-cream text-base sm:text-lg leading-relaxed font-normal mb-6 space-y-3 font-sans">
          <p>{data.answer}</p>
        </div>

        {/* Audio Player Strip (Matching Reference Image) */}
        <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-2xl bg-goa-forest/90 border border-goa-line/30 mb-4">
          {/* Yellow Player Pill */}
          <button
            onClick={onToggleAudio}
            className="flex items-center gap-2.5 px-4 py-2 rounded-full bg-goa-yellow text-goa-forest font-mono text-xs font-bold shadow-md shadow-goa-yellow/20 hover:scale-105 active:scale-95 transition-all"
          >
            {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Volume2 className="w-4 h-4 fill-current" />}
            <span>{isPlaying ? 'Playing response...' : 'Play voice response'}</span>

            {/* Mini Equalizer animation while playing */}
            {isPlaying && (
              <div className="flex items-center gap-0.5 ml-1">
                <span className="w-0.5 h-3 bg-goa-forest animate-pulse" />
                <span className="w-0.5 h-4 bg-goa-forest animate-bounce" />
                <span className="w-0.5 h-2 bg-goa-forest animate-pulse" />
              </div>
            )}
          </button>

          {/* Secondary Controls (Pause, Copy, Share) */}
          <div className="flex items-center gap-3 font-mono text-xs text-goa-cream/80">
            <button
              onClick={onToggleAudio}
              className="flex items-center gap-1 hover:text-goa-cream transition-colors"
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
              <span>{isPlaying ? 'Pause' : 'Play'}</span>
            </button>

            <button
              onClick={handleCopy}
              className="flex items-center gap-1 hover:text-goa-cream transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>

            {onShare && (
              <button
                onClick={onShare}
                className="flex items-center gap-1 hover:text-goa-pink text-goa-pink/90 transition-colors"
              >
                <Share2 className="w-3.5 h-3.5" />
                <span>Share</span>
              </button>
            )}
          </div>
        </div>

        {/* Expandable Sources Strip */}
        <div className="border-t border-goa-line/20 pt-3">
          <button
            onClick={() => setSourcesExpanded(!sourcesExpanded)}
            className="w-full flex items-center justify-between py-1 text-xs font-mono font-semibold text-goa-cream/80 hover:text-goa-cream transition-colors"
          >
            <div className="flex items-center gap-2">
              <Database className="w-3.5 h-3.5 text-goa-yellow" />
              <span className="uppercase tracking-wider">SOURCES ({sources.length})</span>
            </div>
            {sourcesExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {sourcesExpanded && (
            <div className="mt-3 space-y-2 max-h-60 overflow-y-auto pr-1">
              {sources.map((src, i) => (
                <div
                  key={src.chunk_id || i}
                  className="p-3 rounded-2xl bg-goa-forest/80 border border-goa-line/30 text-xs font-mono"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-goa-cream">
                      {String(i + 1).padStart(2, '0')} {src.document_id || 'Corpus Document'}
                    </span>
                    <span className="text-goa-yellow font-bold text-[11px]">
                      {(src.relevance_score).toFixed(2)}
                    </span>
                  </div>
                  <div className="text-[10px] text-goa-cream/60 mb-2 truncate">
                    Chunk ID: {src.chunk_id}
                  </div>

                  {/* Horizontal Relevance Bar */}
                  <div className="w-full h-1.5 bg-goa-forest-deep rounded-full overflow-hidden mb-2">
                    <div
                      style={{ width: `${Math.min(100, Math.max(10, src.relevance_score * 100))}%` }}
                      className="h-full bg-emerald-400 rounded-full"
                    />
                  </div>

                  <p className="text-goa-cream/80 font-sans text-xs line-clamp-3 leading-relaxed">
                    "{src.text}"
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Expandable Detailed Latency Breakdown */}
        {latencyExpanded && (
          <div className="mt-4 pt-4 border-t border-dashed border-goa-line/30 bg-goa-forest/80 -mx-5 sm:-mx-7 -mb-5 sm:-mb-7 p-5 rounded-b-3xl">
            <div className="flex items-center justify-between mb-2 font-mono">
              <span className="text-[11px] uppercase tracking-widest text-goa-yellow font-bold">
                LATENCY {totalLatencyFormatted}
              </span>
              <span className="text-[10px] text-goa-cream/60 uppercase">DETAILS</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs font-mono">
              {latency.stt !== undefined && (
                <div className="p-2 rounded-xl bg-goa-forest-deep border border-goa-line/20">
                  <div className="text-goa-cream/60 text-[10px]">STT</div>
                  <div className="text-goa-cream font-bold">{Math.round(latency.stt)}ms</div>
                </div>
              )}
              {latency.retrieval !== undefined && (
                <div className="p-2 rounded-xl bg-goa-forest-deep border border-goa-line/20">
                  <div className="text-goa-cream/60 text-[10px]">RETRIEVAL</div>
                  <div className="text-goa-cream font-bold">{Math.round(latency.retrieval)}ms</div>
                </div>
              )}
              {latency.reranking !== undefined && (
                <div className="p-2 rounded-xl bg-goa-forest-deep border border-goa-line/20">
                  <div className="text-goa-cream/60 text-[10px]">RERANK</div>
                  <div className="text-goa-cream font-bold">{Math.round(latency.reranking)}ms</div>
                </div>
              )}
              {latency.generation !== undefined && (
                <div className="p-2 rounded-xl bg-goa-forest-deep border border-goa-line/20">
                  <div className="text-goa-cream/60 text-[10px]">LLM</div>
                  <div className="text-goa-cream font-bold">{Math.round(latency.generation)}ms</div>
                </div>
              )}
              {latency.tts !== undefined && (
                <div className="p-2 rounded-xl bg-goa-forest-deep border border-goa-line/20">
                  <div className="text-goa-cream/60 text-[10px]">TTS</div>
                  <div className="text-goa-cream font-bold">{Math.round(latency.tts)}ms</div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
