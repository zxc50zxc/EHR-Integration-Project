/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        arabic: ['Tajawal', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
