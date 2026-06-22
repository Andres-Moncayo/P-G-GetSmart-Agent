/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'background': '#0a0a0a',
        'primary': '#f5f5f5',
        'primary-muted': '#ced4da',
        'accent': '#2563eb',
        'accent-muted': '#60a5fa',
        'secondary': '#a855f7',
        'muted': '#6b7280',
        'muted-20': '#374151',
        'surface': '#161616',
        'elevated': '#1c1c1c',
        'border': '#374151',
        'border-hover': '#4b5563',
        'success': '#22c55e',
        'warning': '#f59e0b',
        'danger': '#ef4444',
      },
    },
  },
  plugins: [],
}