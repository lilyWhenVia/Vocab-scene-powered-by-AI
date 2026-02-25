/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        forest: '#4a5d23',
        'forest-dark': '#3d4d1c',
        olive: '#6b7c3f',
        sage: '#8b9a6d',
        cream: '#f5f3e7',
        gold: '#c9a227',
        emerald: {
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
        }
      }
    },
  },
  plugins: [],
}
