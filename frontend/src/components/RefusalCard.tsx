import React from 'react';
import { ShieldAlert, Volume2, VolumeX, RotateCcw } from 'lucide-react';
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
  const queryText = 'query' in data ? data.query : undefined;

  return (
    <div className="w-full max-w-3xl mx-auto px-4 sm:px-6 my-4 transition-all duration-500">
      <div className="bg-goa-forest-deep/90 border border-goa-pink/30 rounded-3xl p-5 sm:p-7 shadow-2xl backdrop-blur-xl relative overflow-hidden">
        {/* Soft Pink Ambient Glow */}
        <div className="absolute -top-16 -right-16 w-36 h-36 bg-goa-pink/10 rounded-full blur-2xl pointer-events-none" />

        {/* User Query Headline */}
        {queryText && (
          <div className="mb-4 pb-3 border-b border-goa-line/20">
            <span className="text-[11px] uppercase font-mono tracking-widest text-goa-pink font-semibold">
              Voice Question
            </span>
            <p className="text-base sm:text-lg font-medium text-goa-cream/90 italic mt-0.5">
              "{queryText}"
            </p>
          </div>
        )}

        {/* Calm Guardrail Header */}
        <div className="flex items-center gap-2 mb-4">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold bg-rose-950/60 border border-goa-pink/40 text-goa-pink">
            <ShieldAlert className="w-3.5 h-3.5 text-goa-pink" />
            <span>GROUNDING GUARDRAIL ENFORCED</span>
          </div>
          <span className="text-xs font-mono text-goa-cream/60 hidden sm:inline ml-auto">
            Strict Unhallucinated Defense
          </span>
        </div>

        {/* Feature-First Headline & Explanation */}
        <h3 className="text-xl sm:text-2xl font-serif text-goa-cream font-medium mb-2">
          We chose not to guess.
        </h3>
        <p className="text-goa-cream/80 text-sm sm:text-base leading-relaxed mb-5">
          {data.answer || "I don't have enough information in the indexed knowledge base to answer that reliably."}
        </p>

        <div className="p-3.5 rounded-2xl bg-goa-forest/70 border border-goa-line/20 text-xs font-mono text-goa-cream/70 mb-5">
          💡 <strong className="text-goa-yellow">Guardrail Behavior:</strong> The evidence relevance score was below the safe threshold. Rather than fabricating an ungrounded hallucination, NOVARON refuses unsupported inquiries.
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-goa-line/20">
          <button
            onClick={onToggleAudio}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-mono font-semibold transition-all ${
              isPlaying
                ? 'bg-goa-pink text-white font-bold shadow-lg shadow-goa-pink/30 animate-pulse'
                : 'bg-goa-cream/10 hover:bg-goa-cream/20 text-goa-cream border border-goa-line/40'
            }`}
          >
            {isPlaying ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5 text-goa-pink" />}
            <span>{isPlaying ? 'Pause Refusal Audio' : 'Hear Refusal Audio'}</span>
          </button>

          <button
            onClick={onReset}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-mono text-goa-cream/80 hover:text-goa-cream hover:bg-goa-cream/10 transition-colors border border-goa-line/30"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Ask Another Question</span>
          </button>
        </div>
      </div>
    </div>
  );
};
