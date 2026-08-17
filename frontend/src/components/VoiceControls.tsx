import React from 'react';
import { Mic, Square, Keyboard, RotateCcw } from 'lucide-react';
import { AppState } from '../types';

interface VoiceControlsProps {
  state: AppState;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onOpenKeyboard: () => void;
  onReset: () => void;
}

export const VoiceControls: React.FC<VoiceControlsProps> = ({
  state,
  onStartRecording,
  onStopRecording,
  onOpenKeyboard,
  onReset,
}) => {
  const isListening = state === 'LISTENING';
  const isProcessing = ['TRANSCRIBING', 'RETRIEVING', 'GENERATING'].includes(state);

  // Active step in the breadcrumb
  const getActiveStep = () => {
    if (isListening) return 'VOICE';
    if (state === 'TRANSCRIBING') return 'STT';
    if (state === 'RETRIEVING') return 'RETRIEVAL';
    if (state === 'GENERATING') return 'GROUNDING';
    if (state === 'PLAYING_AUDIO') return 'TTS';
    if (state === 'ANSWER_READY') return 'LLM';
    return null;
  };

  const activeStep = getActiveStep();
  const pipelineSteps = ['VOICE', 'STT', 'RETRIEVAL', 'GROUNDING', 'LLM', 'TTS'];

  return (
    <div className="w-full flex flex-col items-center justify-center my-4 select-none">
      {/* 3 Main Action Controls (Type - Mic - Reset) */}
      <div className="flex items-center justify-center gap-4 sm:gap-6 mb-4">
        {/* Left: Type Question Pill */}
        <button
          onClick={onOpenKeyboard}
          disabled={isListening || isProcessing}
          className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-goa-forest-deep/90 hover:bg-goa-cream/10 border border-goa-line/40 text-goa-cream text-xs font-mono font-semibold transition-all hover:scale-105 active:scale-95 disabled:opacity-40 shadow-md"
        >
          <Keyboard className="w-3.5 h-3.5 text-goa-yellow" />
          <span className="hidden sm:inline">TYPE QUESTION</span>
          <span className="sm:hidden">TYPE</span>
        </button>

        {/* Center: Glowing Hot Pink Microphone Button */}
        <div className="relative flex items-center justify-center">
          {/* Ambient Outer Halo */}
          <div className={`absolute w-20 h-20 rounded-full transition-all duration-500 ${
            isListening
              ? 'bg-goa-pink/40 animate-ping'
              : 'bg-goa-pink/20 blur-md group-hover:bg-goa-pink/30'
          }`} />

          <button
            onClick={isListening ? onStopRecording : onStartRecording}
            disabled={isProcessing}
            className={`relative w-16 h-16 sm:w-18 sm:h-18 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 transform active:scale-90 ${
              isListening
                ? 'bg-goa-pink text-white ring-4 ring-goa-pink/50 animate-pulse shadow-goa-pink/60'
                : isProcessing
                ? 'bg-goa-yellow text-goa-forest shadow-goa-yellow/40 animate-spin'
                : 'bg-goa-pink hover:bg-goa-pink/90 text-white hover:scale-105 shadow-lg shadow-goa-pink/40'
            }`}
            title={isListening ? 'Stop Recording' : 'Start Voice Recording'}
          >
            {isListening ? (
              <Square className="w-6 h-6 fill-current" />
            ) : (
              <Mic className="w-7 h-7" />
            )}
          </button>
        </div>

        {/* Right: Reset Pill */}
        <button
          onClick={onReset}
          disabled={isListening || isProcessing}
          className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-goa-forest-deep/90 hover:bg-goa-cream/10 border border-goa-line/40 text-goa-cream text-xs font-mono font-semibold transition-all hover:scale-105 active:scale-95 disabled:opacity-40 shadow-md"
        >
          <RotateCcw className="w-3.5 h-3.5 text-goa-cream/70" />
          <span>RESET</span>
        </button>
      </div>

      {/* Pipeline Breadcrumb Bar */}
      <div className="inline-flex items-center gap-1 sm:gap-2 px-3 sm:px-4 py-1.5 rounded-full bg-goa-forest-deep/70 border border-goa-line/25 text-[10px] sm:text-xs font-mono shadow-inner">
        {pipelineSteps.map((step, idx) => (
          <React.Fragment key={step}>
            <span
              className={`font-semibold tracking-wider transition-colors ${
                activeStep === step
                  ? 'text-goa-pink font-bold underline underline-offset-4'
                  : 'text-goa-cream/50'
              }`}
            >
              {step}
            </span>
            {idx < pipelineSteps.length - 1 && (
              <span className="text-goa-cream/30">→</span>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
