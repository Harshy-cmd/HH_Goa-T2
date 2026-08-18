import React, { useState, useEffect } from 'react';
import { X, Send, Sparkles } from 'lucide-react';

interface TextQueryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (query: string) => void;
}

export const TextQueryModal: React.FC<TextQueryModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [query, setQuery] = useState('');

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSubmit(query.trim());
    setQuery('');
    onClose();
  };

  const sampleSuggestions = [
    'What is photosynthesis?',
    'प्रकाश संश्लेषण क्या है?',
    'What cities are in Calvert County?',
    'What is the speed of an English Mastiff?',
  ];

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="text-query-title"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-fade-in"
    >
      <div className="w-full max-w-lg bg-[#0A2E22]/95 text-[#F4EDD8] rounded-3xl p-6 sm:p-8 border border-white/[0.08] shadow-2xl relative backdrop-blur-xl">
        {/* Close Button */}
        <button
          onClick={onClose}
          aria-label="Close"
          className="absolute top-5 right-5 p-1.5 rounded-full hover:bg-white/[0.08] text-[#F4EDD8]/60 hover:text-[#F4EDD8] transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Headline */}
        <h3 id="text-query-title" className="text-xl font-bold font-serif text-[#F4EDD8] mb-1">
          Type Your Question
        </h3>
        <p className="text-xs font-mono text-[#F4EDD8]/50 mb-5">
          Ask NOVARON directly via keyboard input
        </p>

        {/* Input Form */}
        <form onSubmit={handleSubmit}>
          <div className="relative mb-4">
            <textarea
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything from the verified knowledge base..."
              rows={3}
              className="w-full bg-white/[0.03] border border-white/[0.08] focus:border-[#EE2A6D] rounded-2xl p-4 text-sm text-[#F4EDD8] placeholder-[#F4EDD8]/35 focus:outline-none transition-colors font-sans resize-none"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
          </div>

          {/* Sample Prompts */}
          <div className="mb-6">
            <span className="text-[10px] font-mono uppercase tracking-wider text-[#F4EDD8]/40 block mb-2 flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-[#F5C518]" />
              <span>Suggested Questions</span>
            </span>
            <div className="flex flex-wrap gap-1.5">
              {sampleSuggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setQuery(suggestion)}
                  className="text-left text-[11px] font-mono px-3 py-1.5 rounded-full bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.06] hover:border-white/[0.12] text-[#F4EDD8]/70 hover:text-[#F4EDD8] transition-all duration-150"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-full text-xs font-mono text-[#F4EDD8]/60 hover:text-[#F4EDD8] hover:bg-white/[0.04] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!query.trim()}
              className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-[#EE2A6D] hover:bg-[#f43f5e] text-white font-mono text-xs font-bold transition-all duration-150 active:scale-95 disabled:opacity-30 disabled:pointer-events-none shadow-md shadow-[#EE2A6D]/30"
            >
              <span>Submit</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TextQueryModal;
