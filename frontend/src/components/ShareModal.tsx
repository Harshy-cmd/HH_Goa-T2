import React, { useState, useEffect } from 'react';
import { X, Copy, Check, Share2 } from 'lucide-react';
import { QueryResponse, VoiceQueryResponse } from '../types';

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: QueryResponse | VoiceQueryResponse;
}

export const ShareModal: React.FC<ShareModalProps> = ({
  isOpen,
  onClose,
  data,
}) => {
  const [copied, setCopied] = useState(false);

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

  const queryText = 'query' in data ? data.query : 'Grounded Question';
  const totalMs = data.latency_ms?.total || data.latency_ms?.rag_total || 0;
  const latencyStr = totalMs > 1000 ? `${(totalMs / 1000).toFixed(2)}s` : `${Math.round(totalMs)}ms`;

  const shareText = `🎙️ NOVARON Voice RAG @ HH Goa 2026\n\nQ: "${queryText}"\nA: "${data.answer.slice(0, 150)}..."\n\n⚡ ${latencyStr} latency · ${data.sources?.length || 0} Grounded Sources\n#RAGInGoa #HHGoa2026`;

  const handleCopyText = () => {
    navigator.clipboard.writeText(shareText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleTwitterShare = () => {
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`;
    window.open(url, '_blank');
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="share-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
    >
      <div className="w-full max-w-md bg-goa-forest-deep text-goa-cream rounded-3xl p-6 border border-goa-line/30 shadow-2xl relative animate-fade-in">
        <button
          onClick={onClose}
          aria-label="Close"
          className="absolute top-4 right-4 p-1.5 rounded-full hover:bg-goa-cream/10 text-goa-cream/70 hover:text-goa-cream"
        >
          <X className="w-5 h-5" />
        </button>

        <h3 id="share-modal-title" className="text-lg font-bold font-serif text-goa-cream mb-4 flex items-center gap-2">
          <Share2 className="w-4 h-4 text-goa-pink" />
          <span>Share Grounded Answer</span>
        </h3>

        {/* Share Preview Card */}
        <div className="bg-goa-forest p-4 rounded-2xl border border-goa-line/30 mb-5 font-mono text-xs space-y-2">
          <div className="text-goa-yellow font-bold text-[10px] tracking-wider uppercase">
            HH Goa 2026 · NOVARON Voice RAG
          </div>
          <div className="text-goa-cream italic">"{queryText}"</div>
          <div className="text-goa-cream/80 line-clamp-3 text-[11px] font-sans">
            {data.answer}
          </div>
          <div className="text-[10px] text-emerald-400 font-bold pt-1 border-t border-goa-line/20">
            ✓ GROUNDED · {data.sources?.length || 0} SOURCES · ⚡ {latencyStr}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={handleTwitterShare}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-full bg-[#1DA1F2] hover:bg-[#1a94df] text-white text-xs font-mono font-bold transition-all shadow-md"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
            </svg>
            <span>Post to X</span>
          </button>
          <button
            onClick={handleCopyText}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-full bg-goa-cream/10 hover:bg-goa-cream/20 text-goa-cream text-xs font-mono font-bold border border-goa-line/30 transition-all"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? 'Copied!' : 'Copy Summary'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
