import React from 'react';
import { AppState } from '../types';
import { SparkleIcon } from './Sparkles';
import { ShieldAlert, CheckCircle2, Circle, Loader2 } from 'lucide-react';

interface VoiceOrbProps {
  state: AppState;
  audioLevel: number; // 0.0 to 1.0
  stageLabel?: string;
  onClick?: () => void;
  compact?: boolean;
}

export const VoiceOrb: React.FC<VoiceOrbProps> = ({
  state,
  audioLevel,
  stageLabel,
  onClick,
  compact = false,
}) => {
  const isListening = state === 'LISTENING';
  const isTranscribing = state === 'TRANSCRIBING';
  const isRetrieving = state === 'RETRIEVING';
  const isGenerating = state === 'GENERATING';
  const isPlayingAudio = state === 'PLAYING_AUDIO';
  const isRefused = state === 'REFUSED';
  const isAnswerReady = state === 'ANSWER_READY';

  // Responsive Orb Dimensions
  const orbDimension = compact
    ? 'w-36 h-36 sm:w-44 sm:h-44'
    : isListening
    ? 'w-64 h-64 sm:w-76 sm:h-76'
    : 'w-56 h-56 sm:w-68 sm:h-68';

  // Waveform Bar Heights (for horizontal audio reactive visualization)
  const leftBars = Array.from({ length: 12 }).map((_, i) => {
    if (isListening) {
      const offset = (i / 12) * 0.4;
      const val = Math.max(0.1, (audioLevel * 1.5 + offset) % 1);
      return Math.min(60, Math.max(6, val * 55));
    }
    if (isPlayingAudio) {
      return 8 + Math.sin(Date.now() / 180 + i * 0.6) * 18;
    }
    return 3;
  });

  const rightBars = [...leftBars].reverse();

  return (
    <div className={`relative flex flex-col items-center justify-center transition-all duration-700 select-none ${compact ? 'py-2' : 'py-6 sm:py-8'}`}>
      {/* Decorative Floating Sparkles (Idle & Processing) */}
      {!compact && (
        <>
          <div className="absolute -top-3 left-4 sm:left-12 animate-sparkle">
            <SparkleIcon className="w-5 h-5 text-goa-yellow/80" />
          </div>
          <div className="absolute top-1/2 -right-2 sm:right-6 animate-sparkle" style={{ animationDelay: '2.5s' }}>
            <SparkleIcon className="w-6 h-6 text-goa-pink/70" />
          </div>
        </>
      )}

      {/* Main Interactive Stage with Flanking Horizontal Waveforms */}
      <div className="relative flex items-center justify-center">
        {/* Left Horizontal Waveform (during Listening / Audio Playback) */}
        {(isListening || isPlayingAudio) && !compact && (
          <div className="hidden sm:flex items-center gap-1.5 mr-4 pointer-events-none">
            {leftBars.map((h, i) => (
              <div
                key={i}
                style={{ height: `${h}px` }}
                className={`w-1 rounded-full transition-all duration-75 ${
                  isListening ? 'bg-emerald-400/80 shadow-sm shadow-emerald-400' : 'bg-goa-yellow/80'
                }`}
              />
            ))}
          </div>
        )}

        {/* Central Organic Layered Orb */}
        <div
          onClick={onClick}
          className={`relative ${orbDimension} flex items-center justify-center cursor-pointer group transition-all duration-700`}
        >
          {/* Radar Waves / Ambient Glow */}
          {isListening && (
            <>
              <div className="absolute inset-0 rounded-full border-2 border-goa-pink/40 animate-radar-ring pointer-events-none" />
              <div className="absolute -inset-4 rounded-full border border-goa-pink/30 animate-radar-ring pointer-events-none" style={{ animationDelay: '0.7s' }} />
              <div className="absolute -inset-8 rounded-full border border-goa-pink/20 animate-radar-ring pointer-events-none" style={{ animationDelay: '1.4s' }} />
            </>
          )}

          {/* Layer 1: Outer Cream Organic Layer */}
          <div className={`absolute inset-0 bg-goa-cream shadow-2xl transition-all duration-700 ${
            isListening ? 'animate-blob-1 ring-4 ring-goa-pink/40 shadow-goa-pink/40' : 'animate-blob-1'
          }`} />

          {/* Layer 2: Middle Fluid Ring with Pink / Gold Accents */}
          <div className="absolute inset-1.5 sm:inset-2 bg-gradient-to-tr from-goa-cream via-goa-yellow/30 to-goa-pink/30 shadow-inner animate-blob-2" />

          {/* Layer 3: Inner Contour */}
          <div className="absolute inset-3 sm:inset-4 bg-goa-cream animate-blob-3 shadow-md" />

          {/* Inner Dark Forest Disc & Sun Core */}
          <div className="relative w-3/5 h-3/5 rounded-full bg-goa-forest-deep flex items-center justify-center border-2 border-goa-cream/30 shadow-2xl overflow-hidden z-10">
            {/* Ambient Radial Gradient */}
            <div className={`absolute inset-0 transition-opacity duration-700 ${
              isRefused
                ? 'bg-gradient-to-tr from-rose-900/50 to-transparent opacity-100'
                : isListening
                ? 'bg-gradient-to-tr from-goa-pink/40 to-goa-yellow/30 opacity-100'
                : 'bg-gradient-to-tr from-goa-yellow/20 to-transparent opacity-60'
            }`} />

            {/* Glyph Inside Disc */}
            {isRefused ? (
              <ShieldAlert className="w-8 h-8 sm:w-10 sm:h-10 text-goa-pink animate-pulse" />
            ) : isRetrieving || isGenerating ? (
              <div className="flex flex-col items-center justify-center">
                <Loader2 className="w-8 h-8 text-goa-yellow animate-spin" />
              </div>
            ) : (
              /* Sun Core with Radiating Rays */
              <svg viewBox="0 0 100 100" className={`w-12 h-12 sm:w-16 sm:h-16 text-goa-yellow transition-transform duration-700 ${
                isPlayingAudio ? 'scale-110 text-goa-yellow' : isListening ? 'scale-110 text-goa-pink' : ''
              }`}>
                <circle cx="50" cy="50" r="18" fill="currentColor" />
                {[0, 45, 90, 135, 180, 225, 270, 315].map((angle) => (
                  <line
                    key={angle}
                    x1="50"
                    y1="22"
                    x2="50"
                    y2="10"
                    stroke={isListening ? '#EE2A6D' : '#F5C518'}
                    strokeWidth="4"
                    strokeLinecap="round"
                    transform={`rotate(${angle} 50 50)`}
                  />
                ))}
              </svg>
            )}
          </div>
        </div>

        {/* Right Horizontal Waveform (during Listening / Audio Playback) */}
        {(isListening || isPlayingAudio) && !compact && (
          <div className="hidden sm:flex items-center gap-1.5 ml-4 pointer-events-none">
            {rightBars.map((h, i) => (
              <div
                key={i}
                style={{ height: `${h}px` }}
                className={`w-1 rounded-full transition-all duration-75 ${
                  isListening ? 'bg-emerald-400/80 shadow-sm shadow-emerald-400' : 'bg-goa-yellow/80'
                }`}
              />
            ))}
          </div>
        )}
      </div>

      {/* State Caption & Stage Feedback */}
      {!compact && (
        <div className="mt-4 text-center max-w-sm px-4">
          {isListening && (
            <p className="text-xs sm:text-sm font-mono tracking-wider text-goa-pink font-semibold flex items-center justify-center gap-2">
              <span className="w-2 h-2 rounded-full bg-goa-pink animate-ping" />
              <span>I'm listening…</span>
            </p>
          )}

          {isTranscribing && (
            <p className="text-xs sm:text-sm font-mono tracking-wider text-goa-yellow font-medium">
              Turning your voice into a question…
            </p>
          )}

          {isRetrieving && (
            <div className="text-left bg-goa-forest-deep/90 border border-goa-line/30 p-3 rounded-2xl font-mono text-[11px] space-y-1.5 shadow-lg">
              <div className="flex items-center gap-2 text-emerald-400 font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Speech recognized</span>
              </div>
              <div className="flex items-center gap-2 text-goa-yellow font-bold animate-pulse">
                <span className="w-3.5 h-3.5 flex items-center justify-center">●</span>
                <span>Searching knowledge (FAISS)</span>
              </div>
              <div className="flex items-center gap-2 text-goa-cream/40">
                <Circle className="w-3.5 h-3.5" />
                <span>Verifying evidence grounding</span>
              </div>
              <div className="flex items-center gap-2 text-goa-cream/40">
                <Circle className="w-3.5 h-3.5" />
                <span>Generating grounded answer</span>
              </div>
            </div>
          )}

          {isGenerating && (
            <p className="text-xs sm:text-sm font-mono tracking-wider text-goa-yellow font-medium animate-pulse">
              Checking the evidence before I answer…
            </p>
          )}

          {state === 'IDLE' && (
            <p className="text-xs font-mono text-goa-cream/60 tracking-wider">
              Tap the microphone or ask anything.
            </p>
          )}
        </div>
      )}
    </div>
  );
};
