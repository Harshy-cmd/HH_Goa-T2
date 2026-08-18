import React, { useState } from 'react';
import { Volume2, Pause, Copy, Check, Share2, Database, Zap, ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';
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

  const renderInlineCitations = (content: string) => {
    const parts = content.split(/(\[\d+\])/g);
    return parts.map((part, index) => {
      const match = part.match(/^\[(\d+)\]$/);
      if (match) {
        return (
          <span
            key={index}
            className="inline-flex items-center justify-center font-mono text-[10px] font-bold text-[#F5C518] bg-[#F5C518]/15 border border-[#F5C518]/25 rounded px-1.5 py-0.5 mx-0.5 align-baseline"
          >
            {match[1]}
          </span>
        );
      }
      return part;
    });
  };

  const renderParagraph = (block: string, pIdx: number) => {
    const lines = block.split('\n').map((l) => l.trim()).filter(Boolean);
    const isListBlock = lines.some((l) => l.startsWith('- ') || l.startsWith('* ') || l.startsWith('• ') || /^\d+\.\s+/.test(l));

    if (isListBlock) {
      return (
        <ul key={pIdx} className="space-y-1.5 my-2">
          {lines.map((line, lIdx) => {
            const numberedMatch = line.match(/^(\d+)\.\s+(.*)/);
            if (numberedMatch) {
              return (
                <li key={lIdx} className="flex items-start gap-2.5 ml-1">
                  <span className="font-mono text-xs font-bold text-[#F5C518] mt-0.5 shrink-0">
                    {numberedMatch[1]}.
                  </span>
                  <span className="leading-relaxed">{renderInlineCitations(numberedMatch[2])}</span>
                </li>
              );
            }

            const bulletMatch = line.match(/^[-*•]\s+(.*)/);
            if (bulletMatch) {
              return (
                <li key={lIdx} className="flex items-start gap-2.5 ml-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#F5C518]/80 mt-2 shrink-0" />
                  <span className="leading-relaxed">{renderInlineCitations(bulletMatch[1])}</span>
                </li>
              );
            }

            return (
              <li key={lIdx} className="leading-relaxed">
                {renderInlineCitations(line)}
              </li>
            );
          })}
        </ul>
      );
    }

    return (
      <p key={pIdx} className="leading-relaxed">
        {renderInlineCitations(block)}
      </p>
    );
  };

  return (
    <article className="w-full max-w-2xl mx-auto my-2 animate-fade-in">
      <div className="bg-[#0A2E22]/90 border border-white/[0.08] rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl relative overflow-hidden transition-all duration-300">
        
        {/* Ambient Subtle Accent Glow */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-[#F5C518]/5 via-transparent to-transparent rounded-full blur-3xl pointer-events-none" />

        {/* User Query Header (if from Voice/Text) */}
        {queryText && (
          <div className="mb-4 pb-3 border-b border-white/[0.06]">
            <p className="text-xs font-mono tracking-wider text-[#F4EDD8]/50 uppercase mb-1">
              Question
            </p>
            <p className="text-base sm:text-lg font-medium text-[#F4EDD8] font-sans">
              "{queryText}"
            </p>
          </div>
        )}

        {/* Status Bar: Grounding & Sources Badge */}
        <div className="flex flex-wrap items-center justify-between gap-2.5 mb-5 pb-3 border-b border-white/[0.06]">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 shadow-sm">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Grounded Knowledge</span>
            </span>

            {sources.length > 0 && (
              <button
                onClick={() => setSourcesExpanded(!sourcesExpanded)}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-[#F4EDD8]/80 hover:text-[#F4EDD8] transition-all"
              >
                <Database className="w-3.5 h-3.5 text-[#F5C518]" />
                <span>{sources.length} {sources.length === 1 ? 'Source' : 'Sources'}</span>
                {sourcesExpanded ? <ChevronUp className="w-3 h-3 text-[#F4EDD8]/60" /> : <ChevronDown className="w-3 h-3 text-[#F4EDD8]/60" />}
              </button>
            )}
          </div>

          {/* Latency Tag */}
          <button
            onClick={() => setLatencyExpanded(!latencyExpanded)}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-mono text-[#F5C518]/90 hover:text-[#F5C518] bg-[#F5C518]/10 hover:bg-[#F5C518]/20 border border-[#F5C518]/25 transition-colors"
            title="Toggle latency breakdown"
          >
            <Zap className="w-3 h-3 text-[#F5C518]" />
            <span>{totalLatencyFormatted}</span>
          </button>
        </div>

        {/* Primary Answer Prose with Clear Paragraphs, Lists & Citation Badges */}
        <div className="text-[#F4EDD8] text-base sm:text-lg leading-relaxed font-normal mb-6 font-sans space-y-3.5 selection:bg-[#EE2A6D]/30 selection:text-white">
          {data.answer.split('\n\n').map((paragraph, idx) => renderParagraph(paragraph, idx))}
        </div>

        {/* Minimal Audio & Action Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-2xl bg-white/[0.03] border border-white/[0.06] mb-2">
          {/* Voice Response Trigger */}
          <button
            onClick={onToggleAudio}
            className={`flex items-center gap-2.5 px-4 py-2 rounded-full font-mono text-xs font-semibold transition-all duration-200 active:scale-95 shadow-sm ${
              isPlaying
                ? 'bg-[#EE2A6D] text-white shadow-md shadow-[#EE2A6D]/30'
                : 'bg-[#F4EDD8] text-[#0A2E22] hover:bg-white'
            }`}
            title={isPlaying ? 'Pause Voice Response' : 'Play Voice Response'}
          >
            {isPlaying ? (
              <>
                <Pause className="w-3.5 h-3.5 fill-current" />
                <span>Speaking...</span>
                <span className="flex items-center gap-0.5 ml-1">
                  <span className="w-0.5 h-2.5 bg-white animate-pulse" />
                  <span className="w-0.5 h-3.5 bg-white animate-bounce" />
                  <span className="w-0.5 h-2 bg-white animate-pulse" />
                </span>
              </>
            ) : (
              <>
                <Volume2 className="w-3.5 h-3.5 fill-current" />
                <span>Listen to answer</span>
              </>
            )}
          </button>

          {/* Secondary Actions (Copy & Share) */}
          <div className="flex items-center gap-2 text-xs font-mono text-[#F4EDD8]/70">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-white/[0.06] hover:text-[#F4EDD8] transition-colors"
              title="Copy answer text"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>

            {onShare && (
              <button
                onClick={onShare}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-white/[0.06] hover:text-[#EE2A6D] transition-colors"
                title="Share answer"
              >
                <Share2 className="w-3.5 h-3.5" />
                <span>Share</span>
              </button>
            )}
          </div>
        </div>

        {/* Expandable Grounding Sources Section */}
        {sources.length > 0 && sourcesExpanded && (
          <div className="mt-4 pt-4 border-t border-white/[0.06] space-y-2.5 max-h-64 overflow-y-auto pr-1 animate-fade-in">
            <div className="text-[11px] font-mono uppercase tracking-wider text-[#F4EDD8]/50 mb-2">
              Verified Knowledge Sources
            </div>
            {sources.map((src, i) => (
              <div
                key={src.chunk_id || i}
                className="p-3.5 rounded-2xl bg-white/[0.025] border border-white/[0.06] text-xs font-mono hover:border-white/[0.12] transition-colors"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-semibold text-[#F4EDD8] truncate max-w-[240px] sm:max-w-md">
                    {String(i + 1).padStart(2, '0')}. {src.title || src.document_id || 'Knowledge Base Entry'}
                  </span>
                  <span className="text-[#F5C518] text-[11px] font-medium px-2 py-0.5 rounded-md bg-[#F5C518]/10 border border-[#F5C518]/20">
                    Relevance: {(src.relevance_score).toFixed(2)}
                  </span>
                </div>
                <p className="text-[#F4EDD8]/75 font-sans text-xs line-clamp-2 leading-relaxed italic">
                  "{src.text}"
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Expandable Detailed Latency Breakdown */}
        {latencyExpanded && (
          <div className="mt-4 pt-4 border-t border-white/[0.06] bg-white/[0.015] -mx-6 sm:-mx-8 -mb-6 sm:-mb-8 p-6 rounded-b-3xl animate-fade-in font-mono text-xs">
            <div className="flex items-center justify-between mb-2.5 text-[#F4EDD8]/60 text-[10px] uppercase tracking-wider">
              <span>Pipeline Stage Breakdown</span>
              <span className="text-[#F5C518] font-bold">Total: {totalLatencyFormatted}</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
              {latency.stt !== undefined && (
                <div className="p-2 rounded-xl bg-[#0F3D2E]/50 border border-white/[0.06]">
                  <div className="text-[#F4EDD8]/50 text-[9px] uppercase">STT Whisper</div>
                  <div className="text-[#F4EDD8] font-bold mt-0.5">{Math.round(latency.stt)}ms</div>
                </div>
              )}
              {latency.retrieval !== undefined && (
                <div className="p-2 rounded-xl bg-[#0F3D2E]/50 border border-white/[0.06]">
                  <div className="text-[#F4EDD8]/50 text-[9px] uppercase">FAISS Dense</div>
                  <div className="text-[#F4EDD8] font-bold mt-0.5">{Math.round(latency.retrieval)}ms</div>
                </div>
              )}
              {latency.reranking !== undefined && (
                <div className="p-2 rounded-xl bg-[#0F3D2E]/50 border border-white/[0.06]">
                  <div className="text-[#F4EDD8]/50 text-[9px] uppercase">Reranking</div>
                  <div className="text-[#F4EDD8] font-bold mt-0.5">{Math.round(latency.reranking)}ms</div>
                </div>
              )}
              {latency.generation !== undefined && (
                <div className="p-2 rounded-xl bg-[#0F3D2E]/50 border border-white/[0.06]">
                  <div className="text-[#F4EDD8]/50 text-[9px] uppercase">LLM Answer</div>
                  <div className="text-[#F4EDD8] font-bold mt-0.5">{Math.round(latency.generation)}ms</div>
                </div>
              )}
              {latency.tts !== undefined && (
                <div className="p-2 rounded-xl bg-[#0F3D2E]/50 border border-white/[0.06]">
                  <div className="text-[#F4EDD8]/50 text-[9px] uppercase">EdgeTTS</div>
                  <div className="text-[#F4EDD8] font-bold mt-0.5">{Math.round(latency.tts)}ms</div>
                </div>
              )}
            </div>
          </div>
        )}

      </div>
    </article>
  );
};

export default AnswerCard;
