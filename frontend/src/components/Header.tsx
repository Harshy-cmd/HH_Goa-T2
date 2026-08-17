import React from 'react';
import { Settings as SettingsIcon } from 'lucide-react';
import { Settings } from '../types';

interface HeaderProps {
  isOnline: boolean;
  onOpenSettings: () => void;
  settings: Settings;
  onUpdateSettings: (newSettings: Partial<Settings>) => void;
}

export const Header: React.FC<HeaderProps> = ({
  isOnline,
  onOpenSettings,
  settings,
  onUpdateSettings,
}) => {
  return (
    <header className="w-full flex items-center justify-between px-4 sm:px-8 py-3.5 border-b border-goa-line/30 bg-goa-forest-deep/60 backdrop-blur-md sticky top-0 z-30 select-none">
      {/* Brand (Visible on mobile/tablet) */}
      <div className="flex items-center gap-3 lg:invisible">
        <div className="w-8 h-8 rounded-full bg-goa-cream flex items-center justify-center shadow-md">
          {/* Flower / Sun Geometric Icon */}
          <svg viewBox="0 0 24 24" className="w-5 h-5 text-goa-forest fill-current">
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2C13.1 2 14 3.9 14 6C14 8.1 13.1 10 12 10C10.9 10 10 8.1 10 6C10 3.9 10.9 2 12 2Z" />
            <path d="M12 14C13.1 14 14 15.9 14 18C14 20.1 13.1 22 12 22C10.9 22 10 20.1 10 18C10 15.9 10.9 14 12 14Z" />
            <path d="M22 12C22 13.1 20.1 14 18 14C15.9 14 14 13.1 14 12C14 10.9 15.9 10 18 10C20.1 10 22 10.9 22 12Z" />
            <path d="M10 12C10 13.1 8.1 14 6 14C3.9 14 2 13.1 2 12C2 10.9 3.9 10 6 10C8.1 10 10 10.9 10 12Z" />
          </svg>
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-wider text-goa-cream">
            NOVARON
          </h1>
          <p className="text-[9px] font-mono tracking-widest text-goa-cream/60 uppercase">
            VOICE RAG · HH GOA 2026
          </p>
        </div>
      </div>

      {/* Right Controls: RAG ONLINE, EN | HI toggle, Settings */}
      <div className="flex items-center gap-3 ml-auto">
        {/* Status Pill */}
        <div
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-mono border transition-all ${
            isOnline
              ? 'bg-emerald-950/70 border-emerald-500/40 text-emerald-300 shadow-sm'
              : 'bg-rose-950/70 border-rose-500/40 text-rose-300'
          }`}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              isOnline ? 'bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400' : 'bg-rose-400'
            }`}
          />
          <span className="font-semibold text-[11px] tracking-wide">
            {isOnline ? '● RAG ONLINE' : '○ RAG OFFLINE'}
          </span>
        </div>

        {/* Language Segmented Toggle (EN | HI) */}
        <div className="flex items-center rounded-full bg-goa-forest-deep border border-goa-line/40 p-0.5 text-xs font-mono">
          <button
            onClick={() => onUpdateSettings({ language: 'en' })}
            className={`px-2.5 py-1 rounded-full transition-all ${
              settings.language === 'en'
                ? 'bg-goa-cream text-goa-forest font-bold shadow-sm'
                : 'text-goa-cream/70 hover:text-goa-cream'
            }`}
          >
            EN
          </button>
          <span className="text-goa-line/50 text-[10px] px-0.5">|</span>
          <button
            onClick={() => onUpdateSettings({ language: 'hi' })}
            className={`px-2.5 py-1 rounded-full transition-all ${
              settings.language === 'hi'
                ? 'bg-goa-cream text-goa-forest font-bold shadow-sm'
                : 'text-goa-cream/70 hover:text-goa-cream'
            }`}
          >
            HI
          </button>
        </div>

        {/* Settings Gear Button */}
        <button
          onClick={onOpenSettings}
          className="p-2 rounded-full text-goa-cream/80 hover:text-goa-cream hover:bg-goa-cream/10 transition-colors border border-goa-line/30"
          title="Settings"
        >
          <SettingsIcon className="w-4 h-4 text-goa-cream/70 hover:text-goa-cream" />
        </button>
      </div>
    </header>
  );
};
