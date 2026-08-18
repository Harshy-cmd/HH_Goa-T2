import React, { useEffect } from 'react';
import { X, Database, BookOpen, CheckCircle2 } from 'lucide-react';
import { Source } from '../types';

interface SourcesDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  sources?: Source[];
  queryText?: string;
}

export const SourcesDrawer: React.FC<SourcesDrawerProps> = ({
  isOpen,
  onClose,
  sources = [],
  queryText,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="sources-drawer-title"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
      className="fixed inset-0 z-40 flex justify-end bg-black/60 backdrop-blur-sm lg:left-60 transition-opacity animate-fade-in"
    >
      <div className="w-full max-w-md bg-[#0A2E22]/95 text-[#F4EDD8] h-full p-6 sm:p-8 overflow-y-auto border-l border-white/[0.08] shadow-2xl flex flex-col justify-between backdrop-blur-xl">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-white/[0.08] mb-6">
            <div className="flex items-center gap-2.5">
              <Database className="w-5 h-5 text-[#F5C518]" />
              <div>
                <h2 id="sources-drawer-title" className="text-lg font-bold font-serif tracking-wide text-[#F4EDD8]">
                  Sources
                </h2>
                <p className="text-[10px] font-mono tracking-wider text-[#F4EDD8]/50 uppercase">
                  References used by NOVARON
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              aria-label="Close Sources"
              className="p-1.5 rounded-full hover:bg-white/[0.08] text-[#F4EDD8]/60 hover:text-[#F4EDD8] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Current Query Context (if applicable) */}
          {queryText && (
            <div className="p-3.5 rounded-2xl bg-white/[0.03] border border-white/[0.06] mb-5">
              <span className="text-[10px] uppercase font-mono tracking-wider text-[#F5C518] block mb-1">
                Active Question
              </span>
              <p className="text-xs text-[#F4EDD8]/90 font-sans italic line-clamp-2">
                "{queryText}"
              </p>
            </div>
          )}

          {/* Sources List */}
          {sources.length === 0 ? (
            <div className="text-center py-20 px-4 text-[#F4EDD8]/50 font-mono text-xs space-y-3">
              <BookOpen className="w-10 h-10 mx-auto opacity-30 text-[#F5C518]" />
              <p className="font-medium text-[#F4EDD8]/70">No source references active yet.</p>
              <p className="text-[11px] text-[#F4EDD8]/45 font-sans leading-relaxed">
                Ask a voice or text question to inspect the verified knowledge documents used to ground NOVARON's answers.
              </p>
            </div>
          ) : (
            <div className="space-y-3.5">
              <div className="flex items-center justify-between text-xs font-mono text-[#F4EDD8]/60 mb-1">
                <span className="flex items-center gap-1.5 text-emerald-400 font-semibold text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>{sources.length} Grounded References</span>
                </span>
              </div>

              {sources.map((src, i) => (
                <div
                  key={src.chunk_id || i}
                  className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.07] hover:border-white/[0.14] transition-all text-xs font-mono group"
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-bold px-2 py-0.5 rounded-md bg-[#F5C518]/15 text-[#F5C518] border border-[#F5C518]/25 shrink-0">
                        {String(i + 1).padStart(2, '0')}
                      </span>
                      <h4 className="font-semibold text-[#F4EDD8] line-clamp-1 group-hover:text-[#F5C518] transition-colors">
                        {src.title || src.document_id || 'Corpus Document'}
                      </h4>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      {src.language && (
                        <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-white/[0.06] text-[#F4EDD8]/60">
                          {src.language}
                        </span>
                      )}
                      <span className="text-[10px] text-[#F4EDD8]/50 px-2 py-0.5 rounded bg-white/[0.04]">
                        Score: {(src.relevance_score).toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <p className="text-[#F4EDD8]/75 font-sans text-xs line-clamp-3 leading-relaxed mt-2 italic bg-black/10 p-2.5 rounded-xl border border-white/[0.03]">
                    "{src.text}"
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Minimal Footer */}
        <div className="pt-4 border-t border-white/[0.06] flex items-center justify-between text-[11px] font-mono text-[#F4EDD8]/40 mt-6">
          <span>HH GOA 2026</span>
          <span className="text-emerald-400/80 font-medium">Grounded Verification</span>
        </div>
      </div>
    </div>
  );
};

export default SourcesDrawer;
