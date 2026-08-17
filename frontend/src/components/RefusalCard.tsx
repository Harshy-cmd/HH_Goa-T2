import React, { useState } from 'react';
import { ShieldAlert, Volume2, VolumeX, RotateCcw, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
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
    <div className="w-full max-w-2xl mx-auto my-2 transition-all duration-500 animate-fade-in">
      <div className="bg-goa-forest-deep/95 border border-goa-pink/40 rounded-3xl p-5 sm:p-7 shadow-2xl backdrop-blur-xl relative overflow-hidden">
        {/* Soft Ambient Refusal Glow */}
        <div className="absolute -top-16 -right-16 w-36 h-36 bg-goa-pink/10 rounded-full blur-3xl pointer-events-none" />

        {/* User Query Transcript (if available) */}
        {queryText && (
          <div className="mb-4 pb-3 border-b border-goa-line/20">
            <span className="text-[10px] uppercase font-mono tracking-widest text-goa-pink font-semibold">
              Voice Question
            </span>
            <p className="text-base sm:text-lg font-medium text-goa-cream italic mt-0.5">
              "{queryText}"
            </p>
          </div>
        )}

        {/* Calm Guardrail Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold bg-rose-950/80 border border-goa-pink/50 text-goa-pink">
            <ShieldAlert className="w-3.5 h-3.5 text-goa-pink" />
            <span>GROUNDING GUARDRAIL ENFORCED</span>
          </div>
          <span className="text-[11px] font-mono text-goa-cream/50 hidden sm:inline">
            Zero Hallucination Policy
          </span>
        </div>

        {/* Feature-First Headline & Content */}
        <h3 className="text-2xl sm:text-3xl font-serif text-goa-cream font-medium mb-2">
          We chose not to guess.
        </h3>
        <p className="text-goa-cream/80 text-sm sm:text-base leading-relaxed mb-4 font-sans">
          {data.answer || "I don't have enough information in the indexed knowledge base to answer that reliably."}
        </p>

        {/* Evidence Status Highlight */}
        <div className="p-3.5 rounded-2xl bg-goa-forest/80 border border-goa-line/20 text-xs font-mono text-goa-cream/80 mb-4 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-goa-yellow shrink-0 mt-0.5" />
          <div>
            <strong className="text-goa-yellow">Evidence Relevance Below Threshold:</strong> The retrieved passages did not satisfy the semantic confidence requirements needed to guarantee a factual answer.
          </div>
        </div>

        {/* Actions: Audio & Reset */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-goa-line/20">
          <button
            onClick={onToggleAudio}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-mono font-bold transition-all shadow-md ${
              isPlaying
                ? 'bg-goa-pink text-white ring-2 ring-goa-pink/50 animate-pulse'
                : 'bg-goa-cream/10 hover:bg-goa-cream/20 text-goa-cream border border-goa-line/40'
            }`}
          >
            {isPlaying ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5 text-goa-pink" />}
            <span>{isPlaying ? 'Pause Refusal Audio' : 'Hear Refusal Audio'}</span>
          </button>

          <button
            onClick={onReset}
            className="flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-mono font-semibold text-goa-cream/80 hover:text-goa-cream hover:bg-goa-cream/10 transition-colors border border-goa-line/30"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Ask Another Question</span>
          </button>
        </div>

        {/* Expandable "Why did NOVARON refuse?" Breakdown */}
        <div className="mt-4 pt-3 border-t border-dashed border-goa-line/20">
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            className="w-full flex items-center justify-between text-xs font-mono text-goa-cream/60 hover:text-goa-cream transition-colors"
          >
            <span>Why did NOVARON refuse?</span>
            {showExplanation ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showExplanation && (
            <div className="mt-3 p-3 rounded-2xl bg-goa-forest/90 border border-goa-line/20 text-[11px] font-mono text-goa-cream/70 space-y-1.5 animate-fade-in">
              <div>• <strong>Philosophy:</strong> NO EVIDENCE → NO HALLUCINATION.</div>
              <div>• <strong>Grounding Check:</strong> Cross-checked against Sentence FAISS Dense multilingual index.</div>
              <div>• <strong>Citation Protocol:</strong> Answers are only synthesized when supported by verifiable chunk IDs.</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
