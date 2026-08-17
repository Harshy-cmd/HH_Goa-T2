import React, { useState, useEffect, useRef } from 'react';
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
import { checkHealth, queryText, queryVoice, synthesizeSpeech, DEFAULT_API_BASE_URL } from './services/api';
import { AppState, QueryResponse, VoiceQueryResponse, Settings } from './types';

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
  const [activeTab, setActiveTab] = useState<'ask' | 'history' | 'sources'>('ask');
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
  const [audioLevel, setAudioLevel] = useState<number>(0);
  const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const activeAudioUrlRef = useRef<string | null>(null);

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

  // Real Microphone Recording
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
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      source.connect(analyser);
      analyserRef.current = analyser;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      const updateLevel = () => {
        if (analyserRef.current) {
          analyserRef.current.getByteFrequencyData(dataArray);
          const avg = dataArray.reduce((sum, val) => sum + val, 0) / dataArray.length;
          setAudioLevel(avg / 128.0);
          animationFrameRef.current = requestAnimationFrame(updateLevel);
        }
      };
      updateLevel();

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }
        if (audioContextRef.current) {
          audioContextRef.current.close().catch(() => {});
        }
        stream.getTracks().forEach((track) => track.stop());
        setAudioLevel(0);

        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await processVoiceQuery(audioBlob);
      };

      mediaRecorder.start();
      setAppState('LISTENING');
    } catch (err: any) {
      console.error('Microphone access error:', err);
      setErrorMessage('Microphone access denied or unavailable. Please enable permissions or type your question.');
      setAppState('ERROR');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  // Process Voice Query
  const processVoiceQuery = async (audioBlob: Blob) => {
    setAppState('TRANSCRIBING');
    setStageLabel('Transcribing Voice Speech (Whisper)…');

    try {
      setTimeout(() => {
        setAppState('RETRIEVING');
        setStageLabel('Searching Sentence FAISS Knowledge Base…');
      }, 500);

      const res = await queryVoice({
        audioBlob,
        language: settings.language,
        top_k: settings.top_k,
        chunking_strategy: settings.chunking_strategy,
        retrieval_mode: settings.retrieval_mode,
        synthesize_audio: settings.synthesize_audio,
        apiBaseUrl: settings.apiBaseUrl,
      });

      setResponse(res);

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
      console.error('Voice query error:', err);
      setErrorMessage(err.message || 'Failed to process voice query.');
      setAppState('ERROR');
    }
  };

  // Process Typed Question
  const handleTextQuery = async (text: string) => {
    setAppState('RETRIEVING');
    setStageLabel('Searching Sentence FAISS Knowledge Base…');
    setErrorMessage(null);

    try {
      const res = await queryText({
        query: text,
        top_k: settings.top_k,
        chunking_strategy: settings.chunking_strategy,
        retrieval_mode: settings.retrieval_mode,
        apiBaseUrl: settings.apiBaseUrl,
      });

      setResponse(res);

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

  const handleTabSelect = (tab: 'ask' | 'history' | 'sources') => {
    setActiveTab(tab);
    if (tab === 'history') setIsHistoryOpen(true);
    if (tab === 'sources') setIsSourcesOpen(true);
  };

  const hasAnswer = response !== null && (appState === 'ANSWER_READY' || appState === 'PLAYING_AUDIO' || appState === 'REFUSED');

  return (
    <div className="min-h-screen bg-goa-forest text-goa-cream flex flex-row overflow-x-hidden relative">
      {/* 1. Left Sidebar Rail (Desktop) */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={handleTabSelect}
        onOpenSettings={() => setIsSettingsOpen(true)}
        historyCount={history.length}
      />

      {/* 2. Main Content Canvas */}
      <div className="flex-1 flex flex-col min-h-screen overflow-y-auto">
        {/* Header */}
        <Header
          isOnline={isOnline}
          onOpenSettings={() => setIsSettingsOpen(true)}
          settings={settings}
          onUpdateSettings={handleUpdateSettings}
        />

        {/* Center Interaction Stage */}
        <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-8 py-6 flex flex-col justify-center items-center relative">
          {/* Hero Statement (Centered when Idle, Compact when Answer is Present) */}
          <div className={`text-center transition-all duration-700 ${hasAnswer ? 'mb-2' : 'my-4'}`}>
            <h2 className="text-3xl sm:text-5xl font-serif font-medium tracking-tight text-goa-cream">
              What do you want to know?
            </h2>
            {!hasAnswer && (
              <p className="text-xs sm:text-sm font-sans text-goa-cream/70 mt-1">
                Tap the microphone or ask anything.
              </p>
            )}
          </div>

          {/* Dynamic Voice Orb */}
          <VoiceOrb
            state={appState}
            audioLevel={audioLevel}
            stageLabel={stageLabel}
            compact={hasAnswer}
            onClick={appState === 'LISTENING' ? stopRecording : startRecording}
          />

          {/* Error Alert */}
          {appState === 'ERROR' && errorMessage && (
            <div className="w-full max-w-md my-4 p-4 rounded-3xl bg-rose-950/80 border border-rose-500/50 text-rose-200 text-xs font-mono text-center shadow-2xl">
              <p className="font-bold mb-1">⚠️ System Notice</p>
              <p className="text-[11px] leading-relaxed">{errorMessage}</p>
              <button
                onClick={handleReset}
                className="mt-3 px-4 py-1.5 rounded-full bg-rose-800 hover:bg-rose-700 text-white font-bold"
              >
                Try Again
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

          {/* Bottom Voice Controls & Pipeline Stepper */}
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
        onClose={() => setIsSettingsOpen(false)}
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
    </div>
  );
};

export default App;
