import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export interface MagicRingsProps {
  ringCount?: number;
  speed?: number;
  attenuation?: number;
  lineThickness?: number;
  baseRadius?: number;
  radiusStep?: number;
  scaleRate?: number;
  opacity?: number;
  blur?: number;
  noiseAmount?: number;
  rotation?: number;
  ringGap?: number;
  fadeIn?: number;
  fadeOut?: number;
  followMouse?: boolean;
  mouseInfluence?: number;
  hoverScale?: number;
  parallax?: number;
  clickBurst?: boolean;
  color1?: string;
  color2?: string;
  color3?: string;
  className?: string;
}

export const MagicRings: React.FC<MagicRingsProps> = ({
  ringCount = 5,
  speed = 0.65,
  attenuation = 14,
  lineThickness = 1.5,
  baseRadius = 0.30,
  radiusStep = 0.085,
  scaleRate = 0.055,
  opacity = 0.45,
  blur = 0,
  noiseAmount = 0.025,
  rotation = 0,
  ringGap = 1.7,
  fadeIn = 0.8,
  fadeOut = 0.55,
  followMouse = false,
  mouseInfluence = 0.08,
  hoverScale = 1.05,
  parallax = 0.025,
  clickBurst = true,
  color1 = '#EE2A6D',
  color2 = '#F5C518',
  color3 = '#0F3D2E',
  className = '',
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const animFrameIdRef = useRef<number | null>(null);
  const uniformsRef = useRef<{ [key: string]: THREE.IUniform } | null>(null);

  // Keep state props synced to uniforms without recreating scene
  useEffect(() => {
    if (uniformsRef.current) {
      uniformsRef.current.uRingCount.value = ringCount;
      uniformsRef.current.uSpeed.value = speed;
      uniformsRef.current.uAttenuation.value = attenuation;
      uniformsRef.current.uLineThickness.value = lineThickness;
      uniformsRef.current.uBaseRadius.value = baseRadius;
      uniformsRef.current.uRadiusStep.value = radiusStep;
      uniformsRef.current.uScaleRate.value = scaleRate;
      uniformsRef.current.uOpacity.value = opacity;
      uniformsRef.current.uNoiseAmount.value = noiseAmount;
      uniformsRef.current.uRingGap.value = ringGap;
      uniformsRef.current.uColor1.value.set(color1);
      uniformsRef.current.uColor2.value.set(color2);
      uniformsRef.current.uColor3.value.set(color3);
    }
  }, [
    ringCount,
    speed,
    attenuation,
    lineThickness,
    baseRadius,
    radiusStep,
    scaleRate,
    opacity,
    noiseAmount,
    ringGap,
    color1,
    color2,
    color3,
  ]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Scene & Camera
    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
    camera.position.z = 1;

    // WebGL Renderer
    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance',
    });
    rendererRef.current = renderer;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const width = container.clientWidth || 300;
    const height = container.clientHeight || 300;
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    // Custom Shader Material for Concentric Magic Rings
    const vertexShader = `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = vec4(position, 1.0);
      }
    `;

    const fragmentShader = `
      uniform float uTime;
      uniform vec2 uResolution;
      uniform int uRingCount;
      uniform float uSpeed;
      uniform float uAttenuation;
      uniform float uLineThickness;
      uniform float uBaseRadius;
      uniform float uRadiusStep;
      uniform float uScaleRate;
      uniform float uOpacity;
      uniform float uNoiseAmount;
      uniform float uRingGap;
      uniform vec3 uColor1;
      uniform vec3 uColor2;
      uniform vec3 uColor3;
      varying vec2 vUv;

      // Pseudo-noise function
      float hash(vec2 p) {
        p = fract(p * vec2(123.34, 456.21));
        p += dot(p, p + 45.32);
        return fract(p.x * p.y);
      }

      float noise(vec2 p) {
        vec2 i = floor(p);
        vec2 f = fract(p);
        f = f * f * (3.0 - 2.0 * f);
        float a = hash(i);
        float b = hash(i + vec2(1.0, 0.0));
        float c = hash(i + vec2(0.0, 1.0));
        float d = hash(i + vec2(1.0, 1.0));
        return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
      }

      void main() {
        vec2 uv = (vUv - 0.5) * 2.0;
        float aspect = uResolution.x / max(uResolution.y, 1.0);
        uv.x *= aspect;

        float dist = length(uv);
        float angle = atan(uv.y, uv.x);

        // Dynamic motion & noise deformation
        float time = uTime * uSpeed;
        float n = noise(vec2(angle * 3.0, time * 0.5)) * uNoiseAmount;
        float adjustedDist = dist + n;

        float ringIntensity = 0.0;
        vec3 finalColor = vec3(0.0);

        for (int i = 0; i < 10; i++) {
          if (i >= uRingCount) break;
          float fi = float(i);

          // Evolving radius per ring
          float currentRadius = uBaseRadius + fi * uRadiusStep;
          float wave = sin(time * 1.5 - fi * uRingGap) * uScaleRate;
          float targetRadius = currentRadius + wave;

          // Smooth ring line
          float thickness = (uLineThickness / uResolution.y) * (1.0 + fi * 0.15);
          float ring = 1.0 - smoothstep(0.0, thickness * 2.0, abs(adjustedDist - targetRadius));

          // Color interpolation between Goa Pink, Yellow, and Forest
          float colorBlend = clamp(sin(angle * 2.0 + time + fi * 0.8) * 0.5 + 0.5, 0.0, 1.0);
          vec3 ringColor = mix(uColor1, uColor2, colorBlend);

          // Attenuation towards edges
          float fade = exp(-adjustedDist * uAttenuation * 0.1);
          ringIntensity += ring * fade;
          finalColor += ringColor * ring * fade;
        }

        float alpha = clamp(ringIntensity * uOpacity, 0.0, 1.0);
        gl_FragColor = vec4(finalColor, alpha);
      }
    `;

    const uniforms = {
      uTime: { value: 0 },
      uResolution: { value: new THREE.Vector2(width, height) },
      uRingCount: { value: ringCount },
      uSpeed: { value: speed },
      uAttenuation: { value: attenuation },
      uLineThickness: { value: lineThickness },
      uBaseRadius: { value: baseRadius },
      uRadiusStep: { value: radiusStep },
      uScaleRate: { value: scaleRate },
      uOpacity: { value: opacity },
      uNoiseAmount: { value: noiseAmount },
      uRingGap: { value: ringGap },
      uColor1: { value: new THREE.Color(color1) },
      uColor2: { value: new THREE.Color(color2) },
      uColor3: { value: new THREE.Color(color3) },
    };
    uniformsRef.current = uniforms;

    const geometry = new THREE.PlaneGeometry(2, 2);
    const material = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms,
      transparent: true,
      depthWrite: false,
      depthTest: false,
    });

    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    // Animation Loop
    let lastTime = performance.now();
    let isPaused = false;

    const animate = (currentTime: number) => {
      if (!isPaused) {
        const delta = (currentTime - lastTime) / 1000;
        lastTime = currentTime;
        uniforms.uTime.value += delta;
        renderer.render(scene, camera);
      }
      animFrameIdRef.current = requestAnimationFrame(animate);
    };
    animFrameIdRef.current = requestAnimationFrame(animate);

    // Visibility change listener (pause WebGL when tab inactive)
    const handleVisibilityChange = () => {
      isPaused = document.hidden;
      if (!isPaused) {
        lastTime = performance.now();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // ResizeObserver
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const newWidth = entry.contentRect.width || 300;
        const newHeight = entry.contentRect.height || 300;
        renderer.setSize(newWidth, newHeight);
        uniforms.uResolution.value.set(newWidth, newHeight);
      }
    });
    resizeObserver.observe(container);

    // Cleanup
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      resizeObserver.disconnect();

      if (animFrameIdRef.current) {
        cancelAnimationFrame(animFrameIdRef.current);
      }
      if (renderer.domElement && renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }

      geometry.dispose();
      material.dispose();
      renderer.dispose();
      rendererRef.current = null;
      uniformsRef.current = null;
    };
  }, []);

  return (
    <div
      ref={containerRef}
      aria-hidden="true"
      className={`absolute inset-0 pointer-events-none select-none overflow-hidden ${className}`}
      style={{ pointerEvents: 'none' }}
    />
  );
};
