import React, { useState } from 'react';
import { ShieldAlert, Volume2, Pause, RotateCcw, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { QueryResponse, VoiceQueryResponse } from '../types';

interface RefusalCardProps {
  data: QueryResponse | VoiceQueryResponse;
  isPlaying: boolean;
  onToggleAudio: () => void;
  onReset: () => void;
  onSelectSuggestion?: (question: string) => void;
}

export const RefusalCard: React.FC<RefusalCardProps> = ({
  data,
  isPlaying,
  onToggleAudio,
  onReset,
  onSelectSuggestion,
}) => {
  const [showExplanation, setShowExplanation] = useState(false);
  const queryText = 'query' in data ? data.query : undefined;
  const normalizedQuery = data.normalized_query;
  const suggestedQuestions = (data.suggested_questions && data.suggested_questions.length > 0)
    ? data.suggested_questions
    : [
        'What is Retrieval-Augmented Generation (RAG)?',
        'How does FAISS index high-dimensional vectors?',
        'What is the difference between supervised and unsupervised learning?',
      ];

  return (
    <article className="w-full max-w-2xl mx-auto my-2 animate-fade-in">
      <div className="bg-[#0A2E22]/90 border border-[#EE2A6D]/30 rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl relative overflow-hidden transition-all duration-300">
        
        {/* Soft Ambient Refusal Glow */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-[#EE2A6D]/10 via-transparent to-transparent rounded-full blur-3xl pointer-events-none" />

        {/* User Query Transcript (if available) */}
        {queryText && (
          <div className="mb-4 pb-3 border-b border-white/[0.06]">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
              <p className="text-xs font-mono tracking-wider text-[#EE2A6D]/80 uppercase">
                Heard Question
              </p>
              {normalizedQuery && normalizedQuery.toLowerCase() !== queryText.toLowerCase() && (
                <span className="text-[11px] font-mono text-[#F5C518]/90 bg-[#F5C518]/10 px-2.5 py-0.5 rounded-full border border-[#F5C518]/20">
                  Normalized: "{normalizedQuery}"
                </span>
              )}
            </div>
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

        {/* Suggested Supported Questions */}
        {suggestedQuestions.length > 0 && (
          <div className="mb-5 pt-3 border-t border-white/[0.06] animate-fade-in">
            <p className="text-[11px] font-mono uppercase tracking-wider text-[#F4EDD8]/50 mb-2.5">
              Try Asking a Verified Knowledge Question:
            </p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => onSelectSuggestion?.(q)}
                  className="text-left text-xs font-sans text-[#F4EDD8]/85 hover:text-white bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] hover:border-[#EE2A6D]/40 px-3.5 py-2 rounded-2xl transition-all duration-200 active:scale-95 shadow-sm"
                >
                  <span className="text-[#EE2A6D] mr-1.5 font-mono">→</span>
                  <span>{q}</span>
                </button>
              ))}
            </div>
          </div>
        )}

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
