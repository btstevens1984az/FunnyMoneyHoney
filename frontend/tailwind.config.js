/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#070b12",
          900: "#0c1220",
          800: "#121a2b",
          700: "#1a2438",
        },
        honey: {
          300: "#f6d27a",
          400: "#e8b84b",
          500: "#d4a017",
        },
        mint: {
          400: "#5eead4",
          500: "#2dd4bf",
        },
        coral: {
          400: "#fb7185",
          500: "#f43f5e",
        },
      },
      fontFamily: {
        display: ['"Sora"', "system-ui", "sans-serif"],
        body: ['"IBM Plex Sans"', "system-ui", "sans-serif"],
        mono: ['"IBM Plex Mono"', "ui-monospace", "monospace"],
      },
      boxShadow: {
        glow: "0 0 40px rgba(232, 184, 75, 0.12)",
      },
      backgroundImage: {
        mesh: "radial-gradient(ellipse at 20% 0%, rgba(232,184,75,0.12), transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(45,212,191,0.08), transparent 45%), radial-gradient(ellipse at 50% 100%, rgba(244,63,94,0.06), transparent 40%)",
      },
    },
  },
  plugins: [],
};
