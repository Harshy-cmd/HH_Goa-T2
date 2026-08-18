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

  const formatTimestamp = (date: Date) => {
    try {
      const now = new Date();
      const isToday =
        date.getDate() === now.getDate() &&
        date.getMonth() === now.getMonth() &&
        date.getFullYear() === now.getFullYear();

      const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      return isToday ? `Today · ${timeStr}` : `${date.toLocaleDateString([], { month: 'short', day: 'numeric' })} · ${timeStr}`;
    } catch {
      return 'Recent';
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="history-drawer-title"
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
              <History className="w-5 h-5 text-[#F5C518]" />
              <div>
                <h2 id="history-drawer-title" className="text-lg font-bold font-serif tracking-wide text-[#F4EDD8]">
                  Session History
                </h2>
                <p className="text-[10px] font-mono tracking-wider text-[#F4EDD8]/50 uppercase">
                  Your conversations with NOVARON
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              aria-label="Close History"
              className="p-1.5 rounded-full hover:bg-white/[0.08] text-[#F4EDD8]/60 hover:text-[#F4EDD8] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Conversation List */}
          {history.length === 0 ? (
            <div className="text-center py-20 px-4 text-[#F4EDD8]/50 font-mono text-xs space-y-2.5">
              <History className="w-9 h-9 mx-auto opacity-30 text-[#F5C518] mb-2" />
              <p className="font-semibold text-sm text-[#F4EDD8]/80">No conversations yet</p>
              <p className="text-[11px] text-[#F4EDD8]/45 font-sans leading-relaxed max-w-xs mx-auto">
                Your recent voice sessions will appear here.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {history.map((item) => {
                const isRefused = item.data.refused;

                return (
                  <div
                    key={item.id}
                    onClick={() => {
                      onSelectHistory(item);
                      onClose();
                    }}
                    className="relative p-4 rounded-2xl bg-white/[0.03] border border-white/[0.07] hover:border-white/[0.15] hover:bg-white/[0.055] cursor-pointer transition-all duration-150 group shadow-sm overflow-hidden"
                  >
                    {/* Subtle Pink Left Hover Accent */}
                    <span
                      className="absolute left-0 top-3 bottom-3 w-[2.5px] bg-[#EE2A6D] rounded-r opacity-0 group-hover:opacity-100 transition-opacity duration-150"
                      aria-hidden="true"
                    />

                    {/* Question Title (Primary, max 2 lines) */}
                    <h4 className="text-sm font-medium text-[#F4EDD8] group-hover:text-[#F5C518] transition-colors line-clamp-2 leading-snug mb-2">
                      "{item.query}"
                    </h4>

                    {/* Bottom Secondary Metadata Row */}
                    <div className="flex items-center justify-between text-[11px] font-mono text-[#F4EDD8]/50 pt-1 border-t border-white/[0.04]">
                      <span>{formatTimestamp(item.timestamp)}</span>
                      <div className="flex items-center gap-2">
                        {isRefused ? (
                          <span className="flex items-center gap-1 text-[#EE2A6D] text-[10px] font-medium">
                            <ShieldAlert className="w-3 h-3" />
                            <span>Refusal</span>
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-emerald-400 text-[10px] font-medium">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>Grounded</span>
                          </span>
                        )}
                        <ArrowRight className="w-3 h-3 text-[#F5C518]/60 group-hover:text-[#F5C518] group-hover:translate-x-0.5 transition-transform" />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Quiet Clear History Footer */}
        {history.length > 0 && (
          <div className="pt-4 border-t border-white/[0.06] flex justify-between items-center mt-6">
            <button
              onClick={onClearHistory}
              className="flex items-center gap-1.5 text-xs font-mono text-[#EE2A6D]/80 hover:text-white px-3 py-1.5 rounded-full hover:bg-rose-950/70 border border-[#EE2A6D]/25 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear History</span>
            </button>
            <span className="text-[11px] font-mono text-[#F4EDD8]/40">
              {history.length} {history.length === 1 ? 'item' : 'items'} saved
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryDrawer;
