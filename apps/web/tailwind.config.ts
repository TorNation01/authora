import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['selector', '[data-theme="dark"]'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: {
          DEFAULT: 'hsl(var(--background))',
          secondary: 'hsl(var(--background-secondary))',
          soft: 'hsl(var(--background-soft))',
          surface: 'hsl(var(--background-surface, var(--background-secondary)))',
          elevated: 'hsl(var(--background-elevated, var(--card)))',
        },
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
          hover: 'hsl(var(--primary-hover))',
          soft: 'hsl(var(--primary-soft))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        success: {
          DEFAULT: 'hsl(var(--success))',
          foreground: 'hsl(var(--success-foreground))',
        },
        'support-gold': 'hsl(var(--support-gold))',
        'support-green': 'hsl(var(--support-green, var(--success)))',
        warning: {
          DEFAULT: 'hsl(var(--warning))',
          foreground: 'hsl(var(--warning-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover, var(--card)))',
          foreground: 'hsl(var(--popover-foreground, var(--card-foreground)))',
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        serif: ['var(--font-inter)', 'Georgia', 'serif'],
      },
      spacing: {
        '18': '4.5rem',
        '30': '7.5rem',
      },
      transitionDuration: {
        'fast': '150ms',
        'base': '200ms',
        'slow': '300ms',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'var(--radius-sm)',
        xl: 'var(--radius-xl)',
      },
      fontSize: {
        'display-lg': ['3rem', { lineHeight: '1.1' }],
        'display': ['2.25rem', { lineHeight: '1.2' }],
        'display-sm': ['1.875rem', { lineHeight: '1.25' }],
      },
      boxShadow: {
        'card': 'var(--shadow-card)',
        'soft': '0 2px 12px -4px rgb(0 0 0 / 0.06)',
        'glow-gold': '0 0 40px -10px hsl(var(--primary) / 0.25)',
        'glow-gold-subtle': '0 0 60px -20px hsl(var(--primary) / 0.12)',
        'glow-green': '0 0 40px -10px hsl(var(--success) / 0.2)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
