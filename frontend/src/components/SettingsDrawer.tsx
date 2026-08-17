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
  // Close on Escape key
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
      className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity"
    >
      <div className="w-full max-w-md bg-goa-forest-deep text-goa-cream h-full p-6 sm:p-8 overflow-y-auto border-l border-goa-line/30 shadow-2xl flex flex-col justify-between">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-goa-line/20 mb-6">
            <div className="flex items-center gap-2">
              <Sliders className="w-5 h-5 text-goa-yellow" />
              <h2 id="settings-drawer-title" className="text-lg font-bold tracking-wider font-serif">
                System Settings
              </h2>
            </div>
            <button
              onClick={onClose}
              aria-label="Close Settings"
              className="p-1.5 rounded-full hover:bg-goa-cream/10 text-goa-cream/70 hover:text-goa-cream transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form Groups */}
          <div className="space-y-6 text-sm">
            {/* SECTION 1: USER SETTINGS */}
            <div>
              <span className="text-[10px] uppercase font-mono tracking-widest text-goa-cream/50 block mb-3 font-semibold">
                User Settings
              </span>

              {/* Language */}
              <div className="mb-4">
                <label className="flex items-center gap-1.5 font-mono text-xs text-goa-yellow uppercase tracking-wider font-semibold mb-2">
                  <Globe className="w-3.5 h-3.5" />
                  <span>Language</span>
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['en', 'hi', 'auto'] as const).map((lang) => (
                    <button
                      key={lang}
                      onClick={() => onUpdateSettings({ language: lang })}
                      className={`py-2 px-3 rounded-xl text-xs font-mono font-semibold uppercase border transition-all ${
                        settings.language === lang
                          ? 'bg-goa-pink text-white border-goa-pink shadow-md'
                          : 'bg-goa-forest/60 border-goa-line/30 text-goa-cream/80 hover:bg-goa-cream/10'
                      }`}
                    >
                      {lang === 'en' ? 'English' : lang === 'hi' ? 'Hindi' : 'Auto'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Audio Synthesis Toggle */}
              <div className="flex items-center justify-between p-3.5 rounded-2xl bg-goa-forest/70 border border-goa-line/30">
                <div className="flex items-center gap-2.5">
                  <Volume2 className="w-4 h-4 text-goa-yellow" />
                  <div>
                    <span className="text-xs font-mono font-bold block text-goa-cream">
                      Speak Answers Aloud
                    </span>
                    <span className="text-[10px] font-mono text-goa-cream/60 block">
                      Neural TTS (EdgeTTS Swara/Jenny)
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => onUpdateSettings({ synthesize_audio: !settings.synthesize_audio })}
                  className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors duration-300 ${
                    settings.synthesize_audio ? 'bg-goa-pink' : 'bg-goa-forest-deep border border-goa-line/40'
                  }`}
                >
                  <div
                    className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-300 ${
                      settings.synthesize_audio ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            </div>

            {/* SECTION 2: ADVANCED RAG CONFIGURATION */}
            <div className="pt-4 border-t border-goa-line/20">
              <span className="text-[10px] uppercase font-mono tracking-widest text-goa-cream/50 block mb-3 font-semibold">
                Advanced RAG Configuration
              </span>

              {/* Retrieval Mode */}
              <div className="mb-4">
                <label className="flex items-center gap-1.5 font-mono text-xs text-goa-yellow uppercase tracking-wider font-semibold mb-2">
                  <Cpu className="w-3.5 h-3.5" />
                  <span>Retrieval Mode</span>
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
                      className={`py-2.5 px-3 rounded-xl font-semibold border transition-all text-left ${
                        settings.retrieval_mode === mode.id
                          ? 'bg-goa-cream text-goa-forest font-bold border-goa-cream shadow-md'
                          : 'bg-goa-forest/60 border-goa-line/30 text-goa-cream/80 hover:bg-goa-cream/10'
                      }`}
                    >
                      {mode.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Chunking Strategy */}
              <div className="mb-4">
                <label className="flex items-center gap-1.5 font-mono text-xs text-goa-yellow uppercase tracking-wider font-semibold mb-2">
                  <Database className="w-3.5 h-3.5" />
                  <span>Chunking Strategy</span>
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['sentence', 'fixed', 'hierarchical'] as const).map((strat) => (
                    <button
                      key={strat}
                      onClick={() => onUpdateSettings({ chunking_strategy: strat })}
                      className={`py-2 px-2.5 rounded-xl text-xs font-mono font-semibold capitalize border transition-all ${
                        settings.chunking_strategy === strat
                          ? 'bg-goa-yellow text-goa-forest font-bold border-goa-yellow shadow-md'
                          : 'bg-goa-forest/60 border-goa-line/30 text-goa-cream/80 hover:bg-goa-cream/10'
                      }`}
                    >
                      {strat}
                    </button>
                  ))}
                </div>
              </div>

              {/* Top-K Slider */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="font-mono text-xs text-goa-yellow uppercase tracking-wider font-semibold">
                    Top-K Evidence Passages
                  </label>
                  <span className="font-mono text-xs font-bold text-goa-cream bg-goa-forest px-2 py-0.5 rounded border border-goa-line/30">
                    {settings.top_k}
                  </span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={settings.top_k}
                  onChange={(e) => onUpdateSettings({ top_k: parseInt(e.target.value, 10) })}
                  className="w-full accent-goa-pink bg-goa-forest h-2 rounded-lg cursor-pointer"
                />
              </div>
            </div>

            {/* SECTION 3: DEVELOPER */}
            <div className="pt-4 border-t border-goa-line/20">
              <span className="text-[10px] uppercase font-mono tracking-widest text-goa-cream/50 block mb-3 font-semibold">
                Developer
              </span>
              <div>
                <label className="flex items-center gap-1.5 font-mono text-xs text-goa-cream/80 uppercase tracking-wider font-semibold mb-1.5">
                  <Server className="w-3.5 h-3.5 text-goa-yellow" />
                  <span>Backend Server URL</span>
                </label>
                <input
                  type="text"
                  value={settings.apiBaseUrl}
                  onChange={(e) => onUpdateSettings({ apiBaseUrl: e.target.value })}
                  placeholder="http://localhost:8000"
                  className="w-full bg-goa-forest p-2.5 rounded-xl text-xs font-mono text-goa-cream border border-goa-line/30 focus:outline-none focus:border-goa-pink"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-6 border-t border-goa-line/20 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-full bg-goa-cream text-goa-forest text-xs font-mono font-bold hover:bg-white shadow-lg transition-all"
          >
            Apply & Close
          </button>
        </div>
      </div>
    </div>
  );
};
