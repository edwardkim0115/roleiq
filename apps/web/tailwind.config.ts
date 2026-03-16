import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        sand: "#f6f0e4",
        line: "#d8cfbf",
        signal: "#0f766e",
        glow: "#f59e0b",
        mist: "#e2f0ef",
      },
      boxShadow: {
        panel: "0 18px 48px rgba(15, 23, 42, 0.08)",
      },
      fontFamily: {
        sans: ["Aptos", "Trebuchet MS", "Segoe UI", "sans-serif"],
        mono: ["Cascadia Mono", "Aptos Mono", "Consolas", "monospace"],
      },
      keyframes: {
        rise: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        rise: "rise 0.5s ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;

