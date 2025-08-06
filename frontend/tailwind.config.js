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
        // 赛博朋克配色方案
        primary: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6', // Obsidian紫 - 主色调
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
          950: '#2e1065',
        },
        // 背景色
        bg: {
          primary: '#000000',    // 纯黑主背景
          secondary: '#0a0a0a',  // 深灰背景
          tertiary: '#1a1a1a',   // 中灰背景
        },
        // 文本色
        text: {
          primary: '#ffffff',    // 纯白主要文本
          secondary: '#e5e5e5',  // 浅灰次要文本
          tertiary: '#a3a3a3',   // 中灰辅助文本
        },
        // 霓虹色彩
        neon: {
          cyan: '#00ffff',
          pink: '#ff00ff',
          green: '#00ff00',
          orange: '#ff8000',
          blue: '#0080ff',
        },
        // 矩阵主题色
        matrix: {
          low: '#001a00',      // 低相关性
          medium: '#004d00',   // 中相关性
          high: '#00ff00',     // 高相关性
          intense: '#66ff66',  // 极高相关性
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite alternate',
        'matrix-rain': 'matrix-rain 20s linear infinite',
        'cyber-flicker': 'cyber-flicker 0.15s infinite linear alternate',
      },
      keyframes: {
        'glow-pulse': {
          'from': {
            textShadow: '0 0 5px #8b5cf6, 0 0 10px #8b5cf6, 0 0 15px #8b5cf6, 0 0 20px #8b5cf6',
            boxShadow: '0 0 5px #8b5cf6'
          },
          'to': {
            textShadow: '0 0 10px #8b5cf6, 0 0 20px #8b5cf6, 0 0 30px #8b5cf6, 0 0 40px #8b5cf6',
            boxShadow: '0 0 20px #8b5cf6'
          }
        },
        'matrix-rain': {
          '0%': { transform: 'translateY(-100vh)' },
          '100%': { transform: 'translateY(100vh)' }
        },
        'cyber-flicker': {
          '0%': { opacity: '1' },
          '100%': { opacity: '0.95' }
        }
      },
      backdropBlur: {
        xs: '2px',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'cyber-grid': `
          linear-gradient(rgba(139, 92, 246, 0.1) 1px, transparent 1px),
          linear-gradient(90deg, rgba(139, 92, 246, 0.1) 1px, transparent 1px)
        `,
      },
      backgroundSize: {
        'cyber-grid': '20px 20px',
      }
    },
  },
  plugins: [],
}
