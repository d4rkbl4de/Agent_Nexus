import type { Config } from 'tailwindcss';
import { fontFamily } from 'tailwindcss/defaultTheme';

const config: Config = {
  content: [
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/shell/**/*.{js,ts,jsx,tsx,mdx}',
    './src/design-system/**/*.{js,ts,jsx,tsx,mdx}',
    './src/motion/**/*.{js,ts,jsx,tsx,mdx}',
    './src/visualization/**/*.{js,ts,jsx,tsx,mdx}',
    './src/dashboards/**/*.{js,ts,jsx,tsx,mdx}',
    './src/introspection/**/*.{js,ts,jsx,tsx,mdx}',
    './src/shared/**/*.{js,ts,jsx,tsx,mdx}',
    './src/lobes/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        // Core Nexus Palette (Dark, Cyberpunk-inspired)
        'nexus-bg': 'hsl(210 15% 10%)',
        'nexus-dark': 'hsl(210 15% 5%)',
        'nexus-light': 'hsl(210 15% 95%)',
        
        // Primary Agent Accent
        'nexus-primary': 'hsl(200 80% 50%)', // Bright Cyan/Aqua
        'nexus-primary-darker': 'hsl(200 80% 40%)',
        
        // Secondary Utility Accent
        'nexus-secondary': 'hsl(280 60% 60%)', // Neon Purple/Magenta
        
        // Status Indicators
        'status-success': 'hsl(142 70% 45%)',
        'status-error': 'hsl(0 75% 50%)',
        'status-warning': 'hsl(40 80% 55%)',

        // Generic UI Colors (Mapping to Chakra/Tailwind defaults)
        border: 'hsl(210 15% 20%)',
        input: 'hsl(210 15% 15%)',
        ring: 'hsl(200 80% 50%)',
        background: 'hsl(210 15% 10%)',
        foreground: 'hsl(210 15% 90%)',
        card: {
          DEFAULT: 'hsl(210 15% 12%)',
          foreground: 'hsl(210 15% 90%)',
        },
        popover: {
          DEFAULT: 'hsl(210 15% 12%)',
          foreground: 'hsl(210 15% 90%)',
        },
      },
      borderRadius: {
        'xl': 'calc(var(--radius) + 4px)',
        'lg': 'var(--radius)',
        'md': 'calc(var(--radius) - 2px)',
        'sm': 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        // Custom Keyframes for agentic motion
        'ping-pulse': {
          '0%': { transform: 'scale(0.9)', opacity: '0.7' },
          '100%': { transform: 'scale(1.1)', opacity: '0.0' },
        },
        'fade-in-down': {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'code-typing': {
          '0%': { width: '0' },
          '100%': { width: '100%' },
        },
      },
      animation: {
        'ping-pulse': 'ping-pulse 1.5s cubic-bezier(0, 0, 0.2, 1) infinite',
        'fade-in-down': 'fade-in-down 0.5s ease-out',
        'code-typing': 'code-typing 4s steps(40, end)',
        'spin-slow': 'spin 3s linear infinite',
      },
      fontFamily: {
        sans: ['Inter', ...fontFamily.sans],
        mono: ['Fira Code', ...fontFamily.mono],
        display: ['Playfair Display', ...fontFamily.serif], // Used for the main page/branding
      },
      boxShadow: {
        'glow-sm': '0 0 5px rgba(30, 255, 255, 0.5)',
        'glow-md': '0 0 15px rgba(30, 255, 255, 0.8)',
        'glow-primary': '0 0 20px 0px hsl(200 80% 50% / 0.7)',
      },
      zIndex: {
        '1': '1',
        '2000': '2000', // Modals/Overlays
        '3000': '3000', // Agent command palettes
      }
    },
  },
  plugins: [
    require('tailwindcss-animate'),
    require('@tailwindcss/typography'),
  ],
};

export default config;