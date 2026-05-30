/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: { 50:'#f0fdf4', 500:'#22c55e', 600:'#16a34a', 900:'#14532d' },
        surface: { DEFAULT:'#0f1117', 50:'#1a1d27', 100:'#22263a', 200:'#2d3148' },
      },
    },
  },
  plugins: [],
}
