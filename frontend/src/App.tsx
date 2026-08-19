import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { VoiceOrb } from './components/VoiceOrb';
import { VoiceControls } from './components/VoiceControls';
import { AnswerCard } from './components/AnswerCard';
import { RefusalCard } from './components/RefusalCard';
import { SettingsDrawer } from './components/SettingsDrawer';
import { HistoryDrawer } from './components/HistoryDrawer';
import { SourcesDrawer } from './components/SourcesDrawer';
import { TextQueryModal } from './components/TextQueryModal';
import { ShareModal } from './components/ShareModal';
import { Mic, History as HistoryIcon, Database, X } from 'lucide-react';
import { checkHealth, queryText, queryVoice, synthesizeSpeech, DEFAULT_API_BASE_URL } from './services/api';
import { AppState, QueryResponse, VoiceQueryResponse, Settings } from './types';

// End-of-Speech & Voice Activity Detection Configuration
export const END_OF_SPEECH_SILENCE_MS = 1500; // 1.5 seconds of sustained silence after speaking
export const MIN_SPEECH_DURATION_MS = 250;     // Minimum vocal duration (ms) to confirm speech onset
export const MAX_RECORDING_DURATION_MS = 30000; // Safety cutoff at 30 seconds

interface HistoryItem {
  id: string;
  timestamp: Date;
  query: string;
  data: QueryResponse | VoiceQueryResponse;
}

