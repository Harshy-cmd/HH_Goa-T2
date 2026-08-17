import React from 'react';
import { Mic, Square, Keyboard, Sparkles, RotateCcw } from 'lucide-react';
import { AppState } from '../types';

interface BottomSheetProps {
  state: AppState;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onOpenKeyboard: () => void;
  onReset: () => void;
  onSelectPrompt: (prompt: string) => void;
}

export const BottomSheet: React.FC<BottomSheetProps> = ({
  state,
  onStartRecording,
  onStopRecording,
  onOpenKeyboard,
  onReset,
  onSelectPrompt,
}) => {
  const isListening = state === 'LISTENING';
  const isProcessing = ['TRANSCRIBING', 'RETRIEVING', 'GENERATING'].includes(state);

  const samplePrompts = [
    'What is photosynthesis?',
    'प्रकाश संश्लेषण क्या है?',
    'What cities are in Calvert County?',
    'कैल्वर्ट काउंटी में कौन से शहर हैं?',
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 z-20 pb-4 pt-2 bg-gradient-to-t from-goa-forest-deep via-goa-forest-deep/95 to-transparent backdrop-blur-md">
      <div className="max-w-xl mx-auto px-4">
        {/* Quick Sample Prompts Strip if Idle */}
        {state === 'IDLE' && (
          <div className="flex items-center gap-2 overflow-x-auto pb-3 scrollbar-none justify-start sm:justify-center">
            {samplePrompts.map((p, idx) => (
              <button
                key={idx}
                onClick={() => onSelectPrompt(p)}
                className="whitespace-nowrap px-3 py-1 rounded-full text-xs font-mono bg-goa-cream/10 hover:bg-goa-cream/20 text-goa-cream/90 border border-goa-line/30 transition-all flex items-center gap-1.5"
              >
                <Sparkles className="w-3 h-3 text-goa-yellow" />
                <span>{p}</span>
              </button>
            ))}
          </div>
        )}

        {/* Main Dock Container */}
        <div className="bg-goa-cream text-goa-forest rounded-full p-2.5 sm:p-3 shadow-2xl flex items-center justify-between border-2 border-goa-cream/40">
          {/* 1. Keyboard / Type Query */}
          <button
            onClick={onOpenKeyboard}
            disabled={isListening || isProcessing}
            className="flex flex-col items-center justify-center w-12 h-12 rounded-full hover:bg-goa-forest/10 active:scale-95 text-goa-forest transition-all disabled:opacity-40"
            title="Type Question"
          >
            <Keyboard className="w-5 h-5" />
            <span className="text-[9px] font-mono uppercase font-bold tracking-tight mt-0.5">Type</span>
          </button>

          {/* 2. Big Hot Pink Microphone Action Button */}
          <div className="relative flex items-center justify-center">
            {isListening && (
              <span className="absolute w-20 h-20 rounded-full bg-goa-pink/30 animate-ping pointer-events-none" />
            )}
            <button
              onClick={isListening ? onStopRecording : onStartRecording}
              disabled={isProcessing}
              className={`w-16 h-16 sm:w-18 sm:h-18 rounded-full flex items-center justify-center shadow-xl transition-all duration-300 transform active:scale-90 ${
                isListening
                  ? 'bg-goa-pink text-white ring-4 ring-goa-pink/40 animate-pulse'
                  : isProcessing
                  ? 'bg-goa-yellow text-goa-forest animate-spin'
                  : 'bg-goa-pink hover:bg-goa-pink/90 text-white hover:scale-105 shadow-goa-pink/40'
              }`}
              title={isListening ? 'Stop Recording' : 'Start Voice Recording'}
            >
              {isListening ? (
                <Square className="w-7 h-7 fill-current" />
              ) : (
                <Mic className="w-8 h-8" />
              )}
            </button>
          </div>

          {/* 3. Reset / End Conversation */}
          <button
            onClick={onReset}
            disabled={isListening || isProcessing}
            className="flex flex-col items-center justify-center w-12 h-12 rounded-full hover:bg-goa-forest/10 active:scale-95 text-goa-forest transition-all disabled:opacity-40"
            title="Clear & Reset"
          >
            <RotateCcw className="w-5 h-5" />
            <span className="text-[9px] font-mono uppercase font-bold tracking-tight mt-0.5">Reset</span>
          </button>
        </div>

        {/* Pipeline Breadcrumb Caption */}
        <div className="text-center mt-2">
          <p className="text-[10px] font-mono uppercase tracking-widest text-goa-cream/60">
            Voice → FAISS Dense → Grounded LLM → Neural TTS
          </p>
        </div>
      </div>
    </div>
  );
};
