import React, { useEffect } from 'react';
import { X, Sliders, Volume2, Globe, Database, Cpu, Server } from 'lucide-react';
import { Settings } from '../types';

interface SettingsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  settings: Settings;
  onUpdateSettings: (newSettings: Partial<Settings>) => void;
}

export const SettingsDrawer: React.FC<SettingsDrawerProps> = ({
  isOpen,
  onClose,
  settings,
  onUpdateSettings,
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
      aria-labelledby="settings-drawer-title"
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
              <Sliders className="w-5 h-5 text-[#F5C518]" />
              <div>
                <h2 id="settings-drawer-title" className="text-lg font-bold tracking-wide font-serif text-[#F4EDD8]">
                  Settings
                </h2>
                <p className="text-[10px] font-mono tracking-wider text-[#F4EDD8]/50 uppercase">
                  Preferences & RAG Engine
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              aria-label="Close Settings"
              className="p-1.5 rounded-full hover:bg-white/[0.08] text-[#F4EDD8]/60 hover:text-[#F4EDD8] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form Groups */}
          <div className="space-y-6 text-sm">
            {/* SECTION 1: VOICE & LANGUAGE PREFERENCES */}
            <div>
              <span className="text-[10px] uppercase font-mono tracking-wider text-[#F4EDD8]/45 block mb-3 font-semibold">
                Voice & Interaction
              </span>

              {/* Language Selection */}
              <div className="mb-4">
                <label className="flex items-center gap-1.5 font-mono text-xs text-[#F5C518] uppercase tracking-wider font-semibold mb-2">
                  <Globe className="w-3.5 h-3.5" />
                  <span>Language</span>
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['en', 'hi', 'auto'] as const).map((lang) => (
                    <button
                      key={lang}
                      onClick={() => onUpdateSettings({ language: lang })}
                      className={`py-2 px-3 rounded-xl text-xs font-mono font-semibold uppercase border transition-all duration-150 ${
                        settings.language === lang
                          ? 'bg-[#F4EDD8] text-[#0A2E22] border-[#F4EDD8] font-bold shadow-sm'
                          : 'bg-white/[0.03] border-white/[0.07] text-[#F4EDD8]/70 hover:bg-white/[0.06] hover:text-[#F4EDD8]'
                      }`}
                    >
                      {lang === 'en' ? 'English' : lang === 'hi' ? 'Hindi' : 'Auto'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Audio Synthesis Toggle */}
              <div className="flex items-center justify-between p-3.5 rounded-2xl bg-white/[0.03] border border-white/[0.07]">
                <div className="flex items-center gap-2.5">
                  <Volume2 className="w-4 h-4 text-[#F5C518]" />
                  <div>
                    <span className="text-xs font-mono font-semibold block text-[#F4EDD8]">
                      Speak Answers Aloud
                    </span>
                    <span className="text-[10px] font-mono text-[#F4EDD8]/50 block">
                      Neural TTS voice playback
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => onUpdateSettings({ synthesize_audio: !settings.synthesize_audio })}
                  className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors duration-200 ${
                    settings.synthesize_audio ? 'bg-[#EE2A6D]' : 'bg-black/30 border border-white/[0.12]'
                  }`}
                  aria-label="Toggle Audio Synthesis"
                >
                  <div
                    className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-200 ${
                      settings.synthesize_audio ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            </div>

            {/* SECTION 2: ADVANCED RAG CONFIGURATION */}
            <div className="pt-4 border-t border-white/[0.06]">
              <span className="text-[10px] uppercase font-mono tracking-wider text-[#F4EDD8]/45 block mb-3 font-semibold">
                RAG Engine Configuration
              </span>

              {/* Retrieval Mode */}
              <div className="mb-4">
                <label className="flex items-center gap-1.5 font-mono text-xs text-[#F5C518] uppercase tracking-wider font-semibold mb-2">
                  <Cpu className="w-3.5 h-3.5" />
                  <span>Retrieval Strategy</span>
                </label>
                <div className="grid grid-cols-2 gap-2 font-mono text-xs">
                  {(
                    [
                      { id: 'dense', label: 'Sentence FAISS' },
                      { id: 'bm25', label: 'Lexical BM25' },
                      { id: 'hybrid', label: 'Hybrid RRF' },
                      { id: 'hybrid_rerank', label: 'Hybrid + Rerank' },
                    ] as const
                  ).map((mode) => (
                    <button
                      key={mode.id}
                      onClick={() => onUpdateSettings({ retrieval_mode: mode.id })}
                      className={`py-2 px-3 rounded-xl font-medium border transition-all duration-150 text-left ${
                        settings.retrieval_mode === mode.id
                          ? 'bg-[#F4EDD8] text-[#0A2E22] font-bold border-[#F4EDD8] shadow-sm'
                          : 'bg-white/[0.03] border-white/[0.07] text-[#F4EDD8]/70 hover:bg-white/[0.06] hover:text-[#F4EDD8]'
                      }`}
                    >
                      {mode.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Chunking Strategy */}
              <div className="mb-4">
                <label className="flex items-center gap-1.5 font-mono text-xs text-[#F5C518] uppercase tracking-wider font-semibold mb-2">
                  <Database className="w-3.5 h-3.5" />
                  <span>Chunking Strategy</span>
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['sentence', 'fixed', 'hierarchical'] as const).map((strat) => (
                    <button
                      key={strat}
                      onClick={() => onUpdateSettings({ chunking_strategy: strat })}
                      className={`py-2 px-2.5 rounded-xl text-xs font-mono font-medium capitalize border transition-all duration-150 ${
                        settings.chunking_strategy === strat
                          ? 'bg-[#F5C518] text-[#0A2E22] font-bold border-[#F5C518] shadow-sm'
                          : 'bg-white/[0.03] border-white/[0.07] text-[#F4EDD8]/70 hover:bg-white/[0.06] hover:text-[#F4EDD8]'
                      }`}
                    >
                      {strat}
                    </button>
                  ))}
                </div>
              </div>

              {/* Top-K Evidence Passages Slider */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="font-mono text-xs text-[#F5C518] uppercase tracking-wider font-semibold">
                    Top-K Passages
                  </label>
                  <span className="font-mono text-xs font-bold text-[#F4EDD8] bg-white/[0.06] px-2.5 py-0.5 rounded-md border border-white/[0.08]">
                    {settings.top_k}
                  </span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={settings.top_k}
                  onChange={(e) => onUpdateSettings({ top_k: parseInt(e.target.value, 10) })}
                  className="w-full accent-[#EE2A6D] bg-black/30 h-2 rounded-lg cursor-pointer"
                />
              </div>
            </div>

            {/* SECTION 3: BACKEND ENDPOINT */}
            <div className="pt-4 border-t border-white/[0.06]">
              <span className="text-[10px] uppercase font-mono tracking-wider text-[#F4EDD8]/45 block mb-3 font-semibold">
                Connection
              </span>
              <div>
                <label className="flex items-center gap-1.5 font-mono text-xs text-[#F4EDD8]/75 uppercase tracking-wider font-semibold mb-2">
                  <Server className="w-3.5 h-3.5 text-[#F5C518]" />
                  <span>API Base URL</span>
                </label>
                <input
                  type="text"
                  value={settings.apiBaseUrl}
                  onChange={(e) => onUpdateSettings({ apiBaseUrl: e.target.value })}
                  placeholder="http://localhost:8000"
                  className="w-full bg-white/[0.03] p-3 rounded-2xl text-xs font-mono text-[#F4EDD8] border border-white/[0.08] focus:outline-none focus:border-[#EE2A6D] transition-colors"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-6 border-t border-white/[0.06] flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-full bg-[#F4EDD8] text-[#0A2E22] text-xs font-mono font-bold hover:bg-white transition-all shadow-sm active:scale-95"
          >
            Apply & Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsDrawer;
