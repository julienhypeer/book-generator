/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'book': {
          50: '#fef7e7',
          100: '#fdecc4',
          200: '#fbd88c',
          300: '#f8bd4a',
          400: '#f59f1c',
          500: '#ef8709',
          600: '#d36704',
          700: '#af4807',
          800: '#8e380d',
          900: '#752f0e',
          950: '#431703',
        }
      },
      fontFamily: {
        'serif': ['Merriweather', 'Georgia', 'serif'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['Fira Code', 'monospace'],
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: theme('colors.gray.700'),
            a: {
              color: theme('colors.book.600'),
              '&:hover': {
                color: theme('colors.book.700'),
              },
            },
            'h1, h2, h3, h4': {
              fontFamily: theme('fontFamily.serif').join(', '),
            },
            code: {
              backgroundColor: theme('colors.gray.100'),
              borderRadius: theme('borderRadius.sm'),
              paddingLeft: theme('spacing.1'),
              paddingRight: theme('spacing.1'),
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
          },
        },
        print: {
          css: {
            'h1, h2, h3': {
              pageBreakAfter: 'avoid',
              pageBreakInside: 'avoid',
            },
            'p': {
              orphans: 3,
              widows: 3,
              hyphens: 'auto',
            },
            'img': {
              pageBreakInside: 'avoid',
            },
          },
        },
      }),
      screens: {
        'print': { 'raw': 'print' },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}