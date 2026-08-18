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

  return (
    <div className="w-full flex items-center justify-center gap-4 sm:gap-6 my-3 select-none">
      {/* SECONDARY ACTION: Type instead */}
      <button
        onClick={onOpenKeyboard}
        disabled={isListening || isProcessing}
        className="group flex items-center gap-2 px-4 py-2.5 rounded-full bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] hover:border-white/[0.16] text-[#F4EDD8]/75 hover:text-[#F4EDD8] text-xs font-mono font-medium transition-all duration-150 active:scale-95 disabled:opacity-25 disabled:pointer-events-none shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#EE2A6D]/60"
        title="Type your question instead"
        aria-label="Type your question instead"
      >
        <Keyboard className="w-3.5 h-3.5 text-[#F5C518]/70 group-hover:text-[#F5C518] transition-colors" />
        <span className="tracking-wide">Type instead</span>
      </button>

      {/* PRIMARY ACTION: Microphone Core Trigger */}
      <div className="relative flex items-center justify-center">
        {/* Active Ambient Halo (Restrained breathing outer halo, active ONLY while listening) */}
        {isListening && (
          <div
            className="absolute w-18 h-18 sm:w-20 sm:h-20 rounded-full bg-[#EE2A6D]/20 animate-pulse pointer-events-none"
            aria-hidden="true"
          />
        )}

        <button
          onClick={isListening ? onStopRecording : onStartRecording}
          disabled={isProcessing}
          className={`relative w-14 h-14 sm:w-16 sm:h-16 rounded-full flex items-center justify-center transition-all duration-200 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#EE2A6D] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0A2E22] ${
            isListening
              ? 'bg-[#EE2A6D] text-white ring-2 ring-[#EE2A6D]/50 shadow-md shadow-[#EE2A6D]/40'
              : isProcessing
              ? 'bg-[#0D3326]/80 text-[#F4EDD8]/40 border border-white/[0.08] cursor-not-allowed opacity-75'
              : 'bg-gradient-to-tr from-[#EE2A6D] to-[#f43f5e] hover:from-[#f43f5e] hover:to-[#fb7185] text-white border border-[#EE2A6D]/30 shadow-md shadow-[#EE2A6D]/25 hover:shadow-lg hover:shadow-[#EE2A6D]/35 hover:scale-[1.03]'
          }`}
          title={
            isListening
              ? 'Stop listening'
              : isProcessing
              ? 'Processing query…'
              : 'Start voice interaction'
          }
          aria-label={
            isListening
              ? 'Stop listening'
              : isProcessing
              ? 'Processing query'
              : 'Start voice interaction'
          }
        >
          {isListening ? (
            <Square className="w-5 h-5 sm:w-5.5 sm:h-5.5 fill-current text-white" />
          ) : isProcessing ? (
            <Mic className="w-6 h-6 sm:w-6.5 sm:h-6.5 text-[#F4EDD8]/40" />
          ) : (
            <Mic className="w-6 h-6 sm:w-6.5 sm:h-6.5 text-white" />
          )}
        </button>
      </div>

      {/* UTILITY ACTION: Reset */}
      <button
        onClick={onReset}
        disabled={isListening || isProcessing}
        className="group flex items-center gap-2 px-3.5 py-2.5 rounded-full bg-white/[0.025] hover:bg-white/[0.06] border border-white/[0.06] hover:border-white/[0.12] text-[#F4EDD8]/60 hover:text-[#F4EDD8]/90 text-xs font-mono font-medium transition-all duration-150 active:scale-95 disabled:opacity-25 disabled:pointer-events-none shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#EE2A6D]/60"
        title="Reset conversation and clear state"
        aria-label="Reset conversation"
      >
        <RotateCcw className="w-3.5 h-3.5 text-[#F4EDD8]/50 group-hover:text-[#F4EDD8]/80 transition-colors" />
        <span className="tracking-wide">Reset</span>
      </button>
    </div>
  );
};

export default VoiceControls;
