/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Hanyang color palette - Joseon Dynasty theme
        hanyang: {
          navy: '#081429',      // Primary - Night sky
          'navy-light': '#112244',
          stone: '#373d41',     // Secondary - Stone gray
          'stone-light': '#5a6269',
          gold: '#fdb813',      // Accent - Imperial gold
          'gold-dark': '#d49a0a',
          cream: '#f5f0e8',     // Background
          parchment: '#e8e0d0', // Card background
        },
        // Player colors
        player: {
          blue: '#2e5a87',
          red: '#a63d3d',
          green: '#4a7c4a',
          yellow: '#c9a13b',
        },
        // Resource colors
        resource: {
          wood: '#8b5a2b',
          stone: '#708090',
          tile: '#8b4513',
          ink: '#1a1a1a',
        },
      },
      fontFamily: {
        display: ['Noto Serif KR', 'serif'],
        body: ['Noto Sans KR', 'sans-serif'],
      },
      spacing: {
        'tile': '4rem',
        'card': '6rem',
      },
    },
  },
  plugins: [],
}
