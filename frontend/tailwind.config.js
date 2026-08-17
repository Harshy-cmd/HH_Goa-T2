/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'goa-forest': '#0F3D2E',
        'goa-forest-deep': '#0A2E22',
        'goa-cream': '#F4EDD8',
        'goa-pink': '#EE2A6D',
        'goa-yellow': '#F5C518',
        'goa-line': 'rgba(244, 237, 216, 0.18)',
      },
      fontFamily: {
        serif: ['"Instrument Serif"', '"Melodrama"', 'Georgia', 'serif'],
        sans: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'Consolas', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 12s linear infinite',
        'bounce-subtle': 'bounce 2s infinite',
      }
    },
  },
  plugins: [],
}
