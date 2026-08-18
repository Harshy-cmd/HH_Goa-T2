import React from 'react';
import { Mic, History, Database } from 'lucide-react';

interface SidebarProps {
  activeTab: 'ask' | 'history' | 'sources' | 'settings';
  onSelectTab: (tab: 'ask' | 'history' | 'sources') => void;
  historyCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  historyCount,
}) => {
  const navItems = [
    {
      id: 'ask' as const,
      label: 'Ask',
      icon: Mic,
      onClick: () => onSelectTab('ask'),
      isActive: activeTab === 'ask',
      badge: null,
    },
    {
      id: 'history' as const,
      label: 'History',
      icon: History,
      onClick: () => onSelectTab('history'),
      isActive: activeTab === 'history',
      badge: historyCount > 0 ? historyCount : null,
    },
    {
      id: 'sources' as const,
      label: 'Sources',
      icon: Database,
      onClick: () => onSelectTab('sources'),
      isActive: activeTab === 'sources',
      badge: null,
    },
  ];

  return (
    <aside className="hidden lg:flex flex-col justify-between w-60 bg-[#0A2E22]/90 border-r border-white/[0.06] p-5 shrink-0 select-none min-h-screen backdrop-blur-xl relative z-50">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 mb-8 px-1">
          {/* Geometric NOVARON Brand Mark */}
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#0F3D2E] via-[#0A2E22] to-[#08231a] border border-white/[0.12] flex items-center justify-center shadow-md relative overflow-hidden group shrink-0">
            <div className="absolute inset-0 bg-gradient-to-tr from-[#EE2A6D]/20 via-transparent to-[#F5C518]/25 opacity-70 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="w-3.5 h-3.5 rounded-full bg-gradient-to-tr from-[#F4EDD8] to-[#F5C518] shadow-sm relative z-10 flex items-center justify-center">
              <div className="w-1.5 h-1.5 rounded-full bg-[#0A2E22]" />
            </div>
          </div>

          <div>
            <h1 className="text-sm font-bold tracking-[0.14em] text-[#F4EDD8] font-sans leading-none">
              NOVARON
            </h1>
            <p className="text-[9px] font-mono tracking-[0.18em] text-[#F4EDD8]/50 uppercase mt-1">
              VOICE RAG · HH GOA 2026
            </p>
          </div>
        </div>

        {/* Navigation Rail: Ask, History, Sources */}
        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={item.onClick}
                className={`w-full h-11 flex items-center justify-between px-3.5 rounded-xl text-xs font-mono transition-all duration-150 relative group focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#EE2A6D]/60 ${
                  item.isActive
                    ? 'bg-white/[0.04] text-[#F4EDD8] font-semibold border border-white/[0.07] shadow-sm'
                    : 'text-[#F4EDD8]/60 hover:text-[#F4EDD8] hover:bg-white/[0.025] border border-transparent font-medium'
                }`}
              >
                {/* Active Left Vertical Accent Line (2.5px wide, #EE2A6D) */}
                {item.isActive && (
                  <span
                    className="absolute left-0 top-2 bottom-2 w-[2.5px] rounded-r-sm bg-[#EE2A6D]"
                    aria-hidden="true"
                  />
                )}

                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 transition-colors duration-150 ${
                      item.isActive
                        ? 'text-[#EE2A6D]'
                        : 'text-[#F4EDD8]/50 group-hover:text-[#F4EDD8]/80'
                    }`}
                  />
                  <span className="tracking-wide">{item.label}</span>
                </div>

                {/* History Count Badge */}
                {item.badge !== null && (
                  <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-md bg-white/[0.06] text-[#F4EDD8]/70 border border-white/[0.05] group-hover:text-[#F4EDD8] group-hover:border-white/[0.10] transition-colors">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Clean Minimal Footer */}
      <div className="pt-4 border-t border-white/[0.05] text-[10px] font-mono text-[#F4EDD8]/30 flex items-center justify-between tracking-wider">
        <span>HH GOA 2026</span>
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400/70" title="System Ready" />
      </div>
    </aside>
  );
};

export default Sidebar;
