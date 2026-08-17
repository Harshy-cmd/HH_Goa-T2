import React, { useEffect } from 'react';
import { X, History, ArrowRight, Trash2, CheckCircle2, ShieldAlert } from 'lucide-react';
import { QueryResponse, VoiceQueryResponse } from '../types';

interface HistoryItem {
  id: string;
  timestamp: Date;
  query: string;
  data: QueryResponse | VoiceQueryResponse;
}

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  history: HistoryItem[];
  onSelectHistory: (item: HistoryItem) => void;
  onClearHistory: () => void;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  isOpen,
  onClose,
  history,
  onSelectHistory,
  onClearHistory,
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
      aria-labelledby="history-drawer-title"
      className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity"
    >
      <div className="w-full max-w-md bg-goa-forest-deep text-goa-cream h-full p-6 sm:p-8 overflow-y-auto border-l border-goa-line/30 shadow-2xl flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between pb-4 border-b border-goa-line/20 mb-6">
            <div className="flex items-center gap-2">
              <History className="w-5 h-5 text-goa-yellow" />
              <h2 id="history-drawer-title" className="text-lg font-bold font-serif tracking-wide">
                Session History
              </h2>
            </div>
            <button
              onClick={onClose}
              aria-label="Close History"
              className="p-1.5 rounded-full hover:bg-goa-cream/10 text-goa-cream/70"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {history.length === 0 ? (
            <div className="text-center py-16 text-goa-cream/50 font-mono text-xs">
              <History className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p>No questions asked in this session yet.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {history.map((item) => {
                const totalMs = item.data.latency_ms?.total || item.data.latency_ms?.rag_total || 0;
                const latencyFormatted = `${Math.round(totalMs)}ms`;
                const sourcesCount = item.data.sources?.length || 0;

                return (
                  <div
                    key={item.id}
                    onClick={() => {
                      onSelectHistory(item);
                      onClose();
                    }}
                    className="p-3.5 rounded-2xl bg-goa-forest border border-goa-line/30 hover:border-goa-yellow/50 cursor-pointer transition-all hover:scale-[1.01] group"
                  >
                    <div className="flex items-center justify-between text-[10px] font-mono mb-1.5">
                      <span className="text-goa-cream/50">
                        {item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      <div className="flex items-center gap-1.5">
                        {item.data.refused ? (
                          <span className="flex items-center gap-1 text-goa-pink font-semibold">
                            <ShieldAlert className="w-3 h-3" />
                            <span>REFUSED</span>
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>GROUNDED ({sourcesCount})</span>
                          </span>
                        )}
                        <span className="text-goa-yellow font-bold">· {latencyFormatted}</span>
                      </div>
                    </div>
                    <h4 className="text-sm font-semibold text-goa-cream group-hover:text-goa-yellow transition-colors line-clamp-1">
                      "{item.query}"
                    </h4>
                    <p className="text-xs text-goa-cream/70 font-sans line-clamp-2 mt-1">
                      {item.data.answer}
                    </p>
                    <div className="flex items-center justify-end text-[10px] font-mono text-goa-yellow font-bold mt-2 gap-1">
                      <span>Re-inspect</span>
                      <ArrowRight className="w-3 h-3" />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {history.length > 0 && (
          <div className="pt-4 border-t border-goa-line/20 flex justify-between items-center">
            <button
              onClick={onClearHistory}
              className="flex items-center gap-1.5 text-xs font-mono text-goa-pink hover:text-white px-3 py-1.5 rounded-full hover:bg-rose-900/50 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear History</span>
            </button>
            <span className="text-[11px] font-mono text-goa-cream/40">
              {history.length} items recorded
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
