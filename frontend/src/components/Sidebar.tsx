import React from 'react';
import { Mic, History, Database, Settings as SettingsIcon } from 'lucide-react';

interface SidebarProps {
  activeTab: 'ask' | 'history' | 'sources';
  onSelectTab: (tab: 'ask' | 'history' | 'sources') => void;
  onOpenSettings: () => void;
  historyCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  onOpenSettings,
  historyCount,
}) => {
  return (
    <aside className="hidden lg:flex flex-col justify-between w-60 bg-goa-forest-deep/80 border-r border-goa-line/30 p-5 shrink-0 select-none min-h-screen">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-full bg-goa-cream flex items-center justify-center shadow-lg border border-goa-cream/30">
            {/* Flower / Sun Geometric Icon */}
            <svg viewBox="0 0 24 24" className="w-6 h-6 text-goa-forest fill-current">
              <circle cx="12" cy="12" r="4" />
              <path d="M12 2C13.1 2 14 3.9 14 6C14 8.1 13.1 10 12 10C10.9 10 10 8.1 10 6C10 3.9 10.9 2 12 2Z" />
              <path d="M12 14C13.1 14 14 15.9 14 18C14 20.1 13.1 22 12 22C10.9 22 10 20.1 10 18C10 15.9 10.9 14 12 14Z" />
              <path d="M22 12C22 13.1 20.1 14 18 14C15.9 14 14 13.1 14 12C14 10.9 15.9 10 18 10C20.1 10 22 10.9 22 12Z" />
              <path d="M10 12C10 13.1 8.1 14 6 14C3.9 14 2 13.1 2 12C2 10.9 3.9 10 6 10C8.1 10 10 10.9 10 12Z" />
            </svg>
          </div>
          <div>
            <h1 className="text-base font-bold tracking-wider text-goa-cream font-sans">
              NOVARON
            </h1>
            <p className="text-[10px] font-mono tracking-widest text-goa-cream/60 uppercase">
              VOICE RAG · HH GOA 2026
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-2">
          {/* Ask / Mic */}
          <button
            onClick={() => onSelectTab('ask')}
            className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-xs font-mono font-semibold transition-all ${
              activeTab === 'ask'
                ? 'bg-goa-forest text-goa-pink border border-goa-pink/40 shadow-sm'
                : 'text-goa-cream/70 hover:text-goa-cream hover:bg-goa-forest/40'
            }`}
          >
            <Mic className={`w-4 h-4 ${activeTab === 'ask' ? 'text-goa-pink' : 'text-goa-cream/60'}`} />
            <span>Ask</span>
          </button>

          {/* History */}
          <button
            onClick={() => onSelectTab('history')}
            className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-2xl text-xs font-mono font-semibold transition-all ${
              activeTab === 'history'
                ? 'bg-goa-forest text-goa-cream border border-goa-line/40'
                : 'text-goa-cream/70 hover:text-goa-cream hover:bg-goa-forest/40'
            }`}
          >
            <div className="flex items-center gap-3">
              <History className="w-4 h-4 text-goa-cream/60" />
              <span>History</span>
            </div>
            {historyCount > 0 && (
              <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-goa-cream/10 text-goa-yellow">
                {historyCount}
              </span>
            )}
          </button>

          {/* Sources */}
          <button
            onClick={() => onSelectTab('sources')}
            className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-xs font-mono font-semibold transition-all ${
              activeTab === 'sources'
                ? 'bg-goa-forest text-goa-cream border border-goa-line/40'
                : 'text-goa-cream/70 hover:text-goa-cream hover:bg-goa-forest/40'
            }`}
          >
            <Database className="w-4 h-4 text-goa-cream/60" />
            <span>Sources</span>
          </button>

          {/* Settings */}
          <button
            onClick={onOpenSettings}
            className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-xs font-mono font-semibold text-goa-cream/70 hover:text-goa-cream hover:bg-goa-forest/40 transition-all"
          >
            <SettingsIcon className="w-4 h-4 text-goa-cream/60" />
            <span>Settings</span>
          </button>
        </nav>
      </div>

      {/* Bottom Goa Horizon Line Art */}
      <div className="pt-6 border-t border-goa-line/20">
        <div className="text-[10px] font-mono uppercase tracking-widest text-goa-cream/50 mb-2">
          VOICE RAG SYSTEM
        </div>
        <div className="relative w-full h-14 rounded-2xl bg-goa-forest/60 border border-goa-line/20 overflow-hidden flex items-end p-2 justify-between">
          {/* Sun setting */}
          <div className="absolute top-2 left-4 w-6 h-6 rounded-full bg-goa-yellow/80 shadow-md shadow-goa-yellow/30" />
          
          {/* Sea waves and palm line */}
          <svg viewBox="0 0 120 40" className="w-full h-full text-goa-cream/40 fill-none stroke-current" strokeWidth="1.2">
            {/* Palm tree silhouettes */}
            <path d="M95,38 Q90,20 85,12 Q80,25 95,38 Z" fill="rgba(244, 237, 216, 0.15)" stroke="none" />
            <path d="M100,38 Q102,15 108,10 Q112,24 100,38 Z" fill="rgba(244, 237, 216, 0.15)" stroke="none" />
            {/* Waves */}
            <path d="M0,32 Q15,28 30,32 T60,32 T90,32 T120,32" />
            <path d="M0,36 Q20,33 40,36 T80,36 T120,36" opacity="0.6" />
          </svg>
        </div>
      </div>
    </aside>
  );
};
