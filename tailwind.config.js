/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        teamy: {
          teal: '#04D0C5',
          tealDark: '#03ABA2',
          orange: '#F1A46C',
          orangeDark: '#E89455',
          navy: '#0E1336',
          grayDark: '#716C6C',
          gray: '#C2BDBD',
          grayText: '#353232',
          grayLight: '#D9D2D2',
          pinkRed: '#FF7173',
        },
      },
    },
  },
  plugins: [],
}
