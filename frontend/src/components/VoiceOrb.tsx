import React, { useEffect, useRef } from 'react';
import { AppState } from '../types';
import { ShieldAlert } from 'lucide-react';

interface VoiceOrbProps {
  state: AppState;
  analyser?: AnalyserNode | null;
  audioLevel?: number; // fallback 0.0 to 1.0
  stageLabel?: string;
  onClick?: () => void;
  compact?: boolean;
}

export const VoiceOrb: React.FC<VoiceOrbProps> = ({
  state,
  analyser = null,
  audioLevel = 0,
  stageLabel,
  onClick,
  compact = false,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animFrameRef = useRef<number | null>(null);

  // State flags
  const isIdle = state === 'IDLE';
  const isListening = state === 'LISTENING';
  const isTranscribing = state === 'TRANSCRIBING';
  const isRetrieving = state === 'RETRIEVING';
  const isGenerating = state === 'GENERATING';
  const isPlayingAudio = state === 'PLAYING_AUDIO';
  const isRefused = state === 'REFUSED';
  const isError = state === 'ERROR';
  const isProcessing = isTranscribing || isRetrieving || isGenerating;

  // Smoothing, noise floor tracking, and timing refs
  const smoothedAudioRef = useRef<number>(0);
  const noiseFloorRef = useRef<number>(14);
  const timeRef = useRef<number>(0);
  const orbitAngleRef = useRef<number>(0);
  const audioLevelPropRef = useRef<number>(audioLevel);
  audioLevelPropRef.current = audioLevel;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    let isPaused = false;
    const handleVisibilityChange = () => {
      isPaused = document.hidden;
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Dimension handling
    const size = compact ? 220 : 360;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    ctx.scale(dpr, dpr);

    const cx = size / 2;
    const cy = size / 2;
    const R = compact ? 52 : 88; // Base unit radius

    // Pre-allocate audio frequency buffer for 60fps loop
    const bufferLength = analyser ? analyser.frequencyBinCount : 32;
    const audioDataArray = new Uint8Array(bufferLength);

    const render = () => {
      if (!isPaused) {
        let targetAudio = 0;

        // 1. Direct Web Audio API Analyser sampling with Human Voice Band Filtering & Noise Gate
        if (isListening && analyser) {
          analyser.getByteFrequencyData(audioDataArray);
          
          const startBin = 1;
          const endBin = Math.min(22, audioDataArray.length);
          let sumSquares = 0;
          let count = 0;

          for (let i = startBin; i < endBin; i++) {
            const val = audioDataArray[i];
            sumSquares += val * val;
            count++;
          }
          const vocalRMS = count > 0 ? Math.sqrt(sumSquares / count) : 0;

          // Adaptive background noise floor estimation
          if (vocalRMS < noiseFloorRef.current * 1.6) {
            noiseFloorRef.current += (vocalRMS - noiseFloorRef.current) * 0.035;
            noiseFloorRef.current = Math.max(6, Math.min(40, noiseFloorRef.current));
          }

          // Voice gate threshold
          const threshold = noiseFloorRef.current * 1.25 + 5;

          if (vocalRMS > threshold) {
            const delta = vocalRMS - threshold;
            const normalized = Math.pow(delta / 55, 1.2);
            targetAudio = Math.min(1.0, Math.max(0, normalized));
          } else {
            targetAudio = 0;
          }
        } else if (isListening) {
          targetAudio = audioLevelPropRef.current;
        } else if (isPlayingAudio) {
          targetAudio = 0.32 + Math.sin(Date.now() / 150) * 0.22;
        } else if (isProcessing) {
          targetAudio = 0.15 + Math.sin(Date.now() / 300) * 0.10;
        }

        // Exponential smoothing (LERP):
        const lerpFactor = targetAudio > smoothedAudioRef.current ? 0.30 : 0.10;
        smoothedAudioRef.current += (targetAudio - smoothedAudioRef.current) * lerpFactor;
        const sa = smoothedAudioRef.current;

        // Dynamic time progression:
        const speed = isListening
          ? 0.016 + sa * 0.045
          : isProcessing
          ? 0.024
          : isPlayingAudio
          ? 0.030
          : 0.014;
        timeRef.current += speed;
        const t = timeRef.current;

        orbitAngleRef.current += (isProcessing ? 0.03 : 0.010);
        const orbit = orbitAngleRef.current;

        // Clear canvas
        ctx.clearRect(0, 0, size, size);

        // =========================================================================
        // LAYER 5: OUTER ORBITAL RING, PRECISION ARCS & FREQUENCY RAY BURSTS
        // =========================================================================
        const outerOrbitR = R * 1.58;

        // 1. Fine Outer Orbit Track
        ctx.save();
        ctx.beginPath();
        ctx.arc(cx, cy, outerOrbitR, 0, Math.PI * 2);
        ctx.strokeStyle = isListening
          ? `rgba(238, 42, 109, ${0.25 + sa * 0.35})`
          : isProcessing
          ? 'rgba(245, 197, 24, 0.40)'
          : 'rgba(244, 237, 216, 0.20)';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([4, 6]);
        ctx.stroke();
        ctx.restore();

        // 2. Precision Tick Marks & Frequency Bursts along the Outer Circumference
        const totalTicks = 72;
        ctx.save();
        for (let i = 0; i < totalTicks; i++) {
          const angle = (i / totalTicks) * Math.PI * 2;
          
          const quadWave = Math.pow(Math.abs(Math.sin(angle * 2)), 3);
          const dynamicWave = Math.sin(angle * 4 + t * 2) * 0.5 + 0.5;
          const tickLen = 2 + quadWave * (sa * 32) * dynamicWave;

          const r1 = outerOrbitR + 3;
          const r2 = r1 + tickLen;

          const x1 = cx + Math.cos(angle) * r1;
          const y1 = cy + Math.sin(angle) * r1;
          const x2 = cx + Math.cos(angle) * r2;
          const y2 = cy + Math.sin(angle) * r2;

          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);

          if (isListening) {
            ctx.strokeStyle = i % 2 === 0
              ? `rgba(238, 42, 109, ${0.35 + sa * 0.45})`
              : `rgba(245, 197, 24, ${0.25 + sa * 0.45})`;
          } else if (isProcessing) {
            ctx.strokeStyle = i % 2 === 0 ? 'rgba(245, 197, 24, 0.75)' : 'rgba(244, 237, 216, 0.45)';
          } else {
            ctx.strokeStyle = i % 2 === 0 ? 'rgba(244, 237, 216, 0.35)' : 'rgba(245, 197, 24, 0.25)';
          }
          ctx.lineWidth = 1.4;
          ctx.stroke();
        }
        ctx.restore();

        // 3. Orbiting Energy Beads
        const bead1Angle = orbit;
        const bead1X = cx + Math.cos(bead1Angle) * outerOrbitR;
        const bead1Y = cy + Math.sin(bead1Angle) * outerOrbitR;

        ctx.save();
        ctx.beginPath();
        ctx.arc(bead1X, bead1Y, 4.0 + sa * 3, 0, Math.PI * 2);
        ctx.fillStyle = '#F5C518';
        ctx.shadowColor = '#F5C518';
        ctx.shadowBlur = 8 + sa * 6;
        ctx.fill();
        ctx.restore();

        const bead2Angle = orbit + Math.PI * 0.9;
        const bead2X = cx + Math.cos(bead2Angle) * outerOrbitR;
        const bead2Y = cy + Math.sin(bead2Angle) * outerOrbitR;

        ctx.save();
        ctx.beginPath();
        ctx.arc(bead2X, bead2Y, 3.2 + sa * 2.5, 0, Math.PI * 2);
        ctx.fillStyle = '#EE2A6D';
        ctx.shadowColor = '#EE2A6D';
        ctx.shadowBlur = 6 + sa * 6;
        ctx.fill();
        ctx.restore();

        // =========================================================================
        // LAYER 3: EMERGING PINK ENERGY WING LOBES
        // =========================================================================
        const pinkWingRadius = R * (1.20 + sa * 0.26);
        
        const drawPinkPetal = (startAngle: number, sweep: number) => {
          ctx.save();
          ctx.beginPath();
          ctx.arc(cx, cy, pinkWingRadius, startAngle, startAngle + sweep);
          ctx.lineTo(cx, cy);
          ctx.closePath();

          const grad = ctx.createRadialGradient(cx, cy, R * 0.5, cx, cy, pinkWingRadius);
          grad.addColorStop(0, '#EE2A6D');
          grad.addColorStop(0.85, `rgba(238, 42, 109, ${0.7 + sa * 0.3})`);
          grad.addColorStop(1, 'rgba(238, 42, 109, 0)');

          ctx.fillStyle = grad;
          ctx.shadowColor = '#EE2A6D';
          ctx.shadowBlur = 10 + sa * 12;
          ctx.fill();
          ctx.restore();
        };

        drawPinkPetal(-Math.PI * 0.22 + Math.sin(t * 1.2) * 0.06, Math.PI * 0.38 + sa * 0.22);
        drawPinkPetal(Math.PI * 0.82 + Math.cos(t * 1.1) * 0.06, Math.PI * 0.36 + sa * 0.22);

        // =========================================================================
        // LAYER 2: MULTI-TIERED ORGANIC SCULPTED CREAM FORM (TOPOGRAPHIC RELIEF)
        // =========================================================================
        const numPoints = 64;
        const angleStep = (Math.PI * 2) / numPoints;

        // Tier 1: Outer Cream Sculpted Layer
        ctx.save();
        ctx.beginPath();
        for (let i = 0; i <= numPoints; i++) {
          const a = i * angleStep;
          const h1 = Math.sin(a * 4 + t * 0.6) * (3.5 + sa * 15);
          const h2 = Math.cos(a * 2 - t * 0.4) * (2.5 + sa * 10);
          const h3 = Math.sin(a * 6 + 1.2) * (1.5 + sa * 8);
          const r = R * 1.10 + h1 + h2 + h3;

          const px = cx + Math.cos(a) * r;
          const py = cy + Math.sin(a) * r;

          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();

        ctx.shadowColor = 'rgba(0, 0, 0, 0.45)';
        ctx.shadowBlur = 18;
        ctx.shadowOffsetY = 6;
        ctx.fillStyle = '#F4EDD8';
        ctx.fill();
        ctx.restore();

        // Tier 2: Mid Cream Sculpted Layer (Interior Stepped Relief)
        ctx.save();
        ctx.beginPath();
        for (let i = 0; i <= numPoints; i++) {
          const a = i * angleStep;
          const h1 = Math.sin(a * 4 + t * 0.6 + 0.6) * (2.5 + sa * 10);
          const h2 = Math.cos(a * 3 - t * 0.3) * (2.0 + sa * 7);
          const r = R * 0.94 + h1 + h2;

          const px = cx + Math.cos(a) * r;
          const py = cy + Math.sin(a) * r;

          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();
        ctx.shadowColor = 'rgba(10, 46, 34, 0.25)';
        ctx.shadowBlur = 10;
        ctx.fillStyle = '#FAF6EC';
        ctx.fill();
        ctx.restore();

        // Sinuous Green Ribbon Wave nestled inside the cream surface
        ctx.save();
        ctx.beginPath();
        for (let i = 0; i <= numPoints; i++) {
          const a = i * angleStep;
          const ribbonR = R * 0.98 + Math.sin(a * 3 + t * 1.0) * (3.5 + sa * 11);
          const px = cx + Math.cos(a) * ribbonR;
          const py = cy + Math.sin(a) * ribbonR;
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();
        ctx.strokeStyle = '#0F3D2E';
        ctx.lineWidth = 3.5;
        ctx.lineJoin = 'round';
        ctx.stroke();
        ctx.restore();

        // =========================================================================
        // LAYER 4: INTEGRATED HORIZONTAL AUDIO WAVEFORM (SIGNATURE FLANKING BARS)
        // =========================================================================
        const drawHorizontalWave = (isLeft: boolean) => {
          const barCount = 14;
          const startDist = R * 0.46;
          const maxDist = R * 1.28;
          const dir = isLeft ? -1 : 1;

          ctx.save();
          for (let i = 0; i < barCount; i++) {
            const ratio = i / (barCount - 1);
            const dist = startDist + ratio * (maxDist - startDist);
            const x = cx + dir * dist;

            const envelope = Math.sin(ratio * Math.PI);
            const waveFreq = Math.sin(i * 0.8 + t * 3) * 0.35 + 0.65;
            const barHeight = Math.max(2.5, envelope * (4.5 + sa * 48 * waveFreq));

            ctx.beginPath();
            ctx.moveTo(x, cy - barHeight / 2);
            ctx.lineTo(x, cy + barHeight / 2);

            if (ratio < 0.3) {
              ctx.strokeStyle = '#0F3D2E';
            } else if (ratio < 0.7) {
              ctx.strokeStyle = (isListening && sa > 0.08) ? '#EE2A6D' : '#0D3326';
            } else {
              ctx.strokeStyle = (isListening && sa > 0.08) ? '#F5C518' : '#0F3D2E';
            }

            ctx.lineWidth = 2.4;
            ctx.lineCap = 'round';
            ctx.stroke();

            if (i === barCount - 1) {
              ctx.beginPath();
              ctx.arc(x + dir * 5, cy, 1.8, 0, Math.PI * 2);
              ctx.fillStyle = '#0F3D2E';
              ctx.fill();
            }
          }
          ctx.restore();
        };

        drawHorizontalWave(true);  // Left soundwave
        drawHorizontalWave(false); // Right soundwave

        // =========================================================================
        // LAYER 3.5: CONCENTRIC PRECISION RING ARCS & INNER ORBITAL BEAD
        // =========================================================================
        const innerRingR = R * 0.72;

        ctx.save();
        ctx.beginPath();
        ctx.arc(cx, cy, innerRingR, 0, Math.PI * 2);
        ctx.strokeStyle = isListening
          ? `rgba(238, 42, 109, ${0.30 + sa * 0.35})`
          : 'rgba(238, 42, 109, 0.35)';
        ctx.lineWidth = 1.6;
        ctx.stroke();

        // Inner Yellow Satellite Bead
        const innerBeadAngle = -t * 1.2;
        const ibX = cx + Math.cos(innerBeadAngle) * innerRingR;
        const ibY = cy + Math.sin(innerBeadAngle) * innerRingR;

        ctx.beginPath();
        ctx.arc(ibX, ibY, 3.8 + sa * 1.5, 0, Math.PI * 2);
        ctx.fillStyle = '#F5C518';
        ctx.shadowColor = '#F5C518';
        ctx.shadowBlur = 6 + sa * 6;
        ctx.fill();
        ctx.restore();

        // =========================================================================
        // LAYER 1: CENTRAL LIVING CORE (DEEP FOREST EMERALD HEART & NOVARON SUNSET)
        // =========================================================================
        const coreR = R * 0.44;

        ctx.save();
        ctx.beginPath();
        ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
        ctx.fillStyle = '#0A2E22';
        ctx.shadowColor = 'rgba(10, 46, 34, 0.6)';
        ctx.shadowBlur = 12;
        ctx.fill();

        ctx.strokeStyle = '#0F3D2E';
        ctx.lineWidth = 2.2;
        ctx.stroke();
        ctx.restore();

        // Inner Radiant Light Source (Sunset Nucleus)
        ctx.save();
        ctx.beginPath();
        ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
        ctx.clip();

        const sunRadius = coreR * 0.62 * (1 + sa * 0.16);
        const sunY = cy + coreR * 0.05;

        // Radiant Corona Triangles (5 Sunbeams)
        const beamCount = 5;
        for (let b = 0; b < beamCount; b++) {
          const bAngle = -Math.PI + ((b + 1) / (beamCount + 1)) * Math.PI;
          const beamLen = sunRadius * 1.45 + (sa > 0.1 ? Math.sin(t * 3 + b) * (sa * 4) : 0);
          const tipX = cx + Math.cos(bAngle) * beamLen;
          const tipY = sunY + Math.sin(bAngle) * beamLen;

          const baseW = 0.18;
          const b1X = cx + Math.cos(bAngle - baseW) * sunRadius * 0.85;
          const b1Y = sunY + Math.sin(bAngle - baseW) * sunRadius * 0.85;
          const b2X = cx + Math.cos(bAngle + baseW) * sunRadius * 0.85;
          const b2Y = sunY + Math.sin(bAngle + baseW) * sunRadius * 0.85;

          ctx.beginPath();
          ctx.moveTo(tipX, tipY);
          ctx.lineTo(b1X, b1Y);
          ctx.lineTo(b2X, b2Y);
          ctx.closePath();
          ctx.fillStyle = '#EE2A6D';
          ctx.fill();
        }

        // Golden Semi-Circular Sun Body
        ctx.beginPath();
        ctx.arc(cx, sunY, sunRadius * 0.85, Math.PI, 0, false);
        ctx.closePath();
        ctx.fillStyle = '#F5C518';
        ctx.shadowColor = '#F5C518';
        ctx.shadowBlur = 6 + sa * 8;
        ctx.fill();

        // Horizon Reflection Stripes
        const stripeYStarts = [sunY + 4, sunY + 8, sunY + 12];
        const stripeWidths = [coreR * 0.85, coreR * 0.65, coreR * 0.45];
        const stripeColors = ['#F5C518', '#F5C518', '#EE2A6D'];

        for (let s = 0; s < stripeYStarts.length; s++) {
          const sy = stripeYStarts[s];
          const sw = stripeWidths[s] * (1 + (sa > 0.1 ? Math.sin(t * 2.5 + s) * (sa * 0.3) : 0));
          ctx.beginPath();
          ctx.moveTo(cx - sw / 2, sy);
          ctx.lineTo(cx + sw / 2, sy);
          ctx.strokeStyle = stripeColors[s];
          ctx.lineWidth = 2.2;
          ctx.lineCap = 'round';
          ctx.stroke();
        }

        ctx.restore();
      }

      animFrameRef.current = requestAnimationFrame(render);
    };

    animFrameRef.current = requestAnimationFrame(render);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
      }
    };
  }, [compact, state, analyser, isListening, isProcessing, isPlayingAudio, isRefused, isError]);

  return (
    <div
      className={`relative flex flex-col items-center justify-center select-none transition-all duration-700 ${
        compact ? 'py-1' : 'py-3 sm:py-5'
      }`}
    >
      {/* Interactive Voice Core Canvas Wrapper */}
      <div
        onClick={onClick}
        className={`relative ${
          compact
            ? 'w-44 h-44 sm:w-56 sm:h-56'
            : 'w-[260px] h-[260px] xs:w-[300px] xs:h-[300px] sm:w-[360px] sm:h-[360px]'
        } flex items-center justify-center cursor-pointer transition-transform duration-300 active:scale-95 group`}
        role="button"
        tabIndex={0}
        aria-label={isListening ? 'Stop listening' : 'Start voice interaction'}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onClick?.();
          }
        }}
      >
        <canvas
          ref={canvasRef}
          aria-hidden="true"
          className="w-full h-full pointer-events-none drop-shadow-2xl"
        />

        {/* Refusal / Shield Overlay (Subtle) */}
        {isRefused && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none animate-fade-in">
            <ShieldAlert className="w-9 h-9 text-goa-pink/90 drop-shadow-md" />
          </div>
        )}
      </div>

      {/* State Processing Stage Feedback Label */}
      {!compact && stageLabel && isProcessing && (
        <div className="mt-1 text-center z-20 animate-fade-in">
          <p className="text-xs font-mono tracking-wider text-goa-yellow font-medium bg-goa-forest-deep/90 px-3.5 py-1.5 rounded-full border border-goa-line/30 inline-flex items-center gap-2 shadow-md">
            <span className="w-2 h-2 rounded-full bg-goa-yellow animate-pulse" />
            <span>{stageLabel}</span>
          </p>
        </div>
      )}
    </div>
  );
};

export default VoiceOrb;
