/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        command: {
          950: '#070b14',
          900: '#0d1322',
          850: '#11192e',
          800: '#17223b',
          700: '#233355',
          600: '#334773',
          border: 'rgba(255, 255, 255, 0.08)',
          glow: 'rgba(6, 182, 212, 0.25)',
        },
        bel: {
          blue: '#1e40af',
          cyan: '#06b6d4',
          emerald: '#10b981',
          amber: '#f59e0b',
          crimson: '#ef4444',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'radar-ping': 'radar 2s cubic-bezier(0, 0, 0.2, 1) infinite',
      },
      keyframes: {
        radar: {
          '75%, 100%': {
            transform: 'scale(2.2)',
            opacity: '0',
          },
        },
      },
    },
  },
  plugins: [],
}
