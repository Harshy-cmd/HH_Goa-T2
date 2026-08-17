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
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
    >
      <div className="w-full max-w-lg bg-goa-forest-deep text-goa-cream rounded-3xl p-6 sm:p-7 border border-goa-line/30 shadow-2xl relative animate-fade-in">
        {/* Close Button */}
        <button
          onClick={onClose}
          aria-label="Close"
          className="absolute top-5 right-5 p-1.5 rounded-full hover:bg-goa-cream/10 text-goa-cream/70 hover:text-goa-cream transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Headline */}
        <h3 id="text-query-title" className="text-xl font-bold font-serif text-goa-cream mb-1">
          Type Your Question
        </h3>
        <p className="text-xs font-mono text-goa-cream/60 mb-4">
          Grounded against multilingual FAISS knowledge base
        </p>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. What is photosynthesis? or प्रकाश संश्लेषण क्या है?"
            rows={3}
            autoFocus
            className="w-full bg-goa-forest p-3.5 rounded-2xl text-sm text-goa-cream border border-goa-line/30 focus:outline-none focus:border-goa-pink placeholder:text-goa-cream/30 resize-none font-sans"
          />

          {/* Quick Suggestions */}
          <div>
            <span className="text-[10px] uppercase font-mono tracking-widest text-goa-yellow block mb-2 font-semibold">
              Suggested Questions
            </span>
            <div className="flex flex-wrap gap-1.5">
              {sampleSuggestions.map((s, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setQuery(s)}
                  className="text-xs px-2.5 py-1 rounded-full bg-goa-forest border border-goa-line/20 hover:border-goa-yellow/50 text-goa-cream/80 hover:text-goa-cream transition-all flex items-center gap-1"
                >
                  <Sparkles className="w-3 h-3 text-goa-yellow" />
                  <span>{s}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={!query.trim()}
              className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-goa-pink hover:bg-goa-pink/90 text-white font-mono text-xs font-bold shadow-lg shadow-goa-pink/30 disabled:opacity-40 transition-all"
            >
              <span>Submit Question</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
