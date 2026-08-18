import React, { useState } from 'react';
import { ShieldAlert, Volume2, Pause, RotateCcw, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { QueryResponse, VoiceQueryResponse } from '../types';

interface RefusalCardProps {
  data: QueryResponse | VoiceQueryResponse;
  isPlaying: boolean;
  onToggleAudio: () => void;
  onReset: () => void;
}

export const RefusalCard: React.FC<RefusalCardProps> = ({
  data,
  isPlaying,
  onToggleAudio,
  onReset,
}) => {
  const [showExplanation, setShowExplanation] = useState(false);
  const queryText = 'query' in data ? data.query : undefined;

  return (
    <article className="w-full max-w-2xl mx-auto my-2 animate-fade-in">
      <div className="bg-[#0A2E22]/90 border border-[#EE2A6D]/30 rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl relative overflow-hidden transition-all duration-300">
        
        {/* Soft Ambient Refusal Glow */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-[#EE2A6D]/10 via-transparent to-transparent rounded-full blur-3xl pointer-events-none" />

        {/* User Query Transcript (if available) */}
        {queryText && (
          <div className="mb-4 pb-3 border-b border-white/[0.06]">
            <p className="text-xs font-mono tracking-wider text-[#EE2A6D]/80 uppercase mb-1">
              Question
            </p>
            <p className="text-base sm:text-lg font-medium text-[#F4EDD8] font-sans">
              "{queryText}"
            </p>
          </div>
        )}

        {/* Guardrail Policy Header */}
        <div className="flex items-center justify-between mb-4">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold bg-rose-950/70 border border-[#EE2A6D]/40 text-[#EE2A6D]">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Zero-Hallucination Guardrail Active</span>
          </span>
          <span className="text-[11px] font-mono text-[#F4EDD8]/40 hidden sm:inline">
            Factual Verification
          </span>
        </div>

        {/* Headline & Content */}
        <h3 className="text-2xl sm:text-3xl font-serif text-[#F4EDD8] font-medium mb-3">
          We chose not to guess.
        </h3>
        <p className="text-[#F4EDD8]/85 text-base sm:text-lg leading-relaxed mb-5 font-sans">
          {data.answer || "I don't have enough verified information in the indexed knowledge base to answer that reliably."}
        </p>

        {/* Restrained Evidence Status Note */}
        <div className="p-3.5 rounded-2xl bg-white/[0.03] border border-white/[0.06] text-xs font-mono text-[#F4EDD8]/80 mb-5 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 text-[#F5C518] shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="text-[#F5C518]">Evidence Relevance Below Threshold:</strong> The retrieved knowledge passages did not satisfy the semantic confidence requirements needed to guarantee a factual answer.
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-white/[0.06]">
          <button
            onClick={onToggleAudio}
            className={`flex items-center gap-2 px-4 py-2 rounded-full font-mono text-xs font-semibold transition-all duration-200 active:scale-95 shadow-sm ${
              isPlaying
                ? 'bg-[#EE2A6D] text-white shadow-md shadow-[#EE2A6D]/30'
                : 'bg-white/[0.06] hover:bg-white/[0.12] text-[#F4EDD8] border border-white/[0.08]'
            }`}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Volume2 className="w-3.5 h-3.5 text-[#EE2A6D]" />}
            <span>{isPlaying ? 'Pause Audio' : 'Hear response'}</span>
          </button>

          <button
            onClick={onReset}
            className="flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-mono font-semibold text-[#F4EDD8]/75 hover:text-[#F4EDD8] bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.08] transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Ask Another Question</span>
          </button>
        </div>

        {/* Expandable Explanation Breakdown */}
        <div className="mt-4 pt-3 border-t border-white/[0.06]">
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            className="w-full flex items-center justify-between text-xs font-mono text-[#F4EDD8]/50 hover:text-[#F4EDD8] transition-colors py-1"
          >
            <span>Why did NOVARON refuse?</span>
            {showExplanation ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showExplanation && (
            <div className="mt-3 p-4 rounded-2xl bg-black/20 border border-white/[0.04] text-xs font-mono text-[#F4EDD8]/70 space-y-2 animate-fade-in">
              <p>
                NOVARON strictly grounds its answers in verified Hackathon documents. If a question falls outside the corpus or retrieval relevance scores fall below safety cutoffs, it refuses to prevent hallucinations.
              </p>
              <div className="pt-2 border-t border-white/[0.06] flex items-center justify-between text-[11px] text-[#F4EDD8]/50">
                <span>Guardrail Strategy: Strictly Grounded</span>
                <span className="text-emerald-400 font-bold">Policy: Zero Guessing</span>
              </div>
            </div>
          )}
        </div>

      </div>
    </article>
  );
};

export default RefusalCard;