export const App: React.FC = () => {
  // State Machine
  const [appState, setAppState] = useState<AppState>('IDLE');
  const [response, setResponse] = useState<QueryResponse | VoiceQueryResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [stageLabel, setStageLabel] = useState<string>('Processing...');

  // Navigation & Drawers
  const [activeTab, setActiveTab] = useState<'ask' | 'history' | 'sources' | 'settings'>('ask');
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isSourcesOpen, setIsSourcesOpen] = useState(false);
  const [isTextModalOpen, setIsTextModalOpen] = useState(false);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);

  // History Items
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Settings
  const [settings, setSettings] = useState<Settings>(() => {
    const saved = localStorage.getItem('novaron_settings');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {}
    }
    return {
      language: 'en',
      chunking_strategy: 'sentence',
      retrieval_mode: 'dense',
      top_k: 5,
      synthesize_audio: true,
      apiBaseUrl: DEFAULT_API_BASE_URL,
    };
  });

  // Audio Waveform & Playback
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);
  const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const activeAudioUrlRef = useRef<string | null>(null);
  const lastQueryRef = useRef<string | null>(null);

  // Update Settings
  const handleUpdateSettings = (newSettings: Partial<Settings>) => {
    setSettings((prev) => {
      const updated = { ...prev, ...newSettings };
      localStorage.setItem('novaron_settings', JSON.stringify(updated));
      return updated;
    });
  };

  // Health Polling (every 15s)
  useEffect(() => {
    const pollHealth = async () => {
      const healthy = await checkHealth(settings.apiBaseUrl);
      setIsOnline(healthy);
    };
    pollHealth();
    const interval = setInterval(pollHealth, 15000);
    return () => clearInterval(interval);
  }, [settings.apiBaseUrl]);

  // Clean Audio URLs
  useEffect(() => {
    return () => {
      if (activeAudioUrlRef.current) {
        URL.revokeObjectURL(activeAudioUrlRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  // Audio Playback
  const playAudioPayload = async (audioBase64?: string | null, textToSynthesize?: string) => {
    try {
      if (audioElementRef.current) {
        audioElementRef.current.pause();
      }

      let audioBlob: Blob;
      if (audioBase64) {
        const binaryString = atob(audioBase64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        audioBlob = new Blob([bytes], { type: 'audio/mpeg' });
      } else if (textToSynthesize) {
        audioBlob = await synthesizeSpeech({
          text: textToSynthesize,
          language: settings.language,
          apiBaseUrl: settings.apiBaseUrl,
        });
      } else {
        return;
      }

      if (activeAudioUrlRef.current) {
        URL.revokeObjectURL(activeAudioUrlRef.current);
      }
      const audioUrl = URL.createObjectURL(audioBlob);
      activeAudioUrlRef.current = audioUrl;

      const audio = new Audio(audioUrl);
      audioElementRef.current = audio;

      audio.onplay = () => {
        setIsPlayingAudio(true);
        setAppState('PLAYING_AUDIO');
      };
      audio.onended = () => {
        setIsPlayingAudio(false);
        setAppState((prev) => (response?.refused ? 'REFUSED' : 'ANSWER_READY'));
      };
      audio.onerror = () => {
        setIsPlayingAudio(false);
        setAppState((prev) => (response?.refused ? 'REFUSED' : 'ANSWER_READY'));
      };

      await audio.play();
    } catch (err) {
      console.warn('Audio playback error or prevented by browser:', err);
      setIsPlayingAudio(false);
    }
  };

  const handleToggleAudio = () => {
    if (isPlayingAudio && audioElementRef.current) {
      audioElementRef.current.pause();
      setIsPlayingAudio(false);
      setAppState(response?.refused ? 'REFUSED' : 'ANSWER_READY');
    } else if (response) {
      playAudioPayload(response.audio_base64, response.answer);
    }
  };

  // Real Microphone Recording with Automatic End-of-Speech Detection
  const startRecording = async () => {
    try {
      if (audioElementRef.current) {
        audioElementRef.current.pause();
      }
      setErrorMessage(null);
      audioChunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioCtx;
      const source = audioCtx.createMediaStreamSource(stream);
      const analyserNode = audioCtx.createAnalyser();
      analyserNode.fftSize = 256;
      analyserNode.smoothingTimeConstant = 0.35;
      source.connect(analyserNode);
      analyserRef.current = analyserNode;
      setAnalyser(analyserNode);

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      // Voice Activity & End-of-Speech Detection Loop
      let hasSpeechStarted = false;
      let speechOnsetTimestamp: number | null = null;
      let silenceStartTimestamp: number | null = null;
      let noiseFloor = 14;
      const recordingStartTimestamp = performance.now();
      const frequencyBuffer = new Uint8Array(analyserNode.frequencyBinCount);

      const monitorVoiceActivity = () => {
        if (!analyserRef.current || mediaRecorderRef.current?.state !== 'recording') {
          return;
        }

        analyserNode.getByteFrequencyData(frequencyBuffer);

        // Vocal spectrum: bins 1 to 20 (~180Hz to 3750Hz)
        let sumSquares = 0;
        let count = 0;
        for (let i = 1; i < Math.min(22, frequencyBuffer.length); i++) {
          sumSquares += frequencyBuffer[i] * frequencyBuffer[i];
          count++;
        }
        const vocalRMS = count > 0 ? Math.sqrt(sumSquares / count) : 0;

        // Dynamic noise floor tracking
        if (vocalRMS < noiseFloor * 1.6) {
          noiseFloor += (vocalRMS - noiseFloor) * 0.035;
          noiseFloor = Math.max(6, Math.min(40, noiseFloor));
        }

        const speechThreshold = noiseFloor * 1.25 + 5;
        const now = performance.now();

        if (vocalRMS > speechThreshold) {
          // User is currently speaking
          if (!hasSpeechStarted) {
            if (speechOnsetTimestamp === null) {
              speechOnsetTimestamp = now;
            } else if (now - speechOnsetTimestamp >= MIN_SPEECH_DURATION_MS) {
              hasSpeechStarted = true;
            }
          }
          // Reset silence timer whenever vocal energy is active
          silenceStartTimestamp = null;
        } else {
          // Energy below speech threshold (silence / room ambient)
          if (!hasSpeechStarted) {
            speechOnsetTimestamp = null; // Discard brief noise spikes if < MIN_SPEECH_DURATION_MS
          } else {
            // Speech has already started, now in a sustained silence / pause phase
            if (silenceStartTimestamp === null) {
              silenceStartTimestamp = now;
            } else if (now - silenceStartTimestamp >= END_OF_SPEECH_SILENCE_MS) {
              // Sustained silence reached -> Auto-stop recording!
              stopRecording();
              return;
            }
          }
        }

        // Safety cutoff at 30 seconds
        if (now - recordingStartTimestamp >= MAX_RECORDING_DURATION_MS) {
          stopRecording();
          return;
        }

        animationFrameRef.current = requestAnimationFrame(monitorVoiceActivity);
      };

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
        if (audioContextRef.current) {
          audioContextRef.current.close().catch(() => {});
        }
        stream.getTracks().forEach((track) => track.stop());
        setAnalyser(null);

        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await processVoiceQuery(audioBlob);
      };

      mediaRecorder.start();
      setAppState('LISTENING');
      animationFrameRef.current = requestAnimationFrame(monitorVoiceActivity);
    } catch (err: any) {
      console.error('Microphone access error:', err);
      setErrorMessage('Microphone access denied or unavailable. Please enable permissions or type your question.');
      setAppState('ERROR');
    }
  };

  const stopRecording = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  // Process Voice Query
  const processVoiceQuery = async (audioBlob: Blob) => {
    setAppState('TRANSCRIBING');
    setStageLabel('Understanding your voice with Whisper…');
    setErrorMessage(null);

    const timers: ReturnType<typeof setTimeout>[] = [];

    timers.push(
      setTimeout(() => {
        setAppState('RETRIEVING');
        setStageLabel('Searching 12,184 knowledge passages…');
      }, 450)
    );

    timers.push(
      setTimeout(() => {
        setAppState('GENERATING');
        setStageLabel('Synthesizing grounded answer with citations…');
      }, 950)
    );

    try {
      const res = await queryVoice({
        audioBlob,
        language: settings.language,
        top_k: settings.top_k,
        chunking_strategy: settings.chunking_strategy,
        retrieval_mode: settings.retrieval_mode,
        synthesize_audio: settings.synthesize_audio,
        previous_query: lastQueryRef.current || undefined,
        apiBaseUrl: settings.apiBaseUrl,
      });

      timers.forEach((t) => clearTimeout(t));

      setResponse(res);
      lastQueryRef.current = res.query || res.normalized_query || null;

      // Add to session history
      setHistory((prev) => [
        {
          id: String(Date.now()),
          timestamp: new Date(),
          query: res.query || 'Voice Question',
          data: res,
        },
        ...prev,
      ]);

      if (res.refused) {
        setAppState('REFUSED');
      } else {
        setAppState('ANSWER_READY');
      }

      if (settings.synthesize_audio && res.audio_base64) {
        playAudioPayload(res.audio_base64, res.answer);
      }
    } catch (err: any) {
      timers.forEach((t) => clearTimeout(t));
      console.error('Voice query error:', err);
      setErrorMessage(err.message || "Couldn't understand the audio. Try speaking again or type your question.");
      setAppState('ERROR');
    }
  };

  // Process Typed Question
  const handleTextQuery = async (text: string) => {
    setAppState('RETRIEVING');
    setStageLabel('Searching 12,184 knowledge passages…');
    setErrorMessage(null);

    const genTimer = setTimeout(() => {
      setAppState('GENERATING');
      setStageLabel('Synthesizing grounded answer with citations…');
    }, 450);

    try {
      const res = await queryText({
        query: text,
        top_k: settings.top_k,
        chunking_strategy: settings.chunking_strategy,
        retrieval_mode: settings.retrieval_mode,
        previous_query: lastQueryRef.current || undefined,
        apiBaseUrl: settings.apiBaseUrl,
      });

      clearTimeout(genTimer);
      setResponse(res);
      lastQueryRef.current = text;

      setHistory((prev) => [
        {
          id: String(Date.now()),
          timestamp: new Date(),
          query: text,
          data: res,
        },
        ...prev,
      ]);

      if (res.refused) {
        setAppState('REFUSED');
      } else {
        setAppState('ANSWER_READY');
      }

      if (settings.synthesize_audio) {
        playAudioPayload(null, res.answer);
      }
    } catch (err: any) {
      clearTimeout(genTimer);
      console.error('Text query error:', err);
      setErrorMessage(err.message || 'Failed to process query.');
      setAppState('ERROR');
    }
  };

  const handleReset = () => {
    if (audioElementRef.current) {
      audioElementRef.current.pause();
    }
    setAppState('IDLE');
    setResponse(null);
    setErrorMessage(null);
    setIsPlayingAudio(false);
  };

  const handleTabSelect = (tab: 'ask' | 'history' | 'sources' | 'settings') => {
    setActiveTab(tab);
    if (tab === 'ask') {
      setIsHistoryOpen(false);
      setIsSourcesOpen(false);
      setIsSettingsOpen(false);
    } else if (tab === 'history') {
      setIsSourcesOpen(false);
      setIsSettingsOpen(false);
      setIsHistoryOpen(true);
    } else if (tab === 'sources') {
      setIsHistoryOpen(false);
      setIsSettingsOpen(false);
      setIsSourcesOpen(true);
    } else if (tab === 'settings') {
      setIsHistoryOpen(false);
      setIsSourcesOpen(false);
      setIsSettingsOpen(true);
    }
  };

  const hasAnswer = response !== null && (appState === 'ANSWER_READY' || appState === 'PLAYING_AUDIO' || appState === 'REFUSED');

  // Contextual State-Aware Messaging (Main Heading + Subordinate Supporting Text)
  const heroContent = useMemo(() => {
    switch (appState) {
      case 'LISTENING':
        return {
          main: "I'm listening...",
          supporting: "Speak naturally. I'll know when you're done.",
        };
      case 'TRANSCRIBING':
        return {
          main: 'Understanding your voice...',
          supporting: 'Transcribing speech with local Whisper model...',
        };
      case 'RETRIEVING':
        return {
          main: 'Searching knowledge...',
          supporting: 'Scanning 12,184 verified passages with FAISS & BM25...',
        };
      case 'GENERATING':
        return {
          main: 'Formulating answer...',
          supporting: 'Synthesizing grounded response with verified citations...',
        };
      case 'PLAYING_AUDIO':
        return {
          main: 'Speaking answer...',
          supporting: null,
        };
      case 'ANSWER_READY':
        return {
          main: 'Grounded Answer',
          supporting: null,
        };
      case 'REFUSED':
        return {
          main: 'Grounding check enforced.',
          supporting: 'Zero-hallucination guardrail active.',
        };
      case 'ERROR':
        return {
          main: 'Something went wrong.',
          supporting: errorMessage || 'Please try again.',
        };
      case 'IDLE':
      default:
        return {
          main: 'Ready when you are.',
          supporting: 'Tap the microphone or type your question in English or Indic languages.',
        };
    }
  }, [appState, errorMessage]);

  return (
    <div className="min-h-screen bg-[#07241B] text-goa-cream flex flex-row overflow-x-hidden relative selection:bg-goa-pink/30 selection:text-white">
      {/* ========================================================================= */}
      {/* DEEP NOVARON ATMOSPHERIC FOREST ENVIRONMENT (LAYERED & GPU-ACCELERATED)  */}
      {/* ========================================================================= */}
      <div className="fixed inset-0 pointer-events-none -z-0 overflow-hidden" aria-hidden="true">
        {/* Layer 1: Base Nocturnal Forest Gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#07241B] via-[#051A13] to-[#09281E]" />

        {/* Layer 2: Asynchronous Atmospheric Deep Green Mist Fields (Heavily Blurred, Huge, Soft) */}
        <div className="absolute top-[-15%] left-[10%] w-[950px] h-[850px] bg-gradient-to-br from-[#0F3D2E]/45 via-[#0B3326]/30 to-transparent rounded-full blur-[140px] animate-atmosphere-x" />
        <div className="absolute bottom-[-15%] right-[-10%] w-[900px] h-[800px] bg-gradient-to-tl from-[#082A20]/65 via-[#0D382B]/35 to-transparent rounded-full blur-[150px] animate-atmosphere-y" />
        <div className="absolute top-[20%] right-[15%] w-[800px] h-[750px] bg-gradient-to-bl from-[#0A3024]/40 via-[#061F17]/30 to-transparent rounded-full blur-[140px] animate-atmosphere-breath" />

        {/* Layer 3: Broad Center Ambient Illumination (Soft natural light across the environment) */}
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-gradient-to-br from-[#F5C518]/[0.024] via-[#0F3D2E]/[0.08] to-transparent rounded-full blur-[120px]" />

        {/* Layer 4: Voice-Reactive Energy Aura (Emerges gently when listening / speaking) */}
        <div
          className={`absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[550px] bg-[#EE2A6D]/[0.035] rounded-full blur-[120px] transition-opacity duration-1000 ${
            appState === 'LISTENING' || appState === 'PLAYING_AUDIO' ? 'opacity-100' : 'opacity-0'
          }`}
        />

        {/* Layer 5: Micro-Noise Organic Depth Texture (eliminates digital banding) */}
        <div
          className="absolute inset-0 opacity-[0.02] mix-blend-overlay pointer-events-none"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          }}
        />
      </div>

      {/* 1. Left Sidebar Rail (Desktop) */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={handleTabSelect}
        historyCount={history.length}
      />

      {/* 2. Main Content Canvas */}
      <div className="flex-1 flex flex-col min-h-screen overflow-y-auto relative z-10">
        {/* Header */}
        <Header
          isOnline={isOnline}
          onOpenSettings={() => handleTabSelect('settings')}
          onOpenMenu={() => setIsMobileNavOpen(true)}
          settings={settings}
          onUpdateSettings={handleUpdateSettings}
        />

        {/* Center Interaction Stage */}
        <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-8 py-6 flex flex-col justify-center items-center relative">
          
          {/* Conversational State-Aware Hero Heading */}
          <div
            className={`text-center transition-all duration-300 min-h-[64px] sm:min-h-[72px] flex flex-col justify-center items-center ${
              hasAnswer ? 'mb-2' : 'my-4'
            }`}
          >
            <h2
              key={`heading-${heroContent.main}`}
              className="text-3xl sm:text-4xl md:text-5xl font-serif font-medium tracking-tight text-goa-cream animate-fade-in"
            >
              {heroContent.main}
            </h2>
            {heroContent.supporting && !hasAnswer && (
              <p
                key={`sub-${heroContent.supporting}`}
                className="text-xs sm:text-sm font-sans text-goa-cream/60 mt-2 animate-fade-in"
              >
                {heroContent.supporting}
              </p>
            )}
          </div>

          {/* NOVARON Voice Core */}
          <VoiceOrb
            state={appState}
            analyser={analyser}
            stageLabel={stageLabel}
            compact={hasAnswer}
            onClick={appState === 'LISTENING' ? stopRecording : startRecording}
          />

          {/* Compact Inline Error Notice (Non-blocking) */}
          {appState === 'ERROR' && errorMessage && (
            <div className="w-full max-w-md my-3 p-3.5 rounded-2xl bg-rose-950/70 border border-rose-500/40 text-rose-200 text-xs font-mono text-center shadow-lg backdrop-blur-md animate-fade-in flex items-center justify-between gap-3">
              <span className="text-[11px] leading-snug truncate flex-1">{errorMessage}</span>
              <button
                onClick={handleReset}
                className="px-3 py-1 rounded-full bg-rose-800 hover:bg-rose-700 text-white font-bold text-[10px] shrink-0 transition-all"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Grounded Answer Card */}
          {(appState === 'ANSWER_READY' || appState === 'PLAYING_AUDIO') && response && !response.refused && (
            <AnswerCard
              data={response}
              isPlaying={isPlayingAudio}
              onToggleAudio={handleToggleAudio}
              onShare={() => setIsShareModalOpen(true)}
              onSelectSuggestion={(q) => handleTextQuery(q)}
            />
          )}

          {/* Grounding Guardrail Refusal Card */}
          {appState === 'REFUSED' && response && response.refused && (
            <RefusalCard
              data={response}
              isPlaying={isPlayingAudio}
              onToggleAudio={handleToggleAudio}
              onReset={handleReset}
            />
          )}

          {/* Bottom Voice Controls */}
          <VoiceControls
            state={appState}
            onStartRecording={startRecording}
            onStopRecording={stopRecording}
            onOpenKeyboard={() => setIsTextModalOpen(true)}
            onReset={handleReset}
          />
        </main>
      </div>

      {/* Drawers & Modals */}
      <SettingsDrawer
        isOpen={isSettingsOpen}
        onClose={() => {
          setIsSettingsOpen(false);
          setActiveTab('ask');
        }}
        settings={settings}
        onUpdateSettings={handleUpdateSettings}
      />

      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => {
          setIsHistoryOpen(false);
          setActiveTab('ask');
        }}
        history={history}
        onSelectHistory={(item) => {
          setResponse(item.data);
          setAppState(item.data.refused ? 'REFUSED' : 'ANSWER_READY');
        }}
        onClearHistory={() => setHistory([])}
      />

      <SourcesDrawer
        isOpen={isSourcesOpen}
        onClose={() => {
          setIsSourcesOpen(false);
          setActiveTab('ask');
        }}
        sources={response?.sources || (history.length > 0 ? history[0].data.sources : [])}
        queryText={
          response
            ? ('query' in response ? (response as any).query : undefined)
            : (history.length > 0 ? history[0].query : undefined)
        }
      />

      <TextQueryModal
        isOpen={isTextModalOpen}
        onClose={() => setIsTextModalOpen(false)}
        onSubmit={handleTextQuery}
      />

      {response && (
        <ShareModal
          isOpen={isShareModalOpen}
          onClose={() => setIsShareModalOpen(false)}
          data={response}
        />
      )}

      {/* Mobile Navigation Slide-in Drawer */}
      {isMobileNavOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Mobile Navigation Menu"
          onClick={(e) => {
            if (e.target === e.currentTarget) setIsMobileNavOpen(false);
          }}
          className="fixed inset-0 z-50 flex bg-black/65 backdrop-blur-sm lg:hidden transition-opacity animate-fade-in"
        >
          <div className="w-72 max-w-[80vw] bg-[#0A2E22] border-r border-white/[0.08] p-5 flex flex-col justify-between h-full shadow-2xl">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-white/[0.08] mb-6">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-[#0F3D2E] to-[#0A2E22] border border-white/[0.12] flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-[#F5C518]" />
                  </div>
                  <span className="text-sm font-bold tracking-[0.14em] text-[#F4EDD8] font-sans">
                    NOVARON
                  </span>
                </div>
                <button
                  onClick={() => setIsMobileNavOpen(false)}
                  className="p-1.5 rounded-full hover:bg-white/[0.08] text-[#F4EDD8]/70 hover:text-[#F4EDD8]"
                  aria-label="Close menu"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Navigation Rail */}
              <nav className="space-y-1.5">
                <button
                  onClick={() => {
                    handleTabSelect('ask');
                    setIsMobileNavOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-mono font-medium transition-all ${
                    activeTab === 'ask'
                      ? 'bg-white/[0.08] text-[#F4EDD8] border border-white/[0.10]'
                      : 'text-[#F4EDD8]/70 hover:text-[#F4EDD8] hover:bg-white/[0.04]'
                  }`}
                >
                  <Mic className={`w-4 h-4 ${activeTab === 'ask' ? 'text-[#EE2A6D]' : 'text-[#F4EDD8]/60'}`} />
                  <span>Ask</span>
                </button>

                <button
                  onClick={() => {
                    handleTabSelect('history');
                    setIsMobileNavOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-mono font-medium transition-all ${
                    activeTab === 'history'
                      ? 'bg-white/[0.08] text-[#F4EDD8] border border-white/[0.10]'
                      : 'text-[#F4EDD8]/70 hover:text-[#F4EDD8] hover:bg-white/[0.04]'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <HistoryIcon className={`w-4 h-4 ${activeTab === 'history' ? 'text-[#EE2A6D]' : 'text-[#F4EDD8]/60'}`} />
                    <span>History</span>
                  </div>
                  {history.length > 0 && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-white/[0.08] text-[#F4EDD8]">
                      {history.length}
                    </span>
                  )}
                </button>

                <button
                  onClick={() => {
                    handleTabSelect('sources');
                    setIsMobileNavOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-mono font-medium transition-all ${
                    activeTab === 'sources'
                      ? 'bg-white/[0.08] text-[#F4EDD8] border border-white/[0.10]'
                      : 'text-[#F4EDD8]/70 hover:text-[#F4EDD8] hover:bg-white/[0.04]'
                  }`}
                >
                  <Database className={`w-4 h-4 ${activeTab === 'sources' ? 'text-[#EE2A6D]' : 'text-[#F4EDD8]/60'}`} />
                  <span>Sources</span>
                </button>
              </nav>
            </div>

            <div className="pt-4 border-t border-white/[0.05] text-[10px] font-mono text-[#F4EDD8]/30 flex items-center justify-between">
              <span>HH GOA 2026</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400/70" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
