import React from 'react';
import { Settings as SettingsIcon, Sparkles, Menu } from 'lucide-react';
import { Settings } from '../types';

interface HeaderProps {
  isOnline: boolean;
  onOpenSettings: () => void;
  onOpenMenu?: () => void;
  settings: Settings;
  onUpdateSettings: (newSettings: Partial<Settings>) => void;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenSettings,
  onOpenMenu,
  settings,
  onUpdateSettings,
}) => {
  return (
    <header className="w-full flex items-center justify-between px-4 sm:px-8 py-3 border-b border-white/[0.05] bg-[#0A2E22]/30 backdrop-blur-md sticky top-0 z-30 select-none">
      {/* Mobile Brand Identity & Menu Toggle (Visible on mobile/tablet when sidebar is hidden) */}
      <div className="flex items-center gap-2 lg:invisible">
        <button
          onClick={onOpenMenu}
          className="w-8 h-8 rounded-xl flex items-center justify-center text-[#F4EDD8]/80 hover:text-[#F4EDD8] bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] transition-colors active:scale-95 lg:hidden focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#F5C518]"
          title="Open navigation menu"
          aria-label="Open navigation menu"
        >
          <Menu className="w-4 h-4" />
        </button>

        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#0F3D2E] to-[#0A2E22] border border-white/[0.12] flex items-center justify-center shadow-sm ml-1">
          <Sparkles className="w-3.5 h-3.5 text-[#F5C518]" />
        </div>
        <span className="text-xs font-bold tracking-[0.14em] text-[#F4EDD8] font-sans">
          NOVARON
        </span>
      </div>

      {/* Right Utility Group: Language Selector (EN | HI) & Settings Gear */}
      <div className="flex items-center gap-2.5 sm:gap-3 ml-auto">
        {/* Unified Segmented Language Control */}
        <div
          className="flex items-center rounded-full bg-white/[0.04] border border-white/[0.08] p-0.5 text-xs font-mono shadow-sm"
          role="radiogroup"
          aria-label="Interface Language"
        >
          <button
            onClick={() => onUpdateSettings({ language: 'en' })}
            role="radio"
            aria-checked={settings.language === 'en'}
            className={`px-2.5 sm:px-3 py-1 rounded-full text-xs font-mono font-medium transition-all duration-150 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#F5C518]/60 ${
              settings.language === 'en'
                ? 'bg-[#F4EDD8] text-[#0A2E22] font-bold shadow-sm'
                : 'text-[#F4EDD8]/60 hover:text-[#F4EDD8] hover:bg-white/[0.03]'
            }`}
            title="English"
          >
            EN
          </button>

          <span className="w-px h-3 bg-white/[0.08] mx-0.5" aria-hidden="true" />

          <button
            onClick={() => onUpdateSettings({ language: 'hi' })}
            role="radio"
            aria-checked={settings.language === 'hi'}
            className={`px-2.5 sm:px-3 py-1 rounded-full text-xs font-mono font-medium transition-all duration-150 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#F5C518]/60 ${
              settings.language === 'hi'
                ? 'bg-[#F4EDD8] text-[#0A2E22] font-bold shadow-sm'
                : 'text-[#F4EDD8]/60 hover:text-[#F4EDD8] hover:bg-white/[0.03]'
            }`}
            title="Hindi"
          >
            HI
          </button>
        </div>

        {/* Unified Settings Gear Button */}
        <button
          onClick={onOpenSettings}
          className="w-8 h-8 rounded-full flex items-center justify-center text-[#F4EDD8]/70 hover:text-[#F4EDD8] bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] hover:border-white/[0.16] transition-all duration-150 shadow-sm active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#F5C518]/60"
          title="System Settings"
          aria-label="System Settings"
        >
          <SettingsIcon className="w-4 h-4 text-[#F4EDD8]/70 group-hover:text-[#F4EDD8]" />
        </button>
      </div>
    </header>
  );
};

export default Header;
