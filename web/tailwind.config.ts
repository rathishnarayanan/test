import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./node_modules/@tremor/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Brand neutrals — cool slate
        slate: {
          950: "#0B1120",
          900: "#0F172A",
          850: "#131D2E",
          800: "#1E293B",
          700: "#334155",
          600: "#475569",
          500: "#64748B",
          400: "#94A3B8",
          300: "#CBD5E1",
          200: "#E2E8F0",
          100: "#F1F5F9",
          50: "#F8FAFC",
        },
        // Accent palette
        teal: {
          DEFAULT: "#0F8B7D",
          light: "#14B8A6",
          dark: "#0A6B60",
        },
        amber: {
          DEFAULT: "#E8A33D",
          light: "#FCD34D",
          dark: "#D97706",
        },
        rose: {
          DEFAULT: "#E0655B",
          light: "#F87171",
          dark: "#B91C1C",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      borderRadius: {
        DEFAULT: "12px",
        lg: "16px",
        md: "12px",
        sm: "8px",
      },
    },
  },
  plugins: [],
};

export default config;
