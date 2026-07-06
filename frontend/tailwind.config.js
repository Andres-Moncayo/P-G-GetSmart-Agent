/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'background': '#0A0A0A',
        'primary': '#F5F5F5',
        'primary-muted': '#A3A3A3',
        'accent': '#6366F1',
        'accent-light': '#818CF8',
        'accent-dark': '#4F46E5',
        'secondary': '#8B5CF6',
        'muted': '#737373',
        'disabled': '#525252',
        'surface': '#161616',
        'elevated': '#1C1C1C',
        'bg-hover': '#222222',
        'border': '#2A2A2A',
        'border-hover': '#3A3A3A',
        'success': '#22C55E',
        'warning': '#EAB308',
        'danger': '#EF4444',
      },
      boxShadow: {
        'card': '0 0 0 1px #2A2A2A',
        'modal': '0 25px 50px rgba(0,0,0,0.6)',
        'glow': '0 0 30px rgba(59,130,246,0.15)',
      },
      animation: {
        'flip': 'flip 0.7s ease-in-out',
      },
      keyframes: {
        flip: {
          '0%': { transform: 'rotateY(0deg)' },
          '100%': { transform: 'rotateY(180deg)' }
        }
      },
    },
  },
  plugins: [],
}