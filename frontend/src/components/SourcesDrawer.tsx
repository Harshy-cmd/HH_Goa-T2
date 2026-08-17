import React from 'react';
import { X, Database, Layers, CheckCircle2 } from 'lucide-react';

interface SourcesDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SourcesDrawer: React.FC<SourcesDrawerProps> = ({
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity">
      <div className="w-full max-w-md bg-goa-forest-deep text-goa-cream h-full p-6 sm:p-8 overflow-y-auto border-l border-goa-line/30 shadow-2xl flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between pb-4 border-b border-goa-line/20 mb-6">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-goa-yellow" />
              <h2 className="text-lg font-bold font-serif tracking-wide">
                Knowledge Base & Indexes
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-full hover:bg-goa-cream/10 text-goa-cream/70"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-4 font-mono text-xs">
            {/* 1. Primary Vector Retriever */}
            <div className="p-4 rounded-2xl bg-goa-forest border border-goa-line/30 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-goa-yellow font-bold text-sm">Sentence FAISS Dense</span>
                <span className="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 text-[10px] font-bold border border-emerald-500/40">
                  PRODUCTION
                </span>
              </div>
              <p className="text-goa-cream/70 font-sans text-xs">
                Multilingual 384-dimensional dense embeddings with inner-product cosine similarity.
              </p>
              <div className="pt-2 border-t border-goa-line/20 space-y-1 text-[11px] text-goa-cream/60">
                <div>Model: <strong className="text-goa-cream">intfloat/multilingual-e5-small</strong></div>
                <div>Dimension: <strong className="text-goa-cream">384</strong></div>
                <div>Storage: <strong className="text-goa-cream">data/indexes/sentence</strong></div>
              </div>
            </div>

            {/* 2. Supported Chunking Strategies */}
            <div className="p-4 rounded-2xl bg-goa-forest border border-goa-line/30 space-y-3">
              <span className="text-goa-cream font-bold text-xs uppercase tracking-wider block">
                Active Chunking Strategies
              </span>
              
              <div className="space-y-2">
                <div className="p-2.5 rounded-xl bg-goa-forest-deep border border-goa-line/20 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="font-semibold text-goa-cream">sentence</span>
                  </div>
                  <span className="text-[10px] text-goa-yellow font-bold">Production Default</span>
                </div>

                <div className="p-2.5 rounded-xl bg-goa-forest-deep border border-goa-line/20 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Layers className="w-3.5 h-3.5 text-goa-cream/60" />
                    <span className="font-semibold text-goa-cream">fixed</span>
                  </div>
                  <span className="text-[10px] text-goa-cream/60">500-char sliding</span>
                </div>

                <div className="p-2.5 rounded-xl bg-goa-forest-deep border border-goa-line/20 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Layers className="w-3.5 h-3.5 text-goa-cream/60" />
                    <span className="font-semibold text-goa-cream">hierarchical</span>
                  </div>
                  <span className="text-[10px] text-goa-cream/60">Parent-Child Tree</span>
                </div>
              </div>
            </div>

            {/* 3. Guardrail Thresholds */}
            <div className="p-4 rounded-2xl bg-goa-forest border border-goa-line/30 space-y-2">
              <span className="text-goa-cream font-bold text-xs uppercase tracking-wider block">
                Evidence Guardrails
              </span>
              <p className="text-goa-cream/70 font-sans text-xs">
                Answers are grounded strictly against retrieved passages with citation verification. If relevance scores fall below thresholds, the system refuses rather than guessing.
              </p>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-goa-line/20 text-center text-[11px] font-mono text-goa-cream/50">
          HH Goa 2026 · Task #2 (Voice RAG Model)
        </div>
      </div>
    </div>
  );
};
