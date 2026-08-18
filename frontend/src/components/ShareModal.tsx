import React, { useState, useEffect } from 'react';
import { X, Copy, Check, Share2, Sparkles } from 'lucide-react';
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
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-fade-in"
    >
      <div className="w-full max-w-md bg-[#0A2E22]/95 text-[#F4EDD8] rounded-3xl p-6 sm:p-8 border border-white/[0.08] shadow-2xl relative backdrop-blur-xl">
        <button
          onClick={onClose}
          aria-label="Close"
          className="absolute top-5 right-5 p-1.5 rounded-full hover:bg-white/[0.08] text-[#F4EDD8]/60 hover:text-[#F4EDD8] transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5 mb-2">
          <Share2 className="w-5 h-5 text-[#F5C518]" />
          <h3 id="share-modal-title" className="text-xl font-bold font-serif text-[#F4EDD8]">
            Share Grounded Result
          </h3>
        </div>
        <p className="text-xs font-mono text-[#F4EDD8]/50 mb-5">
          NOVARON Zero-Hallucination Voice RAG
        </p>

        {/* Preview Card */}
        <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] font-mono text-xs text-[#F4EDD8]/80 mb-5 whitespace-pre-wrap leading-relaxed">
          {shareText}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={handleCopyText}
            className="flex items-center justify-center gap-2 py-3 px-4 rounded-full bg-white/[0.06] hover:bg-white/[0.10] border border-white/[0.08] text-xs font-mono font-semibold text-[#F4EDD8] transition-all duration-150 active:scale-95 shadow-sm"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? 'Copied!' : 'Copy Text'}</span>
          </button>

          <button
            onClick={handleTwitterShare}
            className="flex items-center justify-center gap-2 py-3 px-4 rounded-full bg-[#EE2A6D] hover:bg-[#f43f5e] text-white text-xs font-mono font-bold transition-all duration-150 active:scale-95 shadow-md shadow-[#EE2A6D]/30"
          >
            <Sparkles className="w-4 h-4" />
            <span>Share on X</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ShareModal;
